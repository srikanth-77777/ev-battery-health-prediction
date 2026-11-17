"""
Comprehensive 7-Experiment Benchmark Suite:
1. Baseline GRU (multi-task)
2. GRU + Temporal Attention (multi-task)
3. GRU + Stress Features (multi-task)
4. Proposed GRU + Attention + Stress (multi-task)
5. Baseline LSTM (multi-task)
6. Proposed Architecture - Single-Task SOH
7. Proposed Architecture - Single-Task RUL

Evaluates on unseen held-out cells:
  - NASA: B0018
  - CALCE: CS2_38
  - Oxford: Cell4
Reports physical RUL metrics and per-dataset breakdowns.
"""

import os
import sys
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, os.getcwd())
from src.models.gru_attention import BatteryHealthModel

BASE_FEATURES = [
    'avg_voltage', 'min_voltage', 'max_voltage',
    'avg_current', 'max_current',
    'avg_temp', 'max_temp', 'temp_rise',
    'discharge_duration_s'
]

STRESS_FEATURES = [
    'c_rate', 'temp_stress', 'voltage_stress'
]

class BatteryCycleDataset(Dataset):
    def __init__(self, sequences, soh_targets, rul_targets, dset_names, physical_cycles):
        self.sequences = torch.tensor(sequences, dtype=torch.float32)
        self.soh_targets = torch.tensor(soh_targets, dtype=torch.float32).unsqueeze(1)
        self.rul_targets = torch.tensor(rul_targets, dtype=torch.float32).unsqueeze(1)
        self.dset_names = dset_names
        self.physical_cycles = physical_cycles
        
    def __len__(self):
        return len(self.sequences)
        
    def __getitem__(self, idx):
        return self.sequences[idx], self.soh_targets[idx], self.rul_targets[idx], self.dset_names[idx], self.physical_cycles[idx]

def build_windows_by_cell(df, feature_cols, seq_len=10, scaler=None, is_train=True):
    all_seqs, all_soh, all_rul, all_dsets, all_cycles = [], [], [], [], []
    
    if is_train and scaler is None:
        scaler = StandardScaler()
        scaler.fit(df[feature_cols].values)
        
    for (dset, b_id), grp in df.groupby(['dataset', 'battery_id']):
        grp = grp.sort_values('cycle_index').reset_index(drop=True)
        if len(grp) <= seq_len:
            continue
            
        feats = scaler.transform(grp[feature_cols].values)
        soh_arr = grp['soh'].values
        rul_arr = grp['rul'].values # True physical cycles to EOL
        cyc_arr = grp['physical_cycle'].values
        
        for i in range(len(grp) - seq_len):
            all_seqs.append(feats[i : i + seq_len])
            all_soh.append(soh_arr[i + seq_len])
            all_rul.append(rul_arr[i + seq_len])
            all_dsets.append(dset)
            all_cycles.append(cyc_arr[i + seq_len])
            
    return np.array(all_seqs), np.array(all_soh), np.array(all_rul), all_dsets, all_cycles, scaler

def train_and_eval_model(train_df, test_df, feature_cols, rnn_type='GRU', use_attention=True, task_mode='multi_task', seed=42, epochs=35, seq_len=10):
    torch.manual_seed(seed)
    np.random.seed(seed)
    
    X_tr, y_soh_tr, y_rul_tr, d_tr, c_tr, scaler = build_windows_by_cell(train_df, feature_cols, seq_len=seq_len, is_train=True)
    X_te, y_soh_te, y_rul_te, d_te, c_te, _ = build_windows_by_cell(test_df, feature_cols, seq_len=seq_len, scaler=scaler, is_train=False)
    
    train_loader = DataLoader(BatteryCycleDataset(X_tr, y_soh_tr, y_rul_tr, d_tr, c_tr), batch_size=64, shuffle=True)
    test_loader = DataLoader(BatteryCycleDataset(X_te, y_soh_te, y_rul_te, d_te, c_te), batch_size=64, shuffle=False)
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = BatteryHealthModel(
        input_dim=len(feature_cols),
        hidden_dim=48,
        num_layers=2,
        rnn_type=rnn_type,
        use_attention=use_attention,
        task_mode=task_mode,
        dropout=0.15
    ).to(device)
    
    optimizer = torch.optim.Adam(model.parameters(), lr=0.003, weight_decay=1e-4)
    loss_fn = nn.MSELoss()
    rul_scale = 100.0  # Normalized RUL scaling
    
    for ep in range(epochs):
        model.train()
        for seqs, soh, rul, _, _ in train_loader:
            seqs, soh, rul = seqs.to(device), soh.to(device), rul.to(device)
            optimizer.zero_grad()
            soh_pred, rul_pred, _ = model(seqs)
            
            loss = 0.0
            if task_mode in ['multi_task', 'soh_only']:
                loss += loss_fn(soh_pred, soh)
            if task_mode in ['multi_task', 'rul_only']:
                loss += loss_fn(rul_pred / rul_scale, rul / rul_scale)
                
            loss.backward()
            optimizer.step()
            
    # Evaluation on unseen test cells
    model.eval()
    preds_soh, trues_soh = [], []
    preds_rul, trues_rul = [], []
    dset_list = []
    
    with torch.no_grad():
        for seqs, soh, rul, dnames, _ in test_loader:
            seqs = seqs.to(device)
            soh_pred, rul_pred, _ = model(seqs)
            if soh_pred is not None:
                preds_soh.extend(soh_pred.cpu().numpy().flatten())
                trues_soh.extend(soh.numpy().flatten())
            if rul_pred is not None:
                preds_rul.extend(rul_pred.cpu().numpy().flatten())
                trues_rul.extend(rul.numpy().flatten())
            dset_list.extend(dnames)
            
    res = {}
    if task_mode in ['multi_task', 'soh_only']:
        res['soh_mae'] = float(np.mean(np.abs(np.array(trues_soh) - np.array(preds_soh))))
        res['soh_rmse'] = float(np.sqrt(np.mean((np.array(trues_soh) - np.array(preds_soh))**2)))
    else:
        res['soh_mae'], res['soh_rmse'] = np.nan, np.nan
        
    if task_mode in ['multi_task', 'rul_only']:
        res['rul_mae'] = float(np.mean(np.abs(np.array(trues_rul) - np.array(preds_rul))))
        res['rul_rmse'] = float(np.sqrt(np.mean((np.array(trues_rul) - np.array(preds_rul))**2)))
    else:
        res['rul_mae'], res['rul_rmse'] = np.nan, np.nan
        
    # Breakdown by dataset
    res['breakdown'] = {}
    eval_df = pd.DataFrame({'dataset': dset_list})
    if trues_soh:
        eval_df['soh_true'] = trues_soh
        eval_df['soh_pred'] = preds_soh
    if trues_rul:
        eval_df['rul_true'] = trues_rul
        eval_df['rul_pred'] = preds_rul
        
    for d, g in eval_df.groupby('dataset'):
        res['breakdown'][d] = {
            'soh_mae': float(np.mean(np.abs(g['soh_true'] - g['soh_pred']))) if 'soh_true' in g else np.nan,
            'rul_mae': float(np.mean(np.abs(g['rul_true'] - g['rul_pred']))) if 'rul_true' in g else np.nan
        }
        
    res['model_state'] = model.state_dict()
    res['scaler'] = scaler
    res['feature_cols'] = feature_cols
    return res

def run_research_benchmark():
    csv_path = os.path.join("data", "processed", "unified_battery_cycles.csv")
    df = pd.read_csv(csv_path)
    
    test_cells = ["B0018", "Cell4", "CS2_38"]
    train_df = df[~df['battery_id'].isin(test_cells)].copy()
    test_df = df[df['battery_id'].isin(test_cells)].copy()
    
    print("=" * 80)
    print("EXPANDED 7-EXPERIMENT RESEARCH BENCHMARK (PHYSICAL CYCLES)")
    print(f"Training Cells: {train_df['battery_id'].unique().tolist()}")
    print(f"Held-Out Unseen Test Cells: {test_cells}")
    print("=" * 80)
    
    exp_definitions = [
        ("Exp 1: Baseline GRU", BASE_FEATURES, 'GRU', False, 'multi_task'),
        ("Exp 2: GRU + Temporal Attention", BASE_FEATURES, 'GRU', True, 'multi_task'),
        ("Exp 3: GRU + Stress Features", BASE_FEATURES + STRESS_FEATURES, 'GRU', False, 'multi_task'),
        ("Exp 4: Proposed GRU + Attention + Stress", BASE_FEATURES + STRESS_FEATURES, 'GRU', True, 'multi_task'),
        ("Exp 5: Baseline LSTM", BASE_FEATURES, 'LSTM', False, 'multi_task'),
        ("Exp 6: Proposed (Single-Task SOH)", BASE_FEATURES + STRESS_FEATURES, 'GRU', True, 'soh_only'),
        ("Exp 7: Proposed (Single-Task RUL)", BASE_FEATURES + STRESS_FEATURES, 'GRU', True, 'rul_only')
    ]
    
    summary = []
    best_proposed = None
    
    for name, feats, r_type, attn, task in exp_definitions:
        print(f"\nRunning {name}...")
        res = train_and_eval_model(train_df, test_df, feats, rnn_type=r_type, use_attention=attn, task_mode=task, seed=42, epochs=35)
        
        soh_str = f"{res['soh_mae']:.2f}% / {res['soh_rmse']:.2f}%" if not np.isnan(res['soh_mae']) else "N/A"
        rul_str = f"{res['rul_mae']:.1f} / {res['rul_rmse']:.1f} cyc" if not np.isnan(res['rul_mae']) else "N/A"
        
        nasa_res = res['breakdown'].get('NASA', {})
        calce_res = res['breakdown'].get('CALCE', {})
        oxford_res = res['breakdown'].get('Oxford', {})
        
        nasa_str = f"{nasa_res.get('soh_mae', np.nan):.2f}%" if not np.isnan(nasa_res.get('soh_mae', np.nan)) else "N/A"
        calce_str = f"{calce_res.get('soh_mae', np.nan):.2f}%" if not np.isnan(calce_res.get('soh_mae', np.nan)) else "N/A"
        oxford_str = f"{oxford_res.get('soh_mae', np.nan):.2f}%" if not np.isnan(oxford_res.get('soh_mae', np.nan)) else "N/A"
        
        summary.append({
            'Experiment': name,
            'SOH (MAE / RMSE)': soh_str,
            'RUL (MAE / RMSE)': rul_str,
            'NASA SOH MAE': nasa_str,
            'CALCE SOH MAE': calce_str,
            'Oxford SOH MAE': oxford_str
        })
        print(f"  -> {name} | SOH MAE: {soh_str} | RUL: {rul_str}")
        
        if name.startswith("Exp 4"):
            best_proposed = res
            
    res_df = pd.DataFrame(summary)
    out_csv = os.path.join("data", "processed", "ablation_results.csv")
    res_df.to_csv(out_csv, index=False)
    
    if best_proposed:
        model_save_path = os.path.join("src", "models", "best_gru_attention.pth")
        torch.save({
            "model_state": best_proposed["model_state"],
            "features": best_proposed["feature_cols"],
            "scaler_mean": best_proposed["scaler"].mean_.tolist(),
            "scaler_scale": best_proposed["scaler"].scale_.tolist()
        }, model_save_path)
        print(f"\nSaved Best Proposed Model checkpoint to: {model_save_path}")
        
    print("\n" + "=" * 90)
    print("FINAL 7-EXPERIMENT RESEARCH BENCHMARK")
    print("=" * 90)
    print(res_df.to_string(index=False))
    return res_df

if __name__ == "__main__":
    run_research_benchmark()
