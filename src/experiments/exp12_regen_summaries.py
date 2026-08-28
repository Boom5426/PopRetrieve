#!/usr/bin/env python
"""Regenerate exp12's aggregate tables from its per-query CSV, with the pairing bug fixed.

Why this exists. exp12's `recommendation_vs_outcome.csv` disagreed with exp12's own
`per_query_scores.csv`: it reported a median regret reduction of 0.1133 for
DART_coverage_worst on the recommended subset where the per-query data give 0.1190, and the
main figures were built from the aggregate, so the figures disagreed with the manuscript.

Two defects produced that:

1. The paired lookup keyed on (split_type, cell_line, heldout_drug, seed), which is NOT
   unique: the partial_library queries exist at observed_library_fraction 0.2 / 0.4 / 0.6
   under one such key. `ref.loc[key]` then returned three rows and `.iloc[0]` paired a PopRetrieve
   row at fraction 0.4 against a mean_cosine row at fraction 0.2.
2. Undefined MoA metrics carried a -1 sentinel and were averaged as if they were
   measurements.

Both are fixed at source (exp12_partial_observed_retrieval._recommendation_vs_outcome now
keys on all six fields and raises on a non-unique index; exp16_common.mask_undefined turns
the sentinel into NaN). This script re-derives the aggregate from the existing per-query
scores so the correction does not require a full re-run of the expensive scoring pass.

    PYTHONPATH=src python src/experiments/exp12_regen_summaries.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from experiments.exp12_partial_observed_retrieval import _recommendation_vs_outcome, OUT
from experiments.exp16_common import mask_undefined
from utils.io import results_path, write_csv
from utils.logging import log, section


def main() -> None:
    section("EXP12 — regenerate aggregate tables from per_query_scores.csv")
    p = results_path(OUT, "per_query_scores.csv")
    if not Path(p).exists():
        raise SystemExit(f"{p} not found; run exp12 FULL first")

    perf = pd.read_csv(p)
    log(f"  loaded {len(perf)} per-query rows")

    n_sentinel = int((perf["moa_ndcg"] <= -1 + 1e-9).sum()) if "moa_ndcg" in perf else 0
    perf = mask_undefined(perf)
    log(f"  masked {n_sentinel} undefined moa_ndcg sentinel values to NaN")

    rvo = _recommendation_vs_outcome(perf)
    out = results_path(OUT, "recommendation_vs_outcome.csv")
    write_csv(rvo, out)
    log(f"  wrote {out}")

    key = rvo[rvo.dart_method == "DART_coverage_worst"]
    section("DART_coverage_worst by recommendation mode (the Fig 3d / Fig 4d numbers)")
    log(key[["recommendation_mode", "n_queries", "median_regret_reduction",
             "mean_ndcg_gain", "n_ndcg_defined", "frac_regret_improved"]]
        .round(4).to_string(index=False))


if __name__ == "__main__":
    main()
