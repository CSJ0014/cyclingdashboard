import streamlit as st, json, os
from utils.strava_sync import connect_strava

SETTINGS_FILE='ride_data/settings.json'

def _load():
    return json.load(open(SETTINGS_FILE)) if os.path.exists(SETTINGS_FILE) else {}

def _save(s):
    os.makedirs('ride_data',exist_ok=True)
    json.dump(s,open(SETTINGS_FILE,'w'),indent=2)

def render():
    st.title("⚙️ Settings")
    s=_load()
    ftp=st.number_input("FTP (Watts)",100,500,int(s.get("FTP",222)))
    hr=st.number_input("Max HR (bpm)",120,220,int(s.get("HR_MAX",200)))
    st.divider()

    if st.button("💾 Save FTP & HR Settings"):
        s.update({"FTP":int(ftp),"HR_MAX":int(hr)})
        _save(s)
        st.session_state["FTP_DEFAULT"]=int(ftp)
        st.success("✅ Settings saved.")

    st.subheader("🔗 Strava Connection")
    st.markdown("[Create a Strava API App](https://www.strava.com/settings/api) to get your credentials.")

    client_id = st.text_input("Strava Client ID", s.get("STRAVA_CLIENT_ID",""))
    client_secret = st.text_input("Strava Client Secret", s.get("STRAVA_CLIENT_SECRET",""), type="password")

    if client_id:
        auth_url = (
            f"https://www.strava.com/oauth/authorize?client_id={client_id}"
            "&response_type=code&redirect_uri=http://localhost/exchange_token"
            "&approval_prompt=force&scope=activity:read_all"
        )
        st.markdown(f"[👉 Click here to authorize on Strava]({auth_url})")

    code = st.text_input("Paste the code from the redirected URL after authorization:")
    if st.button("🔐 Connect to Strava"):
        if not client_id or not client_secret or not code:
            st.warning("Please fill all fields and paste your code.")
        else:
            msg = connect_strava(client_id, client_secret, code)
            st.success(msg)
