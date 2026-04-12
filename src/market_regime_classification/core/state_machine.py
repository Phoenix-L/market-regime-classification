"""Shared state-machine scaffolding for raw-to-confirmed regime transitions."""

from dataclasses import dataclass
from typing import Optional

from .enums import RegimeState


@dataclass(slots=True)
class StateMachineConfig:
    """Generic anti-flip controls; detector families may extend these."""

    min_dwell_bars: int = 3
    hysteresis_bars: int = 1


class StateMachine:
    """Generic confirmer with dwell and simple proposal streak gating."""

    def __init__(self, config: StateMachineConfig | None = None) -> None:
        self.config = config or StateMachineConfig()
        self._confirmed_state: RegimeState | None = None
        self._state_age = 0
        self._proposal_state: Optional[RegimeState] = None
        self._proposal_streak = 0

    def step(self, proposed_state: RegimeState) -> tuple[RegimeState, int]:
        """Confirm a proposed state with anti-flip controls.

        Rules:
        - First bar initializes confirmed state.
        - Matching proposals increment confirmed state age.
        - Conflicting proposals must repeat for ``hysteresis_bars + 1`` bars.
        - Confirmed state is only eligible to flip once ``min_dwell_bars`` reached.
        """
        if self._confirmed_state is None:
            self._confirmed_state = proposed_state
            self._state_age = 1
            self._proposal_state = None
            self._proposal_streak = 0
            return self._confirmed_state, self._state_age

        if proposed_state == self._confirmed_state:
            self._state_age += 1
            self._proposal_state = None
            self._proposal_streak = 0
            return self._confirmed_state, self._state_age

        if proposed_state == self._proposal_state:
            self._proposal_streak += 1
        else:
            self._proposal_state = proposed_state
            self._proposal_streak = 1

        hold_period_done = self._state_age >= self.config.min_dwell_bars
        hysteresis_done = self._proposal_streak > self.config.hysteresis_bars

        if hold_period_done and hysteresis_done:
            self._confirmed_state = proposed_state
            self._state_age = 1
            self._proposal_state = None
            self._proposal_streak = 0
        else:
            self._state_age += 1

        return self._confirmed_state, self._state_age
