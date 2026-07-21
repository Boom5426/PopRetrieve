#!/usr/bin/env python
"""Cross-cell-line drug-response DIVERGENCE probe (model-free, zero-download).

Question that gates the whole "real divergent source" experiment: when the SAME
drug hits two different cell lines (K562 vs A549), do the two lines respond
DIVERGENTLY enough to clear our failure gate (subpop-response cos < ~0.9)?

For each drug present in BOTH lines we compute the per-line response direction in
2000-HVG log space, with the cell-line BASELINE removed (so this measures drug
RESPONSE divergence, not baseline-transcriptome divergence):

    d_K(g) = mean(K562 + drug) - mean(K562 DMSO)
    d_A(g) = mean(A549 + drug) - mean(A549 DMSO)
    cross_cos = cos(d_K, d_A)          # <1 => the two lines respond differently

To avoid calling sampling noise "divergence" (the CD34 lesson), we also compute a
within-line split-half reliability floor for each line/drug: cos of two disjoint
halves' response directions. A drug's cross-line divergence is REAL only if both
lines have a reliable effect (within-line cos high) AND cross_cos is clearly below
that reliability and below the 0.9 gate.

    python scripts/crossline_divergence.py --line-a K562 --line-b A549
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gidflow.data.processed import SciplexDataset  # noqa: E402


def _cos(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return 0.0 if na < 1e-12 or nb < 1e-12 else float(a @ b / (na * nb))


def split_half_reliability(X, rows, ctrl_mean, rng, n_rep=5):
    """Mean cos between two disjoint-half response directions (within-line noise floor)."""
    if len(rows) < 8:
        return np.nan
    vals = []
    for _ in range(n_rep):
        p = rng.permutation(rows)
        h = len(p) // 2
        d1 = X[p[:h]].mean(0) - ctrl_mean
        d2 = X[p[h:]].mean(0) - ctrl_mean
        vals.append(_cos(d1, d2))
    return float(np.mean(vals))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--processed", default="data/processed/sciplex3_all.pt")
    ap.add_argument("--ann-dir", default="data/annotation")
    ap.add_argument("--line-a", default="K562")
    ap.add_argument("--line-b", default="A549")
    ap.add_argument("--min-cells", type=int, default=30,
                    help="min treated cells per (line,drug) to include")
    ap.add_argument("--gate", type=float, default=0.9,
                    help="divergence gate: cross-line cos below this = failure can trigger")
    ap.add_argument("--rel-floor", type=float, default=0.5,
                    help="min within-line split-half cos for the effect to be 'reliable'")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="results/subflow/crossline_divergence.csv")
    args = ap.parse_args()

    data = SciplexDataset(args.processed, args.ann_dir)
    X = data.X.numpy()
    obs = data.obs
    rng = np.random.default_rng(args.seed)

    line = obs["cell_line"].astype(str).to_numpy()
    drug = obs["perturbation"].astype(str).str.strip().to_numpy()
    is_ctrl = (obs["is_control"].astype(bool).to_numpy() if "is_control" in obs
               else np.zeros(len(obs), bool))

    A, B = args.line_a, args.line_b
    # per-line DMSO control mean (baseline to subtract)
    ctrl = {}
    for L in (A, B):
        cr = data.control_rows.get(L, np.array([], int))
        if len(cr) == 0:  # fall back to any is_control cell in that line
            cr = np.flatnonzero((line == L) & is_ctrl)
        if len(cr) == 0:
            raise SystemExit(f"no control cells for line {L}")
        ctrl[L] = X[cr].mean(0)
        print(f"[probe] {L}: control cells = {len(cr)}")

    def line_drug_rows(L):
        m = (line == L) & ~is_ctrl
        d = drug[m]
        idx = np.flatnonzero(m)
        out = {}
        for name in pd.unique(d):
            r = idx[d == name]
            if len(r) >= args.min_cells:
                out[name] = r
        return out

    rows_a, rows_b = line_drug_rows(A), line_drug_rows(B)
    shared = sorted(set(rows_a) & set(rows_b))
    print(f"[probe] drugs w/ >={args.min_cells} cells: {A}={len(rows_a)} {B}={len(rows_b)} "
          f"shared={len(shared)}")
    if not shared:
        raise SystemExit("no shared drugs -- cannot compute cross-line divergence")

    recs = []
    for name in shared:
        ra, rb = rows_a[name], rows_b[name]
        dA = X[ra].mean(0) - ctrl[A]
        dB = X[rb].mean(0) - ctrl[B]
        recs.append({
            "drug": name, "n_a": len(ra), "n_b": len(rb),
            "eff_a": float(np.linalg.norm(dA)), "eff_b": float(np.linalg.norm(dB)),
            "cross_cos": _cos(dA, dB),
            "rel_a": split_half_reliability(X, ra, ctrl[A], rng),
            "rel_b": split_half_reliability(X, rb, ctrl[B], rng),
        })
    df = pd.DataFrame(recs)
    # a drug's cross-line divergence is trustworthy only if BOTH lines' effects are reliable
    df["reliable"] = (df["rel_a"] >= args.rel_floor) & (df["rel_b"] >= args.rel_floor)
    df["clears_gate"] = df["reliable"] & (df["cross_cos"] < args.gate)
    df = df.sort_values("cross_cos").reset_index(drop=True)

    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)

    rel = df[df["reliable"]]
    print("\n================= CROSS-LINE DIVERGENCE SUMMARY =================")
    print(f"shared drugs                         : {len(df)}")
    print(f"  with reliable effect in BOTH lines : {len(rel)} "
          f"(within-line split-half cos >= {args.rel_floor})")
    if len(rel):
        print(f"within-line reliability (floor)      : "
              f"median rel_a={rel.rel_a.median():.2f} rel_b={rel.rel_b.median():.2f}")
        print(f"cross-line response cos (reliable)   : "
              f"median={rel.cross_cos.median():.2f}  "
              f"[min={rel.cross_cos.min():.2f} max={rel.cross_cos.max():.2f}]")
        n_gate = int((rel.cross_cos < args.gate).sum())
        print(f"clear the {args.gate} gate (reliable)      : "
              f"{n_gate}/{len(rel)} = {n_gate/len(rel):.0%}")
        print(f"cross-line cos MUCH below reliability: "
              f"{int((rel.cross_cos < rel[['rel_a','rel_b']].min(1) - 0.2).sum())}/{len(rel)} "
              f"(cross_cos < min(rel_a,rel_b) - 0.2)")
        print("\nmost divergent reliable drugs (low cross-line cos):")
        cols = ["drug", "n_a", "n_b", "eff_a", "eff_b", "cross_cos", "rel_a", "rel_b"]
        print(rel.sort_values("cross_cos").head(12)[cols].to_string(
            index=False, float_format=lambda x: f"{x:.2f}"))
        print("\nmost CONCORDANT reliable drugs (high cross-line cos):")
        print(rel.sort_values("cross_cos").tail(6)[cols].to_string(
            index=False, float_format=lambda x: f"{x:.2f}"))
    print("================================================================")
    print("READ: if a large fraction of reliable drugs sit below the 0.9 gate AND well "
          "below the within-line reliability, cross-line divergence is REAL -> the "
          "'population-in, mean-out' failure should trigger on a K562+A549 mixture. If "
          "cross_cos hugs the reliability ceiling (~lines respond alike), it will NOT -> "
          "escalate to a naturally divergent dataset (Frangieh/Tahoe).")
    print(f"[probe] wrote {out}")


if __name__ == "__main__":
    main()
