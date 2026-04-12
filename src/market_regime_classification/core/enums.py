"""Shared enums for regime classification outputs."""

from enum import Enum


class RegimeState(str, Enum):
    """Structure-focused regime states used across detector families."""

    OSCILLATING = "oscillating"
    TRANSITION = "transition"
    TRENDING = "trending"


class RegimeDirection(str, Enum):
    """Direction label separated from structural regime state."""

    UP = "up"
    DOWN = "down"
    NONE = "none"
