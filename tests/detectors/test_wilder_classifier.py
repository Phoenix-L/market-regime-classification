from market_regime_classification.detectors.wilder_style.classifier import classify_wilder_states
from market_regime_classification.detectors.wilder_style.config import WilderStyleConfig


def _row(adx: float, gap: float, run: int, crosses: int, side: str, slope: float = 0.5):
    return {
        "adx": adx,
        "adx_slope": slope,
        "di_gap": gap,
        "di_dominance_run": run,
        "recent_di_cross_count": crosses,
        "di_dominant_side": side,
    }


def test_transition_bridge_avoids_direct_flip_between_osc_and_trend() -> None:
    cfg = WilderStyleConfig(trend_confirm_bars=2, osc_confirm_bars=2, transition_trigger_count=2)
    rows = [
        _row(adx=10, gap=2, run=1, crosses=3, side="none", slope=-0.2),
        _row(adx=35, gap=20, run=5, crosses=0, side="up"),
        _row(adx=35, gap=20, run=6, crosses=0, side="up"),
    ]

    out = classify_wilder_states(rows, cfg)
    finals = [r["regime_final"] for r in out]

    assert finals[0] == "oscillating"
    assert finals[1] == "transition"
    assert finals[2] == "trending"


def test_direction_is_assigned_independently_from_structure() -> None:
    cfg = WilderStyleConfig(trend_confirm_bars=1, osc_confirm_bars=1, transition_trigger_count=2)
    rows = [
        _row(adx=30, gap=18, run=4, crosses=0, side="down"),
        _row(adx=32, gap=20, run=5, crosses=0, side="down"),
    ]
    out = classify_wilder_states(rows, cfg)

    assert all(r["regime_direction"] == "down" for r in out)
    assert out[-1]["regime_final"] == "trending"
