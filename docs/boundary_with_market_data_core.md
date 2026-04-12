# Boundary with `market-data-core`

## Ownership Matrix

## `market-data-core` owns

- Provider adapters / external data ingestion.
- Canonical OHLCV schema and normalization.
- Shared validation rules for reusable market-data quality checks.
- Calendar/session handling.
- Storage and dataset access APIs.

## `market-regime-classification` owns

- Detector interfaces and detector family implementations.
- Detector-specific feature derivation and signal composition.
- Regime state machine and label semantics.
- Detector output contracts and metadata.
- Evaluation/comparison workflows for regimes.
- Visualization for detector diagnostics.

## Upstream Contract Assumptions (Current)

This repository currently assumes upstream-delivered bars include:

- Timestamp index or timestamp column.
- Canonical OHLCV fields.
- Instrument + timeframe metadata.
- Session-aware semantics already resolved upstream.

## Must Not Be Duplicated Here

- Re-normalization pipelines already owned by `market-data-core`.
- Alternate canonical schema definitions.
- Dataset storage/provider orchestration.

## Open Contract Sync Items (TODO)

1. Confirm exact `market-data-core` Python API for bar retrieval.
2. Confirm canonical column naming and timezone/session conventions.
3. Confirm dataset metadata fields to preserve in detector outputs.
4. Confirm expected null/missing-data policy before detector runs.
5. Align result artifact serialization conventions for cross-repo workflows.

Until these are confirmed, this repo uses interface placeholders and explicit TODO markers instead of speculative concrete adapters.
