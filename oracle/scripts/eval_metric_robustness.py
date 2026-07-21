#!/usr/bin/env python
"""Metric robustness of the divergence gate: is the 'distribution beats mean' result
specific to energy distance, or does ANY distributional distance show the same gate?

Reuses the divergence construction (minority = majority shifted by lam*(mu_B-mu_A)),
fixed well-powered N, and scores candidates GLOBALLY (K=1) with mean-cosine vs three
distributional distances: energy, RBF-MMD, sliced-Wasserstein. Ground truth = covers-both.

    python scripts/eval_metric_robustness.py --n-seeds 20
"""
from __future__ import annotations
import argparse, sys
from pathlib import Path
import numpy as np, pandas as pd, torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "scripts"))
from build_mixture_queries import MixtureBuilder                              # noqa: E402
from gidflow.losses.distribution import energy_distance, mmd_rbf, sliced_wasserstein  # noqa: E402
from gidflow.metrics.ranking import retrieval_metrics                         # noqa: E402

DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu")
METRICS = ["mean_cosine", "energy", "mmd", "sliced_w"]


def _cos(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return 0.0 if na < 1e-9 or nb < 1e-9 else float(a @ b / (na * nb))


def _cap(P, n, r):
    return P if len(P) <= n else P[r.choice(len(P), n, replace=False)]


def score(q, cap_n, seed):
    r = np.random.default_rng(seed)
    ctrl = q["pseudo_control"]; T = q["target"]
    tgt_sig = T.mean(0) - ctrl
    Tt = torch.as_tensor(_cap(T, cap_n, r), device=DEV)
    out = {m: {} for m in METRICS}
    for name, P in q["candidates"].items():
        out["mean_cosine"][name] = _cos(tgt_sig, P.mean(0) - ctrl)
        Pt = torch.as_tensor(_cap(P, cap_n, r), device=DEV)
        with torch.no_grad():
            out["energy"][name] = -float(energy_distance(Pt, Tt))
            out["mmd"][name] = -float(mmd_rbf(Pt, Tt))
            out["sliced_w"][name] = -float(sliced_wasserstein(Pt, Tt))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--processed", default="data/processed/sciplex3_all.pt")
    ap.add_argument("--cell-line", default="K562")
    ap.add_argument("--alpha", type=float, default=0.7)
    ap.add_argument("--ntot", type=int, default=800)
    ap.add_argument("--cap", type=int, default=220)
    ap.add_argument("--lams", default="0.0,0.5,0.75,1.0,1.5")
    ap.add_argument("--n-distractors", type=int, default=40)
    ap.add_argument("--n-seeds", type=int, default=20)
    ap.add_argument("--out", default="results/subflow/metric_robustness.csv")
    args = ap.parse_args()

    mb = MixtureBuilder(args.processed, cell_line=args.cell_line, n_total=args.ntot)
    Xall = mb.X
    a_build, a_cand, b_build = mb._a_build, mb._a_cand, mb._b_build
    ctrl = mb.pseudo_control
    v = (Xall[b_build].mean(0) - Xall[a_build].mean(0)).astype(np.float32)
    mu_a = Xall[a_build].mean(0)
    n_maj = int(round(args.alpha * args.ntot)); n_min = args.ntot - n_maj
    dist_names = list(mb.distractor_rows)
    lams = [float(x) for x in args.lams.split(",")]

    def pick(rows, n, r):
        return Xall[r.choice(rows, n, replace=len(rows) < n)]

    def build_q(lam, seed):
        r = np.random.default_rng(seed)
        target = np.concatenate([pick(a_build, n_maj, r),
                                 pick(a_build, n_min, r) + lam * v]).astype(np.float32)
        cb = np.concatenate([pick(a_cand, n_maj, r),
                             pick(a_cand, n_min, r) + lam * v]).astype(np.float32)
        cands = {"covers-both": cb,
                 "majority-only": pick(a_cand, args.ntot, r).astype(np.float32),
                 "minority-only": (pick(a_cand, args.ntot, r) + lam * v).astype(np.float32)}
        r.shuffle(dist_names)
        for nm in dist_names[:args.n_distractors]:
            cands[f"distractor:{nm}"] = pick(mb.distractor_rows[nm], args.ntot, r).astype(np.float32)
        return {"target": target, "pseudo_control": ctrl, "candidates": cands}

    print(f"[metric] {args.cell_line} alpha={args.alpha} cap={args.cap} lams={lams} seeds={args.n_seeds}")
    rows = []
    for lam in lams:
        div_cos = _cos(mu_a - ctrl, (mu_a + lam * v) - ctrl)
        for s in range(args.n_seeds):
            q = build_q(lam, 3000 + s)
            sc = score(q, args.cap, 5000 + s)
            names = list(q["candidates"]); gt = names.index("covers-both")
            for m in METRICS:
                vals = np.array([sc[m][n] for n in names])
                rows.append({"lam": lam, "subpop_cos": round(div_cos, 3), "metric": m,
                             "hit@1": retrieval_metrics(vals[None], np.array([gt]))["hit@1"]})
        sub = pd.DataFrame([r for r in rows if r["lam"] == lam])
        msg = "  ".join(f"{m}={sub[sub.metric==m]['hit@1'].mean():.2f}" for m in METRICS)
        print(f"  lam={lam:4.2f} (cos={div_cos:+.2f}) | {msg}", flush=True)

    df = pd.DataFrame(rows)
    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    piv = df.groupby(["subpop_cos", "metric"])["hit@1"].mean().unstack()[METRICS].sort_index()
    print("\n[metric] Hit@1 vs subpop-response similarity, per distributional distance:")
    print(piv.round(2).to_string())
    print("\nread: if energy, MMD and sliced-Wasserstein all show the same gate (advantage "
          "emerging as cos drops), the divergence characterization is metric-agnostic.")
    print(f"[metric] wrote {out}")


if __name__ == "__main__":
    main()
