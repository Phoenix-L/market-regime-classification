# Evaluation Framework

## Goals

Enable consistent evaluation of regime detectors using common output schema and reproducible metrics.

## Phase 4 Baseline (Implemented)

The baseline evaluation layer now provides:

1. **Regime statistics**
- regime bar counts and proportions
- run segmentation from `regime_final`
- duration summaries (mean/median/min/max)
- transition counts and transition matrix
- short-lived run frequency

2. **Forward behavior analysis**
- configurable forward horizons (default 1/3/5/10)
- grouped by `regime_final`
- mean/median forward return
- mean absolute forward return
- directional efficiency proxy
- positive-return rate

3. **Transition event-study analysis**
- confirmed state-change event extraction
- pre/post event aligned return summaries
- transition-focused counts (e.g., to Transition, to Trending)
- conservative continuation/snapback probability baselines

4. **Comparison readiness scaffold**
- detector-keyed summary structures
- consistent horizon handling across detectors
- full ranking/comparison dashboards deferred to later phases

## Important Scope Boundary

Evaluation is about **regime-label quality and behavioral separation**, not strategy backtesting.

Out of scope in this baseline:
- PnL attribution
- portfolio construction analytics
- execution or slippage modeling

## Detector Comparison Principles

- Compare on identical input datasets/windows.
- Use shared schema fields for apples-to-apples metrics.
- Separate structural-state behavior from directional labels.
- Preserve detector-specific diagnostics as secondary context.

## In-Scope for This Repo

- Regime-focused analytics and detector comparisons.
- Study artifacts for research notebooks/reports.

## Deferred to Later Phases

- richer multi-detector ranking logic
- significance testing and confidence-interval frameworks
- integrated evaluation + visualization report generators
