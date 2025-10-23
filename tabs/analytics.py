import streamlit as st, plotly.express as px
from utils.data_loader import list_rides, stream_values
def render():
    st.title("📉 Analytics & Insights")
    rides=list_rides()
    if rides.empty: st.info("No rides found."); return
    c1,c2,c3=st.columns(3)
    c1.metric("Total Distance",f"{rides['Distance (mi)'].sum():.1f} mi")
    c2.metric("Avg Power",f"{rides['Avg Power (W)'].mean():.0f} W")
    c3.metric("Avg HR",f"{rides['Avg HR (bpm)'].mean():.0f} bpm")
    hr=stream_values(rides,'heartrate'); pw=stream_values(rides,'watts')
    if hr: st.plotly_chart(px.histogram(x=hr,nbins=24,title='Heart Rate Distribution'),use_container_width=True)
    if pw: st.plotly_chart(px.histogram(x=pw,nbins=24,title='Power Distribution'),use_container_width=True)
