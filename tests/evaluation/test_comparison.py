from market_regime_classification.evaluation.comparison import compare_detector_outputs


def _rows(offset: float) -> list[dict[str, str | float]]:
    closes = [100 + offset, 101 + offset, 102 + offset, 101 + offset, 100 + offset, 99 + offset]
    states = ["oscillating", "transition", "trending", "trending", "transition", "oscillating"]
    directions = ["none", "none", "up", "up", "none", "none"]
    return [{"close": c, "regime_final": s, "regime_direction": d} for c, s, d in zip(closes, states, directions)]


def test_compare_detector_outputs_scaffold() -> None:
    report = compare_detector_outputs({"det_a": _rows(0.0), "det_b": _rows(1.0)}, horizons=(1, 3))
    assert report["horizons"] == [1, 3]
    assert "det_a" in report["detectors"]
    assert "regime_stats" in report["detectors"]["det_a"]
    assert "forward_behavior" in report["detectors"]["det_a"]
