#!/usr/bin/env python
"""Construct heterogeneous-source controlled queries with KNOWN subpop labels.

Two orthogonal MOA classes (default HDAC vs JAK) at a fixed dose in one cell
line define two response directions. A heterogeneous TARGET population is built
as an alpha / (1-alpha) mixture of the two classes. Candidate populations are
drawn from HELD-OUT cells (disjoint from the target) so the ground truth is
leakage-free:

    majority-only  = pure class-A (held-out)      -- what mean-matching prefers
    minority-only  = pure class-B (held-out)
    covers-both    = alpha/(1-alpha) mix (held-out) -- the correct answer
    + distractors  = other drugs' treated pops (held-out)

By construction the covers-both candidate is drawn from the SAME mixture
distribution as the target, so it is the ground-truth best match.

Importable (MixtureBuilder) or CLI to dump one query to .npz.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gidflow.data.processed import SciplexDataset  # noqa: E402


class MixtureBuilder:
    def __init__(self, processed_path: str, ann_dir: str = "data/annotation",
                 cell_line: str = "K562", class_a: str = "HDAC", class_b: str = "JAK",
                 label_col: str = "target", dose: float | None = 10000.0,
                 n_total: int = 400, seed: int = 0):
        self.data = SciplexDataset(processed_path, ann_dir)
        self.X = self.data.X.numpy()
        obs = self.data.obs
        self.n_total = n_total
        self.rng = np.random.default_rng(seed)

        lab = obs[label_col].astype(str).str.strip()
        line = obs["cell_line"].astype(str)
        dv = obs["dose_value"].astype(float)
        is_ctrl = obs["is_control"].astype(bool).to_numpy() if "is_control" in obs else \
            np.zeros(len(obs), bool)
        base = (line == cell_line).to_numpy()
        if dose is not None and (dv == dose).any():
            base = base & (dv == dose).to_numpy()

        self.rows_a = np.flatnonzero(base & (lab == class_a).to_numpy() & ~is_ctrl)
        self.rows_b = np.flatnonzero(base & (lab == class_b).to_numpy() & ~is_ctrl)
        if len(self.rows_a) < 40 or len(self.rows_b) < 40:
            raise ValueError(f"too few cells: {class_a}={len(self.rows_a)} "
                             f"{class_b}={len(self.rows_b)} in {cell_line}@{dose}")
        # control-pool pseudo-source mean (real DMSO if present, else grand mean)
        ctrl = self.data.control_rows.get(cell_line, np.array([], int))
        self.pseudo_control = (self.X[ctrl].mean(0) if len(ctrl)
                               else self.X.mean(0)).astype(np.float32)
        self.class_a, self.class_b, self.cell_line = class_a, class_b, cell_line

        # split each class into disjoint halves: build vs candidate (held-out)
        self._a_build, self._a_cand = self._halve(self.rows_a)
        self._b_build, self._b_cand = self._halve(self.rows_b)

        # distractor drugs: other conditions in this cell line at this dose
        self.distractor_rows = self._distractors(base & ~is_ctrl, lab, {class_a, class_b})

    def _halve(self, rows):
        r = self.rng.permutation(rows)
        h = len(r) // 2
        return r[:h], r[h:]

    def _distractors(self, base_mask, lab, exclude):
        obs = self.data.obs
        pert = obs["perturbation"].astype(str).str.strip()
        out = {}
        for name in pert[base_mask].unique():
            if lab[pert == name].iloc[0] in exclude:
                continue
            rows = np.flatnonzero(base_mask & (pert == name).to_numpy())
            if len(rows) >= 20:
                out[name] = rows
        return out

    def _sample(self, rows, n, rng):
        return rng.choice(rows, n, replace=len(rows) < n)

    def build(self, alpha: float, n_distractors: int = 40, seed: int | None = None):
        """Return dict with target, candidates, per-cell subpop labels, ground truth."""
        rng = self.rng if seed is None else np.random.default_rng(seed)
        n_maj = int(round(alpha * self.n_total)); n_min = self.n_total - n_maj

        def mix(a_pool, b_pool, r):
            ra = self._sample(a_pool, n_maj, r); rb = self._sample(b_pool, n_min, r)
            X = np.concatenate([self.X[ra], self.X[rb]], 0)
            lab = np.concatenate([np.zeros(n_maj, int), np.ones(n_min, int)])  # 0=A,1=B
            return X.astype(np.float32), lab

        target, target_lab = mix(self._a_build, self._b_build, rng)
        covers_both, _ = mix(self._a_cand, self._b_cand, rng)
        majority = self.X[self._sample(self._a_cand, self.n_total, rng)].astype(np.float32)
        minority = self.X[self._sample(self._b_cand, self.n_total, rng)].astype(np.float32)

        cands = {"covers-both": covers_both, "majority-only": majority,
                 "minority-only": minority}
        names = list(self.distractor_rows)
        rng.shuffle(names)
        for name in names[:n_distractors]:
            cands[f"distractor:{name}"] = self.X[
                self._sample(self.distractor_rows[name], self.n_total, rng)].astype(np.float32)

        return {"alpha": alpha, "target": target, "target_labels": target_lab,
                "candidates": cands, "ground_truth": "covers-both",
                "pseudo_control": self.pseudo_control,
                "class_a": self.class_a, "class_b": self.class_b,
                "cell_line": self.cell_line}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--processed", default="data/processed/sciplex3_all.pt")
    ap.add_argument("--ann-dir", default="data/annotation")
    ap.add_argument("--cell-line", default="K562")
    ap.add_argument("--alpha", type=float, default=0.7)
    ap.add_argument("--n-total", type=int, default=400)
    ap.add_argument("--out", default="results/subflow/mixture_query.npz")
    args = ap.parse_args()
    mb = MixtureBuilder(args.processed, args.ann_dir, cell_line=args.cell_line,
                        n_total=args.n_total)
    q = mb.build(args.alpha)
    print(f"[mixture] cell_line={q['cell_line']} A={q['class_a']} B={q['class_b']} "
          f"alpha={q['alpha']} target={q['target'].shape} "
          f"candidates={len(q['candidates'])} gt={q['ground_truth']}")
    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    np.savez(out, target=q["target"], target_labels=q["target_labels"],
             pseudo_control=q["pseudo_control"],
             **{f"cand::{k}": v for k, v in q["candidates"].items()})
    print(f"[mixture] wrote {out}")


if __name__ == "__main__":
    main()
