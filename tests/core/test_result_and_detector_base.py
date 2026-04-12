import pytest

from market_regime_classification.core.detector_base import BaseRegimeDetector
from market_regime_classification.core.result import DetectionResult


class _DummyDetector(BaseRegimeDetector):
    name = "dummy"
    version = "0.0.1"

    def run(self, data, config=None):
        return DetectionResult(
            detector_name=self.name,
            detector_version=self.version,
            config_snapshot=config or {},
            bars=data,
            summary={"ok": True},
            artifacts={},
        )


class _IncompleteDetector(BaseRegimeDetector):
    name = "incomplete"
    version = "0.0.1"


def test_detection_result_fields() -> None:
    result = _DummyDetector().run(data=[1, 2, 3], config={"a": 1})
    assert result.detector_name == "dummy"
    assert result.detector_version == "0.0.1"
    assert result.config_snapshot["a"] == 1
    assert result.summary["ok"] is True


def test_abstract_detector_cannot_instantiate_without_run() -> None:
    with pytest.raises(TypeError):
        _IncompleteDetector()
