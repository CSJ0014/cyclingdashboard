import streamlit as st
import plotly.express as px
from utils.metrics import build_tss_dataframe, get_all_ride_files

def render():
    st.title("📈 Training Load & PMC (Performance Management Chart)")

    ftp = st.session_state.get("FTP_DEFAULT", 222)
    rides = get_all_ride_files()
    if not rides:
        st.info("No rides found. Sync from Strava or upload FIT files first.")
        return

    df = build_tss_dataframe(rides, ftp=ftp)
    if df.empty:
        st.warning("No valid rides with dates found.")
        return

    st.subheader("📅 Weekly Training Load Summary")
    weekly = df.groupby(df["date"].dt.to_period("W")).agg(
        {"tss": "sum", "CTL": "last", "ATL": "last", "TSB": "last"}
    ).reset_index()
    weekly["date"] = weekly["date"].dt.start_time

    st.dataframe(weekly.tail(10))

    st.subheader("📊 Performance Management Chart")
    fig = px.line(df, x="date", y=["CTL", "ATL", "TSB"],
                  labels={"value": "Score", "date": "Date"},
                  title="Training Load Trends (CTL/ATL/TSB)")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("🚴 TSS Over Time")
    fig2 = px.bar(df, x="date", y="tss", title="Daily Training Stress Score (TSS)",
                  labels={"tss": "TSS", "date": "Date"})
    st.plotly_chart(fig2, use_container_width=True)

    st.success("✅ Training log updated successfully!")
