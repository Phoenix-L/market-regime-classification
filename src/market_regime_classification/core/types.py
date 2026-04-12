"""Shared lightweight types used by detector and state-machine contracts."""

from dataclasses import dataclass
from typing import Optional

from .enums import RegimeDirection, RegimeState


@dataclass(slots=True)
class RegimeObservation:
    """Per-bar regime representation used for standardized detector outputs."""

    raw_state: RegimeState
    confirmed_state: RegimeState
    direction: RegimeDirection
    state_age: int
    transition_reason: Optional[str] = None
    confidence: Optional[float] = None
