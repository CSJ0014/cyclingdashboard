import streamlit as st
from tabs import ride_upload, ride_history, ride_analysis, training_pmc, analytics, settings

st.set_page_config(page_title="Cycling Coaching Dashboard", layout="wide")

TABS = {
    "⬆️ Upload Rides": ride_upload,
    "📜 Ride History": ride_history,
    "📊 Ride Analysis": ride_analysis,
    "📈 Training Load (PMC)": training_pmc,
    "📉 Analytics": analytics,
    "⚙️ Settings": settings,
}

if "active_tab" not in st.session_state:
    st.session_state["active_tab"] = "📜 Ride History"

tab_names = list(TABS.keys())
selection = st.sidebar.radio("Navigation", tab_names, index=tab_names.index(st.session_state["active_tab"]))
TABS[selection].render()
