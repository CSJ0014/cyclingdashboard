# ==============================================================
# 🚴 RIDE HISTORY TAB — Material Design 3 Version (Final Build)
# Lists all rides, handles stream data, and links to Ride Analysis
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

    rides = []

    # ----------------------------------------------------------
    # 📥 LOAD ALL RIDE FILES
    # ----------------------------------------------------------
    for fname in os.listdir(RAW_DIR):
        if not fname.endswith(".json"):
            continue

        path = os.path.join(RAW_DIR, fname)
        try:
            with open(path, "r") as f:
                data = json.load(f)

            # --- Handle both scalar and stream-based fields ---
            raw_distance = data.get("distance", 0)
            if isinstance(raw_distance, dict):
                dist_val = raw_distance.get("data", [0])[-1] if "data" in raw_distance else 0
            else:
                dist_val = raw_distance

            raw_power = data.get("average_watts", 0)
            if isinstance(raw_power, dict):
                avg_power = raw_power.get("data", [0])
                avg_power = sum(avg_power) / len(avg_power) if avg_power else 0
            else:
                avg_power = raw_power or 0

            # Extract normalized power (if available from computed metrics)
            np_power = data.get("np_power", None)
            tss = data.get("tss", None)

            rides.append({
                "name": data.get("name", "Untitled Ride"),
                "date": data.get("start_date_local", None),
                "distance_km": round(dist_val / 1000, 1),
                "moving_time_min": round(data.get("moving_time", 0) / 60, 1),
                "avg_power": round(avg_power, 0),
                "np_power": round(np_power, 0) if np_power else None,
                "tss": round(tss, 0) if tss else None,
                "id": str(data.get("id", fname)),
                "path": path,
            })
        except Exception as e:
            st.warning(f"⚠️ Could not load {fname}: {e}")
            continue

    if not rides:
        st.warning("No rides available. Try syncing with Strava.")
        return

    # ----------------------------------------------------------
    # 📅 SORT RIDES BY DATE (DESC)
    # ----------------------------------------------------------
    df = pd.DataFrame(rides)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.sort_values("date", ascending=False)

    st.markdown("### Recent Rides")

    # ----------------------------------------------------------
    # 🔍 SEARCH + FILTER BAR
    # ----------------------------------------------------------
    with st.expander("🔎 Filter Rides"):
        col1, col2, col3 = st.columns(3)
        name_filter = col1.text_input("Search by Name")
        min_distance = col2.number_input("Min Distance (km)", min_value=0.0, value=0.0, step=10.0)
        min_power = col3.number_input("Min Power (W)", min_value=0, value=0, step=10)

        if name_filter:
            df = df[df["name"].str.contains(name_filter, case=False, na=False)]
        df = df[df["distance_km"] >= min_distance]
        df = df[df["avg_power"] >= min_power]

    # ----------------------------------------------------------
    # 📋 RENDER RIDE CARDS
    # ----------------------------------------------------------
    for idx, row in df.iterrows():
        ride_id = row["id"]
        ride_name = row["name"]
        date_str = (
            row["date"].strftime("%b %d, %Y") if isinstance(row["date"], datetime) else "Unknown"
        )

        np_str = f" | NP: {row['np_power']} W" if row.get("np_power") else ""
        tss_str = f" | TSS: {row['tss']}" if row.get("tss") else ""

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
                ⚡ {row['avg_power']} W | ⏱ {row['moving_time_min']} min{np_str}{tss_str}
            </div>
        </div>
        """

        c1, c2 = st.columns([10, 1])
        with c1:
            st.markdown(card_html, unsafe_allow_html=True)
        with c2:
            if st.button("🔍", key=f"analyze_{ride_id}", help=f"Analyze {ride_name}"):
                st.session_state["selected_ride_path"] = row["path"]
                st.session_state["active_tab"] = "Ride Analysis"
                st.query_params["tab"] = "Ride Analysis"
                st.rerun()
