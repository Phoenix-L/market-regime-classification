# Detector Contract

This document summarizes detector behavior and points to the contract source-of-truth docs.

## Source-of-truth contracts

- Input contract: `docs/input_contract.md`
- Output contract: `docs/output_contract.md`
- State-machine policy: `docs/state_machine.md`
- Minimal pipeline: `docs/pipeline.md`

## Base detector interface

All detectors implement `core.detector_base.BaseRegimeDetector`:

- `name: str`
- `version: str`
- `run(data, config=None) -> DetectionResult`

## Standard artifact

Detectors must return `DetectionResult` and include contract-required per-bar output fields.

## Boundary reminder

Detector entry expects upstream canonical data from `market-data-core`; this repository does not own data fetching/canonicalization/storage concerns.
