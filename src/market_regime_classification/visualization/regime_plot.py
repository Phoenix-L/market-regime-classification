"""Single-detector regime plotting entry points."""

from collections.abc import Mapping as MappingABC
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
_ALLOWED_REGIMES = {"oscillating", "transition", "trending"}
_ALLOWED_DIRECTIONS = {"up", "down", "none"}


def _coerce_rows(bars: Any) -> list[dict[str, Any]]:
    if not isinstance(bars, list):
        raise TypeError("Visualization baseline expects list[dict] detector bars")
    rows: list[dict[str, Any]] = []
    for i, row in enumerate(bars):
        if not isinstance(row, MappingABC):
            raise TypeError(f"Visualization row {i} must be mapping-like")
        rows.append(dict(row))
    return rows


def _validate_columns(rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError("Cannot plot empty detector output")

    for i, row in enumerate(rows):
        missing = sorted(col for col in _REQUIRED_COLUMNS if col not in row)
        if missing:
            raise ValueError(f"Detector output missing required columns at row {i}: {missing}")


def _coerce_numeric_series(rows: list[dict[str, Any]], column: str, *, allow_none: bool = True) -> list[float | None]:
    out: list[float | None] = []
    for i, row in enumerate(rows):
        value = row.get(column)
        if value is None:
            if allow_none:
                out.append(None)
                continue
            raise ValueError(f"Column '{column}' must be numeric; found None at row {i}")
        try:
            out.append(float(value))
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Column '{column}' must be numeric-or-None; invalid at row {i}") from exc
    return out


def _validate_regime_values(rows: list[dict[str, Any]]) -> tuple[list[str], list[str]]:
    regime_final: list[str] = []
    regime_direction: list[str] = []

    for i, row in enumerate(rows):
        final = str(row.get("regime_final", "transition"))
        direction = str(row.get("regime_direction", "none"))
        if final not in _ALLOWED_REGIMES:
            raise ValueError(f"Invalid regime_final '{final}' at row {i}")
        if direction not in _ALLOWED_DIRECTIONS:
            raise ValueError(f"Invalid regime_direction '{direction}' at row {i}")
        regime_final.append(final)
        regime_direction.append(direction)

    return regime_final, regime_direction


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
    close = [float(v) for v in _coerce_numeric_series(rows, "close", allow_none=False)]
    adx = _coerce_numeric_series(rows, "adx")
    di_plus = _coerce_numeric_series(rows, "di_plus")
    di_minus = _coerce_numeric_series(rows, "di_minus")
    regime_final, regime_direction = _validate_regime_values(rows)

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
    if not hasattr(result, "bars"):
        raise TypeError("DetectionResult-like object must provide .bars")

    detector_name = getattr(result, "detector_name", "unknown")
    detector_version = getattr(result, "detector_version", "unknown")
    cfg = getattr(result, "config_snapshot", {})

    composed_title = title or f"{detector_name} ({detector_version})"
    subtitle = None
    if isinstance(cfg, Mapping) and cfg:
        w_len = cfg.get("wilder_length")
        subtitle = f"wilder_length={w_len}" if w_len is not None else None

    return plot_wilder_regime(result.bars, title=composed_title, subtitle=subtitle, save_path=save_path)
