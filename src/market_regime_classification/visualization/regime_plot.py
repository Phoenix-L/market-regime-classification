"""Single-detector regime plotting entry points."""

from pathlib import Path
from typing import Any, Mapping

from .overlays import add_regime_background, add_transition_markers
from .panes import create_default_figure, plot_adx_pane, plot_dmi_pane, plot_price_pane

_REQUIRED_COLUMNS = {
    "close",
    "adx",
    "di_plus",
    "di_minus",
    "regime_final",
    "regime_direction",
}


def _coerce_rows(bars: Any) -> list[dict[str, Any]]:
    if not isinstance(bars, list):
        raise TypeError("Visualization baseline expects list[dict] detector bars")
    return [dict(row) for row in bars]


def _validate_columns(rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError("Cannot plot empty detector output")
    missing = sorted(col for col in _REQUIRED_COLUMNS if col not in rows[0])
    if missing:
        raise ValueError(f"Detector output missing required columns for plotting: {missing}")


def plot_wilder_regime(
    bars: Any,
    *,
    title: str | None = None,
    subtitle: str | None = None,
    save_path: str | Path | None = None,
    show_transition_markers: bool = True,
    adx_trend_enter: float | None = 25.0,
    adx_trend_exit: float | None = 20.0,
) -> tuple[Any, tuple[Any, Any, Any]]:
    """Render default Wilder 3-pane diagnostic plot.

    Returns `(fig, (ax_price, ax_adx, ax_dmi))` and optionally saves to disk.
    """
    rows = _coerce_rows(bars)
    _validate_columns(rows)

    x = list(range(len(rows)))
    close = [float(row["close"]) for row in rows]
    adx = [row.get("adx") for row in rows]
    di_plus = [row.get("di_plus") for row in rows]
    di_minus = [row.get("di_minus") for row in rows]
    regime_final = [str(row.get("regime_final", "transition")) for row in rows]
    regime_direction = [str(row.get("regime_direction", "none")) for row in rows]

    fig, (ax_price, ax_adx, ax_dmi) = create_default_figure(len(rows))

    plot_price_pane(ax_price, x, close)
    add_regime_background(ax_price, x, regime_final, directions=regime_direction, alpha=0.22)
    if show_transition_markers:
        add_transition_markers(ax_price, x, regime_final)

    plot_adx_pane(ax_adx, x, adx, trend_enter=adx_trend_enter, trend_exit=adx_trend_exit)
    plot_dmi_pane(ax_dmi, x, di_plus, di_minus, show_cross_markers=True)

    if title:
        fig.suptitle(title, fontsize=12)
    if subtitle:
        ax_price.set_title(subtitle, fontsize=9, loc="left", color="#555555")

    if save_path is not None:
        out = Path(save_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out, dpi=150, bbox_inches="tight")

    return fig, (ax_price, ax_adx, ax_dmi)


def plot_from_detection_result(
    result: Any,
    *,
    save_path: str | Path | None = None,
    title: str | None = None,
) -> tuple[Any, tuple[Any, Any, Any]]:
    """Convenience entry point using DetectionResult-like object."""
    detector_name = getattr(result, "detector_name", "unknown")
    detector_version = getattr(result, "detector_version", "unknown")
    cfg = getattr(result, "config_snapshot", {})

    composed_title = title or f"{detector_name} ({detector_version})"
    subtitle = None
    if isinstance(cfg, Mapping) and cfg:
        w_len = cfg.get("wilder_length")
        subtitle = f"wilder_length={w_len}" if w_len is not None else None

    return plot_wilder_regime(result.bars, title=composed_title, subtitle=subtitle, save_path=save_path)
