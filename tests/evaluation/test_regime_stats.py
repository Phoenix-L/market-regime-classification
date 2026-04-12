from market_regime_classification.evaluation.regime_stats import (
    segment_state_runs,
    summarize_regime_durations,
)


def _rows(states: list[str]) -> list[dict[str, str | float]]:
    return [
        {
            "close": float(100 + i),
            "regime_final": state,
            "regime_direction": "none",
        }
        for i, state in enumerate(states)
    ]


def test_segment_state_runs_on_controlled_sequence() -> None:
    rows = _rows(["oscillating", "oscillating", "transition", "trending", "trending", "transition"])
    runs = segment_state_runs(rows)
    assert [r["state"] for r in runs] == ["oscillating", "transition", "trending", "transition"]
    assert [r["length"] for r in runs] == [2, 1, 2, 1]


def test_regime_duration_summary_and_transition_matrix() -> None:
    rows = _rows(["oscillating", "oscillating", "transition", "trending", "trending", "transition"])
    summary = summarize_regime_durations(rows, short_run_threshold=1)

    assert summary["bar_count_by_regime"]["oscillating"] == 2
    assert summary["duration_summary_by_regime"]["trending"]["max"] == 2
    assert summary["transition_counts"]["oscillating->transition"] == 1
    assert summary["transition_matrix"]["transition"]["trending"] == 1
    assert summary["short_lived_run_count"] == 2
