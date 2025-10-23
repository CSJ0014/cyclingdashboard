import streamlit as st
from utils.data_loader import list_rides

def render():
    st.title("📜 Ride History")
    rides = list_rides()
    if rides.empty:
        st.info("No rides found.")
        return
    for _, row in rides.iterrows():
        c = st.columns([3,1.5,1.5,1.5,0.6])
        c[0].write(f"**{row['Activity']}**")
        c[1].write(f"{row['Distance (mi)']:.2f} mi")
        c[2].write(f"{row['Avg Power (W)']:.0f} W")
        c[3].write(f"{row['Avg HR (bpm)']:.0f} bpm")
        key=f"v_{row['File'].replace('.json','')}"
        if c[4].button('🔍',key=key):
            st.session_state['selected_ride']=row['File']
            st.session_state['active_tab']='📊 Ride Analysis'
            st.rerun()
