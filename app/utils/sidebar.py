"""Custom sidebar navigation for Streamlit MPA."""

from __future__ import annotations

from pathlib import Path

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PAGES_DIR = PROJECT_ROOT / "app" / "pages"

PAGE_PATHS = {
    "dashboard": "pages/1_Dashboard.py",
    "forecasting": "pages/2_Forecasting.py",
    "anomaly": "pages/3_Anomaly_Detection.py",
    "what_if": "pages/4_What_If_Simulation.py",
    "jira_sync": "pages/6_Jira_Sync.py",
    "settings": "pages/5_Settings.py",
}


def _exists(page_path: str) -> bool:
    if page_path == "main.py":
        return True
    return (PROJECT_ROOT / "app" / page_path).exists()


def _link(page_path: str, label: str, icon: str) -> None:
    if _exists(page_path):
        st.page_link(page_path, label=label, icon=icon)
    else:
        st.caption(f"{label} unavailable")


def render_sidebar() -> None:
    """Render custom sidebar with consistent MPA mapping."""
    user = st.session_state.get(
        "user",
        {
            "username": "demo",
            "full_name": "Demo User",
            "role": "Admin",
        },
    )
    display_name = (
        user.get("full_name")
        or user.get("name")
        or user.get("username")
        or "Demo User"
    )
    role = user.get("role", "Admin")
    initial = display_name[0].upper()

    with st.sidebar:
        st.markdown(
            """
            <div style='padding:16px 12px 12px 12px; border-bottom:1px solid #1C3A54; margin-bottom: 16px;'>
            <span style='color:#FFFFFF; font-weight: 700; font-size:16px;'>Risk Framework</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            "<div class='section-title'>WORKSPACE</div>", unsafe_allow_html=True
        )
        _link(PAGE_PATHS["dashboard"], "Dashboard", "📊")

        st.markdown(
            "<div class='section-title'>MONITORING</div>", unsafe_allow_html=True
        )
        _link(PAGE_PATHS["forecasting"], "Forecasting Lab", "📈")
        _link(PAGE_PATHS["anomaly"], "Anomaly Triage", "🚨")
        _link(PAGE_PATHS["what_if"], "What-If Simulation", "🧪")

        st.markdown(
            "<div class='section-title'>INTEGRATIONS</div>", unsafe_allow_html=True
        )
        _link(PAGE_PATHS["jira_sync"], "Jira Sync", "🔄")

        st.markdown("<div class='sidebar-spacer'></div>", unsafe_allow_html=True)

        st.markdown("<div class='section-title'>SYSTEM</div>", unsafe_allow_html=True)
        _link(PAGE_PATHS["settings"], "Settings", "⚙️")

        st.markdown(
            f"""
            <div class="user-zone">
            <div class="user-card">
            <div class="user-avatar">{initial}</div>
            <div>
            <div class="user-meta-name">{display_name}</div>
            <div class="user-meta-role">{role}</div>
            </div>
            </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
