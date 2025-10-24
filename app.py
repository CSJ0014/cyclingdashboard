# ==============================================================
# 🚴 CYCLING COACHING DASHBOARD — Material Design 3 Replica
# Bright Red Theme · Streamlit-Safe Implementation
# ==============================================================

import streamlit as st
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from utils.md3_components import inject_md3_stylesheet

# Load Material Design 3 theme
inject_md3_stylesheet()

# ---- Internal imports ----
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
# ⚙️ PAGE CONFIGURATION
# --------------------------------------------------------------
st.set_page_config(page_title="Cycling Coaching Dashboard", layout="wide")

# --------------------------------------------------------------
# 🎨 MATERIAL 3-STYLE THEME (BRIGHT RED)
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
    }

    html, body, [class*="block-container"] {
      background-color: var(--md3-surface);
      color: var(--md3-on-surface);
      font-family: "Google Sans", Roboto, sans-serif;
    }

    /* ---- TOP BAR ---- */
    .top-bar {
      position: sticky; top: 0; z-index: 100;
      width: 100%;
      background: var(--md3-primary);
      color: var(--md3-on-primary);
      display: flex; align-items: center; justify-content: space-between;
      padding: 0.8rem 1.5rem;
      box-shadow: 0 2px 6px rgba(0,0,0,0.25);
    }
    .top-bar-title {
      font-weight: 600;
      font-size: 1.2rem;
      letter-spacing: 0.02em;
    }

    /* ---- TAB BAR ---- */
    .tab-bar {
      background: var(--md3-surface-variant);
      border-bottom: 1px solid var(--md3-outline);
      padding: 8px 16px;
      display: flex;
      flex-wrap: wrap;
      justify-content: center;
    }

    /* Streamlit buttons inside tab bar */
    .tab-bar div.stButton > button {
      background: transparent;
      color: rgba(0,0,0,0.70);
      border: none;
      border-radius: var(--md3-radius);
      padding: 8px 14px;
      font-weight: 600;
      cursor: pointer;
      transition: background .2s, color .2s;
    }
    .tab-bar div.stButton > button:hover {
      background: rgba(0,0,0,0.06);
    }

    /* Active tab style */
    .tab-active {
      display: inline-block;
      padding: 8px 14px;
      border-radius: var(--md3-radius);
      font-weight: 700;
      color: var(--md3-primary);
      background: rgba(211,47,47,0.10);
      box-shadow: inset 0 -2px 0 var(--md3-primary);
    }

    /* ---- FAB ---- */
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
      box-shadow: 0 2px 6px rgba(0,0,0,0.3);
      cursor: pointer;
      transition: transform .25s, background .25s;
    }
    .fab:hover { transform: scale(1.05); background: #b71c1c; }

    /* ---- ANIMATIONS ---- */
    .fade-in { animation: fadeIn .3s ease both; }
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(6px); }
      to { opacity: 1; transform: none; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------------------
# 🧭 TAB DEFINITIONS
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

# --------------------------------------------------------------
# 🟥 TOP BAR
# --------------------------------------------------------------
st.markdown(
    """
    <div class="top-bar">
      <div class="top-bar-title">Cycling Coaching Dashboard</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------------------
# 🔖 TAB NAVIGATION (Streamlit Buttons)
# --------------------------------------------------------------
tab_names = list(TABS.keys())
active_tab = st.session_state["active_tab"]

st.markdown('<div class="tab-bar">', unsafe_allow_html=True)
cols = st.columns(len(tab_names))

for i, name in enumerate(tab_names):
    with cols[i]:
        if name == active_tab:
            st.markdown(f"<span class='tab-active'>{name}</span>", unsafe_allow_html=True)
        else:
            if st.button(name, key=f"tabbtn_{name}"):
                st.session_state["active_tab"] = name
                st.query_params["tab"] = name
                st.rerun()

st.markdown("</div>", unsafe_allow_html=True)

# ---- Query param sync ----
qp = st.query_params
if "tab" in qp and qp["tab"] in TABS and qp["tab"] != st.session_state["active_tab"]:
    st.session_state["active_tab"] = qp["tab"]
    st.rerun()
else:
    st.query_params["tab"] = st.session_state["active_tab"]

# --------------------------------------------------------------
# 📊 RENDER SELECTED TAB
# --------------------------------------------------------------
st.markdown("<div class='fade-in'>", unsafe_allow_html=True)
TABS[st.session_state["active_tab"]].render()
st.markdown("</div>", unsafe_allow_html=True)

# --------------------------------------------------------------
# 🔄 FLOATING ACTION BUTTON — Refresh
# --------------------------------------------------------------
st.markdown(
    """
    <div class="fab" onclick="window.location.reload()" title="Refresh Strava Data">⟳</div>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------------------
# 🧾 SIDEBAR — Strava Sync Status
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
    st.caption("© 2025 Cycling Coaching Dashboard · Material 3 Bright Red Edition")
