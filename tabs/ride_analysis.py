# ==============================================================
# 🚴 RIDE ANALYSIS TAB — Material Design 3 Version
# Streamlit-safe, full data analysis pipeline
# ==============================================================

import streamlit as st
import pandas as pd
import numpy as np
import os
from datetime import datetime

from utils.ride_analysis_utils import (
    load_ride_json,
    strava_json_to_df,
    compute_ride_metrics,
)

# --------------------------------------------------------------
# 🎯 MAIN ENTRY POINT
# --------------------------------------------------------------

def render():
    st.title("Ride Analysis")

    # Retrieve the selected ride from session_state
    selected_file = st.session_state.get("selected_ride_path", None)
    if not selected_file or not os.path.exists(selected_file):
        st.info("Select a ride from **Ride History** to analyze.")
        return

    st.markdown(f"**Analyzing ride:** `{os.path.basename(selected_file)}`")

    # ----------------------------------------------------------
    # 🧩 Load and parse ride data
    # ----------------------------------------------------------
    data = load_ride_json(selected_file)
    if not data:
        st.error("⚠️ Failed to load ride data.")
        return

    try:
        df = strava_json_to_df(data)
    except ValueError as e:
        st.error(f"⚠️ Could not parse stream data: {e}")
        return

    # ----------------------------------------------------------
    # ⚙️ Compute metrics
    # ----------------------------------------------------------
    ftp = st.session_state.get("ftp", 250)
    hr_max = st.session_state.get("hr_max", 190)
    metrics = compute_ride_metrics(df, ftp=ftp, hr_max=hr_max)

    # ----------------------------------------------------------
    # 📊 Display Summary
    # ----------------------------------------------------------
    st.subheader("Ride Summary")

    col1, col2, col3 = st.columns(3)
    col1.metric("Distance (mi)", f"{metrics.get('distance_mi', 0):.1f}")
    col2.metric("Duration (min)", f"{metrics.get('duration_min', 0):.1f}")
    col3.metric("Avg Speed (mph)", f"{metrics.get('avg_speed', 0):.1f}")

    col1.metric("Avg Power (W)", f"{metrics.get('avg_power', 0):.0f}")
    col2.metric("Normalized Power (W)", f"{metrics.get('np_power', 0):.0f}")
    col3.metric("Intensity Factor", f"{metrics.get('intensity_factor', 0):.2f}")

    col1.metric("TSS", f"{metrics.get('tss', 0):.0f}")
    col2.metric("Avg HR", f"{metrics.get('avg_hr', 0):.0f}")
    col3.metric("Max HR", f"{metrics.get('max_hr', 0):.0f}")

    # ----------------------------------------------------------
    # ❤️ Heart Rate Zones
    # ----------------------------------------------------------
    if "hr_zone_dist" in metrics:
        st.subheader("Heart Rate Zone Distribution")
        hr_zones = metrics["hr_zone_dist"]
        zone_df = pd.DataFrame({
            "Zone": list(hr_zones.keys()),
            "Time %": list(hr_zones.values())
        })
        st.bar_chart(zone_df.set_index("Zone"))

    # ----------------------------------------------------------
    # ⚡ Power & HR Trace
    # ----------------------------------------------------------
    st.subheader("Ride Trace")
    plot_cols = [c for c in ["watts", "heartrate", "speed_mph"] if c in df.columns]

    if len(plot_cols) > 0:
        st.line_chart(df[plot_cols])
    else:
        st.warning("⚠️ No stream data available for plotting.")

    # ----------------------------------------------------------
    # 📤 Export Option (Phase 3)
    # ----------------------------------------------------------
    st.markdown("---")
    st.subheader("Export Ride Report")

    st.caption("You can export this analysis to a PDF report for AI-based coaching insights.")
    if st.button("📄 Generate PDF Report"):
        from utils.pdf_generator import generate_ride_report
        report_path = generate_ride_report(df, metrics, os.path.basename(selected_file))
        st.success(f"✅ Report saved: `{report_path}`")
        with open(report_path, "rb") as f:
            st.download_button(
                label="⬇️ Download Ride Report PDF",
                data=f,
                file_name=os.path.basename(report_path),
                mime="application/pdf",
            )
