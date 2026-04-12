# Repository Structure

```text
market-regime-classification/
├── docs/
├── examples/
├── src/market_regime_classification/
│   ├── cli/
│   ├── core/
│   ├── detectors/
│   │   ├── feature_based/
│   │   └── wilder_style/
│   ├── evaluation/
│   └── visualization/
└── tests/
    ├── core/
    ├── detectors/
    ├── evaluation/
    └── visualization/
```

## Intent by Area

- `core/`: canonical contracts and cross-detector shared types.
- `detectors/`: algorithm-family modules with local sub-components.
- `evaluation/`: metrics and comparison utilities.
- `visualization/`: plotting architecture for diagnosis.
- `examples/`: sample configs and future notebook/script examples.
- `tests/`: lightweight bootstrap/smoke tests only at this phase.
