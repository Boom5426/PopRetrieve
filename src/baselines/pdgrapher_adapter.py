"""PDGrapher adapter — bridge inverse-design target ranking <-> EvalShift drug ranking.

PDGrapher (Gonzalez et al.) is a *direct inverse-design* method: given a diseased cell state
it ranks candidate intervention **targets** (genes/nodes) by how well perturbing them steers
the state toward a desired one, using network/graph proximity. EvalShift instead ranks candidate
**drugs** by population-to-population retrieval. To compare them head-to-head we need a common
currency, in BOTH directions:

  target ranking  --(drug->target annotations)-->  drug ranking
  drug ranking    --(drug->target annotations)-->  target ranking

This module provides that conversion, and a thin loader over the repository's precomputed
closed-loop benchmark so exp10 does not have to *train* PDGrapher (its ranked outputs for the
LINCS/CIGS closed-loop task are already materialized in
``data/benchmarks/pdgrapher_closed_loop_benchmark.parquet``: 6 queries x 1369 candidate drugs
x 5 baseline rankers, with a ``field_match`` relevance column and a ``graph_proximity`` /
``signature_reversal`` / ``target_overlap`` score per candidate — the PDGrapher-family signals).

Design notes
------------
* ``field_match`` in the benchmark is the per-candidate relevance to the query's observed
  target field; ``field_match >= FIELD_GT_THRESH`` (default 1.0) marks the target-relevant
  drugs = drug-level ground truth for Hit@K/MRR/nDCG.
* Drug->target annotations come from ``drugcentral_target_annotations.parquet``
  (drug_name -> target_gene, with an ``is_moa`` flag) or ``drug_target_prior.parquet``.
* target ranking -> drug ranking: a drug's score is the max (or mean) score over its annotated
  targets. drug ranking -> target ranking: a target's score is the max (or mean) score over
  the drugs that hit it. Both are deliberately simple, order-preserving aggregations so the
  comparison reflects the ranking signal, not a tuned mapping.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

FIELD_GT_THRESH = 1.0
PDGRAPHER_SCORE_COLS = ("graph_proximity", "signature_reversal", "target_overlap",
                        "final_score", "rescue_score")


# ---------------------------------------------------------------------------
# Benchmark loader
# ---------------------------------------------------------------------------


def load_closed_loop_benchmark(path: Optional[str] = None) -> pd.DataFrame:
    """Load the precomputed PDGrapher-family closed-loop benchmark parquet."""
    if path is None:
        # resolve relative to repo: src/baselines/ -> repo/data/benchmarks/...
        here = Path(__file__).resolve()
        path = here.parents[2] / "data" / "benchmarks" / "pdgrapher_closed_loop_benchmark.parquet"
    df = pd.read_parquet(path)
    return df


def benchmark_queries(df: pd.DataFrame) -> list[str]:
    return sorted(df["query_id"].unique())


def ground_truth_drugs(df: pd.DataFrame, query_id: str,
                       thresh: float = FIELD_GT_THRESH) -> list[str]:
    """Drugs whose field_match >= thresh for this query = target-relevant ground truth."""
    sub = df[(df.query_id == query_id) & (df.field_match >= thresh)]
    return sorted(sub.drug_name.unique())


def ranking_for(df: pd.DataFrame, query_id: str, baseline_name: str,
                score_col: str = "final_score") -> pd.DataFrame:
    """Per-candidate scores for one (query, baseline) as a drug->score frame (desc)."""
    sub = df[(df.query_id == query_id) & (df.baseline_name == baseline_name)].copy()
    col = score_col if score_col in sub.columns else "final_score"
    out = sub.groupby("drug_name")[col].max().reset_index().rename(columns={col: "score"})
    return out.sort_values("score", ascending=False).reset_index(drop=True)


# ---------------------------------------------------------------------------
# Drug <-> target annotation table
# ---------------------------------------------------------------------------


class DrugTargetMap:
    """Bidirectional drug<->target map from DrugCentral / drug_target_prior annotations."""

    def __init__(self, drug2targets: dict[str, list[str]], weights: Optional[dict] = None):
        self.drug2targets = {d: list(t) for d, t in drug2targets.items()}
        self.target2drugs: dict[str, list[str]] = {}
        for d, ts in self.drug2targets.items():
            for t in ts:
                self.target2drugs.setdefault(t, []).append(d)
        self.weights = weights or {}

    @classmethod
    def from_drug_target_prior(cls, path: Optional[str] = None,
                               key: str = "drug_name") -> "DrugTargetMap":
        """Build from ``drug_target_prior.parquet`` — the CIGS graph's own drug->target table.

        This is the correct source for the closed-loop benchmark: it matches the benchmark on
        both ``drug_name`` (exact) and ``candidate_id`` (SMILES) with full coverage, and carries
        a ``target_weight`` per (drug, target). ``key`` selects which column keys the map so it
        joins to the benchmark's chosen identifier.
        """
        if path is None:
            here = Path(__file__).resolve()
            path = here.parents[2] / "data" / "annotation" / "drug_target_prior.parquet"
        df = pd.read_parquet(path)
        d2t: dict[str, list[str]] = {}
        w: dict = {}
        for _, row in df.iterrows():
            d = str(row[key])
            g = str(row["target_gene"]).strip()
            if not g or g == "nan":
                continue
            d2t.setdefault(d, [])
            if g not in d2t[d]:
                d2t[d].append(g)
            w[(d, g)] = float(row.get("target_weight", 1.0) or 1.0)
        return cls(d2t, weights=w)

    @classmethod
    def from_drugcentral(cls, path: Optional[str] = None, moa_only: bool = False,
                         casefold: bool = True) -> "DrugTargetMap":
        """Fallback map from DrugCentral (case-insensitive join; ~842/1369 benchmark coverage)."""
        if path is None:
            here = Path(__file__).resolve()
            path = here.parents[2] / "data" / "annotation" / "drugcentral_target_annotations.parquet"
        df = pd.read_parquet(path)
        if moa_only and "is_moa" in df.columns:
            df = df[df.is_moa]
        d2t: dict[str, list[str]] = {}
        w: dict = {}
        for _, row in df.iterrows():
            d = str(row["drug_name"])
            if casefold:
                d = d.lower()
            # target_gene may be 'GENEA|GENEB'
            genes = str(row["target_gene"]).split("|")
            for g in genes:
                g = g.strip()
                if not g or g == "nan":
                    continue
                d2t.setdefault(d, [])
                if g not in d2t[d]:
                    d2t[d].append(g)
                w[(d, g)] = float(row.get("evidence_score", 1.0) or 1.0)
        return cls(d2t, weights=w)

    def targets_of(self, drug: str) -> list[str]:
        return self.drug2targets.get(drug, [])

    def drugs_of(self, target: str) -> list[str]:
        return self.target2drugs.get(target, [])


# ---------------------------------------------------------------------------
# Conversions
# ---------------------------------------------------------------------------


def target_ranking_to_drug_ranking(target_scores: dict[str, float], dt_map: DrugTargetMap,
                                   drugs: Optional[list[str]] = None,
                                   agg: str = "max") -> dict[str, float]:
    """Score each drug by aggregating the scores of the targets it hits.

    ``target_scores`` : gene -> score (higher = better intervention target, PDGrapher signal).
    ``drugs``         : restrict to these drug names (else all drugs known to the map).
    ``agg``           : 'max' (a drug is as good as its best target) or 'mean'.
    """
    aggf = np.max if agg == "max" else np.mean
    cand = drugs if drugs is not None else list(dt_map.drug2targets)
    out = {}
    for d in cand:
        ts = [target_scores[t] for t in dt_map.targets_of(d) if t in target_scores]
        out[d] = float(aggf(ts)) if ts else float("-inf")
    return out


def drug_ranking_to_target_ranking(drug_scores: dict[str, float], dt_map: DrugTargetMap,
                                   targets: Optional[list[str]] = None,
                                   agg: str = "max") -> dict[str, float]:
    """Score each target by aggregating the scores of the drugs that hit it (EvalShift -> targets)."""
    aggf = np.max if agg == "max" else np.mean
    # build target set
    if targets is None:
        targets = sorted({t for d in drug_scores for t in dt_map.targets_of(d)})
    out = {}
    for t in targets:
        ds = [drug_scores[d] for d in dt_map.drugs_of(t) if d in drug_scores]
        out[t] = float(aggf(ds)) if ds else float("-inf")
    return out


def ground_truth_targets(df: pd.DataFrame, query_id: str, dt_map: DrugTargetMap,
                         thresh: float = FIELD_GT_THRESH) -> list[str]:
    """Targets hit by the query's ground-truth drugs (for target-side recall/nDCG)."""
    gt_drugs = ground_truth_drugs(df, query_id, thresh)
    tset = set()
    for d in gt_drugs:
        tset.update(dt_map.targets_of(d))
    return sorted(tset)
