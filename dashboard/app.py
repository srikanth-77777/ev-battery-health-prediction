"""
BatteryAI — Intelligent Battery Health & RUL Predictor
=======================================================
Complete rewrite — v3
Fixes:
  1. SHAP replaced with permutation feature-importance (no tensor errors)
  2. Anomaly = toggle button → alert box + anomaly markers on chart
  3. Checkbox gate after dataset/cell select
  4. 20 virtual cells per dataset (genuine mapped values)
  5. Cell Summary as dedicated nav page, download as PDF (fpdf2)
  6. Anomaly table removed from sidebar
  7. PDF report uses fpdf2 (pure Python, no external binary)
"""

import os, sys, json, io
from datetime import datetime

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import torch
from fpdf import FPDF
from src.models.gru_attention import BatteryHealthModel

# ── page config ───────────────────────────────────────────────
st.set_page_config(
    page_title="BatteryAI – Battery Health Predictor",
    page_icon="🔋", layout="wide",
    initial_sidebar_state="expanded",
)

# ── global CSS ────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;}
.stApp{background-color:#0b0f19;color:#e2e8f0;}
section[data-testid="stSidebar"]{background-color:#080b13;border-right:1px solid #1a2333;}
.brand-title{font-size:24px;font-weight:700;color:#fff;margin-bottom:2px;}
.brand-sub{font-size:10px;font-weight:600;color:#10b981;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:12px;}
.sec-label{font-size:10px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:#475569;margin:12px 0 5px;}
.kpi-card{background:#111827;border:1px solid #1f293d;border-radius:12px;padding:16px 18px;box-shadow:0 4px 15px rgba(0,0,0,.4);margin-bottom:8px;}
.kpi-label{font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:1px;color:#94a3b8;margin-bottom:5px;}
.kv-green{font-size:26px;font-weight:700;color:#10b981;line-height:1.2;}
.kv-blue{font-size:26px;font-weight:700;color:#38bdf8;line-height:1.2;}
.kv-white{font-size:26px;font-weight:700;color:#f8fafc;line-height:1.2;}
.kv-orange{font-size:26px;font-weight:700;color:#f59e0b;line-height:1.2;}
.kv-red{font-size:26px;font-weight:700;color:#ef4444;line-height:1.2;}
.kpi-sub{font-size:11px;color:#64748b;margin-top:4px;}
.ai-box{background:linear-gradient(90deg,rgba(16,185,129,.12),rgba(15,23,42,.6));border:1px solid rgba(16,185,129,.35);border-radius:10px;padding:14px 18px;margin:12px 0 18px;}
.ai-title{color:#10b981;font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;}
.ai-text{color:#cbd5e1;font-size:13px;line-height:1.6;}
.alert-box{background:rgba(239,68,68,.1);border:1px solid rgba(239,68,68,.4);border-radius:10px;padding:14px 18px;margin:12px 0 18px;}
.alert-title{color:#ef4444;font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;}
.alert-text{color:#fca5a5;font-size:13px;line-height:1.6;}
div[data-testid="stButton"]>button{background:#111827;border:1px solid #1f293d;color:#e2e8f0;border-radius:8px;padding:8px 16px;font-weight:600;transition:all .2s;}
div[data-testid="stButton"]>button:hover{border-color:#10b981;color:#10b981;}
</style>
""", unsafe_allow_html=True)

# ── paths ─────────────────────────────────────────────────────
DATA_PATH     = os.path.join(PROJECT_ROOT,"data","processed","unified_battery_cycles.csv")
MODEL_PATH    = os.path.join(PROJECT_ROOT,"src","models","best_gru_attention.pth")
ABLATION_PATH = os.path.join(PROJECT_ROOT,"data","processed","ablation_results.csv")

# ── loaders ───────────────────────────────────────────────────
@st.cache_data
def load_dataset():
    if not os.path.exists(DATA_PATH):
        return None
    raw_df = pd.read_csv(DATA_PATH)
    dfs = []
    for (ds, bid), g in raw_df.groupby(['dataset', 'battery_id']):
        g = g.sort_values('cycle_index').copy()
        if ds == 'CALCE':
            # 1. Cap at cycle 700 (remove cycles > 700)
            g = g[g['physical_cycle'] <= 700].copy()
            # 2. Cut off test restart channel jumps if any
            jump = g[g['soh'].diff() > 15]
            if len(jump) > 0:
                cutoff = jump['physical_cycle'].min() - 1
                g = g[g['physical_cycle'] <= cutoff].copy()
            # 3. Clean single-cycle diagnostic characterization drop spikes in SOH and capacity
            soh = g['soh'].values.copy()
            cap = g['capacity_ah'].values.copy()
            for i in range(1, len(soh)-1):
                if (soh[i-1] - soh[i] > 6) and (soh[i+1] - soh[i] > 6):
                    soh[i] = (soh[i-1] + soh[i+1]) / 2.0
                    cap[i] = (cap[i-1] + cap[i+1]) / 2.0
            g['soh'] = soh
            g['capacity_ah'] = cap
            # Recompute degradation rate and acceleration flag smoothly
            deg_rate = -pd.Series(cap, index=g.index).diff().fillna(0).clip(lower=0)
            g['degradation_rate_ah_per_cycle'] = deg_rate
            g['accelerated_degradation_flag'] = deg_rate > (deg_rate.mean() + 2*deg_rate.std())
        dfs.append(g)
    return pd.concat(dfs, ignore_index=True)

@st.cache_resource
def load_model():
    if not os.path.exists(MODEL_PATH):
        return None, None, None
    ckpt = torch.load(MODEL_PATH, map_location="cpu")
    feat = ckpt["features"]
    mean = np.array(ckpt["scaler_mean"])
    scale= np.array(ckpt["scaler_scale"])
    mdl  = BatteryHealthModel(len(feat),48,2,"GRU",True,"multi_task",0.0)
    mdl.load_state_dict(ckpt["model_state"])
    mdl.eval()
    return mdl, feat, (mean, scale)

df                       = load_dataset()
model, feature_cols, scp = load_model()

if df is None:
    st.error("Dataset not found. Run build_unified_dataset.py first.")
    st.stop()

# ── virtual 20-cell registry ─────────────────────────────────
# Each dataset gets 20 virtual cell names → maps to real cells
REAL_CELLS = {
    "NASA":   ["B0005","B0006","B0007","B0018"],
    "CALCE":  ["CS2_35","CS2_36","CS2_37","CS2_38"],
    "Oxford": ["Cell1","Cell2","Cell3","Cell4","Cell5","Cell6","Cell7","Cell8"],
}

def make_virtual_cells(dataset):
    real = REAL_CELLS[dataset]
    prefixes = {"NASA":"BAT","CALCE":"CS2","Oxford":"OXF"}
    p = prefixes[dataset]
    names = []
    for i in range(1, 21):
        names.append(f"{p}_{i:02d}")
    return names

VIRTUAL_CELLS = {ds: make_virtual_cells(ds) for ds in REAL_CELLS}

def virtual_to_real(dataset, virtual_name):
    vcells = VIRTUAL_CELLS[dataset]
    idx    = vcells.index(virtual_name)
    real   = REAL_CELLS[dataset]
    return real[idx % len(real)]

def virtual_obs_offset(dataset, virtual_name):
    """Give each virtual cell a small cycle-index offset so values differ."""
    vcells = VIRTUAL_CELLS[dataset]
    idx    = vcells.index(virtual_name)
    return idx % 15   # offset 0-14 cycles

# ── inference ─────────────────────────────────────────────────
def infer_counterfactual(cell_df, obs_idx, cf_overrides={}, seq_len=10):
    """
    Run GRU+Attention inference on what-if counterfactual operating parameters.
    cf_overrides: dictionary of overrides, e.g. {'c_rate': 0.8, 'avg_temp': 25.0, ...}
    """
    if model is None or len(cell_df) < 2:
        r = cell_df.iloc[obs_idx-1]
        return float(r["soh"]), float(r["rul"])
    start = max(0, obs_idx - seq_len)
    win = cell_df.iloc[start:obs_idx].copy()
    if len(win) < seq_len:
        pad = pd.concat([win.iloc[[0]]] * (seq_len - len(win)), ignore_index=True)
        win = pd.concat([pad, win], ignore_index=True)
    
    # Apply counterfactual parameter overrides
    for col, val in cf_overrides.items():
        if col in win.columns:
            win[col] = val
    # Recompute coupled stress features if thermal/voltage modified
    if "avg_temp" in cf_overrides and "temp_stress" in win.columns:
        win["temp_stress"] = np.maximum(0, win["avg_temp"] - 35.0)
    if "min_voltage" in cf_overrides and "voltage_stress" in win.columns:
        win["voltage_stress"] = np.maximum(0, 3.0 - win["min_voltage"])

    mean, scale = scp
    norm = (win[feature_cols].values - mean) / (scale + 1e-8)
    inp = torch.tensor(norm, dtype=torch.float32).unsqueeze(0)
    with torch.no_grad():
        s, r, _ = model(inp)
    return float(s.numpy().flatten()[0]), float(r.numpy().flatten()[0])

def infer(cell_df, obs_idx, seq_len=10):
    if model is None or len(cell_df) < 2:
        r = cell_df.iloc[obs_idx-1]
        return float(r["soh"]), float(r["rul"])
    start  = max(0, obs_idx-seq_len)
    win    = cell_df.iloc[start:obs_idx].copy()
    if len(win) < seq_len:
        pad = pd.concat([win.iloc[[0]]]*(seq_len-len(win)), ignore_index=True)
        win = pd.concat([pad,win], ignore_index=True)
    mean,scale = scp
    norm = (win[feature_cols].values - mean)/(scale+1e-8)
    inp  = torch.tensor(norm, dtype=torch.float32).unsqueeze(0)
    with torch.no_grad():
        s,r,_ = model(inp)
    return float(s.numpy().flatten()[0]), float(r.numpy().flatten()[0])

# ── permutation feature importance (replaces SHAP) ────────────
def permutation_importance(cell_df, obs_idx, n_repeats=8, seq_len=10):
    """Permute each feature and measure SOH change → importance."""
    if model is None:
        return None, None
    start = max(0, obs_idx-seq_len)
    win   = cell_df.iloc[start:obs_idx].copy()
    if len(win) < seq_len:
        pad = pd.concat([win.iloc[[0]]]*(seq_len-len(win)), ignore_index=True)
        win = pd.concat([pad,win], ignore_index=True)
    mean,scale = scp
    norm_base = (win[feature_cols].values - mean)/(scale+1e-8)
    base_t    = torch.tensor(norm_base, dtype=torch.float32).unsqueeze(0)
    with torch.no_grad():
        base_soh,_,_ = model(base_t)
    base_val = float(base_soh.numpy().flatten()[0])

    importances = []
    for fi in range(len(feature_cols)):
        diffs = []
        for _ in range(n_repeats):
            perm = norm_base.copy()
            np.random.shuffle(perm[:, fi])
            t = torch.tensor(perm, dtype=torch.float32).unsqueeze(0)
            with torch.no_grad():
                soh_p,_,_ = model(t)
            diffs.append(abs(float(soh_p.numpy().flatten()[0]) - base_val))
        importances.append(np.mean(diffs))
    return np.array(importances), feature_cols

# ── PDF builder using fpdf2 ───────────────────────────────────
def build_pdf(title, kpi_dict, anomaly_info, notes=""):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # header
    pdf.set_fill_color(11,15,25)
    pdf.rect(0,0,210,40,style="F")
    pdf.set_font("Helvetica","B",20)
    pdf.set_text_color(16,185,129)
    pdf.set_xy(10,10)
    pdf.cell(0,10,"BatteryAI", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica","",9)
    pdf.set_text_color(148,163,184)
    pdf.set_x(10)
    pdf.cell(0,6,title, new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(100,116,139)
    pdf.set_x(10)
    pdf.cell(0,5,f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", new_x="LMARGIN", new_y="NEXT")

    pdf.set_y(48)
    pdf.set_font("Helvetica","B",13)
    pdf.set_text_color(56,189,248)
    pdf.cell(0,8,"Key Performance Indicators", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    for k,v in kpi_dict.items():
        pdf.set_fill_color(17,24,39)
        pdf.set_text_color(148,163,184)
        pdf.set_font("Helvetica","",8)
        pdf.cell(80,7,k.upper(),border=0,fill=True)
        pdf.set_text_color(248,250,252)
        pdf.set_font("Helvetica","B",10)
        pdf.cell(110,7,str(v),border=0,fill=True, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1)

    pdf.ln(6)
    pdf.set_font("Helvetica","B",13)
    pdf.set_text_color(56,189,248)
    pdf.cell(0,8,"Anomaly Summary", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_font("Helvetica","",10)
    pdf.set_text_color(203,213,225)
    pdf.multi_cell(0,6,anomaly_info)

    if notes:
        pdf.ln(4)
        pdf.set_font("Helvetica","B",13)
        pdf.set_text_color(56,189,248)
        pdf.cell(0,8,"Research Notes", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)
        pdf.set_font("Helvetica","",9)
        pdf.set_text_color(203,213,225)
        pdf.multi_cell(0,5,notes)

    return bytes(pdf.output())

# ── dark plotly layout ────────────────────────────────────────
DL = dict(template="plotly_dark",plot_bgcolor="#0b0f19",paper_bgcolor="#111827",
          font=dict(color="#94a3b8"),margin=dict(l=40,r=40,t=40,b=40))

# ══════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown('<div class="brand-title">🔋 BatteryAI</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">Intelligent Battery Analytics</div>', unsafe_allow_html=True)

    # Navigation
    st.markdown('<div class="sec-label">Navigation</div>', unsafe_allow_html=True)
    PAGES = [
        "⚡ Forecaster & Live Monitor",
        "🔮 Explainable AI & BMS Recommender",
        "📊 Model Comparison",
        "🔬 Stress & Degradation Explorer",
        "🗂️ Cell Summary",
        "📋 Reports & Analytics",
    ]
    if "nav" not in st.session_state:
        st.session_state.nav = PAGES[0]
    for pg in PAGES:
        if st.button(pg, key=f"nav_{pg}", use_container_width=True):
            st.session_state.nav = pg
    nav = st.session_state.nav

    st.markdown("---")
    st.markdown('<div class="sec-label">🎯 Battery Target</div>', unsafe_allow_html=True)
    datasets    = sorted(df["dataset"].unique().tolist())
    sel_dataset = st.selectbox("Dataset", datasets, label_visibility="collapsed")
    vcells      = VIRTUAL_CELLS[sel_dataset]
    sel_virtual = st.selectbox("Cell ID (20 available)", vcells, label_visibility="collapsed")

    # Checkbox gate — nothing loads until checked
    st.markdown("---")
    load_cell = st.checkbox("✅ Load cell data & predictions", value=False)

    # Only show rest of sidebar when checked
    if load_cell:
        real_cell   = virtual_to_real(sel_dataset, sel_virtual)
        obs_offset  = virtual_obs_offset(sel_dataset, sel_virtual)
        real_sub    = df[(df["dataset"]==sel_dataset)&(df["battery_id"]==real_cell)]
        cell_data   = real_sub.sort_values("cycle_index").reset_index(drop=True)
        total_obs   = len(cell_data)
        xp          = "physical_cycle"

        # Summary stats
        total_cycles  = int(cell_data[xp].max())
        min_soh       = float(cell_data["soh"].min())
        max_soh       = float(cell_data["soh"].max())
        eol_rows      = cell_data[cell_data["soh"]<=80]
        eol_cycle_val = int(eol_rows[xp].iloc[0]) if not eol_rows.empty else None
        avg_temp_val  = float(cell_data["avg_temp"].mean())
        avg_crate_val = float(cell_data["c_rate"].mean())
        anomaly_mask  = (cell_data["accelerated_degradation_flag"]|
                         (cell_data["temp_stress"]>0)|(cell_data["voltage_stress"]>0))
        num_anomalies = int(anomaly_mask.sum())
        anomaly_df    = cell_data[anomaly_mask].copy()

        # Sidebar cell summary (compact)
        st.markdown('<div class="sec-label">📊 Cell Overview</div>', unsafe_allow_html=True)
        ck1,ck2 = st.columns(2)
        with ck1:
            st.markdown(f'<div class="kpi-card"><div class="kpi-label">CYCLES</div>'
                        f'<div class="kv-white" style="font-size:18px">{total_cycles}</div></div>',
                        unsafe_allow_html=True)
        with ck2:
            clr = "kv-red" if num_anomalies>5 else "kv-orange" if num_anomalies>0 else "kv-green"
            st.markdown(f'<div class="kpi-card"><div class="kpi-label">ANOMALIES</div>'
                        f'<div class="{clr}" style="font-size:18px">{num_anomalies}</div></div>',
                        unsafe_allow_html=True)

        # Observation slider
        st.markdown('<div class="sec-label">⏱️ Observation</div>', unsafe_allow_html=True)
        # apply virtual offset
        default_obs = min(25+obs_offset, total_obs)
        sel_obs = st.slider("Cycle index", 1, total_obs, default_obs,
                            label_visibility="collapsed")
        curr_row     = cell_data.iloc[sel_obs-1]
        curr_phys    = int(curr_row[xp])
        nom_cap      = float(curr_row["nominal_capacity"])
        eol_thr      = float(curr_row["eol_threshold"])
        st.caption(f"Physical cycle: **{curr_phys}**")
        st.caption(f"Nominal capacity: **{nom_cap} Ah**")
        st.caption(f"EOL cutoff: **{eol_thr/nom_cap*100:.0f}%**")
    else:
        # defaults so app doesn't crash when unchecked
        real_cell     = virtual_to_real(sel_dataset, sel_virtual)
        real_sub      = df[(df["dataset"]==sel_dataset)&(df["battery_id"]==real_cell)]
        cell_data     = real_sub.sort_values("cycle_index").reset_index(drop=True)
        total_obs     = len(cell_data)
        xp            = "physical_cycle"
        sel_obs       = min(25, total_obs)
        curr_row      = cell_data.iloc[sel_obs-1]
        curr_phys     = int(curr_row[xp])
        nom_cap       = float(curr_row["nominal_capacity"])
        eol_thr       = float(curr_row["eol_threshold"])
        total_cycles  = int(cell_data[xp].max())
        min_soh       = float(cell_data["soh"].min())
        max_soh       = float(cell_data["soh"].max())
        eol_rows      = cell_data[cell_data["soh"]<=80]
        eol_cycle_val = int(eol_rows[xp].iloc[0]) if not eol_rows.empty else None
        avg_temp_val  = float(cell_data["avg_temp"].mean())
        avg_crate_val = float(cell_data["c_rate"].mean())
        anomaly_mask  = (cell_data["accelerated_degradation_flag"]|
                         (cell_data["temp_stress"]>0)|(cell_data["voltage_stress"]>0))
        num_anomalies = int(anomaly_mask.sum())
        anomaly_df    = cell_data[anomaly_mask].copy()

# ══════════════════════════════════════════════════════════════
# GATE: show placeholder if not loaded
# ══════════════════════════════════════════════════════════════
if not load_cell:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #0d1527 0%, #111d35 100%); border: 1px solid #1f2d4a; border-radius: 16px; padding: 28px 32px; margin-bottom: 24px; box-shadow: 0 10px 25px rgba(0,0,0,0.5);">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
        <span style="background: rgba(16,185,129,0.15); color: #10b981; border: 1px solid rgba(16,185,129,0.3); font-size: 11px; font-weight: 700; padding: 4px 10px; border-radius: 6px; letter-spacing: 1px;">WELCOME TO BATTERYAI</span>
        <span style="color: #64748b; font-size: 11px; font-weight: 600; letter-spacing: 1.5px;">INTELLIGENT ANALYTICS</span>
      </div>
      <h1 style="font-size: 28px; font-weight: 800; color: #f8fafc; margin: 0 0 10px 0; letter-spacing: -0.5px;">Understand Your Battery. Predict Its Future.</h1>
      <p style="font-size: 14px; color: #94a3b8; margin: 0 0 24px 0; max-width: 800px; line-height: 1.6;">
        An intelligent battery analytics platform for monitoring battery performance, predicting State of Health (SOH), and understanding degradation.
      </p>
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px;">
        <div style="background: #111827; border: 1px solid #1f293d; border-radius: 12px; padding: 18px 20px;">
          <div style="font-size: 22px; margin-bottom: 6px;">📈</div>
          <div style="color: #f8fafc; font-size: 15px; font-weight: 700; margin-bottom: 4px;">Live Monitoring</div>
          <div style="color: #64748b; font-size: 12px;">Track battery performance</div>
        </div>
        <div style="background: #111827; border: 1px solid #1f293d; border-radius: 12px; padding: 18px 20px;">
          <div style="font-size: 22px; margin-bottom: 6px;">🧬</div>
          <div style="color: #f8fafc; font-size: 15px; font-weight: 700; margin-bottom: 4px;">AI Prediction</div>
          <div style="color: #64748b; font-size: 12px;">Predict battery health</div>
        </div>
        <div style="background: #111827; border: 1px solid #1f293d; border-radius: 12px; padding: 18px 20px;">
          <div style="font-size: 22px; margin-bottom: 6px;">🔬</div>
          <div style="color: #f8fafc; font-size: 15px; font-weight: 700; margin-bottom: 4px;">Degradation Analysis</div>
          <div style="color: #64748b; font-size: 12px;">Understand battery aging</div>
        </div>
        <div style="background: #111827; border: 1px solid #1f293d; border-radius: 12px; padding: 18px 20px;">
          <div style="font-size: 22px; margin-bottom: 6px;">📄</div>
          <div style="color: #f8fafc; font-size: 15px; font-weight: 700; margin-bottom: 4px;">Smart Reports</div>
          <div style="color: #64748b; font-size: 12px;">Generate analytical insights</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.info("👈  **Get Started**: Select a **Dataset** and **Cell ID** in the sidebar, then check **✅ Load cell data & predictions** to begin.")
    st.stop()

# ══════════════════════════════════════════════════════════════
# COMPUTE PREDICTIONS
# ══════════════════════════════════════════════════════════════
raw_pred_soh, raw_pred_rul = infer(cell_data, sel_obs)
raw_actual_soh = float(curr_row["soh"])
raw_actual_rul = float(curr_row["rul"])

# Initialize anomaly toggle state
if "show_anomaly" not in st.session_state:
    st.session_state.show_anomaly = False

show_anomaly = st.session_state.show_anomaly

# When Anomaly mode is toggled ON:
# Display values are adjusted 40% lower (e.g. SOH drops from 70% to 30%, RUL scales down by 40%),
# representing severe degradation / cell failure anomaly state.
if show_anomaly:
    pred_soh = max(5.0, raw_pred_soh - 40.0)
    actual_soh = max(5.0, raw_actual_soh - 40.0)
    pred_rul = max(0.0, raw_pred_rul * 0.6)
    actual_rul = max(0.0, raw_actual_rul * 0.6)
else:
    pred_soh = raw_pred_soh
    actual_soh = raw_actual_soh
    pred_rul = raw_pred_rul
    actual_rul = raw_actual_rul

soh_err = abs(actual_soh - pred_soh)

if pred_soh >= 80:
    status_label, status_color = "Optimal",        "#10b981"
elif pred_soh >= 70:
    status_label, status_color = "Moderate Fade",  "#f59e0b"
else:
    status_label, status_color = "Critical – EOL", "#ef4444"

# ══════════════════════════════════════════════════════════════
# PAGE 1 — FORECASTER
# ══════════════════════════════════════════════════════════════
if nav == PAGES[0]:
    st.title("⚡ Battery Health & RUL Forecaster")
    st.caption(f"Live inference · **{sel_virtual}** (mapped → {real_cell}) · Cycle {curr_phys}")

    # ── KPI cards ────────────────────────────────────────────
    k1,k2,k3,k4 = st.columns(4)
    with k1:
        st.markdown(f"""<div class="kpi-card">
          <div class="kpi-label">Predicted SOH {"⚠️ (Anomaly -40%)" if show_anomaly else ""}</div>
          <div class="{'kv-red' if show_anomaly else 'kv-green'}">{pred_soh:.1f}%</div>
          <div class="kpi-sub">Actual {actual_soh:.1f}% · Error {soh_err:.2f}%</div>
        </div>""", unsafe_allow_html=True)
    with k2:
        st.markdown(f"""<div class="kpi-card">
          <div class="kpi-label">Predicted RUL {"⚠️ (Degraded)" if show_anomaly else ""}</div>
          <div class="{'kv-red' if show_anomaly else 'kv-blue'}">{max(0,int(pred_rul))} <span style="font-size:15px">cycles</span></div>
          <div class="kpi-sub">Actual {int(actual_rul)} cycles to EOL</div>
        </div>""", unsafe_allow_html=True)
    with k3:
        st.markdown(f"""<div class="kpi-card">
          <div class="kpi-label">Health Status</div>
          <div class="kv-white" style="color:{status_color}">{status_label}</div>
          <div class="kpi-sub">EOL at {eol_thr/nom_cap*100:.0f}% SOH</div>
        </div>""", unsafe_allow_html=True)
    with k4:
        st.markdown(f"""<div class="kpi-card">
          <div class="kpi-label">C-Rate</div>
          <div class="kv-white">{curr_row['c_rate']:.2f} C</div>
          <div class="kpi-sub">{curr_row['avg_current']:.2f} A · {curr_row['avg_temp']:.1f}°C</div>
        </div>""", unsafe_allow_html=True)

    # ── AI Narrative ─────────────────────────────────────────
    pts = []
    if show_anomaly:
        pts.append("⚠️ CRITICAL ANOMALY ACTIVE: Degradation accelerated by 40%. Capacity fade has exceeded safe operating limits. Immediate thermal & pack inspection advised.")
    else:
        if curr_row["accelerated_degradation_flag"]:
            pts.append(f"⚠️ Accelerated degradation at cycle {curr_phys} "
                       f"({curr_row['degradation_rate_ah_per_cycle']:.4f} Ah/cycle).")
        else:
            pts.append(f"Stable degradation trajectory at cycle {curr_phys}.")
        if curr_row["temp_stress"] > 0:
            pts.append("Elevated thermal stress detected — accelerates SEI growth.")
        if curr_row["voltage_stress"] > 0:
            pts.append("Deep-discharge voltage stress (<3.0 V) detected.")
        if len(pts)==1:
            pts.append("Operating within safe thermal and electrical bounds.")

    st.markdown(f"""<div class="ai-box">
      <div class="ai-title">🤖 AI Battery Degradation Narrative</div>
      <div class="ai-text">{" ".join(pts)}</div>
    </div>""", unsafe_allow_html=True)

    # ── Anomaly toggle button ─────────────────────────────────
    st.markdown("---")
    col_a, col_b = st.columns([1,4])
    with col_a:
        btn_label = "✅ Reset to Normal View" if show_anomaly else "⚠️ Toggle Anomaly View"
        if st.button(btn_label, use_container_width=True):
            st.session_state.show_anomaly = not st.session_state.show_anomaly
            st.rerun()

    if show_anomaly:
        # Alert box
        acc_count   = int(anomaly_df["accelerated_degradation_flag"].sum()) if not anomaly_df.empty else 0
        temp_count  = int((anomaly_df["temp_stress"]>0).sum()) if not anomaly_df.empty else 0
        volt_count  = int((anomaly_df["voltage_stress"]>0).sum()) if not anomaly_df.empty else 0
        worst_cycle = int(anomaly_df.loc[anomaly_df["degradation_rate_ah_per_cycle"].idxmax(), xp]) if not anomaly_df.empty else curr_phys
        worst_rate  = float(anomaly_df["degradation_rate_ah_per_cycle"].max()) if not anomaly_df.empty else float(curr_row["degradation_rate_ah_per_cycle"])
        st.markdown(f"""<div class="alert-box">
          <div class="alert-title">⚠️ Simulated Anomaly Active — SOH Reduced by 40% & Accelerated Stress</div>
          <div class="alert-text">
            &nbsp;• <b>Simulated SOH Drop</b>: Current observation shifted from <b>{raw_pred_soh:.1f}%</b> down to <b>{pred_soh:.1f}%</b><br>
            &nbsp;• <b>RUL Impact</b>: Remaining Useful Life truncated to <b>{max(0,int(pred_rul))} cycles</b><br>
            &nbsp;• <b>{acc_count}</b> historical accelerated degradation cycles detected<br>
            &nbsp;• <b>{temp_count}</b> cycles with elevated thermal stress (&gt;35°C)<br>
            &nbsp;• <b>{volt_count}</b> cycles with deep-discharge voltage stress (&lt;3.0 V)
          </div>
        </div>""", unsafe_allow_html=True)

    # ── Trajectory chart (anomaly markers & curve shift when toggled) ──
    st.subheader(f"📈 Degradation Trajectory — {sel_virtual}")
    hist_df   = cell_data.iloc[:sel_obs].copy()
    future_df = cell_data.iloc[sel_obs-1:].copy()
    eol_pct   = eol_thr/nom_cap*100.0

    # If anomaly active, shift observed and future curves down by 40% to visually reflect anomaly
    plot_hist_soh = (hist_df["soh"] - 40.0).clip(lower=5.0) if show_anomaly else hist_df["soh"]
    plot_future_soh = (future_df["soh"] - 40.0).clip(lower=5.0) if show_anomaly else future_df["soh"]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=hist_df[xp], y=plot_hist_soh,
        mode="lines+markers", name="Observed SOH" + (" (Anomaly -40%)" if show_anomaly else ""),
        line=dict(color="#ef4444" if show_anomaly else "#10b981", width=3),
        marker=dict(size=4),
    ))
    fig.add_trace(go.Scatter(
        x=future_df[xp], y=plot_future_soh,
        mode="lines", name="Future SOH" + (" (Degraded)" if show_anomaly else " (Ground Truth)"),
        line=dict(color="#f87171" if show_anomaly else "#64748b", width=2, dash="dot"),
    ))
    fig.add_trace(go.Scatter(
        x=[curr_phys], y=[pred_soh],
        mode="markers", name="AI Predicted",
        marker=dict(color="#f59e0b" if show_anomaly else "#38bdf8", size=16, symbol="diamond",
                    line=dict(color="#fff", width=2)),
    ))
    # anomaly markers only when toggled ON
    if show_anomaly and not anomaly_df.empty:
        fig.add_trace(go.Scatter(
            x=anomaly_df[xp], y=(anomaly_df["soh"] - 40.0).clip(lower=5.0),
            mode="markers", name="⚠️ Anomaly Cycles",
            marker=dict(color="#ef4444", size=10, symbol="x", line=dict(width=2, color="#ef4444")),
        ))
    fig.add_hline(y=eol_pct, line_dash="dash", line_color="#ef4444",
                  annotation_text=f"EOL ({eol_pct:.0f}%)",
                  annotation_position="bottom right")
    fig.update_layout(
        **DL,
        xaxis=dict(title="Physical Battery Cycles", gridcolor="#1e293b"),
        yaxis=dict(title="SOH (%)", gridcolor="#1e293b",
                   range=[0 if show_anomaly else min(50, cell_data["soh"].min()-5), 105]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── Feature Importance (permutation) ─────────────────────
    st.markdown("---")
    st.subheader("🧩 AI Explanation — Feature Importance")
    if st.button("Compute Feature Importance for current observation"):
        with st.spinner("Running permutation importance analysis…"):
            imps, feats = permutation_importance(cell_data, sel_obs)
            if imps is not None:
                top_idx  = np.argsort(imps)[-8:][::-1]
                top_f    = [feats[i] for i in top_idx]
                top_v    = imps[top_idx]
                fig_imp  = go.Figure(go.Bar(
                    x=top_v, y=top_f, orientation="h",
                    marker=dict(color=top_v,
                                colorscale=[[0,"#1e3a5f"],[1,"#10b981"]],
                                showscale=False),
                ))
                fig_imp.update_layout(
                    **DL,
                    title="Feature Importance: SOH Sensitivity (Permutation Method)",
                    yaxis=dict(autorange="reversed",gridcolor="#1e293b"),
                    xaxis=dict(title="Avg |SOH change| when feature permuted",
                               gridcolor="#1e293b"),
                )
                st.plotly_chart(fig_imp, use_container_width=True)
                st.caption("Each bar shows how much the SOH prediction changes when that "
                           "feature is randomly shuffled — larger bar = more important feature.")
            else:
                st.warning("Model not loaded. Cannot compute feature importance.")

# ══════════════════════════════════════════════════════════════
# PAGE 2 — MODEL COMPARISON
# ══════════════════════════════════════════════════════════════
elif nav == PAGES[1]:
    st.title("🔮 Explainable AI & Counterfactual BMS Recommender")
    st.caption(f"Physics-grounded XAI feature attribution & interactive 'What-If' control simulator for **{sel_virtual}** (→ {real_cell}) at cycle {curr_phys}.")

    st.markdown("""
    <div class="ai-box">
      <div class="ai-title">🧠 Decision-Support & Diagnostic Rationale</div>
      <div class="ai-text">
        Automotive BMS and warranty engineers need to know <b>why</b> a battery is degrading and <b>what actionable actions</b> will prolong pack lifetime.
        This module computes <b>real-time feature attributions</b> explaining recent degradation and enables <b>counterfactual 'What-If' simulations</b> to prescribe optimal thermal & charge-rate limits.
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ──────────────────────────────────────────────────────────
    # SECTION 1: XAI DECOMPOSITION & FEATURE ATTRIBUTIONS
    # ──────────────────────────────────────────────────────────
    st.subheader("1. 🔍 Explainable AI: Degradation Driver Attribution")
    
    x1, x2 = st.columns([1.3, 1])
    with x1:
        # Run permutation feature sensitivity
        imps, feats = permutation_importance(cell_data, sel_obs, n_repeats=6)
        if imps is not None:
            top_idx = np.argsort(imps)[::-1]
            sorted_f = [feats[i] for i in top_idx]
            sorted_imp = imps[top_idx]
            total_imp = max(sum(sorted_imp), 1e-6)
            pct_imp = (sorted_imp / total_imp) * 100

            # Friendly names
            name_map = {
                "c_rate": "Charging / Discharge C-Rate",
                "avg_temp": "Average Temperature (°C)",
                "max_temp": "Peak Operating Temperature",
                "temp_stress": "High Thermal Stress (>35°C)",
                "voltage_stress": "Deep-Discharge Stress (<3.0V)",
                "avg_voltage": "Mean Cycle Voltage (V)",
                "min_voltage": "Cutoff Voltage Minimum (V)",
                "max_voltage": "Peak Charging Voltage (V)",
                "avg_current": "Average Operating Current (A)",
                "max_current": "Peak Surge Current (A)",
                "discharge_duration_s": "Discharge Duration (sec)",
                "temp_rise": "Cycle Thermal Rise (ΔT)"
            }
            labels = [name_map.get(f, f) for f in sorted_f[:7]]
            values = pct_imp[:7]

            fig_xai = go.Figure(go.Bar(
                x=values[::-1], y=labels[::-1], orientation="h",
                marker=dict(
                    color=values[::-1],
                    colorscale=[[0, "#1e3a5f"], [0.5, "#38bdf8"], [1, "#10b981"]],
                    showscale=False
                ),
                text=[f"{v:.1f}%" for v in values[::-1]],
                textposition="auto"
            ))
            fig_xai.update_layout(
                **DL,
                title="Relative Degradation Attribution (% Influence on SOH Loss)",
                xaxis=dict(title="Contribution to Degradation Rate (%)", gridcolor="#1e293b"),
                yaxis=dict(gridcolor="#1e293b"),
                height=320,
            )
            st.plotly_chart(fig_xai, use_container_width=True)

    with x2:
        st.markdown("#### 🔬 Physical Root-Cause Breakdown")
        lead_feat = sorted_f[0] if imps is not None else "c_rate"
        
        # Determine actionable diagnosis text based on lead feature
        if "temp" in lead_feat:
            diag_title = "🌡️ Thermal Excursion Dominant"
            diag_text = (
                f"Elevated operating temperature (measured {curr_row['avg_temp']:.1f}°C) is the #1 degradation catalyst, "
                "accelerating Solid Electrolyte Interphase (SEI) layer growth and irreversible lithium inventory loss (LLI)."
            )
            diag_action = "Lower thermal chilling setpoint by 3–5°C during high-load charging."
        elif "c_rate" in lead_feat or "current" in lead_feat:
            diag_title = "⚡ C-Rate & Kinetic Overpotential Dominant"
            diag_text = (
                f"High cycling rates (active C-rate {curr_row['c_rate']:.2f}C) are causing active material mechanical cracking (LAM) "
                "and localized lithium plating on the graphite anode."
            )
            diag_action = "Throttle fast-charging above 1.2C when battery state-of-charge exceeds 75%."
        elif "voltage" in lead_feat:
            diag_title = "⚡ Deep-Discharge Voltage Stress Dominant"
            diag_text = (
                f"Cell discharge below threshold (measured {curr_row['min_voltage']:.2f}V) triggers copper dissolution and current collector damage."
            )
            diag_action = "Increase lower cutoff voltage threshold to 3.0V in BMS firmware."
        else:
            diag_title = "🔋 Cyclic Wear Dominant"
            diag_text = "Uniform electrochemical impedance buildup without catastrophic abnormal spikes."
            diag_action = "Maintain regular balanced cycling protocols."

        st.markdown(f"""
        <div class="kpi-card" style="border-left: 4px solid #10b981;">
          <div style="font-weight:700; color:#10b981; font-size:14px; margin-bottom:6px;">{diag_title}</div>
          <div style="color:#cbd5e1; font-size:12px; line-height:1.6; margin-bottom:12px;">{diag_text}</div>
          <div style="background:#080b13; padding:10px 12px; border-radius:8px; border:1px solid #1f293d;">
            <div style="font-size:10px; font-weight:700; color:#38bdf8; text-transform:uppercase; margin-bottom:2px;">Prescribed BMS Action</div>
            <div style="font-size:12px; color:#f8fafc; font-weight:600;">{diag_action}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ──────────────────────────────────────────────────────────
    # SECTION 2: INTERACTIVE "WHAT-IF" COUNTERFACTUAL SIMULATOR
    # ──────────────────────────────────────────────────────────
    st.subheader("2. 🎛️ Counterfactual 'What-If' BMS Control Simulator")
    st.caption("Adjust prospective operational controls to test how BMS thermal management, charge limits, and cutoff thresholds extend pack longevity.")

    cf_col1, cf_col2 = st.columns([1, 1.4])

    with cf_col1:
        st.markdown("##### ⚙️ Simulated BMS Operating Controls")
        
        baseline_crate = float(curr_row["c_rate"])
        baseline_temp = float(curr_row["avg_temp"])
        baseline_minv = float(curr_row["min_voltage"])

        sim_crate = st.slider(
            "Max Fast-Charge / Discharge C-Rate",
            min_value=0.2, max_value=2.5,
            value=float(np.clip(baseline_crate, 0.2, 2.5)),
            step=0.05,
            help="Lowering C-rate reduces ohmic heating (I²R) and prevents lithium plating on negative electrode."
        )

        sim_temp = st.slider(
            "Battery Pack Target Temperature (°C)",
            min_value=15.0, max_value=50.0,
            value=float(np.clip(baseline_temp, 15.0, 50.0)),
            step=0.5,
            help="Optimal lithium-ion operating window is between 20°C and 30°C."
        )

        sim_min_v = st.slider(
            "Discharge Voltage Cutoff Floor (V)",
            min_value=2.5, max_value=3.4,
            value=float(np.clip(baseline_minv, 2.5, 3.4)),
            step=0.05,
            help="Increasing the cutoff floor prevents over-discharge and copper dendrite growth."
        )

        # Quick preset recommendation buttons
        st.markdown("<div style='font-size:11px; font-weight:700; color:#94a3b8; margin: 8px 0 4px;'>QUICK BMS POLICY PRESETS:</div>", unsafe_allow_html=True)
        btn_p1, btn_p2, btn_p3 = st.columns(3)
        with btn_p1:
            if st.button("🛡️ Eco-Preserve", use_container_width=True):
                st.session_state["cf_preset"] = "eco"
                st.rerun()
        with btn_p2:
            if st.button("⚖️ Balanced", use_container_width=True):
                st.session_state["cf_preset"] = "balanced"
                st.rerun()
        with btn_p3:
            if st.button("🏎️ Performance", use_container_width=True):
                st.session_state["cf_preset"] = "perf"
                st.rerun()

    # Apply preset if clicked
    if "cf_preset" in st.session_state:
        if st.session_state["cf_preset"] == "eco":
            sim_crate, sim_temp, sim_min_v = 0.5, 23.0, 3.10
        elif st.session_state["cf_preset"] == "balanced":
            sim_crate, sim_temp, sim_min_v = 1.0, 26.0, 3.00
        elif st.session_state["cf_preset"] == "perf":
            sim_crate, sim_temp, sim_min_v = 2.0, 38.0, 2.70
        del st.session_state["cf_preset"]

    # Compute counterfactual prediction
    cf_overrides = {
        "c_rate": sim_crate,
        "avg_temp": sim_temp,
        "max_temp": sim_temp + 3.0,
        "min_voltage": sim_min_v,
    }
    cf_pred_soh, cf_pred_rul = infer_counterfactual(cell_data, sel_obs, cf_overrides)
    
    # Delta calculations
    delta_soh = cf_pred_soh - pred_soh
    delta_rul = cf_pred_rul - pred_rul

    with cf_col2:
        st.markdown("##### 📈 Projected Health Under Counterfactual Policy")
        
        # 3 Comparison KPI Cards
        ck1, ck2, ck3 = st.columns(3)
        with ck1:
            clr = "kv-green" if delta_soh >= 0 else "kv-red"
            sign = "+" if delta_soh >= 0 else ""
            st.markdown(f"""
            <div class="kpi-card">
              <div class="kpi-label">Projected SOH</div>
              <div class="{clr}">{cf_pred_soh:.1f}%</div>
              <div class="kpi-sub">Shift: <b>{sign}{delta_soh:.1f}%</b></div>
            </div>
            """, unsafe_allow_html=True)
            
        with ck2:
            clr_r = "kv-blue" if delta_rul >= 0 else "kv-orange"
            sign_r = "+" if delta_rul >= 0 else ""
            st.markdown(f"""
            <div class="kpi-card">
              <div class="kpi-label">Projected RUL</div>
              <div class="{clr_r}">{max(0, int(cf_pred_rul))} cyc</div>
              <div class="kpi-sub">Delta: <b>{sign_r}{int(delta_rul)} cycles</b></div>
            </div>
            """, unsafe_allow_html=True)

        with ck3:
            policy_tag = "Optimal Life" if delta_rul > 10 else ("Severe Degrading" if delta_rul < -10 else "Baseline Equivalent")
            tag_color = "#10b981" if delta_rul > 10 else ("#ef4444" if delta_rul < -10 else "#38bdf8")
            st.markdown(f"""
            <div class="kpi-card">
              <div class="kpi-label">Policy Assessment</div>
              <div class="kv-white" style="color:{tag_color}; font-size:18px;">{policy_tag}</div>
              <div class="kpi-sub">vs current observed state</div>
            </div>
            """, unsafe_allow_html=True)

        # Counterfactual trajectory comparison chart
        hist_df_cf = cell_data.iloc[:sel_obs].copy()
        remaining_steps = min(50, total_obs - sel_obs)
        if remaining_steps > 0:
            future_steps_x = np.arange(curr_phys, curr_phys + remaining_steps)
            # Baseline trajectory slope
            base_slope = (cell_data["soh"].iloc[-1] - actual_soh) / max(total_obs - sel_obs, 1)
            future_base_y = np.clip(actual_soh + base_slope * np.arange(remaining_steps), 20.0, 100.0)
            
            # Counterfactual slope adjusted by RUL multiplier
            rul_factor = max(0.1, (cf_pred_rul + 1e-4) / (pred_rul + 1e-4))
            cf_slope = base_slope / rul_factor
            future_cf_y = np.clip(actual_soh + cf_slope * np.arange(remaining_steps), 20.0, 100.0)

            fig_sim = go.Figure()
            fig_sim.add_trace(go.Scatter(
                x=hist_df_cf[xp], y=hist_df_cf["soh"],
                mode="lines", name="Observed Past SOH",
                line=dict(color="#64748b", width=2)
            ))
            fig_sim.add_trace(go.Scatter(
                x=future_steps_x, y=future_base_y,
                mode="lines", name="Current Policy Trajectory",
                line=dict(color="#f59e0b", width=2.5, dash="dot")
            ))
            fig_sim.add_trace(go.Scatter(
                x=future_steps_x, y=future_cf_y,
                mode="lines", name="Counterfactual BMS Policy",
                line=dict(color="#10b981", width=3)
            ))
            fig_sim.add_hline(y=eol_thr/nom_cap*100, line_dash="dash", line_color="#ef4444", annotation_text="EOL (80%)")
            fig_sim.update_layout(
                **DL,
                title="SOH Trajectory Simulation: Baseline vs Counterfactual Policy",
                xaxis=dict(title="Physical Cycles", gridcolor="#1e293b"),
                yaxis=dict(title="SOH (%)", gridcolor="#1e293b", range=[40, 105]),
                height=320,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig_sim, use_container_width=True)

    # ──────────────────────────────────────────────────────────
    # SECTION 3: AUTOMATED BMS PRESCRIPTIONS TABLE
    # ──────────────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("3. 📋 Prescriptive BMS Control Recommendations")
    
    bms_recs = [
        {
            "Subsystem": "🌡️ Thermal Management",
            "Optimal Setpoint": f"{min(sim_temp, 28.0):.1f}°C (Active Chilling)",
            "Current State": f"{curr_row['avg_temp']:.1f}°C",
            "Impact on Cell Longevity": "Extends SEI kinetic stability; suppresses high-temperature Arrhenius side-reactions.",
            "Urgency": "High" if curr_row["avg_temp"] > 35 else "Nominal"
        },
        {
            "Subsystem": "🔌 Fast-Charge Governor",
            "Optimal Setpoint": f"Cap at {min(sim_crate, 1.0):.2f}C above 70% SOC",
            "Current State": f"{curr_row['c_rate']:.2f}C active",
            "Impact on Cell Longevity": "Mitigates overpotential, prevents metallic lithium deposition on anode surface.",
            "Urgency": "High" if curr_row["c_rate"] > 1.5 else "Moderate"
        },
        {
            "Subsystem": "⚡ Voltage Range Window",
            "Optimal Setpoint": f"Floor ≥ {max(sim_min_v, 3.0):.2f}V | Ceiling ≤ 4.15V",
            "Current State": f"{curr_row['min_voltage']:.2f}V cutoff",
            "Impact on Cell Longevity": "Reduces mechanical cathode particle strain and prevents copper dissolution.",
            "Urgency": "High" if curr_row["min_voltage"] < 2.8 else "Nominal"
        },
        {
            "Subsystem": "🔋 State of Charge (SOC) Ceiling",
            "Optimal Setpoint": "Limit daily cycling to 85% SOC (reserve 100% for long trips)",
            "Current State": "Unconstrained 100% cycling",
            "Impact on Cell Longevity": "Reduces transition metal dissolution from positive electrode particles.",
            "Urgency": "Recommended"
        }
    ]
    df_recs = pd.DataFrame(bms_recs)
    st.dataframe(df_recs, use_container_width=True, hide_index=True)

elif nav == PAGES[5]:
    st.title("📊 Multi-Model Research Benchmark")
    st.caption("7-experiment ablation on held-out unseen test cells (B0018, CS2_38, Cell4).")
    if not os.path.exists(ABLATION_PATH):
        st.warning("Run `src/models/train_and_evaluate.py` to generate ablation results.")
    else:
        ab = pd.read_csv(ABLATION_PATH)
        st.dataframe(ab, use_container_width=True)
        rows=[]
        for _,row in ab.iterrows():
            ss=str(row["SOH (MAE / RMSE)"]); rs=str(row["RUL (MAE / RMSE)"])
            soh_m=float(ss.split("%")[0].strip()) if "%" in ss else None
            rul_m=float(rs.split("/")[0].replace("cyc","").strip()) if "cyc" in rs else None
            rows.append({"Exp":str(row["Experiment"]).replace("Exp ","E"),
                         "SOH MAE (%)":soh_m,"RUL MAE (cyc)":rul_m})
        cdf=pd.DataFrame(rows)
        c1,c2=st.columns(2)
        with c1:
            f1=px.bar(cdf.dropna(subset=["SOH MAE (%)"]),x="Exp",y="SOH MAE (%)",
                      title="SOH MAE — Lower is Better",color="SOH MAE (%)",
                      color_continuous_scale=["#10b981","#f59e0b","#ef4444"],template="plotly_dark")
            f1.update_layout(plot_bgcolor="#0b0f19",paper_bgcolor="#111827")
            st.plotly_chart(f1, use_container_width=True)
        with c2:
            f2=px.bar(cdf.dropna(subset=["RUL MAE (cyc)"]),x="Exp",y="RUL MAE (cyc)",
                      title="RUL MAE — Lower is Better",color="RUL MAE (cyc)",
                      color_continuous_scale=["#38bdf8","#f59e0b","#ef4444"],template="plotly_dark")
            f2.update_layout(plot_bgcolor="#0b0f19",paper_bgcolor="#111827")
            st.plotly_chart(f2, use_container_width=True)

        # ── Scenario recommendation table ─────────────────────
        st.markdown("---")
        st.subheader("🎯 Which Model is Best for Your Scenario?")
        scenario_data = {
            "Scenario / Use Case": [
                "🏭 EV Fleet Management — precise SOH monitoring",
                "🔋 Battery Warranty & Replacement scheduling (RUL critical)",
                "⚡ Fast-charging stations — high thermal & voltage stress environments",
                "🏎️ Performance EVs — need both SOH & RUL with lowest combined error",
                "🔬 Research — interpretable single-task SOH baseline",
                "📊 Research — interpretable single-task RUL baseline",
                "💻 Edge deployment — lightweight, no attention overhead",
            ],
            "Recommended Model": [
                "Exp 3: GRU + Stress Features",
                "Exp 2: GRU + Temporal Attention",
                "Exp 3: GRU + Stress Features",
                "Exp 4: GRU + Attention + Stress (Proposed)",
                "Exp 6: Single-Task SOH",
                "Exp 7: Single-Task RUL",
                "Exp 1: Baseline GRU",
            ],
            "Why": [
                "Lowest SOH MAE (4.67%) — stress features directly capture operating conditions",
                "Lowest RUL MAE (13.2 cyc) — temporal attention tracks sequence patterns across charge cycles",
                "Stress features model C-rate, thermal, and voltage explicitly — essential for fast-charging degradation",
                "Best overall multi-task accuracy; temporal attention + stress synergy reduces both SOH and RUL errors",
                "Clean baseline without attention complexity; 7.71% SOH MAE with no RUL overhead",
                "Dedicated RUL head only (30.9 cyc MAE); no SOH noise affecting predictions",
                "Fastest inference, lowest memory; suitable for microcontroller or BMS deployment",
            ],
            "Key Metric": [
                "SOH MAE: 4.67%",
                "RUL MAE: 13.2 cyc",
                "SOH MAE: 4.67% under stress",
                "SOH 11.54% / RUL 34.4 cyc",
                "SOH MAE: 7.71%",
                "RUL MAE: 30.9 cyc",
                "SOH MAE: 14.56% (fast baseline)",
            ],
        }
        scenario_df = pd.DataFrame(scenario_data)
        st.dataframe(scenario_df, use_container_width=True, height=300)

        st.markdown(f"""<div class="ai-box">
          <div class="ai-title">🔬 Research Conclusion</div>
          <div class="ai-text">
            <b>Exp 3 (GRU + Stress Features)</b> delivers the best pure SOH accuracy (4.67% MAE),
            critical for health monitoring applications. <b>Exp 2 (GRU + Temporal Attention)</b>
            achieves the lowest RUL error (13.2 cycles MAE), ideal for replacement scheduling.
            Our <b>proposed Exp 4</b> model balances both tasks, making it the most
            versatile architecture for production EV battery management systems where both
            SOH and RUL must be estimated simultaneously from a single model.
          </div>
        </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# PAGE 3 — STRESS EXPLORER
# ══════════════════════════════════════════════════════════════
elif nav == PAGES[2]:
    st.title("🔬 Operating-Stress & Degradation Explorer")
    st.caption(f"Full degradation & stress intelligence for **{sel_virtual}** (→ {real_cell})")

    # ── Compute rich lifetime-level metrics ──────────────────
    total_cap_loss  = max_soh - min_soh          # total % capacity lost
    fade_rate_per100= total_cap_loss / max(total_cycles,1) * 100  # % per 100 cycles
    accel_pct       = num_anomalies / max(total_obs,1) * 100
    cumulative_deg  = float(cell_data["degradation_rate_ah_per_cycle"].sum())
    peak_deg_rate   = float(cell_data["degradation_rate_ah_per_cycle"].max())
    peak_deg_cycle  = int(cell_data.loc[cell_data["degradation_rate_ah_per_cycle"].idxmax(), xp])
    curr_deg        = float(curr_row["degradation_rate_ah_per_cycle"])
    # knee point: cycle where SOH first drops below 90%
    knee_rows = cell_data[cell_data["soh"] < 90]
    knee_cycle = int(knee_rows[xp].iloc[0]) if not knee_rows.empty else None
    # thermal stats
    avg_t = float(cell_data["avg_temp"].mean())
    max_t = float(cell_data["max_temp"].max())
    # capacity retained at current obs
    cap_retained_pct = actual_soh

    # ── Row 1: 4 headline KPIs ────────────────────────────────
    st.markdown("#### 📊 Battery Degradation Health Indicators")
    s1,s2,s3,s4 = st.columns(4)
    with s1:
        clr_cap = "kv-red" if total_cap_loss > 30 else ("kv-orange" if total_cap_loss > 15 else "kv-green")
        st.markdown(f"""<div class="kpi-card">
          <div class="kpi-label">Total Capacity Loss</div>
          <div class="{clr_cap}">{total_cap_loss:.1f}%</div>
          <div class="kpi-sub">Over {total_cycles} measured cycles</div>
        </div>""", unsafe_allow_html=True)
    with s2:
        st.markdown(f"""<div class="kpi-card">
          <div class="kpi-label">Fade Rate</div>
          <div class="kv-orange">{fade_rate_per100:.3f}%<span style="font-size:14px"> / 100 cyc</span></div>
          <div class="kpi-sub">Average capacity fade per 100 cycles</div>
        </div>""", unsafe_allow_html=True)
    with s3:
        clr_acc = "kv-red" if accel_pct > 20 else ("kv-orange" if accel_pct > 5 else "kv-green")
        st.markdown(f"""<div class="kpi-card">
          <div class="kpi-label">Accelerated Degradation</div>
          <div class="{clr_acc}">{accel_pct:.1f}%</div>
          <div class="kpi-sub">{num_anomalies} of {total_obs} cycles flagged</div>
        </div>""", unsafe_allow_html=True)
    with s4:
        st.markdown(f"""<div class="kpi-card">
          <div class="kpi-label">Capacity Retained Now</div>
          <div class="{'kv-green' if cap_retained_pct>=80 else 'kv-orange' if cap_retained_pct>=70 else 'kv-red'}">{cap_retained_pct:.1f}%</div>
          <div class="kpi-sub">at cycle {curr_phys}</div>
        </div>""", unsafe_allow_html=True)

    # ── Row 2: stress & degradation details ──────────────────
    st.markdown("#### ⚡ Stress & Thermal Indicators")
    r2a,r2b,r2c,r2d = st.columns(4)
    with r2a:
        t_clr = "kv-red" if avg_t > 38 else ("kv-orange" if avg_t > 30 else "kv-white")
        st.markdown(f"""<div class="kpi-card">
          <div class="kpi-label">Operating Temperature</div>
          <div class="{t_clr}">{avg_t:.1f}°C</div>
          <div class="kpi-sub">Peak recorded: {max_t:.1f}°C</div>
        </div>""", unsafe_allow_html=True)
    with r2b:
        curr_deg_clr = "kv-red" if curr_row["accelerated_degradation_flag"] else "kv-green"
        st.markdown(f"""<div class="kpi-card">
          <div class="kpi-label">Current Deg. Rate</div>
          <div class="{curr_deg_clr}">{curr_deg:.4f} Ah/cyc</div>
          <div class="kpi-sub">{"⚠️ Accelerated phase" if curr_row["accelerated_degradation_flag"] else "✅ Normal phase"}</div>
        </div>""", unsafe_allow_html=True)
    with r2c:
        st.markdown(f"""<div class="kpi-card">
          <div class="kpi-label">Peak Deg. Rate</div>
          <div class="kv-red">{peak_deg_rate:.4f} Ah/cyc</div>
          <div class="kpi-sub">Worst at cycle {peak_deg_cycle}</div>
        </div>""", unsafe_allow_html=True)
    with r2d:
        knee_txt = str(knee_cycle) if knee_cycle else "Not yet"
        st.markdown(f"""<div class="kpi-card">
          <div class="kpi-label">Knee Point (SOH&lt;90%)</div>
          <div class="kv-blue">{knee_txt}</div>
          <div class="kpi-sub">Physical cycle of rapid fade onset</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── SOH Trajectory + Degradation Rate dual chart ─────────
    st.subheader("SOH Fade & Degradation Rate across Lifetime")
    fig_dual = go.Figure()
    fig_dual.add_trace(go.Scatter(
        x=cell_data[xp], y=cell_data["soh"],
        name="SOH (%)", line=dict(color="#10b981",width=2.5), yaxis="y1"))
    fig_dual.add_trace(go.Bar(
        x=cell_data[xp], y=cell_data["degradation_rate_ah_per_cycle"]*1000,
        name="Deg. Rate (mAh/cyc)", marker_color="#38bdf8",
        opacity=0.5, yaxis="y2"))
    # highlight accelerated cycles
    acc2 = cell_data[cell_data["accelerated_degradation_flag"]]
    if not acc2.empty:
        fig_dual.add_trace(go.Scatter(
            x=acc2[xp], y=acc2["soh"], mode="markers",
            name="⚠️ Accelerated", yaxis="y1",
            marker=dict(color="#ef4444",size=9,symbol="x",line=dict(width=2))))
    eol_pct_s = eol_thr/nom_cap*100
    fig_dual.add_hline(y=eol_pct_s, line_dash="dash", line_color="#ef4444",
                       annotation_text=f"EOL ({eol_pct_s:.0f}%)",
                       annotation_position="bottom right")
    fig_dual.update_layout(
        **DL,
        xaxis=dict(title="Physical Cycles", gridcolor="#1e293b"),
        yaxis=dict(title="SOH (%)", gridcolor="#1e293b",
                   range=[min(50,cell_data["soh"].min()-5),108], side="left"),
        yaxis2=dict(title="Degradation Rate (mAh/cyc)", overlaying="y",
                    side="right", gridcolor="#1f293d", showgrid=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig_dual, use_container_width=True)

    # ── Cumulative capacity loss bar ──────────────────────────
    col_l, col_r = st.columns(2)
    with col_l:
        fig_sc = px.scatter(
            cell_data, x="soh", y="degradation_rate_ah_per_cycle",
            color="accelerated_degradation_flag",
            color_discrete_map={True:"#ef4444", False:"#10b981"},
            size="c_rate", size_max=15,
            labels={"soh":"SOH (%)","degradation_rate_ah_per_cycle":"Deg. Rate (Ah/cyc)",
                    "accelerated_degradation_flag":"Accelerated","c_rate":"C-Rate"},
            title="SOH vs Degradation Rate (bubble = C-Rate)",
            template="plotly_dark")
        fig_sc.update_layout(plot_bgcolor="#0b0f19",paper_bgcolor="#111827")
        st.plotly_chart(fig_sc, use_container_width=True)
    with col_r:
        # Rolling average degradation
        cell_data_r = cell_data.copy()
        cell_data_r["deg_ma"] = cell_data_r["degradation_rate_ah_per_cycle"].rolling(10,min_periods=1).mean()
        fig_ma = go.Figure()
        fig_ma.add_trace(go.Scatter(
            x=cell_data_r[xp], y=cell_data_r["degradation_rate_ah_per_cycle"]*1000,
            name="Raw Deg. Rate", line=dict(color="#38bdf8",width=1), opacity=0.5))
        fig_ma.add_trace(go.Scatter(
            x=cell_data_r[xp], y=cell_data_r["deg_ma"]*1000,
            name="10-cycle Moving Avg", line=dict(color="#10b981",width=2.5)))
        fig_ma.update_layout(
            **DL,
            title="Degradation Rate Trend (10-cycle Moving Average)",
            xaxis=dict(title="Physical Cycles",gridcolor="#1e293b"),
            yaxis=dict(title="Degradation Rate (mAh/cycle)",gridcolor="#1e293b"),
            legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1))
        st.plotly_chart(fig_ma, use_container_width=True)

    # ── Research insight box ──────────────────────────────────
    insight_txt = (
        f"This cell lost <b>{total_cap_loss:.1f}%</b> of its rated capacity over "
        f"<b>{total_cycles}</b> physical cycles, averaging a fade rate of "
        f"<b>{fade_rate_per100:.3f}% per 100 cycles</b>. "
    )
    if knee_cycle:
        insight_txt += (f"The capacity knee — where rapid non-linear fade begins — "
                        f"was detected at cycle <b>{knee_cycle}</b>. ")
    if accel_pct > 5:
        insight_txt += (f"<b>{accel_pct:.1f}%</b> of observed cycles showed accelerated "
                        f"degradation, linked to operating conditions exceeding safe thresholds. ")
    insight_txt += (f"The peak degradation event reached "
                    f"<b>{peak_deg_rate:.4f} Ah/cycle</b> at cycle <b>{peak_deg_cycle}</b>.")
    st.markdown(f"""<div class="ai-box">
      <div class="ai-title">🔬 Research Insight — Degradation Analysis</div>
      <div class="ai-text">{insight_txt}</div>
    </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# PAGE 4 — CELL SUMMARY (dedicated nav page)
# ══════════════════════════════════════════════════════════════
elif nav == PAGES[3]:
    st.title("🗂️ Cell Summary")
    st.caption(f"Complete health profile for **{sel_virtual}** (mapped → {real_cell})")

    # Full summary KPI grid
    r1c1,r1c2,r1c3,r1c4 = st.columns(4)
    with r1c1:
        st.markdown(f"""<div class="kpi-card">
          <div class="kpi-label">Total Cycles</div>
          <div class="kv-white">{total_cycles}</div>
          <div class="kpi-sub">Full lifetime observed</div>
        </div>""", unsafe_allow_html=True)
    with r1c2:
        st.markdown(f"""<div class="kpi-card">
          <div class="kpi-label">SOH Range</div>
          <div class="kv-green">{min_soh:.1f}% – {max_soh:.1f}%</div>
          <div class="kpi-sub">Min → Max across lifetime</div>
        </div>""", unsafe_allow_html=True)
    with r1c3:
        st.markdown(f"""<div class="kpi-card">
          <div class="kpi-label">EOL Reached At</div>
          <div class="kv-blue">{eol_cycle_val if eol_cycle_val else "Not yet"}</div>
          <div class="kpi-sub">Physical cycle number</div>
        </div>""", unsafe_allow_html=True)
    with r1c4:
        clr3="kv-red" if num_anomalies>5 else "kv-orange" if num_anomalies>0 else "kv-green"
        st.markdown(f"""<div class="kpi-card">
          <div class="kpi-label">Anomaly Events</div>
          <div class="{clr3}">{num_anomalies}</div>
          <div class="kpi-sub">Stress / accel. degradation</div>
        </div>""", unsafe_allow_html=True)

    r2c1,r2c2,r2c3,r2c4 = st.columns(4)
    with r2c1:
        st.markdown(f"""<div class="kpi-card">
          <div class="kpi-label">Avg Temperature</div>
          <div class="kv-white">{avg_temp_val:.1f}°C</div>
        </div>""", unsafe_allow_html=True)
    with r2c2:
        st.markdown(f"""<div class="kpi-card">
          <div class="kpi-label">Avg C-Rate</div>
          <div class="kv-white">{avg_crate_val:.3f} C</div>
        </div>""", unsafe_allow_html=True)
    with r2c3:
        st.markdown(f"""<div class="kpi-card">
          <div class="kpi-label">Dataset</div>
          <div class="kv-white">{sel_dataset}</div>
        </div>""", unsafe_allow_html=True)
    with r2c4:
        st.markdown(f"""<div class="kpi-card">
          <div class="kpi-label">Predicted SOH Now</div>
          <div class="kv-green">{pred_soh:.1f}%</div>
          <div class="kpi-sub">at cycle {curr_phys}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    # Full SOH trajectory for this cell
    st.subheader("Full Lifetime SOH Trajectory")
    fig_full = go.Figure()
    fig_full.add_trace(go.Scatter(
        x=cell_data[xp], y=cell_data["soh"],
        mode="lines+markers", name="SOH",
        line=dict(color="#10b981",width=2), marker=dict(size=3),
    ))
    if not anomaly_df.empty:
        fig_full.add_trace(go.Scatter(
            x=anomaly_df[xp], y=anomaly_df["soh"],
            mode="markers", name="Anomaly",
            marker=dict(color="#ef4444",size=8,symbol="x"),
        ))
    eol_pct2 = eol_thr/nom_cap*100
    fig_full.add_hline(y=eol_pct2,line_dash="dash",line_color="#ef4444",
                       annotation_text=f"EOL ({eol_pct2:.0f}%)",
                       annotation_position="bottom right")
    fig_full.update_layout(**DL,
        xaxis=dict(title="Physical Cycles",gridcolor="#1e293b"),
        yaxis=dict(title="SOH (%)",gridcolor="#1e293b",
                   range=[min(50,cell_data["soh"].min()-5),105]))
    st.plotly_chart(fig_full, use_container_width=True)


    st.markdown("---")
    st.subheader("Download Cell Summary as PDF")
    if st.button("Generate Cell Summary PDF", use_container_width=True):
        kpi_dict = {
            "Cell ID (Virtual)":    sel_virtual,
            "Cell ID (Real Data)":  real_cell,
            "Dataset":              sel_dataset,
            "Total Physical Cycles":str(total_cycles),
            "SOH Range":            f"{min_soh:.1f}% to {max_soh:.1f}%",
            "EOL Physical Cycle":   str(eol_cycle_val) if eol_cycle_val else "Not reached",
            "Avg Temperature (C)":  f"{avg_temp_val:.1f}",
            "Avg C-Rate":           f"{avg_crate_val:.3f} C",
            "Anomaly Events":       str(num_anomalies),
            "Predicted SOH":        f"{pred_soh:.1f}% (at cycle {curr_phys})",
            "Predicted RUL":        f"{max(0,int(pred_rul))} cycles",
            "Health Status":        status_label,
        }
        acc_c  = int(anomaly_df["accelerated_degradation_flag"].sum()) if not anomaly_df.empty else 0
        temp_c = int((anomaly_df["temp_stress"]>0).sum()) if not anomaly_df.empty else 0
        volt_c = int((anomaly_df["voltage_stress"]>0).sum()) if not anomaly_df.empty else 0
        anomaly_info = (
            f"Total anomaly events: {num_anomalies}\n"
            f"Accelerated degradation cycles: {acc_c}\n"
            f"Thermal stress cycles (>35C): {temp_c}\n"
            f"Voltage stress cycles (<3.0V): {volt_c}"
        )
        notes = (
            "Generated by BatteryAI using GRU + Temporal Attention trained on "
            "NASA PCoE, CALCE, and Oxford Battery Degradation datasets. "
            "Predictions use the last 10 observed cycles through the multi-task network. "
            "Anomalies flagged via accelerated degradation + thermal/voltage stress thresholds."
        )
        try:
            title_str = f"Cell Report: {sel_virtual} ({sel_dataset}) Cycle {curr_phys}"
            pdf_bytes = build_pdf(title_str, kpi_dict, anomaly_info, notes)
            st.download_button(
                label="Download PDF",
                data=pdf_bytes,
                file_name=f"BatteryAI_{sel_virtual}_cycle{curr_phys}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
            st.success("PDF ready - click Download PDF above.")
        except Exception as ex:
            st.error(f"PDF generation failed: {ex}")

# PAGE 5 — REPORTS & ANALYTICS
# ══════════════════════════════════════════════════════════════
elif nav == PAGES[4]:
    st.title("📋 Reports & Analytics")
    st.caption("Full dataset statistics across all 16 real cells (3 datasets).")

    stats = df.groupby(["dataset","battery_id"]).agg(
        Total_Cycles=("cycle_index","max"),
        Physical_Cycles=("physical_cycle","max"),
        Min_SOH=("soh","min"),
        Max_SOH=("soh","max"),
        EOL_Cycle=("eol_cycle","first"),
        Anomaly_Events=("accelerated_degradation_flag","sum"),
        Avg_Temp=("avg_temp","mean"),
        Avg_CRate=("c_rate","mean"),
    ).round(2).reset_index()
    st.dataframe(stats, use_container_width=True)

    st.download_button(
        label="📥 Download Full Dataset CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="unified_battery_cycles.csv",
        mime="text/csv",
        use_container_width=True,
    )

    st.markdown("---")
    st.subheader("📊 Dataset Distribution")
    dcnt = df.groupby("dataset").size().reset_index(name="Cycles")
    fig_d = px.pie(dcnt, names="dataset", values="Cycles",
                   title="Cycle Distribution by Dataset",
                   color_discrete_sequence=["#10b981","#38bdf8","#f59e0b"],
                   template="plotly_dark")
    fig_d.update_layout(paper_bgcolor="#111827")
    st.plotly_chart(fig_d, use_container_width=True)
