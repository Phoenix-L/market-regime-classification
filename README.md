# market-regime-classification

`market-regime-classification` is a standalone, research-oriented repository for defining, testing, and comparing **market regime detectors**.

## What this repository is

- A detector-focused research platform.
- A home for regime state machine design and detector outputs.
- A place to evaluate and compare multiple regime detection approaches.
- A visualization and diagnostics layer for regime studies.

## What this repository is not

- Not a market data ingestion/normalization foundation.
- Not a broker/execution/trading strategy engine.
- Not a duplicate of `market-data-core`.

## Relationship to `market-data-core`

This repository assumes `market-data-core` is the trusted upstream source for canonical/curated OHLCV bars, session semantics, and data quality rules.

This repository consumes that upstream data and focuses on:

- detector-specific signal derivation,
- regime classification/state transitions,
- detector output artifacts,
- comparison/evaluation workflows,
- regime diagnostics visualizations.

See `docs/boundary_with_market_data_core.md` for explicit boundary definitions.

## Current maturity

This repo is currently in **Phase 4: evaluation baseline for the Wilder-style detector**.

Included now:
- repository/package skeleton and contracts,
- implemented Wilder-style detector (signals + classifier + state machine),
- detector output schema, baseline visualization artifacts (price/regime, ADX, DMI), and baseline evaluation toolkit,
- architecture and planning documents,
- focused unit tests for core and Wilder baseline behavior.

Not included yet:
- feature-based detector implementation,
- advanced multi-detector comparison dashboards/workflows,
- richer statistical ranking/significance layer for cross-detector studies.

## Planned detector families

- Wilder-style detector (first implementation phase)
- Feature-based detector (later implementation phase)

## Next implementation steps

1. Implement Phase 5 feature-based detector with shared contracts.
2. Expand visual/evaluation diagnostics for multi-detector parity.
3. Build Phase 6 comparison workflows and standardized benchmark reports.
4. Add richer statistical significance tooling for detector comparison.
