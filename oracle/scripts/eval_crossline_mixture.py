#!/usr/bin/env python
"""Cross-cell-line 'population-in, mean-out' retrieval experiment (semi-real anchor).

The §3 controlled experiment built the two divergent response modes from two DRUG
classes (HDAC vs JAK) inside one cell line. Here the two modes are two real CELL
TYPES (K562 vs A549) responding to the SAME drug -- a more realistic model of a
heterogeneous single-cell sample (two cell types / clones). The cross-line
divergence is REAL and near-orthogonal (crossline_divergence.py: median cos 0.12).

For a divergent drug d* and mixture ratio alpha, the heterogeneous target is
    T = alpha * (K562 + d*)  +  (1-alpha) * (A549 + d*)          [BUILD cells]
Candidate library (HELD-OUT cells), each with its OWN matched control so the
mean-cosine signature is a drug-RESPONSE delta (baseline cell-type identity
removed -- otherwise the pure-line candidates leak the K562-vs-A549 baseline):
    covers-both   = alpha/(1-alpha) K562+d* / A549+d*   ctrl = mixture   [GROUND TRUTH]
    majority-only = pure  K562 + d*                      ctrl = K562 DMSO  (what mean prefers)
    minority-only = pure  A549 + d*                      ctrl = A549 DMSO
    distractor d' = alpha/(1-alpha) K562+d' / A549+d'    ctrl = mixture
Ground truth = covers-both (only candidate covering BOTH cell types).

Scorers (identical names to §3): mean_cosine (incumbent), global_energy,
coverage_mean, coverage_worst. Coverage splits by the KNOWN cell-line label; a
candidate missing a subpop (e.g. majority-only has no A549 cells) is penalized.

Averaged over many divergent d* drugs (not cherry-picked) and seeds, swept over
alpha -> the cross-line crossover.

    python scripts/eval_crossline_mixture.py --n-drugs 15 --n-seeds 10
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

from gidflow.data.processed import SciplexDataset          # noqa: E402
from gidflow.losses.distribution import energy_distance    # noqa: E402
from gidflow.metrics.ranking import retrieval_metrics      # noqa: E402

DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu")
SCORERS = ["mean_cosine", "global_energy", "coverage_mean", "coverage_worst"]


def _cos(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return 0.0 if na < 1e-12 or nb < 1e-12 else float(a @ b / (na * nb))


def _edist(a, b):
    if len(a) < 2 or len(b) < 2:
        return 1e6                       # missing subpop -> maximal penalty
    with torch.no_grad():
        return float(energy_distance(torch.as_tensor(a, device=DEV),
                                     torch.as_tensor(b, device=DEV)))


class CrossLineBuilder:
    def __init__(self, processed, ann_dir, line_maj="K562", line_min="A549",
                 min_cells=60, seed=0):
        self.data = SciplexDataset(processed, ann_dir)
        self.X = self.data.X.numpy()
        obs = self.data.obs
        self.rng = np.random.default_rng(seed)
        self.line_maj, self.line_min = line_maj, line_min

        line = obs["cell_line"].astype(str).to_numpy()
        drug = obs["perturbation"].astype(str).str.strip().to_numpy()
        is_ctrl = (obs["is_control"].astype(bool).to_numpy() if "is_control" in obs
                   else np.zeros(len(obs), bool))

        self.ctrl_mean = {}
        for L in (line_maj, line_min):
            cr = self.data.control_rows.get(L, np.array([], int))
            if len(cr) == 0:
                cr = np.flatnonzero((line == L) & is_ctrl)
            self.ctrl_mean[L] = self.X[cr].mean(0).astype(np.float32)

        # per (line, drug) build/cand disjoint halves
        self.pool = {line_maj: {}, line_min: {}}
        for L in (line_maj, line_min):
            m = (line == L) & ~is_ctrl
            idx = np.flatnonzero(m); d = drug[m]
            for name in pd.unique(d):
                r = idx[d == name]
                if len(r) >= min_cells:
                    p = self.rng.permutation(r); h = len(p) // 2
                    self.pool[L][name] = (p[:h], p[h:])   # (build, cand)
        self.shared = sorted(set(self.pool[line_maj]) & set(self.pool[line_min]))

    def _samp(self, rows, n, r):
        return self.X[r.choice(rows, n, replace=len(rows) < n)].astype(np.float32)

    def build(self, d_star, alpha, n_total, distractors, seed):
        r = np.random.default_rng(seed)
        n_maj = int(round(alpha * n_total)); n_min = n_total - n_maj
        Lp, Lm = self.line_maj, self.line_min
        cmix = (alpha * self.ctrl_mean[Lp] + (1 - alpha) * self.ctrl_mean[Lm]).astype(np.float32)

        def mix(drug, half):  # half: 0=build,1=cand
            a = self._samp(self.pool[Lp][drug][half], n_maj, r)
            b = self._samp(self.pool[Lm][drug][half], n_min, r)
            X = np.concatenate([a, b], 0)
            lab = np.concatenate([np.zeros(n_maj, int), np.ones(n_min, int)])
            return X, lab

        target, tlab = mix(d_star, 0)
        cb, cblab = mix(d_star, 1)
        maj = self._samp(self.pool[Lp][d_star][1], n_total, r)
        mino = self._samp(self.pool[Lm][d_star][1], n_total, r)

        cands = {
            "covers-both": (cb, cblab, cmix),
            "majority-only": (maj, np.zeros(n_total, int), self.ctrl_mean[Lp]),
            "minority-only": (mino, np.ones(n_total, int), self.ctrl_mean[Lm]),
        }
        pool = [d for d in self.shared if d != d_star]
        r.shuffle(pool)
        for d in pool[:distractors]:
            X, lab = mix(d, 1)
            cands[f"distractor:{d}"] = (X, lab, cmix)
        return {"target": target, "tlab": tlab, "ctrl_T": cmix, "cands": cands}

    def divergent_drugs(self, csv, n, min_cells_pool):
        """Pick d* drugs: reliable + gate-clearing, most divergent first, w/ enough cells."""
        ok = [d for d in self.shared
              if min(len(self.pool[self.line_maj][d][0]), len(self.pool[self.line_min][d][0]))
              >= min_cells_pool // 2]
        p = Path(csv)
        if p.exists():
            df = pd.read_csv(p)
            df = df[df.get("clears_gate", df["cross_cos"] < 0.9) & df["drug"].isin(ok)]
            return df.sort_values("cross_cos")["drug"].head(n).tolist()
        return ok[:n]


def score(q):
    T, tlab, cT = q["target"], q["tlab"], q["ctrl_T"]
    tsig = T.mean(0) - cT
    T0, T1 = T[tlab == 0], T[tlab == 1]
    out = {s: {} for s in SCORERS}
    for name, (P, plab, cP) in q["cands"].items():
        out["mean_cosine"][name] = _cos(tsig, P.mean(0) - cP)
        out["global_energy"][name] = -_edist(P, T)
        e0, e1 = _edist(P[plab == 0], T0), _edist(P[plab == 1], T1)
        out["coverage_mean"][name] = -0.5 * (e0 + e1)
        out["coverage_worst"][name] = -max(e0, e1)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--processed", default="data/processed/sciplex3_all.pt")
    ap.add_argument("--ann-dir", default="data/annotation")
    ap.add_argument("--line-maj", default="K562")
    ap.add_argument("--line-min", default="A549")
    ap.add_argument("--n-total", type=int, default=200)
    ap.add_argument("--n-distractors", type=int, default=40)
    ap.add_argument("--alphas", default="0.5,0.6,0.7,0.8,0.9")
    ap.add_argument("--n-drugs", type=int, default=15)
    ap.add_argument("--n-seeds", type=int, default=10)
    ap.add_argument("--div-csv", default="results/subflow/crossline_divergence.csv")
    ap.add_argument("--out", default="results/subflow/crossline_mixture.csv")
    args = ap.parse_args()

    mb = CrossLineBuilder(args.processed, args.ann_dir, args.line_maj, args.line_min)
    d_stars = mb.divergent_drugs(args.div_csv, args.n_drugs, args.n_total)
    alphas = [float(a) for a in args.alphas.split(",")]
    print(f"[xline] {args.line_maj}(maj)+{args.line_min}(min) shared={len(mb.shared)} "
          f"d*={len(d_stars)} drugs alphas={alphas} seeds={args.n_seeds} "
          f"lib={3+min(args.n_distractors, len(mb.shared)-1)} dev={DEV}", flush=True)
    print(f"[xline] d* drugs: {', '.join(d_stars[:8])}{' ...' if len(d_stars) > 8 else ''}")

    rows = []
    for alpha in alphas:
        hit = {s: [] for s in SCORERS}
        for d_star in d_stars:
            for s in range(args.n_seeds):
                q = mb.build(d_star, alpha, args.n_total, args.n_distractors, 1000 + s)
                sc = score(q)
                names = list(q["cands"]); gt = names.index("covers-both")
                for scr in SCORERS:
                    vals = np.array([sc[scr][n] for n in names])
                    hit[scr].append(retrieval_metrics(vals[None], np.array([gt]))["hit@1"])
        row = {"alpha": alpha}
        for scr in SCORERS:
            row[f"{scr}_hit@1"] = float(np.mean(hit[scr]))
        rows.append(row)
        print(f"  alpha={alpha:.2f} hit@1 | " + "  ".join(
            f"{scr}={row[f'{scr}_hit@1']:.2f}" for scr in SCORERS), flush=True)

    df = pd.DataFrame(rows)
    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(f"\n[xline] wrote {out}")
    print(df.to_string(index=False))
    print("\n=== HEADLINE (hit@1 of ground-truth 'covers-both', avg over alpha) ===")
    for scr in SCORERS:
        print(f"  {scr:16s}: {df[f'{scr}_hit@1'].mean():.2f}")
    print("\nRead: if mean_cosine stays low while global_energy/coverage stay high, the "
          "'population-in, mean-out' failure REPLICATES on a real two-cell-type mixture "
          "-- the divergent modes come from real cell types, not two different drugs (§3).")


if __name__ == "__main__":
    main()
