import streamlit as st

def inject_md3_stylesheet():
    """Load the MD3 CSS theme globally"""
    with open("style/md3.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def md_card(content: str, elev: int = 1):
    """Display content inside an MD3-style card"""
    st.markdown(f"""
    <div class='md-card md-elev-{elev}'>
        {content}
    </div>
    """, unsafe_allow_html=True)

def md_button(label: str, color: str = "primary"):
    """Render a stylized MD3 button"""
    button_html = f"""
    <button class='md-button md-{color}'>{label}</button>
    """
    st.markdown(button_html, unsafe_allow_html=True)

def md_header(text: str, level: str = "large"):
    """Display a headline or title with MD3 typography"""
    st.markdown(f"<div class='md-headline-{level}'>{text}</div>", unsafe_allow_html=True)
