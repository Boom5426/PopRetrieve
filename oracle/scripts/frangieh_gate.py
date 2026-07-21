#!/usr/bin/env python
"""Per-KO test of the §8 DIVERGENCE GATE on natural Frangieh data: does each KO's
mean-out failure scale with its context-divergence? Aggregate hit@1 is diluted
(most KOs sit near the gate); the clean signal is per-KO.

For each reliable KO, at a fixed well-powered alpha, over many seeds: mean_cosine
hit@1 and global_energy hit@1 of covers-both, plus their gap. Join with the KO's
cross-condition cos (frangieh_divergence.py) and test: is a LOWER cos (more divergent)
associated with a LARGER distributional advantage? Prediction (§8): yes.

    python scripts/frangieh_gate.py --cond-maj Control --cond-min IFNγ
"""
from __future__ import annotations
import argparse
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from eval_frangieh_mixture import FrangiehBuilder, score, SCORERS  # noqa: E402
from gidflow.metrics.ranking import retrieval_metrics             # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--npz", default="data/processed/frangieh_hvg.npz")
    ap.add_argument("--cond-maj", default="Control")
    ap.add_argument("--cond-min", default="IFNγ")
    ap.add_argument("--div-csv", default="results/subflow/frangieh_divergence.csv")
    ap.add_argument("--alpha", type=float, default=0.7)
    ap.add_argument("--n-total", type=int, default=200)
    ap.add_argument("--n-distractors", type=int, default=40)
    ap.add_argument("--n-seeds", type=int, default=20)
    ap.add_argument("--rel-floor", type=float, default=0.5)
    ap.add_argument("--out", default="results/subflow/frangieh_gate.csv")
    args = ap.parse_args()

    mb = FrangiehBuilder(args.npz, args.cond_maj, args.cond_min)
    div = pd.read_csv(args.div_csv).set_index("ko")
    # reliable KOs with enough cells per half for a well-powered query
    kos = [g for g in mb.shared
           if g in div.index and bool(div.loc[g, "reliable"])
           and min(len(mb.pool[args.cond_maj][g][0]), len(mb.pool[args.cond_min][g][0])) >= args.n_total // 2]
    print(f"[gate] {args.cond_maj}+{args.cond_min}: {len(kos)} reliable well-powered KOs, "
          f"alpha={args.alpha}, seeds={args.n_seeds}", flush=True)

    rows = []
    for g in kos:
        hit = {s: [] for s in SCORERS}
        for s in range(args.n_seeds):
            q = mb.build(g, args.alpha, args.n_total, args.n_distractors, 2000 + s)
            sc = score(q); names = list(q["cands"]); gt = names.index("covers-both")
            for scr in SCORERS:
                vals = np.array([sc[scr][n] for n in names])
                hit[scr].append(retrieval_metrics(vals[None], np.array([gt]))["hit@1"])
        rows.append({"ko": g, "cross_cos": float(div.loc[g, "cross_cos"]),
                     "eff_min": float(div.loc[g, "eff_b"]),
                     "mean_cosine": float(np.mean(hit["mean_cosine"])),
                     "global_energy": float(np.mean(hit["global_energy"])),
                     "advantage": float(np.mean(hit["global_energy"]) - np.mean(hit["mean_cosine"]))})
    df = pd.DataFrame(rows).sort_values("cross_cos").reset_index(drop=True)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out, index=False)

    print("\nper-KO (sorted by context-divergence; low cos = more divergent):")
    print(df.to_string(index=False, float_format=lambda x: f"{x:.2f}"))
    rho, p = spearmanr(df["cross_cos"], df["advantage"])
    print(f"\nSpearman(cross_cos, distributional advantage) = {rho:+.2f}  (p={p:.3f})")
    print("  §8 gate predicts NEGATIVE: more divergent (lower cos) -> larger advantage.")
    div_lo = df[df.cross_cos < 0.5]; div_hi = df[df.cross_cos >= 0.5]
    if len(div_lo) and len(div_hi):
        print(f"\n  strongly divergent (cos<0.5, n={len(div_lo)}): "
              f"mean={div_lo.mean_cosine.mean():.2f} energy={div_lo.global_energy.mean():.2f} "
              f"adv={div_lo.advantage.mean():+.2f}")
        print(f"  moderate (cos>=0.5, n={len(div_hi)}):          "
              f"mean={div_hi.mean_cosine.mean():.2f} energy={div_hi.global_energy.mean():.2f} "
              f"adv={div_hi.advantage.mean():+.2f}")
    print(f"[gate] wrote {args.out}")


if __name__ == "__main__":
    main()
