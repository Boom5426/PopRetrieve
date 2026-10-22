#!/usr/bin/env python
"""Conditional bottleneck regression on all queries and on queries below the mean-cosine ceiling.

Outcome: energy-population reciprocal rank in the Tahoe-100M oracle arm. Covariates: mean-cosine
reciprocal rank and the standardised interaction ratio, interaction reproducibility R_int and
response detectability A_sup. Standard errors are clustered by cell line with the CR1 small-sample
correction, and intervals use a t distribution with (clusters - 1) degrees of freedom.

    python -I src/experiments/exp19_ceiling_sensitivity.py \
        --per-query results/phase2_transition/bottleneck/bottleneck_per_query.csv \
        --out results/phase2_transition/bottleneck/ceiling_sensitivity.csv
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

TERMS = ["interaction_share", "R_int", "A_sup"]


def fit(df: pd.DataFrame, label: str) -> pd.DataFrame:
    """OLS of y on [const, ref, standardised TERMS] with CR1 cell-line-clustered errors."""
    X = df[TERMS].copy()
    X = (X - X.mean()) / X.std(ddof=0)
    X.insert(0, "ref", df["ref"].values)
    X.insert(0, "const", 1.0)
    Xm = X.values
    y = df["y"].values
    XtX = np.linalg.inv(Xm.T @ Xm)
    b = XtX @ Xm.T @ y
    e = y - Xm @ b
    g = df["cell_line"].values
    G = np.unique(g)
    n, k = Xm.shape
    meat = sum(np.outer(Xm[g == c].T @ e[g == c], Xm[g == c].T @ e[g == c]) for c in G)
    V = XtX @ meat @ XtX * (len(G) / (len(G) - 1)) * ((n - 1) / (n - k))
    se = np.sqrt(np.diag(V))
    t = stats.t.ppf(0.975, len(G) - 1)
    return pd.DataFrame({"model": label, "term": X.columns, "beta": b,
                         "ci_lo": b - t * se, "ci_hi": b + t * se,
                         "p": 2 * stats.t.sf(np.abs(b / se), len(G) - 1),
                         "n": n, "n_clusters": len(G)})


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-query", required=True, help="bottleneck_per_query.csv")
    ap.add_argument("--out", required=True, help="output CSV")
    args = ap.parse_args()

    d = pd.read_csv(args.per_query)
    d = d.rename(columns={"RR_pop_oracle_vs_cos": "y", "RR_ref_oracle_vs_cos": "ref"})
    d = d.dropna(subset=TERMS + ["y", "ref"])
    d = d[np.isfinite(d.interaction_share)]
    res = pd.concat([fit(d, "all queries"),
                     fit(d[d.ref < 1], "reference not at ceiling (RR_ref < 1)")])
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    res.to_csv(args.out, index=False)
    print(res.round(4).to_string(index=False))


if __name__ == "__main__":
    main()
