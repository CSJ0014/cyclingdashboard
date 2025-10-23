import streamlit as st
import os, json
from utils.fit_parser import parse_fit_to_json

RAW_DIR = "ride_data/raw"

def render():
    st.title("⬆️ Upload Rides")
    os.makedirs(RAW_DIR, exist_ok=True)
    files = st.file_uploader("Upload .fit or .json", type=["fit","json"], accept_multiple_files=True)
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
            except Exception as e: st.error(f"{f.name} failed: {e}")
    st.success(f"Saved {saved} ride(s).")
