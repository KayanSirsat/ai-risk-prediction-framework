"""
Dashboard View
AI-Driven Risk Prediction Framework

Premium overview dashboard with metrics, micro-copy, and chart placeholders.
"""

import streamlit as st
import pandas as pd

from app.utils.styles import render_page_header, render_section_header, COLORS


def render_dashboard():
    """Render the main dashboard overview page."""

    # Page header
    render_page_header(
        title="Dashboard Overview",
        subtitle="Real-time insights into your project risk landscape",
    )

    # Top Metrics Row - 4 columns with micro-copy
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Global Risk Score",
            value="72.4",
            delta="-3.2%",
            delta_color="inverse",
        )
        st.markdown(
            '<div class="micro-copy micro-copy-positive">↓ 3.2% from last week</div>',
            unsafe_allow_html=True,
        )

    with col2:
        st.metric(label="Total Budget", value="$1.2M", delta="+$120K")
        st.markdown(
            '<div class="micro-copy micro-copy-neutral">On track with forecast</div>',
            unsafe_allow_html=True,
        )

    with col3:
        st.metric(label="Active Tickets", value="147", delta="+12")
        st.markdown(
            '<div class="micro-copy micro-copy-positive">↑ 12 new this week</div>',
            unsafe_allow_html=True,
        )

    with col4:
        st.metric(
            label="Predicted Delays", value="8", delta="+2", delta_color="inverse"
        )
        st.markdown(
            '<div class="micro-copy micro-copy-negative">↑ 2 since yesterday</div>',
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 2.5rem'></div>", unsafe_allow_html=True)

    # Charts Section - Two Main Columns
    col_left, col_right = st.columns([2, 1])

    with col_left:
        render_section_header("Risk Distribution Over Time")
        st.markdown(
            """
            <div class="chart-placeholder">
                <div class="chart-placeholder-icon">
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <line x1="12" y1="20" x2="12" y2="10"></line>
                        <line x1="18" y1="20" x2="18" y2="4"></line>
                        <line x1="6" y1="20" x2="6" y2="16"></line>
                    </svg>
                </div>
                <div class="chart-placeholder-title">Time-series forecasting chart</div>
                <div class="chart-placeholder-subtitle">Prophet-based risk projection visualization</div>
            </div>
        """,
            unsafe_allow_html=True,
        )

    with col_right:
        render_section_header("Risk Breakdown")
        st.markdown(
            """
            <div class="chart-placeholder">
                <div class="chart-placeholder-icon">
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M21.21 15.89A10 10 0 1 1 8 2.83"></path>
                        <path d="M22 12A10 10 0 0 0 12 2v10z"></path>
                    </svg>
                </div>
                <div class="chart-placeholder-title">Distribution pie chart</div>
                <div class="chart-placeholder-subtitle">High / Medium / Low breakdown</div>
            </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 2.5rem'></div>", unsafe_allow_html=True)

    # Alerts Section
    render_section_header("Recent Anomaly Alerts")

    # Create alerts with styled badges
    _render_alerts_table()


def _render_alerts_table():
    """Render the alerts table with color-coded badges."""

    alerts_data = [
        {
            "timestamp": "2026-04-08 09:23",
            "ticket": "PROJ-1234",
            "alert": "Budget Spike",
            "severity": "High",
            "status": "Open",
        },
        {
            "timestamp": "2026-04-08 08:45",
            "ticket": "PROJ-1189",
            "alert": "Velocity Drop",
            "severity": "Medium",
            "status": "Acknowledged",
        },
        {
            "timestamp": "2026-04-07 16:30",
            "ticket": "PROJ-1156",
            "alert": "Scope Creep",
            "severity": "Low",
            "status": "Resolved",
        },
        {
            "timestamp": "2026-04-07 14:15",
            "ticket": "PROJ-1142",
            "alert": "Resource Gap",
            "severity": "Medium",
            "status": "Open",
        },
    ]

    # Build table HTML
    rows_html = ""
    for alert in alerts_data:
        severity_class = alert["severity"].lower()
        status_class = (
            "info"
            if alert["status"] == "Open"
            else ("low" if alert["status"] == "Resolved" else "medium")
        )

        rows_html += f"""
            <tr>
                <td style="font-size: 0.875rem; color: {COLORS["text_secondary"]};">{alert["timestamp"]}</td>
                <td>
                    <code style="background: {COLORS["bg_elevated"]}; padding: 0.25rem 0.625rem; 
                                 border-radius: 6px; color: {COLORS["brand_light"]}; font-size: 0.8rem; font-weight: 600;">
                        {alert["ticket"]}
                    </code>
                </td>
                <td style="font-size: 0.875rem; color: {COLORS["text_secondary"]};">{alert["alert"]}</td>
                <td><span class="badge badge-{severity_class}">{alert["severity"]}</span></td>
                <td><span class="badge badge-{status_class}">{alert["status"]}</span></td>
            </tr>
        """

    st.markdown(
        f"""
        <div style="background: {COLORS["bg_card"]}; border: 1px solid {COLORS["border_primary"]}; 
                    border-radius: 12px; overflow: hidden; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.3);">
            <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr style="background: {COLORS["bg_elevated"]};">
                        <th style="text-align: left; padding: 1rem; color: {COLORS["text_muted"]}; 
                                   font-size: 0.75rem; font-weight: 600; text-transform: uppercase; 
                                   letter-spacing: 0.05em;">Timestamp</th>
                        <th style="text-align: left; padding: 1rem; color: {COLORS["text_muted"]}; 
                                   font-size: 0.75rem; font-weight: 600; text-transform: uppercase; 
                                   letter-spacing: 0.05em;">Ticket</th>
                        <th style="text-align: left; padding: 1rem; color: {COLORS["text_muted"]}; 
                                   font-size: 0.75rem; font-weight: 600; text-transform: uppercase; 
                                   letter-spacing: 0.05em;">Alert Type</th>
                        <th style="text-align: left; padding: 1rem; color: {COLORS["text_muted"]}; 
                                   font-size: 0.75rem; font-weight: 600; text-transform: uppercase; 
                                   letter-spacing: 0.05em;">Severity</th>
                        <th style="text-align: left; padding: 1rem; color: {COLORS["text_muted"]}; 
                                   font-size: 0.75rem; font-weight: 600; text-transform: uppercase; 
                                   letter-spacing: 0.05em;">Status</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
        </div>
        <style>
            table tbody tr td {{
                padding: 0.875rem 1rem;
                border-bottom: 1px solid {COLORS["border_primary"]};
            }}
            table tbody tr:hover td {{
                background: {COLORS["bg_elevated"]};
            }}
            table tbody tr:last-child td {{
                border-bottom: none;
            }}
        </style>
    """,
        unsafe_allow_html=True,
    )
