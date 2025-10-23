import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from utils.metrics import build_tss_dataframe, get_all_ride_files

def classify_tsb(tsb):
    """Return freshness zone color and label for TSB (Training Stress Balance)."""
    if tsb > 10:
        return "Fresh", "#2ecc71"  # green
    elif tsb > 0:
        return "Neutral", "#f1c40f"  # yellow
    elif tsb > -10:
        return "Tired", "#e67e22"  # orange
    else:
        return "Fatigued", "#e74c3c"  # red

def interpret_training_state(df):
    """Generate coaching insight text based on latest ATL, CTL, and TSB."""
    if df.empty:
        return "No training data available yet."

    latest = df.iloc[-1]
    ctl, atl, tsb = latest["CTL"], latest["ATL"], latest["TSB"]

    # Coaching logic
    if tsb > 10:
        status = "fresh and well-recovered"
        suggestion = "This is an excellent time to schedule a key workout or race."
    elif 0 < tsb <= 10:
        status = "balanced and ready for moderate training"
        suggestion = "You can maintain this level with controlled load."
    elif -10 <= tsb <= 0:
        status = "slightly fatigued"
        suggestion = "Consider a light recovery spin or endurance ride."
    else:
        status = "fatigued"
        suggestion = "Take a rest day or recovery block before resuming high intensity."

    return (
        f"📊 **Current Training Status:** You are **{status}**.\n\n"
        f"💬 **Coach's Note:** {suggestion}\n\n"
        f"📈 CTL (Fitness): **{ctl:.1f}**, ATL (Fatigue): **{atl:.1f}**, TSB (Freshness): **{tsb:.1f}**"
    )

def render():
    st.title("📈 Training Load & Performance Management Dashboard")

    ftp = st.session_state.get("FTP_DEFAULT", 222)
    rides = get_all_ride_files()
    if not rides:
        st.info("No rides found. Sync from Strava or upload FIT files first.")
        return

    df = build_tss_dataframe(rides, ftp=ftp)
    if df.empty:
        st.warning("No valid rides with dates found.")
        return

    # Weekly summary
    df["week"] = df["date"].dt.to_period("W").apply(lambda r: r.start_time)
    weekly = df.groupby("week").agg({"tss": "sum", "CTL": "last", "ATL": "last", "TSB": "last"}).reset_index()
    weekly["Zone"], weekly["Color"] = zip(*weekly["TSB"].map(classify_tsb))

    # --- Weekly TSS Trend ---
    st.subheader("📅 Weekly Training Load Summary")
    st.dataframe(
        weekly.tail(10)
        .style.format({"tss": "{:.0f}", "CTL": "{:.1f}", "ATL": "{:.1f}", "TSB": "{:.1f}"})
        .apply(lambda s: [f"background-color: {c}" for c in weekly["Color"]], axis=1)
    )

    # --- Combined PMC Chart ---
    st.subheader("📊 Performance Management Chart (CTL/ATL/TSB + TSS)")
    fig = go.Figure()

    # Bars for daily TSS
    fig.add_trace(go.Bar(x=df["date"], y=df["tss"], name="TSS", marker_color="lightblue", yaxis="y2"))

    # Lines for CTL, ATL, TSB
    fig.add_trace(go.Scatter(x=df["date"], y=df["CTL"], mode="lines", name="CTL (Fitness)", line=dict(color="#2ecc71", width=3)))
    fig.add_trace(go.Scatter(x=df["date"], y=df["ATL"], mode="lines", name="ATL (Fatigue)", line=dict(color="#e67e22", width=2)))
    fig.add_trace(go.Scatter(x=df["date"], y=df["TSB"], mode="lines", name="TSB (Form)", line=dict(color="#3498db", width=2, dash="dot")))

    # Layout
    fig.update_layout(
        yaxis=dict(title="CTL / ATL / TSB", side="left"),
        yaxis2=dict(title="TSS", overlaying="y", side="right"),
        xaxis_title="Date",
        legend_title="Metrics",
        bargap=0.25,
        height=600,
        template="plotly_white"
    )
    st.plotly_chart(fig, use_container_width=True)

    # --- Fatigue Zone Trend ---
    st.subheader("🩸 Fatigue & Freshness Zones")
    zone_df = weekly[["week", "TSB", "Zone", "Color"]].copy()
    fig_zones = go.Figure()
    fig_zones.add_trace(go.Bar(
        x=zone_df["week"], y=zone_df["TSB"], marker_color=zone_df["Color"],
        text=zone_df["Zone"], name="TSB Zone", hovertemplate="Week: %{x}<br>TSB: %{y:.1f}<br>Zone: %{text}"
    ))
    fig_zones.add_hline(y=0, line_color="black", line_dash="dot")
    fig_zones.update_layout(
        yaxis_title="TSB (Training Stress Balance)",
        xaxis_title="Week",
        height=400,
        template="plotly_white"
    )
    st.plotly_chart(fig_zones, use_container_width=True)

    # --- Coaching Analysis ---
    st.subheader("💬 Coaching Insights")
    insights = interpret_training_state(df)
    st.markdown(insights)

    # --- Summary Metrics ---
    st.divider()
    st.metric("Fitness (CTL)", f"{df['CTL'].iloc[-1]:.1f}")
    st.metric("Fatigue (ATL)", f"{df['ATL'].iloc[-1]:.1f}")
    st.metric("Form (TSB)", f"{df['TSB'].iloc[-1]:.1f}")
    st.success("✅ Training log updated successfully with detailed coaching insights!")
