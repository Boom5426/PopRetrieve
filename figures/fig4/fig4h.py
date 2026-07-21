"""DART Figure 4 panel 4h: Class C on a SEMANTICALLY MATCHED functional oracle.

Source data: source_data/fig4hi_class_c_functional.csv
  103 leave-one-drug-out queries, SciPlex3 x GDSC2, 10 uM, 34-35 drugs per cell line.

WHAT CHANGED, AND WHY IT MATTERS
--------------------------------
This panel used to grade each ranking against ABSOLUTE POTENCY. That is the wrong oracle for a
retrieval task and it produced a conclusion that does not follow. A similarity retriever is asked
which candidate RESEMBLES the query, not which candidate is most cytotoxic; handed a weak query it
SHOULD return other weak drugs. Grading it on potency therefore all but guaranteed both the
negative correlation and the apparent triumph of a magnitude scalar, since potency is largely
driven by response magnitude and the scalar sorts by magnitude. That comparison survives only as a
confounder audit (Extended Data).

The matched oracle is DRUG-DRUG FUNCTIONAL SIMILARITY: do query and candidate behave alike in an
independent assay? Each compound's GDSC2 dose-response AUC profile across 966 cell lines (the three
SciPlex3 lines held out, so the oracle is out of context) gives
    oracle(q,c) = Spearman( AUC_profile(q), AUC_profile(c) )
Cell-line mean AUC, estimated over all 286 GDSC2 compounds, is subtracted first: cell lines differ
hugely in general drug sensitivity, and left uncorrected that shared main effect makes 85% of all
drug pairs look similar.

THE FINDING IS LAYERED AND THE PANEL MUST SHOW BOTH LAYERS:
  * energy retrieval DOES beat the correctly specified mean incumbent (+0.276 vs +0.083), the
    first oracle-invisible criterion in this study on which the distributional score wins;
  * but a QUERY-DEPENDENT SCALAR that only matches response magnitude, comparing no distributions
    at all, reaches +0.232, and partialling that channel out leaves energy with +0.097.
Bars are therefore split into "performs retrieval" and "performs none", and the partial is drawn
as a dotted remainder inside the energy bar. A reader who takes only the energy bar away from this
panel has taken the wrong thing away, so the panel does not let them.

Run standalone: python fig4h.py
"""
import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

FOCAL, COMP, GREY, INK = "#5185C0", "#E99D4E", "#7A7A7A", "#1A1A1A"
GREEN = "#55966B"
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC = f"{REPO}/figures/source_data/fig4hi_class_c_functional.csv"

ROWS = [
    ("energy_rho",           "energy\n(distributional retrieval)",        FOCAL, True),
    ("mean_cosine_ctrl_rho", "mean cosine\n(control-subtracted)",         COMP,  True),
    ("mean_cosine_raw_rho",  "mean cosine\n(no control subtraction)",     GREY,  True),
    ("magnitude_match_rho",  "response-magnitude match\n(NO retrieval)",  GREEN, False),
    ("potency_match_rho",    "potency match\n(NO retrieval; diagnostic)", GREEN, False),
]
PARTIAL = "energy_rho_partial_magmatch"


def draw_4h(ax):
    if not os.path.exists(SRC):
        raise FileNotFoundError(
            f"{SRC} does not exist. Run analysis/class_c/class_c_functional_oracle.py and export "
            f"the per-query table. This panel will not render placeholder correlations.")
    d = pd.read_csv(SRC)
    if len(d) < 50:
        raise ValueError(f"{SRC} has only {len(d)} queries; expected 103.")

    ys = np.arange(len(ROWS))[::-1]
    for y, (col, _lab, colour, does_retrieval) in zip(ys, ROWS):
        med = float(d[col].median())
        ax.barh(y, med, height=0.60, color=colour, alpha=0.90 if does_retrieval else 0.38,
                edgecolor=colour, lw=1.0, hatch=None if does_retrieval else "///", zorder=2)
        for _line, s in d.groupby("cell_line"):        # per-line medians: the honest unit
            ax.plot(float(s[col].median()), y, "o", ms=2.6, mfc="white", mec=INK, mew=0.6,
                    zorder=4)
        ax.text(med + 0.012, y + 0.31, f"{med:+.3f}", va="center", ha="left",
                fontsize=5.8, fontweight="bold", color=INK)

    # the residual: what energy retains once the magnitude channel is removed
    pmed = float(d[PARTIAL].median())
    ytop = ys[0]
    ax.barh(ytop, pmed, height=0.60, color="none", edgecolor=INK, lw=1.0, ls=":", zorder=5)
    ax.annotate(f"partial on magnitude match: {pmed:+.3f}",
                xy=(pmed, ytop - 0.14), xytext=(pmed + 0.055, ytop - 0.95),
                fontsize=5.2, color=INK,
                arrowprops=dict(arrowstyle="->", lw=0.7, color=INK))

    ax.axvline(0, color=INK, lw=0.9, zorder=3)
    ax.set_yticks(ys)
    ax.set_yticklabels([r[1] for r in ROWS], fontsize=5.4)
    ax.set_xlabel(r"Spearman $\rho$ with drug-drug functional similarity"
                  "\n(GDSC2 dose-response; SciPlex3 lines held out)", fontsize=6)
    ax.set_xlim(-0.02, 0.50)
    ax.set_ylim(-0.95, len(ROWS) - 0.35)
    ax.tick_params(axis="x", labelsize=5.6)
    for sp in ["right", "top", "left"]:
        ax.spines[sp].set_visible(False)

    # Legend labels shortened ("performs retrieval" -> "retrieval") so the key still fits at the
    # 5.5 pt floor Nature enforces at final size. The open-circle / per-cell-line-median note that
    # used to sit under this axis at 4.7 pt now lives in the caption, where it costs no space.
    ax.legend(handles=[
        Patch(facecolor=FOCAL, alpha=0.90, label="retrieval"),
        Patch(facecolor=GREEN, alpha=0.38, hatch="///", label="no retrieval"),
    ], fontsize=5.5, loc="lower right", frameon=False, handlelength=1.3,
        borderaxespad=0.2, labelspacing=0.25)


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(3.7, 2.9))
    draw_4h(ax)
    ax.set_title("Retrieval wins, and a scalar reproduces the win", loc="left", fontsize=8)
    fig.savefig(os.path.join(os.path.dirname(__file__), "4h.png"), dpi=200, bbox_inches="tight")
    print("wrote 4h.png")
