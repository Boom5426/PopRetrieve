"""PopRetrieve Figure 4 panel 4f: is retrieval failure predictable, and from WHAT?

Source data: results/exp11_hir_benchmark/phase_grid_predictability_2x2.csv

A 2x2: {observable, oracle-derived} features x {28 label-determining cells, 672 instances}.
HIR-Bench is the only setting in this study with a specified latent utility oracle, and that is
what makes the circularity measurable rather than arguable: every feature can be labelled
oracle-derived or observable, and the size of the effect read off a dial.

Read across the top row: failure IS moderately predictable from what a retrieval method can
actually see at query time. Read across the bottom row: features derived from the benchmark's
own utility matrix are no better than chance, because they predict one function of the oracle
from another. Read down the columns: an instance-level holdout inflates the circular feature set
by +0.240 but the honest one by only +0.048. Pseudo-replication preferentially rescues features
that carry no generalizing signal, because memorizing near-duplicates is all such features can
do.

The label is a deterministic step function of (alpha, conflict), so the 13,440 instances contain
only 28 independent parameter cells; every held-out fold is single-class and no per-fold AUC
distribution exists. The 0.400-versus-0.5 gap is therefore NOT itself interpretable, and the
panel says so rather than letting the number travel alone.

Run standalone: python fig4f.py
"""
import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

# Palette comes from the house-style module; do NOT re-declare the hex values here. Every
# panel file used to carry its own copy, which made figstyle's "one edit here recolours the
# whole deck" untrue: a recolour meant editing 43 files and missing one was silent.
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
from figstyle import FOCAL_SOFT, COMP_SOFT, GREY, INK  # noqa: E402
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PRED = f"{REPO}/results/exp11_hir_benchmark/phase_grid_predictability_2x2.csv"

CMAP = LinearSegmentedColormap.from_list("auc", [COMP_SOFT, "#f7f7f7", FOCAL_SOFT])

ROWS = [("observable", "observable\nat query time"),
        ("oracle_derived", "evaluator-derived\n(circular)")]
# 2026-07-26: the column labels used to spell out "28 label-determining cells (honest)". At the
# figure's print width one matrix cell is ~0.5 in across and that label was 0.58 in of text, so the
# two columns' labels ran into each other. The caption names the two cross-validation units in
# full; the axis only has to distinguish them.
COLS = [("label_determining_cells", "28 cells\n(honest)"),
        ("instance_grid_id_LEAKY", "672 instances\n(leaky)")]


def draw_4f(ax):
    if not os.path.exists(PRED):
        raise FileNotFoundError(
            f"{PRED} does not exist. Run the HIR-Bench predictability layer on the FULL grid. "
            f"This panel will not render a placeholder AUC.")
    d = pd.read_csv(PRED).set_index(["feature_set", "cv_grouping"])

    M = np.array([[float(d.loc[(r, c), "auc"]) for c, _ in COLS] for r, _ in ROWS])
    base = float(d["majority_baseline"].iloc[0])

    im = ax.imshow(M, cmap=CMAP, vmin=0.35, vmax=0.85, aspect="auto")
    for i in range(2):
        for j in range(2):
            ax.text(j, i - 0.16, f"{M[i, j]:.3f}", ha="center", va="center",
                    fontsize=7.0, color=INK)
    # The in-cell verdicts ("moderately predictable" / "no better than chance") were 4.8 pt, i.e.
    # below Nature's 5 pt floor. They are interpretation, not data, and the caption already states
    # both quantitatively (0.788 vs a 0.643 majority rate; "no better than chance (0.400)").

    # the interaction is the finding: leakage rescues the circular feature set five times harder
    for i in range(2):
        dlt = M[i, 1] - M[i, 0]
        ax.annotate("", xy=(0.80, i + 0.36), xytext=(0.20, i + 0.36),
                    arrowprops=dict(arrowstyle="-|>", lw=0.8, color=INK))
        ax.text(0.5, i + 0.27, f"{dlt:+.3f}", ha="center", va="center", fontsize=6.0,
                color=INK)

    ax.set_xticks([0, 1])
    ax.set_xticklabels([c[1] for c in COLS], fontsize=5.8)
    ax.set_yticks([0, 1])
    ax.set_yticklabels([r[1] for r in ROWS], fontsize=5.8)
    # the "cross-validation unit" axis label is gone: the two column labels are the two units, the
    # caption names the axis ("two feature sets x two cross-validation units"), and the line it
    # occupied is the clearance row 1 needs above the row-2 banner at this figure's print size
    ax.tick_params(length=0)
    for sp in ax.spines.values():
        sp.set_visible(False)

    cb = ax.figure.colorbar(im, ax=ax, fraction=0.050, pad=0.04)
    # The rule on the bar is the majority-class rate. It used to be keyed only in the caption,
    # because the in-panel footnote that keyed it was below the 5 pt floor; folding it into the
    # colour-bar label keys it on the figure at a legal size and costs no extra space.
    # rotated, this label is as long as the colour bar is tall (1.02 in at print size), so the
    # word "majority-class rate" is cut to "majority rate"; the caption gives it in full
    # The majority-class rate is in the caption; a colour-bar label names its quantity.
    cb.set_label("pooled out-of-fold AUC", fontsize=5.8)
    _ = base
    cb.ax.tick_params(labelsize=5.8)
    # the rule on the colour bar marks the majority-class rate; it is keyed in the caption, because
    # the 4.6 pt footnote that used to key it here was below Nature's 5 pt floor. The caveat it
    # carried (effective n = 28 parameter cells, single-class folds, so the 0.400-vs-0.5 gap is not
    # itself interpretable) is load-bearing and is stated verbatim in the Fig. 4 caption.
    cb.ax.axhline(base, color=INK, lw=0.8)


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(3.2, 2.6))
    draw_4f(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "4f.png"), dpi=200, bbox_inches="tight")
    print("wrote 4f.png")
