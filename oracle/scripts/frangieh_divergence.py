#!/usr/bin/env python
"""Frangieh NATURAL context-divergence probe (model-free): does the SAME CRISPR KO
have a divergent effect across immune conditions (Control / IFN-gamma / Co-culture)?
This is the fully-natural analog of crossline_divergence.py -- the subpopulations are
biologically-meaningful immune STATES within one melanoma system, not mixed cell lines.

For each KO g present in both conditions, per-condition response delta (non-targeting
baseline of THAT condition removed):
    d_A(g) = mean(g | condA) - mean(control | condA)
    d_B(g) = mean(g | condB) - mean(control | condB)
    cross_cos = cos(d_A, d_B)          # <1 => the KO's effect is context-dependent
with a within-condition split-half reliability floor (a KO counts only if its effect
is reliably estimated in BOTH conditions -- the CD34 lesson: don't call noise divergence).

    python scripts/frangieh_divergence.py --cond-a Control --cond-b IFNγ
"""
from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
import pandas as pd


def _cos(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return 0.0 if na < 1e-12 or nb < 1e-12 else float(a @ b / (na * nb))


def split_half(X, rows, ctrl_mean, rng, n_rep=5):
    if len(rows) < 8:
        return np.nan
    v = []
    for _ in range(n_rep):
        p = rng.permutation(rows); h = len(p) // 2
        v.append(_cos(X[p[:h]].mean(0) - ctrl_mean, X[p[h:]].mean(0) - ctrl_mean))
    return float(np.mean(v))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--npz", default="data/processed/frangieh_hvg.npz")
    ap.add_argument("--cond-a", default="Control")
    ap.add_argument("--cond-b", default="IFNγ")
    ap.add_argument("--min-cells", type=int, default=40)
    ap.add_argument("--gate", type=float, default=0.9)
    ap.add_argument("--rel-floor", type=float, default=0.5)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="results/subflow/frangieh_divergence.csv")
    args = ap.parse_args()

    d = np.load(args.npz, allow_pickle=True)
    X = d["X"]; cond = d["condition"].astype(str); pert = d["perturbation"].astype(str)
    is_ctrl = d["is_control"]
    rng = np.random.default_rng(args.seed)
    A, B = args.cond_a, args.cond_b

    ctrl = {}
    for L in (A, B):
        cr = np.flatnonzero((cond == L) & is_ctrl)
        if len(cr) == 0:
            raise SystemExit(f"no non-targeting control cells in condition {L}")
        ctrl[L] = X[cr].mean(0); print(f"[frangieh] {L}: control(non-targeting) cells = {len(cr)}")

    def ko_rows(L):
        m = (cond == L) & ~is_ctrl
        idx = np.flatnonzero(m); g = pert[m]
        return {name: idx[g == name] for name in pd.unique(g)
                if (idx[g == name]).size >= args.min_cells}

    ra, rb = ko_rows(A), ko_rows(B)
    shared = sorted(set(ra) & set(rb))
    print(f"[frangieh] KOs w/ >={args.min_cells} cells: {A}={len(ra)} {B}={len(rb)} shared={len(shared)}")

    recs = []
    for g in shared:
        dA = X[ra[g]].mean(0) - ctrl[A]; dB = X[rb[g]].mean(0) - ctrl[B]
        recs.append({"ko": g, "n_a": len(ra[g]), "n_b": len(rb[g]),
                     "eff_a": float(np.linalg.norm(dA)), "eff_b": float(np.linalg.norm(dB)),
                     "cross_cos": _cos(dA, dB),
                     "rel_a": split_half(X, ra[g], ctrl[A], rng),
                     "rel_b": split_half(X, rb[g], ctrl[B], rng)})
    df = pd.DataFrame(recs)
    df["reliable"] = (df.rel_a >= args.rel_floor) & (df.rel_b >= args.rel_floor)
    df["clears_gate"] = df.reliable & (df.cross_cos < args.gate)
    df = df.sort_values("cross_cos").reset_index(drop=True)
    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)

    rel = df[df.reliable]
    print(f"\n========== FRANGIEH CONTEXT DIVERGENCE: {A} vs {B} ==========")
    print(f"shared KOs                          : {len(df)}")
    print(f"  reliable effect in BOTH conditions: {len(rel)} (split-half cos >= {args.rel_floor})")
    if len(rel):
        print(f"within-condition reliability (med)  : rel_a={rel.rel_a.median():.2f} rel_b={rel.rel_b.median():.2f}")
        print(f"cross-condition response cos (med)  : {rel.cross_cos.median():.2f} "
              f"[{rel.cross_cos.min():.2f}, {rel.cross_cos.max():.2f}]")
        n = int((rel.cross_cos < args.gate).sum())
        print(f"clear the {args.gate} gate (reliable)     : {n}/{len(rel)} = {n/len(rel):.0%}")
        cols = ["ko", "n_a", "n_b", "eff_a", "eff_b", "cross_cos", "rel_a", "rel_b"]
        print("\nmost context-divergent reliable KOs (low cross-condition cos):")
        print(rel.sort_values("cross_cos").head(15)[cols].to_string(
            index=False, float_format=lambda x: f"{x:.2f}"))
    print("=" * 60)
    print(f"[frangieh] wrote {out}")


if __name__ == "__main__":
    main()
