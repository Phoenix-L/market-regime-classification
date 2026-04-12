from market_regime_classification.detectors.feature_based.detector import FeatureBasedDetector
from market_regime_classification.detectors.wilder_style.detector import WilderStyleDetector


def test_wilder_placeholder_result() -> None:
    data = [{"ts": "2026-01-01", "open": 1, "high": 1, "low": 1, "close": 1, "volume": 1}]
    result = WilderStyleDetector().run(data=data)
    assert result.detector_name == "wilder_style"
    assert result.bars == data
    assert result.summary["status"] == "placeholder"


def test_feature_based_placeholder_result() -> None:
    data = [{"ts": "2026-01-01", "open": 1, "high": 1, "low": 1, "close": 1, "volume": 1}]
    result = FeatureBasedDetector().run(data=data)
    assert result.detector_name == "feature_based"
    assert result.bars == data
    assert result.summary["status"] == "placeholder"
