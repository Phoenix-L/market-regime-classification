"""Detector input contract validation helpers.

This module enforces only detector-entry preconditions for already curated upstream
market data. It intentionally does not fetch, clean, or canonicalize data.
"""

from datetime import datetime
import math
from typing import Any, Mapping

from .exceptions import DetectorContractError

REQUIRED_INPUT_COLUMNS: tuple[str, ...] = (
    "symbol",
    "timestamp",
    "open",
    "high",
    "low",
    "close",
    "volume",
)
OPTIONAL_INPUT_COLUMNS: tuple[str, ...] = ("turnover_rate",)
_NUMERIC_COLUMNS: tuple[str, ...] = ("open", "high", "low", "close", "volume")


def _coerce_timestamp(value: Any) -> datetime:
    if isinstance(value, datetime):
        ts = value
    elif isinstance(value, str):
        candidate = value.replace("Z", "+00:00") if value.endswith("Z") else value
        try:
            ts = datetime.fromisoformat(candidate)
        except ValueError as exc:
            raise DetectorContractError("timestamp must be ISO-8601 parseable") from exc
    else:
        raise DetectorContractError("timestamp must be datetime or ISO-8601 string")

    if ts.tzinfo is None or ts.utcoffset() is None:
        raise DetectorContractError("timestamp must be timezone-aware")
    return ts


def validate_detector_input_v1(data: Any) -> list[dict[str, Any]]:
    """Validate detector input against Input Contract v1.

    Returns a shallow-copied list of rows for detector usage.
    """
    if not isinstance(data, list):
        raise DetectorContractError("detector input must be list[Mapping]")
    if not data:
        raise DetectorContractError("detector input must be non-empty")

    rows: list[dict[str, Any]] = []
    seen: set[tuple[str, datetime]] = set()
    prev_ts: datetime | None = None
    series_symbol: str | None = None

    for i, row in enumerate(data):
        if not isinstance(row, Mapping):
            raise DetectorContractError(f"row {i} must be Mapping")

        row_dict = dict(row)
        missing = [col for col in REQUIRED_INPUT_COLUMNS if col not in row_dict]
        if missing:
            raise DetectorContractError(f"row {i} missing required columns: {missing}")

        ts = _coerce_timestamp(row_dict["timestamp"])

        symbol = str(row_dict["symbol"])
        if series_symbol is None:
            series_symbol = symbol
        elif symbol != series_symbol:
            raise DetectorContractError("input must be a single symbol ordered series")

        key = (symbol, ts)
        if key in seen:
            raise DetectorContractError("(symbol, timestamp) must be unique")
        if prev_ts is not None and ts <= prev_ts:
            raise DetectorContractError("timestamps must be strictly increasing")
        seen.add(key)

        for col in _NUMERIC_COLUMNS:
            try:
                value = float(row_dict[col])
            except (TypeError, ValueError) as exc:
                raise DetectorContractError(f"row {i} column '{col}' must be castable to numeric") from exc
            if not math.isfinite(value):
                raise DetectorContractError(f"row {i} column '{col}' must be finite numeric")

        rows.append(row_dict)
        prev_ts = ts

    return rows
