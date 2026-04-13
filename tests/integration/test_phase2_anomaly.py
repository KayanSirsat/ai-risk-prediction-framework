import numpy as np
import pandas as pd
import pytest
from sklearn.metrics import roc_auc_score

from src.anomaly.anomaly_detector import AnomalyEngine


def _prepare_features() -> pd.DataFrame:
    df = pd.read_csv("data/ml_ready_data.csv")
    df["budget_overrun_pct"] = (
        (df["Cost_Consumed"] - df["Budget_Allocated"]) / df["Budget_Allocated"] * 100
    )
    df["days_overrun_pct"] = (
        (df["Actual_Days"] - df["Estimated_Days"]) / df["Estimated_Days"] * 100
    )
    df["efficiency_score"] = df["Estimated_Days"] / df["Actual_Days"]
    df["cost_efficiency"] = df["Budget_Allocated"] / df["Cost_Consumed"]

    feature_columns = [
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
    return df[feature_columns].replace([np.inf, -np.inf], np.nan).dropna().copy()


@pytest.mark.integration
def test_phase2_anomaly_detection_outputs() -> None:
    features_df = _prepare_features()
    feature_columns = list(features_df.columns)

    engine = AnomalyEngine(contamination=0.05)
    results = engine.detect_anomalies(features_df, feature_columns)

    assert len(results) == len(features_df)
    assert "is_anomaly" in results.columns
    assert "anomaly_score" in results.columns
    assert "severity" in results.columns
    assert "feature_contributions" in results.columns


@pytest.mark.integration
@pytest.mark.slow
def test_phase2_anomaly_roc_auc_target() -> None:
    features_df = _prepare_features()
    feature_columns = list(features_df.columns)

    y_true = (
        (features_df["budget_overrun_pct"] > 30)
        | (features_df["days_overrun_pct"] > 35)
        | (features_df["efficiency_score"] < 0.6)
    ).astype(int)

    engine = AnomalyEngine(contamination=0.03)
    results = engine.detect_anomalies(features_df, feature_columns)
    anomaly_scores = -results["anomaly_score"].to_numpy()

    roc_auc = roc_auc_score(y_true, anomaly_scores)
    assert roc_auc >= 0.80
