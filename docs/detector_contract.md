# Detector Contract

## Base Detector Interface

All detectors should implement the base interface exposed by `core.detector_base.BaseRegimeDetector`.

Required:
- `name: str`
- `version: str`
- `run(data, config=None) -> DetectionResult`

## Expected Inputs

- Tabular bar data supplied by upstream `market-data-core` workflows.
- Detector configuration object/dict (family-specific).
- Optional run context (symbol/timeframe window metadata).

## Expected Outputs

Return `DetectionResult` with:
- detector identity (`detector_name`, `detector_version`)
- `config_snapshot` for reproducibility
- `bars` table-like structure containing regime outputs
- `summary` dictionary for aggregate run diagnostics
- `artifacts` metadata for generated outputs

## Required Output Fields (Per Bar)

At minimum, detector output table should include:
- `raw_state` (proposal before anti-flip confirmation)
- `confirmed_state` (post state-machine gate)
- `direction` (Up/Down/None)
- `state_age` (bars since confirmed state start)
- `transition_reason` (optional textual marker)
- `confidence` (placeholder optional)

## Metadata and Config Capture

Every run should capture immutable detector metadata and resolved config snapshot to support exact reruns and comparisons.

## Raw State vs Final State

- Raw state represents immediate detector evidence.
- Confirmed state applies anti-flip/hysteresis logic for stability.

## Regime Structure vs Regime Direction

State structure and direction are modeled separately:
- Structure: Oscillating / Transition / Trending
- Direction: Up / Down / None

This improves comparability across detector families.

## Comparison-Friendly Schema Principles

- Stable common columns across detectors.
- Detector-specific extra columns allowed under namespaced prefixes.
- Preserve upstream bar key columns to allow joins and aligned studies.
