"""Executive Dashboard page for native Streamlit multipage app."""

import streamlit as st

st.set_page_config(layout="wide", initial_sidebar_state="expanded")

from app.utils.routes import MAIN_PAGE, switch_page_safe
from app.utils.styles import inject_global_css, render_topbar
from app.utils.sidebar import render_sidebar
from app.views.dashboard import render_dashboard


def main() -> None:
    if not st.session_state.get("authenticated", False):
        if not switch_page_safe(MAIN_PAGE):
            st.warning("Could not route to Sign In page.")
            st.stop()

    inject_global_css()
    render_sidebar()
    render_topbar("Dashboard")
    render_dashboard(show_topbar=False)


if __name__ == "__main__":
    main()
