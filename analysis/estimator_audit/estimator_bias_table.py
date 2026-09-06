#!/usr/bin/env python
"""Phase 1 (P0-A): quantify the sample-size bias of every population scorer this project uses.

The unit tests in tests/test_estimator_bias.py assert the qualitative properties. This script
measures them, so the audit report quotes numbers rather than adjectives, and so the size of the
bias can be compared against the size of the effects the manuscript claims.

Three measurements, all on Gaussian data so the population value of every statistic is known:

1.  NULL SCALING.  P and Q are drawn from the same distribution, so the population energy
    distance and MMD are both exactly zero. Anything a scorer returns is bias plus noise. Run at
    n = 25, 50, 100, 200 to expose the 1/n term.

2.  UNEQUAL SIZES.  The query has N_QUERY cells; candidates of several sizes are drawn from the
    query's OWN distribution, so every candidate is equally correct and any spread across sizes
    is an artefact. This is the configuration that occurs throughout the Phase-II benchmark,
    where a candidate bank holds between 50 and 100 cells.

3.  BIAS AGAINST EFFECT.  The same unequal-size spread expressed as the mean shift that would
    produce it, which is the only way to judge whether the artefact is large enough to matter:
    a bias worth 0.02 of a standard deviation is a curiosity, one worth 0.5 is a confound.

Dimensionality is swept because the manuscript works at 2,000 to 2,304 genes and a bias measured
at 32 dimensions would not transfer.

Run:
    python analysis/estimator_audit/estimator_bias_table.py --out results/estimator_audit
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from retrieval.metrics import (                                      # noqa: E402
    energy_distance, energy_distance_u, mmd_rbf, mmd_rbf_u, sliced_wasserstein,
)

SIZES = (25, 50, 100, 200, 400)
DIMS = (32, 256, 2304)
N_QUERY = 200
N_REP = 24
SEED = 0


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def draw(n: int, g: int, gen: torch.Generator, shift: float = 0.0) -> torch.Tensor:
    return torch.randn(n, g, generator=gen) + shift


def scorers(P, Q) -> dict[str, float]:
    return {
        "energy_u": float(energy_distance_u(P, Q)),
        "energy_v": float(energy_distance(P, Q)),
        "mmd_u": float(mmd_rbf_u(P, Q)),
        "mmd_v": float(mmd_rbf(P, Q)),
        "sliced_wasserstein": float(sliced_wasserstein(P, Q)),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True)
    ap.add_argument("--n-rep", type=int, default=N_REP)
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    # ---- 1. null scaling ----
    rows = []
    for g in DIMS:
        for n in SIZES:
            acc = {k: [] for k in scorers(torch.zeros(2, g), torch.zeros(2, g))}
            for rep in range(a.n_rep):
                gen = torch.Generator().manual_seed(SEED + 1000 * rep + n + g)
                P, Q = draw(n, g, gen), draw(n, g, gen)
                for k, v in scorers(P, Q).items():
                    acc[k].append(v)
            rec = {"dim": g, "n": n}
            for k, v in acc.items():
                rec[k] = float(np.mean(v))
                rec[f"{k}_se"] = float(np.std(v, ddof=1) / np.sqrt(len(v)))
            rows.append(rec)
        log(f"null scaling done for dim={g} ({time.time() - t0:.0f}s)")
    null = pd.DataFrame(rows)
    null.to_csv(out / "null_scaling.csv", index=False)

    # ---- 2. unequal candidate sizes against a fixed query ----
    rows = []
    for g in DIMS:
        for m in SIZES:
            acc = {k: [] for k in ("energy_u", "energy_v", "mmd_u", "mmd_v",
                                   "sliced_wasserstein")}
            for rep in range(a.n_rep):
                gen = torch.Generator().manual_seed(SEED + 7000 * rep + m + g)
                Q = draw(N_QUERY, g, gen)
                P = draw(m, g, gen)                    # same distribution as the query
                for k, v in scorers(P, Q).items():
                    acc[k].append(v)
            rec = {"dim": g, "n_query": N_QUERY, "n_candidate": m}
            for k, v in acc.items():
                rec[k] = float(np.mean(v))
                rec[f"{k}_se"] = float(np.std(v, ddof=1) / np.sqrt(len(v)))
            rows.append(rec)
        log(f"unequal sizes done for dim={g} ({time.time() - t0:.0f}s)")
    uneq = pd.DataFrame(rows)
    uneq.to_csv(out / "unequal_sizes.csv", index=False)

    # ---- 3. express the artefact as an equivalent mean shift ----
    #
    # How large a real mean shift would move the score by as much as shrinking a candidate from
    # 400 cells to 50 does? Calibrated per dimension by measuring the score of a 400-cell
    # candidate at several shifts and inverting.
    cal_rows, equiv_rows = [], []
    shifts = (0.0, 0.02, 0.05, 0.1, 0.2, 0.4)
    for g in DIMS:
        curve = {}
        for s in shifts:
            acc = {"energy_u": [], "energy_v": []}
            for rep in range(a.n_rep):
                gen = torch.Generator().manual_seed(SEED + 9000 * rep + g)
                Q = draw(N_QUERY, g, gen)
                P = draw(400, g, gen, shift=s)
                sc = scorers(P, Q)
                acc["energy_u"].append(sc["energy_u"])
                acc["energy_v"].append(sc["energy_v"])
            curve[s] = {k: float(np.mean(v)) for k, v in acc.items()}
            cal_rows.append({"dim": g, "shift": s, **curve[s]})
        u = uneq[uneq.dim == g].set_index("n_candidate")
        for est in ("energy_u", "energy_v"):
            artefact = float(u.loc[50, est] - u.loc[400, est])
            xs = np.array(shifts)
            ys = np.array([curve[s][est] - curve[0.0][est] for s in shifts])
            equiv = float(np.interp(artefact, ys, xs)) if artefact > 0 else 0.0
            equiv_rows.append({"dim": g, "estimator": est,
                               "artefact_50_vs_400": artefact,
                               "equivalent_mean_shift_sd": equiv})
        log(f"calibration done for dim={g} ({time.time() - t0:.0f}s)")
    pd.DataFrame(cal_rows).to_csv(out / "shift_calibration.csv", index=False)
    equiv = pd.DataFrame(equiv_rows)
    equiv.to_csv(out / "artefact_as_mean_shift.csv", index=False)

    # ---- 4. the dispersion channel, which survives equal sample sizes ----
    #
    # E_V = E_U + within(X)/m + within(Y)/n. The query term is the same for every candidate, so
    # it cancels from a ranking. The candidate term does NOT: at equal m it still varies with the
    # candidate's own dispersion, so the V form systematically prefers tighter candidates. This
    # measures how large that residual preference is, expressed as the extra spread a candidate
    # can carry before the V form starts to prefer it over a correct but slightly tighter rival.
    disp_rows = []
    for g in DIMS:
        for m in (100, 200, 400):
            for sd in (1.0, 1.1, 1.3, 1.6):
                acc = {"energy_u": [], "energy_v": []}
                for rep in range(a.n_rep):
                    gen = torch.Generator().manual_seed(SEED + 5000 * rep + m + g)
                    Q = draw(N_QUERY, g, gen)
                    P = torch.randn(m, g, generator=gen) * sd
                    sc = scorers(P, Q)
                    acc["energy_u"].append(sc["energy_u"])
                    acc["energy_v"].append(sc["energy_v"])
                disp_rows.append({"dim": g, "n_candidate": m, "candidate_sd": sd,
                                  **{k: float(np.mean(v)) for k, v in acc.items()},
                                  **{f"{k}_se": float(np.std(v, ddof=1) / np.sqrt(len(v)))
                                     for k, v in acc.items()}})
        log(f"dispersion channel done for dim={g} ({time.time() - t0:.0f}s)")
    disp = pd.DataFrame(disp_rows)
    disp.to_csv(out / "dispersion_channel.csv", index=False)

    (out / "provenance.json").write_text(json.dumps({
        "sizes": list(SIZES), "dims": list(DIMS), "n_query": N_QUERY,
        "n_rep": a.n_rep, "seed": SEED,
        "distribution": "isotropic standard normal, so every population value is known exactly",
        "mmd_implementation": ("multi-bandwidth RBF, scales (0.25, 1, 4) times the median of the "
                              "pooled squared pairwise distances; the repository default is the "
                              "V-statistic form"),
        "runtime_seconds": round(time.time() - t0, 1),
    }, indent=2) + "\n")
    log(equiv.to_string(index=False))
    log(f"wrote {out} ({time.time() - t0:.0f}s)")


if __name__ == "__main__":
    sys.exit(main())
