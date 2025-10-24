import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.metrics import build_tss_dataframe, get_all_ride_files

def classify_tsb(tsb):
    if tsb > 10:
        return "Fresh", "#2ecc71"
    elif tsb > 0:
        return "Neutral", "#f1c40f"
    elif tsb > -10:
        return "Tired", "#e67e22"
    else:
        return "Fatigued", "#e74c3c"

def interpret_training_state(df):
    if df.empty:
        return "No training data available."
    latest = df.iloc[-1]
    ctl, atl, tsb = latest["CTL"], latest["ATL"], latest["TSB"]
    if tsb > 10:
        state, msg = "fresh and well-recovered", "Ideal time for a key session or race."
    elif 0 < tsb <= 10:
        state, msg = "balanced", "You can maintain or slightly increase training load."
    elif -10 <= tsb <= 0:
        state, msg = "slightly fatigued", "Consider a recovery spin or endurance ride."
    else:
        state, msg = "fatigued", "Take rest before your next intense session."
    return f"📊 You are **{state}**.\n\n💬 {msg}\n\nCTL: **{ctl:.1f}**, ATL: **{atl:.1f}**, TSB: **{tsb:.1f}**"

def detect_phases(df):
    if len(df) < 21:
        df["Phase"] = "Insufficient Data"
        return df
    phases = []
    for i in range(len(df)):
        ctl_trend = df["CTL"].iloc[max(0, i-14):i+1].diff().mean()
        tsb_val = df["TSB"].iloc[i]
        if ctl_trend < -0.1 and tsb_val > 5:
            phase = "Recovery"
        elif ctl_trend > 0.15 and tsb_val < -5:
            phase = "Build"
        elif ctl_trend > 0.05 and -5 <= tsb_val <= 5:
            phase = "Base"
        elif ctl_trend < 0.1 and tsb_val > 5:
            phase = "Peak"
        else:
            phase = "Unclassified"
        phases.append(phase)
    df["Phase"] = phases
    return df

def render():
    st.title("📈 Training Load & Performance Dashboard")
    ftp = st.session_state.get("FTP_DEFAULT", 222)
    rides = get_all_ride_files()
    if not rides:
        st.info("No rides found. Sync from Strava or upload FIT files.")
        return

    df = build_tss_dataframe(rides, ftp=ftp)
    if df.empty:
        st.warning("No valid ride data found.")
        return

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])
    df = detect_phases(df)
    df["week"] = df["date"].dt.to_period("W").apply(lambda r: r.start_time)
    weekly = df.groupby("week").agg({"tss": "sum","CTL":"last","ATL":"last","TSB":"last"}).reset_index()
    weekly["Zone"], weekly["Color"] = zip(*weekly["TSB"].map(classify_tsb))

    # Filters
    st.subheader("📅 Weekly Training Summary")
    col1,col2,col3 = st.columns(3)
    with col1:
        phase_filter = st.selectbox("🧩 Phase",["All"]+sorted(df["Phase"].unique()),0)
    with col2:
        zone_filter = st.selectbox("💡 Zone",["All"]+sorted(weekly["Zone"].unique()),0)
    with col3:
        sort_by = st.selectbox("↕️ Sort by",["Date","TSS","CTL","ATL","TSB"],0)

    filtered = weekly.copy()
    if phase_filter!="All":
        filtered = filtered[filtered["week"].isin(df[df["Phase"]==phase_filter]["week"])]
    if zone_filter!="All":
        filtered = filtered[filtered["Zone"]==zone_filter]
    filtered = filtered.sort_values("week" if sort_by=="Date" else sort_by.lower(), ascending=False)

    # Phase Breakdown
    st.markdown("#### 🧱 Phase Breakdown")
    phase_counts = df["Phase"].value_counts().to_dict()
    chips = "  ".join([f"✅ **{k}:** {v} days" for k,v in phase_counts.items() if k not in ["Unclassified","Insufficient Data"]])
    st.markdown(chips or "_No classified phases yet._")

    # Color rows
    def highlight_rows(row): return [f"background-color: {row['Color']}"]*len(row)
    styled = filtered.tail(15).style.format({"tss":"{:.0f}","CTL":"{:.1f}","ATL":"{:.1f}","TSB":"{:.1f}"}).apply(highlight_rows,axis=1)
    st.dataframe(styled, use_container_width=True)

    # PMC Chart
    st.subheader("📊 Performance Management Chart")
    fig = go.Figure()
    fig.add_bar(x=df["date"], y=df["tss"], name="TSS", marker_color="lightblue", yaxis="y2")
    fig.add_scatter(x=df["date"], y=df["CTL"], mode="lines", name="CTL", line=dict(color="#2ecc71",width=3))
    fig.add_scatter(x=df["date"], y=df["ATL"], mode="lines", name="ATL", line=dict(color="#e67e22",width=2))
    fig.add_scatter(x=df["date"], y=df["TSB"], mode="lines", name="TSB", line=dict(color="#3498db",width=2,dash="dot"))
    fig.update_layout(yaxis=dict(title="CTL / ATL / TSB"),yaxis2=dict(title="TSS",overlaying="y",side="right"),height=600,template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

    # Phase Chart
    st.subheader("📆 Phase Timeline (by CTL)")
    phase_colors={"Base":"#2980b9","Build":"#e67e22","Peak":"#9b59b6","Recovery":"#2ecc71","Unclassified":"#95a5a6"}
    fig2=go.Figure()
    for phase,color in phase_colors.items():
        sub=df[df["Phase"]==phase]
        if not sub.empty:
            fig2.add_scatter(x=sub["date"],y=sub["CTL"],mode="lines",name=phase,line=dict(width=4,color=color))
    fig2.update_layout(height=400,template="plotly_white")
    st.plotly_chart(fig2,use_container_width=True)

    st.subheader("💬 Coaching Insights")
    st.markdown(interpret_training_state(df))
    st.divider()
    st.metric("Fitness (CTL)",f"{df['CTL'].iloc[-1]:.1f}")
    st.metric("Fatigue (ATL)",f"{df['ATL'].iloc[-1]:.1f}")
    st.metric("Form (TSB)",f"{df['TSB'].iloc[-1]:.1f}")
    st.metric("Current Phase",df["Phase"].iloc[-1])
    st.success("✅ Training log updated successfully.")
