from __future__ import annotations

import json
import signal
import subprocess
import sys
import time
import traceback
from collections import Counter
from pathlib import Path
from typing import Any, Callable


ROOT = Path("/home/ht/projects")
MDC = ROOT / "market-data-core"
MRC = ROOT / "market-regime-classification"
ARTIFACTS = MRC / "artifacts"
REPORT = ARTIFACTS / "integration_due_diligence_report.md"
PYTHON = ROOT / ".venvs" / "market-stack" / "bin" / "python"

SYMBOL = "002850.SZ"
START = "2025-11-03"
END = "2026-04-10"
PROVIDER = "baostock"
EXPECTED_30M_ANCHORS = ["09:30", "10:00", "10:30", "11:00", "13:00", "13:30", "14:00", "14:30"]
DELETED_STALE_CACHE_FILES = [
    "/home/ht/projects/market-regime-classification/.data/market_data/baostock/002850.SZ/30m/2025-11-03_2026-04-10.parquet"
]


def run_cmd(cmd: list[str], cwd: Path) -> dict[str, Any]:
    proc = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    return {
        "cmd": " ".join(cmd),
        "cwd": str(cwd),
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
    }


def compact_exception(exc: BaseException) -> dict[str, str]:
    return {
        "type": type(exc).__name__,
        "message": str(exc),
        "traceback_tail": "".join(traceback.format_exception(type(exc), exc, exc.__traceback__)[-4:]).strip(),
    }


def fenced(value: Any, lang: str = "json") -> str:
    if isinstance(value, str):
        text = value
        lang = "" if lang == "json" else lang
    else:
        text = json.dumps(value, indent=2, default=str, ensure_ascii=False)
    return f"```{lang}\n{text.strip()}\n```"


def df_summary(df: Any) -> dict[str, Any]:
    return {
        "shape": list(df.shape),
        "head": df.head(3).to_dict(orient="records"),
        "tail": df.tail(3).to_dict(orient="records"),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
    }


def validation_summary(report: Any) -> dict[str, Any]:
    return {
        "ok": getattr(report, "ok", None),
        "errors": list(getattr(report, "errors", []) or []),
        "warnings": list(getattr(report, "warnings", []) or []),
        "stats": dict(getattr(report, "stats", {}) or {}),
    }


def timestamp_anchors(df: Any) -> list[str]:
    return sorted({ts.strftime("%H:%M") for ts in df["timestamp"]})


def turnover_status(df: Any) -> str:
    if "turnover_rate" not in df.columns:
        return "turnover_rate column absent"
    nulls = int(df["turnover_rate"].isna().sum())
    negatives = int((df["turnover_rate"].dropna() < 0).sum())
    return f"present; null_count={nulls}; negative_count={negatives}"


def is_retryable_provider_failure(exc: BaseException) -> bool:
    try:
        from market_data_core.core.exceptions import ProviderError
    except Exception:
        ProviderError = Exception  # type: ignore
    return isinstance(exc, ProviderError)


def _parse_child_result(stdout: str) -> dict[str, Any] | None:
    for line in reversed(stdout.splitlines()):
        if line.startswith("RESULT_JSON="):
            return json.loads(line.removeprefix("RESULT_JSON="))
    return None


def retry_load_bars_subprocess(
    label: str,
    *,
    frequency: str,
    use_cache: bool,
    output_path: Path,
    attempts: int = 3,
    wait_seconds: int = 3,
    timeout_seconds: int = 20,
) -> tuple[Any | None, list[dict[str, Any]]]:
    import pandas as pd

    code = f"""
import json
import traceback
from pathlib import Path
from market_data_core.access import load_bars

out = Path({str(output_path)!r})
try:
    df = load_bars(
        symbol={SYMBOL!r},
        start={START!r},
        end={END!r},
        frequency={frequency!r},
        provider={PROVIDER!r},
        use_cache={use_cache!r},
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out, index=False)
    print("RESULT_JSON=" + json.dumps({{"success": True, "shape": list(df.shape), "output_path": str(out)}}))
except Exception as exc:
    print("RESULT_JSON=" + json.dumps({{
        "success": False,
        "error": {{
            "type": type(exc).__name__,
            "message": str(exc),
            "traceback_tail": "".join(traceback.format_exception(type(exc), exc, exc.__traceback__)[-4:]).strip(),
        }},
    }}, ensure_ascii=False))
    raise SystemExit(1)
"""
    log: list[dict[str, Any]] = []
    for attempt in range(1, attempts + 1):
        try:
            proc = subprocess.run(
                ["timeout", f"{timeout_seconds}s", str(PYTHON), "-c", code],
                cwd=MRC,
                text=True,
                capture_output=True,
            )
        except Exception as exc:
            log.append({"label": label, "attempt": attempt, "success": False, "retryable": False, "error": compact_exception(exc)})
            return None, log

        parsed = _parse_child_result(proc.stdout)
        if proc.returncode == 0 and parsed and parsed.get("success"):
            log.append({"label": label, "attempt": attempt, "success": True, "shape": parsed.get("shape")})
            return pd.read_parquet(output_path), log

        if proc.returncode == 124:
            error = {"type": "TimeoutExpired", "message": f"child load exceeded {timeout_seconds}s"}
            retryable = True
        else:
            error = (parsed or {}).get("error") or {"type": "UnknownChildFailure", "message": proc.stderr or proc.stdout}
            retryable = error.get("type") == "ProviderError"
        log.append(
            {
                "label": label,
                "attempt": attempt,
                "success": False,
                "retryable": retryable,
                "error": error,
                "stdout": proc.stdout.strip(),
                "stderr": proc.stderr.strip(),
            }
        )
        if not retryable or attempt == attempts:
            return None, log
        time.sleep(wait_seconds)
    return None, log


class AttemptTimeout(TimeoutError):
    pass


def _timeout_handler(_signum: int, _frame: Any) -> None:
    raise AttemptTimeout("live provider call exceeded per-attempt timeout")


def retry_live_load(
    label: str,
    loader: Callable[[], Any],
    attempts: int = 3,
    wait_seconds: int = 3,
    timeout_seconds: int = 30,
) -> tuple[Any | None, list[dict[str, Any]]]:
    log: list[dict[str, Any]] = []
    for attempt in range(1, attempts + 1):
        previous_handler = signal.signal(signal.SIGALRM, _timeout_handler)
        signal.alarm(timeout_seconds)
        try:
            df = loader()
            signal.alarm(0)
            log.append({"label": label, "attempt": attempt, "success": True, "shape": list(df.shape)})
            return df, log
        except Exception as exc:
            signal.alarm(0)
            retryable = isinstance(exc, AttemptTimeout) or is_retryable_provider_failure(exc)
            log.append({"label": label, "attempt": attempt, "success": False, "retryable": retryable, "error": compact_exception(exc)})
            if not retryable or attempt == attempts:
                return None, log
            time.sleep(wait_seconds)
        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, previous_handler)
    return None, log


def compare_frames(fresh: Any, cached: Any) -> dict[str, Any]:
    left = fresh.reset_index(drop=True)
    right = cached.reset_index(drop=True)
    common = sorted(set(left.columns) & set(right.columns))
    dtype_differences = {
        col: {"fresh": str(left[col].dtype), "cached": str(right[col].dtype)}
        for col in common
        if str(left[col].dtype) != str(right[col].dtype)
    }
    value_difference_columns = [col for col in common if not left[col].equals(right[col])]
    return {
        "shape_matches": left.shape == right.shape,
        "timestamps_match": "timestamp" in common and left["timestamp"].equals(right["timestamp"]),
        "full_dataframe_equals": left.equals(right),
        "dtype_differences": dtype_differences,
        "value_difference_columns": value_difference_columns,
        "fresh_columns": list(left.columns),
        "cached_columns": list(right.columns),
    }


def main() -> int:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    results: dict[str, Any] = {}
    retry_log: list[dict[str, Any]] = []

    results["repo_status"] = {
        "market-data-core_status": run_cmd(["git", "status", "--short"], MDC),
        "market-data-core_log": run_cmd(["git", "log", "--oneline", "-n", "5"], MDC),
        "market-regime-classification_status": run_cmd(["git", "status", "--short"], MRC),
        "market-regime-classification_log": run_cmd(["git", "log", "--oneline", "-n", "5"], MRC),
    }
    results["tests"] = {
        "market-data-core": run_cmd([str(PYTHON), "-m", "pytest", "-q"], MDC),
        "market-regime-classification": run_cmd([str(PYTHON), "-m", "pytest", "-q"], MRC),
    }

    try:
        import market_data_core
        import market_regime_classification
        from market_data_core.storage import CACHE_CONTRACT_VERSION
        from market_data_core.storage.parquet_store import cache_file_path

        results["environment"] = {
            "sys_executable": sys.executable,
            "expected_python": str(PYTHON),
            "market_data_core_file": market_data_core.__file__,
            "market_regime_classification_file": market_regime_classification.__file__,
            "cache_contract_version": CACHE_CONTRACT_VERSION,
            "active_30m_cache_path": str(cache_file_path(PROVIDER, SYMBOL, "30m", START, END)),
        }
    except Exception as exc:
        results["environment"] = {"error": compact_exception(exc)}

    daily_df = None
    fresh_30m_df = None
    cached_30m_df = None
    detection_result = None

    try:
        from market_data_core.access import load_bars
        from market_data_core.validation import validate_bars

        daily_df, log = retry_load_bars_subprocess(
            "daily use_cache=False",
            frequency="1d",
            use_cache=False,
            output_path=ARTIFACTS / "tmp_daily_load.parquet",
        )
        retry_log.extend(log)
        if daily_df is None:
            raise RuntimeError("daily live load failed after retry budget")
        report = validate_bars(daily_df, frequency="1d", strict=True)
        results["daily_load"] = {
            "success": True,
            **df_summary(daily_df),
            "validation": validation_summary(report),
            "turnover_rate_status": turnover_status(daily_df),
        }
    except Exception as exc:
        results["daily_load"] = {"success": False, "error": compact_exception(exc)}

    try:
        from market_data_core.access import load_bars
        from market_data_core.validation import validate_bars

        fresh_30m_df, log = retry_load_bars_subprocess(
            "30m use_cache=False",
            frequency="30m",
            use_cache=False,
            output_path=ARTIFACTS / "tmp_30m_fresh.parquet",
        )
        retry_log.extend(log)
        if fresh_30m_df is None:
            raise RuntimeError("30m fresh live load failed after retry budget")
        report = validate_bars(fresh_30m_df, frequency="30m", strict=True)
        anchors = timestamp_anchors(fresh_30m_df)
        results["fresh_30m_load"] = {
            "success": True,
            **df_summary(fresh_30m_df),
            "validation": validation_summary(report),
            "unique_timestamp_clock_anchors": anchors,
            "expected_timestamp_clock_anchors": EXPECTED_30M_ANCHORS,
            "anchors_match_expected": anchors == EXPECTED_30M_ANCHORS,
        }
    except Exception as exc:
        results["fresh_30m_load"] = {"success": False, "error": compact_exception(exc)}

    try:
        from market_data_core.access import load_bars
        from market_data_core.storage.parquet_store import cache_file_path
        from market_data_core.validation import validate_bars

        cache_path = cache_file_path(PROVIDER, SYMBOL, "30m", START, END)
        cache_existed_before = cache_path.exists()
        populate_df, log = retry_load_bars_subprocess(
            "30m use_cache=True populate",
            frequency="30m",
            use_cache=True,
            output_path=ARTIFACTS / "tmp_30m_cache_populate.parquet",
        )
        retry_log.extend(log)
        if populate_df is None:
            raise RuntimeError("30m cache populate load failed after retry budget")
        cached_30m_df = load_bars(SYMBOL, START, END, frequency="30m", provider=PROVIDER, use_cache=True)
        report = validate_bars(cached_30m_df, frequency="30m", strict=True)
        comparison = compare_frames(fresh_30m_df, cached_30m_df) if fresh_30m_df is not None else {}
        results["cache_roundtrip"] = {
            "success": True,
            "cache_path": str(cache_path),
            "cache_existed_before": cache_existed_before,
            "cache_exists_after": cache_path.exists(),
            "validation": validation_summary(report),
            "cached_summary": df_summary(cached_30m_df),
            **comparison,
        }
    except Exception as exc:
        try:
            from market_data_core.storage.parquet_store import cache_file_path

            cache_path_value = str(cache_file_path(PROVIDER, SYMBOL, "30m", START, END))
        except Exception:
            cache_path_value = None
        results["cache_roundtrip"] = {"success": False, "cache_path": cache_path_value, "error": compact_exception(exc)}

    try:
        from market_regime_classification.detectors.wilder_style import WilderStyleDetector

        source_df = fresh_30m_df if fresh_30m_df is not None else cached_30m_df
        if source_df is None:
            raise RuntimeError("No valid 30m DataFrame available for detector handoff")
        bars = source_df[["symbol", "timestamp", "open", "high", "low", "close", "volume"]].to_dict(orient="records")
        detection_result = WilderStyleDetector().run(bars)
        results["detector_handoff"] = {
            "success": True,
            "detector_name": detection_result.detector_name,
            "detector_version": detection_result.detector_version,
            "summary": dict(detection_result.summary),
            "first_two_result_bars": detection_result.bars[:2],
            "last_two_result_bars": detection_result.bars[-2:],
            "result_row_count": len(detection_result.bars),
            "input_row_count": len(bars),
            "row_count_matches_input": len(detection_result.bars) == len(bars),
        }
    except Exception as exc:
        results["detector_handoff"] = {"success": False, "error": compact_exception(exc)}

    try:
        if detection_result is None:
            raise RuntimeError("No detection result available for output contract check")
        required = ["regime_raw", "regime_final", "regime_direction", "state_age"]
        missing_count = sum(any(field not in row for field in required) for row in detection_result.bars)
        results["output_contract"] = {
            "success": True,
            "missing_row_count": missing_count,
            "regime_final_distribution": dict(Counter(str(row.get("regime_final")) for row in detection_result.bars)),
            "regime_direction_distribution": dict(Counter(str(row.get("regime_direction")) for row in detection_result.bars)),
            "valid_adx_count": sum(row.get("adx") is not None for row in detection_result.bars),
            "total_rows": len(detection_result.bars),
        }
    except Exception as exc:
        results["output_contract"] = {"success": False, "error": compact_exception(exc)}

    try:
        import matplotlib

        matplotlib.use("Agg")
        from market_regime_classification.visualization import plot_from_detection_result

        if detection_result is None:
            raise RuntimeError("No detection result available for visualization")
        out = ARTIFACTS / "002850_30m_wilder_smoke.png"
        fig, _axes = plot_from_detection_result(detection_result, save_path=out)
        try:
            import matplotlib.pyplot as plt

            plt.close(fig)
        except Exception:
            pass
        results["visualization"] = {"success": True, "generated_file_path": str(out), "file_size_bytes": out.stat().st_size}
    except Exception as exc:
        results["visualization"] = {"success": False, "error": compact_exception(exc)}

    try:
        from market_regime_classification.evaluation import summarize_regime_durations

        if detection_result is None:
            raise RuntimeError("No detection result available for evaluation")
        results["evaluation"] = {"success": True, "summary_output": summarize_regime_durations(detection_result.bars)}
    except Exception as exc:
        results["evaluation"] = {"success": False, "error": compact_exception(exc)}

    results["retry_log"] = retry_log
    results["stale_cache_cleanup"] = {
        "deleted_paths": DELETED_STALE_CACHE_FILES,
        "confirmation": "Deleted only the confirmed old unversioned close-anchor 30m parquet file for the requested symbol/range.",
    }

    issues: list[str] = []
    if results["tests"]["market-data-core"]["returncode"] != 0:
        issues.append("market-data-core test suite failed.")
    if results["tests"]["market-regime-classification"]["returncode"] != 0:
        issues.append("market-regime-classification test suite failed.")
    if not results.get("daily_load", {}).get("success"):
        issues.append("market-data-core daily live load failed.")
    if not results.get("fresh_30m_load", {}).get("success"):
        issues.append("market-data-core 30m fresh live load failed.")
    elif not results["fresh_30m_load"].get("anchors_match_expected"):
        issues.append("30m anchors did not match canonical open anchors.")
    if not results.get("cache_roundtrip", {}).get("success"):
        issues.append("30m cache roundtrip failed.")
    elif not results["cache_roundtrip"].get("full_dataframe_equals"):
        issues.append("30m cache roundtrip loaded but full DataFrame equality failed.")
    if not results.get("detector_handoff", {}).get("success"):
        issues.append("Wilder detector handoff failed.")
    if not results.get("output_contract", {}).get("success") or results.get("output_contract", {}).get("missing_row_count"):
        issues.append("Detector output contract check failed or found missing rows.")
    if not results.get("visualization", {}).get("success"):
        issues.append("Visualization smoke failed.")
    if not results.get("evaluation", {}).get("success"):
        issues.append("Evaluation smoke failed.")

    recommendations = []
    if results["tests"]["market-regime-classification"]["returncode"] != 0:
        recommendations.append("Fix the existing market-regime-classification visualization test fixture that emits invalid dates after March 31.")
    if not results.get("daily_load", {}).get("success") or not results.get("fresh_30m_load", {}).get("success"):
        recommendations.append("Retry live BaoStock due diligence when vendor connectivity is stable; failures were retried and logged.")
    if not results.get("cache_roundtrip", {}).get("success"):
        recommendations.append("After a successful live 30m fetch, verify the new v2 cache path is populated and then rerun cache roundtrip.")
    if not recommendations:
        recommendations.append("Proceed to notebook-level research play and keep this due diligence smoke as a regression gate.")

    sections = [
        ("Executive summary", "\n".join([
            f"Overall due diligence passed: {'yes' if not issues else 'no'}",
            f"Primary symbol/range/provider: {SYMBOL}, {START} to {END}, {PROVIDER}",
            f"Issues found: {len(issues)}",
        ])),
        ("Invalid-date fixture fix", "\n".join([
            "Fixed `tests/visualization/test_regime_plot.py::test_plot_from_detection_result_smoke`.",
            "Root cause: the fixture generated 40 timestamps using `2026-03-{i+1:02d}`, which produced impossible dates after March 31, e.g. `2026-03-32T00:00:00+00:00`.",
            "Fix: generate timestamps from a timezone-aware `datetime(2026, 3, 1, tzinfo=timezone.utc)` plus `timedelta(days=i)` so the fixture remains ordered, timezone-aware, and otherwise compliant with Detector Input Contract v1.",
        ])),
        ("Phase 6.6 changes made", "\n".join([
            "- Added `CACHE_CONTRACT_VERSION = \"v2\"` in `market_data_core.storage.constants`.",
            "- Updated Cache Mode parquet paths to include the cache contract version.",
            "- Added tests for versioned paths, unversioned cache bypass, canonical 30m cache roundtrip, and stale close-anchor validation failure.",
            "- Documented canonical bar-open timestamp semantics and BaoStock 30m end-anchor normalization.",
            "- Kept `load_bars` and `validate_bars` public signatures unchanged.",
        ])),
        ("Cache contract versioning decision", fenced(results.get("environment"))),
        ("Canonical timestamp convention", "\n".join([
            "Canonical intraday `timestamp` means bar-open timestamp.",
            f"CN A-share 30m valid anchors: {', '.join(EXPECTED_30M_ANCHORS)}.",
            "Provider-specific timestamp conventions are normalized inside `market-data-core`; downstream repos must not apply BaoStock-specific timestamp shifts.",
        ])),
        ("Stale cache cleanup result", fenced(results.get("stale_cache_cleanup"))),
        ("Repository status", fenced(results.get("repo_status"))),
        ("Test suite results", fenced(results.get("tests"))),
        ("market-data-core daily load result", fenced(results.get("daily_load"))),
        ("market-data-core 30m fresh load result", fenced(results.get("fresh_30m_load"))),
        ("BaoStock retry log", fenced(results.get("retry_log"))),
        ("30m timestamp anchor verification", fenced({
            "observed": results.get("fresh_30m_load", {}).get("unique_timestamp_clock_anchors"),
            "expected": EXPECTED_30M_ANCHORS,
            "matches_expected": results.get("fresh_30m_load", {}).get("anchors_match_expected"),
        })),
        ("30m cache roundtrip result", fenced(results.get("cache_roundtrip"))),
        ("market-regime-classification detector handoff result", fenced(results.get("detector_handoff"))),
        ("Detector output contract check", fenced(results.get("output_contract"))),
        ("Visualization smoke result", fenced(results.get("visualization"))),
        ("Evaluation smoke result", fenced(results.get("evaluation"))),
        ("Issues found", "\n".join(f"- {issue}" for issue in issues) if issues else "No issues found in executed checks."),
        ("Recommended next steps", "\n".join(f"- {rec}" for rec in recommendations)),
    ]

    REPORT.write_text("\n\n".join(f"## {title}\n\n{body}" for title, body in sections) + "\n", encoding="utf-8")
    print(json.dumps({"report": str(REPORT), "issues": issues, "recommendations": recommendations}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
