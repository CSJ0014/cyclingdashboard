import streamlit as st
import os, json
from utils.fit_parser import parse_fit_to_json
from utils.strava_sync import fetch_strava_rides

RAW_DIR = "ride_data/raw"

def render():
    st.title("⬆️ Upload or Sync Rides")
    os.makedirs(RAW_DIR, exist_ok=True)

    if st.button("🔄 Sync from Strava"):
        msg = fetch_strava_rides(after_year=2025)
        st.success(msg)

    files = st.file_uploader("Upload .fit or .json files", type=["fit","json"], accept_multiple_files=True)
    if not files: return
    saved = 0
    for f in files:
        if f.name.endswith(".json"):
            with open(os.path.join(RAW_DIR, f.name),"wb") as w: w.write(f.read()); saved+=1
        else:
            try:
                data = parse_fit_to_json(f)
                out = os.path.join(RAW_DIR, f"activity_{data['_meta']['id']}.json")
                with open(out,"w") as w: json.dump(data,w); saved+=1
            except Exception as e:
                st.error(f"{f.name} failed: {e}")
    st.success(f"✅ Saved {saved} ride(s).")
