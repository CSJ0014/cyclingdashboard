import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.metrics import build_tss_dataframe, get_all_ride_files

def classify_tsb(tsb):
    if tsb > 10:
        return "Fresh", "#34a853"
    elif tsb > 0:
        return "Neutral", "#fbbc05"
    elif tsb > -10:
        return "Tired", "#f29900"
    else:
        return "Fatigued", "#ea4335"

def render():
    st.title("📈 Training Load & Performance")

    ftp = st.session_state.get("FTP_DEFAULT", 222)
    rides = get_all_ride_files()
    if not rides:
        st.info("No rides found. Sync from Strava or upload FIT files first.")
        return

    df = build_tss_dataframe(rides, ftp=ftp)
    if df.empty:
        st.warning("No valid training data found.")
        return

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])

    df["week"] = df["date"].dt.to_period("W").apply(lambda r: r.start_time)
    weekly = df.groupby("week").agg({"tss":"sum","CTL":"last","ATL":"last","TSB":"last"}).reset_index()
    weekly["Zone"], weekly["Color"] = zip(*weekly["TSB"].map(classify_tsb))

    # --- Card: Weekly Load Chart ---
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📊 Weekly Training Stress Balance (TSB)")
    fig = go.Figure()
    fig.add_scatter(x=weekly["week"], y=weekly["CTL"], mode="lines", name="CTL", line=dict(color="#1a73e8", width=3))
    fig.add_scatter(x=weekly["week"], y=weekly["ATL"], mode="lines", name="ATL", line=dict(color="#f29900", width=2))
    fig.add_scatter(x=weekly["week"], y=weekly["TSB"], mode="lines", name="TSB", line=dict(color="#34a853", width=2, dash="dot"))
    fig.update_layout(template="plotly_white", height=500)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # --- Card: Metrics ---
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📅 Current Training Metrics")
    cols = st.columns(4)
    cols[0].metric("CTL", f"{df['CTL'].iloc[-1]:.1f}")
    cols[1].metric("ATL", f"{df['ATL'].iloc[-1]:.1f}")
    cols[2].metric("TSB", f"{df['TSB'].iloc[-1]:.1f}")
    cols[3].metric("Last TSS", f"{df['tss'].iloc[-1]:.0f}")
    st.markdown('</div>', unsafe_allow_html=True)

    # --- Card: Coaching Summary ---
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("💬 Coaching Summary")

    tsb = df["TSB"].iloc[-1]
    ctl = df["CTL"].iloc[-1]
    atl = df["ATL"].iloc[-1]

    if tsb > 10:
        summary = "You're **fresh and well-rested**. A good time for a key workout or race effort."
    elif tsb > 0:
        summary = "You're **balanced** — continue structured training and monitor fatigue."
    elif tsb > -10:
        summary = "You're **moderately fatigued**. A recovery spin or endurance ride would help."
    else:
        summary = "You're **deep in fatigue**. Prioritize rest or a light active recovery day."

    st.markdown(summary)
    st.markdown('</div>', unsafe_allow_html=True)
