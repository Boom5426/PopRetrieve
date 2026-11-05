#!/usr/bin/env python
"""Render Supplementary Table 8 (top-ranked candidates in the analogue tasks) from the result tables.

    python -I src/experiments/exp20_decision_level_table.py \
        --res results/exp20_decision_level --out supp_table8.tex

Every number comes from summary.csv and changed_top1.csv written by exp20_decision_level.py.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

TITLE = "Supplementary Table 8"
# (dataset, outcome label in summary.csv, row label in the table)
ROWS_A = [
    ("GDSC2", "top1 percentile, centred", "GDSC2, centred: top-1 percentile"),
    ("GDSC2", "top5 mean percentile, centred", "GDSC2, centred: top-5 mean percentile"),
    ("GDSC2", "top1 percentile, uncentred", "GDSC2, uncentred: top-1 percentile"),
    ("GDSC2", "top5 mean percentile, uncentred", "GDSC2, uncentred: top-5 mean percentile"),
    ("MoA", "Hit@1", "Mechanism: Hit@1"),
    ("MoA", "Hit@5", "Mechanism: Hit@5"),
]
STRUCT = "structure (energy - mean_l2)"
MAG = "magnitude (mean_l2 - mean_cosine)"
CRIT_LABEL = {"centred": "GDSC2, centred", "uncentred": "GDSC2, uncentred",
              "shares annotated mechanism": "Mechanism"}
CMP_LABEL = {"structure (energy vs mean_l2)": "Energy vs mean L2",
             "magnitude (mean_l2 vs mean_cosine)": "Mean L2 vs mean cosine"}


def signed(x: float, nd: int = 3) -> str:
    s = f"{x:+.{nd}f}"
    if float(s) == 0.0:
        s = f"{0:.{nd}f}"
    return f"${s}$"


def row(cells: list[str]) -> str:
    return " & ".join(cells) + " \\\\"


def longtable(colspec: str, first: list[str], panel: str, head: list[str],
              body: list[str]) -> list[str]:
    return [f"\\begin{{longtable}}{{{colspec}}}", *first,
            "\\toprule", row(head), "\\midrule", "\\endfirsthead",
            f"\\caption*{{\\textit{{{TITLE}({panel}) continued.}}}}\\\\",
            "\\toprule", row(head), "\\midrule", "\\endhead",
            "\\bottomrule", "\\endlastfoot", *body, "\\end{longtable}"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--res", required=True, help="results/exp20_decision_level")
    ap.add_argument("--out", required=True, help="output .tex file")
    args = ap.parse_args()
    res = Path(args.res)
    summ = pd.read_csv(res / "summary.csv")
    chg = pd.read_csv(res / "changed_top1.csv")

    def get(ds: str, outcome: str, quantity: str) -> pd.Series:
        sel = summ[(summ.dataset == ds) & (summ.outcome == outcome) & (summ.quantity == quantity)]
        assert len(sel) == 1, (ds, outcome, quantity)
        return sel.iloc[0]

    body_a = []
    for ds, outcome, label in ROWS_A:
        if not ((summ.dataset == ds) & (summ.outcome == outcome)).any():
            continue
        means = [f"{get(ds, outcome, r)['mean']:.3f}" for r in ("mean_cosine", "mean_l2", "energy")]
        ci = []
        for q in (MAG, STRUCT):
            r = get(ds, outcome, q)
            ci.append(f"{signed(r['mean'])} ({signed(r.ci_lo)}, {signed(r.ci_hi)})")
        n = get(ds, outcome, "energy")
        body_a.append(row([label, f"{int(n.n_queries):,} ({int(n.n_clusters)})", *means, *ci]))
    out = longtable(
        "@{}P{4.3cm}C{1.5cm}C{1.3cm}C{1.3cm}C{1.3cm}C{2.6cm}C{2.6cm}@{}",
        [f"\\caption*{{{{\\large\\bfseries {TITLE}. Top-ranked candidates in the analogue "
         "tasks.}}\\\\",
         "\\caption*{{\\bfseries (a) Outcome of the top-ranked candidates under each rule.}}\\\\"],
        "a", ["Criterion and outcome", "Queries (clusters)", "Mean cosine", "Mean L2", "Energy",
              "Mean L2 minus mean cosine", "Energy minus mean L2"], body_a)

    body_b = [row([CRIT_LABEL[r.criterion], CMP_LABEL[r.comparison],
                   f"{r.n_changed:,} of {r.n_queries:,}", f"{r.first_better:,}",
                   f"{r.first_worse:,}", f"{r.equal:,}"]) for r in chg.itertuples()]
    out += ["", "\\bigskip"] + longtable(
        "@{}P{4.4cm}P{3.4cm}C{2.2cm}C{1.6cm}C{1.6cm}C{1.4cm}@{}",
        [f"\\caption*{{{{\\large\\bfseries {TITLE} continued. (b) Queries in which two rules "
         "ranked different candidates first.}}\\\\"],
        "b", ["Criterion", "Comparison", "Changed queries", "First rule better",
              "First rule worse", "Equal"], body_b)

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
