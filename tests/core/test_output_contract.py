import pytest

from market_regime_classification.core.exceptions import DetectorContractError
from market_regime_classification.core.output_contract import validate_detector_output_v1


def test_validate_detector_output_v1_rejects_missing_required_field() -> None:
    rows = [
        {
            "regime_raw": "transition",
            "regime_final": "transition",
            "regime_direction": "none",
            # state_age intentionally missing
        }
    ]
    with pytest.raises(DetectorContractError, match="missing required columns"):
        validate_detector_output_v1(rows)
