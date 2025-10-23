import streamlit as st, pandas as pd, numpy as np, json, os, plotly.express as px
RAW_DIR="ride_data/raw"
def render():
    st.title("📊 Ride Analysis")
    if 'selected_ride' not in st.session_state:
        st.info("Select a ride from history."); return
    path=os.path.join(RAW_DIR,st.session_state['selected_ride'])
    try: data=json.load(open(path))
    except: st.error("Load failed."); return
    meta=data.get('_meta',{})
    name=meta.get('name','Ride'); dist=(meta.get('distance_m',0) or 0)/1609.34; dur=(meta.get('moving_time_s',0) or 0)/60
    st.markdown(f"**{name}** — {dist:.2f} mi | {dur:.1f} min")
    df=pd.DataFrame()
    for k in ['time','watts','heartrate','velocity_smooth','distance']:
        if k in data: df[k]=data[k]['data']
    if 'velocity_smooth' in df: df['speed_mph']=np.array(df['velocity_smooth'])*2.23694
    if 'distance' in df: df['distance_mi']=np.array(df['distance'])/1609.34
    df['minutes']=df['time']/60 if 'time' in df else range(len(df))
    if 'watts' in df: st.plotly_chart(px.line(df,x='minutes',y='watts',title='Power (W)'),use_container_width=True)
    if 'heartrate' in df: st.plotly_chart(px.line(df,x='minutes',y='heartrate',title='Heart Rate (bpm)'),use_container_width=True)
    if 'speed_mph' in df: st.plotly_chart(px.line(df,x='minutes',y='speed_mph',title='Speed (mph)'),use_container_width=True)
