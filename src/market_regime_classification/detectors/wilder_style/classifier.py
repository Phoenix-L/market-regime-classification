"""Classifier and state machine for Wilder-style regime detection."""

from dataclasses import dataclass
from typing import Any

from ...core.enums import RegimeDirection, RegimeState
from .config import WilderStyleConfig


@dataclass(slots=True)
class _MachineState:
    confirmed: RegimeState = RegimeState.TRANSITION
    age: int = 0
    target: RegimeState | None = None
    target_streak: int = 0


def _raw_proposal(row: dict[str, Any], cfg: WilderStyleConfig) -> RegimeState:
    adx = row.get("adx")
    adx_slope = row.get("adx_slope")
    di_gap = row.get("di_gap")
    dominance_run = row.get("di_dominance_run", 0)
    cross_count = row.get("recent_di_cross_count", 0)

    trend_evidence = 0
    if isinstance(adx, (int, float)) and adx >= cfg.adx_trend_enter:
        trend_evidence += 1
    if isinstance(di_gap, (int, float)) and di_gap >= cfg.di_gap_trend_enter:
        trend_evidence += 1
    if isinstance(dominance_run, int) and dominance_run >= cfg.dominance_run_trend_min:
        trend_evidence += 1
    if isinstance(adx_slope, (int, float)) and adx_slope > 0:
        trend_evidence += 1

    osc_evidence = 0
    if isinstance(adx, (int, float)) and adx <= cfg.adx_osc_enter:
        osc_evidence += 1
    if isinstance(di_gap, (int, float)) and di_gap <= cfg.di_gap_osc_max:
        osc_evidence += 1
    if isinstance(cross_count, int) and cross_count >= cfg.recent_cross_osc_min:
        osc_evidence += 1

    if trend_evidence >= cfg.transition_trigger_count:
        return RegimeState.TRENDING
    if osc_evidence >= cfg.transition_trigger_count:
        return RegimeState.OSCILLATING
    return RegimeState.TRANSITION


def _direction_from_side(side: str) -> RegimeDirection:
    if side == "up":
        return RegimeDirection.UP
    if side == "down":
        return RegimeDirection.DOWN
    return RegimeDirection.NONE


def classify_wilder_states(rows: list[dict[str, Any]], cfg: WilderStyleConfig) -> list[dict[str, Any]]:
    """Attach raw/confirmed regime labels using transition-bridge confirmation."""
    machine = _MachineState()

    for row in rows:
        raw = _raw_proposal(row, cfg)
        reason: str | None = None

        if machine.age == 0:
            machine.confirmed = raw
            machine.age = 1
        elif raw == machine.confirmed:
            machine.age += 1
            machine.target = None
            machine.target_streak = 0
        else:
            if machine.confirmed in {RegimeState.OSCILLATING, RegimeState.TRENDING} and raw in {
                RegimeState.OSCILLATING,
                RegimeState.TRENDING,
            }:
                machine.confirmed = RegimeState.TRANSITION
                machine.age = 1
                machine.target = raw
                machine.target_streak = 1
                reason = "transition_bridge"
            elif machine.confirmed == RegimeState.TRANSITION and raw in {
                RegimeState.OSCILLATING,
                RegimeState.TRENDING,
            }:
                if machine.target == raw:
                    machine.target_streak += 1
                else:
                    machine.target = raw
                    machine.target_streak = 1

                confirm_bars = (
                    cfg.trend_confirm_bars if raw == RegimeState.TRENDING else cfg.osc_confirm_bars
                )
                if machine.target_streak >= confirm_bars:
                    machine.confirmed = raw
                    machine.age = 1
                    machine.target = None
                    machine.target_streak = 0
                    reason = "confirmed"
                else:
                    machine.age += 1
                    reason = "await_confirmation"
            else:
                machine.confirmed = RegimeState.TRANSITION
                machine.age = 1
                machine.target = raw if raw != RegimeState.TRANSITION else None
                machine.target_streak = 1 if machine.target else 0
                reason = "enter_transition"

        row["regime_raw"] = raw.value
        row["regime_final"] = machine.confirmed.value
        row["regime_direction"] = _direction_from_side(row.get("di_dominant_side", "none")).value
        row["transition_reason"] = reason
        row["state_age"] = machine.age

    return rows
