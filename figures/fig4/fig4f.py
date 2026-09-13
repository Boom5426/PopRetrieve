"""PopRetrieve Figure 4 panel b: is retrieval failure predictable, and from WHAT?

Source data: results/exp11_hir_benchmark/phase_grid_predictability_2x2.csv

A 2x2: {observable, evaluator-derived} features x {28 label-determining cells, 672 instances}.
HIR-Bench is the only setting in this study with a specified latent utility oracle, and that is
what makes the circularity measurable rather than arguable: every feature can be labelled
evaluator-derived or observable, and the size of the effect read off a dial.

Read across the top row: failure IS moderately predictable from what a retrieval method can
actually see at query time. Read across the bottom row: features derived from the benchmark's
own utility matrix are no better than chance, because they predict one function of the oracle
from another. Read down the columns: an instance-level holdout inflates the circular feature set
by +0.240 but the honest one by only +0.048. Pseudo-replication preferentially rescues features
that carry no generalizing signal, because memorizing near-duplicates is all such features can
do.

The label is a deterministic step function of (alpha, conflict), so the 13,440 instances contain
only 28 independent parameter cells; every held-out fold is single-class and no per-fold AUC
distribution exists. The 0.400-versus-0.5 gap is therefore NOT itself interpretable. The panel
draws 0.400 and cannot qualify it at this size, so the qualification is caption debt: as of
2026-08-31 the Fig. 4 caption does NOT yet carry it, and the number travels alone until it does.

2026-08-31, THE 6.5 pt PASS. This panel was the last of the deck still on the old 5 pt floor.
Colour and type now come from fig4_style; no size is typed here. One hex value survives, the
near-white midpoint of the diverging map, because it is the only colour this panel needs that
fig4_style does not export. See the CMAP note.
  RAISED  the four cell AUCs           7.0 -> PT_ANNOT 7.2
          the two arrow deltas         6.0 -> PT_SMALL 6.5
          the column and row labels    5.8 -> PT_TICK 6.8 (the explicit fontsize is deleted, so
                                       the rcParams tick size set by fig4_assemble applies)
          the colour-bar tick labels   5.8 -> PT_TICK 6.8
          the colour-bar label         5.8 -> PT_SMALL 6.5
  CUT     nothing. Every word on the panel survives the raise. Neither row label fits its gutter
          on two lines any more, so both are re-broken onto three: at 6.8 pt "evaluator-derived"
          measures 0.71 in and "at query time" 0.55 in, against the 0.52 in that is left of this
          panel's 0.60 in of slack once the tick pad is taken out. "evaluator-" splits at a hyphen
          the term already carries. Shortening either label would have cost the word that names
          what its row IS, which is the one thing this panel exists to measure.
          The earlier cuts stand and are OWED to the caption, which does not yet carry them:
          the in-cell verdicts ("moderately predictable" / "no better than chance"), the
          "cross-validation unit" axis label, the footnote keying the rule on the colour bar to
          the majority-class rate, and the single-class-fold caveat. Checked against
          manuscript/latex/PopRetrieve_manuscript.tex on 2026-08-31: the caption gives 0.788 and
          0.643 and the phrase "do not generalize beyond chance", and nothing else on this list.
  RETUNED for the taller box (1.40 x 1.75 in, was 1.36 x 1.46). The cell AUC, the delta label and
          the arrow are placed in DATA units, so the 0.29 in of new height stretched the gaps
          between them by 1.20x while the type stayed the same size. They are pulled back toward
          their own row's centre line so the pair reads as one cell rather than as two rows.

Run standalone: python fig4f.py
"""
import os
import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

# Colour and type come from the figure's style module; do NOT re-declare a hex value or type a
# point size here. Every panel file used to carry its own copy of the palette, which made
# "one edit here recolours the whole deck" untrue: a recolour meant editing 43 files and missing
# one was silent.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fig4_style import MEAN, POP, PT_ANNOT, PT_SMALL, TEXT  # noqa: E402
from color_preferences import MIDPOINT  # noqa: E402

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PRED = f"{REPO}/results/exp11_hir_benchmark/phase_grid_predictability_2x2.csv"

# The colour axis is the AUC value, not the arm: MEAN orange at the bottom of the scale, POP blue
# at the top, white at the midpoint. Which arm a cell belongs to is carried by its row.
# The midpoint is the neutral tone from the Figure 1 reference palette. The endpoints remain the
# semantic MEAN and POP colours imported from fig4_style, so the map does not invent a new arm.
# It is NOT re-declaring MEAN or POP, which
# are imported. The single-source fix is to re-export DIVMAP_SOFT from fig4_style and import it
# here; that is a fig4_style edit, outside this file, and is left for whoever owns that module.
CMAP = LinearSegmentedColormap.from_list("auc", [MEAN, MIDPOINT, POP])

# 2026-08-31: both row labels are set on THREE lines. At PT_TICK "evaluator-derived" measures
# 0.71 in and "at query time" 0.55 in, against a usable 0.52 in between the tick pad and panel a's
# right edge; on two lines each would have hung over into a. Breaking them costs no word, and
# "evaluator-" splits at a hyphen the term already carries.
ROWS = [("observable", "observable\nat query\ntime"),
        ("oracle_derived", "evaluator-\nderived\n(circular)")]
# 2026-07-26: the column labels used to spell out "28 label-determining cells (honest)". At the
# figure's print width one matrix cell is ~0.6 in across and that label was 0.58 in of text at
# 5.8 pt, so the two columns' labels ran into each other. The axis only has to distinguish the
# two units; naming them in full is caption debt, and as of 2026-08-31 the caption does not do it
# either, so "28 cells (honest)" and "672 instances (leaky)" are currently the only statement of
# the cross-validation units anywhere in the figure or its caption.
COLS = [("label_determining_cells", "28 cells\n(honest)"),
        ("instance_grid_id_LEAKY", "672 instances\n(leaky)")]


def draw_4f(ax):
    """Draw the 2x2 predictability matrix and the two within-arm leakage deltas.

    Every number drawn is computed from the source CSV at draw time; none is a literal.
    """
    if not os.path.exists(PRED):
        raise FileNotFoundError(
            f"{PRED} does not exist. Run the HIR-Bench predictability layer on the FULL grid. "
            f"This panel will not render a placeholder AUC.")
    d = pd.read_csv(PRED).set_index(["feature_set", "cv_grouping"])

    M = np.array([[float(d.loc[(r, c), "auc"]) for c, _ in COLS] for r, _ in ROWS])
    base = float(d["majority_baseline"].iloc[0])

    im = ax.imshow(M, cmap=CMAP, vmin=0.35, vmax=0.85, aspect="auto")
    # One matrix row is 0.875 in tall here, up from 0.73 in. The AUC sits above its row's centre
    # line and the delta pair below it; the offsets are data units, so they hold if the row
    # changes height again.
    for i in range(2):
        for j in range(2):
            ax.text(j, i - 0.17, f"{M[i, j]:.3f}", ha="center", va="center",
                    fontsize=PT_ANNOT, color=TEXT)
    # The in-cell verdicts ("moderately predictable" / "no better than chance") belong to the
    # caption: they are interpretation, not data, and this panel states no verdict. The caption
    # states the top row quantitatively (0.788 against a 0.643 majority rate) but stops at "do not
    # generalize beyond chance" for the bottom row, so the 0.400 drawn here is still unqualified
    # there. See the colour-bar block below for the rest of this panel's caption debt.

    # the interaction is the finding: leakage rescues the circular feature set five times harder
    for i in range(2):
        dlt = M[i, 1] - M[i, 0]
        ax.annotate("", xy=(0.80, i + 0.33), xytext=(0.20, i + 0.33),
                    arrowprops=dict(arrowstyle="-|>", lw=0.8, color=TEXT))
        ax.text(0.5, i + 0.18, f"{dlt:+.3f}", ha="center", va="center", fontsize=PT_SMALL,
                color=TEXT)

    ax.set_xticks([0, 1])
    ax.set_xticklabels([c[1] for c in COLS])
    ax.set_yticks([0, 1])
    ax.set_yticklabels([r[1] for r in ROWS])
    # No explicit labelsize on either axis: the tick size is fig4_assemble's rcParams value
    # (PT_TICK), so this panel cannot drift below the figure's floor on its own.
    # the "cross-validation unit" axis label is gone: the two column labels ARE the two units, and
    # the line it occupied is the clearance row 1 needs above the row-2 banner at this figure's
    # print size. Naming the axis ("two feature sets x two cross-validation units") is caption
    # debt; the Fig. 4 caption does not name it yet.
    ax.tick_params(length=0)
    for sp in ax.spines.values():
        sp.set_visible(False)

    cb = ax.figure.colorbar(im, ax=ax, fraction=0.050, pad=0.04)
    # 2026-08-31, MEASURED ACROSS THE GUTTER, not inside this panel, because the single-panel
    # harness renders b alone and cannot see this. make_axes pins the bar's RIGHT edge to this
    # panel's box edge at 4.100 in, so the apparatus grows rightward from there and neither `pad`
    # nor `fraction` moves it: shrinking either only widens the heat map. At PT_TICK the default
    # 3.5 pt tick pad put the rotated bar label at x 4.365 to 4.455 in, against panel c's rotated
    # y label over the same rows, leaving 0.013 in between the two sets of GLYPHS. 1.0 pt is the
    # only lever that moves the label left without closing the gap between the bar's own tick
    # labels and it (that stays at 0.056 in); it moves the label 0.035 in left, to an ink gap of
    # 0.048 in measured off a 600 dpi render.
    # The tight bboxes still nominally touch, because c's rotated label bbox carries font ascent
    # and descent padding either side of its ink. Do not read that as headroom. The b-to-c gutter
    # is 0.80 in wide; this apparatus occupies 0.320 in of it and c's y furniture 0.490 in, which
    # is 0.810 in of demand, so the gutter is oversubscribed in the RECTS/SLACK ledger and only
    # the bbox padding is absorbing it. b has no lever left worth pulling: the next one costs the
    # bar's own tick-label spacing. If c's y label grows again the fix is in the ledger or in c,
    # not in further squeezing here.
    cb.ax.tick_params(pad=1.0)
    cb.set_label("pooled out-of-fold AUC", fontsize=PT_SMALL)
    # No labelsize here either. The bar's axes is created with the current rcParams, so deleting
    # the explicit 5.8 pt is what lifts its tick labels to PT_TICK.
    # The rule on the colour bar marks the majority-class rate, computed from the same CSV. The
    # footnote that used to key it here was below the floor, so the key is caption debt. The
    # Fig. 4 caption AS IT STANDS gives "majority-class rate 0.643" but does not say the rule marks
    # it, and it carries NEITHER the 0.400 value now drawn in the bottom-left cell NOR the caveat
    # that makes 0.400 readable (effective n = 28 parameter cells, every held-out fold single-class,
    # so the 0.400-versus-0.5 gap is not itself interpretable). That caveat is load-bearing and is
    # still owed to the caption; do not treat this comment as evidence that it is already there.
    cb.ax.axhline(base, color=TEXT, lw=0.8)


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(3.2, 2.6))
    draw_4f(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "4f.png"), dpi=200, bbox_inches="tight")
    print("wrote 4f.png")
