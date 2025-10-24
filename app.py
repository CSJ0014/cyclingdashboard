# ==============================================================
# 🚴 CYCLING COACHING DASHBOARD — Material 3 Replica (Bright Red)
# ==============================================================

import streamlit as st
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import os

from utils.strava_sync import fetch_strava_rides, auto_sync_if_ready, reconnect_prompt
from tabs import (
    ride_upload,
    ride_history,
    ride_analysis,
    training_pmc,
    analytics,
    settings,
)

# --------------------------------------------------------------
# ⚙️ PAGE CONFIG
# --------------------------------------------------------------
st.set_page_config(page_title="Cycling Coaching Dashboard", layout="wide")

# --------------------------------------------------------------
# 🎨 MATERIAL 3-STYLE THEME (No JS)
# --------------------------------------------------------------
st.markdown(
    """
    <style>
    :root {
      --md3-primary: #d32f2f;
      --md3-on-primary: #ffffff;
      --md3-surface: #ffffff;
      --md3-surface-variant: #f5f5f5;
      --md3-outline: #d0d0d0;
      --md3-on-surface: #1d1b20;
      --md3-on-surface-variant: #49454f;
      --md3-radius: 10px;
      --md3-shadow: 0 2px 6px rgba(0,0,0,0.15);
      --md3-transition: all 0.25s ease;
    }

    body {
      font-family: "Google Sans", Roboto, sans-serif;
      background: var(--md3-surface);
      color: var(--md3-on-surface);
    }

    /* ---- Top App Bar ---- */
    .top-bar {
      position: sticky; top: 0; z-index: 100;
      width: 100%;
      background: var(--md3-primary);
      color: var(--md3-on-primary);
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

    /* ---- Tabs ---- */
    .tabs {
      display: flex;
      justify-content: center;
      background: var(--md3-surface-variant);
      border-bottom: 1px solid var(--md3-outline);
      gap: 0.5rem;
      padding: 0.5rem;
      flex-wrap: wrap;
    }
    .tab-btn {
      border: none;
      background: none;
      color: var(--md3-on-surface-variant);
      padding: 0.5rem 1rem;
      border-radius: var(--md3-radius);
      font-weight: 600;
      cursor: pointer;
      transition: var(--md3-transition);
      position: relative;
    }
    .tab-btn:hover {
      background: rgba(0,0,0,0.05);
    }
    .tab-btn.active {
      color: var(--md3-primary);
      background: rgba(211,47,47,0.1);
      box-shadow: inset 0 -2px 0 var(--md3-primary);
    }

    /* ---- Fade Animation ---- */
    .fade-in {
      animation: fadeIn 0.3s ease both;
    }
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(6px); }
      to { opacity: 1; transform: none; }
    }

    /* ---- Floating Action Button ---- */
    .fab {
      position: fixed;
      bottom: 24px;
      right: 24px;
      z-index: 99;
      background: var(--md3-primary);
      color: var(--md3-on-primary);
      border-radius: 50%;
      width: 56px; height: 56px;
      display: flex; align-items: center; justify-content: center;
      font-size: 24px;
      box-shadow: var(--md3-shadow);
      cursor: pointer;
      transition: var(--md3-transition);
    }
    .fab:hover {
      background: #b71c1c;
      transform: scale(1.05);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------------------
# 🧭 TABS SETUP
# --------------------------------------------------------------
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

# ---- Top Bar ----
st.markdown(
    """
    <div class="top-bar">
      <div class="top-bar-title">Cycling Coaching Dashboard</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---- Material 3-Styled Tabs (Pure HTML) ----
tab_html = '<div class="tabs">'
for name in TABS.keys():
    active = "active" if st.session_state["active_tab"] == name else ""
    tab_html += f"""
    <button class="tab-btn {active}" onclick="window.location.search='?tab={name}'">
      {name}
    </button>
    """
tab_html += "</div>"
st.markdown(tab_html, unsafe_allow_html=True)

# ---- URL + Session State Sync ----
query_params = st.query_params
if "tab" in query_params and query_params["tab"] in TABS:
    st.session_state["active_tab"] = query_params["tab"]
    st.query_params["tab"] = query_params["tab"]
else:
    st.query_params["tab"] = st.session_state["active_tab"]

# --------------------------------------------------------------
# 📊 RENDER SELECTED TAB
# --------------------------------------------------------------
st.markdown("<div class='fade-in'>", unsafe_allow_html=True)
TABS[st.session_state["active_tab"]].render()
st.markdown("</div>", unsafe_allow_html=True)

# --------------------------------------------------------------
# 🔄 FLOATING ACTION BUTTON
# --------------------------------------------------------------
st.markdown(
    """
    <div class="fab" onclick="window.location.reload()" title="Refresh Strava Data">⟳</div>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------------------
# 🧾 SIDEBAR FOOTER & STRAVA STATUS
# --------------------------------------------------------------
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
    st.caption("© 2025 Cycling Coaching Dashboard · Material 3 Bright Red Edition (Static CSS)")
