#!/usr/bin/env python
"""Generator for ed1_metric_correlation.csv, the matrix behind main-text Fig. 2f.

WHY THIS FILE EXISTS
--------------------
figures/source_data/README.md records that this matrix had no generator: nothing under results/
was known to hold the query-candidate scores it summarises, so the panel could not be recomputed
from the released code and the README says in as many words not to present Fig. 2f as
reproducible. That was half right. exp08_signature_baselines.py does write every score, to
results/exp08_signature_baselines/per_query_scores.csv, but that file matches the
`results/**/per_query_scores.csv` line in .gitignore and so is absent from a fresh clone. The
matrix was therefore recomputable by re-running the experiment and not otherwise, and nothing said
so.

This closes that. Re-run exp08 and run this; the matrix is rebuilt from the per-query scores with
the correlation computed here rather than carried in a file with no parent.

WHAT CHANGED IN THE MATRIX ITSELF
---------------------------------
It gains `mean_l2`. Fig. 2f exists to show that the mean family and the population family rank
candidates by different information, and after Phase A that claim needs a magnitude-aware mean in
it: two thirds of the energy distance's oracle advantage over mean cosine is recovered by a scorer
that keeps only the mean and its magnitude (docs/phase2/03_ORACLE_RETRIEVAL_RESULTS.md). The
question the panel now answers is whether rho(mean_l2, energy) is materially higher than
rho(mean_cosine, energy). If it is, part of what looked like a separate information channel was
magnitude sensitivity.

Spearman, over every (query, candidate) pair pooled across all task settings, which is the same
unit the retired matrix used.

    python figures/source_data/build_metric_correlation.py
"""
from __future__ import annotations

import os
import sys

import pandas as pd
from scipy.stats import spearmanr

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC = os.path.join(REPO, "results", "exp08_signature_baselines", "per_query_scores.csv")
DST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ed1_metric_correlation.csv")

# The scorers the matrix carries, in no particular order here; Fig. 2f fixes the display order.
COLUMNS = ["mean_cosine", "mean_l2", "global_energy", "coverage_mean", "coverage_worst",
           "cmap_cosine", "cmap_wtcs"]


def build(src: str = SRC) -> pd.DataFrame:
    if not os.path.exists(src):
        raise FileNotFoundError(
            f"{src} is missing. It is written by src/experiments/exp08_signature_baselines.py and "
            f"is git-ignored (results/**/per_query_scores.csv), so a fresh clone must re-run that "
            f"experiment before this matrix can be built.")
    d = pd.read_csv(src)
    missing = [c for c in COLUMNS if c not in d.columns]
    if missing:
        raise KeyError(
            f"per_query_scores.csv lacks {missing}; present: {sorted(d.columns)}. "
            f"mean_l2 was added to retrieval.rankers.SCORERS on 2026-09-03, so a per-query file "
            f"written before that will not carry it and the experiment must be re-run.")
    m = pd.DataFrame(index=COLUMNS, columns=COLUMNS, dtype=float)
    for a in COLUMNS:
        for b in COLUMNS:
            m.loc[a, b] = 1.0 if a == b else float(spearmanr(d[a], d[b]).statistic)
    m.attrs["n_pairs"] = len(d)
    return m


def main() -> None:
    m = build()
    m.to_csv(DST)
    print(f"wrote {DST}  ({len(m)} scorers, {m.attrs['n_pairs']:,} query-candidate pairs)")
    print(m.round(3).to_string())


if __name__ == "__main__":
    sys.exit(main())
