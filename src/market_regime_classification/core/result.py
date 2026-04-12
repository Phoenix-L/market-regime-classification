"""Standardized result container for detector runs."""

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(slots=True)
class DetectionResult:
    """Detector output contract for comparison-friendly research workflows.

    The ``bars`` payload is intentionally generic (table-like) because the exact
    upstream/downstream stack may differ by project (e.g., pandas/polars).
    """

    detector_name: str
    detector_version: str
    config_snapshot: Mapping[str, Any] = field(default_factory=dict)
    bars: Any = None
    summary: Mapping[str, Any] = field(default_factory=dict)
    artifacts: Mapping[str, Any] = field(default_factory=dict)
