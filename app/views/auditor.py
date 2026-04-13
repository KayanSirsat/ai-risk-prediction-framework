"""
Ticket Auditor View
AI-Driven Risk Prediction Framework

Premium ticket analysis with card layout, risk banners, and SHAP visualization.
"""

import streamlit as st
import pandas as pd
import os

from app.utils.styles import render_page_header, render_section_header, COLORS

# Configuration
DATA_PATH = "data/ml_ready_data.csv"
MODEL_PATH = "models/xgb_model.pkl"

# Try to import legacy components
try:
    import joblib
    from app.components.ticket_viewer import render_ticket_context
    from app.components.shap_visuals import render_shap_table
    from app.components.genai_auditor import render_mitigation_engine

    LEGACY_AVAILABLE = True
except ImportError:
    LEGACY_AVAILABLE = False


@st.cache_data
def load_dataset(path: str) -> pd.DataFrame:
    """Load dataset from CSV with caching."""
    if os.path.exists(path):
        return pd.read_csv(path)
    return None


@st.cache_resource
def load_model(path: str):
    """Load ML model from pickle with caching."""
    if os.path.exists(path) and LEGACY_AVAILABLE:
        import joblib

        return joblib.load(path)
    return None


def render_auditor():
    """Render the ticket auditor page."""

    # Page header
    render_page_header(
        title="Ticket Auditor",
        subtitle="Analyze individual tickets with AI-powered risk assessment",
    )

    # Load data
    dataset = load_dataset(DATA_PATH)
    model = load_model(MODEL_PATH)

    # Check data availability
    if dataset is None or model is None:
        _render_demo_auditor()
        return

    if LEGACY_AVAILABLE:
        _render_full_auditor(dataset, model)
    else:
        _render_demo_auditor()


def _render_full_auditor(dataset: pd.DataFrame, model):
    """Render the full auditor with live data."""

    # Card Layout for Ticket Selection
    st.markdown(
        f"""
        <div class="premium-card" style="margin-bottom: 1.5rem;">
            <div style="font-size: 0.75rem; font-weight: 600; color: {COLORS["text_muted"]}; 
                        text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.75rem;">
                Select Ticket to Audit
            </div>
        </div>
    """,
        unsafe_allow_html=True,
    )

    ticket_index = st.selectbox(
        "Select Ticket",
        options=range(len(dataset)),
        format_func=lambda x: f"Ticket #{x}",
        label_visibility="collapsed",
    )

    ticket_data = dataset.iloc[ticket_index]

    # Render ticket context
    risk_label, processed_features, original_features = render_ticket_context(
        ticket_data, model, dataset
    )

    if risk_label is None:
        return

    # Risk Banner with Thick Left Border
    _render_risk_banner(risk_label, confidence=0.87)

    # Ticket Metrics Row
    st.markdown(
        f"""
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-bottom: 1.5rem;">
            <div class="premium-card" style="padding: 1rem;">
                <div style="font-size: 0.7rem; font-weight: 600; color: {COLORS["text_muted"]}; 
                            text-transform: uppercase; letter-spacing: 0.05em;">Estimated Days</div>
                <div style="font-size: 1.5rem; font-weight: 700; color: {COLORS["text_primary"]}; margin-top: 0.5rem;">
                    {ticket_data.get("Estimated_Days", "N/A")}
                </div>
            </div>
            <div class="premium-card" style="padding: 1rem;">
                <div style="font-size: 0.7rem; font-weight: 600; color: {COLORS["text_muted"]}; 
                            text-transform: uppercase; letter-spacing: 0.05em;">Story Points</div>
                <div style="font-size: 1.5rem; font-weight: 700; color: {COLORS["text_primary"]}; margin-top: 0.5rem;">
                    {ticket_data.get("Story_Points", "N/A")}
                </div>
            </div>
            <div class="premium-card" style="padding: 1rem;">
                <div style="font-size: 0.7rem; font-weight: 600; color: {COLORS["text_muted"]}; 
                            text-transform: uppercase; letter-spacing: 0.05em;">Budget</div>
                <div style="font-size: 1.5rem; font-weight: 700; color: {COLORS["text_primary"]}; margin-top: 0.5rem;">
                    ${ticket_data.get("Budget_Allocated", 0):,.0f}
                </div>
            </div>
            <div class="premium-card" style="padding: 1rem;">
                <div style="font-size: 0.7rem; font-weight: 600; color: {COLORS["text_muted"]}; 
                            text-transform: uppercase; letter-spacing: 0.05em;">Priority</div>
                <div style="font-size: 1.5rem; font-weight: 700; color: {COLORS["text_primary"]}; margin-top: 0.5rem;">
                    {ticket_data.get("Priority", "N/A")}
                </div>
            </div>
        </div>
    """,
        unsafe_allow_html=True,
    )

    # Two-column layout
    col1, col2 = st.columns(2)

    with col1:
        render_section_header("Feature Importance (SHAP)")
        st.markdown('<div class="premium-card">', unsafe_allow_html=True)
        render_shap_table(processed_features, model)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        render_section_header("AI Mitigation Strategy")
        st.markdown('<div class="premium-card">', unsafe_allow_html=True)
        shap_drivers = {
            "summary": str(ticket_data.get("Summary", "N/A")),
            "priority": str(ticket_data.get("Priority", "N/A")),
            "assignee_seniority": str(ticket_data.get("Assignee_Seniority", "N/A")),
            "estimated_days": int(ticket_data.get("Estimated_Days", 0)),
            "story_points": int(ticket_data.get("Story_Points", 0)),
            "budget_allocated": float(ticket_data.get("Budget_Allocated", 0)),
            "top_factors": list(processed_features.columns[:5]),
        }
        render_mitigation_engine(ticket_index, risk_label, shap_drivers)
        st.markdown("</div>", unsafe_allow_html=True)


def _render_demo_auditor():
    """Render demo auditor with mock data."""

    # Card Layout for Ticket Selection
    st.markdown(
        f"""
        <div class="premium-card" style="margin-bottom: 1.5rem;">
            <div style="font-size: 0.75rem; font-weight: 600; color: {COLORS["text_muted"]}; 
                        text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.75rem;">
                Select Ticket to Audit
            </div>
        </div>
    """,
        unsafe_allow_html=True,
    )

    ticket_id = st.selectbox(
        "Select Ticket",
        options=["PROJ-1234", "PROJ-1235", "PROJ-1236", "PROJ-1237", "PROJ-1238"],
        label_visibility="collapsed",
    )

    # Demo risk data
    demo_risks = {
        "PROJ-1234": {
            "level": "High",
            "confidence": 0.89,
            "days": 14,
            "points": 8,
            "budget": 24500,
            "priority": "High",
        },
        "PROJ-1235": {
            "level": "Medium",
            "confidence": 0.72,
            "days": 7,
            "points": 5,
            "budget": 12000,
            "priority": "Medium",
        },
        "PROJ-1236": {
            "level": "Low",
            "confidence": 0.94,
            "days": 3,
            "points": 3,
            "budget": 5500,
            "priority": "Low",
        },
        "PROJ-1237": {
            "level": "High",
            "confidence": 0.81,
            "days": 21,
            "points": 13,
            "budget": 35000,
            "priority": "High",
        },
        "PROJ-1238": {
            "level": "Medium",
            "confidence": 0.67,
            "days": 10,
            "points": 5,
            "budget": 18000,
            "priority": "Medium",
        },
    }

    risk_data = demo_risks.get(
        ticket_id,
        {
            "level": "Medium",
            "confidence": 0.75,
            "days": 10,
            "points": 5,
            "budget": 15000,
            "priority": "Medium",
        },
    )

    # Risk Banner with Thick Left Border
    _render_risk_banner(risk_data["level"], risk_data["confidence"])

    # Ticket Metrics Row
    st.markdown(
        f"""
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-bottom: 1.5rem;">
            <div class="premium-card" style="padding: 1rem;">
                <div style="font-size: 0.7rem; font-weight: 600; color: {COLORS["text_muted"]}; 
                            text-transform: uppercase; letter-spacing: 0.05em;">Estimated Days</div>
                <div style="font-size: 1.5rem; font-weight: 700; color: {COLORS["text_primary"]}; margin-top: 0.5rem;">
                    {risk_data["days"]}
                </div>
            </div>
            <div class="premium-card" style="padding: 1rem;">
                <div style="font-size: 0.7rem; font-weight: 600; color: {COLORS["text_muted"]}; 
                            text-transform: uppercase; letter-spacing: 0.05em;">Story Points</div>
                <div style="font-size: 1.5rem; font-weight: 700; color: {COLORS["text_primary"]}; margin-top: 0.5rem;">
                    {risk_data["points"]}
                </div>
            </div>
            <div class="premium-card" style="padding: 1rem;">
                <div style="font-size: 0.7rem; font-weight: 600; color: {COLORS["text_muted"]}; 
                            text-transform: uppercase; letter-spacing: 0.05em;">Budget</div>
                <div style="font-size: 1.5rem; font-weight: 700; color: {COLORS["text_primary"]}; margin-top: 0.5rem;">
                    ${risk_data["budget"]:,}
                </div>
            </div>
            <div class="premium-card" style="padding: 1rem;">
                <div style="font-size: 0.7rem; font-weight: 600; color: {COLORS["text_muted"]}; 
                            text-transform: uppercase; letter-spacing: 0.05em;">Priority</div>
                <div style="font-size: 1.5rem; font-weight: 700; color: {COLORS["text_primary"]}; margin-top: 0.5rem;">
                    {risk_data["priority"]}
                </div>
            </div>
        </div>
    """,
        unsafe_allow_html=True,
    )

    # Two-column layout
    col1, col2 = st.columns(2)

    with col1:
        render_section_header("Feature Importance (SHAP)")
        _render_demo_shap_table()

    with col2:
        render_section_header("AI Mitigation Strategy")
        _render_demo_mitigation(risk_data["level"])


def _render_risk_banner(risk_level: str, confidence: float):
    """Render risk banner with thick left border and semi-transparent background."""

    level_lower = risk_level.lower()

    st.markdown(
        f"""
        <div class="risk-banner risk-banner-{level_lower}">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <div class="risk-banner-label">Predicted Risk Level</div>
                    <div class="risk-banner-value risk-value-{level_lower}">{risk_level.upper()}</div>
                </div>
                <div style="text-align: right;">
                    <div class="risk-banner-label">Confidence</div>
                    <div class="risk-banner-value risk-value-{level_lower}">{confidence:.0%}</div>
                </div>
            </div>
        </div>
    """,
        unsafe_allow_html=True,
    )


def _render_demo_shap_table():
    """Render demo SHAP table with Indigo-500 progress bars."""

    features = [
        {"name": "Budget Variance", "influence": 0.34, "direction": "negative"},
        {"name": "Timeline Pressure", "influence": 0.28, "direction": "negative"},
        {"name": "Team Experience", "influence": 0.18, "direction": "positive"},
        {"name": "Scope Complexity", "influence": 0.12, "direction": "negative"},
        {"name": "Historical Success", "influence": 0.08, "direction": "positive"},
    ]

    rows_html = ""
    for feat in features:
        bar_color = COLORS["brand_primary"]  # Indigo-500 for all bars
        bar_width = feat["influence"] * 100
        direction_icon = "↓" if feat["direction"] == "negative" else "↑"
        direction_color = (
            COLORS["error"] if feat["direction"] == "negative" else COLORS["success"]
        )

        rows_html += f"""
            <div style="padding: 0.875rem 0; border-bottom: 1px solid {COLORS["border_primary"]};">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.5rem;">
                    <span style="color: {COLORS["text_secondary"]}; font-size: 0.875rem; font-weight: 500;">
                        {feat["name"]}
                    </span>
                    <div style="display: flex; align-items: center; gap: 0.75rem;">
                        <span style="color: {COLORS["text_primary"]}; font-weight: 600; font-size: 0.875rem;">
                            {feat["influence"]:.0%}
                        </span>
                        <span style="color: {direction_color}; font-size: 0.9rem; font-weight: 600;">
                            {direction_icon}
                        </span>
                    </div>
                </div>
                <div class="shap-progress-bar">
                    <div class="shap-progress-fill" style="width: {bar_width}%;"></div>
                </div>
            </div>
        """

    st.markdown(
        f"""
        <div class="premium-card">
            {rows_html}
        </div>
    """,
        unsafe_allow_html=True,
    )


def _render_demo_mitigation(risk_level: str):
    """Render demo mitigation strategies."""

    strategies = {
        "High": [
            "Immediately allocate additional budget buffer of 15-20% to absorb projected overruns",
            "Schedule daily standups with technical leads to identify and resolve blockers proactively",
            "Consider scope reduction by deferring non-critical features to a follow-up release",
        ],
        "Medium": [
            "Review current resource allocation and consider redistributing workload across team members",
            "Implement bi-weekly risk review meetings to monitor key indicators",
            "Document dependencies and establish contingency plans for critical path items",
        ],
        "Low": [
            "Maintain current project trajectory with standard monitoring procedures",
            "Continue weekly progress reviews and stakeholder updates",
            "Document lessons learned for future project planning",
        ],
    }

    steps = strategies.get(risk_level, strategies["Medium"])

    steps_html = ""
    for i, step in enumerate(steps, 1):
        steps_html += f"""
            <div style="display: flex; gap: 1rem; padding: 1rem 0; 
                        border-bottom: 1px solid {COLORS["border_primary"]};">
                <div style="width: 32px; height: 32px; background: {COLORS["brand_primary"]}; 
                            border-radius: 8px; display: flex; align-items: center; justify-content: center;
                            color: white; font-weight: 700; font-size: 0.875rem; flex-shrink: 0;">
                    {i}
                </div>
                <div style="color: {COLORS["text_secondary"]}; font-size: 0.9rem; line-height: 1.6; padding-top: 0.25rem;">
                    {step}
                </div>
            </div>
        """

    st.markdown(
        f"""
        <div class="premium-card">
            <div style="display: flex; align-items: center; gap: 0.75rem; padding-bottom: 1rem; 
                        border-bottom: 1px solid {COLORS["border_primary"]}; margin-bottom: 0.5rem;">
                <div style="font-size: 0.75rem; font-weight: 600; color: {COLORS["text_muted"]}; 
                            text-transform: uppercase; letter-spacing: 0.05em;">
                    Recommended Actions
                </div>
                <div style="background: {COLORS["brand_subtle"]}; color: {COLORS["brand_primary"]}; 
                            font-size: 0.7rem; padding: 0.25rem 0.625rem; border-radius: 6px; font-weight: 600;">
                    AI Generated
                </div>
            </div>
            {steps_html}
            <div style="padding-top: 1rem; margin-top: 0.5rem;">
                <div style="font-size: 0.75rem; color: {COLORS["text_disabled"]};">
                    Generated by Qwen 3.5 via NVIDIA Inference API
                </div>
            </div>
        </div>
    """,
        unsafe_allow_html=True,
    )
