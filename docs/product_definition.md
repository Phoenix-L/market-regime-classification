# Product Definition

## Purpose

`market-regime-classification` provides a focused research platform for market regime detection, labeling, visualization, and comparison across multiple detector families.

## Target Users

- Quant researchers studying market structure/regime behavior.
- Research engineers implementing detector variants.
- Analysts diagnosing detector outputs and transition dynamics.

## First-Release Scope (Bootstrap + Alignment)

- Detector-focused package skeleton.
- Core contracts (detector interface, output schema, shared enums/types).
- State-machine philosophy and guardrails.
- Evaluation/visualization architecture documents.
- Explicit repository boundary with `market-data-core`.

## Out of Scope (Current Phase)

- Full detector algorithm implementation.
- Strategy and signal-to-trade logic.
- Broker/execution integration.
- Rebuilding data provider adapters/canonicalization.

## Relationship to `market-data-core`

- `market-data-core` is the upstream data foundation.
- This repo consumes curated/canonical bars and session-aware datasets.
- This repo must not duplicate upstream data ownership responsibilities.

## Expected Outputs

- Per-bar regime labels (raw + confirmed).
- Regime direction labels (separate from structure state).
- Detector metadata/config snapshots for reproducibility.
- Evaluation summaries and comparison-ready artifacts.
- Diagnostic visualizations for detector behavior review.

## First-Release Success Criteria

1. Repo structure and docs clearly separate responsibilities from `market-data-core`.
2. Detector contract is explicit enough for multiple implementations.
3. Shared state machine model is established and reusable.
4. Basic tests validate package importability and core contract scaffolding.
5. Open contract-sync TODOs are documented, not guessed.
