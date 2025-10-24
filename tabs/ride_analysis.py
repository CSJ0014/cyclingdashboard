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
        st.warning("No valid data in this ride.")
        return

    df["minutes"] = df["time"] / 60

    # --- Card: Summary ---
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🚴 Ride Summary")
    cols = st.columns(3)
    cols[0].metric("Distance", f"{df['distance_mi'].iloc[-1]:.2f} mi")
    cols[1].metric("Duration", f"{df['minutes'].iloc[-1]:.1f} min")
    cols[2].metric("Avg Power", f"{np.mean(df['power']):.0f} W" if "power" in df else "—")
    st.markdown('</div>', unsafe_allow_html=True)

    # --- Card: Graphs ---
    with st.expander("📈 View Detailed Graphs", expanded=True):
        st.markdown('<div class="card">', unsafe_allow_html=True)

        if "power" in df:
            fig = px.line(df, x="minutes", y="power", title="Power (W)")
            st.plotly_chart(fig, use_container_width=True)

        if "heart_rate" in df:
            fig = px.line(df, x="minutes", y="heart_rate", title="Heart Rate (bpm)")
            st.plotly_chart(fig, use_container_width=True)

        if "speed_mph" in df:
            fig = px.line(df, x="minutes", y="speed_mph", title="Speed (mph)")
            st.plotly_chart(fig, use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # --- Card: Action Buttons ---
    st.markdown('<div class="card">', unsafe_allow_html=True)
    cols = st.columns([1,1,4])
    with cols[0]:
        st.button("📄 Export Report")
    with cols[1]:
        st.button("🗑️ Delete Ride")
    st.markdown('</div>', unsafe_allow_html=True)
