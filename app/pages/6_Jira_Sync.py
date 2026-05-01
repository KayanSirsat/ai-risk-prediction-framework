"""Jira Sync page for native Streamlit multipage app."""

import streamlit as st

st.set_page_config(layout="wide", initial_sidebar_state="expanded")

from app.utils.styles import inject_global_css, render_topbar
from app.utils.sidebar import render_sidebar
from app.views.jira_sync import handle_oauth_callback, render_jira_sync_page

if not st.session_state.get("authenticated", False):
    st.switch_page("main.py")

inject_global_css()
render_sidebar()
render_topbar("Jira Sync")
handle_oauth_callback()
render_jira_sync_page()
