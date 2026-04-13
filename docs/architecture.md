# Architecture Overview

## Guiding Principles

- Architecture-first, implementation-light in current phase.
- Narrow detector-focused scope.
- Explicit upstream dependency on `market-data-core` for market-data concerns.
- Standardized outputs to enable multi-detector comparison.

## Package / Module Boundaries

- `core/`: foundational contracts, enums, types, state-machine helpers, result container.
- `detectors/`: detector family implementations and detector-specific configs/signals.
- `evaluation/`: detector output analytics and comparison computations.
- `visualization/`: plotting and diagnostic overlays/panes.
- `cli/`: lightweight entrypoints for research workflows.

## Detector Abstraction Layer

`core.detector_base.BaseRegimeDetector` defines minimal detector identity and run contract:
- `name`
- `version`
- `run(data, config)` returning `DetectionResult`

This keeps implementations swappable and comparison-friendly.

## State Machine Layer

`core.state_machine` defines a generic state confirmation flow:
- Raw proposed state
- Confirmed state
- Anti-flip controls (min dwell + hysteresis hooks)

Detectors can provide different evidence pipelines while sharing transition semantics.

## Evaluation Layer

`evaluation/` is responsible for:
- regime duration and transition diagnostics,
- forward behavior/event studies,
- standardized detector-to-detector comparisons.

It is intentionally data-consumer-side and does not own upstream raw data validation.

## Visualization Layer

`visualization/` provides first-class diagnostics:
- price + state overlays,
- detector-specific panes,
- comparison strips across detectors.

## CLI / Research Workflow Layer

`cli.main` offers bootstrap command surface for local research automation and reproducible runs.

## Upstream Dependency: `market-data-core`

This repository assumes bars/session semantics are already curated upstream and uses explicit input/output contract docs for detector-entry and detector-output enforcement.

## Must Remain Outside This Repo

- Data provider adapters
- Canonical OHLCV normalization/cleaning
- Session/calendar ownership
- Shared storage/dataset service APIs
- Execution/trading layers
