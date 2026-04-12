"""Wilder-style detector config placeholders."""

from dataclasses import dataclass


@dataclass(slots=True)
class WilderStyleConfig:
    """Configuration scaffold for future Wilder-style detector implementation."""

    trend_window: int = 14
    volatility_window: int = 14
    min_dwell_bars: int = 3
