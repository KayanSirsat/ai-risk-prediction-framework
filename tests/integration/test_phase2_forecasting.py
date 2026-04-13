import pandas as pd
import pytest

from src.forecasting.forecast import ProjectForecaster


@pytest.mark.integration
@pytest.mark.slow
def test_phase2_forecasting_mape_target() -> None:
    data_path = "data/ml_ready_data.csv"
    df = pd.read_csv(data_path)

    ts_df = pd.DataFrame(
        {
            "ds": pd.date_range(start="2021-01-01", periods=len(df), freq="D"),
            "y": df["Cost_Consumed"].values,
        }
    )
    ts_df["y"] = ts_df["y"].rolling(window=14, min_periods=1).mean()

    forecaster = ProjectForecaster(enable_sprint_seasonality=True)
    result = forecaster.generate_forecast(
        ts_df,
        metric_column="y",
        periods=30,
        include_metrics=True,
        include_components=True,
        date_column="ds",
    )

    metrics = result["metrics"]
    forecast_df = result["forecast"]

    assert metrics is not None
    assert metrics["mape"] is not None
    assert metrics["mape"] <= 15.0
    assert len(forecast_df) == len(ts_df) + 30
    assert {"ds", "yhat", "yhat_lower", "yhat_upper"}.issubset(forecast_df.columns)
