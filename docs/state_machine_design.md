# State Machine Design

## Core 3-State Model

- **Oscillating**: range-bound/choppy structure.
- **Transition**: unstable handoff between dominant structures.
- **Trending**: directional persistence and structural continuation.

## Raw Proposal vs Confirmed State

1. Detector computes a raw proposed state per bar.
2. State machine applies confirmation rules.
3. Confirmed state is emitted for downstream labeling/evaluation.

## Anti-Flip Mechanisms

First-pass concepts:
- Minimum dwell bars before permitting reversal.
- Hysteresis thresholds for state exits.
- Optional transition buffer bars.

Exact thresholds are detector-configurable and should be surfaced in config snapshots.

## Dwell Time and Hysteresis

- Dwell time reduces rapid oscillation due to noise.
- Hysteresis uses asymmetric enter/exit evidence to improve state stability.

## Transition Reasoning

A textual or categorical `transition_reason` can record why a state changed (e.g., evidence threshold breach, timeout, volatility shock).

## Plug-In Philosophy for Detector Evidence

Different detector families may use different evidence (trend strength, volatility context, feature model scores), but all should map into this common state-machine confirmation philosophy.
