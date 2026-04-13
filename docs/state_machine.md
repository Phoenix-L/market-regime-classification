# State Machine Policy

## Decision

This repository adopts **Option B**:

- `core.state_machine` is the default shared mechanism for detectors.
- Detector-specific state-machine logic is allowed only when explicitly justified and documented.

## Current status

- `core.state_machine` remains the shared generic confirmer utility.
- The Wilder-style detector currently uses detector-local transition logic because it encodes a domain-specific transition-bridge policy (`oscillating/trending` flips pass through `transition` with confirmation rules).

## Guardrails

1. Detector-local state logic must document why generic state machine behavior is insufficient.
2. Required output fields (`regime_raw`, `regime_final`, `regime_direction`, `state_age`) remain mandatory regardless of implementation detail.
3. Cross-detector comparability is enforced at output contract level, not by forcing identical internals.
