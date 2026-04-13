# Boundary with `market-data-core`

## Ownership matrix

### `market-data-core` owns

- Provider adapters / external data ingestion.
- Canonical OHLCV schema and normalization.
- Shared validation rules for reusable market-data quality checks.
- Calendar/session handling.
- Storage and dataset access APIs.

### `market-regime-classification` owns

- Detector interfaces and detector family implementations.
- Detector-specific feature derivation and signal composition.
- Regime state labels and detector output contracts.
- Evaluation/comparison workflows for regimes.
- Visualization for detector diagnostics.

## Contract handoff

This repository consumes upstream canonical bar payloads and enforces only detector-entry preconditions described in `docs/input_contract.md`.

## Must not be implemented here

- Provider/data fetching adapters.
- Canonicalization/re-cleaning pipelines owned upstream.
- Alternate canonical schema definitions.
- Storage/provider orchestration abstractions.

## Minimal integration expectation

`market-data-core` load (external) -> detector run in this repo -> `DetectionResult` output.

No market-data fetching path is implemented inside this package.
