from market_regime_classification.core.enums import RegimeState
from market_regime_classification.core.state_machine import StateMachine, StateMachineConfig


def test_state_machine_requires_min_dwell_before_flip() -> None:
    sm = StateMachine(StateMachineConfig(min_dwell_bars=3))

    state, age = sm.step(RegimeState.OSCILLATING)
    assert (state, age) == (RegimeState.OSCILLATING, 1)

    state, age = sm.step(RegimeState.TRENDING)
    assert (state, age) == (RegimeState.OSCILLATING, 2)

    state, age = sm.step(RegimeState.TRENDING)
    assert (state, age) == (RegimeState.OSCILLATING, 3)

    state, age = sm.step(RegimeState.TRENDING)
    assert (state, age) == (RegimeState.TRENDING, 1)
