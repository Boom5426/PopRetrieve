#!/usr/bin/env python
"""Render Supplementary Table 7 (dose-mismatch re-identification) from the result tables.

    python -I src/experiments/exp18_dose_mismatch_table.py \
        --res results/exp18_dose_mismatch --out supp_table7.tex

The output holds the three panel longtables that the Supplementary Information reads with \\input
inside its own table group and note, so every number in the table comes from summary_by_dose_pair.csv,
primary_contrasts.csv and summary_all_dose_library.csv without transcription.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

DOSE_LABEL = {10.0: "0.01", 100.0: "0.1", 1000.0: "1", 10000.0: "10"}
CONTRAST_LABEL = {"d_mag": "mean L2 minus mean cosine",
                  "d_struct": "energy minus mean L2",
                  "d_energy_cos": "energy minus mean cosine"}
CONDITION_LABEL = {"matched": "Matched", "mismatched": "Mismatched",
                   "mismatched_minus_matched": "Mismatched minus matched"}
SUBSET_LABEL = {"all": "All compounds", "responsive": "Responsive subset"}
TITLE = "Supplementary Table 7"
PAIRS = "Query--\\allowbreak seed pairs"


def signed(x: float, nd: int = 3) -> str:
    """Signed fixed-point number in LaTeX math, with a true minus sign."""
    s = f"{x:+.{nd}f}"
    if float(s) == 0.0:
        s = f"{0:.{nd}f}"
    return f"${s}$"


def row(cells: list[str]) -> str:
    return " & ".join(cells) + " \\\\"


def longtable(colspec: str, first: list[str], panel: str, head: list[str],
              body: list[str]) -> list[str]:
    """One panel as a longtable with its own header on every page."""
    return [f"\\begin{{longtable}}{{{colspec}}}", *first,
            "\\toprule", row(head), "\\midrule", "\\endfirsthead",
            f"\\caption*{{\\textit{{{TITLE}({panel}) continued.}}}}\\\\",
            "\\toprule", row(head), "\\midrule", "\\endhead",
            "\\bottomrule", "\\endlastfoot", *body, "\\end{longtable}"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--res", required=True, help="results/exp18_dose_mismatch")
    ap.add_argument("--out", required=True, help="output .tex file")
    args = ap.parse_args()
    res = Path(args.res)

    summ = pd.read_csv(res / "summary_by_dose_pair.csv")
    summ = summ[summ.subset == "all"].sort_values(["dose_query", "dose_library"])
    assert len(summ) == 16, len(summ)
    cont = pd.read_csv(res / "primary_contrasts.csv")
    alld = pd.read_csv(res / "summary_all_dose_library.csv").sort_values("dose_query")
    assert len(alld) == 4, len(alld)

    mrr_head = ["MRR, mean cosine", "MRR, mean L2", "MRR, energy",
                "Mean L2 minus mean cosine", "Energy minus mean L2"]

    def mrr_cells(r) -> list[str]:
        return [f"{r.MRR_mean_cosine:.3f}", f"{r.MRR_mean_l2:.3f}", f"{r.MRR_energy:.3f}",
                signed(r.MRR_mean_l2 - r.MRR_mean_cosine), signed(r.MRR_energy - r.MRR_mean_l2)]

    body_a = [row([DOSE_LABEL[r.dose_query], DOSE_LABEL[r.dose_library], f"{r.n_queries:,}",
                   *mrr_cells(r)]) for r in summ.itertuples()]
    out = longtable(
        "@{}C{1.4cm}C{1.4cm}C{1.7cm}C{1.8cm}C{1.8cm}C{1.8cm}C{2.3cm}C{2.3cm}@{}",
        [f"\\caption*{{{{\\large\\bfseries {TITLE}. Re-identification across matched and "
         "mismatched doses in SciPlex3.}}\\\\",
         "\\caption*{{\\bfseries (a) All 16 ordered dose pairs.}}\\\\"],
        "a", ["Query dose ($\\mu$M)", "Library dose ($\\mu$M)", PAIRS, *mrr_head], body_a)

    body_b: list[str] = []
    for subset in ("all", "responsive"):
        for contrast in ("d_mag", "d_struct", "d_energy_cos"):
            if body_b:
                body_b.append("\\addlinespace")
            body_b.append(f"\\multicolumn{{4}}{{@{{}}l}}{{\\textit{{{SUBSET_LABEL[subset]}, "
                          f"{CONTRAST_LABEL[contrast]}}}}} \\\\")
            for cond in ("matched", "mismatched", "mismatched_minus_matched"):
                sel = cont[(cont.subset == subset) & (cont.contrast == contrast)
                           & (cont.condition == cond)]
                assert len(sel) == 1, (subset, contrast, cond)
                r = sel.iloc[0]
                body_b.append(row([f"\\quad {CONDITION_LABEL[cond]}", f"{int(r.n_queries):,}",
                                   f"{int(r.n_drugs)}",
                                   f"{signed(r['mean'])} ({signed(r.ci_lo)}, {signed(r.ci_hi)})"]))
    out += ["", "\\bigskip"] + longtable(
        "@{}P{6.4cm}C{2.2cm}C{2.2cm}C{5.4cm}@{}",
        [f"\\caption*{{{{\\large\\bfseries {TITLE} continued. (b) Primary contrasts at 1 and "
         "10\\,$\\mu$M.}}\\\\"],
        "b", ["Condition", PAIRS, "Compounds", "MRR difference (95\\% CI)"], body_b)

    body_c = [row([DOSE_LABEL[r.dose_query], f"{r.n_queries:,}", *mrr_cells(r)])
              for r in alld.itertuples()]
    out += ["", "\\bigskip"] + longtable(
        "@{}C{1.8cm}C{1.9cm}C{2.0cm}C{2.0cm}C{2.0cm}C{2.4cm}C{2.4cm}@{}",
        [f"\\caption*{{{{\\large\\bfseries {TITLE} continued. (c) All-dose library.}}}}\\\\"],
        "c", ["Query dose ($\\mu$M)", PAIRS, *mrr_head], body_c)

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
