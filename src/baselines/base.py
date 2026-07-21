"""Unified baseline interfaces (Phase-2 external-baselines comparison).

The original package rankers consume two different query-dict shapes (``score_controlled``
takes ``q["target"]/q["target_labels"]/q["pseudo_control"]/q["candidates"]``; ``score_labeled``
takes ``q["target"]/q["tlab"]/q["ctrl_T"]/q["cands"]``).  To let every external baseline
run on *both* task styles without special-casing, we normalize either dict into a single
``NormalizedQuery`` view, then define two thin protocols:

    Ranker     — score candidate populations directly:      score(nq) -> {name: float}
    Predictor  — predict a drug's response, THEN rank:       predict(context) -> signature/pop

Both return **higher = better** score vectors over the query's candidate list, matching the
package-wide convention in ``retrieval.metrics`` (similarity as-is, distance negated).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Optional, Protocol, runtime_checkable

import numpy as np


# ---------------------------------------------------------------------------
# Normalized query view (bridges controlled + labeled task dicts)
# ---------------------------------------------------------------------------


@dataclass
class Candidate:
    """One candidate response population and its (optional) matched control / labels."""
    name: str
    X: np.ndarray                          # cells × genes
    control: Optional[np.ndarray] = None   # matched control MEAN vector (genes,) or None
    labels: Optional[np.ndarray] = None    # per-cell subpopulation labels or None

    @property
    def mean(self) -> np.ndarray:
        return np.asarray(self.X, dtype=np.float64).mean(0)

    @property
    def delta(self) -> np.ndarray:
        """Mean response signature (mean - matched control), or mean if no control."""
        m = self.mean
        return m - np.asarray(self.control, dtype=np.float64) if self.control is not None else m


@dataclass
class NormalizedQuery:
    """A retrieval query flattened to one uniform shape for every baseline."""
    query_id: str
    Q: np.ndarray                          # target/query cells × genes
    control_Q: Optional[np.ndarray]        # matched control MEAN vector (genes,) or None
    labels_Q: Optional[np.ndarray]         # per-cell subpop labels of the query or None
    candidates: list[Candidate] = field(default_factory=list)
    ground_truth: str = "covers-both"
    divergence: Optional[float] = None     # subpop-response cosine (lower => more divergent)
    metadata: dict = field(default_factory=dict)

    @property
    def names(self) -> list[str]:
        return [c.name for c in self.candidates]

    @property
    def gt_index(self) -> Optional[int]:
        n = self.names
        return n.index(self.ground_truth) if self.ground_truth in n else None

    @property
    def query_delta(self) -> np.ndarray:
        m = np.asarray(self.Q, dtype=np.float64).mean(0)
        return m - np.asarray(self.control_Q, dtype=np.float64) if self.control_Q is not None else m


def normalize_query(q: dict, query_id: str = "", ground_truth: str = "covers-both",
                    divergence: Optional[float] = None) -> NormalizedQuery:
    """Flatten a controlled- or labeled-style task dict into a ``NormalizedQuery``.

    controlled: candidates = {name: X}, shared pseudo-control, query labels in
                ``target_labels``.
    labeled:    candidates = {name: (X, plab, control_mean)}, per-candidate control,
                query labels in ``tlab``, query control in ``ctrl_T``.
    """
    if "candidates" in q and "pseudo_control" in q:                 # controlled style
        pc = np.asarray(q["pseudo_control"], dtype=np.float64)
        labels_Q = np.asarray(q["target_labels"]) if "target_labels" in q else None
        cands = [Candidate(name=n, X=np.asarray(P, dtype=np.float32), control=pc)
                 for n, P in q["candidates"].items()]
        return NormalizedQuery(query_id=query_id, Q=np.asarray(q["target"], dtype=np.float32),
                               control_Q=pc, labels_Q=labels_Q, candidates=cands,
                               ground_truth=ground_truth, divergence=divergence)
    if "cands" in q:                                                # labeled style
        cT = np.asarray(q["ctrl_T"], dtype=np.float64) if q.get("ctrl_T") is not None else None
        labels_Q = np.asarray(q["tlab"]) if q.get("tlab") is not None else None
        cands = []
        for n, tup in q["cands"].items():
            P, plab, cP = tup
            cands.append(Candidate(name=n, X=np.asarray(P, dtype=np.float32),
                                   control=np.asarray(cP, dtype=np.float64) if cP is not None else None,
                                   labels=np.asarray(plab) if plab is not None else None))
        return NormalizedQuery(query_id=query_id, Q=np.asarray(q["target"], dtype=np.float32),
                               control_Q=cT, labels_Q=labels_Q, candidates=cands,
                               ground_truth=ground_truth, divergence=divergence)
    raise ValueError("unrecognized query dict; expected controlled ('candidates'+'pseudo_control') "
                     "or labeled ('cands') style")


# ---------------------------------------------------------------------------
# Protocols
# ---------------------------------------------------------------------------


@runtime_checkable
class Ranker(Protocol):
    """Score candidate populations against the query directly (retrieval baselines)."""
    name: str

    def score(self, nq: NormalizedQuery, **kwargs) -> dict[str, float]:
        """Return {candidate_name: score} with higher = better match."""
        ...


@runtime_checkable
class Predictor(Protocol):
    """Predict a drug's response in a query context (predict-then-rank baselines)."""
    name: str

    def predict(self, drug: str, context: Any, **kwargs) -> np.ndarray:
        """Return a predicted response signature (genes,) or population (cells×genes)."""
        ...


def scores_to_vector(nq: NormalizedQuery, score_map: dict[str, float]) -> np.ndarray:
    """Order a {name: score} map into a vector aligned with ``nq.names``."""
    return np.array([score_map[n] for n in nq.names], dtype=float)


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    a = np.asarray(a, dtype=np.float64); b = np.asarray(b, dtype=np.float64)
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return 0.0 if na < 1e-12 or nb < 1e-12 else float(a @ b / (na * nb))
