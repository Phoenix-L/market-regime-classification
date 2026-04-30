## Executive summary

Overall due diligence passed: no
Primary symbol/range/provider: 002850.SZ, 2025-11-03 to 2026-04-10, baostock
Issues found: 7

## Invalid-date fixture fix

Fixed `tests/visualization/test_regime_plot.py::test_plot_from_detection_result_smoke`.

Root cause: the fixture generated 40 timestamps using `2026-03-{i+1:02d}`, which produced impossible dates after March 31, e.g. `2026-03-32T00:00:00+00:00`.

Fix: generate timestamps from a timezone-aware `datetime(2026, 3, 1, tzinfo=timezone.utc)` plus `timedelta(days=i)` so the fixture remains ordered, timezone-aware, and otherwise compliant with Detector Input Contract v1.

## Phase 6.6 changes made

- Added `CACHE_CONTRACT_VERSION = "v2"` in `market_data_core.storage.constants`.
- Updated Cache Mode parquet paths to include the cache contract version.
- Added tests for versioned paths, unversioned cache bypass, canonical 30m cache roundtrip, and stale close-anchor validation failure.
- Documented canonical bar-open timestamp semantics and BaoStock 30m end-anchor normalization.
- Kept `load_bars` and `validate_bars` public signatures unchanged.

## Cache contract versioning decision

```json
{
  "sys_executable": "/home/ht/projects/.venvs/market-stack/bin/python",
  "expected_python": "/home/ht/projects/.venvs/market-stack/bin/python",
  "market_data_core_file": "/home/ht/projects/market-data-core/src/market_data_core/__init__.py",
  "market_regime_classification_file": "/home/ht/projects/market-regime-classification/src/market_regime_classification/__init__.py",
  "cache_contract_version": "v2",
  "active_30m_cache_path": ".data/market_data/v2/baostock/002850.SZ/30m/2025-11-03_2026-04-10.parquet"
}
```

## Canonical timestamp convention

Canonical intraday `timestamp` means bar-open timestamp.
CN A-share 30m valid anchors: 09:30, 10:00, 10:30, 11:00, 13:00, 13:30, 14:00, 14:30.
Provider-specific timestamp conventions are normalized inside `market-data-core`; downstream repos must not apply BaoStock-specific timestamp shifts.

## Stale cache cleanup result

```json
{
  "deleted_paths": [
    "/home/ht/projects/market-regime-classification/.data/market_data/baostock/002850.SZ/30m/2025-11-03_2026-04-10.parquet"
  ],
  "confirmation": "Deleted only the confirmed old unversioned close-anchor 30m parquet file for the requested symbol/range."
}
```

## Repository status

```json
{
  "market-data-core_status": {
    "cmd": "git status --short",
    "cwd": "/home/ht/projects/market-data-core",
    "returncode": 0,
    "stdout": "M README.md\n M docs/consumer_api.md\n M docs/integration_with_market_regime_classification.md\n M docs/storage_layout.md\n M src/market_data_core/storage/__init__.py\n M src/market_data_core/storage/parquet_store.py\n M src/market_data_core/validation/schema_checks.py\n M tests/access/test_load_bars.py\n M tests/storage/test_parquet_store.py\n?? src/market_data_core/storage/constants.py",
    "stderr": ""
  },
  "market-data-core_log": {
    "cmd": "git log --oneline -n 5",
    "cwd": "/home/ht/projects/market-data-core",
    "returncode": 0,
    "stdout": "49c811e Merge pull request #9 from Phoenix-L/codex/inspect-baostock-provider-for-errors\ne88917d Merge branch 'main' into codex/inspect-baostock-provider-for-errors\n9f56db1 Align BaoStock 30m timestamps to open anchors\n41e0a94 Merge pull request #8 from Phoenix-L/codex/inspect-baostock-provider-for-errors\n8b1a13b Fix BaoStock 30m compact timestamp parsing",
    "stderr": ""
  },
  "market-regime-classification_status": {
    "cmd": "git status --short",
    "cwd": "/home/ht/projects/market-regime-classification",
    "returncode": 0,
    "stdout": "M tests/visualization/test_regime_plot.py\n?? .data/\n?? .ipynb_checkpoints/\n?? Untitled.ipynb\n?? artifacts/\n?? examples/.ipynb_checkpoints/\n?? examples/IntegrationSmoke.ipynb\n?? playground.ipynb",
    "stderr": ""
  },
  "market-regime-classification_log": {
    "cmd": "git log --oneline -n 5",
    "cwd": "/home/ht/projects/market-regime-classification",
    "returncode": 0,
    "stdout": "cbde988 Merge pull request #10 from Phoenix-L/codex/prepare-phase-0/1-proposal-for-repo\n21ff5ac Merge branch 'main' into codex/prepare-phase-0/1-proposal-for-repo\n8ec8f21 Phase 4 hardening: enforce evaluation consistency and deterministic summaries\nb01d0ea Merge pull request #9 from Phoenix-L/codex/prepare-phase-0/1-proposal-for-repo\nd8ce6f3 Merge branch 'main' into codex/prepare-phase-0/1-proposal-for-repo",
    "stderr": ""
  }
}
```

## Test suite results

```json
{
  "market-data-core": {
    "cmd": "/home/ht/projects/.venvs/market-stack/bin/python -m pytest -q",
    "cwd": "/home/ht/projects/market-data-core",
    "returncode": 0,
    "stdout": ".......................s..........................                       [100%]\n49 passed, 1 skipped in 0.72s",
    "stderr": ""
  },
  "market-regime-classification": {
    "cmd": "/home/ht/projects/.venvs/market-stack/bin/python -m pytest -q",
    "cwd": "/home/ht/projects/market-regime-classification",
    "returncode": 0,
    "stdout": "....................................................                     [100%]\n52 passed in 1.21s",
    "stderr": ""
  }
}
```

## market-data-core daily load result

```json
{
  "success": false,
  "error": {
    "type": "RuntimeError",
    "message": "daily live load failed after retry budget",
    "traceback_tail": "Traceback (most recent call last):\n  File \"/home/ht/projects/market-regime-classification/artifacts/tmp_due_diligence_smoke.py\", line 295, in main\n    raise RuntimeError(\"daily live load failed after retry budget\")\nRuntimeError: daily live load failed after retry budget"
  }
}
```

## market-data-core 30m fresh load result

```json
{
  "success": false,
  "error": {
    "type": "RuntimeError",
    "message": "30m fresh live load failed after retry budget",
    "traceback_tail": "Traceback (most recent call last):\n  File \"/home/ht/projects/market-regime-classification/artifacts/tmp_due_diligence_smoke.py\", line 318, in main\n    raise RuntimeError(\"30m fresh live load failed after retry budget\")\nRuntimeError: 30m fresh live load failed after retry budget"
  }
}
```

## BaoStock retry log

```json
[
  {
    "label": "daily use_cache=False",
    "attempt": 1,
    "success": false,
    "retryable": true,
    "error": {
      "type": "TimeoutExpired",
      "message": "child load exceeded 20s"
    },
    "stdout": "",
    "stderr": ""
  },
  {
    "label": "daily use_cache=False",
    "attempt": 2,
    "success": false,
    "retryable": true,
    "error": {
      "type": "TimeoutExpired",
      "message": "child load exceeded 20s"
    },
    "stdout": "",
    "stderr": ""
  },
  {
    "label": "daily use_cache=False",
    "attempt": 3,
    "success": false,
    "retryable": true,
    "error": {
      "type": "TimeoutExpired",
      "message": "child load exceeded 20s"
    },
    "stdout": "",
    "stderr": ""
  },
  {
    "label": "30m use_cache=False",
    "attempt": 1,
    "success": false,
    "retryable": true,
    "error": {
      "type": "TimeoutExpired",
      "message": "child load exceeded 20s"
    },
    "stdout": "",
    "stderr": ""
  },
  {
    "label": "30m use_cache=False",
    "attempt": 2,
    "success": false,
    "retryable": true,
    "error": {
      "type": "TimeoutExpired",
      "message": "child load exceeded 20s"
    },
    "stdout": "",
    "stderr": ""
  },
  {
    "label": "30m use_cache=False",
    "attempt": 3,
    "success": false,
    "retryable": true,
    "error": {
      "type": "TimeoutExpired",
      "message": "child load exceeded 20s"
    },
    "stdout": "",
    "stderr": ""
  },
  {
    "label": "30m use_cache=True populate",
    "attempt": 1,
    "success": false,
    "retryable": true,
    "error": {
      "type": "TimeoutExpired",
      "message": "child load exceeded 20s"
    },
    "stdout": "",
    "stderr": ""
  },
  {
    "label": "30m use_cache=True populate",
    "attempt": 2,
    "success": false,
    "retryable": true,
    "error": {
      "type": "TimeoutExpired",
      "message": "child load exceeded 20s"
    },
    "stdout": "",
    "stderr": ""
  },
  {
    "label": "30m use_cache=True populate",
    "attempt": 3,
    "success": false,
    "retryable": true,
    "error": {
      "type": "TimeoutExpired",
      "message": "child load exceeded 20s"
    },
    "stdout": "",
    "stderr": ""
  }
]
```

## 30m timestamp anchor verification

```json
{
  "observed": null,
  "expected": [
    "09:30",
    "10:00",
    "10:30",
    "11:00",
    "13:00",
    "13:30",
    "14:00",
    "14:30"
  ],
  "matches_expected": null
}
```

## 30m cache roundtrip result

```json
{
  "success": false,
  "cache_path": ".data/market_data/v2/baostock/002850.SZ/30m/2025-11-03_2026-04-10.parquet",
  "error": {
    "type": "RuntimeError",
    "message": "30m cache populate load failed after retry budget",
    "traceback_tail": "Traceback (most recent call last):\n  File \"/home/ht/projects/market-regime-classification/artifacts/tmp_due_diligence_smoke.py\", line 347, in main\n    raise RuntimeError(\"30m cache populate load failed after retry budget\")\nRuntimeError: 30m cache populate load failed after retry budget"
  }
}
```

## market-regime-classification detector handoff result

```json
{
  "success": false,
  "error": {
    "type": "RuntimeError",
    "message": "No valid 30m DataFrame available for detector handoff",
    "traceback_tail": "Traceback (most recent call last):\n  File \"/home/ht/projects/market-regime-classification/artifacts/tmp_due_diligence_smoke.py\", line 374, in main\n    raise RuntimeError(\"No valid 30m DataFrame available for detector handoff\")\nRuntimeError: No valid 30m DataFrame available for detector handoff"
  }
}
```

## Detector output contract check

```json
{
  "success": false,
  "error": {
    "type": "RuntimeError",
    "message": "No detection result available for output contract check",
    "traceback_tail": "Traceback (most recent call last):\n  File \"/home/ht/projects/market-regime-classification/artifacts/tmp_due_diligence_smoke.py\", line 393, in main\n    raise RuntimeError(\"No detection result available for output contract check\")\nRuntimeError: No detection result available for output contract check"
  }
}
```

## Visualization smoke result

```json
{
  "success": false,
  "error": {
    "type": "RuntimeError",
    "message": "No detection result available for visualization",
    "traceback_tail": "Traceback (most recent call last):\n  File \"/home/ht/projects/market-regime-classification/artifacts/tmp_due_diligence_smoke.py\", line 414, in main\n    raise RuntimeError(\"No detection result available for visualization\")\nRuntimeError: No detection result available for visualization"
  }
}
```

## Evaluation smoke result

```json
{
  "success": false,
  "error": {
    "type": "RuntimeError",
    "message": "No detection result available for evaluation",
    "traceback_tail": "Traceback (most recent call last):\n  File \"/home/ht/projects/market-regime-classification/artifacts/tmp_due_diligence_smoke.py\", line 431, in main\n    raise RuntimeError(\"No detection result available for evaluation\")\nRuntimeError: No detection result available for evaluation"
  }
}
```

## Issues found

- market-data-core daily live load failed.
- market-data-core 30m fresh live load failed.
- 30m cache roundtrip failed.
- Wilder detector handoff failed.
- Detector output contract check failed or found missing rows.
- Visualization smoke failed.
- Evaluation smoke failed.

## Recommended next steps

- Retry live BaoStock due diligence when vendor connectivity is stable; failures were retried and logged.
- After a successful live 30m fetch, verify the new v2 cache path is populated and then rerun cache roundtrip.
