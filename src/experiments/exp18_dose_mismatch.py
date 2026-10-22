#!/usr/bin/env python
"""Dose-mismatch identity retrieval on SciPlex3.

The dose pair, primary contrast and outcome rule were fixed before the analysis (manuscript
Methods). A query is drug d at dose a
(half A of the condition's cells); the library is every eligible drug at dose b (half B); the
correct candidate is drug d at dose b. The question is whether the magnitude-aware mean keeps
its advantage over direction-only mean cosine when a != b.

    python src/experiments/exp18_dose_mismatch.py \
        --data data/processed/sciplex3_all.pt --out results/exp18_dose_mismatch
"""
from __future__ import annotations

import argparse
import json
import sys
from itertools import product
from pathlib import Path

import numpy as np
import pandas as pd
import torch

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))
from retrieval.metrics import energy_distance_u  # noqa: E402

SCORES = ("mean_cosine", "mean_l2", "energy")
MIN_HALF = 20            # cells per half for a condition to be eligible
SPLIT_SEEDS = (0, 1, 2, 3, 4)
PRIMARY_DOSES = (1000.0, 10000.0)   # nM
RESPONSIVE_COS = 0.5
N_BOOT = 10_000


def offdiag_mean_dist(X: torch.Tensor) -> float:
    D = torch.cdist(X, X)
    n = X.shape[0]
    return float((D.sum() - D.diagonal().sum()) / (n * (n - 1)))


def split_halves(idx: np.ndarray, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    perm = rng.permutation(idx)
    h = len(perm) // 2
    return np.sort(perm[:h]), np.sort(perm[h:2 * h])


class Half:
    """Populations of one split half within one cell line."""

    def __init__(self, X: torch.Tensor, cond_idx: dict, ctrl_idx: np.ndarray):
        self.ctrl_mean = X[ctrl_idx].mean(0)
        self.keys = sorted(cond_idx)
        self.cells = {k: X[cond_idx[k]] for k in self.keys}
        self.mean = {k: v.mean(0) for k, v in self.cells.items()}
        self.resp = {k: self.mean[k] - self.ctrl_mean for k in self.keys}
        self.within = {k: offdiag_mean_dist(v) for k, v in self.cells.items()}
        # Library view over all conditions, built once so each query needs one distance pass.
        self.index = {k: i for i, k in enumerate(self.keys)}
        self.cat = torch.cat([self.cells[k] for k in self.keys])
        self.sizes = [self.cells[k].shape[0] for k in self.keys]
        self.resp_mat = torch.stack([self.resp[k] for k in self.keys])
        self.within_vec = torch.tensor([self.within[k] for k in self.keys])


def score_all(q: Half, qkey, lib: Half) -> dict[str, np.ndarray]:
    """Scores of query ``qkey`` against every condition of ``lib``, in ``lib.keys`` order."""
    qc, qr = q.cells[qkey], q.resp[qkey]
    cos = torch.nn.functional.cosine_similarity(lib.resp_mat, qr[None, :], dim=1)
    l2 = -torch.linalg.norm(lib.resp_mat - qr[None, :], dim=1)
    cross = torch.cdist(qc, lib.cat).mean(0)
    cross_means = torch.stack([s.mean() for s in torch.split(cross, lib.sizes)])
    energy = -(2 * cross_means - q.within[qkey] - lib.within_vec)
    return {"mean_cosine": cos.numpy(), "mean_l2": l2.numpy(), "energy": energy.numpy()}


def rank_of(scores: np.ndarray, pos: int) -> int:
    return 1 + int((scores > scores[pos]).sum())


def cluster_boot(df: pd.DataFrame, col: str, rng: np.random.Generator) -> tuple[float, float]:
    drugs = df["drug"].values
    vals = df[col].values
    ud = np.unique(drugs)
    sums = pd.Series(vals).groupby(drugs).sum().reindex(ud).values
    counts = pd.Series(vals).groupby(drugs).size().reindex(ud).values
    draws = rng.integers(0, len(ud), size=(N_BOOT, len(ud)))
    boot = sums[draws].sum(1) / counts[draws].sum(1)
    return float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=str(REPO / "data/processed/sciplex3_all.pt"))
    ap.add_argument("--out", default=str(REPO / "results/exp18_dose_mismatch"))
    ap.add_argument("--threads", type=int, default=16)
    args = ap.parse_args()
    torch.set_num_threads(args.threads)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    blob = torch.load(args.data, map_location="cpu", weights_only=False)
    X = torch.as_tensor(np.asarray(blob["X"], dtype=np.float32))
    obs = blob["obs"].reset_index(drop=True)
    obs["perturbation"] = obs["perturbation"].astype(str).str.strip()
    doses = sorted(float(d) for d in blob["doses"])
    lines = sorted(blob["cell_lines"])

    # The batched energy above must equal the repository's U-statistic estimator.
    a_idx = np.where(~obs.is_control.values)[0][:50]
    b_idx = np.where(~obs.is_control.values)[0][50:90]
    ref = float(energy_distance_u(X[a_idx], X[b_idx]))
    cross = float(torch.cdist(X[a_idx], X[b_idx]).mean())
    mine = 2 * cross - offdiag_mean_dist(X[a_idx]) - offdiag_mean_dist(X[b_idx])
    assert abs(ref - mine) < 1e-4 * max(1.0, abs(ref)), (ref, mine)

    rows, rows_all = [], []
    responsive = {}
    for seed, line in product(SPLIT_SEEDS, lines):
        rng = np.random.default_rng([seed, lines.index(line)])
        in_line = obs.cell_line.values == line
        ctrl = np.where(in_line & obs.is_control.values)[0]
        cA, cB = split_halves(ctrl, rng)
        treated = obs[in_line & ~obs.is_control.values]
        condA, condB = {}, {}
        for (drug, dose), grp in treated.groupby(["perturbation", "dose_value"], sort=True):
            hA, hB = split_halves(grp.index.values, rng)
            if len(hA) >= MIN_HALF:
                condA[(drug, float(dose))] = hA
                condB[(drug, float(dose))] = hB
        A, B = Half(X, condA, cA), Half(X, condB, cB)

        if seed == 0:
            for k in A.keys:
                responsive[(line,) + k] = float(torch.nn.functional.cosine_similarity(
                    A.resp[k], B.resp[k], dim=0))

        dose_idx = {db: np.array([B.index[k] for k in B.keys if k[1] == db]) for db in doses}
        for qi, qkey in enumerate(A.keys):
            sc_all = score_all(A, qkey, B)
            drug, da = qkey
            # Primary: library = every eligible drug at dose db; correct = (drug, db).
            for db in doses:
                if (drug, db) not in B.index:
                    continue
                sub = dose_idx[db]
                pos = int(np.where(sub == B.index[(drug, db)])[0][0])
                row = {"seed": seed, "cell_line": line, "drug": drug, "dose_query": da,
                       "dose_library": db, "n_library": len(sub),
                       "n_query_cells": A.cells[qkey].shape[0],
                       "n_correct_cells": B.cells[(drug, db)].shape[0]}
                for s in SCORES:
                    r = rank_of(sc_all[s][sub], pos)
                    row[f"rank_{s}"] = r
                    row[f"rr_{s}"] = 1.0 / r
                rows.append(row)
            # Secondary 2: all-dose library, query's own (drug, dose) removed.
            keep = np.array([i for i, k in enumerate(B.keys) if k != qkey])
            same = [j for j, i in enumerate(keep) if B.keys[i][0] == drug]
            if same:
                row = {"seed": seed, "cell_line": line, "drug": drug, "dose_query": da,
                       "n_library": len(keep), "n_same_drug": len(same)}
                for s in SCORES:
                    r = min(rank_of(sc_all[s][keep], j) for j in same)
                    row[f"rank_{s}"] = r
                    row[f"rr_{s}"] = 1.0 / r
                rows_all.append(row)
            if qi % 100 == 0:
                print(f"[dose] seed={seed} line={line} query {qi}/{len(A.keys)}", flush=True)
        print(f"[dose] seed={seed} line={line} conditions A={len(A.keys)} rows={len(rows)}",
              flush=True)

    per = pd.DataFrame(rows)
    per_all = pd.DataFrame(rows_all)
    resp = pd.Series(responsive, name="split_half_cos")
    resp.index.names = ["cell_line", "drug", "dose"]
    resp.reset_index().to_csv(out / "split_half_response_cosine.csv", index=False)

    def is_resp(r) -> bool:
        a = responsive.get((r.cell_line, r.drug, r.dose_query), np.nan)
        b = responsive.get((r.cell_line, r.drug, r.dose_library), np.nan)
        return bool(a >= RESPONSIVE_COS and b >= RESPONSIVE_COS)

    per["responsive_both"] = per.apply(is_resp, axis=1)
    per["matched"] = per.dose_query == per.dose_library
    per.to_csv(out / "per_query.csv.gz", index=False)
    per_all.to_csv(out / "per_query_all_dose_library.csv.gz", index=False)

    boot_rng = np.random.default_rng(0)
    summ = []
    for (dq, dl), g in per.groupby(["dose_query", "dose_library"]):
        for subset, gg in (("all", g), ("responsive", g[g.responsive_both])):
            if len(gg) == 0:
                continue
            rec = {"dose_query": dq, "dose_library": dl, "subset": subset,
                   "n_queries": len(gg), "n_drugs": gg.drug.nunique()}
            for s in SCORES:
                rec[f"MRR_{s}"] = gg[f"rr_{s}"].mean()
                rec[f"Hit1_{s}"] = (gg[f"rank_{s}"] == 1).mean()
            summ.append(rec)
    pd.DataFrame(summ).to_csv(out / "summary_by_dose_pair.csv", index=False)

    # Primary contrasts on the 1 uM / 10 uM block.
    prim = per[per.dose_query.isin(PRIMARY_DOSES) & per.dose_library.isin(PRIMARY_DOSES)].copy()
    prim["d_mag"] = prim.rr_mean_l2 - prim.rr_mean_cosine
    prim["d_struct"] = prim.rr_energy - prim.rr_mean_l2
    prim["d_energy_cos"] = prim.rr_energy - prim.rr_mean_cosine
    contrasts = []
    for subset, sub in (("all", prim), ("responsive", prim[prim.responsive_both])):
        for col in ("d_mag", "d_struct", "d_energy_cos"):
            for cond, g in (("matched", sub[sub.matched]), ("mismatched", sub[~sub.matched])):
                lo, hi = cluster_boot(g, col, boot_rng)
                contrasts.append({"subset": subset, "contrast": col, "condition": cond,
                                  "n_queries": len(g), "n_drugs": g.drug.nunique(),
                                  "mean": g[col].mean(), "ci_lo": lo, "ci_hi": hi})
            # Interaction: mismatched minus matched, resampling drugs jointly.
            drugs = np.unique(sub.drug)
            gm = sub[sub.matched].groupby("drug")[col].agg(["sum", "size"]).reindex(drugs).fillna(0)
            gx = sub[~sub.matched].groupby("drug")[col].agg(["sum", "size"]).reindex(drugs).fillna(0)
            draws = boot_rng.integers(0, len(drugs), size=(N_BOOT, len(drugs)))
            bm = gm["sum"].values[draws].sum(1) / gm["size"].values[draws].sum(1)
            bx = gx["sum"].values[draws].sum(1) / gx["size"].values[draws].sum(1)
            point = sub[~sub.matched][col].mean() - sub[sub.matched][col].mean()
            contrasts.append({"subset": subset, "contrast": col,
                              "condition": "mismatched_minus_matched", "n_queries": len(sub),
                              "n_drugs": len(drugs), "mean": point,
                              "ci_lo": float(np.percentile(bx - bm, 2.5)),
                              "ci_hi": float(np.percentile(bx - bm, 97.5))})
    pd.DataFrame(contrasts).to_csv(out / "primary_contrasts.csv", index=False)

    alls = []
    for dq, g in per_all.groupby("dose_query"):
        rec = {"dose_query": dq, "n_queries": len(g), "n_drugs": g.drug.nunique()}
        for s in SCORES:
            rec[f"MRR_{s}"] = g[f"rr_{s}"].mean()
            rec[f"Hit1_{s}"] = (g[f"rank_{s}"] == 1).mean()
        alls.append(rec)
    pd.DataFrame(alls).to_csv(out / "summary_all_dose_library.csv", index=False)

    prov = {"data": str(args.data), "n_cells": int(X.shape[0]), "n_genes": int(X.shape[1]),
            "doses_nM": doses, "lines": lines, "split_seeds": list(SPLIT_SEEDS),
            "min_cells_per_half": MIN_HALF, "responsive_cos": RESPONSIVE_COS,
            "n_boot": N_BOOT, "bootstrap_seed": 0, "energy_check": [ref, mine],
            "torch": torch.__version__, "numpy": np.__version__, "pandas": pd.__version__,
            "analysis_plan": "manuscript Methods, dose-mismatch re-identification"}
    (out / "provenance.json").write_text(json.dumps(prov, indent=2))
    print(pd.DataFrame(contrasts).to_string(index=False))


if __name__ == "__main__":
    main()
