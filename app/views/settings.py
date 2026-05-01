"""
Settings View
AI-Driven Risk Prediction Framework

User preferences, integrations, and model configuration.
"""

import json
from pathlib import Path

import streamlit as st

from app.utils.styles import render_page_header, COLORS

_SETTINGS_FILE = Path(__file__).resolve().parents[2] / "logs" / "user_settings.json"

# Keys that are persisted across sessions
_PERSISTENT_KEYS = [
    "settings_name",
    "settings_email",
    "settings_role",
    "notif_email_high_risk",
    "notif_anomaly",
    "notif_weekly_digest",
    "notif_slack",
    "jira_url",
    "jira_project_key",
    "model_anomaly_sensitivity",
    "model_forecast_horizon",
    "model_risk_threshold",
    "model_genai_provider",
]


def _load_saved_settings() -> None:
    """Load previously saved settings into session_state (only if not already set)."""
    if not _SETTINGS_FILE.exists():
        return
    try:
        saved = json.loads(_SETTINGS_FILE.read_text(encoding="utf-8"))
        for key, value in saved.items():
            if key not in st.session_state:
                st.session_state[key] = value
    except (json.JSONDecodeError, OSError):
        pass  # Silently ignore corrupt settings file


def _save_current_settings() -> None:
    """Persist current widget values to disk."""
    _SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    snapshot = {k: st.session_state.get(k) for k in _PERSISTENT_KEYS if k in st.session_state}
    _SETTINGS_FILE.write_text(json.dumps(snapshot, indent=2, default=str), encoding="utf-8")


def render_settings():
    """Render the settings page with card-based layout."""

    # Load persisted values into session_state before widgets render
    _load_saved_settings()

    # Page header
    render_page_header(
        title="Settings",
        subtitle="Configure your dashboard preferences and integrations",
    )

    # Two-column layout
    col1, col2 = st.columns(2)

    with col1:
        # Profile Settings Card
        _render_profile_settings()

        # Notification Settings Card
        _render_notification_settings()

    with col2:
        # Jira Integration Card
        _render_jira_settings()

        # Model Configuration Card
        _render_model_settings()

    st.markdown("<div style='height: 1.5rem'></div>", unsafe_allow_html=True)

    # Save button
    col_save, col_spacer = st.columns([1, 3])
    with col_save:
        if st.button("Save Settings", type="primary", use_container_width=True):
            _save_current_settings()
            st.success(
                f"Settings saved successfully to `{_SETTINGS_FILE.relative_to(Path.cwd()) if _SETTINGS_FILE.is_relative_to(Path.cwd()) else _SETTINGS_FILE}`. "
                "They will be restored on your next session."
            )



def _render_profile_settings():
    """Render profile settings card."""

    st.markdown(
        f"""
        <div style="background: {COLORS["bg_card"]}; border: 1px solid {COLORS["border_primary"]}; 
                    border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem;">
            <div style="font-size: 1rem; font-weight: 600; color: {COLORS["text_primary"]}; 
                        margin-bottom: 1rem; padding-bottom: 0.75rem; 
                        border-bottom: 1px solid {COLORS["border_subtle"]};">
                Profile Settings
            </div>
        </div>
    """,
        unsafe_allow_html=True,
    )

    # Get user data from session
    user = st.session_state.get("user", {})

    with st.container():
        st.text_input(
            "Full Name",
            value=user.get("full_name", ""),
            key="settings_name",
            placeholder="Enter your full name",
        )

        st.text_input(
            "Email Address",
            value=user.get("email", ""),
            key="settings_email",
            placeholder="Enter your email",
        )

        st.selectbox(
            "Role",
            options=["Administrator", "Project Manager", "Data Analyst", "Viewer"],
            key="settings_role",
        )


def _render_notification_settings():
    """Render notification settings card."""

    st.markdown(
        f"""
        <div style="background: {COLORS["bg_card"]}; border: 1px solid {COLORS["border_primary"]}; 
                    border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem;">
            <div style="font-size: 1rem; font-weight: 600; color: {COLORS["text_primary"]}; 
                        margin-bottom: 1rem; padding-bottom: 0.75rem; 
                        border-bottom: 1px solid {COLORS["border_subtle"]};">
                Notification Preferences
            </div>
        </div>
    """,
        unsafe_allow_html=True,
    )

    with st.container():
        st.toggle(
            "Email notifications for high-risk alerts",
            value=True,
            key="notif_email_high_risk",
        )

        st.toggle("In-app anomaly notifications", value=True, key="notif_anomaly")

        st.toggle("Weekly risk summary digest", value=False, key="notif_weekly_digest")

        st.toggle("Real-time Slack notifications", value=False, key="notif_slack")


def _render_jira_settings():
    """Render Jira integration settings card."""

    st.markdown(
        f"""
        <div style="background: {COLORS["bg_card"]}; border: 1px solid {COLORS["border_primary"]}; 
                    border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem;">
            <div style="font-size: 1rem; font-weight: 600; color: {COLORS["text_primary"]}; 
                        margin-bottom: 1rem; padding-bottom: 0.75rem; 
                        border-bottom: 1px solid {COLORS["border_subtle"]};">
                Jira Integration
            </div>
        </div>
    """,
        unsafe_allow_html=True,
    )

    with st.container():
        st.text_input(
            "Jira Instance URL",
            placeholder="https://your-company.atlassian.net",
            key="jira_url",
        )

        st.text_input(
            "API Token",
            type="password",
            placeholder="Enter your Jira API token",
            key="jira_token",
        )

        st.text_input("Project Key", placeholder="e.g., PROJ", key="jira_project_key")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Test Connection", key="test_jira", use_container_width=True):
                jira_url = st.session_state.get("jira_url", "")
                if jira_url:
                    st.info(
                        "Connection is validated via OAuth on the **Jira Sync** page. "
                        "Navigate to **Page 6 → Jira Sync** to authorize and test."
                    )
                else:
                    st.warning("Enter a Jira Instance URL above first.")

        with col2:
            if st.button(
                "Go to Jira Sync", key="sync_jira", type="secondary", use_container_width=True
            ):
                from app.utils.routes import JIRA_SYNC_PAGE, switch_page_safe
                switched = switch_page_safe(JIRA_SYNC_PAGE)
                if not switched:
                    st.info("Navigate to **Page 6 → Jira Sync** in the sidebar.")


def _render_model_settings():
    """Render model configuration settings card."""

    st.markdown(
        f"""
        <div style="background: {COLORS["bg_card"]}; border: 1px solid {COLORS["border_primary"]}; 
                    border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem;">
            <div style="font-size: 1rem; font-weight: 600; color: {COLORS["text_primary"]}; 
                        margin-bottom: 1rem; padding-bottom: 0.75rem; 
                        border-bottom: 1px solid {COLORS["border_subtle"]};">
                Model Configuration
            </div>
        </div>
    """,
        unsafe_allow_html=True,
    )

    with st.container():
        st.slider(
            "Anomaly Detection Sensitivity",
            min_value=0.01,
            max_value=0.15,
            value=0.05,
            step=0.01,
            format="%.2f",
            key="model_anomaly_sensitivity",
            help="Lower values detect fewer anomalies (stricter), higher values detect more (lenient)",
        )

        st.slider(
            "Forecast Horizon (days)",
            min_value=7,
            max_value=90,
            value=14,
            step=7,
            key="model_forecast_horizon",
            help="Number of days to forecast into the future",
        )

        st.selectbox(
            "Risk Threshold Mode",
            options=["Conservative", "Balanced", "Aggressive"],
            index=1,
            key="model_risk_threshold",
            help="Conservative flags more risks, Aggressive flags fewer",
        )

        st.selectbox(
            "GenAI Provider",
            options=["NVIDIA (Qwen 3.5)", "OpenAI (GPT-4)", "Anthropic (Claude)"],
            index=0,
            key="model_genai_provider",
            help="Select the AI provider for mitigation recommendations",
        )

        # Model info section
        st.markdown(
            f"""
            <div style="background: {COLORS["bg_tertiary"]}; border-radius: 8px; 
                        padding: 1rem; margin-top: 1rem;">
                <div style="font-size: 0.8rem; font-weight: 600; color: {COLORS["text_muted"]}; 
                            text-transform: uppercase; letter-spacing: 0.04em; margin-bottom: 0.5rem;">
                    Current Model
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                    <span style="color: {COLORS["text_secondary"]}; font-size: 0.875rem;">Classifier</span>
                    <span style="color: {COLORS["text_primary"]}; font-size: 0.875rem; font-weight: 500;">XGBoost v2.0</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                    <span style="color: {COLORS["text_secondary"]}; font-size: 0.875rem;">Last Trained</span>
                    <span style="color: {COLORS["text_primary"]}; font-size: 0.875rem; font-weight: 500;">Apr 7, 2026</span>
                </div>
                <div style="display: flex; justify-content: space-between;">
                    <span style="color: {COLORS["text_secondary"]}; font-size: 0.875rem;">Accuracy</span>
                    <span style="color: {COLORS["success"]}; font-size: 0.875rem; font-weight: 500;">87.3%</span>
                </div>
            </div>
        """,
            unsafe_allow_html=True,
        )
