# ==============================================================
# 📊 TRAINING PMC TAB — Streamlit-native Performance Manager Chart
# Uses same FTP variable as reports (from Settings tab)
# ==============================================================

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
import json
from datetime import datetime

RAW_DIR = "ride_data/raw"


# --------------------------------------------------------------
# 📈 MAIN FUNCTION
# --------------------------------------------------------------

def render():
    st.title("Training Performance Manager (PMC)")

    # --- Get FTP from Settings tab (fallback to 250) ---
    ftp = st.session_state.get("ftp", 250.0)
    st.caption(f"Using FTP: **{ftp:.0f} W** from Settings")

    # --- Parameters ---
    ctl_window = st.slider("CTL window (days)", 28, 60, 42)
    atl_window = st.slider("ATL window (days)", 3, 14, 7)

    # --- Load rides ---
    df = _load_all_rides(raw_dir=RAW_DIR, ftp=ftp)
    if df.empty:
        st.warning("No ride data available. Sync with Strava to view your PMC.")
        return

    # --- Compute PMC ---
    pmc_df = _compute_pmc(df, ctl_days=ctl_window, atl_days=atl_window)
    if pmc_df.empty:
        st.warning("Not enough data to compute CTL/ATL/TSB yet.")
        return

    # ----------------------------------------------------------
    # 🧮 STATS OVERVIEW
    # ----------------------------------------------------------
    latest = pmc_df.iloc[-1]
    st.markdown(
        f"""
        **Current Fitness (CTL):** {latest['CTL']:.1f}  
        **Fatigue (ATL):** {latest['ATL']:.1f}  
        **Form (TSB):** {latest['TSB']:.1f}
        """
    )

    # ----------------------------------------------------------
    # 📊 CHART: Performance Manager
    # ----------------------------------------------------------
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(pmc_df["date"], pmc_df["CTL"], label="CTL (Fitness)", color="#6200EE", linewidth=2)
    ax.plot(pmc_df["date"], pmc_df["ATL"], label="ATL (Fatigue)", color="#B00020", linewidth=2)
    ax.plot(pmc_df["date"], pmc_df["TSB"], label="TSB (Form)", color="#018786", linewidth=2)
    ax.axhline(0, color="grey", linestyle="--", linewidth=0.8)
    ax.set_title("Performance Manager Chart")
    ax.set_xlabel("Date")
    ax.set_ylabel("Load (TSS/day)")
    ax.legend()
    st.pyplot(fig)

    # ----------------------------------------------------------
    # 📈 Weekly summary
    # ----------------------------------------------------------
    weekly = (
        df.groupby(pd.Grouper(key="date", freq="W"))[["tss", "distance_km"]]
        .sum()
        .reset_index()
    )

    st.markdown("### Weekly Load Summary")
    st.dataframe(weekly.tail(8), use_container_width=True)


# --------------------------------------------------------------
# 🗂️ LOAD RIDES + ESTIMATE TSS IF MISSING
# --------------------------------------------------------------

def _load_all_rides(raw_dir: str, ftp: float = 250.0) -> pd.DataFrame:
    """Aggregate ride summaries and compute TSS if missing."""
    if not os.path.exists(raw_dir):
        return pd.DataFrame(columns=["date", "tss", "distance_km", "avg_power"])

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

            # --- Distance ---
            dist = data.get("distance", 0)
            if isinstance(dist, dict):
                dist = dist.get("data", [0])[-1] if "data" in dist else 0

            # --- Power & time ---
            avg_power = data.get("average_watts", 0) or 0
            np_power = data.get("np_power", avg_power)
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
                "distance_km": dist / 1000,
                "avg_power": avg_power,
                "tss": tss,
            })
        except Exception:
            continue

    df = pd.DataFrame(records)
    if df.empty:
        return pd.DataFrame(columns=["date", "tss", "distance_km", "avg_power"])

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
    return df
