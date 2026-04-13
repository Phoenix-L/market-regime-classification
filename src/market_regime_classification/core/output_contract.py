"""Detector output contract helpers."""

from typing import Any

from .exceptions import DetectorContractError

REQUIRED_OUTPUT_COLUMNS: tuple[str, ...] = (
    "regime_raw",
    "regime_final",
    "regime_direction",
    "state_age",
)
OPTIONAL_OUTPUT_COLUMNS: tuple[str, ...] = (
    "transition_reason",
    "confidence",
)


def validate_detector_output_v1(rows: Any) -> list[dict[str, Any]]:
    """Validate detector rows against Output Contract v1."""
    if not isinstance(rows, list):
        raise DetectorContractError("detector output bars must be list[dict]")
    if not rows:
        raise DetectorContractError("detector output bars must be non-empty")

    normalized: list[dict[str, Any]] = []
    for i, row in enumerate(rows):
        if not isinstance(row, dict):
            raise DetectorContractError(f"output row {i} must be dict")
        missing = [c for c in REQUIRED_OUTPUT_COLUMNS if c not in row]
        if missing:
            raise DetectorContractError(f"output row {i} missing required columns: {missing}")
        normalized.append(row)
    return normalized
