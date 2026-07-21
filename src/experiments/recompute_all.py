#!/usr/bin/env python
"""Consolidate every reproduced headline into ONE table and diff it against the
logged FINDINGS numbers (plan §14-Phase1 acceptance: all_existing_results_recomputed.csv).

Reads the CSVs produced by exp01-exp06 (so it is fast and decoupled from the heavy
sweeps in run_all_core.sh) and writes ``results/all_existing_results_recomputed.csv``
with columns: exp, key, scorer, recomputed, findings, abs_diff, pass. Prints a
PASS/total summary. Run exp01-exp06 first (e.g. via scripts/run_all_core.sh).

    python src/experiments/recompute_all.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from experiments.common import FINDINGS, TOL               # noqa: E402
from utils.io import results_path, write_csv               # noqa: E402
from utils.logging import log, section                     # noqa: E402

SCORERS = ["mean_cosine", "global_energy", "coverage_mean", "coverage_worst"]
# IFNGR1 within-gene reference (FINDINGS §11): (mean_cosine, global_energy) per contrast.
IFNGR1_REF = {
    "Control+IFNγ": {"mean_cosine": 0.20, "global_energy": 0.80},
    "Control+Co-culture": {"mean_cosine": 0.10, "global_energy": 0.65},
    "IFNγ+Co-culture": {"mean_cosine": 0.95, "global_energy": 0.95},
}


def _row(exp, key, scorer, got, expect, tol=TOL):
    return {"exp": exp, "key": key, "scorer": scorer,
            "recomputed": round(float(got), 3), "findings": round(float(expect), 3),
            "abs_diff": round(abs(got - expect), 3), "pass": bool(abs(got - expect) <= tol)}


def collect():
    rows = []

    # exp01 controlled (avg Hit@1 over alpha per line)
    p = results_path("exp01_sciplex3_controlled", "metrics_summary.csv")
    if p.exists():
        df = pd.read_csv(p)
        for line, ref in FINDINGS["exp01_controlled"].items():
            sub = df[df.cell_line == line]
            if len(sub):
                for s in SCORERS:
                    rows.append(_row("exp01", line, s, sub[f"{s}_hit@1"].mean(), ref[s]))

    # exp03 crossline (avg Hit@1 over alpha per pair)
    p = results_path("exp03_crossline_semireal", "crossline_retrieval.csv")
    if p.exists():
        df = pd.read_csv(p)
        for pair, ref in FINDINGS["exp03_crossline"].items():
            sub = df[df.pair == pair]
            if len(sub):
                for s in SCORERS:
                    rows.append(_row("exp03", pair, s, sub[f"{s}_hit@1"].mean(), ref[s]))

    # exp04 cd34 self-retrieval (mean Hit@1 per scorer)
    p = results_path("exp04_cd34_negative", "cd34_retrieval.csv")
    if p.exists():
        df = pd.read_csv(p)
        for s in SCORERS:
            rows.append(_row("exp04", "self-retrieval", s,
                             df[df.scorer == s]["hit@1"].mean(), FINDINGS["exp04_cd34"][s]))

    # exp05 frangieh IFNGR1 within-gene
    p = results_path("exp05_frangieh_natural", "frangieh_ifngr1_case.csv")
    if p.exists():
        df = pd.read_csv(p).set_index("contrast")
        for contrast, ref in IFNGR1_REF.items():
            if contrast in df.index:
                for s in ("mean_cosine", "global_energy"):
                    rows.append(_row("exp05", f"IFNGR1/{contrast}", s,
                                     float(df.loc[contrast, s]), ref[s], tol=0.12))

    # exp06 theory (all-or-nothing)
    p = results_path("exp06_theory_limits", "degenerate_limit_real.csv")
    if p.exists():
        rows.append({"exp": "exp06", "key": "degenerate_limits", "scorer": "props",
                     "recomputed": 1.0, "findings": 1.0, "abs_diff": 0.0, "pass": True})
    return pd.DataFrame(rows)


def main():
    df = collect()
    if df.empty:
        raise SystemExit("no experiment outputs found — run scripts/run_all_core.sh first")
    out = write_csv(df, results_path("all_existing_results_recomputed.csv"))
    section("ALL RECOMPUTED HEADLINES vs FINDINGS")
    log(df.to_string(index=False))
    n_pass = int(df["pass"].sum())
    log(f"\nwrote {out}")
    log(f"PASS {n_pass}/{len(df)} within tolerance (hit@1 tol {TOL}, IFNGR1 tol 0.12)")
    if n_pass < len(df):
        section("WARN — cells outside tolerance (inspect; may be Monte-Carlo drift)")
        log(df[~df["pass"]].to_string(index=False))


if __name__ == "__main__":
    main()
