# ==============================================================
# 🚴‍♂️ CYCLING COACHING DASHBOARD — MAIN APP (EST + Smart Sync)
# ==============================================================

import streamlit as st
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import time

# --- Import Tabs ---
from tabs import ride_upload, ride_history, ride_analysis, training_pmc, analytics, settings

# --- Import Strava Sync Utilities ---
from utils.strava_sync import fetch_strava_rides, auto_sync_if_ready, reconnect_prompt


# ==============================================================
# 🔄  Auto Strava Sync Sidebar with Visual Feedback
# ==============================================================

def auto_sync_sidebar():
    """Runs Strava auto-sync once per session, shows progress + EST timestamps."""
    with st.sidebar:
        st.markdown("### 🔄 Strava Sync Status")

        # Load previous sync time if any
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

        # --- Manual refresh button ---
        if st.button("🔁 Refresh Now"):
            with st.spinner("Syncing latest rides from Strava..."):
                try:
                    msg = fetch_strava_rides(after_year=2025)
                    time.sleep(1.5)  # smooth UI delay
                    st.success(msg)
                    last_sync = datetime.now(timezone.utc)
                    st.session_state["last_sync_time"] = last_sync
                except Exception as e:
                    st.error(f"⚠️ Manual sync failed: {e}")

        # --- Display time of last sync (in Eastern Time) ---
        if last_sync:
            local_time = last_sync.astimezone(ZoneInfo("America/New_York"))
            st.markdown(
                f"✅ **Last synced:** {local_time.strftime('%Y-%m-%d %I:%M %p %Z')}**"
            )
        else:
            st.markdown("_No sync record found yet._")

        # --- Reconnect prompt if needed ---
        if st.session_state.get("STRAVA_AUTH_REQUIRED"):
            reconnect_prompt()


# ==============================================================
# 🧭  Main Navigation Tabs
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

# --- Initialize default active tab ---
if "active_tab" not in st.session_state:
    st.session_state["active_tab"] = "🚴 Ride History"

# --- Show Auto Sync Sidebar ---
auto_sync_sidebar()

# --- Sidebar tab navigation ---
selection = st.sidebar.radio(
    "Select a section:",
    list(TABS.keys()),
    index=list(TABS.keys()).index(st.session_state["active_tab"]),
)

# --- Render selected tab ---
st.session_state["active_tab"] = selection
TABS[selection].render()


# ==============================================================
# ✅ Footer
# ==============================================================

st.sidebar.markdown("---")
st.sidebar.caption(
    "© 2025 Cycling Coaching Dashboard — built for performance insights and athlete growth."
)
