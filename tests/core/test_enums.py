from market_regime_classification.core.enums import RegimeDirection, RegimeState


def test_regime_state_values() -> None:
    assert RegimeState.OSCILLATING.value == "oscillating"
    assert RegimeState.TRANSITION.value == "transition"
    assert RegimeState.TRENDING.value == "trending"


def test_regime_direction_values() -> None:
    assert RegimeDirection.UP.value == "up"
    assert RegimeDirection.DOWN.value == "down"
    assert RegimeDirection.NONE.value == "none"
