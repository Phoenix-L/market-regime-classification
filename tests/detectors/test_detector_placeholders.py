from market_regime_classification.detectors.feature_based.detector import FeatureBasedDetector
from market_regime_classification.detectors.wilder_style.detector import WilderStyleDetector


def _sample_bars() -> list[dict[str, float | str]]:
    closes = [100, 101, 102, 104, 105, 104, 103, 102, 101, 100, 99, 98, 99, 100, 101]
    bars = []
    for i, c in enumerate(closes):
        bars.append(
            {
                "symbol": "SPY",
                "timestamp": f"2026-01-{i+1:02d}T00:00:00+00:00",
                "open": c - 0.2,
                "high": c + 0.8,
                "low": c - 0.8,
                "close": c,
                "volume": 1000,
            }
        )
    return bars


def test_wilder_detector_result_structure_and_columns() -> None:
    result = WilderStyleDetector().run(data=_sample_bars())

    assert result.detector_name == "wilder_style"
    assert result.summary["status"] == "ok"
    assert result.summary["num_bars"] == len(_sample_bars())
    assert len(result.bars) == len(_sample_bars())

    expected_columns = {
        "tr",
        "dm_plus",
        "dm_minus",
        "atr_wilder",
        "di_plus",
        "di_minus",
        "dx",
        "adx",
        "adx_slope",
        "di_gap",
        "di_dominant_side",
        "di_dominance_run",
        "di_cross",
        "recent_di_cross_count",
        "regime_raw",
        "regime_final",
        "regime_direction",
        "transition_reason",
        "state_age",
        "detector_name",
        "detector_version",
    }
    assert expected_columns.issubset(result.bars[-1].keys())


def test_feature_based_placeholder_result() -> None:
    data = [{"symbol": "SPY", "timestamp": "2026-01-01T00:00:00+00:00", "open": 1, "high": 1, "low": 1, "close": 1, "volume": 1}]
    result = FeatureBasedDetector().run(data=data)
    assert result.detector_name == "feature_based"
    assert result.bars[0]["regime_final"] == "transition"
    assert result.bars[0]["regime_raw"] == "transition"
    for col in ("regime_raw", "regime_final", "regime_direction", "state_age"):
        assert col in result.bars[0]
    assert result.summary["status"] == "placeholder"
