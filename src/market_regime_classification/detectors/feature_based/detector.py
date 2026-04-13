"""Feature-based detector scaffold."""

from dataclasses import asdict
from typing import Any, Mapping

from ...core.detector_base import BaseRegimeDetector
from ...core.input_contract import validate_detector_input_v1
from ...core.output_contract import validate_detector_output_v1
from ...core.result import DetectionResult
from .config import FeatureBasedConfig


class FeatureBasedDetector(BaseRegimeDetector):
    """Placeholder detector for planned feature-based regime classification."""

    name = "feature_based"
    version = "0.1.0-placeholder"

    def run(self, data: Any, config: Mapping[str, Any] | None = None) -> DetectionResult:
        rows_in = validate_detector_input_v1(data)
        cfg = FeatureBasedConfig(**(config or {}))

        rows = []
        for row in rows_in:
            out = dict(row)
            out.update(
                {
                    "regime_raw": "transition",
                    "regime_final": "transition",
                    "regime_direction": "none",
                    "state_age": 1,
                    "transition_reason": "placeholder",
                    "confidence": None,
                }
            )
            rows.append(out)

        validate_detector_output_v1(rows)

        return DetectionResult(
            detector_name=self.name,
            detector_version=self.version,
            config_snapshot=asdict(cfg),
            bars=rows,
            summary={"status": "placeholder", "note": "Algorithm not yet implemented."},
            artifacts={"schema_version": "detector_output_v1", "table_type": "list_of_dicts"},
        )
