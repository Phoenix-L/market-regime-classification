# Detector Output Contract v1

This document is the single source of truth for detector output schema requirements.

## Standard artifact

All detectors must return `core.result.DetectionResult` as the inter-module artifact used by downstream consumers.

## Required per-bar fields

- `regime_raw`
- `regime_final`
- `regime_direction`
- `state_age`

## Optional per-bar fields

- `transition_reason`
- `confidence`

## Notes

- Required fields above are the minimum shared contract for cross-detector tooling.
- Detector-specific diagnostic fields are allowed (e.g., ADX/DI for Wilder-style) but are not part of the shared minimum.
- Cross-detector consumers should rely on the shared required fields unless they explicitly opt into detector-specific columns.
- `DetectionResult.bars` remains the tabular per-bar payload (`list[dict]` in the current baseline).

## Runtime enforcement

- Enforced by `core.output_contract.validate_detector_output_v1`.
- Detectors are responsible for producing the required output fields before returning `DetectionResult`.
