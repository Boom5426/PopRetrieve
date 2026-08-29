"""PopRetrieve Figure 5 panel 5d: multi-dimensional structure diagnostics, predicted relative to real.
Source data: results/exp09_structure_diagnostics/exp09_structure_diagnostics_summary.csv
Run standalone: python fig5d.py

Redrawn 2026-07-26, presentation only: same three diagnostics, same three predictors, same
nine numbers, same denominator (the real alpha-blended candidate under synth='real').

WHY THE HEATMAP WENT. A 3x3 grid of printed numbers plus a colour bar spent a quarter of the
figure's top row on nine values whose message is ordinal, "is this ratio near 1 or not", and
it made the reader decode a diverging colour map to find out. A ratio axis with the reference
at 1 shows the same nine values, shows the magnitude of each departure directly, and needs
neither colour bar nor printed numbers. The axis is log-scaled because the quantity is a
ratio: 2x and 0.5x are the same size of departure and must look it.
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
from figstyle import FOCAL_SOFT, COMP_SOFT, GREY, INK  # noqa: E402
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

PREDS = [("average_effect", "avg-effect"),
         ("scgen", "linear-latent"),
         ("nearest_neighbor", "NN")]
REAL = "real_blend"          # the alpha-blended candidate a scorer actually ranks
SYNTH = "cells"              # the faithful synthesizer; 'gaussian' is the retracted legacy one

METS = [("subpop_variance_ratio_mean", "subpop variance ratio"),
        ("response_diversity_mean", "response diversity"),
        ("isotropy_index_mean", "isotropy")]


def draw_5d(ax):
    """predicted/real ratio per structure diagnostic, under the FAITHFUL synthesizer.

    A ratio near 1 means the predictor preserves that property of the real candidate
    population. Under the legacy 'gaussian' synthesizer every ratio collapsed toward 0, but
    that measured the synthesizer (an isotropic cloud), not the predictor. Rows are selected
    on synth='cells' and the panel fails loudly if those rows are absent.
    """
    sd = pd.read_csv(f"{REPO}/results/exp09_structure_diagnostics/"
                     f"exp09_structure_diagnostics_summary.csv")

    def row(pred, synth):
        sub = sd[(sd.predictor == pred) & (sd.synth == synth)]
        if sub.empty:
            raise KeyError(f"no row predictor={pred!r} synth={synth!r}; re-run "
                           f"exp09_structure_diagnostics.py --synth both")
        return sub.iloc[0]

    real = row(REAL, "real")
    M = np.array([[row(p, SYNTH)[col] / real[col] for col, _ in METS] for p, _ in PREDS])

    # One row per (metric, predictor), each carrying its own tick label. avg-effect and NN are
    # numerically almost identical here (0.14172987 vs 0.14172986 for the variance ratio), so a
    # shared-lane layout puts their markers and their labels on top of each other; giving every
    # value its own row is the only arrangement in which all nine can be read.
    rows, ylabs, headers = [], [], []
    y = 0.0
    for j, (_col, mlab) in enumerate(METS):
        y -= 1.0                                        # the group's header slot
        headers.append((y, mlab))
        for i, (_key, plab) in enumerate(PREDS):
            y -= 1.0
            rows.append((y, M[i, j]))
            ylabs.append(plab)
        y -= 0.45                                       # breathing room after the group

    # The reference line is drawn per group rather than as a full-height axvline, so it never
    # runs through a group header. No tolerance band is drawn: any "within x%" shading would be
    # a threshold this study never defines.
    for hy, _ in headers:
        ax.plot([1.0, 1.0], [hy - 0.5, hy - len(PREDS) - 0.5], ls="--", lw=1.0, color=INK,
                zorder=2)

    for (yy, v) in rows:
        ax.plot([1.0, v], [yy, yy], lw=1.0, color=FOCAL_SOFT, alpha=0.55, zorder=3)
        ax.plot([v], [yy], "o", ms=4.4, color=FOCAL_SOFT, mec="white", mew=0.5, zorder=4)

    ax.set_xscale("log")
    ax.set_xlim(0.60, 5.2)
    ax.set_xticks([0.7, 1, 2, 4])
    ax.set_xticklabels(["0.7", "1", "2", "4"], fontsize=5.8)
    ax.minorticks_off()
    # labelpad 1.5: at the default this label descended into panel f's title in the row below,
    # which the row-gap budget (0.46 in for a 0.36 in xlabel zone plus a 0.22-0.32 in title)
    # cannot absorb. Pulling the label up is cheaper than restacking the rows.
    ax.set_xlabel("predicted / real (log scale)", labelpad=1.5)
    ax.set_yticks([r[0] for r in rows])
    ax.set_yticklabels(ylabs, fontsize=5.6)
    # 0.40 of a row slot below the last marker and 0.60 above the first header. At the printed
    # panel height (1.62 in) the old y+0.10 / -0.15 pair left the bottom marker sitting on the
    # x axis spine, which read as a data point pinned to the axis rather than one row of nine.
    ax.set_ylim(y - 0.25, -0.50)
    for hy, mlab in headers:                            # metric names head their own group
        ax.text(0.615, hy, mlab, ha="left", va="center", fontsize=6, color=INK,
                fontweight="bold")
    for sp in ["right", "top", "left"]:
        ax.spines[sp].set_visible(False)
    ax.tick_params(axis="y", length=0, pad=1.5)


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(1.85, 1.62))   # the slot it occupies in fig5_assemble
    draw_5d(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "5d.png"), dpi=200, bbox_inches="tight")
    print("wrote 5d.png")
