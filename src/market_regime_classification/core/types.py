"""Shared lightweight types used by detector and state-machine contracts."""

from dataclasses import dataclass
from typing import Optional

from .enums import RegimeDirection, RegimeState


@dataclass(slots=True)
class RegimeObservation:
    """Per-bar regime representation used for standardized detector outputs."""

    regime_raw: RegimeState
    regime_final: RegimeState
    regime_direction: RegimeDirection
    state_age: int
    transition_reason: Optional[str] = None
    confidence: Optional[float] = None
