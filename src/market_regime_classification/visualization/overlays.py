"""Overlay utilities for regime diagnostics."""

from collections.abc import Sequence
from typing import Any

REGIME_COLORS: dict[str, str] = {
    "oscillating": "#d9d9d9",
    "transition": "#fdd49e",
    "trending": "#c7e9c0",
}

TREND_DIRECTION_COLORS: dict[str, str] = {
    "up": "#74c476",
    "down": "#fb6a4a",
    "none": "#c7e9c0",
}


def add_regime_background(
    ax: Any,
    x: Sequence[int],
    regimes: Sequence[str],
    *,
    directions: Sequence[str] | None = None,
    alpha: float = 0.2,
) -> None:
    """Shade background by confirmed regime in contiguous segments."""
    if not regimes:
        return

    start = 0
    for i in range(1, len(regimes) + 1):
        boundary = i == len(regimes) or regimes[i] != regimes[i - 1]
        if not boundary:
            continue

        state = regimes[i - 1]
        color = REGIME_COLORS.get(state, "#efefef")
        if state == "trending" and directions is not None and i - 1 < len(directions):
            color = TREND_DIRECTION_COLORS.get(directions[i - 1], color)

        left = x[start]
        right = x[i - 1] + 1
        ax.axvspan(left, right, color=color, alpha=alpha, linewidth=0)
        start = i


def add_transition_markers(ax: Any, x: Sequence[int], regimes: Sequence[str]) -> list[int]:
    """Mark confirmed regime changes with subtle vertical lines."""
    points: list[int] = []
    for i in range(1, len(regimes)):
        if regimes[i] != regimes[i - 1]:
            points.append(x[i])
            ax.axvline(x[i], color="#636363", linewidth=0.8, alpha=0.35, linestyle="--")
    return points


def add_regime_strip(ax: Any, x: Sequence[int], regimes: Sequence[str]) -> None:
    """Draw a compact categorical strip that mirrors confirmed regime states."""
    mapping = {"oscillating": 0, "transition": 1, "trending": 2}
    y = [mapping.get(state, 1) for state in regimes]
    ax.step(x, y, where="post", color="#525252", linewidth=0.9)
    ax.set_yticks([0, 1, 2], ["Osc", "Trn", "Trd"])
    ax.set_ylim(-0.5, 2.5)
    ax.set_ylabel("Regime")
