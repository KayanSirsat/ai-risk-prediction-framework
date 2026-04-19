"""Unit tests for WhatIfSimulator."""

from __future__ import annotations

from unittest.mock import MagicMock

import numpy as np
import pandas as pd
import pytest

from src.phase2.simulation.what_if_simulator import WhatIfSimulator


pytestmark = pytest.mark.unit


def _build_simulator() -> tuple[WhatIfSimulator, MagicMock, MagicMock]:
    model = MagicMock()
    model.feature_names_in_ = [
        "Budget_Allocated",
        "Estimated_Days",
        "assignee_count",
        "story_points_total",
        "days_overrun_pct",
    ]
    model.classes_ = np.array([0, 1, 2])
    model.predict_proba.side_effect = [
        np.array([[0.10, 0.30, 0.60]]),
        np.array([[0.20, 0.30, 0.50]]),
    ]

    explainer = MagicMock()
    explainer.shap_values.return_value = np.array(
        [
            [
                [0.01, 0.02, 0.03],
                [0.11, 0.12, 0.13],
                [0.21, 0.22, 0.23],
                [0.31, 0.32, 0.33],
                [0.41, 0.42, 0.43],
            ]
        ],
        dtype=float,
    )

    simulator = WhatIfSimulator(model=model, explainer=explainer)
    return simulator, model, explainer


def test_apply_deltas_budget_multiplier_scales_budget_feature() -> None:
    simulator, _, _ = _build_simulator()
    baseline = {
        "Budget_Allocated": 1000.0,
        "assignee_count": 4,
        "story_points_total": 20,
    }

    updated = simulator.apply_deltas(
        baseline_data=baseline,
        deltas={"Budget Multiplier": 1.2},
    )

    assert updated["Budget_Allocated"] == pytest.approx(1200.0)
    assert updated["assignee_count"] == 4
    assert updated["story_points_total"] == 20


def test_apply_deltas_team_size_floor_guard() -> None:
    simulator, _, _ = _build_simulator()
    baseline = {
        "assignee_count": 3,
        "Budget_Allocated": 1000.0,
        "story_points_total": 10,
    }

    updated = simulator.apply_deltas(
        baseline_data=baseline,
        deltas={"team_size_delta": -5},
    )

    assert updated["assignee_count"] == 1.0


def test_simulate_scenario_returns_schema_and_calls_model_and_explainer() -> None:
    simulator, model, explainer = _build_simulator()
    baseline = {
        "Budget_Allocated": 1000.0,
        "Estimated_Days": 10.0,
        "assignee_count": 3.0,
        "story_points_total": 20.0,
        "days_overrun_pct": 5.0,
    }
    deltas = {
        "Budget Multiplier": 1.2,
        "Timeline Extension": 2,
        "team_size_delta": -1,
        "Scope Reduction": 0.25,
        "Risk Buffer": 0.1,
    }

    result = simulator.simulate_scenario(baseline_data=baseline, deltas=deltas)

    assert set(result.keys()) == {
        "original_score",
        "simulated_score",
        "score_delta",
        "new_top_shap_features",
    }
    assert isinstance(result["new_top_shap_features"], list)

    assert model.predict_proba.call_count == 2
    assert explainer.shap_values.call_count == 1

    first_call_df = model.predict_proba.call_args_list[0].args[0]
    second_call_df = model.predict_proba.call_args_list[1].args[0]

    assert isinstance(first_call_df, pd.DataFrame)
    assert isinstance(second_call_df, pd.DataFrame)

    assert second_call_df.loc[0, "Budget_Allocated"] == pytest.approx(1200.0)
    assert second_call_df.loc[0, "days_overrun_pct"] == pytest.approx(7.0)
    assert second_call_df.loc[0, "assignee_count"] == pytest.approx(2.0)
    assert second_call_df.loc[0, "story_points_total"] == pytest.approx(15.0)

    shap_arg = explainer.shap_values.call_args.args[0]
    np.testing.assert_allclose(shap_arg, second_call_df.values)


def test_apply_deltas_raises_if_active_slider_missing_required_feature() -> None:
    simulator, _, _ = _build_simulator()
    baseline = {
        "Estimated_Days": 10.0,
        "assignee_count": 3.0,
        "story_points_total": 20.0,
    }

    with pytest.raises(KeyError):
        simulator.apply_deltas(
            baseline_data=baseline,
            deltas={"Budget Multiplier": 1.2},
        )
