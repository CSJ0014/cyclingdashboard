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

/* === MD3 Layout === */

.md3-topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: var(--md-sys-color-surface);
  color: var(--md-sys-color-on-surface);
  height: 64px;
  padding: 0 24px;
  position: sticky;
  top: 0;
  z-index: 1000;
  box-shadow: var(--md-elev-2);
  border-bottom: 1px solid rgba(0,0,0,0.05);
}

.md3-topbar-title {
  font-size: 20px;
  font-weight: 500;
  color: var(--md-sys-color-on-surface);
}

.md3-topbar-actions button {
  margin-left: 8px;
}

.md3-content {
  padding: 24px 48px;
  max-width: 1600px;
  margin: 0 auto;
}

@media (max-width: 900px) {
  .md3-content { padding: 16px; }
  .md3-topbar { flex-direction: column; height: auto; padding: 12px; }
}
