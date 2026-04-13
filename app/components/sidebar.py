"""
Sidebar Navigation Component
AI-Driven Risk Prediction Framework

Professional dark sidebar with indigo accents.
"""

import streamlit as st
from app.utils.styles import COLORS


def get_sidebar_styles() -> str:
    """Return custom CSS for the sidebar."""
    return f"""
    <style>
        /* Sidebar Base */
        [data-testid="stSidebar"] {{
            background: {COLORS["bg_sidebar"]};
            border-right: 1px solid {COLORS["border_sidebar"]};
        }}
        
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {{
            color: {COLORS["text_secondary"]};
        }}
        
        /* Brand Section */
        .sidebar-brand {{
            padding: 1.25rem 1.25rem;
            display: flex;
            align-items: center;
            gap: 0.75rem;
            border-bottom: 1px solid {COLORS["border_sidebar"]};
            margin-bottom: 0.5rem;
        }}
        
        .sidebar-brand-icon {{
            width: 36px;
            height: 36px;
            background: linear-gradient(135deg, {COLORS["brand_primary"]} 0%, #4f46e5 100%);
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
        }}
        
        .sidebar-brand-text {{
            font-size: 1.25rem;
            font-weight: 700;
            color: {COLORS["text_primary"]};
            font-family: 'Inter', sans-serif;
            letter-spacing: -0.02em;
        }}
        
        .sidebar-version {{
            background: rgba(99, 102, 241, 0.2);
            color: {COLORS["brand_light"]};
            font-size: 0.65rem;
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            font-weight: 600;
            font-family: 'Inter', sans-serif;
            margin-left: auto;
        }}
        
        /* Profile Section */
        .sidebar-profile {{
            padding: 1.25rem;
            border-bottom: 1px solid {COLORS["border_sidebar"]};
            margin-bottom: 0.5rem;
        }}
        
        .sidebar-avatar {{
            width: 44px;
            height: 44px;
            border-radius: 10px;
            background: linear-gradient(135deg, {COLORS["brand_primary"]} 0%, #8b5cf6 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 700;
            font-size: 1.1rem;
            font-family: 'Inter', sans-serif;
            margin-bottom: 0.75rem;
        }}
        
        .sidebar-username {{
            color: {COLORS["text_primary"]};
            font-weight: 600;
            font-size: 0.95rem;
            font-family: 'Inter', sans-serif;
            margin-bottom: 0.2rem;
        }}
        
        .sidebar-role {{
            color: {COLORS["text_muted"]};
            font-size: 0.8rem;
            font-family: 'Inter', sans-serif;
        }}
        
        /* Navigation Label */
        .sidebar-nav-label {{
            color: {COLORS["text_disabled"]};
            font-size: 0.7rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            padding: 0.75rem 1.25rem 0.5rem;
            font-family: 'Inter', sans-serif;
        }}
        
        /* Radio Navigation Styling */
        [data-testid="stSidebar"] .stRadio > div {{
            display: flex;
            flex-direction: column;
            gap: 0.25rem;
            padding: 0 0.75rem;
        }}
        
        [data-testid="stSidebar"] .stRadio > div > label {{
            background: transparent;
            border-radius: 8px;
            padding: 0.7rem 0.75rem;
            margin: 0;
            cursor: pointer;
            transition: all 0.15s ease;
            border: 1px solid transparent;
        }}
        
        [data-testid="stSidebar"] .stRadio > div > label:hover {{
            background: {COLORS["bg_sidebar_hover"]};
        }}
        
        [data-testid="stSidebar"] .stRadio > div > label[data-checked="true"] {{
            background: {COLORS["bg_sidebar_active"]};
            border-color: rgba(99, 102, 241, 0.3);
        }}
        
        [data-testid="stSidebar"] .stRadio > div > label span {{
            color: {COLORS["text_secondary"]} !important;
            font-family: 'Inter', sans-serif !important;
            font-weight: 500 !important;
            font-size: 0.9rem !important;
        }}
        
        [data-testid="stSidebar"] .stRadio > div > label[data-checked="true"] span {{
            color: {COLORS["text_primary"]} !important;
        }}
        
        /* Hide radio circles */
        [data-testid="stSidebar"] .stRadio > div > label > div:first-child {{
            display: none;
        }}
        
        /* Logout Button */
        [data-testid="stSidebar"] .stButton > button {{
            width: 100%;
            background: transparent !important;
            border: 1px solid rgba(239, 68, 68, 0.25) !important;
            color: {COLORS["error"]} !important;
            border-radius: 8px !important;
            padding: 0.6rem 1rem !important;
            font-family: 'Inter', sans-serif !important;
            font-weight: 500 !important;
            font-size: 0.875rem !important;
            transition: all 0.15s ease !important;
        }}
        
        [data-testid="stSidebar"] .stButton > button:hover {{
            background: {COLORS["error_hover"]} !important;
            border-color: rgba(239, 68, 68, 0.4) !important;
        }}
        
        /* Footer */
        .sidebar-footer {{
            padding: 1rem 1.25rem;
            text-align: center;
            margin-top: auto;
        }}
        
        .sidebar-footer-text {{
            color: {COLORS["text_disabled"]};
            font-size: 0.7rem;
            font-family: 'Inter', sans-serif;
        }}
    </style>
    """


def render_sidebar() -> str:
    """
    Render the sidebar navigation.

    Returns:
        str: The selected navigation page.
    """

    # Inject custom styles
    st.markdown(get_sidebar_styles(), unsafe_allow_html=True)

    with st.sidebar:
        # Brand header
        st.markdown(
            """
            <div class="sidebar-brand">
                <div class="sidebar-brand-icon">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        <path d="M2 17L12 22L22 17" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        <path d="M2 12L12 17L22 12" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </div>
                <span class="sidebar-brand-text">RiskAI</span>
                <span class="sidebar-version">v2.0</span>
            </div>
        """,
            unsafe_allow_html=True,
        )

        # User profile section
        user = st.session_state.get("user", {})
        user_initials = _get_initials(user.get("full_name", "User"))

        st.markdown(
            f"""
            <div class="sidebar-profile">
                <div class="sidebar-avatar">{user_initials}</div>
                <div class="sidebar-username">{user.get("full_name", "User")}</div>
                <div class="sidebar-role">{user.get("role", "Project Manager")}</div>
            </div>
        """,
            unsafe_allow_html=True,
        )

        # Navigation label
        st.markdown(
            '<div class="sidebar-nav-label">Navigation</div>', unsafe_allow_html=True
        )

        # Navigation options
        nav_options = ["Overview", "Ticket Auditor", "Settings"]

        # Initialize selected page
        if "selected_page" not in st.session_state:
            st.session_state.selected_page = "Overview"

        # Radio navigation
        selected = st.radio(
            label="Navigation",
            options=nav_options,
            index=nav_options.index(st.session_state.selected_page),
            label_visibility="collapsed",
            key="nav_radio",
        )

        # Update session state
        st.session_state.selected_page = selected

        # Spacer
        st.markdown("<div style='height: 25vh'></div>", unsafe_allow_html=True)

        # Account section
        st.markdown(
            '<div class="sidebar-nav-label">Account</div>', unsafe_allow_html=True
        )

        if st.button("Sign Out", key="logout_btn", use_container_width=True):
            _handle_logout()

        # Footer
        st.markdown(
            """
            <div class="sidebar-footer">
                <span class="sidebar-footer-text">AI Risk Prediction Framework</span>
            </div>
        """,
            unsafe_allow_html=True,
        )

    return selected


def _get_initials(name: str) -> str:
    """Extract initials from a full name."""
    if not name:
        return "U"

    parts = name.strip().split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    elif len(parts) == 1:
        return parts[0][0].upper()
    return "U"


def _handle_logout():
    """Handle user logout by clearing session state."""

    keys_to_clear = [
        "authenticated",
        "user",
        "selected_page",
        "auth_mode",
        "login_error",
        "signup_success",
    ]

    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

    st.session_state.authenticated = False
    st.rerun()
