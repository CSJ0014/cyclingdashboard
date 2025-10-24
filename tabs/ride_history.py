# ==============================================================
# 🚴 RIDE HISTORY TAB — Material Design 3 Version
# Lists rides, shows basic stats, and links to Ride Analysis
# ==============================================================

import streamlit as st
import os
import json
import pandas as pd
from datetime import datetime

RAW_DIR = "ride_data/raw"

# --------------------------------------------------------------
# 🎯 MAIN ENTRY POINT
# --------------------------------------------------------------

def render():
    st.title("Ride History")

    # Ensure data directory exists
    if not os.path.exists(RAW_DIR):
        st.info("No rides found yet. Sync with Strava to import activities.")
        return

    # Load rides
    rides = []
    for fname in os.listdir(RAW_DIR):
        if not fname.endswith(".json"):
            continue
        path = os.path.join(RAW_DIR, fname)

        try:
            with open(path, "r") as f:
                data = json.load(f)

            # Parse and normalize data
            rides.append({
                "name": data.get("name", "Untitled Ride"),
                "date": data.get("start_date_local", "Unknown"),
                "distance_km": round(data.get("distance", 0) / 1000, 1),
                "moving_time_min": round(data.get("moving_time", 0) / 60, 1),
                "avg_power": int(data.get("average_watts", 0)),
                "id": data.get("id", fname.replace("activity_", "").replace(".json", "")),
                "path": path,
            })
        except Exception:
            continue

    if not rides:
        st.warning("No rides available. Try syncing with Strava.")
        return

    # Sort rides by date descending (most recent first)
    df = pd.DataFrame(rides)
    if "date" in df.columns:
        try:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
            df = df.sort_values("date", ascending=False)
        except Exception:
            pass

    st.markdown("### Recent Rides")

    # ----------------------------------------------------------
    # 📋 Render Ride Cards with Analyze Button
    # ----------------------------------------------------------
    for i, row in df.iterrows():
        with st.container():
            st.markdown(
                f"""
                <div style='padding: 10px; border-radius: 10px; margin-bottom: 8px;
                            background-color: #f7f7f8; border: 1px solid #ddd;'>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <div>
                            <strong>{row['name']}</strong><br>
                            <span style='font-size: 0.9em; color: #666;'>📅 {row['date'].strftime('%b %d, %Y') if isinstance(row['date'], datetime) else row['date']}</span>
                        </div>
                        <div style='font-size: 0.9em; color: #444;'>
                            🏁 {row['distance_km']} km |
                            ⏱ {row['moving_time_min']} min |
                            ⚡ {row['avg_power']} W
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            cols = st.columns([9, 1])
            with cols[1]:
                if st.button("🔍", key=f"analyze_{row['id']}", help="Analyze this ride"):
                    # Save selection and navigate to Ride Analysis
                    st.session_state["selected_ride_path"] = row["path"]
                    st.session_state["active_tab"] = "Ride Analysis"
                    st.query_params["tab"] = "Ride Analysis"
                    st.rerun()
