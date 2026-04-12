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

This repo is currently in **Phase 0/1: bootstrap + architecture/contract alignment**.

Included now:
- repository/package skeleton,
- detector interface contracts,
- regime state and result types,
- architecture and planning documents,
- lightweight smoke tests.

Not included yet:
- full Wilder-style detector implementation,
- feature-based detector implementation,
- production-grade evaluation/visualization pipelines.

## Planned detector families

- Wilder-style detector (first implementation phase)
- Feature-based detector (later implementation phase)

## Next implementation steps

1. Confirm synchronization points with `market-data-core` contract owners.
2. Implement Phase 2 Wilder-style detector internals behind current interfaces.
3. Establish baseline plots/evaluation metrics for detector diagnostics.
4. Add feature-based detector and run standardized comparison studies.
