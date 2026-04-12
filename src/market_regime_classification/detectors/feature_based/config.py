"""Feature-based detector config placeholders."""

from dataclasses import dataclass, field


@dataclass(slots=True)
class FeatureBasedConfig:
    """Configuration scaffold for a later feature-based detector family."""

    feature_set: list[str] = field(default_factory=list)
    lookback_bars: int = 50
    min_dwell_bars: int = 3
