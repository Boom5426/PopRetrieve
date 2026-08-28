#!/usr/bin/env python
"""Consolidate exp08–exp11 baseline results into one master comparison table.

Reads the compact per-experiment summary CSVs and emits
``results/baseline_comparison_master.csv`` with one row per (experiment, method, family) and a
common metric schema (Drug Hit@1/5, MRR, nDCG@10, plus experiment-specific extras carried in a
``notes`` column). This is the single table a reader consults to compare every baseline against
PopRetrieve across the whole Phase-2 comparison; the per-experiment CSVs remain the detailed source.

    python src/experiments/recompute_baselines.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from utils.io import results_path, write_csv
from utils.logging import log, section

# method -> family label (paper's taxonomy)
FAMILY = {
    "mean_cosine": "signature (PopRetrieve special case)",
    "global_energy": "PopRetrieve distributional",
    "coverage_mean": "PopRetrieve divergence-gated",
    "coverage_worst": "PopRetrieve divergence-gated",
    "cmap_cosine": "signature retrieval",
    "cmap_wtcs": "signature retrieval",
    "pca_mean": "latent mean retrieval",
    "pca_dist": "latent distributional",
    "graph_proximity": "direct inverse design (PDGrapher)",
    "target_overlap": "direct inverse design (PDGrapher)",
    "signature_reversal": "signature retrieval",
    "distance_reduction": "PopRetrieve-flavored population signal",
    "field_match": "reference (upper)",
    "random": "reference (lower)",
}


def _safe_read(path: Path) -> pd.DataFrame | None:
    if path.exists():
        return pd.read_csv(path)
    log(f"[recompute] MISSING {path} — skipping")
    return None


def _rows_exp08(root: Path) -> list[dict]:
    df = _safe_read(root / "exp08_signature_baselines" / "summary.csv")
    if df is None:
        return []
    # exp08 summary schema: method + Drug Hit@1/5, MRR, nDCG etc (averaged over tasks/seeds)
    metric = _pick(df, ["hit@1", "hit1", "drug_hit@1"])
    rows = []
    grp = df.groupby("method") if "method" in df.columns else [(m, df[df.iloc[:, 0] == m]) for m in df.iloc[:, 0].unique()]
    agg = df.groupby("method").mean(numeric_only=True).reset_index() if "method" in df.columns else df
    for _, r in agg.iterrows():
        m = r["method"] if "method" in agg.columns else r.iloc[0]
        rows.append({
            "experiment": "exp08_signature_baselines", "method": m,
            "family": FAMILY.get(m, "?"),
            "drug_hit@1": _val(r, ["hit@1", "hit1"]), "drug_hit@5": _val(r, ["hit@5", "hit5"]),
            "mrr": _val(r, ["mrr"]), "ndcg@10": _val(r, ["ndcg@10", "ndcg"]),
            "notes": "real heterogeneous populations (SciPlex3+Frangieh)",
        })
    return rows


def _rows_exp09(root: Path) -> list[dict]:
    df = _safe_read(root / "exp09_predict_then_rank" / "predictor_ranker_matrix.csv")
    if df is None:
        return []
    rows = []
    for _, r in df.iterrows():
        method = f"{r['predictor']}+{r['retrieval']}"
        rows.append({
            "experiment": "exp09_predict_then_rank", "method": method,
            "family": f"predict-then-rank / {r['retrieval']}",
            "drug_hit@1": r.get("hit1"), "drug_hit@5": r.get("hit5"),
            "mrr": r.get("mrr"), "ndcg@10": r.get("ndcg"),
            "notes": "forward predictor x retrieval layer",
        })
    return rows


def _rows_exp10(root: Path) -> list[dict]:
    ddf = _safe_read(root / "exp10_pdgrapher_comparison" / "drug_ranking_summary.csv")
    tdf = _safe_read(root / "exp10_pdgrapher_comparison" / "target_ranking_summary.csv")
    rows = []
    if ddf is not None:
        tmap = {}
        if tdf is not None:
            tmap = {r["signal"]: r for _, r in tdf.iterrows()}
        for _, r in ddf.iterrows():
            sig = r["signal"]
            tr = tmap.get(sig, {})
            rows.append({
                "experiment": "exp10_pdgrapher_comparison", "method": sig,
                "family": FAMILY.get(sig, r.get("family", "?")),
                "drug_hit@1": r.get("hit@1"), "drug_hit@5": r.get("hit@5"),
                "mrr": r.get("mrr"), "ndcg@10": r.get("ndcg@10"),
                "target_ndcg@10": tr.get("target_ndcg@10") if len(tr) else None,
                "target_recall@5": tr.get("target_recall@5") if len(tr) else None,
                "notes": "LINCS/CIGS closed-loop benchmark (precomputed, no training)",
            })
    return rows


def _rows_exp11(root: Path) -> list[dict]:
    df = _safe_read(root / "exp11_synthetic_phase_diagram" / "boundary_contour.csv")
    src = _safe_read(root / "exp11_synthetic_phase_diagram" / "dart_advantage_grid.csv")
    rows = []
    if src is not None:
        # report the max PopRetrieve energy advantage over the whole grid (the phase-diagram summary)
        max_adv = float(src["adv_energy_vs_mean"].max())
        mean_adv = float(src["adv_energy_vs_mean"].mean())
        rows.append({
            "experiment": "exp11_synthetic_phase_diagram",
            "method": "global_energy vs mean_cosine",
            "family": "PopRetrieve distributional vs signature",
            "drug_hit@1": None, "drug_hit@5": None, "mrr": None, "ndcg@10": None,
            "max_energy_advantage": max_adv, "mean_energy_advantage": mean_adv,
            "notes": "divergence-gated boundary; advantage = Hit@1(energy) - Hit@1(mean)",
        })
    if df is not None:
        for _, r in df.iterrows():
            rows.append({
                "experiment": "exp11_synthetic_phase_diagram",
                "method": f"boundary@alpha={r['alpha']}",
                "family": "phase boundary",
                "notes": f"lambda*={r['lambda_star']} (energy advantage first >= "
                         f"{r['advantage_thresh']}), max_advantage={r['max_advantage']:.2f}",
            })
    return rows


def _pick(df, names):
    for n in names:
        if n in df.columns:
            return n
    return None


def _val(row, names):
    for n in names:
        if n in row.index:
            return row[n]
    return None


def run(root=None):
    section("RECOMPUTE — consolidate exp08–exp11 into master comparison table")
    root = Path(root) if root else Path(__file__).resolve().parents[2] / "results"
    rows = []
    rows += _rows_exp08(root)
    rows += _rows_exp09(root)
    rows += _rows_exp10(root)
    rows += _rows_exp11(root)
    master = pd.DataFrame(rows)
    # order columns
    lead = ["experiment", "method", "family", "drug_hit@1", "drug_hit@5", "mrr", "ndcg@10"]
    extra = [c for c in master.columns if c not in lead and c != "notes"]
    cols = [c for c in lead if c in master.columns] + extra + ["notes"]
    master = master[cols]
    out = root / "baseline_comparison_master.csv"
    write_csv(master, out)
    log(f"[recompute] wrote {out} — {len(master)} rows, {master.experiment.nunique()} experiments")
    section("MASTER TABLE")
    log(master.to_string(index=False))
    return master


if __name__ == "__main__":
    run()
