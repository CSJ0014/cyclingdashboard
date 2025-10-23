import streamlit as st, plotly.express as px
from utils.data_loader import list_rides
from utils.metrics import build_tss_dataframe
def render():
    st.title("📈 Training Load (PMC)")
    rides=list_rides()
    if rides.empty: st.info("No rides found."); return
    ftp=float(st.session_state.get("FTP_DEFAULT",222))
    df=build_tss_dataframe(rides,ftp=ftp)
    if df.empty: st.warning("Not enough data."); return
    fig=px.line(df,x='date',y=['CTL','ATL','TSB'],title='Performance Management Chart')
    st.plotly_chart(fig,use_container_width=True)
