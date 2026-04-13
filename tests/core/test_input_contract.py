import pytest

from market_regime_classification.core.exceptions import DetectorContractError
from market_regime_classification.core.input_contract import validate_detector_input_v1


def _row(ts: str) -> dict[str, object]:
    return {
        "symbol": "SPY",
        "timestamp": ts,
        "open": 100,
        "high": 101,
        "low": 99,
        "close": 100.5,
        "volume": 1000,
    }


def test_validate_detector_input_v1_accepts_valid_rows() -> None:
    rows = [_row("2026-01-01T00:00:00+00:00"), _row("2026-01-02T00:00:00+00:00")]
    out = validate_detector_input_v1(rows)
    assert len(out) == 2


def test_validate_detector_input_v1_rejects_naive_timestamp() -> None:
    with pytest.raises(DetectorContractError, match="timezone-aware"):
        validate_detector_input_v1([_row("2026-01-01T00:00:00")])


def test_validate_detector_input_v1_rejects_non_increasing_timestamp() -> None:
    rows = [_row("2026-01-02T00:00:00+00:00"), _row("2026-01-01T00:00:00+00:00")]
    with pytest.raises(DetectorContractError, match="strictly increasing"):
        validate_detector_input_v1(rows)
