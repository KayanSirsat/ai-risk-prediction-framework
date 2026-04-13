"""Landing page for native Streamlit multipage app."""

import streamlit as st

from app.utils.env import ensure_project_root

ensure_project_root()

from app.utils.routes import DASHBOARD_PAGE, switch_page_safe
from app.views.login import render_login_view

st.set_page_config(initial_sidebar_state="collapsed", layout="centered")


def _inject_login_css(hide_sidebar: bool = True) -> None:
    sidebar_css = (
        '[data-testid="stSidebar"] { display: none !important; }\n'
        '[data-testid="stSidebarNav"] { display: none !important; }'
        if hide_sidebar
        else ""
    )
    st.markdown(
        """
        <style>
        """
        + sidebar_css
        + """
            .stApp {
                background: radial-gradient(circle at top left, #1e293b 0%, #0f172a 45%, #0b1220 100%);
            }
            .login-shell {
                margin-top: 8vh;
                border: 1px solid #334155;
                border-radius: 12px;
                padding: 24px;
                background: #1e293b;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        _inject_login_css(hide_sidebar=False)
        switch_page_safe(DASHBOARD_PAGE)
        st.stop()

    _inject_login_css(hide_sidebar=True)
    render_login_view()


if __name__ == "__main__":
    main()
