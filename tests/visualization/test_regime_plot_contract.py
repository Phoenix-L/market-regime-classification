import pytest

from market_regime_classification.visualization.regime_plot import plot_wilder_regime


def test_plot_wilder_regime_validates_required_columns() -> None:
    bad_rows = [{"close": 100.0, "adx": 20.0}]
    with pytest.raises(ValueError, match="missing required columns"):
        plot_wilder_regime(bad_rows)


def test_plot_wilder_regime_rejects_non_list_input() -> None:
    with pytest.raises(TypeError, match="expects list"):
        plot_wilder_regime({"close": 1.0})
