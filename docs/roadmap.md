# Roadmap

## Phase 0/1 — Bootstrap + Contract Alignment (Completed)

- Establish repository skeleton.
- Define architecture and detector contracts.
- Clarify boundary with `market-data-core`.
- Add lightweight scaffold tests.

## Phase 2 — Wilder-Style Detector Implementation (Completed: v0.1 baseline)

- Implemented Wilder internals (TR/DM/DI/DX/ADX + derived signals).
- Implemented explicit 3-state classifier and confirmation logic.
- Added focused unit tests around signal and state behavior.

## Phase 3 — Visualization Baseline (Next)

- Implement baseline price/regime overlays.
- Add Wilder diagnostic panes.
- Add exportable static plotting utilities.

## Phase 4 — Evaluation Baseline

- Implement regime duration/transition metrics.
- Implement event-study style forward behavior modules.
- Add reproducible report tables.

## Phase 5 — Feature-Based Detector Implementation

- Implement feature extraction + model-style classification pipeline.
- Integrate with shared state-machine contract.
- Add family-specific diagnostic outputs.

## Phase 6 — Multi-Detector Comparison Workflows

- Unified benchmark runner across detectors.
- Comparison dashboards/plots and summary outputs.
- Research workflow templates for iterative detector development.
