# Visualization Architecture

## Design Principle

Visualization is first-class for detector diagnosis, not an afterthought.

## Phase 3 Baseline (Implemented)

Default single-detector layout (Wilder baseline):
- **Pane 1**: close price with confirmed-regime background shading.
- **Pane 2**: ADX line (+ optional threshold references).
- **Pane 3**: DI+ / DI- lines (+ optional crossover markers).

Rationale:
- keep trend strength (ADX) visually separate from directional dominance (DMI),
- make structural regime and transition points easy to inspect against price.

## Module Responsibilities

- `visualization/panes.py`
  - reusable pane construction,
  - price/ADX/DMI plotting helpers,
  - shared axis conventions.

- `visualization/overlays.py`
  - regime background shading,
  - transition markers,
  - compact regime strip helpers.

- `visualization/regime_plot.py`
  - detector-output-driven single-detector plotting entry points,
  - save-to-file support,
  - return figure/axes for notebooks/scripts.

- `visualization/comparison_plot.py`
  - minimal Phase 3 scaffold for compact multi-detector regime strips,
  - full comparison dashboards deferred to Phase 6.

## Input Contract for Plotting

Expected columns (minimum):
- `close`
- `adx`
- `di_plus`
- `di_minus`
- `regime_final`
- `regime_direction`

Validation behavior:
- plotting validates required columns on every row, not just the first row,
- `close` must be numeric,
- `regime_final` must be one of `oscillating|transition|trending`,
- `regime_direction` must be one of `up|down|none`.

Optional diagnostics:
- `regime_raw`, `transition_reason`, `state_age`, `di_gap`, `adx_slope`.

## Scope Boundary

Visualization modules consume detector outputs; they do not ingest/clean raw market data.

## Deferred to Later Phases

- richer multi-detector comparison layouts,
- disagreement/conflict panels,
- evaluation-linked report rendering.
