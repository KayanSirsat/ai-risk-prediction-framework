"""
Login/Signup View Component
AI-Driven Risk Prediction Framework

Dark themed authentication interface with indigo accents.
"""

import streamlit as st
from app.utils.styles import COLORS


def get_login_styles() -> str:
    """Return custom CSS for the login page."""
    return f"""
    <style>
        /* Hide Streamlit branding on login */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}
        
        /* Page background */
        .stApp {{
            background-color: {COLORS["bg_primary"]};
        }}
        
        /* Login container */
        .login-container {{
            max-width: 400px;
            margin: 0 auto;
            padding: 2rem;
            background: {COLORS["bg_card"]};
            border-radius: 16px;
            border: 1px solid {COLORS["border_primary"]};
            box-shadow: 0 4px 24px rgba(0, 0, 0, 0.3);
        }}
        
        .login-header {{
            text-align: center;
            margin-bottom: 2rem;
        }}
        
        .login-logo {{
            width: 56px;
            height: 56px;
            background: linear-gradient(135deg, {COLORS["brand_primary"]} 0%, {COLORS["brand_dark"]} 100%);
            border-radius: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 1rem;
        }}
        
        .login-title {{
            font-size: 1.5rem;
            font-weight: 700;
            color: {COLORS["text_primary"]};
            margin-bottom: 0.25rem;
            font-family: 'Inter', sans-serif;
            letter-spacing: -0.02em;
        }}
        
        .login-subtitle {{
            color: {COLORS["text_muted"]};
            font-size: 0.9rem;
            font-family: 'Inter', sans-serif;
        }}
        
        .login-divider {{
            display: flex;
            align-items: center;
            margin: 1.5rem 0;
            color: {COLORS["text_muted"]};
            font-size: 0.8rem;
        }}
        
        .login-divider::before,
        .login-divider::after {{
            content: '';
            flex: 1;
            border-bottom: 1px solid {COLORS["border_primary"]};
        }}
        
        .login-divider span {{
            padding: 0 1rem;
        }}
        
        .auth-toggle {{
            text-align: center;
            margin-top: 1.5rem;
            padding-top: 1.5rem;
            border-top: 1px solid {COLORS["border_primary"]};
        }}
        
        .auth-toggle-text {{
            color: {COLORS["text_muted"]};
            font-size: 0.875rem;
            font-family: 'Inter', sans-serif;
        }}
        
        .error-message {{
            background: {COLORS["error_bg"]};
            border: 1px solid rgba(239, 68, 68, 0.3);
            border-radius: 8px;
            padding: 0.75rem 1rem;
            color: {COLORS["error"]};
            font-size: 0.85rem;
            margin-bottom: 1rem;
            font-family: 'Inter', sans-serif;
        }}
        
        .success-message {{
            background: {COLORS["success_bg"]};
            border: 1px solid rgba(34, 197, 94, 0.3);
            border-radius: 8px;
            padding: 0.75rem 1rem;
            color: {COLORS["success"]};
            font-size: 0.85rem;
            margin-bottom: 1rem;
            font-family: 'Inter', sans-serif;
        }}
        
        /* Input styling */
        .stTextInput > div > div > input {{
            background: {COLORS["bg_input"]} !important;
            border: 1px solid {COLORS["border_primary"]} !important;
            border-radius: 8px !important;
            padding: 0.7rem 0.875rem !important;
            font-family: 'Inter', sans-serif !important;
            font-size: 0.9rem !important;
            color: {COLORS["text_primary"]} !important;
            transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
        }}
        
        .stTextInput > div > div > input:focus {{
            border-color: {COLORS["border_focus"]} !important;
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15) !important;
        }}
        
        .stTextInput > div > div > input::placeholder {{
            color: {COLORS["text_muted"]} !important;
        }}
        
        /* Button styling */
        .stButton > button {{
            width: 100%;
            border-radius: 8px !important;
            padding: 0.7rem 1.5rem !important;
            font-weight: 600 !important;
            font-family: 'Inter', sans-serif !important;
            font-size: 0.9rem !important;
            transition: all 0.15s ease !important;
            border: none !important;
        }}
        
        .stButton > button[kind="primary"] {{
            background: {COLORS["brand_primary"]} !important;
            color: white !important;
        }}
        
        .stButton > button[kind="primary"]:hover {{
            background: {COLORS["brand_dark"]} !important;
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4) !important;
        }}
        
        .stButton > button[kind="secondary"] {{
            background: transparent !important;
            color: {COLORS["text_secondary"]} !important;
            border: 1px solid {COLORS["border_primary"]} !important;
        }}
        
        .stButton > button[kind="secondary"]:hover {{
            background: {COLORS["bg_card"]} !important;
            border-color: {COLORS["brand_primary"]} !important;
            color: {COLORS["text_primary"]} !important;
        }}
    </style>
    """


def render_login_view():
    """Render the login/signup interface."""

    # Initialize session state
    if "auth_mode" not in st.session_state:
        st.session_state.auth_mode = "login"

    if "login_error" not in st.session_state:
        st.session_state.login_error = None

    if "signup_success" not in st.session_state:
        st.session_state.signup_success = False

    # Inject custom styles
    st.markdown(get_login_styles(), unsafe_allow_html=True)

    # Center the login form
    col1, col2, col3 = st.columns([1, 1.1, 1])

    with col2:
        # Vertical spacing
        st.markdown("<div style='height: 10vh'></div>", unsafe_allow_html=True)

        # Login container
        st.markdown('<div class="login-container">', unsafe_allow_html=True)

        # Header with logo
        st.markdown(
            f"""
            <div class="login-header">
                <div class="login-logo">
                    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        <path d="M2 17L12 22L22 17" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        <path d="M2 12L12 17L22 12" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </div>
                <div class="login-title">RiskAI</div>
                <div class="login-subtitle">AI-Driven Risk Prediction Framework</div>
            </div>
        """,
            unsafe_allow_html=True,
        )

        # Error message
        if st.session_state.login_error:
            st.markdown(
                f'<div class="error-message">{st.session_state.login_error}</div>',
                unsafe_allow_html=True,
            )

        # Success message
        if st.session_state.signup_success:
            st.markdown(
                '<div class="success-message">Account created. Please sign in.</div>',
                unsafe_allow_html=True,
            )
            st.session_state.signup_success = False

        # Render form based on mode
        if st.session_state.auth_mode == "login":
            _render_login_form()
        else:
            _render_signup_form()

        st.markdown("</div>", unsafe_allow_html=True)


def _render_login_form():
    """Render the login form."""

    username = st.text_input(
        "Username",
        placeholder="Enter your username",
        key="login_username",
        label_visibility="collapsed",
    )
    st.markdown("<div style='height: 0.4rem'></div>", unsafe_allow_html=True)

    password = st.text_input(
        "Password",
        type="password",
        placeholder="Enter your password",
        key="login_password",
        label_visibility="collapsed",
    )

    st.markdown("<div style='height: 1rem'></div>", unsafe_allow_html=True)

    if st.button("Sign In", type="primary", use_container_width=True):
        _handle_login(username, password)

    st.markdown(
        """
        <div class="auth-toggle">
            <span class="auth-toggle-text">Don't have an account?</span>
        </div>
    """,
        unsafe_allow_html=True,
    )

    if st.button("Create Account", type="secondary", use_container_width=True):
        st.session_state.auth_mode = "signup"
        st.session_state.login_error = None
        st.rerun()


def _render_signup_form():
    """Render the signup form."""

    full_name = st.text_input(
        "Full Name",
        placeholder="Enter your full name",
        key="signup_name",
        label_visibility="collapsed",
    )
    st.markdown("<div style='height: 0.4rem'></div>", unsafe_allow_html=True)

    email = st.text_input(
        "Email",
        placeholder="Enter your email",
        key="signup_email",
        label_visibility="collapsed",
    )
    st.markdown("<div style='height: 0.4rem'></div>", unsafe_allow_html=True)

    username = st.text_input(
        "Username",
        placeholder="Choose a username",
        key="signup_username",
        label_visibility="collapsed",
    )
    st.markdown("<div style='height: 0.4rem'></div>", unsafe_allow_html=True)

    password = st.text_input(
        "Password",
        type="password",
        placeholder="Create a password",
        key="signup_password",
        label_visibility="collapsed",
    )
    st.markdown("<div style='height: 0.4rem'></div>", unsafe_allow_html=True)

    confirm_password = st.text_input(
        "Confirm Password",
        type="password",
        placeholder="Confirm your password",
        key="signup_confirm_password",
        label_visibility="collapsed",
    )

    st.markdown("<div style='height: 1rem'></div>", unsafe_allow_html=True)

    if st.button("Create Account", type="primary", use_container_width=True):
        _handle_signup(full_name, email, username, password, confirm_password)

    st.markdown(
        """
        <div class="auth-toggle">
            <span class="auth-toggle-text">Already have an account?</span>
        </div>
    """,
        unsafe_allow_html=True,
    )

    if st.button("Sign In", type="secondary", use_container_width=True):
        st.session_state.auth_mode = "login"
        st.session_state.login_error = None
        st.rerun()


def _handle_login(username: str, password: str):
    """Handle login authentication."""

    st.session_state.login_error = None

    if not username or not password:
        st.session_state.login_error = "Please enter both username and password."
        st.rerun()
        return

    # Mock authentication
    if username == "admin" and password == "admin":
        st.session_state.authenticated = True
        st.session_state.user = {
            "username": username,
            "full_name": "Admin User",
            "email": "admin@riskai.io",
            "role": "Administrator",
        }
        st.session_state.login_error = None
        st.rerun()
    else:
        st.session_state.login_error = "Invalid credentials. Use admin / admin."
        st.rerun()


def _handle_signup(
    full_name: str, email: str, username: str, password: str, confirm_password: str
):
    """Handle user signup."""

    st.session_state.login_error = None

    if not all([full_name, email, username, password, confirm_password]):
        st.session_state.login_error = "Please fill in all fields."
        st.rerun()
        return

    if password != confirm_password:
        st.session_state.login_error = "Passwords do not match."
        st.rerun()
        return

    if len(password) < 4:
        st.session_state.login_error = "Password must be at least 4 characters."
        st.rerun()
        return

    # Mock signup success
    st.session_state.signup_success = True
    st.session_state.auth_mode = "login"
    st.rerun()
