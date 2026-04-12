# Wilder-Style Detector (v0.1 Baseline)

This detector is the first concrete implementation in this repository.

## What it does

The Wilder-style detector computes classic DMI/ADX internals and uses an explicit state machine to classify each bar as:

- `oscillating`
- `transition`
- `trending`

Direction is output separately from structure as:

- `up`
- `down`
- `none`

## Signals used

Core Wilder indicators:
- True Range (`tr`)
- Directional Movement (`dm_plus`, `dm_minus`)
- Wilder smoothing for ATR and DM streams
- `di_plus`, `di_minus`, `dx`, `adx`

Derived regime signals:
- `adx_slope`
- `di_gap`
- `di_dominant_side`
- `di_dominance_run`
- `di_cross`
- `recent_di_cross_count`

## State-machine behavior

The classifier emits both:
- `regime_raw`: immediate per-bar proposal from threshold evidence
- `regime_final`: confirmed state after anti-flip controls

Anti-flip controls include:
- transition-bridge behavior (prefer `oscillating -> transition -> trending` and reverse)
- per-target confirmation bars (`trend_confirm_bars`, `osc_confirm_bars`)
- explicit hysteresis via enter/exit-like threshold separation

## Current limitations

- Baseline thresholds are conservative defaults, not symbol-optimized.
- Input format in this version is `list[dict]` OHLCV bars.
- No full evaluation reports or plotting diagnostics in this phase.

## Later phases

- add richer visualization panes for ADX/DI diagnostics
- add evaluation baselines for transition quality and persistence
- compare against upcoming feature-based detector under common schema
