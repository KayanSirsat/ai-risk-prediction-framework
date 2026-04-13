"""Shared Jira-style sidebar for Streamlit native multipage app."""

import streamlit as st
from app.utils.routes import (
    ANOMALY_PAGE,
    DASHBOARD_PAGE,
    FORECASTING_PAGE,
    MAIN_PAGE,
    page_link_safe,
)


def render_sidebar() -> None:
    """Render custom sidebar navigation using page links."""
    user = st.session_state.get(
        "user",
        {
            "username": "kayan",
            "full_name": "Kayan Sirsat",
            "email": "kayan@example.com",
            "role": "Admin",
        },
    )
    display_name = user.get("full_name") or user.get("username") or "User"
    initial = display_name[0].upper()

    with st.sidebar:
        st.markdown(
            """
            <div class='sidebar-logo'>
                <span class='sidebar-logo-dot'></span>
                <span class='sidebar-logo-text'>Risk Framework</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            "<div class='sidebar-section'>WORKSPACE</div>", unsafe_allow_html=True
        )
        page_link_safe(DASHBOARD_PAGE, label="Dashboard", icon="📊")

        st.markdown(
            "<div class='sidebar-section'>MONITORING</div>", unsafe_allow_html=True
        )
        page_link_safe(FORECASTING_PAGE, label="Forecasting Lab", icon="📈")
        page_link_safe(ANOMALY_PAGE, label="Anomaly Triage", icon="🚨")

        st.markdown("<div class='sidebar-section'>ACCESS</div>", unsafe_allow_html=True)
        if not st.session_state.get("authenticated", False):
            page_link_safe(MAIN_PAGE, label="Sign In", icon="🔐")

        st.markdown(
            f"""
            <div class='sidebar-user'>
                <div class='sidebar-avatar'>{initial}</div>
                <div>
                    <div class='sidebar-user-name'>{display_name}</div>
                    <div class='sidebar-user-role'>{user.get("role", "PM")}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
