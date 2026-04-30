from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

matplotlib = pytest.importorskip("matplotlib")
matplotlib.use("Agg")

from market_regime_classification.detectors.wilder_style.detector import WilderStyleDetector
from market_regime_classification.visualization.regime_plot import (
    plot_from_detection_result,
    plot_wilder_regime,
)


def _sample_detector_output() -> list[dict[str, float | str]]:
    closes = [100, 101, 102, 103, 102, 101, 100, 99, 100, 101, 102, 103, 104, 105, 104, 103]
    bars = []
    for i, c in enumerate(closes):
        bars.append(
            {
                "symbol": "SPY",
                "timestamp": f"2026-02-{i+1:02d}T00:00:00+00:00",
                "open": c - 0.1,
                "high": c + 0.9,
                "low": c - 0.9,
                "close": c,
                "volume": 1000,
            }
        )
    return WilderStyleDetector().run(bars).bars


def test_plot_wilder_regime_returns_three_axes_and_saves(tmp_path: Path) -> None:
    bars = _sample_detector_output()
    out_path = tmp_path / "wilder_plot.png"

    fig, axes = plot_wilder_regime(bars, title="Wilder", save_path=out_path)

    assert fig is not None
    assert len(axes) == 3
    assert out_path.exists()


def test_plot_from_detection_result_smoke(tmp_path: Path) -> None:
    closes = [100 + i * 0.5 for i in range(40)]
    start = datetime(2026, 3, 1, tzinfo=timezone.utc)
    data = [
        {
            "symbol": "SPY",
            "timestamp": (start + timedelta(days=i)).isoformat(),
            "open": c - 0.2,
            "high": c + 0.8,
            "low": c - 0.8,
            "close": c,
            "volume": 1000,
        }
        for i, c in enumerate(closes)
    ]
    result = WilderStyleDetector().run(data)

    fig, axes = plot_from_detection_result(result, save_path=tmp_path / "from_result.png")
    assert fig is not None
    assert len(axes) == 3
