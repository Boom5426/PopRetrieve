"""JUDGE Figure 4 panel 4h: Class C on a SEMANTICALLY MATCHED functional oracle.

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

FOCAL, COMP, GREY, INK = "#5185C0", "#E99D4E", "#7A7A7A", "#1A1A1A"
GREEN = "#55966B"
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC = f"{REPO}/figures/source_data/fig4hi_class_c_functional.csv"

# Category labels are ONE LINE EACH, and that is a legibility requirement rather than a
# preference. Set as two lines ("energy" / "(distributional retrieval)") the ten lines shared a
# single 13.3 pt row pitch with a 13.2 pt label height, so the gap BETWEEN two labels measured
# 0.07-0.29 pt while the gap INSIDE one label measured about 2.8 pt: the qualifier bound more
# tightly to the next category than to its own, and at print size the block read as ten
# undifferentiated lines. Only a taller axes could have opened that pitch, and row 3's height is
# shared with panel i, whose equal-aspect scatter would have gone portrait. One line per bar makes
# the pitch (13.3 pt) five times the label height's own leading, so each label is unambiguously
# its bar's. The cost is 1.51 in of left pad, taken out of this panel's axes width, which had
# 40% of its x range empty.
ROWS = [
    ("energy_rho",           "energy (distributional retrieval)",        FOCAL, True),
    ("mean_cosine_ctrl_rho", "mean cosine (control-subtracted)",         COMP,  True),
    ("mean_cosine_raw_rho",  "mean cosine (no control subtraction)",     GREY,  True),
    ("magnitude_match_rho",  "response-magnitude match (no retrieval)",  GREEN, False),
    ("potency_match_rho",    "potency match (no retrieval; diagnostic)", GREEN, False),
]
PARTIAL = "energy_rho_partial_magmatch"

# Panel title. Stated here rather than only in fig4_assemble.py so a standalone run cannot show a
# different claim from the composite. The old title ("similarity is anti-aligned with potency")
# described the WITHDRAWN potency oracle and contradicted these bars, on which energy leads.
TITLE_4H = "Energy leads, but a scalar reproduces the lead"


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
        # 0.014 rather than 0.012 rho: the axes is 0.46 in narrower than it was, so the offset
        # that used to put 4.2 pt between a value and its bar's end would now put 3.7 pt.
        ax.text(med + 0.014, y + 0.31, f"{med:+.3f}", va="center", ha="left",
                fontsize=5.8, fontweight="bold", color=INK)

    # the residual: what energy retains once the magnitude channel is removed
    pmed = float(d[PARTIAL].median())
    ytop = ys[0]
    ax.barh(ytop, pmed, height=0.60, color="none", edgecolor=INK, lw=1.0, ls=":", zorder=5)
    # 1:1 re-cut: the two-line gloss ("dotted: energy with the magnitude channel partialled out")
    # is stated verbatim in the Fig. 4 caption, so only the number it carries stays on the panel.
    # It used to sit in the 0.4-unit gap under the energy bar, which is 5.3 pt tall and left this
    # 4 pt of ink 0.65 pt clear of two bar edges. It is set instead ON the energy row, to the right
    # of that row's rightmost per-cell-line median (+0.45), in the data-free right third of the x
    # range: same row, so the association is unambiguous, and the nearest ink is 0.2 in away.
    ax.text(0.500, ytop, f"dotted: partial {pmed:+.3f}",
            fontsize=5.6, color=INK, va="center", ha="left")

    ax.axvline(0, color=INK, lw=0.9, zorder=3)
    ax.set_yticks(ys)
    ax.set_yticklabels([r[1] for r in ROWS], fontsize=5.8)
    ax.set_xlabel(r"Spearman $\rho$ with drug-drug functional similarity", fontsize=6.2)
    # The x range must clear the per-cell-line medians, not just the bars: the A549 median for
    # potency match is +0.68 and was being clipped off the old 0.50 limit.
    ax.set_xlim(-0.03, 0.80)
    ax.set_xticks([0.0, 0.2, 0.4, 0.6, 0.8])
    ax.set_ylim(-0.72, len(ROWS) - 0.32)
    ax.tick_params(axis="x", labelsize=5.8)
    ax.tick_params(axis="y", length=0)
    for sp in ["right", "top", "left"]:
        ax.spines[sp].set_visible(False)

    # No detached key: the hatch is defined by the axis labels themselves ("no retrieval"), which
    # is where the reader is already looking, and by the caption. The open-circle / per-cell-line
    # median note lives in the caption too, where it costs no space.


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(4.6, 2.4))
    draw_4h(ax)
    ax.set_title(TITLE_4H, loc="left", fontsize=8)
    fig.savefig(os.path.join(os.path.dirname(__file__), "4h.png"), dpi=200, bbox_inches="tight")
    print("wrote 4h.png")
