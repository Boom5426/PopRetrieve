"""Smoke tests for exp12 partial-observed retrieval helpers (synthetic, no real data)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src" / "experiments"))

import numpy as np


def _import():
    import importlib
    return importlib.import_module("exp12_partial_observed_retrieval")


def test_ranking_metrics_basic():
    m = _import()
    names = ["a", "b", "c", "d"]
    scores = np.array([0.9, 0.1, 0.8, 0.2])  # order: a, c, d, b
    gt = {"c"}  # c is at rank 2
    r = m._ranking_metrics(scores, names, gt)
    assert r["hit@1"] == 0 and r["hit@5"] == 1, r
    assert abs(r["mrr"] - 0.5) < 1e-9, r
    assert r["best_rank"] == 2, r


def test_ranking_metrics_top1():
    m = _import()
    names = ["a", "b", "c"]
    scores = np.array([0.9, 0.1, 0.2])
    r = m._ranking_metrics(scores, names, {"a"})
    assert r["hit@1"] == 1 and abs(r["mrr"] - 1.0) < 1e-9


def test_subpop_variance_ratio_structured():
    m = _import()
    rng = np.random.default_rng(0)
    # Two well-separated clusters -> high variance ratio
    X = np.vstack([rng.normal(0, 0.1, (50, 10)), rng.normal(5, 0.1, (50, 10))])
    vr = m._subpop_variance_ratio(X)
    assert vr > 0.8, f"structured var ratio should be high, got {vr}"


def test_subpop_variance_ratio_isotropic():
    m = _import()
    rng = np.random.default_rng(0)
    X = rng.normal(0, 1, (100, 10))  # single blob
    vr = m._subpop_variance_ratio(X)
    assert vr < 0.3, f"isotropic var ratio should be low, got {vr}"


def test_recommendation_mode_logic():
    m = _import()
    # low structure -> mean_or_no_call
    assert m.recommendation_mode(0.1, 0.9) == "mean_or_no_call"
    # high structure, low conflict -> mean_sufficient
    assert m.recommendation_mode(0.8, 0.1) == "mean_sufficient"
    # high structure, high conflict -> DART_recommended
    assert m.recommendation_mode(0.8, 0.8) == "DART_recommended"


def test_structure_reliability_bounds():
    m = _import()
    s = m.structure_reliability(0.5, 0.2, 0.4, 0.9, energy_disagreement=0.3)
    assert 0 <= s <= 1, s
    # All-max inputs -> high score (var>=0.05, diversity=1, stability=1, disagreement=1)
    s_hi = m.structure_reliability(0.05, 0.0, 1.0, 1.0, energy_disagreement=1.0)
    assert s_hi > 0.9, s_hi
    # Low stability + low disagreement -> low score even with structure
    s_lo = m.structure_reliability(0.05, 0.0, 0.5, 0.1, energy_disagreement=0.0)
    assert s_lo < 0.4, s_lo


def test_decision_regret_nonneg():
    m = _import()
    wv = {"a": -1.0, "b": -3.0, "c": -0.5}
    assert abs(m._decision_regret(wv, "c")) < 1e-9  # c is optimal
    assert m._decision_regret(wv, "b") > 0  # b is worse


def test_welfare_proxy_shapes():
    m = _import()
    rng = np.random.default_rng(0)
    query_X = np.vstack([rng.normal(0, 0.3, (40, 8)), rng.normal(4, 0.3, (40, 8))])
    states = np.array([0] * 40 + [1] * 40)
    cand_pops = {
        "close": np.vstack([rng.normal(0, 0.3, (30, 8)), rng.normal(4, 0.3, (30, 8))]),
        "far": rng.normal(10, 0.3, (60, 8)),
    }
    wv = m._welfare_proxy(cand_pops, query_X, states, welfare="worst", seed=0)
    assert set(wv.keys()) == {"close", "far"}
    assert wv["close"] > wv["far"], f"close should have higher welfare: {wv}"


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
