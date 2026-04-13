"""Forward behavior and event-study utilities for regime analysis."""

from collections import defaultdict
import math
from statistics import mean, median
from typing import Any, Iterable


_ALLOWED_DIRECTIONS = {"up", "down", "none"}


def _require_rows(rows: list[dict[str, Any]]) -> None:
    if not isinstance(rows, list):
        raise TypeError("evaluation expects list[dict] rows")
    if not rows:
        raise ValueError("rows cannot be empty")
    for i, row in enumerate(rows):
        if not isinstance(row, dict):
            raise TypeError(f"row {i} must be dict")


def _require_columns(rows: list[dict[str, Any]], *columns: str) -> None:
    for i, row in enumerate(rows):
        missing = [col for col in columns if col not in row]
        if missing:
            raise ValueError(f"rows missing columns at row {i}: {missing}")


def _coerce_price_series(rows: list[dict[str, Any]], price_col: str) -> list[float]:
    closes: list[float] = []
    for i, row in enumerate(rows):
        try:
            value = float(row[price_col])
        except (TypeError, ValueError) as exc:
            raise ValueError(f"price column '{price_col}' must be numeric at row {i}") from exc
        if not math.isfinite(value):
            raise ValueError(f"price column '{price_col}' must be finite at row {i}")
        closes.append(value)
    return closes


def _forward_return(closes: list[float], idx: int, horizon: int) -> float | None:
    j = idx + horizon
    if j >= len(closes):
        return None
    start = closes[idx]
    if start == 0:
        return None
    return (closes[j] - start) / start


def _directional_efficiency(closes: list[float], idx: int, horizon: int) -> float | None:
    j = idx + horizon
    if j >= len(closes):
        return None
    path = closes[idx : j + 1]
    denominator = sum(abs(path[k] - path[k - 1]) for k in range(1, len(path)))
    if denominator == 0:
        return 0.0
    return abs(path[-1] - path[0]) / denominator


def summarize_forward_behavior(
    rows: list[dict[str, Any]],
    *,
    horizons: Iterable[int] = (1, 3, 5, 10),
    group_col: str = "regime_final",
    price_col: str = "close",
) -> dict[str, Any]:
    """Group forward return/move/efficiency summaries by regime label."""
    _require_rows(rows)
    _require_columns(rows, group_col, price_col)

    closes = _coerce_price_series(rows, price_col)
    horizon_list = list(horizons)
    out: dict[str, Any] = {"horizons": horizon_list, "by_horizon": {}}

    for horizon in horizon_list:
        grouped: dict[str, list[dict[str, float]]] = defaultdict(list)
        for i, row in enumerate(rows):
            ret = _forward_return(closes, i, horizon)
            if ret is None:
                continue
            grouped[str(row[group_col])].append(
                {
                    "forward_return": ret,
                    "forward_abs_return": abs(ret),
                    "directional_efficiency": _directional_efficiency(closes, i, horizon) or 0.0,
                }
            )

        summary = {}
        for state, vals in grouped.items():
            rets = [v["forward_return"] for v in vals]
            abs_rets = [v["forward_abs_return"] for v in vals]
            eff = [v["directional_efficiency"] for v in vals]
            summary[state] = {
                "count": len(vals),
                "mean_forward_return": float(mean(rets)),
                "median_forward_return": float(median(rets)),
                "mean_abs_forward_return": float(mean(abs_rets)),
                "mean_directional_efficiency": float(mean(eff)),
                "positive_return_rate": float(sum(1 for r in rets if r > 0) / len(rets)),
            }
        out["by_horizon"][horizon] = summary

    return out


def extract_regime_transition_events(
    rows: list[dict[str, Any]],
    *,
    state_col: str = "regime_final",
    from_state: str | None = None,
    to_state: str | None = None,
) -> list[dict[str, Any]]:
    """Extract confirmed state-change events."""
    _require_rows(rows)
    _require_columns(rows, state_col)

    events: list[dict[str, Any]] = []
    for i in range(1, len(rows)):
        prev_state = str(rows[i - 1][state_col])
        curr_state = str(rows[i][state_col])
        if curr_state == prev_state:
            continue
        if from_state is not None and prev_state != from_state:
            continue
        if to_state is not None and curr_state != to_state:
            continue
        events.append({"index": i, "from_state": prev_state, "to_state": curr_state})
    return events


def run_regime_event_study(
    rows: list[dict[str, Any]],
    *,
    pre_window: int = 3,
    post_window: int = 5,
    price_col: str = "close",
    focus_to_state: str | None = None,
) -> dict[str, Any]:
    """Event-aligned returns around confirmed regime changes."""
    _require_rows(rows)
    _require_columns(rows, price_col)

    closes = _coerce_price_series(rows, price_col)
    events = extract_regime_transition_events(rows, to_state=focus_to_state)

    aligned: dict[int, list[float]] = defaultdict(list)
    for event in events:
        idx = event["index"]
        base = closes[idx]
        if base == 0:
            continue
        for offset in range(-pre_window, post_window + 1):
            k = idx + offset
            if k < 0 or k >= len(closes):
                continue
            aligned[offset].append((closes[k] - base) / base)

    aligned_summary = {
        offset: {
            "count": len(vals),
            "mean_return": float(mean(vals)) if vals else None,
            "median_return": float(median(vals)) if vals else None,
        }
        for offset, vals in sorted(aligned.items())
    }

    to_transition = extract_regime_transition_events(rows, to_state="transition")
    to_trending = extract_regime_transition_events(rows, to_state="trending")

    continuation_prob = _continuation_probability(rows, state="trending", horizon=min(3, post_window), price_col=price_col)
    snapback_prob = _snapback_probability(rows, horizon=min(3, post_window), price_col=price_col)

    return {
        "num_events": len(events),
        "events": events,
        "aligned_return_summary": aligned_summary,
        "num_events_to_transition": len(to_transition),
        "num_events_to_trending": len(to_trending),
        "continuation_probability_trending": continuation_prob,
        "snapback_probability": snapback_prob,
    }


def _continuation_probability(
    rows: list[dict[str, Any]], *, state: str, horizon: int, price_col: str
) -> float | None:
    closes = _coerce_price_series(rows, price_col)
    hits = 0
    total = 0
    for i, row in enumerate(rows):
        if str(row.get("regime_final")) != state:
            continue
        direction = str(row.get("regime_direction", "none"))
        if direction not in _ALLOWED_DIRECTIONS:
            continue
        if direction == "none":
            continue
        ret = _forward_return(closes, i, horizon)
        if ret is None:
            continue
        total += 1
        if (direction == "up" and ret > 0) or (direction == "down" and ret < 0):
            hits += 1
    if total == 0:
        return None
    return hits / total


def _snapback_probability(rows: list[dict[str, Any]], *, horizon: int, price_col: str) -> float | None:
    closes = _coerce_price_series(rows, price_col)
    reversals = 0
    total = 0
    for i in range(len(rows) - 2 * horizon):
        first = closes[i + horizon] - closes[i]
        second = closes[i + 2 * horizon] - closes[i + horizon]
        if first == 0:
            continue
        total += 1
        if first * second < 0:
            reversals += 1
    if total == 0:
        return None
    return reversals / total
