# Usage Guide

## 1. Introduction

`market-regime-classification` is a research-focused Python package for labeling market behavior into interpretable **regime states** (for example, oscillating vs trending) using OHLCV bar data. In the current release, the primary detector is a Wilder-style DMI/ADX baseline that produces both structural state labels and directional context.

In this project, **regime classification** means assigning each bar to a market structure state (`oscillating`, `transition`, `trending`) and a direction label (`up`, `down`, `none`) based on transparent indicator rules and confirmation logic. After following this guide, you should be able to load bars from `market-data-core`, run detection, inspect outputs, create diagnostic plots, and evaluate regime behavior in script or notebook workflows.

## 2. Installation

This package requires Python 3.11+.

### Option A: editable install (recommended for local research)

```bash
git clone <your-fork-or-repo-url>
cd market-regime-classification
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .
```

### Option B: standard install from source

```bash
pip install .
```

### Install `market-data-core`

This repository intentionally does **not** implement data ingestion. Install and configure `market-data-core` in the same environment so you can fetch curated OHLCV bars upstream.

```bash
pip install market-data-core
```

> If your team uses a private/internal distribution of `market-data-core`, use that install method instead.

## 3. Quick Start (Minimal Example)

Minimal end-to-end example using in-memory OHLCV bars:

```python
from market_regime_classification.detectors.wilder_style import WilderStyleDetector

bars = [
    {"ts": "2026-01-01", "open": 100, "high": 101, "low": 99, "close": 100.5, "volume": 1000},
    {"ts": "2026-01-02", "open": 100.5, "high": 102, "low": 100, "close": 101.8, "volume": 1200},
    {"ts": "2026-01-03", "open": 101.8, "high": 103, "low": 101, "close": 102.6, "volume": 1100},
    # ... more bars
]

detector = WilderStyleDetector()
result = detector.run(bars)

print(result.summary)
print(result.bars[-3:])  # last 3 enriched rows with regime labels + indicators
```

The detector input is currently `list[dict]` with OHLCV keys (`open`, `high`, `low`, `close`, `volume`).

## 4. Core Workflow

### 4.1 Load data

Get curated bars from `market-data-core` (or adapt from your own upstream pipeline) and convert to a list of dictionaries.

```python
# Pseudocode: adapt this to your market-data-core API
# df = market_data_core_client.get_bars(symbol="SPY", timeframe="1D", start="2024-01-01", end="2025-12-31")
# bars = df[["ts", "open", "high", "low", "close", "volume"]].to_dict("records")

bars = your_market_data_core_loader(...)
```

### 4.2 Run detector

```python
from market_regime_classification.detectors.wilder_style import WilderStyleDetector

detector = WilderStyleDetector()
result = detector.run(bars)
```

### 4.3 Inspect outputs

```python
print(result.detector_name, result.detector_version)
print(result.config_snapshot)
print(result.summary)

rows = result.bars
print(rows[0].keys())
```

### 4.4 Visualize results

```python
from market_regime_classification.visualization import plot_from_detection_result

fig, axes = plot_from_detection_result(
    result,
    save_path="artifacts/regime_plot.png",
    title="SPY Wilder Regime Diagnostics",
)
```

### 4.5 Evaluate regimes

```python
from market_regime_classification.evaluation import (
    summarize_regime_durations,
    summarize_forward_behavior,
    run_regime_event_study,
)

dur = summarize_regime_durations(result.bars)
fwd = summarize_forward_behavior(result.bars, horizons=(1, 5, 10))
evt = run_regime_event_study(result.bars, pre_window=3, post_window=5)

print(dur["bar_proportion_by_regime"])
print(fwd["by_horizon"][5])
print(evt["num_events"])
```

## 5. Detector Usage (Wilder-style)

Instantiate the detector and optionally pass a configuration dictionary to `run`.

```python
from market_regime_classification.detectors.wilder_style import WilderStyleDetector

detector = WilderStyleDetector()

config = {
    "wilder_length": 14,
    "adx_trend_enter": 25.0,
    "adx_trend_exit": 20.0,
    "adx_osc_enter": 16.0,
    "di_gap_trend_enter": 12.0,
    "di_gap_trend_exit": 8.0,
    "di_gap_osc_max": 6.0,
    "dominance_run_trend_min": 3,
    "recent_cross_window": 8,
    "recent_cross_osc_min": 2,
    "trend_confirm_bars": 3,
    "osc_confirm_bars": 3,
    "transition_trigger_count": 2,
}

result = detector.run(bars, config=config)
```

### Expected inputs

- Data type: `list[dict]`
- Required fields: `open`, `high`, `low`, `close`, `volume`
- Optional extra fields (kept in output): timestamp, symbol, timeframe metadata, etc.

### Produced outputs

`run(...)` returns a `DetectionResult` containing:
- `bars`: enriched per-bar rows (original fields + indicators + regime labels)
- `summary`: run-level counts and metadata
- `config_snapshot`: resolved detector config
- `artifacts`: lightweight schema metadata

## 6. Understanding the Output

Common output columns in `result.bars`:

- `regime_raw`: immediate per-bar state proposal from current evidence
- `regime_final`: confirmed state after transition/confirmation logic
- `regime_direction`: directional side (`up`, `down`, `none`) independent from structure
- `state_age`: number of consecutive bars in the current confirmed state
- ADX / DMI fields: `adx`, `di_plus`, `di_minus`, plus diagnostics like `di_gap`, `adx_slope`

### Raw vs final regime

- `regime_raw` can change quickly as indicator evidence changes.
- `regime_final` is smoothed by anti-flip confirmation rules, so it is generally more stable for analysis.

### Direction vs structure

- **Structure** (`regime_final`) answers: “Is the market trending, oscillating, or in transition?”
- **Direction** (`regime_direction`) answers: “If directional pressure exists, is it up or down?”

These dimensions are intentionally separate.

## 7. Visualization

Use built-in plotting to inspect regime labels against price and indicators.

```python
from market_regime_classification.visualization import plot_wilder_regime

fig, (ax_price, ax_adx, ax_dmi) = plot_wilder_regime(
    result.bars,
    title="Wilder Regime Plot",
    subtitle="SPY 1D",
    save_path="artifacts/wilder_spy.png",
    show_transition_markers=True,
    adx_trend_enter=25.0,
    adx_trend_exit=20.0,
)
```

Default layout:
1. **Price + regime background** (confirmed regime shading, optional transition markers)
2. **ADX pane** (trend strength with optional threshold references)
3. **DMI pane** (`DI+` and `DI-`, with crossover markers)

Interpretation pattern:
- persistent high ADX + wide DI separation often aligns with `trending`
- lower ADX + frequent DI crosses often aligns with `oscillating`
- mixed evidence commonly appears in `transition`

## 8. Evaluation

The baseline evaluation layer supports three practical views.

### 8.1 Regime stats (durations and transitions)

```python
from market_regime_classification.evaluation import summarize_regime_durations

stats = summarize_regime_durations(result.bars)
print(stats["duration_summary_by_regime"])
print(stats["transition_counts"])
```

Use this to understand persistence and transition frequency.

### 8.2 Forward behavior by regime

```python
from market_regime_classification.evaluation import summarize_forward_behavior

forward = summarize_forward_behavior(result.bars, horizons=(1, 3, 5, 10))
print(forward["by_horizon"][5])
```

Useful for checking whether regimes separate future behavior (returns, absolute movement, efficiency).

### 8.3 Transition event study

```python
from market_regime_classification.evaluation import run_regime_event_study

events = run_regime_event_study(result.bars, pre_window=3, post_window=5)
print(events["aligned_return_summary"])
```

Useful for analyzing what tends to happen before/after confirmed state changes.

## 9. Working with market-data-core

This repository expects cleaned, canonical bars from `market-data-core`; it does **not** provide raw market-data ingestion.

Integration pattern:

```python
from market_regime_classification.detectors.wilder_style import WilderStyleDetector

# 1) Retrieve canonical bars via your market-data-core integration
bars_df = your_market_data_core_loader(symbol="BTC-USD", timeframe="1H", start="2025-01-01", end="2025-06-30")

# 2) Normalize into list[dict] for detector input
bars = bars_df[["ts", "open", "high", "low", "close", "volume"]].to_dict("records")

# 3) Run detector
result = WilderStyleDetector().run(bars)
```

Input assumptions for best results:
- OHLCV values are numeric and pre-validated upstream.
- Bar ordering is chronological.
- Session/calendar and missing-data handling are already resolved upstream.

## 10. Common Patterns

### Run on multiple symbols

```python
from market_regime_classification.detectors.wilder_style import WilderStyleDetector

detector = WilderStyleDetector()
results_by_symbol = {}

for symbol in ["SPY", "QQQ", "IWM"]:
    bars = load_bars_from_market_data_core(symbol)
    results_by_symbol[symbol] = detector.run(bars)
```

### Save outputs for later analysis

```python
import json

rows = result.bars
with open("artifacts/spy_regimes.json", "w", encoding="utf-8") as f:
    json.dump(rows, f, indent=2, default=str)
```

### Batch comparison experiments

```python
from market_regime_classification.evaluation import compare_detector_outputs

detector_bars = {symbol: res.bars for symbol, res in results_by_symbol.items()}
report = compare_detector_outputs(detector_bars, horizons=(1, 5, 10))
```

### Notebook-friendly workflow

```python
# In notebooks:
# - run detector once
# - keep result.bars in memory
# - iterate quickly on plots/evaluation slices

bars = load_bars_from_market_data_core("SPY")
result = WilderStyleDetector().run(bars)
plot_from_detection_result(result)
```

## 11. Limitations (Important)

- This package is **research tooling**, not an execution or trading system.
- Outputs are detector diagnostics and labels, not trade signals.
- The Wilder detector is a **v0.1 baseline** implementation.
- Default thresholds are generic and **not optimized** per symbol/timeframe.
- Evaluation currently provides baseline summaries, not full statistical ranking/significance pipelines.

## 12. Next Steps

Expected near-term evolution:
- feature-based detector implementation
- expanded detector comparison framework
- richer visualization (especially multi-detector diagnostics)

As those land, this guide should be updated with side-by-side workflows and more robust evaluation/reporting patterns.

## 13. Documentation Summary

1. **Sections created:** Introduction, Installation, Quick Start, Core Workflow, Wilder detector usage, output interpretation, visualization, evaluation, `market-data-core` integration, common patterns, limitations, and next steps.
2. **Example workflows covered:** minimal single-run script, configurable detector run, plotting, regime-duration analysis, forward behavior analysis, event study, multi-symbol processing, output persistence, and notebook iteration.
3. **Assumptions made about upstream integration:** users access canonical OHLCV bars through `market-data-core` (or a wrapper), then convert to ordered `list[dict]` records containing `open/high/low/close/volume`.
4. **Current gaps / TODOs:** exact `market-data-core` retrieval API examples are intentionally generic, and advanced multi-detector ranking/report generation is not yet part of the baseline package.
