import streamlit as st
import json, os, re, shutil, importlib.util

SETTINGS_FILE = "ride_data/settings.json"
THEME_FILE = "utils/css_theme.py"
DEFAULT_THEME_FILE = "utils/css_theme_default.py"  # for reset fallback

def inject_live_theme():
    """Re-inject CSS immediately after saving a color change (live preview)."""
    theme_path = os.path.join("utils", "css_theme.py")
    if not os.path.exists(theme_path):
        return
    spec = importlib.util.spec_from_file_location("css_theme", theme_path)
    css_theme = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(css_theme)
    css_theme.inject_material_theme()

def read_theme_file():
    if not os.path.exists(THEME_FILE):
        return ""
    with open(THEME_FILE, "r") as f:
        return f.read()

def update_color(variable, new_value):
    """Replace CSS variable's value in the theme and auto-inject live preview."""
    css = read_theme_file()
    pattern = rf"({variable}:\s*)(#[0-9a-fA-F]{{3,8}})"
    updated_css, count = re.subn(pattern, rf"\\1{new_value}", css)
    if count > 0:
        with open(THEME_FILE, "w") as f:
            f.write(updated_css)
        inject_live_theme()  # 👈 instantly refresh styles
        return True
    return False

def reset_theme_to_default():
    if os.path.exists(DEFAULT_THEME_FILE):
        shutil.copy(DEFAULT_THEME_FILE, THEME_FILE)
        inject_live_theme()  # 👈 also live-apply default theme
        return True
    return False

def render():
    st.title("⚙️ Settings")

    # ==============================================================
    # TRAINING SETTINGS
    # ==============================================================
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🔧 Training Zones & Preferences")

    ftp = st.number_input(
        "Functional Threshold Power (FTP)",
        min_value=50, max_value=500,
        value=st.session_state.get("FTP_DEFAULT", 222)
    )
    hr_max = st.number_input(
        "Max Heart Rate (bpm)",
        min_value=120, max_value=220,
        value=st.session_state.get("HR_MAX", 200)
    )

    if st.button("💾 Save Training Settings"):
        os.makedirs("ride_data", exist_ok=True)
        with open(SETTINGS_FILE, "w") as f:
            json.dump({"FTP_DEFAULT": ftp, "HR_MAX": hr_max}, f, indent=2)
        st.session_state["FTP_DEFAULT"] = ftp
        st.session_state["HR_MAX"] = hr_max
        st.success("✅ Training settings saved successfully.")
    st.markdown('</div>', unsafe_allow_html=True)

    # ==============================================================
    # THEME CUSTOMIZER (AUTO PREVIEW)
    # ==============================================================
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🎨 Theme Customizer")

    st.markdown("Adjust your dashboard’s colors — they’ll update **instantly** on save.")

    # --- Button Colors ---
    st.markdown("#### 🔘 Buttons")
    col1, col2 = st.columns(2)
    with col1:
        btn_color = st.color_picker("Button Base Color", "#1a73e8")
        if st.button("💾 Save Button Color"):
            if update_color("--button-bg", btn_color):
                st.success(f"Updated → {btn_color}")
    with col2:
        hover_color = st.color_picker("Button Hover Color", "#155ab6")
        if st.button("💾 Save Hover Color"):
            if update_color("--button-bg-hover", hover_color):
                st.success(f"Updated → {hover_color}")

    st.divider()

    # --- Card + Background Colors ---
    st.markdown("#### 🧱 Cards & Background")
    col3, col4 = st.columns(2)
    with col3:
        card_color = st.color_picker("Card Background", "#ffffff")
        if st.button("💾 Save Card Background"):
            update_color("--card-bg", card_color)
            st.success(f"Updated card → {card_color}")
    with col4:
        bg_color = st.color_picker("App Background", "#fafafa")
        if st.button("💾 Save App Background"):
            update_color("--background", bg_color)
            st.success(f"Updated background → {bg_color}")

    st.divider()

    # --- Accent Colors ---
    st.markdown("#### 🌈 Accent Colors")
    col5, col6, col7 = st.columns(3)
    with col5:
        success_color = st.color_picker("Success (Green)", "#34a853")
        if st.button("💾 Save Success Color"):
            update_color("--success", success_color)
            st.success(f"Updated success → {success_color}")
    with col6:
        warning_color = st.color_picker("Warning (Yellow)", "#fbbc05")
        if st.button("💾 Save Warning Color"):
            update_color("--warning", warning_color)
            st.success(f"Updated warning → {warning_color}")
    with col7:
        error_color = st.color_picker("Error (Red)", "#ea4335")
        if st.button("💾 Save Error Color"):
            update_color("--error", error_color)
            st.success(f"Updated error → {error_color}")

    st.markdown('</div>', unsafe_allow_html=True)

    # ==============================================================
    # RESET SECTION
    # ==============================================================
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🧹 Reset Theme")

    st.markdown("Restore original Material Design colors immediately.")
    if st.button("♻️ Reset to Default Theme"):
        if reset_theme_to_default():
            st.success("✅ Theme restored and live-applied.")
        else:
            st.error("⚠️ Default theme file not found.")
    st.markdown('</div>', unsafe_allow_html=True)
