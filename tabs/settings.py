import streamlit as st
import json, os

SETTINGS_FILE = "ride_data/settings.json"

def render():
    st.title("⚙️ Settings")
    st.markdown("Update your default FTP and Max Heart Rate here.")

    ftp = st.number_input("FTP (Functional Threshold Power)", min_value=50, max_value=500, value=222)
    hr_max = st.number_input("Max Heart Rate (bpm)", min_value=120, max_value=220, value=200)

    if st.button("💾 Save Settings"):
        os.makedirs("ride_data", exist_ok=True)
        with open(SETTINGS_FILE, "w") as f:
            json.dump({"FTP_DEFAULT": ftp, "HR_MAX": hr_max}, f, indent=2)
        st.session_state["FTP_DEFAULT"] = ftp
        st.success("Settings saved successfully.")
