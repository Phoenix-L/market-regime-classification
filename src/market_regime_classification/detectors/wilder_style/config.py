"""Configuration for the Wilder-style regime detector."""

from dataclasses import dataclass


@dataclass(slots=True)
class WilderStyleConfig:
    """Thresholds and anti-flip settings for the baseline Wilder detector."""

    wilder_length: int = 14
    adx_trend_enter: float = 25.0
    adx_trend_exit: float = 20.0
    adx_osc_enter: float = 16.0
    di_gap_trend_enter: float = 12.0
    di_gap_trend_exit: float = 8.0
    di_gap_osc_max: float = 6.0
    dominance_run_trend_min: int = 3
    recent_cross_window: int = 8
    recent_cross_osc_min: int = 2
    trend_confirm_bars: int = 3
    osc_confirm_bars: int = 3
    transition_trigger_count: int = 2

    def validate(self) -> None:
        if self.wilder_length < 2:
            raise ValueError("wilder_length must be >= 2")
        if self.trend_confirm_bars < 1 or self.osc_confirm_bars < 1:
            raise ValueError("confirm bars must be >= 1")
        if self.transition_trigger_count < 1:
            raise ValueError("transition_trigger_count must be >= 1")
        if self.recent_cross_window < 1:
            raise ValueError("recent_cross_window must be >= 1")
        if self.adx_trend_enter < self.adx_trend_exit:
            raise ValueError("adx_trend_enter must be >= adx_trend_exit")
        if self.di_gap_trend_enter < self.di_gap_trend_exit:
            raise ValueError("di_gap_trend_enter must be >= di_gap_trend_exit")
        if self.di_gap_trend_exit < self.di_gap_osc_max:
            raise ValueError("di_gap_trend_exit should be >= di_gap_osc_max")
