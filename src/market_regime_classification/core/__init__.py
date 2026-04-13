"""Core contracts and shared types for regime detectors."""

from .detector_base import BaseRegimeDetector
from .enums import RegimeDirection, RegimeState
from .exceptions import DetectorContractError, MarketRegimeError
from .input_contract import OPTIONAL_INPUT_COLUMNS, REQUIRED_INPUT_COLUMNS, validate_detector_input_v1
from .output_contract import OPTIONAL_OUTPUT_COLUMNS, REQUIRED_OUTPUT_COLUMNS, validate_detector_output_v1
from .result import DetectionResult
from .state_machine import StateMachine, StateMachineConfig

__all__ = [
    "BaseRegimeDetector",
    "DetectionResult",
    "RegimeState",
    "RegimeDirection",
    "StateMachine",
    "StateMachineConfig",
    "MarketRegimeError",
    "DetectorContractError",
    "REQUIRED_INPUT_COLUMNS",
    "OPTIONAL_INPUT_COLUMNS",
    "validate_detector_input_v1",
    "REQUIRED_OUTPUT_COLUMNS",
    "OPTIONAL_OUTPUT_COLUMNS",
    "validate_detector_output_v1",
]
