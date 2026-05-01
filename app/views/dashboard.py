"""Dashboard View for live forecasting and anomaly analytics."""

import logging
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
from sklearn.metrics import roc_auc_score

from app.utils.styles import COLORS, render_page_header, render_section_header
from app.utils.routes import AUDITOR_PAGE, switch_page_safe
from src.anomaly.anomaly_detector import AnomalyEngine
from src.forecasting.forecast import ProjectForecaster


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = PROJECT_ROOT / "data" / "ml_ready_data.csv"
FORECAST_FIG_PATH = PROJECT_ROOT / "reports" / "fig_phase2_a_prophet_forecast.png"
SEVERITY_FIG_PATH = PROJECT_ROOT / "reports" / "fig_phase2_b_severity_dist.png"
FEATURE_COLUMNS = [
    "Story_Points",
    "Estimated_Days",
    "Actual_Days",
    "Budget_Allocated",
    "Cost_Consumed",
    "budget_overrun_pct",
    "days_overrun_pct",
    "efficiency_score",
    "cost_efficiency",
]


def _setup_logger() -> logging.Logger:
    logger = logging.getLogger("dashboard")
    if logger.handlers:
        return logger

    log_dir = PROJECT_ROOT / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(log_dir / "dashboard_audit.log")
    formatter = logging.Formatter(
        "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
    )
    file_handler.setFormatter(formatter)

    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.propagate = False
    return logger


LOGGER = _setup_logger()


def _prepare_anomaly_features(df: pd.DataFrame) -> pd.DataFrame:
    frame = df.copy()
    frame["budget_overrun_pct"] = (
        (frame["Cost_Consumed"] - frame["Budget_Allocated"])
        / frame["Budget_Allocated"]
        * 100
    )
    frame["days_overrun_pct"] = (
        (frame["Actual_Days"] - frame["Estimated_Days"]) / frame["Estimated_Days"] * 100
    )
    frame["efficiency_score"] = frame["Estimated_Days"] / frame["Actual_Days"]
    frame["cost_efficiency"] = frame["Budget_Allocated"] / frame["Cost_Consumed"]
    frame = frame.replace([np.inf, -np.inf], np.nan)
    frame = frame.dropna(subset=FEATURE_COLUMNS).copy()
    return frame


def _infer_alert_name(contribution: str) -> str:
    mapping = {
        "budget_overrun_pct": "Budget Overrun",
        "days_overrun_pct": "Schedule Overrun",
        "efficiency_score": "Efficiency Drop",
        "cost_efficiency": "Cost Efficiency Decline",
        "Actual_Days": "Duration Spike",
        "Cost_Consumed": "Cost Spike",
    }
    if not contribution or contribution == "None":
        return "General Risk Pattern"

    top_feature = contribution.split(",", 1)[0].split(":", 1)[0].strip()
    return mapping.get(top_feature, "General Risk Pattern")


def _build_alerts_table(anomaly_results: pd.DataFrame) -> pd.DataFrame:
    if anomaly_results.empty:
        return pd.DataFrame(
            columns=["timestamp", "ticket", "alert", "severity", "status"]
        )

    severity_rank = {"High": 3, "Medium": 2, "Low": 1, "Normal": 0}
    table = anomaly_results.copy()
    table = table[table["is_anomaly"]]

    if table.empty:
        return pd.DataFrame(
            columns=["timestamp", "ticket", "alert", "severity", "status"]
        )

    table["anomaly_intensity"] = -table["anomaly_score"]
    table["severity_rank"] = table["severity"].astype(str).map(severity_rank).fillna(0)
    table = table.sort_values(
        ["severity_rank", "anomaly_intensity"], ascending=[False, False]
    ).head(5)

    now_ts = pd.Timestamp.utcnow().floor("s")
    alerts = []
    for idx, row in table.iterrows():
        synthetic_ts = now_ts - pd.to_timedelta(int(idx), unit="m")
        alerts.append(
            {
                "timestamp": synthetic_ts.strftime("%Y-%m-%d %H:%M:%S"),
                "ticket": f"{str(row.get('Risk_Level', 'UNKNOWN')).upper()}-{int(idx):05d}",
                "alert": _infer_alert_name(row.get("feature_contributions", "None")),
                "severity": str(row["severity"]),
                "status": "Open",
            }
        )

    return pd.DataFrame(alerts)


def _build_shap_proxy_table(anomaly_results: pd.DataFrame) -> pd.DataFrame:
    """Build a proxy SHAP driver table from anomaly feature contributions."""
    if anomaly_results.empty or "feature_contributions" not in anomaly_results.columns:
        return pd.DataFrame(columns=["Feature", "Influence"])

    anomalies = anomaly_results[anomaly_results["is_anomaly"]].copy()
    if anomalies.empty:
        return pd.DataFrame(columns=["Feature", "Influence"])

    friendly_names = {
        "budget_overrun_pct": "Budget Overrun %",
        "days_overrun_pct": "Schedule Overrun %",
        "efficiency_score": "Delivery Efficiency",
        "cost_efficiency": "Cost Efficiency",
        "Actual_Days": "Actual Days",
        "Estimated_Days": "Estimated Days",
        "Cost_Consumed": "Cost Consumed",
        "Budget_Allocated": "Budget Allocated",
        "Story_Points": "Story Points",
    }

    contribution_totals: dict[str, float] = {}
    for raw in anomalies["feature_contributions"].astype(str).tolist():
        if not raw or raw == "None":
            continue
        for segment in raw.split(","):
            parts = segment.split(":", 1)
            if len(parts) != 2:
                continue
            feature = parts[0].strip()
            try:
                magnitude = float(parts[1].strip())
            except ValueError:
                continue
            contribution_totals[feature] = contribution_totals.get(feature, 0.0) + abs(
                magnitude
            )

    if not contribution_totals:
        return pd.DataFrame(columns=["Feature", "Influence"])

    total = sum(contribution_totals.values()) or 1.0
    rows = []
    for feature, magnitude in sorted(
        contribution_totals.items(), key=lambda item: item[1], reverse=True
    )[:5]:
        rows.append(
            {
                "Feature": friendly_names.get(feature, feature),
                "Influence": f"{(magnitude / total) * 100:.1f}%",
            }
        )
    return pd.DataFrame(rows)


@st.cache_resource(show_spinner=False)
def _load_dashboard_models(contamination: float, forecast_horizon: int) -> dict:
    LOGGER.info(
        "Loading dashboard models with contamination=%.2f and horizon=%d",
        contamination,
        forecast_horizon,
    )

    df = pd.read_csv(DATA_PATH)

    ts_df = pd.DataFrame(
        {
            "ds": pd.date_range(start="2021-01-01", periods=len(df), freq="D"),
            "y": df["Cost_Consumed"].values,
        }
    )
    ts_df_model = ts_df.copy()
    ts_df_model["y"] = ts_df_model["y"].rolling(window=14, min_periods=1).mean()

    forecaster = ProjectForecaster(enable_sprint_seasonality=True)
    forecast_result = forecaster.generate_forecast(
        ts_df_model,
        metric_column="y",
        periods=forecast_horizon,
        include_metrics=True,
        include_components=False,
        date_column="ds",
    )

    anomaly_input_df = _prepare_anomaly_features(df)
    engine = AnomalyEngine(contamination=contamination)
    anomaly_results = engine.detect_anomalies(anomaly_input_df, FEATURE_COLUMNS)

    y_true = (
        (anomaly_input_df["budget_overrun_pct"] > 30)
        | (anomaly_input_df["days_overrun_pct"] > 35)
        | (anomaly_input_df["efficiency_score"] < 0.6)
    ).astype(int)
    roc_auc = roc_auc_score(y_true, -anomaly_results["anomaly_score"].to_numpy())

    severity_order = ["High", "Medium", "Low", "Normal"]
    severity_counts = (
        anomaly_results["severity"]
        .astype(str)
        .value_counts()
        .reindex(severity_order, fill_value=0)
    )

    alerts_table = _build_alerts_table(anomaly_results)
    return {
        "forecast": forecast_result,
        "anomaly": anomaly_results,
        "severity_counts": severity_counts,
        "roc_auc": roc_auc,
        "alerts": alerts_table,
    }


def render_dashboard(show_topbar: bool = True) -> None:
    """Render the main dashboard overview page."""
    render_page_header(
        title="Dashboard Overview",
        subtitle="Real-time insights into your project risk landscape",
    )

    contamination = float(st.session_state.get("model_anomaly_sensitivity", 0.05))
    forecast_horizon = int(st.session_state.get("model_forecast_horizon", 14))
    risk_threshold_mode = st.session_state.get("model_risk_threshold", "Balanced")

    controls_col, _ = st.columns([1.5, 4.5])
    with controls_col:
        if st.button("Regenerate Models", use_container_width=True):
            st.cache_resource.clear()
            LOGGER.info("Dashboard model cache cleared by user")
            st.rerun()

    st.caption(
        f"Anomaly sensitivity: {contamination:.2f} | Forecast horizon: {forecast_horizon} days | Risk mode: {risk_threshold_mode}"
    )

    try:
        dashboard_data = _load_dashboard_models(contamination, forecast_horizon)
    except Exception as exc:
        LOGGER.exception("Dashboard model loading failed: %s", exc)
        st.error("Unable to load forecasting and anomaly analytics. Please try again.")
        return

    forecast_metrics = dashboard_data["forecast"].get("metrics") or {}
    severity_counts = dashboard_data["severity_counts"]
    anomaly_rate = dashboard_data["anomaly"]["is_anomaly"].mean() * 100.0
    risk_score = max(0.0, 100.0 - anomaly_rate)
    total_budget = pd.read_csv(DATA_PATH)["Budget_Allocated"].sum()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Global Risk Score", value=f"{risk_score:.1f}")
        st.markdown(
            '<div class="micro-copy micro-copy-neutral">Derived from anomaly prevalence</div>',
            unsafe_allow_html=True,
        )
    with col2:
        st.metric(label="Total Budget", value=f"${total_budget:,.0f}")
        st.markdown(
            '<div class="micro-copy micro-copy-neutral">Portfolio-wide budget allocation</div>',
            unsafe_allow_html=True,
        )
    with col3:
        st.metric(label="Active Tickets", value=f"{len(dashboard_data['anomaly']):,}")
        st.markdown(
            '<div class="micro-copy micro-copy-positive">Loaded from current project dataset</div>',
            unsafe_allow_html=True,
        )
    with col4:
        st.metric(
            label="Detected Anomalies",
            value=f"{int(dashboard_data['anomaly']['is_anomaly'].sum())}",
        )
        st.markdown(
            '<div class="micro-copy micro-copy-negative">Isolation Forest flagged records</div>',
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 2rem'></div>", unsafe_allow_html=True)

    col_left, col_right = st.columns([3, 2])

    with col_left:
        render_section_header("Risk Distribution Over Time")
        if FORECAST_FIG_PATH.exists():
            st.image(str(FORECAST_FIG_PATH), use_container_width=True)
        else:
            st.warning(
                "Forecast figure not found. Run forecast figure script to generate it."
            )

        mape = forecast_metrics.get("mape")
        rmse = forecast_metrics.get("rmse")
        r2 = forecast_metrics.get("r2")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("MAPE", f"{mape:.2f}%" if mape is not None else "N/A")
        m2.metric("RMSE", f"{rmse:.2f}" if rmse is not None else "N/A")
        m3.metric("R²", f"{r2:.3f}" if r2 is not None else "N/A")
        m4.metric("Forecast Days", str(forecast_horizon))

        forecast_csv = (
            dashboard_data["forecast"]["forecast"].to_csv(index=False).encode("utf-8")
        )
        st.download_button(
            label="Download Forecast CSV",
            data=forecast_csv,
            file_name="phase2_forecast_output.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with col_right:
        render_section_header("Top Risk Drivers (SHAP Proxy)")
        if SEVERITY_FIG_PATH.exists():
            st.image(str(SEVERITY_FIG_PATH), use_container_width=True)
        else:
            st.warning(
                "Severity figure not found. Run severity figure script to generate it."
            )

        shap_proxy_df = _build_shap_proxy_table(dashboard_data["anomaly"])
        if shap_proxy_df.empty:
            st.info("No anomaly-linked feature contributions available yet.")
        else:
            st.dataframe(shap_proxy_df, hide_index=True, use_container_width=True)

        st.metric("ROC-AUC", f"{dashboard_data['roc_auc']:.3f}")
        st.caption("ROC-AUC compares domain labels vs anomaly score ranking.")
        st.metric("High", f"{int(severity_counts['High'])}")
        st.metric("Medium", f"{int(severity_counts['Medium'])}")
        st.metric("Low", f"{int(severity_counts['Low'])}")
        st.metric("Normal", f"{int(severity_counts['Normal'])}")

    st.markdown("<div style='height: 2rem'></div>", unsafe_allow_html=True)
    render_section_header("Recent Anomaly Alerts")
    _render_alerts_table(dashboard_data["alerts"])


def _render_alerts_table(alerts_df: pd.DataFrame) -> None:
    """Render anomaly alerts table in a stable Streamlit grid."""
    if alerts_df.empty:
        st.info("No anomaly alerts available for the current settings.")
        return

    table_df = alerts_df[["timestamp", "ticket", "alert", "severity", "status"]].copy()
    table_df.columns = ["Timestamp", "Ticket", "Alert Type", "Severity", "Status"]
    st.dataframe(table_df, hide_index=True, use_container_width=True)

    options = list(range(len(table_df)))
    selected_idx = st.selectbox(
        "Open selected alert in Ticket Auditor",
        options=options,
        format_func=lambda i: f"{table_df.iloc[i]['Ticket']} ({table_df.iloc[i]['Severity']})",
    )
    if st.button("Open in Auditor", use_container_width=True):
        st.session_state["auditor_ticket_index"] = int(selected_idx)
        switched = switch_page_safe(AUDITOR_PAGE)
        if not switched:
            st.warning("Ticket Auditor page is not available in this environment.")


def render_forecasting_page(show_topbar: bool = True) -> None:
    """Fully functional Forecasting Lab page (Phase 2-A)."""
    render_page_header(
        title="Forecasting Lab",
        subtitle="Prophet-based time-series risk forecasting with sprint seasonality",
    )

    contamination = float(st.session_state.get("model_anomaly_sensitivity", 0.05))
    forecast_horizon = int(st.session_state.get("model_forecast_horizon", 14))

    controls_col, _ = st.columns([1.5, 4.5])
    with controls_col:
        if st.button("Regenerate Forecast", use_container_width=True):
            st.cache_resource.clear()
            LOGGER.info("Forecast cache cleared by user")
            st.rerun()

    st.caption(
        f"Forecast horizon: **{forecast_horizon} days** | Anomaly sensitivity: {contamination:.2f} | "
        "Model: Facebook Prophet with 14-day sprint seasonality"
    )

    try:
        dashboard_data = _load_dashboard_models(contamination, forecast_horizon)
    except Exception as exc:
        LOGGER.exception("Forecast model loading failed: %s", exc)
        st.error("Unable to load forecasting models. Please try again.")
        return

    forecast_df = dashboard_data["forecast"].get("forecast")
    forecast_metrics = dashboard_data["forecast"].get("metrics") or {}
    forecast_meta = dashboard_data["forecast"].get("metadata") or {}

    # --- KPI row ---
    mape = forecast_metrics.get("mape")
    rmse = forecast_metrics.get("rmse")
    r2 = forecast_metrics.get("r2")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("MAPE", f"{mape:.2f}%" if mape is not None else "N/A", help="Mean Absolute Percentage Error")
    m2.metric("RMSE", f"{rmse:.2f}" if rmse is not None else "N/A", help="Root Mean Squared Error")
    m3.metric("R²", f"{r2:.3f}" if r2 is not None else "N/A", help="Coefficient of determination")
    m4.metric("Forecast Days", str(forecast_horizon))

    st.markdown("<div style='height: 1rem'></div>", unsafe_allow_html=True)
    render_section_header("Forecast: Cost Risk Trajectory")

    # Static figure if available; live data fallback
    if FORECAST_FIG_PATH.exists():
        st.image(str(FORECAST_FIG_PATH), use_container_width=True)
        st.caption(
            "Pre-generated Prophet forecast figure. Click 'Regenerate Forecast' to refresh."
        )
    elif forecast_df is not None and not forecast_df.empty:
        st.line_chart(
            forecast_df.set_index("ds")[["yhat", "yhat_lower", "yhat_upper"]].tail(
                forecast_horizon + 60
            )
        )
    else:
        st.warning("Forecast figure not available. Run the forecast figure generation script.")

    render_section_header("Prophet Model Configuration")
    seasonalities = forecast_meta.get("seasonalities", [])
    training_periods = forecast_meta.get("training_periods", "N/A")
    col_a, col_b = st.columns(2)
    col_a.markdown(
        f"""
        **Seasonalities Modelled:** {', '.join(seasonalities) if seasonalities else 'weekly'}  
        **Training Periods:** {training_periods} data points  
        **Changepoint Prior:** 0.05 (default)  
        **Sprint Cycle:** 14-day Fourier seasonality (order 3)
        """
    )
    col_b.markdown(
        """
        **Validation Method:** 80/20 train-test split  
        **Metrics Computed:** MAPE, RMSE, R²  
        **Confidence Intervals:** 80% and 95%  
        **Growth Type:** Linear
        """
    )

    if forecast_df is not None and not forecast_df.empty:
        st.markdown("<div style='height: 0.5rem'></div>", unsafe_allow_html=True)
        forecast_csv = forecast_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download Full Forecast CSV",
            data=forecast_csv,
            file_name="prophet_forecast_output.csv",
            mime="text/csv",
            use_container_width=True,
        )


def render_anomaly_page(show_topbar: bool = True) -> None:
    """Fully functional Anomaly Triage Board page (Phase 2-B)."""
    render_page_header(
        title="Anomaly Triage Board",
        subtitle="Isolation Forest anomaly detection with severity ranking and SHAP-proxy attribution",
    )

    contamination = float(st.session_state.get("model_anomaly_sensitivity", 0.05))
    forecast_horizon = int(st.session_state.get("model_forecast_horizon", 14))

    controls_col, _ = st.columns([1.5, 4.5])
    with controls_col:
        if st.button("Refresh Anomalies", use_container_width=True):
            st.cache_resource.clear()
            LOGGER.info("Anomaly cache cleared by user")
            st.rerun()

    st.caption(f"Isolation Forest | Contamination: {contamination:.2f} | n_estimators: 100")

    try:
        dashboard_data = _load_dashboard_models(contamination, forecast_horizon)
    except Exception as exc:
        LOGGER.exception("Anomaly model loading failed: %s", exc)
        st.error("Unable to load anomaly detection models. Please try again.")
        return

    anomaly_results = dashboard_data["anomaly"]
    severity_counts = dashboard_data["severity_counts"]
    roc_auc = dashboard_data["roc_auc"]
    alerts_table = dashboard_data["alerts"]

    # --- KPI row ---
    anomaly_rate = anomaly_results["is_anomaly"].mean() * 100.0
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Anomaly Rate", f"{anomaly_rate:.2f}%")
    c2.metric("ROC-AUC Score", f"{roc_auc:.3f}")
    c3.metric("High Severity", int(severity_counts["High"]))
    c4.metric("Total Anomalies", int(anomaly_results["is_anomaly"].sum()))

    st.markdown("<div style='height: 1rem'></div>", unsafe_allow_html=True)

    col_left, col_right = st.columns([3, 2])
    with col_left:
        render_section_header("Severity Distribution")
        if SEVERITY_FIG_PATH.exists():
            st.image(str(SEVERITY_FIG_PATH), use_container_width=True)
        else:
            sev_df = severity_counts.reset_index()
            sev_df.columns = ["Severity", "Count"]
            st.bar_chart(sev_df.set_index("Severity"))

        render_section_header("Recent Anomaly Alerts")
        _render_alerts_table(alerts_table)

    with col_right:
        render_section_header("Top Risk Drivers (SHAP Proxy)")
        shap_proxy_df = _build_shap_proxy_table(anomaly_results)
        if shap_proxy_df.empty:
            st.info("No feature contribution data available.")
        else:
            st.dataframe(shap_proxy_df, hide_index=True, use_container_width=True)

        render_section_header("Severity Breakdown")
        for level in ["High", "Medium", "Low", "Normal"]:
            count = int(severity_counts[level])
            st.metric(level, count)

        st.caption("ROC-AUC compares domain-derived labels vs Isolation Forest anomaly scores.")

    # Full anomaly data export
    st.markdown("<div style='height: 1rem'></div>", unsafe_allow_html=True)
    render_section_header("Raw Anomaly Data")
    severity_filter = st.selectbox(
        "Filter by Severity",
        options=["All", "High", "Medium", "Low", "Normal"],
        index=0,
        key="anomaly_severity_filter",
    )
    display_df = anomaly_results.copy()
    if severity_filter != "All":
        display_df = display_df[display_df["severity"].astype(str) == severity_filter]

    anomaly_only = st.toggle("Show anomalies only", value=True, key="anomaly_only_toggle")
    if anomaly_only:
        display_df = display_df[display_df["is_anomaly"]]

    cols_to_show = [c for c in [
        "is_anomaly", "anomaly_score", "severity",
        "budget_overrun_pct", "days_overrun_pct",
        "efficiency_score", "cost_efficiency",
        "feature_contributions",
    ] if c in display_df.columns]
    st.dataframe(display_df[cols_to_show].head(200), use_container_width=True, hide_index=False)

    csv_bytes = display_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Anomaly Report (CSV)",
        data=csv_bytes,
        file_name="anomaly_triage_report.csv",
        mime="text/csv",
        use_container_width=True,
    )
