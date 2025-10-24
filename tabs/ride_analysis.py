import streamlit as st
import pandas as pd
import numpy as np
import json, os
import plotly.express as px

RAW_DIR = "ride_data/raw"

def load_ride_json(file):
    path = os.path.join(RAW_DIR, file)
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        return json.load(f)

def render():
    st.title("📊 Ride Analysis")
    selected = st.session_state.get("selected_ride")

    if not selected:
        st.info("Select a ride from the Ride History tab to analyze.")
        return

    data = load_ride_json(selected)
    if not data:
        st.error("Ride file not found.")
        return

    df = pd.DataFrame()
    if "time" in data:
        df["time"] = data["time"]["data"]
    if "distance" in data:
        df["distance_mi"] = np.array(data["distance"]["data"]) / 1609.34
    if "watts" in data:
        df["power"] = data["watts"]["data"]
    if "heartrate" in data:
        df["heart_rate"] = data["heartrate"]["data"]
    if "velocity_smooth" in data:
        df["speed_mph"] = np.array(data["velocity_smooth"]["data"]) * 2.23694

    if df.empty:
        st.warning("No valid data in this file.")
        return

    df["minutes"] = df["time"] / 60
    st.markdown(
        f"**Duration:** {df['minutes'].iloc[-1]:.1f} min "
        f"**Distance:** {df['distance_mi'].iloc[-1]:.2f} mi"
    )

    for col, title, ylab in [
        ("power", "Power (W)", "Watts"),
        ("heart_rate", "Heart Rate (bpm)", "bpm"),
        ("speed_mph", "Speed (mph)", "mph"),
    ]:
        if col in df:
            fig = px.line(df, x="minutes", y=col, title=title, labels={"minutes": "Minutes", col: ylab})
            st.plotly_chart(fig, use_container_width=True)
