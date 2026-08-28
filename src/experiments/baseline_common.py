"""Shared harness for the Phase-2 external-baseline experiments (exp08–exp11).

Provides one place for:
  * ``query_divergence`` — per-query subpopulation response cosine (lower = more divergent),
    computed from the query's own subpop labels, so every task style yields a comparable
    divergence axis for stratification.
  * ``dart_scores`` — the package's four distributional scorers via ``score_controlled`` /
    ``score_labeled`` (mean_cosine / global_energy / coverage_mean / coverage_worst).
  * ``signature_scores`` — the CMap / PCA retrieval baselines over a NormalizedQuery.
  * ``per_query_metrics`` — Hit@k / MRR / nDCG@10 / median-rank for one score vector, plus
    ranking-flip vs a reference ranker (top-1 flip, top-k overlap, delta-rank).
  * ``aggregate`` / ``stratify`` — mean over queries and divergence-stratified means.

Runtime is captured per method with ``Timer``. Everything writes through the package's
``results_path`` / ``write_csv``.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))    # src on path

from typing import Callable, Optional, Sequence

import numpy as np
import pandas as pd

from baselines.base import NormalizedQuery, cosine, normalize_query, scores_to_vector
from baselines.cmap_signature import CMapSignatureRetrieval
from baselines.pca_latent_retrieval import PCALatentRetrieval
from retrieval.evaluation import (
    delta_rank, rank_of, ranks_of_true, retrieval_metrics, top1_flip, top1_index,
    topk_overlap,
)
from retrieval.rankers import score_controlled, score_labeled, SCORERS as DART_SCORERS
from retrieval.target_metrics import Timer, divergence_bucket, stratify_by_divergence


# ---------------------------------------------------------------------------
# Per-query divergence (subpopulation response cosine)
# ---------------------------------------------------------------------------


def query_divergence(nq: NormalizedQuery) -> float:
    """Cosine between the query's two subpopulation mean-delta signatures.

    Uses the query's own per-cell subpop labels (``labels_Q``). If unavailable or only one
    subpop present, returns NaN (query treated as 'unknown' divergence). Low cosine =>
    the subpopulations respond in near-orthogonal directions => a divergent query where
    the mean signature is unrepresentative (PopRetrieve's regime).
    """
    if nq.labels_Q is None:
        return float("nan")
    lab = np.asarray(nq.labels_Q)
    uniq = np.unique(lab)
    if len(uniq) < 2:
        return float("nan")
    Q = np.asarray(nq.Q, dtype=np.float64)
    ctrl = np.asarray(nq.control_Q, dtype=np.float64) if nq.control_Q is not None else 0.0
    a = Q[lab == uniq[0]].mean(0) - ctrl
    b = Q[lab == uniq[1]].mean(0) - ctrl
    return cosine(a, b)


# ---------------------------------------------------------------------------
# Method score producers
# ---------------------------------------------------------------------------


def dart_scores(q: dict, style: str, max_cells: Optional[int] = None,
                seed: int = 0) -> dict[str, dict[str, float]]:
    """The four PopRetrieve scorers for a raw task dict (controlled or labeled style)."""
    if style == "controlled":
        return score_controlled(q, max_cells=max_cells, seed=seed)
    if style == "labeled":
        return score_labeled(q, max_cells=max_cells, seed=seed)
    raise ValueError(f"unknown style {style!r}")


def signature_scores(nq: NormalizedQuery,
                     rankers: Optional[Sequence] = None) -> dict[str, dict[str, float]]:
    """CMap + PCA retrieval baselines over a NormalizedQuery -> {method: {name: score}}."""
    if rankers is None:
        rankers = [CMapSignatureRetrieval("cosine"), CMapSignatureRetrieval("wtcs"),
                   PCALatentRetrieval(mode="mean"), PCALatentRetrieval(mode="dist")]
    return {r.name: r.score(nq) for r in rankers}


# ---------------------------------------------------------------------------
# Per-query metric computation
# ---------------------------------------------------------------------------


def per_query_metrics(vals: np.ndarray, gt_index: int,
                      ref_vals: Optional[np.ndarray] = None,
                      ks: Sequence[int] = (1, 5), topk: int = 5) -> dict:
    """Retrieval metrics for one candidate score vector, + optional flip vs a reference.

    ``vals``     : per-candidate scores of the method under test (higher = better).
    ``gt_index`` : index of the ground-truth candidate.
    ``ref_vals`` : score vector of the reference ranker (PopRetrieve) for flip / overlap / Δrank.
    """
    vals = np.asarray(vals, dtype=float)
    r = int((vals > vals[gt_index]).sum()) + 1
    out = {f"hit@{k}": float(r <= k) for k in ks}
    out["mrr"] = 1.0 / r
    out["ndcg@10"] = float(1.0 / np.log2(r + 1)) if r <= 10 else 0.0
    out["rank"] = r
    if ref_vals is not None:
        ref_vals = np.asarray(ref_vals, dtype=float)
        out["top1_flip_vs_ref"] = int(top1_flip(vals, ref_vals))
        out["topk_overlap_vs_ref"] = topk_overlap(vals, ref_vals, topk, "jaccard")
        # delta_rank(a=ref, b=method): + => method ranks GT higher (better) than reference
        out["delta_rank_vs_ref"] = delta_rank(ref_vals, vals, gt_index)
    return out


def summarize(per_query: pd.DataFrame, group_cols: Sequence[str],
              metric_cols: Sequence[str]) -> pd.DataFrame:
    """Mean each metric over queries within the given grouping."""
    agg = {m: (m, "mean") for m in metric_cols}
    agg["n_queries"] = (metric_cols[0], "size")
    return per_query.groupby(list(group_cols), sort=False).agg(**agg).reset_index()
