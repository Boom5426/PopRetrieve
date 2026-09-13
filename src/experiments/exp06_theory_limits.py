#!/usr/bin/env python
"""Experiment 6 — Degenerate limits and theory (plan §8-Exp6, reproduces FINDINGS §10).

Numerical proofs that the distribution-aware score is a STRICT generalization of the
mean-matching incumbent (10/10 checks), now with CSV export (the original only
printed PASS/FAIL):

  Prop 1: mean-matching = zero-spread limit of energy distance
          (point masses => energy == 2||mu_P - mu_Q||).
  Prop 2: global energy == coverage at K=1 (any beta).
  Prop 3: one temperature beta interpolates coverage_mean(beta->0) <-> coverage_worst
          (beta->inf), monotone.

Ladder: mean-matching  ⊂  global energy (= K=1 coverage)  ⊂  β-family coverage.

    python src/experiments/exp06_theory_limits.py
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
import torch

from data.load_sciplex3 import load_sciplex3               # noqa: E402
from retrieval.metrics import energy_distance_u, coverage_aggregate  # noqa: E402
from utils.io import results_path, write_csv                # noqa: E402
from utils.logging import log, section                     # noqa: E402

OUT = "exp06_theory_limits"
G = 2000
_checks = []


def _check(name, cond, detail=""):
    _checks.append(bool(cond))
    log(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"   {detail}" if detail else ""))


def prop1_synthetic():
    section("Prop 1 — mean-matching = zero-spread limit of energy distance")
    torch.manual_seed(0)
    P = torch.randn(300, G) + 0.7
    T = torch.randn(260, G) - 0.4
    muP, muT = P.mean(0), T.mean(0)
    dmu = float((muP - muT).norm())
    Pm, Tm = muP.expand(120, G).clone(), muT.expand(90, G).clone()
    e_point = float(energy_distance_u(Pm, Tm))
    # relative tolerance: float32 cdist (mm-mode) leaves a tiny spurious self-distance
    # residual (~1e-2 at G=2000); the point-mass identity holds to float precision.
    rel = 1e-3
    _check("energy(point-mass, point-mass) == 2||dmu||",
           abs(e_point - 2 * dmu) < rel * (2 * dmu + 1e-9),
           f"{e_point:.5f} vs {2*dmu:.5f}")
    rows = []
    for t in (1.0, 0.5, 0.25, 0.1, 0.01, 0.0):
        Pt, Tt = muP + t * (P - muP), muT + t * (T - muT)
        e = float(energy_distance_u(Pt, Tt))
        rows.append({"t_spread": t, "energy": e, "two_dmu": 2 * dmu})
    _check("energy -> 2||dmu|| as spread -> 0",
           abs(rows[-1]["energy"] - 2 * dmu) < rel * (2 * dmu + 1e-9),
           f"t=0 -> {rows[-1]['energy']:.5f}")
    _check("mean-only differs from full-population energy (mean is lossy)",
           abs(rows[0]["energy"] - 2 * dmu) > 1e-2,
           f"full={rows[0]['energy']:.3f} vs mean-only={2*dmu:.3f}")
    return pd.DataFrame(rows)


def prop2_synthetic():
    section("Prop 2 — global energy == coverage at K=1")
    torch.manual_seed(1)
    P, T = torch.randn(200, G), torch.randn(180, G) + 0.5
    g = energy_distance_u(P, T)
    rows, ok = [], True
    for beta in (0.0, 0.1, 1.0, 10.0, 1e3):
        c = float(coverage_aggregate(g.reshape(1), beta))
        ok &= abs(c - float(g)) < 1e-6
        rows.append({"beta": beta, "coverage_K1": c, "global_energy": float(g)})
    _check("coverage_aggregate([energy], beta) == energy for all beta", ok,
           f"global={float(g):.5f}")
    return pd.DataFrame(rows)


def prop3_interpolation():
    section("Prop 3 — one temperature interpolates mean <-> worst")
    e = torch.tensor([0.20, 0.55, 1.30, 0.80])
    betas = [1e-9, 0.1, 0.5, 1, 2, 5, 10, 20, 100, 1e9]
    rows = [{"beta": b, "D_beta": float(coverage_aggregate(e, b)),
             "mean": float(e.mean()), "max": float(e.max())} for b in betas]
    _check("beta->0 == mean", abs(rows[0]["D_beta"] - float(e.mean())) < 1e-4)
    _check("beta->inf == max (worst)", abs(rows[-1]["D_beta"] - float(e.max())) < 1e-4)
    vals = [r["D_beta"] for r in rows]
    _check("monotone non-decreasing in beta",
           all(vals[i] <= vals[i + 1] + 1e-6 for i in range(len(vals) - 1)),
           " -> ".join(f"{v:.3f}" for v in vals))
    return pd.DataFrame(rows)


def real_anchor(processed=None):
    section("Real-cell anchor — SciPlex3 K562/A549 populations")
    rows = []
    try:
        data = load_sciplex3(processed)
    except Exception as ex:  # noqa: BLE001
        log(f"  (skipped real anchor: {ex})")
        return pd.DataFrame(rows)
    X, ctx, pert, isc = data.X, data.context, data.pert, data.is_control
    rng = np.random.default_rng(0)

    def pop(L, d, n=150):
        r = np.flatnonzero((ctx == L) & ~isc & (pert == d))
        return torch.as_tensor(X[rng.choice(r, min(n, len(r)), replace=False)])

    d = "Panobinostat (LBH589)"
    Pk, Pa = pop("K562", d), pop("A549", d)
    Tk, Ta = pop("K562", d), pop("A549", d)
    Pmix, Tmix = torch.cat([Pk, Pa]), torch.cat([Tk, Ta])
    g = energy_distance_u(Pmix, Tmix)
    c_k1 = float(coverage_aggregate(g.reshape(1), 1.0))
    _check("K=1 coverage == global energy (real mixture)", abs(c_k1 - float(g)) < 1e-6,
           f"{float(g):.4f}")
    e_k, e_a = energy_distance_u(Pk, Tk), energy_distance_u(Pa, Ta)
    dists = torch.stack([e_k, e_a])
    cmean = float(coverage_aggregate(dists, 1e-9))
    cworst = float(coverage_aggregate(dists, 1e9))
    _check("coverage_mean == 0.5*(e_K562 + e_A549)", abs(cmean - 0.5 * (float(e_k) + float(e_a))) < 1e-4,
           f"e_K={float(e_k):.3f} e_A={float(e_a):.3f} mean={cmean:.3f}")
    _check("coverage_worst == max(e_K562, e_A549)", abs(cworst - max(float(e_k), float(e_a))) < 1e-4,
           f"worst={cworst:.3f}")
    rows.append({"drug": d, "global_energy": float(g), "coverage_K1": c_k1,
                 "e_K562": float(e_k), "e_A549": float(e_a),
                 "coverage_mean": cmean, "coverage_worst": cworst})
    return pd.DataFrame(rows)


def run(processed=None):
    _checks.clear()
    p1 = prop1_synthetic()
    p2 = prop2_synthetic()
    p3 = prop3_interpolation()
    real = real_anchor(processed)
    write_csv(pd.concat([p1.assign(prop="prop1_spread"),
                         p2.assign(prop="prop2_K1")], ignore_index=True),
              results_path(OUT, "degenerate_limit_synthetic.csv"))
    write_csv(p3, results_path(OUT, "beta_interpolation.csv"))
    write_csv(real, results_path(OUT, "degenerate_limit_real.csv"))
    section(f"EXP06 RESULT: {sum(_checks)}/{len(_checks)} checks passed"
            + ("  -- ALL PROOFS HOLD" if all(_checks) else "  -- SOME FAILED"))
    return {"checks": [{"label": "degenerate_limits", "pass": all(_checks),
                        "detail": f"{sum(_checks)}/{len(_checks)}"}],
            "all_pass": all(_checks)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--processed", default=None)
    args = ap.parse_args()
    res = run(processed=args.processed)
    sys.exit(0 if res["all_pass"] else 1)


if __name__ == "__main__":
    main()
