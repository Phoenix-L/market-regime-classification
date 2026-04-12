"""Wilder-style signal and indicator computations."""

from collections import deque
from typing import Any, Mapping


def _wilder_smooth(values: list[float], length: int) -> list[float | None]:
    out: list[float | None] = [None] * len(values)
    if len(values) < length:
        return out

    seed = sum(values[:length])
    out[length - 1] = seed / length
    prev_sum = seed
    for i in range(length, len(values)):
        prev_sum = prev_sum - (prev_sum / length) + values[i]
        out[i] = prev_sum / length
    return out


def _rolling_int_sum(values: list[int], window: int) -> list[int]:
    out: list[int] = []
    q: deque[int] = deque()
    running = 0
    for value in values:
        q.append(value)
        running += value
        if len(q) > window:
            running -= q.popleft()
        out.append(running)
    return out


def compute_wilder_signals(
    bars: list[Mapping[str, Any]],
    *,
    wilder_length: int,
    recent_cross_window: int,
) -> list[dict[str, Any]]:
    """Compute Wilder DMI/ADX indicators and derived regime signals."""
    if not bars:
        return []

    highs = [float(bar["high"]) for bar in bars]
    lows = [float(bar["low"]) for bar in bars]
    closes = [float(bar["close"]) for bar in bars]

    tr: list[float] = [0.0]
    dm_plus: list[float] = [0.0]
    dm_minus: list[float] = [0.0]

    for i in range(1, len(bars)):
        up_move = highs[i] - highs[i - 1]
        down_move = lows[i - 1] - lows[i]

        dm_plus.append(up_move if (up_move > down_move and up_move > 0) else 0.0)
        dm_minus.append(down_move if (down_move > up_move and down_move > 0) else 0.0)

        range_a = highs[i] - lows[i]
        range_b = abs(highs[i] - closes[i - 1])
        range_c = abs(lows[i] - closes[i - 1])
        tr.append(max(range_a, range_b, range_c))

    atr_wilder = _wilder_smooth(tr, wilder_length)
    dm_plus_wilder = _wilder_smooth(dm_plus, wilder_length)
    dm_minus_wilder = _wilder_smooth(dm_minus, wilder_length)

    di_plus: list[float | None] = []
    di_minus: list[float | None] = []
    dx: list[float | None] = []

    for i in range(len(bars)):
        atr = atr_wilder[i]
        plus_sm = dm_plus_wilder[i]
        minus_sm = dm_minus_wilder[i]

        if atr is None or plus_sm is None or minus_sm is None or atr == 0:
            di_plus.append(None)
            di_minus.append(None)
            dx.append(None)
            continue

        plus = 100.0 * (plus_sm / atr)
        minus = 100.0 * (minus_sm / atr)
        di_plus.append(plus)
        di_minus.append(minus)
        denom = plus + minus
        dx.append(0.0 if denom == 0 else 100.0 * (abs(plus - minus) / denom))

    adx: list[float | None] = [None] * len(bars)
    n = wilder_length
    if len(bars) >= (2 * n - 1):
        seed_start = n - 1
        seed_end = 2 * n - 1
        seed_values = [v for v in dx[seed_start:seed_end] if v is not None]
        if len(seed_values) == n:
            adx[seed_end - 1] = sum(seed_values) / n
            for i in range(seed_end, len(bars)):
                prev_adx = adx[i - 1]
                dx_i = dx[i]
                if prev_adx is None or dx_i is None:
                    adx[i] = prev_adx
                else:
                    adx[i] = ((prev_adx * (n - 1)) + dx_i) / n

    adx_slope: list[float | None] = [None]
    for i in range(1, len(bars)):
        prev = adx[i - 1]
        curr = adx[i]
        adx_slope.append(None if prev is None or curr is None else curr - prev)

    di_gap: list[float | None] = []
    di_dominant_side: list[str] = []
    di_cross: list[int] = [0]
    di_dominance_run: list[int] = []

    prev_side = "none"
    run = 0
    for i in range(len(bars)):
        plus = di_plus[i]
        minus = di_minus[i]
        if plus is None or minus is None:
            gap = None
            side = "none"
        else:
            gap = abs(plus - minus)
            side = "up" if plus > minus else "down" if minus > plus else "none"

        di_gap.append(gap)
        di_dominant_side.append(side)

        if i > 0 and side in {"up", "down"} and prev_side in {"up", "down"} and side != prev_side:
            di_cross.append(1)
        elif i > 0:
            di_cross.append(0)

        if side == "none":
            run = 0
        elif side == prev_side:
            run += 1
        else:
            run = 1
        di_dominance_run.append(run)
        prev_side = side

    recent_di_cross_count = _rolling_int_sum(di_cross, recent_cross_window)

    rows: list[dict[str, Any]] = []
    for i, bar in enumerate(bars):
        row = dict(bar)
        row.update(
            {
                "tr": tr[i],
                "dm_plus": dm_plus[i],
                "dm_minus": dm_minus[i],
                "atr_wilder": atr_wilder[i],
                "dm_plus_wilder": dm_plus_wilder[i],
                "dm_minus_wilder": dm_minus_wilder[i],
                "di_plus": di_plus[i],
                "di_minus": di_minus[i],
                "dx": dx[i],
                "adx": adx[i],
                "adx_slope": adx_slope[i],
                "di_gap": di_gap[i],
                "di_dominant_side": di_dominant_side[i],
                "di_dominance_run": di_dominance_run[i],
                "di_cross": di_cross[i],
                "recent_di_cross_count": recent_di_cross_count[i],
            }
        )
        rows.append(row)

    return rows
