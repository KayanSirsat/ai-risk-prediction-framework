"""Jira Sync view with OAuth flow and live issue ingestion."""

from __future__ import annotations

import os
import time
from typing import Any, Dict, List

import pandas as pd
import streamlit as st

from app.utils.styles import render_page_header, render_section_header
from src.integrations.jira_client import (
    InvalidJQLError,
    JiraAPIClient,
    JiraConnectionError,
    RateLimitError,
)
from src.integrations.oauth_handler import JiraOAuthError, JiraOAuthHandler


DATASET_PATH = "data/ml_ready_data.csv"
DEFAULT_MAX_RESULTS = 250


def _env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def _config_snapshot() -> Dict[str, str]:
    return {
        "jira_url": _env("JIRA_URL"),
        "project_key": _env("JIRA_PROJECT_KEY", "RISK"),
        "client_id": _env("JIRA_OAUTH_CLIENT_ID"),
        "client_secret": _env("JIRA_OAUTH_CLIENT_SECRET"),
        "redirect_uri": _env("JIRA_OAUTH_REDIRECT_URI", "http://localhost:8501"),
    }


def _check_config(config: Dict[str, str]) -> List[str]:
    missing = []
    if not config["jira_url"]:
        missing.append("JIRA_URL")
    if not config["project_key"]:
        missing.append("JIRA_PROJECT_KEY")
    if not config["client_id"]:
        missing.append("JIRA_OAUTH_CLIENT_ID")
    if not config["client_secret"]:
        missing.append("JIRA_OAUTH_CLIENT_SECRET")
    if not config["redirect_uri"]:
        missing.append("JIRA_OAUTH_REDIRECT_URI")
    return missing


def _init_jira_session_state() -> None:
    defaults = {
        "jira_authenticated": False,
        "jira_access_token": "",
        "jira_refresh_token": "",
        "jira_expires_at": 0.0,
        "jira_cloud_id": "",
        "jira_sync_results": [],
        "jira_sync_error": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _handler_from_config(config: Dict[str, str]) -> JiraOAuthHandler:
    return JiraOAuthHandler(
        client_id=config["client_id"],
        client_secret=config["client_secret"],
        redirect_uri=config["redirect_uri"],
    )


def handle_oauth_callback() -> None:
    """Handle Jira OAuth callback and persist token data in session state."""
    _init_jira_session_state()
    code = st.query_params.get("code")
    if not code:
        return

    config = _config_snapshot()
    missing = _check_config(config)
    if missing:
        st.error(f"Jira OAuth callback failed; missing config: {', '.join(missing)}")
        return

    state = st.query_params.get("state")
    expected_state = st.session_state.get("jira_oauth_state")
    if state and expected_state and state != expected_state:
        st.error("Jira OAuth state mismatch detected. Please retry authorization.")
        return

    try:
        handler = _handler_from_config(config)
        token_data = handler.exchange_auth_code(str(code))
        cloud_id = handler.fetch_cloud_id(token_data.get("access_token", ""))
    except JiraOAuthError as exc:
        st.session_state["jira_sync_error"] = str(exc)
        st.error(f"OAuth exchange failed: {exc}")
        return

    st.session_state["jira_access_token"] = token_data.get("access_token", "")
    st.session_state["jira_refresh_token"] = token_data.get("refresh_token", "")
    st.session_state["jira_expires_at"] = float(token_data.get("expires_at", 0.0))
    st.session_state["jira_cloud_id"] = cloud_id
    st.session_state["jira_authenticated"] = bool(token_data.get("access_token"))
    st.session_state["jira_sync_error"] = ""
    st.query_params.clear()
    st.success("Jira OAuth connected successfully.")
    st.rerun()


def _build_jira_client(config: Dict[str, str]) -> JiraAPIClient:
    oauth_handler = _handler_from_config(config)
    return JiraAPIClient(
        base_url=config["jira_url"],
        project_key=config["project_key"],
        access_token=st.session_state.get("jira_access_token", ""),
        cloud_id=st.session_state.get("jira_cloud_id", ""),
        refresh_token=st.session_state.get("jira_refresh_token", ""),
        token_expires_at=float(st.session_state.get("jira_expires_at", 0.0) or 0.0),
        oauth_handler=oauth_handler,
    )


def _jira_connected() -> bool:
    return bool(st.session_state.get("jira_authenticated") and st.session_state.get("jira_access_token"))


def _render_oauth_status(config: Dict[str, str]) -> None:
    connected = _jira_connected()
    c1, c2, c3 = st.columns(3)
    c1.metric("OAuth Status", "Connected" if connected else "Disconnected")
    c2.metric("Project", config["project_key"] or "N/A")
    cloud_id = st.session_state.get("jira_cloud_id", "")
    c3.metric("Cloud ID", cloud_id[:10] + "..." if cloud_id else "N/A")


def _render_oauth_controls(config: Dict[str, str]) -> None:
    if not _jira_connected():
        state = JiraOAuthHandler.generate_state()
        st.session_state["jira_oauth_state"] = state
        authorize_url = _handler_from_config(config).get_authorization_url(state=state)
        st.link_button("Authorize with Jira", authorize_url, use_container_width=False)
        st.caption(
            "After authorization, Jira redirects back to localhost and this page completes token exchange automatically."
        )
        return

    expires_at = float(st.session_state.get("jira_expires_at", 0.0) or 0.0)
    expires_in = max(0, int(expires_at - time.time())) if expires_at else 0
    mins = expires_in // 60
    st.success(f"Jira connected. Access token valid for ~{mins} minutes.")
    if st.button("Disconnect Jira", type="secondary"):
        for key in [
            "jira_authenticated",
            "jira_access_token",
            "jira_refresh_token",
            "jira_expires_at",
            "jira_cloud_id",
            "jira_oauth_state",
        ]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()


def _safe_description(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        text_fragments: List[str] = []
        for block in value.get("content", []):
            for child in block.get("content", []):
                text = child.get("text")
                if text:
                    text_fragments.append(text)
        return " ".join(text_fragments)
    return ""


def _normalize_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    normalized: List[Dict[str, Any]] = []
    for row in rows:
        current = dict(row)
        current["Summary"] = str(current.get("Summary", "") or "")
        current["Description"] = _safe_description(current.get("Description", ""))
        normalized.append(current)
    return normalized


def _merge_into_dataset(rows: List[Dict[str, Any]], dataset_path: str = DATASET_PATH) -> int:
    if not rows:
        return 0

    incoming = pd.DataFrame(_normalize_rows(rows))
    incoming["source_system"] = "jira"
    incoming["synced_at"] = pd.Timestamp.utcnow().isoformat()

    if os.path.exists(dataset_path):
        existing = pd.read_csv(dataset_path)
    else:
        existing = pd.DataFrame(columns=incoming.columns)

    for column in existing.columns:
        if column not in incoming.columns:
            incoming[column] = None
    for column in incoming.columns:
        if column not in existing.columns:
            existing[column] = None

    incoming = incoming[existing.columns]

    combined = pd.concat([existing, incoming], ignore_index=True)
    if "Issue_key" in combined.columns:
        combined = combined.drop_duplicates(subset=["Issue_key"], keep="last")

    combined.to_csv(dataset_path, index=False)
    return int(len(incoming))


def _sync_now(config: Dict[str, str], jql_query: str, max_results: int) -> None:
    try:
        client = _build_jira_client(config)
        rows = client.sync_issues(jql_query=jql_query, max_results=max_results)
    except InvalidJQLError as exc:
        st.session_state["jira_sync_error"] = str(exc)
        st.error("Invalid JQL query. Please adjust your filter and retry.")
        return
    except RateLimitError:
        st.session_state["jira_sync_error"] = "Jira API rate limit exceeded"
        st.warning("Jira rate limited the request. Please retry in a moment.")
        return
    except (JiraConnectionError, JiraOAuthError) as exc:
        st.session_state["jira_sync_error"] = str(exc)
        st.error(f"Jira sync failed: {exc}")
        return

    inserted = _merge_into_dataset(rows)
    st.session_state["jira_sync_results"] = rows
    st.session_state["jira_last_sync_at"] = pd.Timestamp.utcnow().isoformat()
    st.session_state["jira_sync_error"] = ""
    st.success(f"Synced {len(rows)} issue(s) from Jira. Added {inserted} row(s) to dataset.")


def _render_sync_controls(config: Dict[str, str]) -> None:
    render_section_header("Sync Controls")
    default_query = (
        f"project = {config['project_key']} "
        "AND statusCategory != Done ORDER BY updated DESC"
    )
    jql_query = st.text_area("JQL Query", value=default_query, height=88)

    c1, c2, c3 = st.columns([1.1, 1, 2])
    with c1:
        max_results = int(
            st.number_input("Max Results", min_value=1, max_value=1000, value=DEFAULT_MAX_RESULTS, step=1)
        )
    with c2:
        if st.button("Sync Now", type="primary", use_container_width=True):
            with st.spinner("Syncing issues from Jira..."):
                _sync_now(config, jql_query, max_results)
    with c3:
        last_sync = st.session_state.get("jira_last_sync_at")
        st.caption(f"Last sync: {last_sync or 'Never'}")


def _render_sync_results() -> None:
    render_section_header("Latest Sync Results")
    rows = st.session_state.get("jira_sync_results") or []
    if not rows:
        st.info("No Jira issues synced yet. Authorize and run Sync Now.")
        return

    df = pd.DataFrame(rows)
    preferred_cols = [
        "Issue_key",
        "Priority",
        "Issue_Type",
        "Story_Points",
        "Estimated_Days",
        "Budget_Allocated",
        "Summary",
    ]
    present_cols = [col for col in preferred_cols if col in df.columns]
    if present_cols:
        st.dataframe(df[present_cols], use_container_width=True)
    else:
        st.dataframe(df, use_container_width=True)

    csv_bytes = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download Last Sync (CSV)",
        data=csv_bytes,
        file_name="jira_sync_results.csv",
        mime="text/csv",
    )


def render_jira_sync_page() -> None:
    """Render Jira Sync page."""
    _init_jira_session_state()
    config = _config_snapshot()
    missing = _check_config(config)

    render_page_header(
        title="Jira Sync",
        subtitle="Authorize Jira OAuth and sync live tickets into the risk pipeline",
    )

    if missing:
        st.error(f"Missing Jira configuration in .env: {', '.join(missing)}")
        st.info("Update .env and reload the app. Refer to env.example.md for required keys.")
        return

    _render_oauth_status(config)
    _render_oauth_controls(config)

    if _jira_connected():
        _render_sync_controls(config)

    sync_error = st.session_state.get("jira_sync_error")
    if sync_error:
        st.warning(f"Latest sync warning: {sync_error}")

    _render_sync_results()
