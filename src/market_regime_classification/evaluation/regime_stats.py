"""Regime duration and transition statistics for detector outputs."""

from collections import Counter, defaultdict
from statistics import mean, median
from typing import Any


def _validate_rows(rows: list[dict[str, Any]], *, state_col: str = "regime_final") -> None:
    if not isinstance(rows, list):
        raise TypeError("evaluation expects list[dict] rows")
    if not rows:
        raise ValueError("rows cannot be empty")

    for i, row in enumerate(rows):
        if not isinstance(row, dict):
            raise TypeError(f"row {i} must be dict")
        if state_col not in row:
            raise ValueError(f"missing state column '{state_col}' at row {i}")


def segment_state_runs(rows: list[dict[str, Any]], *, state_col: str = "regime_final") -> list[dict[str, Any]]:
    """Segment contiguous runs of a confirmed regime state."""
    _validate_rows(rows, state_col=state_col)

    runs: list[dict[str, Any]] = []
    start = 0
    current = str(rows[0][state_col])
    for i in range(1, len(rows) + 1):
        boundary = i == len(rows) or str(rows[i][state_col]) != current
        if not boundary:
            continue

        end = i - 1
        runs.append({"state": current, "start_idx": start, "end_idx": end, "length": end - start + 1})
        if i < len(rows):
            start = i
            current = str(rows[i][state_col])
    return runs


def summarize_regime_durations(
    rows: list[dict[str, Any]],
    *,
    state_col: str = "regime_final",
    short_run_threshold: int = 2,
) -> dict[str, Any]:
    """Summarize stability statistics from regime label runs."""
    runs = segment_state_runs(rows, state_col=state_col)
    total_bars = len(rows)

    bar_counts: Counter[str] = Counter(str(row[state_col]) for row in rows)
    run_counts: Counter[str] = Counter(run["state"] for run in runs)

    durations_by_state: dict[str, list[int]] = defaultdict(list)
    for run in runs:
        durations_by_state[run["state"]].append(run["length"])

    duration_summary: dict[str, dict[str, float | int]] = {}
    short_lived_run_count = 0
    for state, durations in durations_by_state.items():
        short_lived_run_count += sum(1 for d in durations if d <= short_run_threshold)
        duration_summary[state] = {
            "mean": float(mean(durations)),
            "median": float(median(durations)),
            "max": int(max(durations)),
            "min": int(min(durations)),
            "num_runs": int(len(durations)),
        }

    transition_counts: Counter[tuple[str, str]] = Counter()
    for i in range(1, len(runs)):
        transition_counts[(runs[i - 1]["state"], runs[i]["state"])] += 1

    states = sorted(set(bar_counts.keys()) | {s for pair in transition_counts for s in pair})
    transition_matrix = {
        from_state: {to_state: int(transition_counts.get((from_state, to_state), 0)) for to_state in states}
        for from_state in states
    }

    return {
        "num_bars": total_bars,
        "num_runs": len(runs),
        "bar_count_by_regime": dict(bar_counts),
        "bar_proportion_by_regime": {k: v / total_bars for k, v in bar_counts.items()},
        "run_count_by_regime": dict(run_counts),
        "duration_summary_by_regime": duration_summary,
        "transition_counts": {f"{a}->{b}": int(c) for (a, b), c in transition_counts.items()},
        "transition_matrix": transition_matrix,
        "short_lived_run_count": short_lived_run_count,
        "short_lived_run_frequency": (short_lived_run_count / len(runs)) if runs else 0.0,
        "runs": runs,
    }
