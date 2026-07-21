"""Unit tests for HIR-Bench generator, oracle, conflict, and boundary modules."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np

from benchmarks.heterogeneous_retrieval_benchmark import generate_hir_cell
from benchmarks.oracle_utility import (
    welfare_mean, welfare_worst, welfare_cvar,
    oracle_population_optimal, oracle_mean_optimal, oracle_flip_risk,
    oracle_utility_gap, decision_regret,
)
from benchmarks.preference_conflict import (
    topk_disagreement, standard_kendall_conflict, response_cosine,
)
from benchmarks.theory_boundary import compute_boundary


def test_shapes_query():
    cell = generate_hir_cell(n_subpops=2, dim=30, library_size=20, seed=42)
    assert cell.query_X.ndim == 2 and cell.query_X.shape[1] == 30

def test_shapes_utility():
    cell = generate_hir_cell(n_subpops=2, dim=30, library_size=20, seed=42)
    assert cell.utility_matrix.shape == (20, 2)

def test_shapes_weights():
    cell = generate_hir_cell(n_subpops=2, dim=30, library_size=20, seed=42)
    assert len(cell.true_weights) == 2

def test_shapes_drugs():
    cell = generate_hir_cell(n_subpops=2, dim=30, library_size=20, seed=42)
    assert len(cell.drug_ids) == 20 and len(cell.candidate_populations) == 20

def test_query_labels():
    cell = generate_hir_cell(n_subpops=2, dim=30, library_size=20, seed=42)
    assert set(cell.query_labels.tolist()) == {0, 1}

def test_no_conflict_flip():
    cell0 = generate_hir_cell(conflict_level=0.0, library_size=20, seed=0)
    assert oracle_flip_risk(cell0, welfare="worst") == 0, "flip should be 0 at conflict=0"

def test_no_conflict_topk():
    cell0 = generate_hir_cell(conflict_level=0.0, library_size=20, seed=0)
    td = topk_disagreement(cell0)
    assert td <= 0.6, f"topk too high at conflict=0: {td:.3f}"

def test_max_conflict_flip():
    cell1 = generate_hir_cell(conflict_level=1.0, library_size=20, seed=0, majority_fraction=0.7)
    assert oracle_flip_risk(cell1, welfare="worst") == 1, "flip should be 1 at max conflict"

def test_max_conflict_topk():
    cell1 = generate_hir_cell(conflict_level=1.0, library_size=20, seed=0, majority_fraction=0.7)
    td = topk_disagreement(cell1)
    assert td >= 0.5, f"topk too low at max conflict: {td:.3f}"

def test_welfare_order():
    cell = generate_hir_cell(conflict_level=0.5, seed=7)
    w_mean = welfare_mean(cell)
    w_worst = welfare_worst(cell)
    w_cvar = welfare_cvar(cell, q=0.5)
    assert np.all(w_worst <= w_cvar + 1e-8), "worst should be <= cvar"
    assert np.all(w_cvar <= w_mean + 1e-8), "cvar should be <= mean"

def test_boundary_exists():
    cell = generate_hir_cell(conflict_level=0.8, majority_fraction=0.7, seed=3)
    b = compute_boundary(cell)
    assert b is not None and not b.get("no_conflict", False), "boundary should exist at conflict=0.8"

def test_boundary_formula():
    cell = generate_hir_cell(conflict_level=0.8, majority_fraction=0.7, seed=3)
    b = compute_boundary(cell)
    if b and not b.get("no_conflict"):
        expected = b["B"] / (b["A"] + b["B"])
        assert abs(b["alpha_star"] - expected) < 1e-10, f"formula mismatch: {b['alpha_star']} vs {expected}"
        assert 0 < b["alpha_star"] < 1, "alpha_star should be in (0,1)"

def test_predicted_mean_isotropic():
    from sklearn.cluster import KMeans
    cell = generate_hir_cell(conflict_level=0.5, information_condition="predicted_mean",
                              seed=5, cells_per_subpop=60)
    var_ratios = []
    for d_id in list(cell.drug_ids)[:5]:
        X = cell.candidate_populations[d_id]
        mu = X.mean(axis=0)
        sst = float(np.sum((X - mu) ** 2))
        if sst < 1e-12:
            continue
        km = KMeans(n_clusters=2, n_init=3, random_state=0, max_iter=50).fit(X)
        ssw = sum(float(np.sum((X[km.labels_ == c] - X[km.labels_ == c].mean(0)) ** 2))
                  for c in range(2))
        var_ratios.append((sst - ssw) / sst)
    mean_vr = np.mean(var_ratios) if var_ratios else 0
    assert mean_vr < 0.05, f"mean variance ratio={mean_vr:.4f} should be <0.05 for isotropic"

def test_regret_optimal_zero():
    cell = generate_hir_cell(n_subpops=2, dim=30, library_size=20, seed=42)
    opt_drug, _ = oracle_population_optimal(cell, welfare="mean")
    regret = decision_regret(cell, opt_drug, welfare="mean")
    assert abs(regret) < 1e-10, f"regret for optimal drug should be ~0, got {regret}"

def test_regret_worst_positive():
    cell = generate_hir_cell(n_subpops=2, dim=30, library_size=20, seed=42)
    U_mean = welfare_mean(cell)
    worst_drug = cell.drug_ids[int(np.argmin(U_mean))]
    regret = decision_regret(cell, worst_drug, welfare="mean")
    assert regret > 0, f"regret for worst drug should be positive, got {regret}"

def test_response_cosine_order():
    cell0 = generate_hir_cell(conflict_level=0.0, seed=0)
    cell1 = generate_hir_cell(conflict_level=1.0, seed=0)
    cos0 = response_cosine(cell0)
    cos1 = response_cosine(cell1)
    assert cos0 >= cos1 - 0.01, f"no_conflict cos={cos0:.3f} should >= max_conflict cos={cos1:.3f}"

def test_conflict_monotonic_flip():
    """Flip rate should increase with conflict level over many seeds."""
    flips = {}
    for cl in [0.0, 0.5, 1.0]:
        rates = [oracle_flip_risk(generate_hir_cell(conflict_level=cl, library_size=20,
                                                     seed=s, majority_fraction=0.7), welfare="worst")
                 for s in range(20)]
        flips[cl] = np.mean(rates)
    assert flips[0.0] <= flips[0.5], f"flip should increase: {flips[0.0]} -> {flips[0.5]}"
    assert flips[0.5] <= flips[1.0] + 0.05, f"flip should increase: {flips[0.5]} -> {flips[1.0]}"


def test_standard_kendall_conflict_constant_column_is_finite():
    """A subpop with a constant utility column makes kendalltau NaN; the guard must
    return a finite conflict value rather than propagating NaN into the gate features."""
    class _Cell:
        pass
    cell = _Cell()
    # subpop 0 varies, subpop 1 is constant -> kendalltau(., const) is NaN
    cell.utility_matrix = np.column_stack([np.arange(10.0), np.ones(10)])
    val = standard_kendall_conflict(cell)
    assert np.isfinite(val), f"expected finite conflict, got {val}"


def test_score_disagreement_constant_ranking_is_finite():
    """score_disagreement must not propagate NaN when one ranking is constant."""
    from benchmarks.predictability import score_disagreement
    val = score_disagreement(np.ones(8), np.arange(8.0))
    assert np.isfinite(val) and val == 0.0, f"expected 0.0, got {val}"


# ── standalone runner ──
def _run_tests():
    """Run all test_ functions and report."""
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
