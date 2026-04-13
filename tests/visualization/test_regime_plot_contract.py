import pytest

from market_regime_classification.visualization.regime_plot import plot_from_detection_result, plot_wilder_regime


def test_plot_wilder_regime_validates_required_columns() -> None:
    bad_rows = [{"close": 100.0, "adx": 20.0}]
    with pytest.raises(ValueError, match="missing required columns"):
        plot_wilder_regime(bad_rows)


def test_plot_wilder_regime_validates_required_columns_across_all_rows() -> None:
    bad_rows = [
        {
            "close": 100.0,
            "adx": 20.0,
            "di_plus": 15.0,
            "di_minus": 12.0,
            "regime_final": "transition",
            "regime_direction": "none",
        },
        {
            "close": 101.0,
            "adx": 21.0,
            "di_plus": 16.0,
            # di_minus missing intentionally on second row
            "regime_final": "transition",
            "regime_direction": "none",
        },
    ]
    with pytest.raises(ValueError, match="row 1"):
        plot_wilder_regime(bad_rows)


def test_plot_wilder_regime_rejects_non_list_input() -> None:
    with pytest.raises(TypeError, match="expects list"):
        plot_wilder_regime({"close": 1.0})


def test_plot_wilder_regime_rejects_invalid_regime_direction() -> None:
    bad_rows = [
        {
            "close": 100.0,
            "adx": 20.0,
            "di_plus": 15.0,
            "di_minus": 12.0,
            "regime_final": "transition",
            "regime_direction": "sideways",
        }
    ]
    with pytest.raises(ValueError, match="Invalid regime_direction"):
        plot_wilder_regime(bad_rows)


def test_plot_from_detection_result_requires_bars_attribute() -> None:
    class NoBars:
        detector_name = "x"

    with pytest.raises(TypeError, match="must provide .bars"):
        plot_from_detection_result(NoBars())
