# ==============================================================
# 🚴 CYCLING COACHING DASHBOARD — Material Design 3 (Bright Red)
# ==============================================================

import importlib.util
import streamlit as st
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import os

# ==============================================================
# 🎨 IMPORT THEME & STRAVA UTILS
# ==============================================================

from utils.strava_sync import fetch_strava_rides, auto_sync_if_ready, reconnect_prompt
from tabs import ride_upload, ride_history, ride_analysis, training_pmc, analytics, settings

# ==============================================================
# ⚙️ PAGE CONFIG
# ==============================================================

st.set_page_config(page_title="Cycling Coaching Dashboard", layout="wide")

# ==============================================================
# 🎨 MATERIAL WEB COMPONENTS & THEME
# ==============================================================

st.markdown(
    """
    <!-- Load Material Web library -->
    <script type="module" src="https://esm.run/@material/web/all.js"></script>

    <!-- Material Design 3 Red Theme -->
    <style>
      :root {
        --md-sys-color-primary: #d32f2f;
        --md-sys-color-on-primary: #ffffff;
        --md-sys-color-primary-container: #ffdad4;
        --md-sys-color-on-primary-container: #410001;
        --md-sys-color-secondary: #ba1a1a;
        --md-sys-color-on-secondary: #ffffff;
        --md-sys-color-surface: #ffffff;
        --md-sys-color-surface-variant: #f8f8f8;
        --md-sys-color-outline: #d0d0d0;
        --md-sys-color-on-surface: #1d1b20;
        --md-sys-color-on-surface-variant: #49454f;
        --md-sys-typescale-title-medium-size: 1rem;
      }

      body {
        font-family: 'Google Sans', Roboto, sans-serif;
        background-color: var(--md-sys-color-surface);
        color: var(--md-sys-color-on-surface);
      }

      /* Top App Bar */
      .top-bar {
        position: sticky;
        top: 0;
        z-index: 100;
        width: 100%;
        background: var(--md-sys-color-primary);
        color: var(--md-sys-color-on-primary);
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.75rem 1.5rem;
        box-shadow: 0 2px 6px rgba(0,0,0,0.25);
      }

      .top-bar-title {
        font-weight: 600;
        font-size: 1.2rem;
        letter-spacing: 0.02em;
      }

      /* Tabs */
      .tabs-container {
        background: var(--md-sys-color-surface-variant);
        display: flex;
        justify-content: center;
        border-bottom: 1px solid var(--md-sys-color-outline);
        gap: 0.75rem;
        padding: 0.5rem 0;
      }

      md-filled-button {
        --md-filled-button-container-color: var(--md-sys-color-primary);
        --md-filled-button-label-text-color: var(--md-sys-color-on-primary);
        margin: 0 0.25rem;
      }

      md-filled-button.active {
        --md-filled-button-container-color: var(--md-sys-color-primary-container);
        --md-filled-button-label-text-color: var(--md-sys-color-on-primary-container);
      }

      /* Content fade transition */
      .fade-in {
        animation: fadeIn 0.3s ease both;
      }
      @keyframes fadeIn {
        from { opacity: 0; transform: translateY(6px); }
        to { opacity: 1; transform: none; }
      }

      /* Floating Action Button */
      .fab {
        position: fixed;
        bottom: 24px;
        right: 24px;
        z-index: 99;
      }

      .fab md-fab {
        --md-fab-container-color: var(--md-sys-color-primary);
        --md-fab-icon-color: var(--md-sys-color-on-primary);
      }
    </style>
    """,
    unsafe_allow_html=True,
)

/* ======== Material Web Tabs Styling ======== */
.tabs-container {
  background: var(--md-sys-color-surface-variant);
  border-bottom: 1px solid var(--md-sys-color-outline);
  padding: 0.25rem 1.5rem;
  display: flex;
  justify-content: center;
  align-items: center;
}

md-tabs {
  width: 100%;
  max-width: 1000px;
  --md-tabs-active-indicator-color: var(--md-sys-color-primary);
  --md-primary-tab-active-label-text-color: var(--md-sys-color-primary);
  --md-primary-tab-label-text-color: var(--md-sys-color-on-surface-variant);
}

md-primary-tab {
  font-weight: 600;
  text-transform: none;
  font-size: 0.95rem;
}

md-primary-tab.active {
  --md-primary-tab-active-label-text-color: var(--md-sys-color-primary);
}


# ==============================================================
# 🧭 TOP NAVIGATION BAR
# ==============================================================

TABS = {
    "Ride Upload": ride_upload,
    "Ride History": ride_history,
    "Ride Analysis": ride_analysis,
    "Training PMC": training_pmc,
    "Analytics": analytics,
    "Settings": settings,
}

if "active_tab" not in st.session_state:
    st.session_state["active_tab"] = "Ride History"

# --- Top Bar ---
st.markdown(
    """
    <div class="top-bar">
      <div class="top-bar-title">Cycling Coaching Dashboard</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- Material Web Top Navigation (Refined MD3 Style) ---
tab_html = """
<div class="tabs-container">
  <md-tabs>
"""
for name in TABS.keys():
    active = "active" if st.session_state["active_tab"] == name else ""
    tab_html += f"""
    <md-primary-tab
      class="{active}"
      label="{name}"
      onclick="window.location.search='?tab={name}'">
    </md-primary-tab>
    """
tab_html += """
  </md-tabs>
</div>
"""
st.markdown(tab_html, unsafe_allow_html=True)

# ==============================================================
# 📊 RENDER CURRENT TAB
# ==============================================================

st.markdown("<div class='fade-in'>", unsafe_allow_html=True)
TABS[st.session_state["active_tab"]].render()
st.markdown("</div>", unsafe_allow_html=True)

# ==============================================================
# 🔄 FLOATING ACTION BUTTON
# ==============================================================

st.markdown(
    """
    <div class="fab" onclick="window.location.reload()" title="Refresh Strava Data">
      <md-fab label="Sync" icon="sync"></md-fab>
    </div>
    """,
    unsafe_allow_html=True,
)

# ==============================================================
# 🧾 SIDEBAR FOOTER & STRAVA SYNC STATUS
# ==============================================================

with st.sidebar:
    st.subheader("Strava Sync")
    try:
        msg = auto_sync_if_ready()
        st.success(msg)
    except Exception as e:
        st.error(f"⚠️ Auto-sync failed: {e}")
    if st.session_state.get("STRAVA_AUTH_REQUIRED"):
        reconnect_prompt()
    st.markdown("---")
    st.caption("© 2025 Cycling Coaching Dashboard · Material Design 3 Edition · Bright Red Theme")
