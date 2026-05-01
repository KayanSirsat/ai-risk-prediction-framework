"""Ticket auditor view with split-screen explainability and mitigation guidance."""

from __future__ import annotations

import os

import pandas as pd
import streamlit as st

from app.components.audit_trail_viewer import render_audit_trail
from app.components.genai_auditor import render_mitigation_engine
from app.components.shap_visuals import (
    get_top_driver_names,
    render_shap_force_plot,
    render_shap_table,
)
from app.components.ticket_viewer import render_ticket_context
from app.utils.routes import WHAT_IF_PAGE, switch_page_safe
from app.utils.styles import render_page_header, render_section_header

DATA_PATH = "data/ml_ready_data.csv"
MODEL_PATH = "models/xgb_model.pkl"


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


def _ticket_label(ticket_data: pd.Series, ticket_index: int) -> str:
    issue_key = ticket_data.get("Issue_key")
    issue_id = ticket_data.get("Issue_ID")
    if pd.notna(issue_key):
        return str(issue_key)
    if pd.notna(issue_id):
        return str(issue_id)
    return f"TICKET-{ticket_index}"


def _compute_confidence(model, processed_features: pd.DataFrame, risk_label: str) -> float:
    risk_map = {"Low": 0, "Medium": 1, "High": 2}
    try:
        probabilities = model.predict_proba(processed_features)[0]
        idx = risk_map.get(risk_label, 0)
        return float(probabilities[idx] * 100)
    except Exception:
        return 0.0


def _render_split_columns(
    ticket_index: int,
    ticket_data: pd.Series,
    model,
    dataset: pd.DataFrame,
    shap_mode: str,
    button_key: str,
) -> None:
    risk_label, processed_features, _ = render_ticket_context(ticket_data, model, dataset)
    if risk_label is None:
        return

    confidence_pct = _compute_confidence(model, processed_features, risk_label)
    _render_risk_banner(risk_label, confidence=confidence_pct / 100)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Estimated Days", f"{ticket_data.get('Estimated_Days', 'N/A')}")
    m2.metric("Story Points", f"{ticket_data.get('Story_Points', 'N/A')}")
    m3.metric("Budget", f"${ticket_data.get('Budget_Allocated', 0):,.0f}")
    m4.metric("Priority", f"{ticket_data.get('Priority', 'N/A')}")

    if st.button("🎯 Try What-If Scenario", key=f"what_if_{ticket_index}", use_container_width=True):
        st.session_state["what_if_ticket_index"] = int(ticket_index)
        switched = switch_page_safe(WHAT_IF_PAGE)
        if not switched:
            st.warning("What-If Simulation page is not available in this environment.")

    col1, col2 = st.columns([11, 9])

    top_drivers = get_top_driver_names(processed_features, model, top_n=5)

    with col1:
        st.markdown('<div class="auditor-sticky-title">Why this ticket is risky</div>', unsafe_allow_html=True)
        st.caption("Top factors that increase risk for this ticket.")
        st.markdown('<div class="premium-card">', unsafe_allow_html=True)
        if shap_mode == "Force View":
            render_shap_force_plot(processed_features, model)
        else:
            render_shap_table(processed_features, model)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="auditor-sticky-title">Suggested actions</div>', unsafe_allow_html=True)
        st.caption("Practical steps to lower delivery risk.")
        st.markdown('<div class="premium-card">', unsafe_allow_html=True)
        shap_drivers = {
            "summary": str(ticket_data.get("Summary", "N/A")),
            "priority": str(ticket_data.get("Priority", "N/A")),
            "assignee_seniority": str(ticket_data.get("Assignee_Seniority", "N/A")),
            "estimated_days": int(ticket_data.get("Estimated_Days", 0)),
            "story_points": int(ticket_data.get("Story_Points", 0)),
            "budget_allocated": float(ticket_data.get("Budget_Allocated", 0)),
            "top_factors": top_drivers,
        }
        render_mitigation_engine(
            ticket_index,
            risk_label,
            shap_drivers,
            audit_context={
                "ticket_id": _ticket_label(ticket_data, ticket_index),
                "confidence_pct": confidence_pct,
                "top_drivers": top_drivers,
            },
            button_key=button_key,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    render_audit_trail(_ticket_label(ticket_data, ticket_index))


def _render_full_auditor(dataset: pd.DataFrame, model) -> None:
    """Render full auditor with optional multi-ticket comparison."""
    render_section_header("Select Ticket")

    preselected = int(st.session_state.get("auditor_ticket_index", 0) or 0)
    if preselected < 0 or preselected >= len(dataset):
        preselected = 0

    single_ticket = st.selectbox(
        "Primary ticket",
        options=range(len(dataset)),
        index=preselected,
        format_func=lambda x: f"Ticket #{x}",
        label_visibility="collapsed",
    )
    st.session_state["auditor_ticket_index"] = int(single_ticket)

    comparison_mode = st.toggle(
        "Compare multiple tickets",
        value=False,
        help="Recommended: compare up to 3 tickets side-by-side in stacked panels.",
    )
    shap_mode = st.radio(
        "Explanation view",
        options=["Table View", "Force View"],
        horizontal=True,
    )

    if comparison_mode:
        selected = st.multiselect(
            "Tickets to compare (max 3)",
            options=range(len(dataset)),
            default=[single_ticket],
            format_func=lambda x: f"Ticket #{x}",
            max_selections=3,
        )
        if not selected:
            st.info("Select at least one ticket for comparison.")
            return
        for idx in selected:
            ticket_data = dataset.iloc[int(idx)]
            with st.expander(f"Ticket #{idx}", expanded=True):
                _render_split_columns(
                    ticket_index=int(idx),
                    ticket_data=ticket_data,
                    model=model,
                    dataset=dataset,
                    shap_mode=shap_mode,
                    button_key=f"mitigate_{idx}",
                )
    else:
        ticket_data = dataset.iloc[int(single_ticket)]
        _render_split_columns(
            ticket_index=int(single_ticket),
            ticket_data=ticket_data,
            model=model,
            dataset=dataset,
            shap_mode=shap_mode,
            button_key=f"mitigate_{single_ticket}",
        )


def _render_risk_banner(risk_level: str, confidence: float) -> None:
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

