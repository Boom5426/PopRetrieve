#!/usr/bin/env python
"""Characterization axis #1: POWER. When is distribution-aware ranking worth it?

Reuses the controlled K562 HDAC/JAK mixture (ground truth = covers-both), but
subsamples each subpopulation to N cells/drug before scoring. Sweeping N shows
the distribution-aware advantage over mean-cosine EMERGING with cell count — and
vanishing at CD34-like depths (~15-60 cells/subpop), which is exactly why the
CD34+ natural-heterogeneity test came back at the noise floor.

    python scripts/eval_power_sweep.py --n-seeds 20
"""
from __future__ import annotations
import argparse, sys
from pathlib import Path
import numpy as np, pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "scripts"))
from build_mixture_queries import MixtureBuilder                 # noqa: E402
from eval_controlled_mixture import score_query, SCORERS         # noqa: E402
from gidflow.metrics.ranking import retrieval_metrics            # noqa: E402


def subsample(q, N, seed):
    r = np.random.default_rng(seed)
    lab = q["target_labels"]; T = q["target"]
    keep = []
    for c in (0, 1):
        idx = np.where(lab == c)[0]
        keep.append(r.choice(idx, min(N, len(idx)), replace=False))
    keep = np.concatenate(keep)
    q2 = dict(q); q2["target"] = T[keep]; q2["target_labels"] = lab[keep]
    q2["candidates"] = {name: (P[r.choice(len(P), min(2 * N, len(P)), replace=False)])
                        for name, P in q["candidates"].items()}
    return q2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--processed", default="data/processed/sciplex3_all.pt")
    ap.add_argument("--cell-line", default="K562")
    ap.add_argument("--alpha", type=float, default=0.7)
    ap.add_argument("--Ns", default="15,30,60,120,240")
    ap.add_argument("--n-seeds", type=int, default=20)
    ap.add_argument("--out", default="results/subflow/power_sweep.csv")
    args = ap.parse_args()

    Ns = [int(x) for x in args.Ns.split(",")]
    mb = MixtureBuilder(args.processed, cell_line=args.cell_line, n_total=1600)
    print(f"[power] {args.cell_line} HDAC/JAK alpha={args.alpha}  Ns={Ns}  seeds={args.n_seeds}")
    rows = []
    for N in Ns:
        for s in range(args.n_seeds):
            q = mb.build(args.alpha, n_distractors=40, seed=1000 + s)
            q2 = subsample(q, N, seed=2000 + s)
            sc = score_query(q2)
            names = list(q2["candidates"]); gt = names.index("covers-both")
            for scorer in SCORERS:
                vals = np.array([sc[scorer][n] for n in names])
                rows.append({"N": N, "scorer": scorer,
                             "hit@1": retrieval_metrics(vals[None], np.array([gt]))["hit@1"]})
        sub = pd.DataFrame([r for r in rows if r["N"] == N])
        msg = "  ".join(f"{s}={sub[sub.scorer==s]['hit@1'].mean():.2f}" for s in SCORERS)
        print(f"  N={N:4d} cells/subpop | hit@1  {msg}", flush=True)

    df = pd.DataFrame(rows)
    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    piv = df.groupby(["N", "scorer"])["hit@1"].mean().unstack()[SCORERS]
    print("\n[power] Hit@1 vs cells/subpop (ground-truth covers-both):")
    print(piv.round(2).to_string())
    gap = piv["global_energy"] - piv["mean_cosine"]
    print("\n[power] distribution-aware advantage (global_energy - mean_cosine) by N:")
    print(gap.round(2).to_string())
    print(f"\n[power] wrote {out}")


if __name__ == "__main__":
    main()
