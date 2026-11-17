"""
Rigorous Multi-Dataset Preprocessing Pipeline:
- Preserves physical battery cycle counts across all datasets:
  - NASA: Discrete discharge cycle index (1..168)
  - CALCE: Continuous full-lifetime cycles (1..1057)
  - Oxford: Physical battery cycles (0, 100, 200 ... up to 8200 cycles).
    RUL is strictly physical cycles to EOL: RUL = EOL_physical_cycle - current_physical_cycle.
    Also retains observation_step for sequence sliding windows.
- SOH = (Q_discharge / Q_nominal) * 100%
- Operating stress indicators: C-rate, temperature stress (>35°C exposure), deep discharge voltage stress (<3.0V).
- Accelerated degradation rate dQ/dCycle over rolling window.
"""

import os
import glob
import numpy as np
import pandas as pd
import scipy.io as sio

PROCESSED_DIR = os.path.join(os.getcwd(), "data", "processed")
os.makedirs(PROCESSED_DIR, exist_ok=True)

# ----------------------------------------------------------------------
# 1. NASA Dataset Parser
# -------------------------------------------------------------
def parse_nasa():
    print("\n[ETL 1/3] Parsing NASA PCoE Battery Dataset...")
    base_dir = os.path.join("data", "raw", "nasa")
    mat_files = glob.glob(os.path.join(base_dir, "**", "B00*.mat"), recursive=True)
    target_cells = ["B0005", "B0006", "B0007", "B0018"]
    selected_files = [f for f in mat_files if any(c in os.path.basename(f) for c in target_cells)]
    
    nominal_q = 2.0
    eol_threshold = 1.4  # 70% retention documented criterion
    records = []
    
    for fpath in selected_files:
        cell_id = os.path.splitext(os.path.basename(fpath))[0]
        try:
            mat = sio.loadmat(fpath)
            cycles_struct = mat[cell_id][0, 0]['cycle'][0]
        except Exception as e:
            print(f"  Error reading {cell_id}: {e}")
            continue
            
        cycle_idx = 0
        cell_records = []
        for c in cycles_struct:
            if str(c['type'][0]) == 'discharge':
                data = c['data'][0, 0]
                v = np.array(data['Voltage_measured']).flatten() if 'Voltage_measured' in data.dtype.names else np.array([])
                cur = np.array(data['Current_measured']).flatten() if 'Current_measured' in data.dtype.names else np.array([])
                temp = np.array(data['Temperature_measured']).flatten() if 'Temperature_measured' in data.dtype.names else np.array([])
                t = np.array(data['Time']).flatten() if 'Time' in data.dtype.names else np.array([])
                cap = float(data['Capacity'][0, 0]) if 'Capacity' in data.dtype.names and len(data['Capacity']) > 0 else np.nan
                
                if len(v) == 0 or np.isnan(cap):
                    continue
                    
                cycle_idx += 1
                duration = float(t[-1] - t[0]) if len(t) > 1 else 0.0
                
                cell_records.append({
                    "dataset": "NASA",
                    "battery_id": cell_id,
                    "cycle_index": cycle_idx,          # Physical cycle index
                    "physical_cycle": cycle_idx,        # Explicit physical cycle
                    "avg_voltage": float(np.mean(v)),
                    "min_voltage": float(np.min(v)),
                    "max_voltage": float(np.max(v)),
                    "avg_current": float(np.mean(np.abs(cur))),
                    "max_current": float(np.max(np.abs(cur))),
                    "avg_temp": float(np.mean(temp)) if len(temp) > 0 else 24.0,
                    "max_temp": float(np.max(temp)) if len(temp) > 0 else 24.0,
                    "temp_rise": float(np.max(temp) - temp[0]) if len(temp) > 0 else 0.0,
                    "discharge_duration_s": duration,
                    "c_rate": float(np.max(np.abs(cur))) / nominal_q,
                    "temp_stress": float(np.mean(temp > 35.0)) if len(temp) > 0 else 0.0,
                    "voltage_stress": float(np.mean(v < 3.0)),
                    "capacity_ah": cap,
                    "nominal_capacity": nominal_q,
                    "eol_threshold": eol_threshold
                })
                
        df_cell = pd.DataFrame(cell_records)
        if len(df_cell) > 0:
            below_eol = df_cell[df_cell['capacity_ah'] <= eol_threshold]
            eol_cycle = int(below_eol['physical_cycle'].iloc[0]) if len(below_eol) > 0 else int(df_cell['physical_cycle'].max())
            df_cell['eol_cycle'] = eol_cycle
            # Physical RUL in true battery cycles
            df_cell['rul'] = np.maximum(0, df_cell['eol_cycle'] - df_cell['physical_cycle'])
            df_cell['soh'] = (df_cell['capacity_ah'] / nominal_q) * 100.0
            records.extend(df_cell.to_dict('records'))
            print(f"  [NASA] {cell_id}: {len(df_cell)} cycles (Initial SOH={df_cell['soh'].iloc[0]:.1f}%, Final={df_cell['soh'].iloc[-1]:.1f}%, Physical EOL={eol_cycle} cyc)")
            
    return pd.DataFrame(records)

# ----------------------------------------------------------------------
# 2. Oxford Dataset Parser (True Physical Cycles Preserved)
# -------------------------------------------------------------
def parse_oxford():
    print("\n[ETL 2/3] Parsing Oxford Battery Degradation Dataset 1 (Physical Cycles)...")
    fpath = os.path.join("data", "raw", "oxford", "Oxford_Battery_Degradation_Dataset_1.mat")
    if not os.path.exists(fpath):
        return pd.DataFrame()
        
    records = []
    nominal_q = 0.74  # 740 mAh
    eol_threshold = 0.74 * 0.80  # 0.592 Ah (80% retention)
    
    mat = sio.loadmat(fpath)
    cells = [k for k in mat.keys() if k.startswith("Cell")]
    
    for cell_id in cells:
        cell_struct = mat[cell_id][0, 0]
        cycle_fields = sorted([f for f in cell_struct.dtype.names if f.startswith('cyc')])
        cell_records = []
        
        step_idx = 0
        for cfield in cycle_fields:
            try:
                cyc_data = cell_struct[cfield][0, 0]
                if 'C1dc' not in cyc_data.dtype.names:
                    continue
                dc = cyc_data['C1dc'][0, 0]
                
                v = np.array(dc['v']).flatten() if 'v' in dc.dtype.names else np.array([])
                q_arr = np.array(dc['q']).flatten() if 'q' in dc.dtype.names else np.array([])
                t = np.array(dc['t']).flatten() if 't' in dc.dtype.names else np.array([])
                
                if len(v) == 0 or len(q_arr) == 0:
                    continue
                    
                cap = float(np.abs(q_arr[-1])) / 1000.0  # Convert mAh to Ah
                if cap < 0.35 or cap > 0.90:
                    continue
                    
                step_idx += 1
                physical_cycle = int(cfield.replace('cyc', ''))
                duration = float(t[-1] - t[0]) if len(t) > 1 else 0.0
                
                cell_records.append({
                    "dataset": "Oxford",
                    "battery_id": cell_id,
                    "cycle_index": step_idx,           # Sequential step for windowing
                    "physical_cycle": physical_cycle,   # True physical battery cycles (0, 100, 200.. 8200)
                    "avg_voltage": float(np.mean(v)),
                    "min_voltage": float(np.min(v)),
                    "max_voltage": float(np.max(v)),
                    "avg_current": 0.74,
                    "max_current": 0.74,
                    "avg_temp": 40.0,
                    "max_temp": 40.5,
                    "temp_rise": 0.5,
                    "discharge_duration_s": duration,
                    "c_rate": 1.0,
                    "temp_stress": 1.0,
                    "voltage_stress": float(np.mean(v < 3.2)),
                    "capacity_ah": cap,
                    "nominal_capacity": nominal_q,
                    "eol_threshold": eol_threshold
                })
            except Exception:
                continue
                
        df_cell = pd.DataFrame(cell_records)
        if len(df_cell) > 0:
            df_cell = df_cell.sort_values("physical_cycle").reset_index(drop=True)
            below_eol = df_cell[df_cell['capacity_ah'] <= eol_threshold]
            eol_cycle = int(below_eol['physical_cycle'].iloc[0]) if len(below_eol) > 0 else int(df_cell['physical_cycle'].max())
            df_cell['eol_cycle'] = eol_cycle
            # Physical RUL in real battery cycles
            df_cell['rul'] = np.maximum(0, df_cell['eol_cycle'] - df_cell['physical_cycle'])
            df_cell['soh'] = (df_cell['capacity_ah'] / nominal_q) * 100.0
            records.extend(df_cell.to_dict('records'))
            print(f"  [Oxford] {cell_id}: {len(df_cell)} checks, max physical cyc={df_cell['physical_cycle'].max()} (Initial SOH={df_cell['soh'].iloc[0]:.1f}%, Final={df_cell['soh'].iloc[-1]:.1f}%, Physical EOL={eol_cycle} cyc)")
            
    return pd.DataFrame(records)

# ----------------------------------------------------------------------
# 3. CALCE Dataset Parser
# -------------------------------------------------------------
def parse_calce():
    print("\n[ETL 3/3] Parsing CALCE CS2 Battery Dataset (Full Lifetime)...")
    base_dir = os.path.join("data", "raw", "calce")
    target_cells = ["CS2_35", "CS2_36", "CS2_37", "CS2_38"]
    records = []
    nominal_q = 1.1
    eol_threshold = 1.1 * 0.80  # 0.88 Ah (80% retention)
    
    for cell_id in target_cells:
        cell_path = os.path.join(base_dir, cell_id, cell_id)
        if not os.path.exists(cell_path):
            cell_path = os.path.join(base_dir, cell_id)
        if not os.path.exists(cell_path):
            continue
            
        xlsx_files = sorted(glob.glob(os.path.join(cell_path, "*.xlsx")))
        if not xlsx_files:
            continue
            
        print(f"  Reading CALCE {cell_id} across {len(xlsx_files)} Excel files...")
        cell_records = []
        global_cycle = 0
        
        for xf in xlsx_files:
            try:
                df_raw = pd.read_excel(xf, sheet_name=1)
                cols = {c.strip(): c for c in df_raw.columns}
                c_col = next((cols[k] for k in cols if 'Cycle_Index' in k), None)
                q_col = next((cols[k] for k in cols if 'Discharge_Capacity' in k), None)
                v_col = next((cols[k] for k in cols if 'Voltage' in k), None)
                i_col = next((cols[k] for k in cols if 'Current' in k), None)
                
                if not (c_col and q_col):
                    continue
                    
                for _, grp in df_raw.groupby(c_col):
                    cap = float(grp[q_col].max() - grp[q_col].min())
                    if cap < 0.3 or cap > 1.3:
                        continue
                        
                    global_cycle += 1
                    v_vals = grp[v_col].values if v_col else np.array([3.7])
                    i_vals = grp[i_col].values if i_col else np.array([0.55])
                    
                    cell_records.append({
                        "dataset": "CALCE",
                        "battery_id": cell_id,
                        "cycle_index": global_cycle,
                        "physical_cycle": global_cycle,
                        "avg_voltage": float(np.mean(v_vals)),
                        "min_voltage": float(np.min(v_vals)),
                        "max_voltage": float(np.max(v_vals)),
                        "avg_current": float(np.mean(np.abs(i_vals))),
                        "max_current": float(np.max(np.abs(i_vals))),
                        "avg_temp": 25.0,
                        "max_temp": 26.0,
                        "temp_rise": 1.0,
                        "discharge_duration_s": 3600.0,
                        "c_rate": float(np.max(np.abs(i_vals))) / nominal_q,
                        "temp_stress": 0.0,
                        "voltage_stress": float(np.mean(v_vals < 3.0)) if v_col else 0.0,
                        "capacity_ah": cap,
                        "nominal_capacity": nominal_q,
                        "eol_threshold": eol_threshold
                    })
            except Exception:
                continue
                
        df_cell = pd.DataFrame(cell_records)
        if len(df_cell) > 0:
            df_cell = df_cell.sort_values("cycle_index").reset_index(drop=True)
            df_cell['cycle_index'] = np.arange(1, len(df_cell) + 1)
            df_cell['physical_cycle'] = df_cell['cycle_index']
            below_eol = df_cell[df_cell['capacity_ah'] <= eol_threshold]
            eol_cycle = int(below_eol['physical_cycle'].iloc[0]) if len(below_eol) > 0 else int(df_cell['physical_cycle'].max())
            df_cell['eol_cycle'] = eol_cycle
            df_cell['rul'] = np.maximum(0, df_cell['eol_cycle'] - df_cell['physical_cycle'])
            df_cell['soh'] = (df_cell['capacity_ah'] / nominal_q) * 100.0
            records.extend(df_cell.to_dict('records'))
            print(f"  [CALCE] {cell_id}: {len(df_cell)} cycles (Initial SOH={df_cell['soh'].iloc[0]:.1f}%, Final={df_cell['soh'].iloc[-1]:.1f}%, Physical EOL={eol_cycle} cyc)")
            
    return pd.DataFrame(records)

# ----------------------------------------------------------------------
# 4. Accelerated Degradation Feature Engineering
# -------------------------------------------------------------
def compute_accelerated_degradation(df, window=5):
    print("\n--- Computing Accelerated Degradation Metrics & Alerts ---")
    df_out = []
    for (dset, b_id), grp in df.groupby(['dataset', 'battery_id']):
        grp = grp.sort_values('cycle_index').copy()
        cap = grp['capacity_ah'].values
        cycles = grp['physical_cycle'].values
        
        degr_rate = np.zeros(len(grp))
        for i in range(len(grp)):
            start_i = max(0, i - window)
            if i > start_i and (cycles[i] - cycles[start_i]) > 0:
                rate = (cap[start_i] - cap[i]) / (cycles[i] - cycles[start_i])
                degr_rate[i] = max(0.0, rate)
            else:
                degr_rate[i] = 0.0
                
        grp['degradation_rate_ah_per_cycle'] = degr_rate
        pos_rates = degr_rate[degr_rate > 0]
        mean_rate = np.mean(pos_rates) if len(pos_rates) > 0 else 1e-4
        std_rate = np.std(pos_rates) if len(pos_rates) > 0 else 1e-4
        
        grp['accelerated_degradation_flag'] = (degr_rate > (mean_rate + 1.5 * std_rate)) & (degr_rate > 0.0001)
        df_out.append(grp)
        
    return pd.concat(df_out, ignore_index=True)

def main():
    df_nasa = parse_nasa()
    df_oxford = parse_oxford()
    df_calce = parse_calce()
    
    combined = pd.concat([df_nasa, df_oxford, df_calce], ignore_index=True)
    combined = compute_accelerated_degradation(combined)
    
    out_csv = os.path.join(PROCESSED_DIR, "unified_battery_cycles.csv")
    combined.to_csv(out_csv, index=False)
    
    print("\n" + "=" * 80)
    print("ROBUST UNIFIED MULTI-DATASET SUMMARY (PHYSICAL CYCLES)")
    print("=" * 80)
    print(f"Total Cycles Extracted: {len(combined)}")
    print(combined.groupby(['dataset', 'battery_id']).agg(
        obs_count=('cycle_index', 'count'),
        max_physical_cycle=('physical_cycle', 'max'),
        min_soh=('soh', 'min'),
        max_soh=('soh', 'max'),
        physical_eol_cycle=('eol_cycle', 'first'),
        max_physical_rul=('rul', 'max')
    ))
    print(f"\nSaved clean harmonized dataset to: {out_csv}")

if __name__ == "__main__":
    main()
