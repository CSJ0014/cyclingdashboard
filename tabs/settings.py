import streamlit as st, json, os
SETTINGS_FILE='ride_data/settings.json'
def _load():
    return json.load(open(SETTINGS_FILE)) if os.path.exists(SETTINGS_FILE) else {}
def _save(s):
    os.makedirs('ride_data',exist_ok=True); json.dump(s,open(SETTINGS_FILE,'w'),indent=2)
def render():
    st.title("⚙️ Settings")
    s=_load()
    ftp=st.number_input("FTP (Watts)",100,500,int(s.get("FTP",222)))
    hr=st.number_input("Max HR (bpm)",120,220,int(s.get("HR_MAX",200)))
    st.divider()
    st.caption("Optional: Strava sync utilities available in utils/strava_sync.py")
    if st.button("💾 Save"):
        s.update({"FTP":int(ftp),"HR_MAX":int(hr)}); _save(s)
        st.session_state["FTP_DEFAULT"]=int(ftp)
        st.success("Settings saved.")
