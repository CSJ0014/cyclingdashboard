# ==============================================================
# 🚴‍♂️ CYCLING COACHING DASHBOARD — MAIN APP
# ==============================================================

import streamlit as st
from datetime import datetime, timezone
import time

# --- Import all tabs ---
from tabs import ride_upload, ride_history, ride_analysis, training_pmc, analytics, settings

# --- Strava Utilities ---
from utils.strava_sync import fetch_strava_rides


# ==============================================================
# 🧭 Auto Strava Sync Section (with visual feedback)
# ==============================================================

def auto_sync_sidebar():
    """Display Strava sync status and run auto-sync once per session."""
    with st.sidebar:
        st.markdown("### 🔄 Strava Sync Status")

        # Load previous sync time if any
        last_sync = st.session_state.get("last_sync_time")

        # Run automatic sync on first load
        if "strava_synced" not in st.session_state:
            with st.spinner("Connecting to Strava and checking for new rides..."):
                try:
                    msg = fetch_strava_rides(after_year=2025)
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
                    time.sleep(1.5)  # Small delay for smoother UI feel
                    st.success(msg)
                    last_sync = datetime.now(timezone.utc)
                    st.session_state["last_sync_time"] = last_sync
                except Exception as e:
                    st.error(f"⚠️ Manual sync failed: {e}")

        # --- Show last sync time ---
from datetime import datetime, timezone, timedelta

# Define Eastern Time (UTC-5 or UTC-4 for daylight saving)
eastern_offset = timedelta(hours=-4)  # adjust automatically later if needed

if last_sync:
    est_time = (last_sync + eastern_offset).strftime("%Y-%m-%d %I:%M %p EST")
    st.markdown(f"✅ **Last synced:** {est_time}**")
else:
    st.markdown("_No sync record found yet._")

# --- Run sidebar auto-sync on every load ---
auto_sync_sidebar()


# ==============================================================
# 🧭 Main Navigation Tabs
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

# --- Default active tab (if first session) ---
if "active_tab" not in st.session_state:
    st.session_state["active_tab"] = "🚴 Ride History"

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
