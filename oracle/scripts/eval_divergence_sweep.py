#!/usr/bin/env python
"""Characterization axis #2: DIVERGENCE (the binding one). When is distribution-aware
ranking worth it?

Fixed, well-powered cell counts; sweep how DIFFERENT the two subpopulations'
drug responses are. Minority cells = majority(class-A) cells shifted by lam*(mu_B-mu_A),
so lam=0 => subpops identical (homogeneous response, no heterogeneity), lam>=1 =>
fully divergent (orthogonal-ish). Ground truth = covers-both. Shows the advantage of
distribution-aware over mean-cosine EMERGING with subpop divergence and vanishing when
subpops respond alike -- which is where the real CD34+ natural lineages sit.

    python scripts/eval_divergence_sweep.py --n-seeds 20
"""
from __future__ import annotations
import argparse, sys
from pathlib import Path
import numpy as np, pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "scripts"))
from build_mixture_queries import MixtureBuilder                 # noqa: E402
from eval_controlled_mixture import score_query, SCORERS, _cos   # noqa: E402
from gidflow.metrics.ranking import retrieval_metrics            # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--processed", default="data/processed/sciplex3_all.pt")
    ap.add_argument("--cell-line", default="K562")
    ap.add_argument("--alpha", type=float, default=0.7)
    ap.add_argument("--ntot", type=int, default=800)
    ap.add_argument("--lams", default="0.0,0.25,0.5,0.75,1.0,1.5")
    ap.add_argument("--n-distractors", type=int, default=40)
    ap.add_argument("--n-seeds", type=int, default=20)
    ap.add_argument("--out", default="results/subflow/divergence_sweep.csv")
    args = ap.parse_args()

    mb = MixtureBuilder(args.processed, cell_line=args.cell_line, n_total=args.ntot)
    Xall = mb.X
    a_build, a_cand, b_build = mb._a_build, mb._a_cand, mb._b_build
    ctrl = mb.pseudo_control
    mu_a = Xall[a_build].mean(0); mu_b = Xall[b_build].mean(0)
    v = (mu_b - mu_a).astype(np.float32)                         # divergence direction
    n_maj = int(round(args.alpha * args.ntot)); n_min = args.ntot - n_maj
    dist_names = list(mb.distractor_rows)
    lams = [float(x) for x in args.lams.split(",")]
    print(f"[div] {args.cell_line} alpha={args.alpha} ntot={args.ntot} "
          f"n_min(minority cells)={n_min}  lams={lams}  seeds={args.n_seeds}")

    def pick(rows, n, r):
        return Xall[r.choice(rows, n, replace=len(rows) < n)]

    def build_q(lam, seed):
        r = np.random.default_rng(seed)
        maj_t = pick(a_build, n_maj, r)
        min_t = pick(a_build, n_min, r) + lam * v
        target = np.concatenate([maj_t, min_t]).astype(np.float32)
        lab = np.concatenate([np.zeros(n_maj, int), np.ones(n_min, int)])
        cb = np.concatenate([pick(a_cand, n_maj, r), pick(a_cand, n_min, r) + lam * v]).astype(np.float32)
        cands = {"covers-both": cb,
                 "majority-only": pick(a_cand, args.ntot, r).astype(np.float32),
                 "minority-only": (pick(a_cand, args.ntot, r) + lam * v).astype(np.float32)}
        r.shuffle(dist_names)
        for nm in dist_names[:args.n_distractors]:
            cands[f"distractor:{nm}"] = pick(mb.distractor_rows[nm], args.ntot, r).astype(np.float32)
        return {"target": target, "target_labels": lab, "pseudo_control": ctrl,
                "candidates": cands}

    rows = []
    for lam in lams:
        div_cos = _cos(mu_a - ctrl, (mu_a + lam * v) - ctrl)     # subpop signature cosine
        for s in range(args.n_seeds):
            q = build_q(lam, 3000 + s)
            sc = score_query(q)
            names = list(q["candidates"]); gt = names.index("covers-both")
            for scorer in SCORERS:
                vals = np.array([sc[scorer][n] for n in names])
                rows.append({"lam": lam, "subpop_cos": round(div_cos, 3), "scorer": scorer,
                             "hit@1": retrieval_metrics(vals[None], np.array([gt]))["hit@1"]})
        sub = pd.DataFrame([r for r in rows if r["lam"] == lam])
        msg = "  ".join(f"{s}={sub[sub.scorer==s]['hit@1'].mean():.2f}" for s in SCORERS)
        print(f"  lam={lam:4.2f} (subpop cos={div_cos:+.2f}) | hit@1  {msg}", flush=True)

    df = pd.DataFrame(rows)
    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    piv = df.groupby(["subpop_cos", "scorer"])["hit@1"].mean().unstack()[SCORERS]
    print("\n[div] Hit@1 vs subpop-response similarity (cos=1 -> identical subpops):")
    print(piv.round(2).to_string())
    print("\n[div] distribution-aware advantage (global_energy - mean_cosine):")
    print((piv["global_energy"] - piv["mean_cosine"]).round(2).to_string())
    print(f"\n[div] wrote {out}")
    print("read: advantage vanishes as subpops become similar (cos->1); CD34+ natural "
          "lineages sit near cos~1 (responses alike) -> no advantage, as observed.")


if __name__ == "__main__":
    main()
