# Detector Input Contract v1

This document is the single source of truth for detector input preconditions in `market-regime-classification`.

## Scope

This contract applies at detector entry only. It validates upstream payload shape before detector-specific calculations.

It does **not** perform upstream responsibilities such as provider access, canonicalization, data cleaning, or storage.

## Required columns

- `symbol`
- `timestamp`
- `open`
- `high`
- `low`
- `close`
- `volume`

## Optional columns

- `turnover_rate`

## Rules

1. Input must be non-empty `list[Mapping]`.
2. `timestamp` must be timezone-aware (`datetime` with tzinfo or parseable ISO-8601 string with timezone offset).
3. Rows must be strictly ordered by `timestamp` ascending.
4. `(symbol, timestamp)` must be unique.
5. Numeric detector inputs (`open`, `high`, `low`, `close`, `volume`) must be castable to numeric.
6. Expected timezone convention must align with upstream `market-data-core` contract.

## Runtime enforcement

- Enforced by `core.input_contract.validate_detector_input_v1`.
- Validation is intentionally lightweight and fail-fast.
- No local fallback cleaning/transformation is performed here.
