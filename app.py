# ==============================================================
# 🚴 CYCLING COACHING DASHBOARD — MATERIAL DESIGN 3 EDITION
# ==============================================================

import importlib.util
import streamlit as st
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import time, os

# ==============================================================
# 🎨 THEME LOADER
# ==============================================================

def load_theme():
    theme_path = os.path.join("utils", "css_theme.py")
    spec = importlib.util.spec_from_file_location("css_theme", theme_path)
    css_theme = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(css_theme)
    css_theme.inject_material_theme()

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

from utils.strava_sync import fetch_strava_rides, auto_sync_if_ready, reconnect_prompt

# ==============================================================
# 🔄 STRAVA SIDEBAR STATUS
# ==============================================================

def strava_status():
    with st.sidebar:
        st.subheader("Strava Sync")
        last_sync = st.session_state.get("last_sync_time")

        if "strava_synced" not in st.session_state:
            try:
                msg = auto_sync_if_ready()
                st.session_state["strava_synced"] = True
                st.session_state["last_sync_time"] = datetime.now(timezone.utc)
                st.success(msg)
            except Exception as e:
                st.error(f"Auto-sync failed: {e}")

        if st.button("Refresh Now", use_container_width=True):
            with st.spinner("Syncing latest rides…"):
                try:
                    msg = fetch_strava_rides(after_year=2025)
                    st.session_state["last_sync_time"] = datetime.now(timezone.utc)
                    st.success(msg)
                except Exception as e:
                    st.error(f"Manual sync failed: {e}")

        if last_sync:
            local = last_sync.astimezone(ZoneInfo("America/New_York"))
            st.caption(f"Last synced {local.strftime('%b %d %I:%M %p %Z')}")
        else:
            st.caption("_No sync record found._")

        if st.session_state.get("STRAVA_AUTH_REQUIRED"):
            reconnect_prompt()

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

st.markdown(
    """
    <style>
    /* ======= Material Design 3 Top Nav Bar ======= */
    .top-nav {
        display:flex;justify-content:space-between;align-items:center;
        background:var(--md-sys-color-surface-variant,#ffffff);
        padding:0.6rem 1.5rem;box-shadow:0 2px 6px rgba(0,0,0,0.08);
        position:sticky;top:0;z-index:999;border-bottom:1px solid rgba(0,0,0,0.1);
    }
    .nav-tabs button{
        background:none;border:none;cursor:pointer;
        padding:0.6rem 1rem;margin:0 0.25rem;
        font-weight:600;font-size:0.95rem;
        color:rgba(0,0,0,0.65);border-radius:0.4rem;
        transition:background 0.2s,color 0.2s;
    }
    .nav-tabs button:hover{background:rgba(0,0,0,0.06);}
    .nav-tabs button.active{
        color:var(--md-sys-color-primary,#0b57d0);
        background:rgba(11,87,208,0.08);
    }
    .brand{
        font-weight:600;font-size:1.1rem;
        color:var(--md-sys-color-primary,#0b57d0);
    }
    .fade-in{animation:fadeIn 0.3s ease both;}
    @keyframes fadeIn{from{opacity:0;transform:translateY(4px);}to{opacity:1;transform:none;}}
    </style>
    """,
    unsafe_allow_html=True,
)

nav_html = "<div class='top-nav'><div class='brand'>Cycling Dashboard</div><div class='nav-tabs'>"
for name in TABS.keys():
    active = "active" if st.session_state["active_tab"] == name else ""
    nav_html += f"<button class='{active}' onclick=\"window.location.search='?tab={name}'\">{name}</button>"
nav_html += "</div></div>"
st.markdown(nav_html, unsafe_allow_html=True)

# Parse tab selection from URL query
query = st.experimental_get_query_params()
if "tab" in query and query["tab"][0] in TABS:
    st.session_state["active_tab"] = query["tab"][0]
    st.experimental_set_query_params(tab=query["tab"][0])

# ==============================================================
# 📊 RENDER CURRENT TAB
# ==============================================================

st.markdown("<div class='fade-in'>", unsafe_allow_html=True)
TABS[st.session_state["active_tab"]].render()
st.markdown("</div>", unsafe_allow_html=True)

# ==============================================================
# 🔄 FLOATING SYNC BUTTON
# ==============================================================

st.markdown(
    """
    <div class="fab" onclick="window.location.reload()" title="Refresh Strava Data">
        <span style="font-size:20px;">⟳</span>
    </div>
    <style>
    .fab{
        position:fixed;bottom:24px;right:24px;
        background:var(--md-sys-color-primary,#0b57d0);
        color:white;width:48px;height:48px;
        border-radius:50%;display:flex;align-items:center;justify-content:center;
        box-shadow:0 4px 12px rgba(0,0,0,0.25);cursor:pointer;
        transition:background 0.25s;
    }
    .fab:hover{background:var(--md-sys-color-primary-container,#084bb3);}
    </style>
    """,
    unsafe_allow_html=True,
)

# ==============================================================
# 🧾 SIDEBAR FOOTER
# ==============================================================

strava_status()
st.sidebar.markdown("---")
st.sidebar.caption("© 2025 Cycling Coaching Dashboard · Material Design 3 Edition")
