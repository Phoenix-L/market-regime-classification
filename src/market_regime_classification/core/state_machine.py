"""Shared state-machine scaffolding for raw-to-confirmed regime transitions."""

from dataclasses import dataclass

from .enums import RegimeState


@dataclass(slots=True)
class StateMachineConfig:
    """Generic anti-flip controls; detector families may extend these."""

    min_dwell_bars: int = 3
    hysteresis_bars: int = 1


class StateMachine:
    """Minimal state confirmer.

    This is intentionally lightweight in bootstrap phase and should evolve when
    detector implementations are added.
    """

    def __init__(self, config: StateMachineConfig | None = None) -> None:
        self.config = config or StateMachineConfig()
        self._confirmed_state: RegimeState | None = None
        self._state_age = 0

    def step(self, proposed_state: RegimeState) -> tuple[RegimeState, int]:
        """Confirm proposed state with minimal anti-flip gating."""
        if self._confirmed_state is None:
            self._confirmed_state = proposed_state
            self._state_age = 1
            return self._confirmed_state, self._state_age

        if proposed_state == self._confirmed_state:
            self._state_age += 1
            return self._confirmed_state, self._state_age

        if self._state_age >= self.config.min_dwell_bars:
            self._confirmed_state = proposed_state
            self._state_age = 1
        else:
            self._state_age += 1

        return self._confirmed_state, self._state_age
