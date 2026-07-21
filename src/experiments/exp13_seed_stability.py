#!/usr/bin/env python
"""Do exp13's "distributionally dominant" real-data tasks survive reseeding? Mostly not.

This experiment exists because a count of threshold crossings looked like a finding and was
not. It is load-bearing evidence for CORRECTIONS.md R13 and for Result 3, so it ships as a
first-class experiment rather than as an analysis script.

WHY THE QUESTION ARISES. exp13 records, per task, the minority-state coverage of the DART
pick minus that of the mean pick, and a task is conventionally called "distributionally
dominant" when that difference exceeds +0.01. Two things make a COUNT of such tasks
untrustworthy on this data:

  1. The threshold is not calibrated to the data. It sits at 0.77 standard deviations of the
     nonzero-difference distribution (sd = 0.013), i.e. inside its noise band. It is also
     one-sided: on the FULL run 11 tasks clear it for DART and 2 clear it for the mean.

  2. THE SEED IS NOT A REPLICATE. In exp13 it re-draws which drugs are held out
     (rng.choice(common, n_drugs)) and it redefines the minority subpopulation by
     re-clustering (_query_states(qX, k=2, seed=seed)). So "drug X was dominant at seed s"
     says nothing about whether drug X is robustly dominant.

WHAT THIS DOES. Stage 1 rebuilds tasks with exp13's own builder and checks that we reproduce
the deltas recorded in projection.csv. This is not optional: a replication test run on a
harness that cannot reproduce the original numbers tests nothing. (An earlier attempt of ours
rebuilt the cross-line query as a 50/50 mixture of two cell lines. _crossline_tasks actually
uses the held-out drug's response in the QUERY line only, with candidates drawn from the
OTHER line. That reconstruction returned deltas near zero where the pipeline records +0.087,
which is how an unfaithful harness announces itself.)

Stage 2 holds the drug fixed, resamples the seed ten times, and does the same for control
drugs that were NOT recorded as dominant, so the comparison has a baseline.

RESULT (see results/exp13_real_data_projection/seed_stability.csv). Only 2 of the 10
threshold-crossing cross-line tasks remain dominant in >= 8 of 10 seeds, both HDAC inhibitors
in the A549->MCF7 pair. Control drugs that never crossed the threshold in the recorded run
cross it in 2 to 4 of 10 resamples. The count is a count of noise excursions.

    PYTHONPATH=src python src/experiments/exp13_seed_stability.py
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from data.load_sciplex3 import load_sciplex3
import experiments.exp12_partial_observed_retrieval as e12
import experiments.exp13_real_data_projection as e13
from utils.io import results_path, write_csv
from utils.logging import log, section

OUT = "exp13_real_data_projection"
MARGIN = 0.01          # the dominance criterion in exp13._observed_best_family
STABLE_AT = 8          # "replication-stable" = dominant in >= 8 of 10 reseeds


def _sweep(ds, qline, lline, drug, seeds):
    """exp13's cross-line construction with the drug forced and the seed swept."""
    q = sorted(set(np.asarray(ds.pert)[(ds.context == qline) & (~ds.is_control)].tolist()))
    l = sorted(set(np.asarray(ds.pert)[(ds.context == lline) & (~ds.is_control)].tolist()))
    common = sorted(set(q) & set(l))
    ctrl = ds.control_mean(lline)
    out = []
    for seed in seeds:
        rng = np.random.default_rng(seed)
        rows = ds.treated_rows(qline, drug)
        if len(rows) < 20:
            continue
        if len(rows) > 200:
            rows = rng.choice(rows, 200, replace=False)
        qX = ds.X[rows]
        qs, mino = e12._query_states(qX, k=2, seed=seed)
        lib = [d for d in common if d != drug]
        cand = e12._build_candidate_pops(ds, lline, lib, max_cells=120, rng=rng)
        if len(cand) < 5:
            continue
        _fam, dcov, mcov = e13._observed_best_family(cand, qX, qs, ctrl, mino, seed=seed)
        out.append(dcov - mcov)
    return np.asarray(out)


def run(n_seeds: int = 10, n_controls: int = 6) -> pd.DataFrame:
    seeds = list(range(n_seeds))
    ds = load_sciplex3()
    proj = pd.read_csv(results_path(OUT, "projection.csv"))
    proj["delta"] = proj.observed_dart_minority_cov - proj.observed_mean_minority_cov
    recorded = {r.task_id: r.delta for _, r in proj.iterrows()}

    section("STAGE 1 — is the harness faithful to projection.csv?")
    ok = bad = 0
    worst = 0.0
    for _dsn, tid, _info, cand, qX, qs, ctrl, mino, seed in e13._crossline_tasks(False, [0]):
        exp = recorded.get(tid)
        if exp is None:
            continue
        _f, dcov, mcov = e13._observed_best_family(cand, qX, qs, ctrl, mino, seed=seed)
        diff = abs((dcov - mcov) - exp)
        worst = max(worst, diff)
        ok, bad = (ok + 1, bad) if diff < 1e-6 else (ok, bad + 1)
    log(f"  reproduced {ok}, mismatched {bad}, worst |diff| = {worst:.2e}")
    if bad or not ok:
        raise RuntimeError(
            "harness does not reproduce projection.csv, so a replication test on it would be "
            "meaningless. Do not interpret any number below.")
    log("  faithful.")

    section(f"STAGE 2 — hold the drug fixed, resample the seed {n_seeds}x")
    # A control must be a drug that is dominant at NO seed. Selecting on task_id alone lets a
    # drug that crosses the threshold at one seed and misses at another land in BOTH groups,
    # which would compare the dominant set against a set that partly contains it. Deduplicate
    # to (pair, drug) and subtract the dominant set.
    def _pair_drug(t):
        f = t.split(":")
        return (f[0], f[1])

    dominant = {_pair_drug(t) for t in recorded if "->" in t and recorded[t] > MARGIN}
    targets = sorted(dominant)
    controls = sorted({_pair_drug(t) for t in recorded
                       if "->" in t and 0 < recorded[t] <= MARGIN} - dominant)[:n_controls]
    log(f"  {len(targets)} recorded-dominant cross-line drugs, {len(controls)} matched controls "
        f"(controls are dominant at no seed)")

    rows = []
    for group, items in (("recorded_dominant", targets), ("control", controls)):
        for pair, drug in items:
            qline, lline = pair.split("->")
            a = _sweep(ds, qline, lline, drug, seeds)
            if not len(a):
                continue
            rec = max((v for k, v in recorded.items() if k.startswith(f"{pair}:{drug}:")),
                      default=float("nan"))
            rows.append({"group": group, "pair": pair, "drug": drug, "recorded_delta": rec,
                         "mean": float(a.mean()), "sd": float(a.std()),
                         "min": float(a.min()), "max": float(a.max()),
                         "n_dominant": int((a > MARGIN).sum()), "n_seeds": int(len(a))})
            log(f"  {group:<18} {pair}:{drug:<32} recorded {rec:+.4f}  "
                f"reseeded {a.mean():+.4f} +- {a.std():.4f}  "
                f"dominant {int((a > MARGIN).sum())}/{len(a)}")

    df = pd.DataFrame(rows)
    write_csv(df, results_path(OUT, "seed_stability.csv"))

    section("VERDICT")
    t = df[df.group == "recorded_dominant"]
    c = df[df.group == "control"]
    stable = t[t.n_dominant >= STABLE_AT]
    log(f"  recorded-dominant tasks re-tested : {len(t)}")
    log(f"    replication-stable (>= {STABLE_AT}/{n_seeds} seeds) : {len(stable)}")
    for _, r in stable.iterrows():
        log(f"      {r['pair']}:{r['drug']}  {r['mean']:+.4f} +- {r['sd']:.4f}  "
            f"{r['n_dominant']}/{r['n_seeds']}")
    if len(c):
        log(f"  matched controls (dominant at NO seed in the recorded run): {len(c)}")
        log(f"    yet they cross the same threshold in {int(c.n_dominant.min())} to "
            f"{int(c.n_dominant.max())} of {n_seeds} reseeds (median "
            f"{c.n_dominant.median():.0f})")
        log(f"    -> the threshold sits inside the noise band; a count of crossings is a "
            f"count of noise excursions.")
    return df


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-seeds", type=int, default=10)
    ap.add_argument("--n-controls", type=int, default=6)
    args = ap.parse_args()
    run(n_seeds=args.n_seeds, n_controls=args.n_controls)


if __name__ == "__main__":
    main()
