from market_regime_classification.evaluation.event_study import (
    extract_regime_transition_events,
    run_regime_event_study,
    summarize_forward_behavior,
)


def _synthetic_rows() -> list[dict[str, str | float]]:
    closes = [100, 101, 102, 101, 100, 99, 100, 102, 104, 103, 102, 101]
    states = [
        "oscillating",
        "oscillating",
        "transition",
        "trending",
        "trending",
        "transition",
        "oscillating",
        "transition",
        "trending",
        "trending",
        "transition",
        "oscillating",
    ]
    directions = ["none", "none", "none", "up", "up", "none", "none", "none", "up", "up", "none", "none"]
    return [
        {
            "close": float(c),
            "regime_final": s,
            "regime_direction": d,
        }
        for c, s, d in zip(closes, states, directions)
    ]


def test_forward_behavior_grouping_and_horizon_output() -> None:
    rows = _synthetic_rows()
    summary = summarize_forward_behavior(rows, horizons=(1, 3))

    assert summary["horizons"] == [1, 3]
    assert "trending" in summary["by_horizon"][1]
    assert summary["by_horizon"][1]["trending"]["count"] > 0


def test_event_extraction_and_event_study_alignment() -> None:
    rows = _synthetic_rows()
    events = extract_regime_transition_events(rows, to_state="transition")
    assert len(events) >= 1

    study = run_regime_event_study(rows, pre_window=2, post_window=3)
    assert study["num_events"] >= 1
    assert 0 in study["aligned_return_summary"]
    assert "continuation_probability_trending" in study
