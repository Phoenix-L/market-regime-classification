"""Minimal comparison-ready evaluation scaffold."""

from typing import Any

from .event_study import summarize_forward_behavior
from .regime_stats import summarize_regime_durations


def compare_detector_outputs(
    detector_bars: dict[str, list[dict[str, Any]]], *, horizons: tuple[int, ...] = (1, 3, 5, 10)
) -> dict[str, Any]:
    """Build baseline comparable summaries per detector.

    This is intentionally lightweight for Phase 4 and avoids full ranking logic.
    """
    if not detector_bars:
        raise ValueError("detector_bars cannot be empty")

    per_detector: dict[str, Any] = {}
    for name in sorted(detector_bars):
        bars = detector_bars[name]
        if not isinstance(bars, list) or not bars:
            raise ValueError(f"detector '{name}' must provide non-empty list[dict] bars")
        per_detector[name] = {
            "regime_stats": summarize_regime_durations(bars),
            "forward_behavior": summarize_forward_behavior(bars, horizons=horizons),
        }

    return {
        "horizons": list(horizons),
        "detectors": per_detector,
        "notes": "Phase 4 baseline comparison scaffold. Full multi-detector ranking deferred.",
    }
