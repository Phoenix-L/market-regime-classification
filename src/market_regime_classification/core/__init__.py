"""Core contracts and shared regime types."""

from .detector_base import BaseRegimeDetector
from .enums import RegimeDirection, RegimeState
from .result import DetectionResult

__all__ = [
    "BaseRegimeDetector",
    "RegimeDirection",
    "RegimeState",
    "DetectionResult",
]
