"""
Test script for AnomalyEngine module
This script validates the implementation of the AnomalyEngine class
"""

import pandas as pd
import numpy as np
import os
from src.anomaly import AnomalyEngine


def test_anomaly_engine():
    """Test the AnomalyEngine implementation"""
    print("[INFO] Testing AnomalyEngine implementation")

    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)

    # Generate synthetic test data
    np.random.seed(42)
    n_samples = 1000

    # Generate normal data
    data = {
        "burn_rate": np.random.normal(1.2, 0.3, n_samples),
        "velocity_delta": np.random.normal(0, 0.5, n_samples),
        "schedule_variance": np.random.normal(0, 2, n_samples),
        "scope_creep_rate": np.random.normal(0.1, 0.05, n_samples),
        "blocker_count": np.random.poisson(0.5, n_samples).astype(float),
        "comment_sentiment": np.random.normal(0.1, 0.3, n_samples).astype(float),
    }

    # Inject some anomalies
    anomaly_indices = np.random.choice(
        n_samples, size=int(n_samples * 0.05), replace=False
    )
    for idx in anomaly_indices:
        data["burn_rate"][idx] = np.random.normal(4, 0.5)  # High burn rate anomaly

    # Create DataFrame
    df = pd.DataFrame(data)
    print(f"[INFO] Generated {len(df)} test records")

    # Test AnomalyEngine
    engine = AnomalyEngine(contamination=0.05)

    # Test with PRD specified features
    feature_columns = [
        "burn_rate",
        "velocity_delta",
        "schedule_variance",
        "scope_creep_rate",
        "blocker_count",
        "comment_sentiment",
    ]

    print("[INFO] Running anomaly detection...")
    results = engine.detect_anomalies(
        data=df, feature_columns=feature_columns, contamination=0.05
    )

    print("[PASS] Anomaly detection completed successfully")
    print(f"[INFO] Detected {sum(results['is_anomaly'])} anomalies")

    # Show some results
    anomalies = results[results["is_anomaly"]]
    if len(anomalies) > 0:
        print("[INFO] Sample anomalies:")
        for idx, row in anomalies.head().iterrows():
            print(
                f"  - Anomaly with score {row['anomaly_score']:.3f}, severity: {row['severity']}"
            )
            print(f"    Contributions: {row['feature_contributions']}")

    # Save model
    print("[INFO] Saving model...")
    engine.save_model("models/isolation_forest.pkl")
    print("[PASS] Model saved successfully")

    # Validate output schema
    required_columns = [
        "is_anomaly",
        "anomaly_score",
        "severity",
        "feature_contributions",
    ]
    for col in required_columns:
        if col not in results.columns:
            raise ValueError(f"Missing required column: {col}")

    print("[PASS] Output schema validation passed")
    print("[INFO] AnomalyEngine test completed successfully")


if __name__ == "__main__":
    test_anomaly_engine()
