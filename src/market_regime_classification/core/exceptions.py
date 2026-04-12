"""Domain-specific exceptions for regime detector workflows."""


class MarketRegimeError(Exception):
    """Base package exception."""


class DetectorContractError(MarketRegimeError):
    """Raised when detector inputs/outputs violate shared contract expectations."""
