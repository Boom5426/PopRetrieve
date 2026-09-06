#!/usr/bin/env python
"""Offline, pytest-free test runner.

The venv here has no pytest, so this discovers and executes every ``test_*``
function in the test modules and reports PASS/FAIL. If pytest IS available, prefer
``pytest tests/`` — the test files are standard pytest tests.

    python tests/run_tests.py
"""
from __future__ import annotations

import importlib
import sys
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))    # package src on path (like conftest.py)
sys.path.insert(0, str(HERE))                    # so the test modules import

MODULES = ["test_metrics", "test_estimator_bias", "test_interaction_statistic", "test_retrieval_ranking", "test_degenerate_limits", "test_baseline_metrics", "test_baselines_smoke", "test_predictors_smoke", "test_scgen_predictor", "test_pdgrapher_adapter", "test_hir_generator", "test_exp12_partial_observed", "test_exp13_projection", "test_exp16_17"]


def main():
    passed = failed = 0
    fails = []
    for mod_name in MODULES:
        mod = importlib.import_module(mod_name)
        for name in sorted(dir(mod)):
            if not name.startswith("test_"):
                continue
            fn = getattr(mod, name)
            if not callable(fn):
                continue
            try:
                fn()
                passed += 1
                print(f"  PASS  {mod_name}.{name}")
            except Exception as exc:  # noqa: BLE001
                failed += 1
                fails.append((mod_name, name, exc))
                print(f"  FAIL  {mod_name}.{name}: {exc}")
    print(f"\n{passed} passed, {failed} failed")
    for mod_name, name, exc in fails:
        print(f"\n--- {mod_name}.{name} ---")
        traceback.print_exception(type(exc), exc, exc.__traceback__)
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
