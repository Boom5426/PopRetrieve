#!/usr/bin/env python
"""Controlled heterogeneous-source experiment: mean-cosine vs coverage ranking.

For each mixture ratio alpha, build a heterogeneous target (alpha class-A +
(1-alpha) class-B) and a candidate library {covers-both (ground truth),
majority-only, minority-only, + distractors} from HELD-OUT cells. Rank the
library by (i) mean-cosine of mean-delta signatures and (ii) coverage =
-max_k energy_distance over the two subpopulations. Report the rank of the
ground-truth covers-both candidate under each scorer, averaged over seeds with
bootstrap CIs, and sweep alpha (the headline crossover figure).

Scoring here is MODEL-FREE (isolates the mean-vs-distribution variable). The
coverage score is exactly the ranking principle SubFlow uses.

    python scripts/eval_controlled_mixture.py --cell-line K562 --n-seeds 20
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from build_mixture_queries import MixtureBuilder            # noqa: E402
from gidflow.losses.distribution import energy_distance     # noqa: E402
from gidflow.metrics.ranking import retrieval_metrics       # noqa: E402

DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def _cos(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return 0.0 if na < 1e-12 or nb < 1e-12 else float(a @ b / (na * nb))


def _edist(a, b):
    if len(a) < 2 or len(b) < 2:
        return 1e6
    with torch.no_grad():
        return float(energy_distance(torch.as_tensor(a, device=DEV),
                                     torch.as_tensor(b, device=DEV)))


SCORERS = ["mean_cosine", "global_energy", "coverage_mean", "coverage_worst"]


def score_query(q):
    """Rank candidates by four scorers (higher = better), isolating the mechanism:

      mean_cosine    : cosine of mean-delta signatures            (the 'mean-out' incumbent)
      global_energy  : -energy_distance(whole cand, whole target) (K=1: any distributional distance)
      coverage_mean  : -mean_k energy over the 2 subpops          (distributional + subpop, avg agg)
      coverage_worst : -max_k  energy over the 2 subpops          (distributional + subpop, worst agg)

    Comparing these tells us whether the win comes from (a) using a distributional
    distance at all (global_energy already beats mean_cosine), or (b) specifically
    the worst-subpopulation aggregation (only coverage_worst wins)."""
    target, lab, pc = q["target"], q["target_labels"], q["pseudo_control"]
    mu_a, mu_b = target[lab == 0].mean(0), target[lab == 1].mean(0)
    T_A, T_B = target[lab == 0], target[lab == 1]
    tgt_sig = target.mean(0) - pc

    def split(P):
        m = np.linalg.norm(P - mu_a, axis=1) < np.linalg.norm(P - mu_b, axis=1)
        return P[m], P[~m]

    out = {s: {} for s in SCORERS}
    for name, P in q["candidates"].items():
        out["mean_cosine"][name] = _cos(tgt_sig, P.mean(0) - pc)
        out["global_energy"][name] = -_edist(P, target)
        P_A, P_B = split(P)
        ea, eb = _edist(P_A, T_A), _edist(P_B, T_B)
        out["coverage_mean"][name] = -0.5 * (ea + eb)
        out["coverage_worst"][name] = -max(ea, eb)
    return out


def rank_of(scores: dict, name: str) -> int:
    order = sorted(scores, key=lambda k: -scores[k])
    return order.index(name) + 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--processed", default="data/processed/sciplex3_all.pt")
    ap.add_argument("--ann-dir", default="data/annotation")
    ap.add_argument("--cell-line", default="K562")
    ap.add_argument("--class-a", default="HDAC")
    ap.add_argument("--class-b", default="JAK")
    ap.add_argument("--n-total", type=int, default=400)
    ap.add_argument("--n-distractors", type=int, default=40)
    ap.add_argument("--alphas", default="0.5,0.6,0.7,0.8,0.9")
    ap.add_argument("--n-seeds", type=int, default=20)
    ap.add_argument("--out", default="results/subflow/controlled_mixture.csv")
    args = ap.parse_args()

    mb = MixtureBuilder(args.processed, args.ann_dir, cell_line=args.cell_line,
                        class_a=args.class_a, class_b=args.class_b, n_total=args.n_total)
    print(f"[ctrl] {args.cell_line}: {args.class_a}={len(mb.rows_a)} "
          f"{args.class_b}={len(mb.rows_b)} distractors={len(mb.distractor_rows)} "
          f"lib_size={3+min(args.n_distractors,len(mb.distractor_rows))}", flush=True)

    alphas = [float(a) for a in args.alphas.split(",")]
    rows = []
    for alpha in alphas:
        hit = {s: [] for s in SCORERS}
        rnk = {s: [] for s in SCORERS}
        for s in range(args.n_seeds):
            q = mb.build(alpha, n_distractors=args.n_distractors, seed=1000 + s)
            scored = score_query(q)
            names = list(q["candidates"]); gt = names.index("covers-both")
            for sc in SCORERS:
                vals = np.array([scored[sc][n] for n in names])
                hit[sc].append(retrieval_metrics(vals[None], np.array([gt]))["hit@1"])
                rnk[sc].append(rank_of(scored[sc], "covers-both"))
        row = {"alpha": alpha}
        for sc in SCORERS:
            row[f"{sc}_hit@1"] = float(np.mean(hit[sc]))
            row[f"{sc}_rank_med"] = float(np.median(rnk[sc]))
        rows.append(row)
        print(f"  alpha={alpha:.2f} hit@1 | " + "  ".join(
            f"{sc}={row[f'{sc}_hit@1']:.2f}" for sc in SCORERS), flush=True)

    df = pd.DataFrame(rows)
    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(f"\n[ctrl] wrote {out}")
    print(df.to_string(index=False))
    print("\n=== HEADLINE (hit@1 of ground-truth 'covers-both', avg over alpha) ===")
    for sc in SCORERS:
        print(f"  {sc:16s}: {df[f'{sc}_hit@1'].mean():.2f}")
    print("\nMechanism read: mean_cosine is the incumbent; if global_energy already "
          "beats it, the win is 'distribution vs mean'; if only coverage_worst wins, "
          "the win is specifically worst-subpopulation aggregation.")


if __name__ == "__main__":
    main()
