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

def detect_training_phases(df):
    """Label training blocks (Base, Build, Peak, Recovery) based on CTL and TSB."""
    if len(df) < 21:
        df["Phase"] = "Insufficient Data"
        return df

    phases = []
    for i in range(len(df)):
        ctl_trend = df["CTL"].iloc[max(0, i - 14):i + 1].diff().mean()
        tsb_val = df["TSB"].iloc[i]

        if ctl_trend < -0.1 and tsb_val > 5:
            phase = "Recovery"
        elif ctl_trend > 0.15 and tsb_val < -5:
            phase = "Build"
        elif ctl_trend > 0.05 and tsb_val > -5 and tsb_val <= 5:
            phase = "Base"
        elif ctl_trend < 0.1 and tsb_val > 5:
            phase = "Peak"
        else:
            phase = "Unclassified"

        phases.append(phase)

    df["Phase"] = phases
    return df

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

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])

    # Detect training phases
    df = detect_training_phases(df)

    # --- Weekly Aggregation ---
    df["week"] = df["date"].dt.to_period("W").apply(lambda r: r.start_time)
    weekly = df.groupby("week").agg(
        {"tss": "sum", "CTL": "last", "ATL": "last", "TSB": "last"}
    ).reset_index()
    weekly["Zone"], weekly["Color"] = zip(*weekly["TSB"].map(classify_tsb))

    # --- Weekly Summary ---
    st.subheader("📅 Weekly Training Load Summary")
    st.dataframe(
        weekly.tail(10)
        .style.format({"tss": "{:.0f}", "CTL": "{:.1f}", "ATL": "{:.1f}", "TSB": "{:.1f}"})
        .apply(lambda s: [f"background-color: {c}" for c in weekly["Color"]], axis=1)
    )

    # --- PMC Chart ---
    st.subheader("📊 Performance Management Chart (CTL/ATL/TSB + TSS)")
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df["date"], y=df["tss"], name="TSS", marker_color="lightblue", yaxis="y2"))
    fig.add_trace(go.Scatter(x=df["date"], y=df["CTL"], mode="lines", name="CTL (Fitness)", line=dict(color="#2ecc71", width=3)))
    fig.add_trace(go.Scatter(x=df["date"], y=df["ATL"], mode="lines", name="ATL (Fatigue)", line=dict(color="#e67e22", width=2)))
    fig.add_trace(go.Scatter(x=df["date"], y=df["TSB"], mode="lines", name="TSB (Form)", line=dict(color="#3498db", width=2, dash="dot")))
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

    # --- Phase Visualization ---
    st.subheader("📆 Training Phase Timeline")
    phase_colors = {
        "Base": "#2980b9",
        "Build": "#e67e22",
        "Peak": "#9b59b6",
        "Recovery": "#2ecc71",
        "Unclassified": "#95a5a6",
        "Insufficient Data": "#bdc3c7"
    }
    phase_df = df.groupby("Phase")["date"].count().reset_index().rename(columns={"date": "Days"})
    st.dataframe(phase_df)

    phase_chart = go.Figure()
    for phase, color in phase_colors.items():
        phase_subset = df[df["Phase"] == phase]
        if not phase_subset.empty:
            phase_chart.add_trace(go.Scatter(
                x=phase_subset["date"], y=phase_subset["CTL"],
                mode="lines", name=phase,
                line=dict(width=4, color=color)
            ))
    phase_chart.update_layout(
        title="Training Phase Progression (by CTL)",
        yaxis_title="CTL (Fitness)",
        xaxis_title="Date",
        height=400,
        template="plotly_white"
    )
    st.plotly_chart(phase_chart, use_container_width=True)

    # --- Coaching Insights ---
    st.subheader("💬 Coaching Insights")
    insights = interpret_training_state(df)
    st.markdown(insights)

    # --- Summary Metrics ---
    st.divider()
    st.metric("Fitness (CTL)", f"{df['CTL'].iloc[-1]:.1f}")
    st.metric("Fatigue (ATL)", f"{df['ATL'].iloc[-1]:.1f}")
    st.metric("Form (TSB)", f"{df['TSB'].iloc[-1]:.1f}")
    st.metric("Current Phase", df["Phase"].iloc[-1])
    st.success("✅ Training log updated with phase detection and advanced analysis!")
