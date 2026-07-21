#!/usr/bin/env python
"""Regenerate exp13's acceptance report from its existing projection.csv.

The diagnosis pass over the real tasks is expensive (energy distances over hundreds of
populations). The report is cheap. Separating them means a formatting change to the report
does not cost a full re-diagnosis, and it means a crash while writing the report cannot
destroy the diagnosis that preceded it.

    PYTHONPATH=src python src/experiments/exp13_regen_report.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from experiments.exp13_real_data_projection import (
    OUT, _acceptance_report, fit_hir_boundary,
)
from utils.io import results_path
from utils.logging import log, section


def main() -> None:
    section("EXP13 — regenerate the acceptance report from projection.csv")
    p = results_path(OUT, "projection.csv")
    if not Path(p).exists():
        raise SystemExit(f"{p} not found; run exp13_real_data_projection.py first")

    df = pd.read_csv(p)
    log(f"  loaded {len(df)} diagnosed tasks from {p}")

    boundary = fit_hir_boundary()
    # the report needs the transferred threshold, which run() computes on the observed tasks
    obs_conf = df[df.information_condition_mode == "observed"].preference_conflict
    boundary["real_conflict_threshold"] = float(
        obs_conf.quantile(boundary["conflict_crossover_percentile"]))

    report = _acceptance_report(df, boundary)
    out = Path(results_path(OUT, "acceptance_report.md"))
    out.write_text(report)
    log(f"  wrote {out}")

    section("VERDICT")
    for line in report.splitlines():
        if any(k in line for k in ("VACUOUS", "majority-class baseline", "projection accuracy",
                                   "observed-label", "tautology", "distributionally dominant")):
            log("  " + line.strip())


if __name__ == "__main__":
    main()
