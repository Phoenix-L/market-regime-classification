"""Minimal comparison-ready visualization scaffold."""

from typing import Any

from .overlays import add_regime_strip
from .panes import _require_matplotlib


def plot_detector_comparison(detector_runs: dict[str, list[dict[str, Any]]]) -> tuple[Any, Any]:
    """Plot compact regime strips for multiple detectors.

    This is intentionally minimal for Phase 3 and only visualizes `regime_final`.
    """
    if not detector_runs:
        raise ValueError("detector_runs cannot be empty")

    plt = _require_matplotlib()
    names = list(detector_runs.keys())
    fig, axes = plt.subplots(len(names), 1, sharex=True, figsize=(12, 1.8 * len(names)))
    if len(names) == 1:
        axes = [axes]

    for ax, name in zip(axes, names):
        rows = detector_runs[name]
        x = list(range(len(rows)))
        regimes = [str(row.get("regime_final", "transition")) for row in rows]
        add_regime_strip(ax, x, regimes)
        ax.set_title(name, loc="left", fontsize=9)

    axes[-1].set_xlabel("Bar Index")
    fig.tight_layout(pad=1.0)
    return fig, axes
