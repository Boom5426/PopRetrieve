"""Preference-conflict scores for HIR-Bench.

Quantify how much subpopulations disagree on the drug ranking — the structural
cause of mean-vs-distributional retrieval divergence.
"""
from __future__ import annotations

import numpy as np
from scipy.stats import kendalltau

from .heterogeneous_retrieval_benchmark import HIRCell


def topk_disagreement(cell: HIRCell, k: int | None = None) -> float:
    """Primary conflict score: 1 - |TopK_1 ∩ TopK_2| / K.

    For K > 2 subpops, average over all pairs.
    """
    U = cell.utility_matrix  # (n_drugs, n_subpops)
    n_drugs, n_subpops = U.shape
    if k is None:
        k = min(10, max(1, n_drugs // 5))

    # TopK per subpop (indices of top-k drugs)
    topk_sets = []
    for s in range(n_subpops):
        order = np.argsort(-U[:, s])[:k]
        topk_sets.append(set(order.tolist()))

    # Average pairwise disagreement
    pairs = 0
    total = 0.0
    for i in range(n_subpops):
        for j in range(i + 1, n_subpops):
            overlap = len(topk_sets[i] & topk_sets[j])
            total += 1.0 - overlap / k
            pairs += 1
    return float(total / pairs) if pairs > 0 else 0.0


def standard_kendall_conflict(cell: HIRCell) -> float:
    """Average pairwise Kendall tau distance (1 - tau) / 2, in [0, 1]."""
    U = cell.utility_matrix
    n_subpops = U.shape[1]
    vals = []
    for i in range(n_subpops):
        for j in range(i + 1, n_subpops):
            tau, _ = kendalltau(U[:, i], U[:, j])
            if not np.isfinite(tau):
                # constant utility column for a subpop -> no ranking to conflict with
                vals.append(0.0)
            else:
                vals.append((1 - tau) / 2)  # convert correlation to distance
    return float(np.mean(vals)) if vals else 0.0


def weighted_kendall_conflict(cell: HIRCell, top_weight: float = 3.0) -> float:
    """Kendall-like conflict that weights top-ranked discordant pairs more heavily.

    Pairs involving a drug in the top-20% of either ranking get ``top_weight`` extra weight.
    """
    U = cell.utility_matrix
    n_drugs, n_subpops = U.shape
    top_n = max(1, n_drugs // 5)
    vals = []
    for i in range(n_subpops):
        for j in range(i + 1, n_subpops):
            order_i = np.argsort(-U[:, i])
            order_j = np.argsort(-U[:, j])
            rank_i = np.empty(n_drugs, dtype=int)
            rank_j = np.empty(n_drugs, dtype=int)
            rank_i[order_i] = np.arange(n_drugs)
            rank_j[order_j] = np.arange(n_drugs)
            top_set = set(order_i[:top_n].tolist()) | set(order_j[:top_n].tolist())
            concordant = 0.0
            discordant = 0.0
            for a in range(n_drugs):
                for b in range(a + 1, n_drugs):
                    w = top_weight if (a in top_set or b in top_set) else 1.0
                    if (rank_i[a] - rank_i[b]) * (rank_j[a] - rank_j[b]) > 0:
                        concordant += w
                    else:
                        discordant += w
            total = concordant + discordant
            vals.append(discordant / total if total > 0 else 0.0)
    return float(np.mean(vals)) if vals else 0.0


def response_cosine(cell: HIRCell) -> float:
    """Average pairwise cosine similarity between subpop utility vectors.

    Low cosine = high conflict.  Returns the average, not 1-cosine.
    """
    U = cell.utility_matrix  # (n_drugs, n_subpops)
    n_subpops = U.shape[1]
    vals = []
    for i in range(n_subpops):
        for j in range(i + 1, n_subpops):
            vi, vj = U[:, i], U[:, j]
            d = np.linalg.norm(vi) * np.linalg.norm(vj)
            if d < 1e-12:
                vals.append(1.0)
            else:
                vals.append(float(np.dot(vi, vj) / d))
    return float(np.mean(vals)) if vals else 1.0
