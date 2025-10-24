# ==============================================================
# 🚴 CYCLING COACHING DASHBOARD — Material Design 3 Replica
# Polished Purple Theme · Streamlit-Safe Implementation
# ==============================================================

import streamlit as st
import traceback
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

# ---- Internal Imports ----
from utils.layout import init_layout, end_layout
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
# 🎨 MATERIAL DESIGN 3 PURPLE THEME
# --------------------------------------------------------------
st.markdown(
    """
    <style>
    /* ==========================================================
       Material Design 3 — Streamlit-native Purple Theme
       ========================================================== */
    :root {
      --md3-primary: #6750A4;
      --md3-on-primary: #FFFFFF;
      --md3-surface: #FFFBFE;
      --md3-surface-variant: #F4EFFA;
      --md3-outline: #E0E0E0;
      --md3-on-surface: #1C1B1F;
      --md3-radius: 12px;
    }

    html, body, [class*="block-container"] {
      background-color: var(--md3-surface);
      color: var(--md3-on-surface);
      font-family: "Inter", "Roboto", sans-serif;
    }

    /* ---- TOP BAR ---- */
    .top-bar {
      position: sticky;
      top: 0;
      z-index: 100;
      width: 100%;
      background: var(--md3-surface);
      color: var(--md3-on-surface);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 1rem 2rem;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
      border-bottom: 1px solid var(--md3-outline);
    }
    .top-bar-title {
      font-weight: 600;
      font-size: 1.3rem;
      color: var(--md3-primary);
      letter-spacing: 0.01em;
    }

    /* ---- TAB BAR ---- */
    .tab-bar {
      background: var(--md3-surface-variant);
      border-bottom: 1px solid var(--md3-outline);
      display: flex;
      flex-wrap: wrap;
      justify-content: center;
      padding: 20px 16px 16px 16px; /* adds space below top bar */
      gap: 12px;
      box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }

    /* Streamlit buttons inside tab bar */
    .tab-bar div.stButton > button {
      background: var(--md3-primary);
      color: var(--md3-on-primary);
      border: none;
      border-radius: 24px;
      padding: 10px 18px;
      font-weight: 500;
      box-shadow: 0 1px 2px rgba(0,0,0,0.15);
      transition: all 0.2s ease;
    }
    .tab-bar div.stButton > button:hover {
      box-shadow: 0 4px 8px rgba(0,0,0,0.2);
      transform: translateY(-1px);
      background: #5b43a0;
    }

    /* Active tab style */
    .tab-active {
      display: inline-block;
      padding: 10px 18px;
      border-radius: 24px;
      font-weight: 600;
      color: var(--md3-primary);
      background: #EADDFF;
      border: 2px solid var(--md3-primary);
      box-shadow: 0 3px 6px rgba(0,0,0,0.1);
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
      width: 56px;
      height: 56px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 24px;
      box-shadow: 0 3px 6px rgba(0,0,0,0.3);
      cursor: pointer;
      transition: transform 0.25s, background 0.25s;
    }
    .fab:hover {
      transform: scale(1.05);
      background: #5b43a0;
    }

    /* ---- ANIMATIONS ---- */
    .fade-in {
      animation: fadeIn 0.3s ease both;
    }
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(6px); }
      to   { opacity: 1; transform: none; }
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
# 🟣 TOP BAR
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
# 🔖 TAB NAVIGATION
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
    st.caption("© 2025 Cycling Coaching Dashboard · Material Design 3 Edition")

end_layout()
