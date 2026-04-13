# Minimal End-to-End Pipeline (Phase 0/1 Retrofit)

The smallest valid workflow for this repository is:

1. Load canonical bars externally via `market-data-core`.
2. Pass a single symbol / single timeframe ordered bar series to a detector in this repository.
3. Receive `DetectionResult` with per-bar regime labels.

## Explicitly out of the minimum pipeline

- Visualization modules.
- Evaluation/comparison modules.

These layers consume detector outputs but are not required to run baseline detection.

## Minimal contract path

`market-data-core` (external load) -> `validate_detector_input_v1` -> detector calculations -> `validate_detector_output_v1` -> `DetectionResult`

## Responsibility split

- `market-data-core`: data access, canonical schema, session/calendar semantics, upstream validation/normalization.
- `market-regime-classification`: detector-specific logic, regime state decisions, standardized detector outputs.
