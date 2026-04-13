import sys

from market_regime_classification.core.result import DetectionResult
from market_regime_classification.detectors.wilder_style.detector import WilderStyleDetector


def test_minimal_pipeline_returns_detection_result() -> None:
    bars = [
        {
            "symbol": "SPY",
            "timestamp": f"2026-01-{i+1:02d}T00:00:00+00:00",
            "open": 100 + i,
            "high": 101 + i,
            "low": 99 + i,
            "close": 100.5 + i,
            "volume": 1000,
        }
        for i in range(20)
    ]

    result = WilderStyleDetector().run(bars)

    assert isinstance(result, DetectionResult)
    assert result.detector_name == "wilder_style"
    assert len(result.bars) == len(bars)


def test_minimal_pipeline_does_not_require_visualization_or_evaluation_modules(monkeypatch) -> None:
    monkeypatch.setitem(sys.modules, "market_regime_classification.visualization", None)
    monkeypatch.setitem(sys.modules, "market_regime_classification.evaluation", None)

    bars = [
        {
            "symbol": "SPY",
            "timestamp": f"2026-02-{i+1:02d}T00:00:00+00:00",
            "open": 200 + i,
            "high": 201 + i,
            "low": 199 + i,
            "close": 200.5 + i,
            "volume": 1000,
        }
        for i in range(20)
    ]

    result = WilderStyleDetector().run(bars)
    assert isinstance(result, DetectionResult)
