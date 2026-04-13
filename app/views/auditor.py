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

import joblib
from app.components.ticket_viewer import render_ticket_context
from app.components.shap_visuals import render_shap_table
from app.components.genai_auditor import render_mitigation_engine


@st.cache_data
def load_dataset(path: str) -> pd.DataFrame:
    """Load dataset from CSV with caching."""
    if os.path.exists(path):
        return pd.read_csv(path)
    return None


@st.cache_resource
def load_model(path: str):
    """Load ML model from pickle with caching."""
    if os.path.exists(path):
        import joblib

        return joblib.load(path)
    return None


def render_auditor():
    """Render the ticket auditor page."""

    # Page header
    render_page_header(
        title="Ticket Auditor",
        subtitle="Review one ticket at a time with plain-language risk guidance",
    )

    # Load data
    dataset = load_dataset(DATA_PATH)
    model = load_model(MODEL_PATH)

    # Check data availability
    if dataset is None or model is None:
        st.warning("Model or data not available. Please ensure data is generated.")
        return

    _render_full_auditor(dataset, model)


def _render_full_auditor(dataset: pd.DataFrame, model):
    """Render the full auditor with live data."""
    render_section_header("Select Ticket")

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

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Estimated Days", f"{ticket_data.get('Estimated_Days', 'N/A')}")
    m2.metric("Story Points", f"{ticket_data.get('Story_Points', 'N/A')}")
    m3.metric("Budget", f"${ticket_data.get('Budget_Allocated', 0):,.0f}")
    m4.metric("Priority", f"{ticket_data.get('Priority', 'N/A')}")

    # Two-column layout
    col1, col2 = st.columns(2)

    with col1:
        render_section_header("Why this ticket is risky")
        st.caption("Top factors that increase risk for this ticket.")
        st.markdown('<div class="premium-card">', unsafe_allow_html=True)
        render_shap_table(processed_features, model)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        render_section_header("Suggested actions")
        st.caption("Practical steps to lower delivery risk.")
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



