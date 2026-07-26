"""Smoke tests for exp13 real-data projection (boundary fit + predict_regime)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src" / "experiments"))


def _import():
    import importlib
    return importlib.import_module("exp13_real_data_projection")


def test_predict_regime_predicted_mean():
    m = _import()
    # predicted_mean condition -> no_DART regardless of structure/conflict
    assert m.predict_regime(0.9, 0.9, "predicted_mean", 0.5) == "no_DART"
    assert m.predict_regime(0.9, 0.9, "mean_only", 0.5) == "no_DART"


def test_predict_regime_low_structure():
    m = _import()
    # low structure -> mean_sufficient even with high conflict
    assert m.predict_regime(0.1, 0.9, "observed", 0.5) == "mean_sufficient"


def test_predict_regime_dart():
    m = _import()
    # high structure + high conflict (above threshold) -> JUDGE
    assert m.predict_regime(0.8, 0.7, "observed", 0.5) == "DART_recommended"
    # high structure + low conflict (below threshold) -> mean
    assert m.predict_regime(0.8, 0.3, "observed", 0.5) == "mean_sufficient"


def test_fit_hir_boundary_keys():
    m = _import()
    import os
    # Only run if the HIR grid exists (server); otherwise skip gracefully
    if not os.path.exists(f"{m.HIR}/phase_grid_method_independent.csv"):
        return
    b = m.fit_hir_boundary()
    assert "conflict_crossover_percentile" in b
    assert 0 <= b["conflict_crossover_percentile"] <= 1
    assert b["n_cells"] > 0


def _run_tests():
    passed = failed = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                passed += 1
            except Exception as e:
                failed += 1
                print(f"  FAIL: {name}  {e}")
    print(f"\n{passed} passed, {failed} failed")
    return failed


if __name__ == "__main__":
    sys.exit(_run_tests())
