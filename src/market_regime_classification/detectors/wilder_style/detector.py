"""Wilder-style detector implementation."""

from dataclasses import asdict
from typing import Any, Mapping

from ...core.detector_base import BaseRegimeDetector
from ...core.input_contract import validate_detector_input_v1
from ...core.output_contract import validate_detector_output_v1
from ...core.result import DetectionResult
from .classifier import classify_wilder_states
from .config import WilderStyleConfig
from .signals import compute_wilder_signals


class WilderStyleDetector(BaseRegimeDetector):
    """Deterministic DMI/ADX-driven regime detector baseline."""

    name = "wilder_style"
    version = "0.1.0"

    def run(self, data: Any, config: Mapping[str, Any] | None = None) -> DetectionResult:
        rows_in = validate_detector_input_v1(data)

        cfg = WilderStyleConfig(**(config or {}))
        cfg.validate()

        rows = compute_wilder_signals(
            rows_in,
            wilder_length=cfg.wilder_length,
            recent_cross_window=cfg.recent_cross_window,
        )
        rows = classify_wilder_states(rows, cfg)
        validate_detector_output_v1(rows)

        final_counts: dict[str, int] = {"oscillating": 0, "transition": 0, "trending": 0}
        for row in rows:
            final_counts[row["regime_final"]] += 1

        summary = {
            "status": "ok",
            "num_bars": len(rows),
            "final_state_counts": final_counts,
            "notes": "Baseline Wilder-style detector with interpretable thresholds.",
        }

        artifacts = {"schema_version": "wilder_style_result_v1", "table_type": "list_of_dicts"}

        for row in rows:
            row["detector_name"] = self.name
            row["detector_version"] = self.version

        return DetectionResult(
            detector_name=self.name,
            detector_version=self.version,
            config_snapshot=asdict(cfg),
            bars=rows,
            summary=summary,
            artifacts=artifacts,
        )
