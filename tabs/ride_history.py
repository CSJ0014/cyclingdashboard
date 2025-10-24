import streamlit as st
import pandas as pd
import os, json

RAW_DIR = "ride_data/raw"

def list_rides():
    rides = []
    if not os.path.exists(RAW_DIR):
        os.makedirs(RAW_DIR)
        return pd.DataFrame()

    for f in sorted(os.listdir(RAW_DIR), reverse=True):
        if f.endswith(".json"):
            path = os.path.join(RAW_DIR, f)
            with open(path, "r") as file:
                data = json.load(file)
            name = data.get("_meta", {}).get("name", "Unnamed Ride")
            distance = data.get("distance", {}).get("data", [])
            distance_mi = round(distance[-1] / 1609.34, 2) if distance else 0
            rides.append({"Activity": name, "File": f, "Distance (mi)": distance_mi})
    return pd.DataFrame(rides)

def render():
    st.title("🚴 Ride History")
    rides = list_rides()

    if rides.empty:
        st.info("No rides found. Sync with Strava or upload files.")
        return

    st.write("Click a ride to analyze it:")
    for _, row in rides.iterrows():
        cols = st.columns([4, 1, 1])
        cols[0].markdown(f"**{row['Activity']}** — {row['Distance (mi)']} mi")
        if cols[1].button("🔍", key=f"analyze_{row['File']}"):
            st.session_state["selected_ride"] = row["File"]
            st.session_state["active_tab"] = "📊 Ride Analysis"
            st.rerun()
        if cols[2].button("🗑️", key=f"delete_{row['File']}"):
            os.remove(os.path.join(RAW_DIR, row["File"]))
            st.success(f"Deleted {row['Activity']}")
            st.rerun()
