"""Dashboard View for live forecasting and anomaly analytics."""

import logging
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
from sklearn.metrics import roc_auc_score

from app.utils.styles import COLORS, render_page_header, render_section_header
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


def render_forecasting_page(show_topbar: bool = True) -> None:
    """Backward-compatible forecasting page entrypoint."""
    if show_topbar:
        st.caption("Forecasting page header is rendered by the calling page.")
    st.info(
        "Forecasting view is transitioning to the new Phase 2 layout. "
        "Use Dashboard for full live forecasting metrics right now."
    )


def render_anomaly_page(show_topbar: bool = True) -> None:
    """Backward-compatible anomaly page entrypoint."""
    if show_topbar:
        st.caption("Anomaly page header is rendered by the calling page.")
    st.info(
        "Anomaly triage board is transitioning to the new Phase 2 layout. "
        "Use Dashboard for current anomaly detection outputs right now."
    )
