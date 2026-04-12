"""Standardized result container for detector runs."""

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping


@dataclass(slots=True)
class DetectionResult:
    """Detector output contract for comparison-friendly research workflows.

    The ``bars`` payload is intentionally generic (table-like) because the exact
    upstream/downstream stack may differ by project (e.g., pandas/polars/lists).
    """

    detector_name: str
    detector_version: str
    config_snapshot: Mapping[str, Any] = field(default_factory=dict)
    bars: Any = None
    summary: Mapping[str, Any] = field(default_factory=dict)
    artifacts: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize result into a plain dictionary for downstream integrations."""
        return asdict(self)
