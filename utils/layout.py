import streamlit as st
from utils.md3_components import inject_md3_stylesheet

def init_layout(page_title: str = "Cycling Dashboard"):
    """Initialize MD3 layout with global style and page setup"""
    st.set_page_config(page_title=page_title, layout="wide")
    inject_md3_stylesheet()
    render_topbar(page_title)
    st.markdown("<div class='md3-content'>", unsafe_allow_html=True)

def end_layout():
    """Close the main content container"""
    st.markdown("</div>", unsafe_allow_html=True)

def render_topbar(title: str):
    """Material Design 3 top app bar"""
    st.markdown(f"""
    <div class='md3-topbar md-elev-2'>
        <div class='md3-topbar-title'>{title}</div>
        <div class='md3-topbar-actions'>
            <button class='md-button md-tonal'>Settings</button>
        </div>
    </div>
    """, unsafe_allow_html=True)

def section(title: str, content_fn):
    """Reusable section container with heading + content callback"""
    st.markdown(f"<div class='md-headline-large'>{title}</div>", unsafe_allow_html=True)
    st.markdown("<div class='md-card md-elev-1'>", unsafe_allow_html=True)
    content_fn()
    st.markdown("</div>", unsafe_allow_html=True)
