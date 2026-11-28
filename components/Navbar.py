import streamlit as st
import base64
from pathlib import Path

def _logo_base64() -> str:
    try:
        logo_path = Path(__file__).resolve().parent.parent / "assets" / "Logo.png"
        return base64.b64encode(logo_path.read_bytes()).decode("utf-8")
    except Exception:
        return ""

def render_navbar():
    # Inject Material Icons and global Theme.css
    st.markdown('<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">', unsafe_allow_html=True)
    theme_file = Path(__file__).resolve().parent.parent / "styles" / "Theme.css"
    if theme_file.exists():
        st.markdown(f"<style>\n{theme_file.read_text(encoding='utf-8')}\n</style>", unsafe_allow_html=True)

    # Use Streamlit columns for navbar layout
    col_brand, spacer1, col_l1, col_l2, col_l3, col_l4, col_l5, col_l6, spacer2 = st.columns(
        [4, 1, 1, 1.4, 1.4, 1.5, 1.5, 1, 2]
    )

    with col_brand:
        st.markdown(f"""
        <div class="navbar-brand">
            <img src="data:image/png;base64,{_logo_base64()}" alt="PolicyPal logo" />
            <span>PolicyPal AI</span>
        </div>
        """, unsafe_allow_html=True)

    with col_l1:
        st.page_link("app.py",                     label="Home",          icon=None)
    with col_l2:
        st.page_link("pages/Dashboard.py",          label="Dashboard",     icon=None)
    with col_l3:
        st.page_link("pages/RiskAnalysis.py",       label="Risk Analysis", icon=None)
    with col_l4:
        st.page_link("pages/ClauseExplorer.py",     label="Clauses",       icon=None)
    with col_l5:
        st.page_link("pages/Obligations.py",        label="Obligations",   icon=None)
    with col_l6:
        st.page_link("pages/About.py",              label="About",         icon=None)
