# ==============================================================
# 🚴‍♂️ CYCLING COACHING DASHBOARD — MAIN APP (Dynamic Theme)
# ==============================================================

import importlib.util
import streamlit as st
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import time
import os

# ==============================================================
# 🎨 DYNAMIC THEME LOADER
# ==============================================================

def load_theme():
    """Always load and inject the latest version of the theme file dynamically."""
    theme_path = os.path.join("utils", "css_theme.py")
    if not os.path.exists(theme_path):
        st.warning("⚠️ Theme file missing: utils/css_theme.py")
        return
    spec = importlib.util.spec_from_file_location("css_theme", theme_path)
    css_theme = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(css_theme)
    css_theme.inject_material_theme()

# Inject the most recent theme on app startup
load_theme()

# ==============================================================
# 📦 IMPORT TABS
# ==============================================================

from tabs import (
    ride_upload,
    ride_history,
    ride_analysis,
    training_pmc,
    analytics,
    settings,
)

# ==============================================================
# 🔄 STRAVA INTEGRATION
# ==============================================================

from utils.strava_sync import fetch_strava_rides, auto_sync_if_ready, reconnect_prompt


def auto_sync_sidebar():
    """Sidebar logic for Strava auto-sync + manual refresh."""
    with st.sidebar:
        st.markdown("### 🔄 Strava Sync Status")

        last_sync = st.session_state.get("last_sync_time")

        # Run automatic sync once per session
        if "strava_synced" not in st.session_state:
            with st.spinner("Connecting to Strava and checking for new rides..."):
                try:
                    msg = auto_sync_if_ready()
                    st.success(msg)
                    last_sync = datetime.now(timezone.utc)
                    st.session_state["last_sync_time"] = last_sync
                    st.session_state["strava_synced"] = True
                except Exception as e:
                    st.error(f"⚠️ Auto-sync failed: {e}")

        # Manual refresh button
        if st.button("🔁 Refresh Now"):
            with st.spinner("Syncing latest rides from Strava..."):
                try:
                    msg = fetch_strava_rides(after_year=2025)
                    time.sleep(1.5)
                    st.success(msg)
                    last_sync = datetime.now(timezone.utc)
                    st.session_state["last_sync_time"] = last_sync
                except Exception as e:
                    st.error(f"⚠️ Manual sync failed: {e}")

        # Display time of last sync (in Eastern Time)
        if last_sync:
            local_time = last_sync.astimezone(ZoneInfo("America/New_York"))
            st.markdown(
                f"✅ **Last synced:** {local_time.strftime('%Y-%m-%d %I:%M %p %Z')}**"
            )
        else:
            st.markdown("_No sync record found yet._")

        if st.session_state.get("STRAVA_AUTH_REQUIRED"):
            reconnect_prompt()


# ==============================================================
# 🧭 MAIN NAVIGATION
# ==============================================================

st.sidebar.markdown("---")
st.sidebar.markdown("## 🧭 Navigation")

TABS = {
    "📤 Ride Upload": ride_upload,
    "🚴 Ride History": ride_history,
    "📊 Ride Analysis": ride_analysis,
    "📈 Training PMC": training_pmc,
    "📉 Analytics": analytics,
    "⚙️ Settings": settings,
}

# Initialize default tab
if "active_tab" not in st.session_state:
    st.session_state["active_tab"] = "🚴 Ride History"

# Sidebar sync + navigation
auto_sync_sidebar()
selection = st.sidebar.radio(
    "Select a section:",
    list(TABS.keys()),
    index=list(TABS.keys()).index(st.session_state["active_tab"]),
)

# Save and render current tab
st.session_state["active_tab"] = selection
TABS[selection].render()

# ==============================================================
# ✨ FLOATING ACTION BUTTON (Quick Sync)
# ==============================================================

st.markdown("""
    <div class="fab" onclick="window.location.reload()"
         title="Refresh Strava Data">🔄</div>
""", unsafe_allow_html=True)

# ==============================================================
# 🧾 FOOTER
# ==============================================================

st.sidebar.markdown("---")
st.sidebar.caption(
    "© 2025 Cycling Coaching Dashboard — built with Streamlit, Strava API, and Material Design 3."
)
