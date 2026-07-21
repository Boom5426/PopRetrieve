#!/usr/bin/env python
"""Frangieh NATURAL divergent-source retrieval: 'population-in, mean-out' on a real
melanoma sample that mixes immune microenvironments. Subpops = immune CONDITIONS
(Control / IFN-gamma / Co-culture); the perturbation library = 248 CRISPR KOs.

This is the fully-natural rung above cross-line: a real tumor genuinely contains cells
under different immune pressure, and immune-evasion KOs act differently across them
(context-divergent, frangieh_divergence.py). Same construction as eval_crossline_mixture.py
(per-candidate matched-control delta space; coverage splits by the KNOWN condition label).

    python scripts/eval_frangieh_mixture.py --cond-maj Control --cond-min IFNγ
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
from gidflow.losses.distribution import energy_distance    # noqa: E402
from gidflow.metrics.ranking import retrieval_metrics      # noqa: E402

DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu")
SCORERS = ["mean_cosine", "global_energy", "coverage_mean", "coverage_worst"]


def _cos(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return 0.0 if na < 1e-12 or nb < 1e-12 else float(a @ b / (na * nb))


def _edist(a, b):
    if len(a) < 2 or len(b) < 2:
        return 1e6
    with torch.no_grad():
        return float(energy_distance(torch.as_tensor(a, device=DEV),
                                     torch.as_tensor(b, device=DEV)))


class FrangiehBuilder:
    def __init__(self, npz, cond_maj="Control", cond_min="IFNγ", min_cells=60, seed=0):
        d = np.load(npz, allow_pickle=True)
        self.X = d["X"]; cond = d["condition"].astype(str)
        pert = d["perturbation"].astype(str); is_ctrl = d["is_control"]
        self.rng = np.random.default_rng(seed)
        self.cmaj, self.cmin = cond_maj, cond_min

        self.ctrl_mean = {}
        for L in (cond_maj, cond_min):
            cr = np.flatnonzero((cond == L) & is_ctrl)
            self.ctrl_mean[L] = self.X[cr].mean(0).astype(np.float32)

        self.pool = {cond_maj: {}, cond_min: {}}
        for L in (cond_maj, cond_min):
            m = (cond == L) & ~is_ctrl
            idx = np.flatnonzero(m); g = pert[m]
            for name in pd.unique(g):
                r = idx[g == name]
                if len(r) >= min_cells:
                    p = self.rng.permutation(r); h = len(p) // 2
                    self.pool[L][name] = (p[:h], p[h:])
        self.shared = sorted(set(self.pool[cond_maj]) & set(self.pool[cond_min]))

    def _samp(self, rows, n, r):
        return self.X[r.choice(rows, n, replace=len(rows) < n)].astype(np.float32)

    def build(self, g_star, alpha, n_total, distractors, seed):
        r = np.random.default_rng(seed)
        n_maj = int(round(alpha * n_total)); n_min = n_total - n_maj
        Lp, Lm = self.cmaj, self.cmin
        cmix = (alpha * self.ctrl_mean[Lp] + (1 - alpha) * self.ctrl_mean[Lm]).astype(np.float32)

        def mix(ko, half):
            a = self._samp(self.pool[Lp][ko][half], n_maj, r)
            b = self._samp(self.pool[Lm][ko][half], n_min, r)
            return np.concatenate([a, b], 0), np.concatenate([np.zeros(n_maj, int), np.ones(n_min, int)])

        target, tlab = mix(g_star, 0)
        cb, cblab = mix(g_star, 1)
        maj = self._samp(self.pool[Lp][g_star][1], n_total, r)
        mino = self._samp(self.pool[Lm][g_star][1], n_total, r)
        cands = {"covers-both": (cb, cblab, cmix),
                 "majority-only": (maj, np.zeros(n_total, int), self.ctrl_mean[Lp]),
                 "minority-only": (mino, np.ones(n_total, int), self.ctrl_mean[Lm])}
        pool = [g for g in self.shared if g != g_star]; r.shuffle(pool)
        for g in pool[:distractors]:
            X, lab = mix(g, 1); cands[f"distractor:{g}"] = (X, lab, cmix)
        return {"target": target, "tlab": tlab, "ctrl_T": cmix, "cands": cands}

    def divergent_kos(self, csv, n, min_cells_pool):
        ok = [g for g in self.shared
              if min(len(self.pool[self.cmaj][g][0]), len(self.pool[self.cmin][g][0])) >= min_cells_pool // 2]
        p = Path(csv)
        if p.exists():
            df = pd.read_csv(p)
            df = df[df.get("clears_gate", df["cross_cos"] < 0.9) & df["ko"].isin(ok)]
            return df.sort_values("cross_cos")["ko"].head(n).tolist()
        return ok[:n]


def score(q):
    T, tlab, cT = q["target"], q["tlab"], q["ctrl_T"]
    tsig = T.mean(0) - cT; T0, T1 = T[tlab == 0], T[tlab == 1]
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
    ap.add_argument("--npz", default="data/processed/frangieh_hvg.npz")
    ap.add_argument("--cond-maj", default="Control")
    ap.add_argument("--cond-min", default="IFNγ")
    ap.add_argument("--n-total", type=int, default=200)
    ap.add_argument("--n-distractors", type=int, default=40)
    ap.add_argument("--alphas", default="0.5,0.6,0.7,0.8,0.9")
    ap.add_argument("--n-drugs", type=int, default=15)
    ap.add_argument("--n-seeds", type=int, default=10)
    ap.add_argument("--div-csv", default="results/subflow/frangieh_divergence.csv")
    ap.add_argument("--out", default="results/subflow/frangieh_mixture.csv")
    args = ap.parse_args()

    mb = FrangiehBuilder(args.npz, args.cond_maj, args.cond_min)
    gs = mb.divergent_kos(args.div_csv, args.n_drugs, args.n_total)
    alphas = [float(a) for a in args.alphas.split(",")]
    print(f"[frangieh-xp] {args.cond_maj}(maj)+{args.cond_min}(min) shared={len(mb.shared)} "
          f"KO*={len(gs)} alphas={alphas} seeds={args.n_seeds} "
          f"lib={3+min(args.n_distractors, len(mb.shared)-1)} dev={DEV}", flush=True)
    print(f"[frangieh-xp] divergent KOs: {', '.join(gs[:10])}")

    rows = []
    for alpha in alphas:
        hit = {s: [] for s in SCORERS}
        for g in gs:
            for s in range(args.n_seeds):
                q = mb.build(g, alpha, args.n_total, args.n_distractors, 1000 + s)
                sc = score(q); names = list(q["cands"]); gt = names.index("covers-both")
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
    print(f"\n[frangieh-xp] wrote {out}")
    print("=== HEADLINE (hit@1 of 'covers-both', avg over alpha) ===")
    for scr in SCORERS:
        print(f"  {scr:16s}: {df[f'{scr}_hit@1'].mean():.2f}")
    print("\nRead: mean_cosine low + global_energy/coverage high => the mean-out failure "
          "triggers on a REAL tumor sample mixing immune microenvironments (natural, "
          "well-powered divergent subpopulations) -- the strongest rung of the anchor ladder.")


if __name__ == "__main__":
    main()
