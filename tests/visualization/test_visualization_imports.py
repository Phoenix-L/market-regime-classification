import market_regime_classification.visualization.comparison_plot as comparison_plot
import market_regime_classification.visualization.overlays as overlays
import market_regime_classification.visualization.panes as panes
import market_regime_classification.visualization.regime_plot as regime_plot


def test_visualization_modules_import() -> None:
    assert comparison_plot is not None
    assert overlays is not None
    assert panes is not None
    assert regime_plot is not None
