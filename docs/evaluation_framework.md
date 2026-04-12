# Evaluation Framework

## Goals

Enable consistent evaluation of regime detectors using common output schema and reproducible metrics.

## Core Evaluation Components

- **Regime duration analysis**: distribution of consecutive state lengths.
- **Transition statistics**: frequency and type of state changes.
- **Forward behavior analysis**: post-state-entry return/volatility profiles.
- **Snapback vs continuation**: probability of reversal vs persistence after transitions.

## Detector Comparison Principles

- Compare on identical input datasets/windows.
- Use shared schema fields for apples-to-apples metrics.
- Separate structural-state performance from directional calls.
- Preserve detector-specific diagnostics as secondary context.

## In-Scope for This Repo

- Regime-focused analytics and detector comparisons.
- Study artifacts for research notebooks/reports.

## Out-of-Scope for This Repo

- Portfolio construction attribution.
- Execution slippage modeling.
- Broker or order-routing analysis.

## Bootstrap Status

Current modules are placeholders that define intended function signatures and TODOs for Phase 4 implementation.
