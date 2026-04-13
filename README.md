# market-regime-classification

`market-regime-classification` is a research-oriented Python package for defining, running, and comparing **market regime detectors**.

## Current repository reality

This repository already includes:

- Phase 2 baseline: implemented Wilder-style detector.
- Phase 3 baseline: visualization utilities for detector diagnostics.
- Phase 4 baseline: evaluation/comparison utilities.

Current work in this cycle focuses on **Phase 0/1 retrofit alignment**:

- explicit detector input/output contracts,
- strict boundary with `market-data-core`,
- minimal end-to-end detector pipeline definition,
- internal contract consistency improvements.

`market-data-core` is the upstream data foundation and owns:

- provider adapters and data ingestion,
- canonical OHLCV schema,
- validation and normalization,
- calendar/session semantics,
- storage helpers and dataset access.

This repository consumes upstream canonical bars and owns:

- detector definitions and detector-specific calculations,
- regime state labeling and detector outputs,
- visualization and evaluation of detector outputs.

See `docs/boundary_with_market_data_core.md` for ownership boundaries.

## Core contracts

- Input contract: `docs/input_contract.md`
- Output contract: `docs/output_contract.md`
- Minimal pipeline: `docs/pipeline.md`
- State-machine policy: `docs/state_machine.md`
- Wilder detector reference: `docs/detectors/wilder.md`

## Minimal detector usage

```python
from market_regime_classification.detectors.wilder_style import WilderStyleDetector

bars = load_from_market_data_core(...)  # external upstream call
result = WilderStyleDetector().run(bars)
print(result.detector_name, result.summary)
```

`run(...)` returns `DetectionResult`, the standard artifact consumed by downstream modules.

## Contributor boundary reminder

Do not add local data-provider adapters, market-data fetching utilities, or upstream-style canonicalization/storage helpers in this repository; those belong in `market-data-core`.
