from market_regime_classification.detectors.wilder_style.signals import compute_wilder_signals


def _bars_from_close(closes: list[float]) -> list[dict[str, float]]:
    bars = []
    for i, c in enumerate(closes):
        bars.append(
            {
                "ts": f"2026-01-{i+1:02d}",
                "open": c,
                "high": c + 1.0,
                "low": c - 1.0,
                "close": c,
                "volume": 1000.0,
            }
        )
    return bars


def test_dm_plus_and_dm_minus_present_on_directional_sequence() -> None:
    bars = _bars_from_close([100, 102, 104, 103, 101, 100, 99])
    out = compute_wilder_signals(bars, wilder_length=3, recent_cross_window=3)

    assert any(row["dm_plus"] > 0 for row in out[1:])
    assert any(row["dm_minus"] > 0 for row in out[1:])
    assert all("adx" in row for row in out)


def test_flat_series_is_stable_and_no_crash() -> None:
    bars = _bars_from_close([100, 100, 100, 100, 100])
    out = compute_wilder_signals(bars, wilder_length=3, recent_cross_window=2)

    assert len(out) == 5
    assert all(row["dm_plus"] == 0 for row in out)
    assert all(row["dm_minus"] == 0 for row in out)
    populated = [row["dx"] for row in out if row["dx"] is not None]
    assert all(value == 0 for value in populated)


def test_short_series_gracefully_returns_none_for_unsmoothed_fields() -> None:
    bars = _bars_from_close([100, 101])
    out = compute_wilder_signals(bars, wilder_length=14, recent_cross_window=3)

    assert out[0]["atr_wilder"] is None
    assert out[1]["adx"] is None
