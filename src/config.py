"""Configuration helpers for environment-based runtime settings."""

from __future__ import annotations

import os
from pathlib import Path


def load_env_file(path: str | None = None) -> None:
    """Load key/value pairs from an .env file into process env."""
    env_path = Path(path) if path else Path(__file__).resolve().parents[1] / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def get_env(key: str, default: str = "") -> str:
    """Get an environment variable with a default."""
    return os.getenv(key, default)


def get_jira_oauth_settings() -> dict[str, str]:
    """Return Jira OAuth settings from environment with sensible defaults."""
    load_env_file()
    return {
        "client_id": get_env("JIRA_OAUTH_CLIENT_ID"),
        "client_secret": get_env("JIRA_OAUTH_CLIENT_SECRET"),
        "redirect_uri": get_env("JIRA_OAUTH_REDIRECT_URI", "http://localhost:8501"),
    }


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class Paths:
    """Canonical project path constants. Single source of truth for all file paths."""

    DATA_DIR: Path = PROJECT_ROOT / "data"
    MODEL_DIR: Path = PROJECT_ROOT / "models"
    LOGS_DIR: Path = PROJECT_ROOT / "logs"
    REPORTS_DIR: Path = PROJECT_ROOT / "reports"
    APP_COMPONENTS_DIR: Path = PROJECT_ROOT / "app" / "components"

    ML_READY_DATA: Path = DATA_DIR / "ml_ready_data.csv"
    RAW_JIRA_DATA: Path = DATA_DIR / "raw_jira_data.csv"
    CURATED_ANOMALIES: Path = DATA_DIR / "curated_anomalies.csv"
    AUTH_DB: Path = DATA_DIR / "auth.db"

    XGB_MODEL: Path = MODEL_DIR / "xgb_model.pkl"
    RF_MODEL: Path = MODEL_DIR / "rf_model.pkl"
    FEATURE_COLUMNS: Path = MODEL_DIR / "feature_columns.pkl"
    ISOLATION_FOREST: Path = MODEL_DIR / "isolation_forest.pkl"

    CONFUSION_MATRIX_IMG: Path = APP_COMPONENTS_DIR / "confusion_matrix.png"
    ROC_CURVE_IMG: Path = APP_COMPONENTS_DIR / "roc_curve.png"
    SHAP_SUMMARY_IMG: Path = APP_COMPONENTS_DIR / "shap_summary.png"

    FORECAST_FIGURE: Path = REPORTS_DIR / "fig_phase2_a_prophet_forecast.png"
    SEVERITY_HISTOGRAM: Path = APP_COMPONENTS_DIR / "severity_breakdown.png"
