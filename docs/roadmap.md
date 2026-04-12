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

## Phase 3 — Visualization Baseline (Completed: v0.1 baseline)

- Implemented default 3-pane Wilder diagnostic plot:
  - price + regime overlay,
  - ADX strength pane,
  - DMI direction pane.
- Added saved-artifact path and DetectionResult plotting entry point.
- Added visualization smoke and overlay behavior tests.

## Phase 4 — Evaluation Baseline (Completed: v0.1 baseline)

- Implemented regime stability statistics (run lengths, durations, transition matrix).
- Implemented grouped forward-behavior summaries by regime.
- Implemented transition/event-study baseline with aligned pre/post windows.
- Added comparison-ready summary scaffold and focused evaluation tests.

## Phase 5 — Feature-Based Detector Implementation (Next)

- Implement feature extraction + model-style classification pipeline.
- Integrate with shared state-machine contract.
- Add family-specific diagnostic outputs.

## Phase 6 — Multi-Detector Comparison Workflows

- Unified benchmark runner across detectors.
- Comparison dashboards/plots and summary outputs.
- Research workflow templates for iterative detector development.
