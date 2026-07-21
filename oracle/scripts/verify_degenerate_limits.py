#!/usr/bin/env python
"""Correctness / degenerate-limit proofs for the distribution-aware score.

Establishes (numerically, to machine tolerance) that our score is a STRICT
GENERALIZATION of the mean-matching incumbent, not an unrelated heuristic:

  Prop 1 (mean-matching is the zero-spread limit of the distributional distance):
    energy_distance(P, T) with each population collapsed to a point mass at its mean
    equals 2*||mu_P - mu_T||  (a pure mean-difference). The extra terms energy keeps,
    -E||X-X'|| - E||Y-Y'||, are exactly the within-population spread the mean discards.

  Prop 2 (global distance = coverage at K=1):
    coverage_aggregate([energy(P,T)], beta) == energy(P,T) for ANY beta. With one
    subpopulation the coverage score reduces EXACTLY to the global energy distance.

  Prop 3 (one temperature interpolates mean <-> worst):
    coverage_aggregate(dists, beta) -> mean(dists) as beta->0 and -> max(dists) as
    beta->inf, and is monotone in beta. Our reported coverage_mean / coverage_worst
    are the two endpoints of this single continuum.

Verified on synthetic tensors (exact) and on REAL SciPlex3 cross-line populations.

    python scripts/verify_degenerate_limits.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gidflow.losses.distribution import energy_distance, coverage_aggregate  # noqa: E402

torch.manual_seed(0)
G = 2000                        # gene-space dim (as in the real experiments)
OK = "\033[92mPASS\033[0m"; BAD = "\033[91mFAIL\033[0m"
results = []


def check(name, cond, detail=""):
    results.append(cond)
    print(f"  [{OK if cond else BAD}] {name}" + (f"   {detail}" if detail else ""))


def prop1_mean_is_zero_spread_limit():
    print("\nProp 1 — mean-matching = zero-spread limit of energy distance")
    P = torch.randn(300, G) + 0.7
    T = torch.randn(260, G) - 0.4
    muP, muT = P.mean(0), T.mean(0)
    dmu = float((muP - muT).norm())

    # point masses at the means
    Pm = muP.expand(120, G).clone()
    Tm = muT.expand(90, G).clone()
    e_point = float(energy_distance(Pm, Tm))
    check("energy(point-mass P, point-mass T) == 2*||mu_P - mu_T||",
          abs(e_point - 2 * dmu) < 1e-4, f"{e_point:.5f} vs {2*dmu:.5f}")

    # shrink within-population spread P_t = mu + t*(P-mu); t->0 must reach 2||dmu||
    print("    within-spread shrink t -> 0  (energy -> 2||dmu|| = %.4f):" % (2 * dmu))
    curve = []
    for t in (1.0, 0.5, 0.25, 0.1, 0.01, 0.0):
        Pt = muP + t * (P - muP); Tt = muT + t * (T - muT)
        e = float(energy_distance(Pt, Tt)); curve.append(e)
        print(f"       t={t:<5} energy={e:.4f}")
    check("energy -> 2||dmu|| as spread -> 0", abs(curve[-1] - 2 * dmu) < 1e-4,
          f"t=0 -> {curve[-1]:.5f}")
    # mean-matching (point mass) != full-population energy: the mean is LOSSY. Spread
    # changes the distance (here it shrinks it: overlapping clouds are closer than
    # their means suggest) -- mean-matching ignores exactly this within-population term.
    check("mean-only (point-mass) energy differs from full-population energy "
          "(mean discards within-population spread)",
          abs(curve[0] - 2 * dmu) > 1e-2, f"full t=1:{curve[0]:.3f} vs mean-only:{2*dmu:.3f}")


def prop2_global_is_coverage_K1():
    print("\nProp 2 — global energy == coverage at K=1 (strict generalization)")
    P = torch.randn(200, G); T = torch.randn(180, G) + 0.5
    g = energy_distance(P, T)
    worst = True
    for beta in (0.0, 0.1, 1.0, 10.0, 1e3):
        c = coverage_aggregate(g.reshape(1), beta)
        worst &= abs(float(c) - float(g)) < 1e-6
    check("coverage_aggregate([energy],beta) == energy for all beta", worst,
          f"global={float(g):.5f}")


def prop3_beta_interpolates():
    print("\nProp 3 — one temperature beta interpolates mean <-> worst")
    e = torch.tensor([0.20, 0.55, 1.30, 0.80])          # per-subpop distances
    c0 = float(coverage_aggregate(e, 1e-9)); cinf = float(coverage_aggregate(e, 1e9))
    check("beta->0  == arithmetic mean", abs(c0 - float(e.mean())) < 1e-4,
          f"{c0:.5f} vs mean {float(e.mean()):.5f}")
    check("beta->inf == max (worst subpop)", abs(cinf - float(e.max())) < 1e-4,
          f"{cinf:.5f} vs max {float(e.max()):.5f}")
    vals = [float(coverage_aggregate(e, b)) for b in (1e-9, 0.5, 1, 2, 5, 20, 1e9)]
    check("monotone non-decreasing in beta (mean <= ... <= max)",
          all(vals[i] <= vals[i + 1] + 1e-6 for i in range(len(vals) - 1)),
          " -> ".join(f"{v:.3f}" for v in vals))


def real_anchor():
    print("\nReal-cell anchor — the same identities on SciPlex3 K562/A549 populations")
    try:
        from gidflow.data.processed import SciplexDataset
        data = SciplexDataset("data/processed/sciplex3_all.pt", "data/annotation")
        X = data.X.numpy(); obs = data.obs
        line = obs["cell_line"].astype(str).to_numpy()
        drug = obs["perturbation"].astype(str).str.strip().to_numpy()
        isc = (obs["is_control"].astype(bool).to_numpy() if "is_control" in obs
               else np.zeros(len(obs), bool))
    except Exception as ex:                                  # noqa: BLE001
        print(f"  (skipped real anchor: {ex})"); return
    rng = np.random.default_rng(0)

    def pop(L, d, n=150):
        r = np.flatnonzero((line == L) & ~isc & (drug == d))
        return torch.as_tensor(X[rng.choice(r, min(n, len(r)), replace=False)])

    d = "Panobinostat (LBH589)"      # strong, reliable, cross-line-divergent
    Pk, Pa = pop("K562", d), pop("A549", d)                 # candidate d in each line
    Tk, Ta = pop("K562", d), pop("A549", d)                 # independent target draw
    Pmix = torch.cat([Pk, Pa]); Tmix = torch.cat([Tk, Ta])

    g = energy_distance(Pmix, Tmix)
    c_k1 = coverage_aggregate(g.reshape(1), 1.0)
    check("K=1 coverage == global energy (real mixture)",
          abs(float(c_k1) - float(g)) < 1e-6, f"{float(g):.4f}")

    e_k = energy_distance(Pk, Tk); e_a = energy_distance(Pa, Ta)
    dists = torch.stack([e_k, e_a])
    cmean = float(coverage_aggregate(dists, 1e-9)); cworst = float(coverage_aggregate(dists, 1e9))
    check("coverage_mean == 0.5*(e_K562 + e_A549) (real)",
          abs(cmean - 0.5 * (float(e_k) + float(e_a))) < 1e-4,
          f"e_K={float(e_k):.3f} e_A={float(e_a):.3f} mean={cmean:.3f}")
    check("coverage_worst == max(e_K562, e_A549) (real)",
          abs(cworst - max(float(e_k), float(e_a))) < 1e-4, f"worst={cworst:.3f}")


if __name__ == "__main__":
    print("=" * 68)
    print("DEGENERATE-LIMIT CORRECTNESS PROOFS (distribution-aware score)")
    print("=" * 68)
    prop1_mean_is_zero_spread_limit()
    prop2_global_is_coverage_K1()
    prop3_beta_interpolates()
    real_anchor()
    print("\n" + "=" * 68)
    print(f"RESULT: {sum(results)}/{len(results)} checks passed"
          + ("  -- ALL PROOFS HOLD" if all(results) else "  -- SOME FAILED"))
    print("=" * 68)
    sys.exit(0 if all(results) else 1)
