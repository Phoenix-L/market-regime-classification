import copy
from datetime import datetime, timedelta, timezone

import pytest

from market_regime_classification.core.exceptions import DetectorContractError
from market_regime_classification.detectors.wilder_style.detector import WilderStyleDetector


def _bars_from_close(closes: list[float], *, symbol: str = "SPY") -> list[dict[str, float | str]]:
    bars = []
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    for i, c in enumerate(closes):
        bars.append(
            {
                "symbol": symbol,
                "timestamp": (start + timedelta(days=i)).isoformat(),
                "open": c,
                "high": c + 1.0,
                "low": c - 1.0,
                "close": c,
                "volume": 1000.0,
            }
        )
    return bars


def test_wilder_detector_is_deterministic_for_identical_input() -> None:
    closes = [100 + i * 0.8 for i in range(40)]
    bars = _bars_from_close(closes)

    detector = WilderStyleDetector()
    r1 = detector.run(copy.deepcopy(bars)).to_dict()
    r2 = detector.run(copy.deepcopy(bars)).to_dict()

    assert r1 == r2


def test_wilder_detector_trending_sequence_produces_trending_labels() -> None:
    closes = [100 + i * 1.5 for i in range(50)]
    result = WilderStyleDetector().run(
        _bars_from_close(closes),
        config={
            "wilder_length": 5,
            "trend_confirm_bars": 2,
            "osc_confirm_bars": 2,
            "transition_trigger_count": 2,
        },
    )

    finals = [row["regime_final"] for row in result.bars[-10:]]
    assert finals.count("trending") >= 6
    assert result.bars[-1]["regime_direction"] == "up"


def test_wilder_detector_oscillating_sequence_produces_oscillating_labels() -> None:
    closes = [100 + (1 if i % 2 == 0 else -1) * 1.8 for i in range(60)]
    result = WilderStyleDetector().run(
        _bars_from_close(closes),
        config={
            "wilder_length": 5,
            "trend_confirm_bars": 2,
            "osc_confirm_bars": 2,
            "transition_trigger_count": 2,
            "recent_cross_window": 4,
            "recent_cross_osc_min": 1,
            "adx_osc_enter": 25.0,
            "di_gap_osc_max": 6.0,
        },
    )

    finals = [row["regime_final"] for row in result.bars]
    assert finals.count("oscillating") >= 5


def test_wilder_detector_transition_state_appears_on_regime_handoff() -> None:
    closes = [100 + (1 if i % 2 == 0 else -1) * 1.4 for i in range(20)] + [100 + i * 1.2 for i in range(20)]
    result = WilderStyleDetector().run(
        _bars_from_close(closes),
        config={
            "wilder_length": 4,
            "trend_confirm_bars": 2,
            "osc_confirm_bars": 2,
            "transition_trigger_count": 2,
            "recent_cross_window": 4,
            "recent_cross_osc_min": 1,
            "adx_osc_enter": 24.0,
            "di_gap_osc_max": 6.0,
        },
    )

    reasons = [row.get("transition_reason") for row in result.bars]
    assert "transition_bridge" in reasons or "enter_transition" in reasons


def test_wilder_required_output_fields_present_and_state_age_positive() -> None:
    result = WilderStyleDetector().run(_bars_from_close([100 + i * 0.6 for i in range(30)]))
    required = {"regime_raw", "regime_final", "regime_direction", "state_age"}

    for row in result.bars:
        assert required.issubset(row.keys())
        assert row["regime_raw"] is not None
        assert row["regime_final"] is not None
        assert row["regime_direction"] is not None
        assert isinstance(row["state_age"], int)
        assert row["state_age"] >= 1


def test_wilder_intermediate_fields_are_consistently_named_and_numeric_or_none() -> None:
    result = WilderStyleDetector().run(_bars_from_close([100 + i * 0.7 for i in range(35)]), config={"wilder_length": 5})

    for row in result.bars:
        assert "adx" in row and "di_plus" in row and "di_minus" in row
        assert row["adx"] is None or isinstance(row["adx"], float)
        assert row["di_plus"] is None or isinstance(row["di_plus"], float)
        assert row["di_minus"] is None or isinstance(row["di_minus"], float)


def test_wilder_warmup_behavior_for_short_series_is_explicit() -> None:
    result = WilderStyleDetector().run(_bars_from_close([100, 101, 102]), config={"wilder_length": 5})

    assert all(row["adx"] is None for row in result.bars)
    assert all(row["regime_raw"] in {"oscillating", "transition", "trending"} for row in result.bars)
    assert all(row["regime_final"] in {"oscillating", "transition", "trending"} for row in result.bars)


def test_wilder_rejects_nan_inputs_via_input_contract() -> None:
    bars = _bars_from_close([100, 101, 102, 103, 104])
    bars[3]["close"] = float("nan")

    with pytest.raises(DetectorContractError, match="finite numeric"):
        WilderStyleDetector().run(bars)
