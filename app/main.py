"""
Main Application Entry Point
AI-Driven Risk Prediction Framework

Handles authentication routing and page navigation with unified dark theme.
"""

import streamlit as st
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Page configuration - must be first Streamlit command
st.set_page_config(
    page_title="RiskAI - AI-Driven Risk Prediction",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Import components after page config
from app.utils.styles import apply_custom_styles, render_header
from app.views.login import render_login_view
from app.views.dashboard import render_dashboard
from app.views.auditor import render_auditor
from app.views.settings import render_settings
from app.components.sidebar import render_sidebar


def main():
    """Main application entry point."""

    # Apply global custom styles
    apply_custom_styles()

    # Initialize authentication state
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    # Routing logic
    if not st.session_state.authenticated:
        # Show login view
        render_login_view()
    else:
        # Show authenticated application
        selected_page = render_sidebar()

        # Render global header
        render_header()

        # Route to selected page
        if selected_page == "Overview":
            render_dashboard()
        elif selected_page == "Ticket Auditor":
            render_auditor()
        elif selected_page == "Settings":
            render_settings()


if __name__ == "__main__":
    main()
