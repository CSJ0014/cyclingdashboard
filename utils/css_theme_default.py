import streamlit as st

def inject_material_theme():
    """Apply global Material 3 / Google-style CSS theme, with editable color config."""
    st.markdown("""
    <style>

    /* =========================================================
       🎨 COLOR CONFIGURATION — EASY TO EDIT
       ========================================================= */

    /* Primary Colors */
    :root {
        /* Buttons & Links */
        --button-bg: #1a73e8;        /* Primary blue */
        --button-bg-hover: #155ab6;  /* Darker hover blue */
        --button-text: #ffffff;      /* Button text color */

        /* Cards */
        --card-bg: #ffffff;          /* Card surface color */
        --card-shadow: 0 2px 6px rgba(0,0,0,0.08);
        --card-radius: 12px;

        /* Page Background */
        --background: #fafafa;

        /* Sidebar */
        --sidebar-bg: #f1f3f4;
        --sidebar-outline: #e0e0e0;

        /* Text Colors */
        --text-primary: #202124;
        --text-secondary: #5f6368;

        /* Accent / Status Colors */
        --success: #34a853;
        --error: #ea4335;
        --warning: #fbbc05;
    }

    /* =========================================================
       ✨ GLOBAL LAYOUT & TYPOGRAPHY
       ========================================================= */

    .stApp {
        background: var(--background);
        font-family: "Inter", "Roboto", sans-serif;
    }

    h1, h2, h3 {
        color: var(--text-primary);
        font-weight: 600;
        letter-spacing: -0.01em;
    }

    p, span, div {
        color: var(--text-secondary);
    }

    /* =========================================================
       🧱 CARD DESIGN
       ========================================================= */

    .card {
        background: var(--card-bg);
        border-radius: var(--card-radius);
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: var(--card-shadow);
        transition: all 0.25s ease;
    }

    .card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.12);
    }

    /* =========================================================
       🔘 BUTTON STYLING
       ========================================================= */

    div.stButton > button {
        background: var(--button-bg);
        color: var(--button-text);
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.3rem;
        font-weight: 500;
        box-shadow: var(--card-shadow);
        transition: all 0.2s ease;
    }

    div.stButton > button:hover {
        background: var(--button-bg-hover);
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }

    /* =========================================================
       🧭 SIDEBAR
       ========================================================= */

    section[data-testid="stSidebar"] {
        background: var(--sidebar-bg);
        border-right: 1px solid var(--sidebar-outline);
    }

    /* =========================================================
       📊 METRICS
       ========================================================= */

    [data-testid="stMetricValue"] {
        color: var(--button-bg);
        font-weight: 600;
    }

    /* =========================================================
       🔘 FLOATING ACTION BUTTON
       ========================================================= */

    .fab {
        position: fixed;
        bottom: 1.5rem;
        right: 1.5rem;
        width: 56px;
        height: 56px;
        border-radius: 50%;
        background: var(--button-bg);
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--button-text);
        font-size: 28px;
        cursor: pointer;
        z-index: 9999;
        transition: all 0.25s ease;
    }

    .fab:hover {
        background: var(--button-bg-hover);
        transform: scale(1.05);
    }

    /* =========================================================
       📂 EXPANDERS
       ========================================================= */

    [data-testid="stExpander"] {
        border-radius: var(--card-radius) !important;
        box-shadow: var(--card-shadow);
        background: var(--card-bg);
    }

    </style>
    """, unsafe_allow_html=True)

