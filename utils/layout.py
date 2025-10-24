import streamlit as st
from utils.md3_components import inject_md3_stylesheet

def init_layout(page_title: str = "Cycling Coaching Dashboard"):
    """Initialize MD3 layout with stylesheet and top bar"""
    st.set_page_config(page_title=page_title, layout="wide")
    inject_md3_stylesheet()
    render_topbar(page_title)

def render_topbar(title: str):
    """Top app bar styled with MD3 principles"""
    st.markdown(f"""
    <div class='md3-topbar md-elev-2'>
        <div class='md3-topbar-title'>{title}</div>
    </div>
    """, unsafe_allow_html=True)

def render_navbar(pages: list, current_page: str):
    """Horizontal MD3 navigation buttons"""
    st.markdown("<div class='navbar'>", unsafe_allow_html=True)
    cols = st.columns(len(pages))
    for i, page in enumerate(pages):
        active = "active" if page == current_page else ""
        if cols[i].button(page, key=f"nav_{page}"):
            st.session_state["page"] = page
        cols[i].markdown(
            f"<style>div[data-testid='stButton'] button#{page} {{ all: unset; }}</style>",
            unsafe_allow_html=True,
        )
        st.markdown(f"<style>button.nav-btn.{active}{{}}</style>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

def end_layout():
    """Optional closing markup if needed"""
    st.markdown("</div>", unsafe_allow_html=True)
