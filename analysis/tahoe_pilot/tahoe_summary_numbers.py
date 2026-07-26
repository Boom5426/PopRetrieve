"""Single source of truth for every Tahoe number quoted in the manuscript.

The manuscript quotes each headline figure through a LaTeX macro rather than as a literal, so
that the text, the figure caption and the Methods cannot drift apart. This script derives every
one of those numbers from the pilot's per-condition and per-pair CSVs and writes them to
results/tahoe_pilot/manuscript_numbers.json, which is what the macro block in the .tex is copied
from. If a number in the paper is ever doubted, it is recomputed by running this file.

Numbers only; no plots. Run: python tahoe_summary_numbers.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
from scipy.stats import spearmanr

REPO = Path(__file__).resolve().parents[2]
P = REPO / "results" / "tahoe_pilot"


def main() -> int:
    g1 = pd.read_csv(P / "gate1_per_condition.csv")
    g2 = pd.read_csv(P / "g2panel" / "gate2_clusterer_panel.csv")
    cc = pd.read_csv(P / "disjoint" / "gate3_disjoint_cellcycle_G1_vs_G2M.csv")
    st = pd.read_csv(P / "disjoint" / "gate3_disjoint_controlstate_k2.csv")
    ov = pd.read_csv(P / "gate3_per_line.csv")
    ov = ov[ov.compartment == "G2M"]

    c = g1.induced_cosine_G1_vs_G2M
    n = {
        # scope
        "TAHOELINES": int(g1.cell_line.nunique()),
        "TAHOEDRUGS": int(g1.drug.nunique()),
        "TAHOECONDS": int(len(g1)),
        # Gate 1
        "TAHOEGONE": f"{c.median():.3f}",
        "TAHOEGONEQ": f"{c.quantile(.25):.3f} to {c.quantile(.75):.3f}",
        # what fraction of unconstructed conditions are as divergent as the manuscript's anchors
        "TAHOEBELOWREAL": f"{100 * (c < 0.205).mean():.1f}",
        "TAHOEBELOWMIX": f"{100 * (c < 0.05).mean():.2f}",
        # Gate 2, best of the same four-method panel the manuscript reports
        "TAHOEGTWOCEIL": f"{g2.supervised_ceiling.median():.3f}",
        "TAHOEGTWOUNSUP": f"{g2.best_unsupervised.median():.3f}",
        "TAHOEGTWOGAP": f"{g2.gap_vs_best.median():.3f}",
        "TAHOEGTWOPAIRS": int(len(g2)),
        "TAHOEGTWOLINES": int(g2.cell_line.nunique()),
        "TAHOEGTWOLINESPOS": int((g2.groupby("cell_line").gap_vs_best.median() > 0.05).sum()),
        "TAHOEKMEANS": f"{g2.kmeans_full.median():.3f}",
        "TAHOEGMM": f"{g2.gmm_pca.median():.3f}",
        "TAHOELEIDEN": f"{g2.leiden_pca.median():.3f}",
        # Gate 3, disjoint cell sets, both partitions
        "TAHOEGTHREECC": f"{cc.spearman_rho.median():.3f}",
        "TAHOEGTHREECCN": int(len(cc)),
        "TAHOEGTHREEST": f"{st.spearman_rho.median():.3f}",
        "TAHOEGTHREESTN": int(len(st)),
        "TAHOEGTHREESTOPEN": int((st.spearman_rho < 0.5).sum()),
        "TAHOEGTHREESTMIN": f"{st.spearman_rho.min():.3f}",
        "TAHOEGTHREEOVERLAP": f"{ov.spearman_rho.median():.3f}",
    }

    # Gate 1 versus Gate 3: is the third condition merely the first restated?
    #
    # This must be computed WITHIN one partition. Gate 1 is defined on the cell-cycle split, so
    # the comparison uses the cell-cycle Gate 3, not the control-state one; correlating a
    # cell-cycle Gate 1 against a control-state Gate 3 would compare two different partitions and
    # the number would mean nothing. The cross-partition value is reported separately below and
    # labelled as such.
    med = g1.groupby("cell_line").induced_cosine_G1_vs_G2M.median().rename("g1")
    j = cc.set_index("cell_line").join(med, how="inner").dropna(subset=["g1", "spearman_rho"])
    rho, _ = spearmanr(j.g1, j.spearman_rho)
    n["TAHOECOUPLING"] = f"{rho:.3f}"
    n["TAHOECOUPLINGRSQ"] = f"{rho ** 2:.3f}"
    n["TAHOECOUPLINGN"] = int(len(j))
    # the five contexts with the MOST divergent subpopulations still show a closed Gate 3
    lo = j.nsmallest(5, "g1")
    n["TAHOEOPENGONE"] = f"{lo.g1.min():.3f} to {lo.g1.max():.3f}"
    n["TAHOEOPENGTHREE"] = f"{lo.spearman_rho.min():.3f} to {lo.spearman_rho.max():.3f}"
    # cross-partition, reported only to show that the two partitions are not interchangeable
    jx = st.set_index("cell_line").join(med, how="inner").dropna(subset=["g1", "spearman_rho"])
    n["TAHOECOUPLINGCROSS"] = f"{spearmanr(jx.g1, jx.spearman_rho)[0]:.3f}"
    # do the two partitions agree on WHICH contexts are open
    k = st.set_index("cell_line").spearman_rho.rename("st").to_frame().join(
        cc.set_index("cell_line").spearman_rho.rename("cc"), how="inner").dropna()
    n["TAHOEPARTAGREE"] = f"{spearmanr(k.st, k.cc)[0]:.3f}"

    out = P / "manuscript_numbers.json"
    out.write_text(json.dumps(n, indent=2))
    print(json.dumps(n, indent=2))
    print(f"\nwrote {out}")
    print("\n---- LaTeX macro block ----")
    for k_, v in n.items():
        print(f"\\newcommand{{\\{k_}}}{{{v}}}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
