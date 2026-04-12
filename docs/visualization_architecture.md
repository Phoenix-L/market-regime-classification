# Visualization Architecture

## Design Principle

Visualization is first-class for detector diagnosis, not an afterthought.

## Planned Components

- **Price/regime overlays**: colorized confirmed-state bands over price.
- **Detector-specific panes**: family-specific evidence diagnostics.
- **Comparison strips**: aligned state ribbons for multi-detector runs.
- **Transition markers**: annotation of confirmed state changes.

## Default Wilder-Style Pane Separation (Planned)

- Pane 1: price + confirmed regime overlay.
- Pane 2: Wilder evidence signals (e.g., trend strength components).
- Pane 3: state-machine diagnostics (raw vs confirmed, dwell counters).

## Multi-Detector Comparison Layout (Planned)

- Shared top price panel.
- One compact regime strip per detector.
- Optional aggregate disagreement/conflict panel.

## Scope Boundary

Visualization modules consume detector outputs; they do not ingest/clean raw market data.
