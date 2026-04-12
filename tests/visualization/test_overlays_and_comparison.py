import pytest

matplotlib = pytest.importorskip("matplotlib")
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from market_regime_classification.visualization.comparison_plot import plot_detector_comparison
from market_regime_classification.visualization.overlays import add_regime_background, add_transition_markers


def test_overlay_helpers_handle_states_and_transitions() -> None:
    fig, ax = plt.subplots()
    x = list(range(6))
    regimes = ["oscillating", "oscillating", "transition", "trending", "trending", "oscillating"]
    directions = ["none", "none", "none", "up", "up", "none"]

    add_regime_background(ax, x, regimes, directions=directions)
    points = add_transition_markers(ax, x, regimes)

    assert points == [2, 3, 5]


def test_comparison_plot_minimal_scaffold() -> None:
    runs = {
        "wilder_a": [{"regime_final": "oscillating"}, {"regime_final": "transition"}],
        "wilder_b": [{"regime_final": "trending"}, {"regime_final": "trending"}],
    }
    fig, axes = plot_detector_comparison(runs)
    assert fig is not None
    assert len(axes) == 2
