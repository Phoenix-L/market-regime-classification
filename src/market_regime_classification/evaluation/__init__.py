"""Evaluation modules for regime detector outputs."""

from .comparison import compare_detector_outputs
from .event_study import (
    extract_regime_transition_events,
    run_regime_event_study,
    summarize_forward_behavior,
)
from .regime_stats import segment_state_runs, summarize_regime_durations

__all__ = [
    "segment_state_runs",
    "summarize_regime_durations",
    "summarize_forward_behavior",
    "extract_regime_transition_events",
    "run_regime_event_study",
    "compare_detector_outputs",
]
