"""Shared config scaffolding for detector runs."""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class RunContext:
    """Optional run metadata to preserve provenance for research workflows."""

    symbol: str | None = None
    timeframe: str | None = None
    source_dataset: str | None = None
    notes: dict[str, Any] = field(default_factory=dict)
