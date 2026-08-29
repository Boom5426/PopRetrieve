"""PopRetrieve Figure 3 panel 3h: Class C on a SEMANTICALLY MATCHED functional oracle.

Source data: source_data/fig3hi_class_c_functional.csv
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

Run standalone: python fig3h.py
"""
import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Palette comes from the house-style module; do NOT re-declare the hex values here. Every
# panel file used to carry its own copy, which made figstyle's "one edit here recolours the
# whole deck" untrue: a recolour meant editing 43 files and missing one was silent.
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
from figstyle import FOCAL_SOFT, COMP_SOFT, GREY, INK, TRACK, META  # noqa: E402
GREEN_SOFT = "#55966B"
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC = f"{REPO}/figures/source_data/fig3hi_class_c_functional.csv"

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
    ("energy_rho",           "energy (distributional retrieval)",        FOCAL_SOFT, True),
    ("mean_cosine_ctrl_rho", "mean cosine (control-subtracted)",         COMP_SOFT,  True),
    ("mean_cosine_raw_rho",  "mean cosine (no control subtraction)",     GREY,  True),
    ("magnitude_match_rho",  "response-magnitude match (no retrieval)",  GREEN_SOFT, False),
    ("potency_match_rho",    "potency match (no retrieval; diagnostic)", GREEN_SOFT, False),
]
PARTIAL = "energy_rho_partial_magmatch"

# Panel title. Stated here rather than only in fig3_assemble.py so a standalone run cannot show a
# different claim from the composite. The old title ("similarity is anti-aligned with potency")
# described the WITHDRAWN potency oracle and contradicted these bars, on which energy leads.
TITLE_4H = "Energy leads, but a scalar reproduces the lead"


def draw_3h(ax):
    if not os.path.exists(SRC):
        raise FileNotFoundError(
            f"{SRC} does not exist. Run analysis/class_c/class_c_functional_oracle.py and export "
            f"the per-query table. This panel will not render placeholder correlations.")
    d = pd.read_csv(SRC)
    if len(d) < 50:
        raise ValueError(f"{SRC} has only {len(d)} queries; expected 103.")

    # The track states the axis: rho runs to +0.80 here, and drawing it makes every bar read as
    # a fraction of the same span instead of against a distant axis. Open control bars knock a
    # white gap in their own track, which is exactly what "this one does no retrieval" should
    # look like.
    TRACK_MAX = 0.80
    LABEL_X = TRACK_MAX + 0.02
    ys = np.arange(len(ROWS))[::-1]
    for y, (col, _lab, colour, does_retrieval) in zip(ys, ROWS):
        ax.barh(y, TRACK_MAX, height=0.60, color=TRACK, lw=0, zorder=1)
        med = float(d[col].median())
        # Filled = the bar ranks candidates; open = a no-retrieval control. Open bars are the
        # standard journal encoding for a control series, and they replace a "///" hatch at 38%
        # alpha, which was three visual channels (fill, hatch, transparency) spent on one binary.
        ax.barh(y, med, height=0.60, color=colour if does_retrieval else "white",
                edgecolor=colour, lw=0.8, zorder=2)
        for _line, s in d.groupby("cell_line"):        # per-line medians: the honest unit
            ax.plot(float(s[col].median()), y, "o", ms=2.6, mfc="white", mec=INK, mew=0.6,
                    zorder=4)
        # One label lane past the end of the track, not five labels chasing five bar tips.
        ax.text(LABEL_X, y, f"{med:+.3f}", va="center", ha="left", fontsize=5.8, color=META)

    # the residual: what energy retains once the magnitude channel is removed
    pmed = float(d[PARTIAL].median())
    ytop = ys[0]
    ax.barh(ytop, pmed, height=0.60, color="none", edgecolor=INK, lw=0.8, ls=":", zorder=5)
    # 1:1 re-cut: the two-line gloss ("dotted: energy with the magnitude channel partialled out")
    # is stated verbatim in the Fig. 3 caption, so only the number it carries stays on the panel.
    # It used to sit in the 0.4-unit gap under the energy bar, which is 5.3 pt tall and left this
    # 4 pt of ink 0.65 pt clear of two bar edges. It is set instead ON the energy row, to the right
    # of that row's rightmost per-cell-line median (+0.45), in the data-free right third of the x
    # range: same row, so the association is unambiguous, and the nearest ink is 0.2 in away.
    # The dotted overlay and its value are defined in the caption. Naming an encoding on the
    # panel and again in the legend is the duplication production asks authors to remove.
    _ = pmed

    ax.axvline(0, color=INK, lw=0.7, zorder=3)
    ax.set_yticks(ys)
    ax.set_yticklabels([r[1] for r in ROWS], fontsize=5.8)
    ax.set_xlabel(r"Spearman $\rho$ with drug-drug functional similarity", fontsize=6.2)
    # The x range must clear the per-cell-line medians, not just the bars: the A549 median for
    # potency match is +0.68 and was being clipped off the old 0.50 limit.
    ax.set_xlim(-0.03, 0.965)
    ax.set_xticks([0.0, 0.2, 0.4, 0.6, 0.8])
    ax.spines['bottom'].set_bounds(0.0, TRACK_MAX)   # the axis is the track
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
    draw_3h(ax)
    ax.set_title(TITLE_4H, loc="left", fontsize=8)
    fig.savefig(os.path.join(os.path.dirname(__file__), "3h.png"), dpi=200, bbox_inches="tight")
    print("wrote 3h.png")
