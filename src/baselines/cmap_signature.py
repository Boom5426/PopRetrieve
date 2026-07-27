"""CMap / LINCS-style mean-signature connectivity retrieval (baseline).

The incumbent retrieval paradigm: reduce every population to a single *mean differential
expression signature* and rank candidates by how well their signature connects to the
query's.  We expose two connectivity kernels over the mean-delta signatures (candidate
mean - matched control, query mean - matched control):

    scoring='cosine'   — weighted cosine of the full mean-delta vectors (a smooth,
                         full-transcriptome connectivity).
    scoring='wtcs'     — a Connectivity-Map WTCS-lite: build the query's up / down gene
                         SETS (top / bottom ``n_genes`` of the query signature), then score
                         each candidate by a signed, normalized rank-enrichment of those
                         sets in the candidate's signature (the sign-aware GSEA-style score
                         CMap/L1000 uses, reduced to the two-tag mean form).

Both collapse the query population to its MEAN, so — by construction — they are blind to
query subpopulation structure. That is exactly the degenerate zero-spread limit EvalShift is
designed to beat; this baseline makes the comparison explicit.
"""
from __future__ import annotations

import numpy as np

from .base import Candidate, NormalizedQuery, cosine


def _signed_rank_enrichment(signature: np.ndarray, up_idx: np.ndarray,
                            dn_idx: np.ndarray) -> float:
    """WTCS-lite: normalized mean signed rank of the up/down query tags in a candidate.

    Rank the candidate signature (ascending); genes the query marks UP should sit at high
    ranks, genes it marks DOWN at low ranks. Return (mean_up_rank - mean_dn_rank) scaled to
    roughly [-1, 1]. This is the two-tag, rank-based reduction of the Connectivity-Map
    weighted connectivity score (KS-enrichment in the full L1000; here the balanced mean
    form, which is monotone in the same quantity and needs no per-gene weights).
    """
    n = len(signature)
    order = np.argsort(signature, kind="stable")          # ascending
    rank = np.empty(n, dtype=float)
    rank[order] = np.arange(1, n + 1)                      # 1..n, high = strongly up
    rank = (rank - 1) / (n - 1) if n > 1 else rank * 0.0   # -> [0,1]
    up = rank[up_idx].mean() if len(up_idx) else 0.5
    dn = rank[dn_idx].mean() if len(dn_idx) else 0.5
    return float(up - dn)                                  # in [-1, 1]


class CMapSignatureRetrieval:
    """Rank candidates by connectivity of their mean-delta signature to the query's."""

    def __init__(self, scoring: str = "cosine", n_genes: int = 50):
        if scoring not in ("cosine", "wtcs"):
            raise ValueError("scoring must be 'cosine' or 'wtcs'")
        self.scoring = scoring
        self.n_genes = n_genes
        self.name = f"cmap_{scoring}"

    # -- query tag sets (top/bottom of the query mean-delta) --
    def _query_tags(self, q_sig: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        k = min(self.n_genes, max(1, len(q_sig) // 2))
        order = np.argsort(q_sig, kind="stable")
        dn_idx = order[:k]
        up_idx = order[-k:]
        return up_idx, dn_idx

    def score(self, nq: NormalizedQuery, **_) -> dict[str, float]:
        q_sig = nq.query_delta
        if self.scoring == "cosine":
            return {c.name: cosine(q_sig, c.delta) for c in nq.candidates}
        up_idx, dn_idx = self._query_tags(q_sig)
        return {c.name: _signed_rank_enrichment(c.delta, up_idx, dn_idx)
                for c in nq.candidates}


def cmap_scores(nq: NormalizedQuery, scoring: str = "cosine",
                n_genes: int = 50) -> dict[str, float]:
    """Functional entry point mirroring the package's ``score_*`` helpers."""
    return CMapSignatureRetrieval(scoring=scoring, n_genes=n_genes).score(nq)
