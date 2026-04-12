"""Reusable pane builders for detector diagnosis plots."""

from collections.abc import Sequence
from typing import Any


def _require_matplotlib():
    try:
        import matplotlib.pyplot as plt
    except ModuleNotFoundError as exc:  # pragma: no cover - exercised by import path
        raise RuntimeError(
            "matplotlib is required for visualization. Install with `pip install matplotlib`."
        ) from exc
    return plt


def create_default_figure(num_points: int) -> tuple[Any, tuple[Any, Any, Any]]:
    """Create default 3-pane layout: price, ADX, DMI."""
    plt = _require_matplotlib()
    fig, axes = plt.subplots(
        3,
        1,
        sharex=True,
        figsize=(12, 8),
        gridspec_kw={"height_ratios": [3.0, 1.3, 1.3]},
    )
    fig.tight_layout(pad=1.2)
    if num_points <= 120:
        axes[0].grid(alpha=0.15)
        axes[1].grid(alpha=0.2)
        axes[2].grid(alpha=0.2)
    return fig, (axes[0], axes[1], axes[2])


def plot_price_pane(ax: Any, x: Sequence[int], closes: Sequence[float], label: str = "Close") -> None:
    """Plot price series on the top pane."""
    ax.plot(x, closes, color="black", linewidth=1.2, label=label)
    ax.set_ylabel("Price")
    ax.legend(loc="upper left")


def plot_adx_pane(
    ax: Any,
    x: Sequence[int],
    adx: Sequence[float | None],
    *,
    trend_enter: float | None = None,
    trend_exit: float | None = None,
) -> None:
    """Plot ADX in a dedicated strength pane."""
    y = [float(v) if v is not None else float("nan") for v in adx]
    ax.plot(x, y, color="#1f77b4", linewidth=1.1, label="ADX")
    if trend_enter is not None:
        ax.axhline(trend_enter, color="#1f77b4", linestyle="--", alpha=0.45, linewidth=0.8, label="ADX trend enter")
    if trend_exit is not None:
        ax.axhline(trend_exit, color="#1f77b4", linestyle=":", alpha=0.35, linewidth=0.8, label="ADX trend exit")
    ax.set_ylabel("ADX")
    ax.legend(loc="upper left", ncol=2, fontsize=8)


def plot_dmi_pane(
    ax: Any,
    x: Sequence[int],
    di_plus: Sequence[float | None],
    di_minus: Sequence[float | None],
    *,
    show_cross_markers: bool = True,
) -> None:
    """Plot DI+/DI- in a dedicated direction pane."""
    plus = [float(v) if v is not None else float("nan") for v in di_plus]
    minus = [float(v) if v is not None else float("nan") for v in di_minus]

    ax.plot(x, plus, color="#2ca02c", linewidth=1.0, label="DI+")
    ax.plot(x, minus, color="#d62728", linewidth=1.0, label="DI-")

    if show_cross_markers:
        for i in range(1, len(x)):
            if plus[i - 1] != plus[i - 1] or minus[i - 1] != minus[i - 1]:  # NaN check
                continue
            prev_gap = plus[i - 1] - minus[i - 1]
            curr_gap = plus[i] - minus[i]
            if prev_gap == 0 or curr_gap == 0:
                continue
            if prev_gap * curr_gap < 0:
                ax.axvline(x[i], color="#9467bd", linestyle=":", alpha=0.25, linewidth=0.8)

    ax.set_ylabel("DMI")
    ax.set_xlabel("Bar Index")
    ax.legend(loc="upper left", ncol=2, fontsize=8)
