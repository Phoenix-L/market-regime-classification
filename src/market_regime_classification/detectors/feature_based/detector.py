"""Feature-based detector scaffold."""

from dataclasses import asdict
from typing import Any, Mapping

from ...core.detector_base import BaseRegimeDetector
from ...core.result import DetectionResult
from .config import FeatureBasedConfig


class FeatureBasedDetector(BaseRegimeDetector):
    """Placeholder detector for planned feature-based regime classification."""

    name = "feature_based"
    version = "0.1.0-placeholder"

    def run(self, data: Any, config: Mapping[str, Any] | None = None) -> DetectionResult:
        cfg = FeatureBasedConfig(**(config or {}))
        return DetectionResult(
            detector_name=self.name,
            detector_version=self.version,
            config_snapshot=asdict(cfg),
            bars=data,
            summary={"status": "placeholder", "note": "Algorithm not yet implemented."},
            artifacts={},
        )
