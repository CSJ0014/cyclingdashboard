# ==============================================================
# 📊 TRAINING PMC TAB — Material Design 3 Style (Miles / 2dp)
# Unified with report FTP and visual theme
# ==============================================================

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
import json
from datetime import datetime

RAW_DIR = "ride_data/raw"


# --------------------------------------------------------------
# 🎨 CUSTOM CSS — Material Design 3 Theme
# --------------------------------------------------------------

def inject_md3_style():
    st.markdown(
        """
        <style>
        .md3-card {
            background: #ffffff;
            border: 1px solid #e0e0e0;
            border-radius: 12px;
            padding: 1.2rem;
            margin-bottom: 1rem;
            box-shadow: 0 2px 6px rgba(0,0,0,0.08);
        }
        .md3-header {
            color: #6200EE;
            font-weight: 600;
            font-size: 1.1rem;
            margin-bottom: 0.3rem;
        }
        .md3-sub {
            color: #666;
            font-size: 0.9rem;
            margin-bottom: 0.5rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# --------------------------------------------------------------
# 📈 MAIN FUNCTION
# --------------------------------------------------------------

def render():
    st.title("Training Performance Manager")

    inject_md3_style()

    # --- Get FTP from Settings tab (fallback to 222) ---
    ftp = st.session_state.get("Functional Threshold Power (FTP)", 222.0)
    st.caption(f"Using FTP: **{ftp:.0f} W** (from Settings tab)")


    # --- Load rides ---
    df = _load_all_rides(raw_dir=RAW_DIR, ftp=ftp)
    if df.empty:
        st.warning("No ride data available. Sync with Strava to view your PMC.")
        return

    # --- Sliders for CTL/ATL windows ---
    st.markdown("<div class='md3-card'>", unsafe_allow_html=True)
    ctl_window = st.slider("CTL window (days)", 28, 60, 42)
    atl_window = st.slider("ATL window (days)", 3, 14, 7)
    st.markdown("</div>", unsafe_allow_html=True)

    # --- Compute PMC ---
    pmc_df = _compute_pmc(df, ctl_days=ctl_window, atl_days=atl_window)
    if pmc_df.empty:
        st.warning("Not enough data to compute CTL/ATL/TSB yet.")
        return

    # ----------------------------------------------------------
    # 🧮 METRICS OVERVIEW
    # ----------------------------------------------------------
    latest = pmc_df.iloc[-1]
    st.markdown("<div class='md3-card'>", unsafe_allow_html=True)
    st.markdown("<div class='md3-header'>📊 Current Training Load</div>", unsafe_allow_html=True)
    st.markdown(
        f"""
        **Fitness (CTL):** {latest['CTL']:.2f}  
        **Fatigue (ATL):** {latest['ATL']:.2f}  
        **Form (TSB):** {latest['TSB']:.2f}
        """
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # ----------------------------------------------------------
    # 📊 CHART: PERFORMANCE MANAGER
    # ----------------------------------------------------------
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(pmc_df["date"], pmc_df["CTL"], label="CTL (Fitness)", color="#6200EE", linewidth=2)
    ax.plot(pmc_df["date"], pmc_df["ATL"], label="ATL (Fatigue)", color="#B00020", linewidth=2)
    ax.plot(pmc_df["date"], pmc_df["TSB"], label="TSB (Form)", color="#018786", linewidth=2)
    ax.fill_between(pmc_df["date"], pmc_df["CTL"], color="#6200EE", alpha=0.08)
    ax.axhline(0, color="grey", linestyle="--", linewidth=0.8)
    ax.set_title("Performance Manager Chart", fontsize=14, color="#333")
    ax.set_xlabel("Date")
    ax.set_ylabel("Load (TSS/day)")
    ax.legend()
    st.pyplot(fig)

    # ----------------------------------------------------------
    # 📅 WEEKLY LOAD SUMMARY
    # ----------------------------------------------------------
    weekly = (
        df.groupby(pd.Grouper(key="date", freq="W"))[["tss", "distance_mi"]]
        .sum()
        .reset_index()
    )
    weekly["tss"] = weekly["tss"].round(2)
    weekly["distance_mi"] = weekly["distance_mi"].round(2)

    st.markdown("<div class='md3-card'>", unsafe_allow_html=True)
    st.markdown("<div class='md3-header'>📅 Weekly Load Summary</div>", unsafe_allow_html=True)
    st.dataframe(weekly.tail(8), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


# --------------------------------------------------------------
# 🗂️ LOAD RIDES + ESTIMATE TSS IF MISSING
# --------------------------------------------------------------

def _load_all_rides(raw_dir: str, ftp: float = 250.0) -> pd.DataFrame:
    """Aggregate ride summaries and compute TSS if missing."""
    if not os.path.exists(raw_dir):
        return pd.DataFrame(columns=["date", "tss", "distance_mi", "avg_power"])

    records = []
    for fname in os.listdir(raw_dir):
        if not fname.endswith(".json"):
            continue
        try:
            with open(os.path.join(raw_dir, fname), "r") as f:
                data = json.load(f)

            # --- Parse date ---
            date_val = data.get("start_date_local") or data.get("start_date")
            if not date_val:
                continue
            date = pd.to_datetime(date_val, errors="coerce")
            if pd.isna(date):
                continue

            # --- Distance (convert to miles) ---
            dist = data.get("distance", 0)
            if isinstance(dist, dict):
                dist = dist.get("data", [0])[-1] if "data" in dist else 0
            dist_mi = dist / 1609.34 if dist else 0

            # --- Power & time ---
            avg_power = float(data.get("average_watts", 0) or 0)
            np_power = float(data.get("np_power", avg_power))
            moving_time = float(data.get("moving_time", 0))
            hours = moving_time / 3600 if moving_time else 0

            # --- TSS estimation ---
            intensity_factor = data.get("intensity_factor")
            tss = data.get("tss", None)
            if not tss or tss == 0:
                if not intensity_factor and np_power and ftp:
                    intensity_factor = np_power / ftp
                if hours > 0 and intensity_factor:
                    tss = hours * (intensity_factor ** 2) * 100
                elif hours > 0 and avg_power and ftp:
                    tss = hours * ((avg_power / ftp) ** 2) * 100
                else:
                    tss = 0

            records.append({
                "date": date,
                "distance_mi": round(dist_mi, 2),
                "avg_power": round(avg_power, 2),
                "tss": round(tss, 2),
            })
        except Exception:
            continue

    df = pd.DataFrame(records)
    if df.empty:
        return pd.DataFrame(columns=["date", "tss", "distance_mi", "avg_power"])

    df = df.dropna(subset=["date"])
    df = df.sort_values("date").reset_index(drop=True)
    return df


# --------------------------------------------------------------
# 📈 PMC COMPUTATION
# --------------------------------------------------------------

def _compute_pmc(df: pd.DataFrame, ctl_days: int = 42, atl_days: int = 7) -> pd.DataFrame:
    """Compute CTL, ATL, and TSB curves using exponential moving averages."""
    if "tss" not in df.columns or df.empty:
        return pd.DataFrame()

    df = df.copy()
    df = df.set_index("date").asfreq("D", fill_value=0)
    df["CTL"] = df["tss"].ewm(span=ctl_days, adjust=False).mean()
    df["ATL"] = df["tss"].ewm(span=atl_days, adjust=False).mean()
    df["TSB"] = df["CTL"] - df["ATL"]
    df.reset_index(inplace=True)
    df = df.round(2)
    return df
