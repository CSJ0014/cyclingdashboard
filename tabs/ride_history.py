# ==============================================================
# 🚴 RIDE HISTORY TAB — Material Design 3 Version (Fixed)
# Lists rides, shows stats, and links to Ride Analysis
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

    if not os.path.exists(RAW_DIR):
        st.info("No rides found yet. Sync with Strava to import activities.")
        return

    # Collect all rides
    rides = []
    for fname in os.listdir(RAW_DIR):
        if not fname.endswith(".json"):
            continue

        path = os.path.join(RAW_DIR, fname)
        try:
            with open(path, "r") as f:
                data = json.load(f)

            rides.append({
                "name": data.get("name", "Untitled Ride"),
                "date": data.get("start_date_local", None),
                "distance_km": round(data.get("distance", 0) / 1000, 1),
                "moving_time_min": round(data.get("moving_time", 0) / 60, 1),
                "avg_power": int(data.get("average_watts", 0)),
                "id": str(data.get("id", fname)),
                "path": path,
            })
        except Exception as e:
            st.warning(f"⚠️ Could not load {fname}: {e}")
            continue

    if not rides:
        st.warning("No rides available. Try syncing with Strava.")
        return

    # Convert to DataFrame for sorting
    df = pd.DataFrame(rides)

    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.sort_values("date", ascending=False)

    st.markdown("### Recent Rides")

    # ----------------------------------------------------------
    # 📋 Render Ride Cards
    # ----------------------------------------------------------
    for idx, row in df.iterrows():
        ride_id = row["id"]
        ride_name = row["name"]
        date_str = (
            row["date"].strftime("%b %d, %Y") if isinstance(row["date"], datetime) else "Unknown"
        )

        card_html = f"""
        <div style='
            background-color: #f8f8f9;
            border: 1px solid #ddd;
            border-radius: 10px;
            padding: 12px 16px;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        '>
            <div>
                <strong>{ride_name}</strong><br>
                <span style='font-size: 0.9em; color: #666;'>📅 {date_str}</span>
            </div>
            <div style='font-size: 0.9em; color: #333; text-align: right;'>
                🏁 {row['distance_km']} km<br>
                ⚡ {row['avg_power']} W | ⏱ {row['moving_time_min']} min
            </div>
        </div>
        """

        # Render card and button in the same row (unique container each time)
        c1, c2 = st.columns([10, 1])
        with c1:
            st.markdown(card_html, unsafe_allow_html=True)
        with c2:
            if st.button("🔍", key=f"analyze_{ride_id}", help=f"Analyze {ride_name}"):
                st.session_state["selected_ride_path"] = row["path"]
                st.session_state["active_tab"] = "Ride Analysis"
                st.query_params["tab"] = "Ride Analysis"
                st.rerun()
