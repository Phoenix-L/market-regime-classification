# Wilder Detector Reference (Phase 2 Hardening)

This document makes the Wilder-style detector logic explicit under the current input/output contracts.

## Scope

- Detector: `wilder_style`
- Input contract: `docs/input_contract.md`
- Output contract: `docs/output_contract.md`

The detector is deterministic and rule-based. It does not perform data fetching, canonicalization, or storage operations.

## Input assumptions (enforced before computation)

1. Non-empty `list[Mapping]`.
2. Required fields: `symbol`, `timestamp`, `open`, `high`, `low`, `close`, `volume`.
3. Single symbol ordered series.
4. Strictly increasing timezone-aware `timestamp`.
5. Numeric OHLCV fields must be finite.

## Indicator construction

Given bars indexed by `i`:

### 1) True Range (TR)
For `i > 0`:
- `range_a = high[i] - low[i]`
- `range_b = abs(high[i] - close[i-1])`
- `range_c = abs(low[i] - close[i-1])`
- `TR[i] = max(range_a, range_b, range_c)`

`TR[0] = 0.0`.

### 2) Directional Movement (DM+ / DM-)
For `i > 0`:
- `up_move = high[i] - high[i-1]`
- `down_move = low[i-1] - low[i]`
- `DM+[i] = up_move` when `up_move > down_move` and `up_move > 0`, else `0.0`
- `DM-[i] = down_move` when `down_move > up_move` and `down_move > 0`, else `0.0`

`DM+[0] = DM-[0] = 0.0`.

### 3) Wilder smoothing
For series `x` and period `n`:
- Seed at `n-1`: average of `x[0:n]`
- Recurrence for `i >= n`:
  - `sum_i = sum_{i-1} - (sum_{i-1}/n) + x[i]`
  - smoothed value = `sum_i / n`

Applied to TR, DM+, DM- to obtain ATR and smoothed DMs.

### 4) DI+, DI-, DX
When ATR and both smoothed DM values are available and ATR != 0:
- `DI+ = 100 * DM+_smoothed / ATR`
- `DI- = 100 * DM-_smoothed / ATR`
- `DX = 100 * abs(DI+ - DI-) / (DI+ + DI-)` (or `0.0` if denominator is zero)

Otherwise values are `None`.

### 5) ADX
- ADX is `None` until enough DX history exists.
- With period `n`, first ADX appears at index `2n - 2` (requires `2n - 1` bars).
- Seed ADX = mean of `n` DX values from indices `[n-1, 2n-2]`.
- Recurrence:
  - `ADX[i] = ((ADX[i-1] * (n - 1)) + DX[i]) / n`

### 6) Derived diagnostics
- `adx_slope`: first difference of ADX (`None` when unavailable).
- `di_gap`: `abs(DI+ - DI-)` when both available, else `None`.
- `di_dominant_side`: `up`, `down`, or `none` (tie or unavailable).
- `di_cross`: binary marker for side changes between `up` and `down`.
- `recent_di_cross_count`: rolling sum of `di_cross` over configured window.
- `di_dominance_run`: run length of current non-`none` dominant side.

## Warm-up behavior

- Indicator fields depending on smoothing are `None` during warm-up.
- Regime labels are still emitted from bar 0:
  - missing indicator evidence contributes no trend/oscillation evidence,
  - resulting early raw labels are typically `transition` unless other evidence thresholds are met.
- Required output fields are always present.

## Regime logic

### `regime_raw` (immediate evidence)
Per bar, raw proposal counts evidence toward trending and oscillating states:

Trending evidence increments when:
- `adx >= adx_trend_enter`
- `di_gap >= di_gap_trend_enter`
- `di_dominance_run >= dominance_run_trend_min`
- `adx_slope > 0`

Oscillating evidence increments when:
- `adx <= adx_osc_enter`
- `di_gap <= di_gap_osc_max`
- `recent_di_cross_count >= recent_cross_osc_min`

If evidence count >= `transition_trigger_count`:
- trending evidence -> `regime_raw = trending`
- oscillating evidence -> `regime_raw = oscillating`
- otherwise `transition`.

### `regime_final` (smoothed state)
A transition-bridge confirmer is applied:

1. Initial bar confirms raw state, `state_age = 1`.
2. Matching raw state increments `state_age`.
3. Direct flips between `oscillating` and `trending` are not allowed; detector first enters `transition` (`transition_reason=transition_bridge`).
4. While in `transition`, candidate target state must persist for configured confirmation bars:
   - `trend_confirm_bars` for trending
   - `osc_confirm_bars` for oscillating
5. On confirmation, state flips and age resets to 1 (`transition_reason=confirmed`).

### `regime_direction`
Derived from `di_dominant_side`:
- `up` -> `up`
- `down` -> `down`
- `none` -> `none`

### `state_age`
Number of consecutive bars in current confirmed state.

## Output fields

Mandatory output contract fields are always emitted:
- `regime_raw`
- `regime_final`
- `regime_direction`
- `state_age`

Wilder-specific fields retained for visualization/evaluation:
- `adx`, `di_plus`, `di_minus`
- plus supporting diagnostics (`dx`, `di_gap`, `adx_slope`, etc.).

## Determinism

For identical ordered input rows and config:
- indicator values,
- raw/final regimes,
- state ages,
- summary counts
are reproducible exactly.

No randomness is used.
