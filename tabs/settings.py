import streamlit as st
import json, os

SETTINGS_FILE = "ride_data/settings.json"

def render():
    st.title("⚙️ Settings")

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🔧 Training Zones & Preferences")

    ftp = st.number_input("Functional Threshold Power (FTP)", min_value=50, max_value=500, value=st.session_state.get("FTP_DEFAULT", 222))
    hr_max = st.number_input("Max Heart Rate (bpm)", min_value=120, max_value=220, value=st.session_state.get("HR_MAX", 200))

    if st.button("💾 Save Settings"):
        os.makedirs("ride_data", exist_ok=True)
        with open(SETTINGS_FILE, "w") as f:
            json.dump({"FTP_DEFAULT": ftp, "HR_MAX": hr_max}, f, indent=2)
        st.session_state["FTP_DEFAULT"] = ftp
        st.session_state["HR_MAX"] = hr_max
        st.success("✅ Settings saved successfully.")
    st.markdown('</div>', unsafe_allow_html=True)

    with st.expander("🎨 Theme Preview"):
        st.markdown("Edit colors and layout in `utils/css_theme.py` under each labeled section.")
