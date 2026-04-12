"""Base interface for all regime detector families."""

from abc import ABC, abstractmethod
from typing import Any, Mapping

from .result import DetectionResult


class BaseRegimeDetector(ABC):
    """Abstract detector contract.

    Notes
    -----
    Input ``data`` is expected to come from `market-data-core` curated outputs.
    This package intentionally does not define provider/storage APIs.
    """

    name: str
    version: str

    @abstractmethod
    def run(self, data: Any, config: Mapping[str, Any] | None = None) -> DetectionResult:
        """Run detector on upstream-provided bar data."""
        raise NotImplementedError
