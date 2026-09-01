"""Extended Data Fig. 7: the three conditions re-measured on unconstructed material.

SINCE 2026-08-30 these four panels are main-text Fig. 5k-n, drawn by fig5/fig5_assemble.py, where
they measure all three of Fig. 5a's requirements on 4,158,278 unconstructed cells. build() here
still assembles the standalone preview.

WHAT THIS FIGURE IS FOR
-----------------------
Every gate statistic in the main text rests on either cell-line mixtures we assembled or a
ten-patient glioblastoma dataset in which one patient supplies most of the pairs. This figure
recomputes the same three statistics on Tahoe-100M plate 3: a complete 50 cell line x 93 drug
grid, one dose per drug, DMSO_TF control in every line, median 648 cells per condition, with a
cell-cycle call on every cell. Nobody pipetted two populations together, so the within-line
heterogeneity is intrinsic cell state. It is not tissue, and it is not a construction of ours;
it is a third kind of material, and its role here is to supply sample size, not relevance.

GEOMETRY
--------
Authored at the printed width (6.90 in) so nominal size equals printed size and LaTeX does not
rescale. This is deliberately NOT the convention the other Extended Data figures use: ED1-ED4 are
authored at 10.2-12.6 in against a 6.93 in text block and therefore print at 2.75-3.53 pt, below
the Nature Portfolio 5 pt floor (see figures/edfigs/README.md). That deck needs a re-cut; this
figure does not inherit the defect.

PANELS
------
a  Gate 1. Distribution of the induced response cosine between the two subpopulations, over every
   condition that clears the cell-count rule, with the main text's four anchors marked. The point
   is where the constructed mixtures sit relative to unconstructed material.
b  Gate 2. Supervised ceiling against the best of the same four-method clusterer panel the main
   text reports, one point per drug pair, with the three main-text settings marked.
c  Gate 3. Per-context Spearman correlation, under two partitions, both computed on disjoint cell
   sets, against the tissue value computed the same way.
d  Gate 1 against Gate 3 within the cell-cycle partition, which is the test of whether the third
   condition is merely the first restated.

Run standalone: python ed7_tahoe.py
"""

from __future__ import annotations

import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "figures"))
from figstyle import FOCAL_SOFT, COMP_SOFT, GREY, INK, PURPLE_SOFT, apply_style, panel_letter, save, soften_axes, strip_titles  # noqa: E402
sys.path.insert(0, os.path.join(REPO, "figures", "fig5"))
from fig5_style import MATERIAL, PT_SMALL, PT_TICK  # noqa: E402

P = os.path.join(REPO, "results", "tahoe_pilot")
STEM = "ed7_tahoe"
FIG_W, FIG_H = 6.90, 2.45

# Panel rectangles in INCHES, (x0, y0, w, h), origin bottom-left.
#
# Vertical budget, and it is the binding one. Every title is two lines of 7 pt, which is
# 2 x 7 x 1.2 = 16.8 pt = 0.23 in, and the panel letter sits a further line above it. Every x
# label is two lines of 6.2 pt over its tick labels, which needs 0.46 in. A first version used
# FIG_H 2.05 with y0 0.52 and h 1.30, leaving 0.23 in above the axes for a two-line title plus a
# letter, and both ran off the canvas. The panels are now 1.20 in tall with 0.52 in below for the
# labels and 0.73 in above for title and letter.
# These are the rects fig5_assemble gives these four panels, copied here so the preview shows what
# the page prints rather than something narrower. Before 2026-09-01 the preview was 0.06 to 0.13 in
# wider per panel than the figure, which hid the label collisions that the figure actually had; at
# the 6.5 pt floor it was also 0.18 in short for panel d's rightmost x tick.
BOXES = {
    "a": (0.59, 0.52, 1.21, 1.10),
    "b": (2.43, 0.52, 1.11, 1.10),
    "c": (4.29, 0.52, 0.87, 1.10),
    "d": (5.91, 0.52, 0.93, 1.10),
}


def draw_a(ax):
    """Differential response: where the constructed mixtures sit in the unconstructed distribution."""
    g1 = pd.read_csv(os.path.join(P, "gate1_per_condition.csv"))
    c = g1.induced_cosine_G1_vs_G2M.dropna().to_numpy()
    ax.hist(c, bins=40, range=(-0.1, 1.0), color=FOCAL_SOFT, alpha=0.55, lw=0)
    top = ax.get_ylim()[1]
    ax.set_ylim(0, top * 1.02)
    ax.axvline(float(np.median(c)), color=FOCAL_SOFT, lw=1.1)
    # Anchor labels go INSIDE the panel and rotated, at staggered heights. Placed above the axis
    # as horizontal text they collided with each other (0.03 and 0.205 are 0.17 apart on an axis
    # 1.17 wide, i.e. 0.19 in, and each label was 0.30 in) and with the two-line title.
    # Colours follow fig5_style, which orange does not get to break: orange is the additive
    # limit, so it is on the ceiling at cosine 1 and NOT on the constructed-mixture anchor, which
    # is a material and takes MATERIAL slate. Before 2026-09-01 this panel had them the other way
    # round, so the same ceiling was orange in panel c and near-black here.
    # The constructed anchor keeps its emphasis through line weight rather than hue: it is this
    # panel's subject, and the point is how far left of everything else it sits.
    for x, lab, col, lw in [(0.014, "constructed mixtures", MATERIAL, 1.3),
                            (0.205, "real cells, state split", GREY, 0.8),
                            (0.566, "patient tissue", PURPLE_SOFT, 0.8),
                            (1.0, "additive ceiling", COMP_SOFT, 0.8)]:
        yf = 0.97
        ax.axvline(x, color=col, lw=lw, ls=(0, (2.2, 1.6)))
        ax.text(x - 0.022, top * yf, lab, ha="right", va="top", rotation=90,
                fontsize=PT_SMALL, color=INK)
    ax.text(float(np.median(c)) + 0.025, top * 0.97, f"median {np.median(c):.2f}",
            ha="left", va="top", rotation=90, fontsize=PT_SMALL, color=INK)
    ax.set_xlim(-0.12, 1.06)
    ax.set_xlabel("induced response cosine\nbetween subpopulations", fontsize=PT_SMALL, labelpad=1.5)
    ax.set_ylabel(f"conditions (n = {len(c):,})", fontsize=PT_SMALL)
    ax.tick_params(labelsize=PT_TICK)


def draw_b(ax):
    """Recoverability: the information is there and off-the-shelf clustering does not reach it."""
    g2 = pd.read_csv(os.path.join(P, "g2panel", "gate2_clusterer_panel.csv"))
    ax.scatter(g2.best_unsupervised, g2.supervised_ceiling, s=2.0, color=FOCAL_SOFT,
               alpha=0.28, lw=0, zorder=2)
    ax.plot([0.45, 1.0], [0.45, 1.0], ls=(0, (2.2, 1.6)), lw=0.8, color=GREY, zorder=1)
    ax.text(0.985, 0.965, "no gap", fontsize=PT_SMALL, color=GREY, ha="right", va="top", rotation=41)
    # A KEY IN THE EMPTY TRIANGLE, 2026-09-01, replacing four hand-staggered in-place labels.
    # The old layout offset each label in DATA units, which is a fixed fraction of the axes, while
    # the text is a fixed size in inches. At the Extended Data width that balance held; at this
    # figure's 1.11 in it does not, and the labels collided exactly as the old comment predicted
    # they would: "constructed, drug vs drug" ran 0.167 in off the right edge and through
    # "Tahoe median gap 0.157", and "constructed, pooled" ran off the left.
    #
    # No point can fall below the diagonal, because the supervised ceiling upper-bounds the
    # unsupervised method it is computed against, so the lower-right triangle is empty BY
    # CONSTRUCTION rather than by luck. That is where the key goes. The labels are short because
    # the caption defines the three settings; the panel only has to let a reader tell them apart.
    med = (g2.best_unsupervised.median(), g2.supervised_ceiling.median())
    KEY = [(0.674, 0.692, "pooled", MATERIAL, "D", 3.4),
           (0.837, 0.879, "drug pair", MATERIAL, "D", 3.4),
           (0.777, 0.923, "tissue", PURPLE_SOFT, "D", 3.4),
           (med[0], med[1], f"median gap {g2.gap_vs_best.median():.3f}", FOCAL_SOFT, "o", 4.6)]
    for x, y, lab, col, mk, ms in KEY:
        ax.plot([x], [y], mk, ms=ms, color=col, mec="white", mew=0.5 if mk == "D" else 0.7,
                zorder=4 if mk == "D" else 5)
    for row, (_, _, lab, col, mk, ms) in enumerate(reversed(KEY)):
        yk = 0.055 + row * 0.088
        ax.plot([0.965], [yk], mk, ms=ms, color=col, mec="white",
                mew=0.5 if mk == "D" else 0.7, transform=ax.transAxes, zorder=6, clip_on=False)
        ax.text(0.925, yk, lab, transform=ax.transAxes, fontsize=PT_SMALL, color=INK,
                ha="right", va="center", zorder=6)
    ax.set_xlim(0.45, 1.0); ax.set_ylim(0.45, 1.02)
    ax.set_xlabel("best unsupervised accuracy", fontsize=PT_SMALL, labelpad=1.5)
    ax.set_ylabel("supervised ceiling", fontsize=PT_SMALL)
    ax.tick_params(labelsize=PT_TICK)
    # Bottom-right, not bottom-left: no point can fall below the diagonal (the ceiling is never
    # beaten by an unsupervised method it upper-bounds), so that corner is empty by construction
    # while the bottom-left is dense.
    # Top left, not bottom right: the key now owns the empty triangle. The cloud's top-left
    # corner is the sparsest part of the occupied region, and n is grey so it recedes.
    ax.text(0.02, 0.985, f"n = {len(g2)} pairs\n{g2.cell_line.nunique()} lines",
            transform=ax.transAxes, fontsize=PT_SMALL, color=GREY, va="top", ha="left",
            linespacing=1.2)


def draw_c(ax):
    """State-ordering agreement: two partitions, both on disjoint cell sets, against the tissue value."""
    cc = pd.read_csv(os.path.join(P, "disjoint", "gate3_disjoint_cellcycle_G1_vs_G2M.csv"))
    st = pd.read_csv(os.path.join(P, "disjoint", "gate3_disjoint_controlstate_k2.csv"))
    rng = np.random.default_rng(0)
    for i, (d, lab, col) in enumerate([(cc, "cell cycle", FOCAL_SOFT), (st, "cell state", FOCAL_SOFT)]):
        y = d.spearman_rho.to_numpy()
        ax.scatter(np.full(len(y), i) + rng.uniform(-0.16, 0.16, len(y)), y,
                   s=5, color=col, alpha=0.55, lw=0, zorder=2)
        ax.plot([i - 0.30, i + 0.30], [np.median(y)] * 2, color=col, lw=1.4, zorder=3)
        ax.text(i, 1.035, f"{np.median(y):.3f}", ha="center", va="bottom",
                fontsize=PT_SMALL, color=INK)
    # ANNOTATIONS MOVED RIGHT, 2026-09-01. All three used to sit in a left gutter bought by
    # setting xlim to -0.85, which cost 30 per cent of the x range. That was affordable at the
    # Extended Data width; at this figure's 0.87 in of axes the gutter is 0.26 in wide, and
    # "tissue 0.835" ran straight through the cell-cycle points and its median bar, "0.5" sat on
    # its own dotted line, and the count block landed on the 0.4 and 0.2 tick labels.
    #
    # The right side is genuinely empty: both columns jitter within 0.16 of their tick, so
    # everything right of x = 1.2 is free at every height. The two reference lines are now
    # labelled at their right ends, where a line label belongs anyway.
    ax.axhline(0.835, color=PURPLE_SOFT, lw=0.8, ls=(0, (2.2, 1.6)), zorder=1)
    ax.text(1.54, 0.845, "tissue 0.835", fontsize=PT_SMALL, color=INK, ha="right", va="bottom")
    ax.axhline(0.5, color=GREY, lw=0.7, ls=":", zorder=1)
    ax.text(1.54, 0.512, "0.5", fontsize=PT_SMALL, color=GREY, ha="right", va="bottom")
    ax.set_xticks([0, 1]); ax.set_xticklabels(["cell\ncycle", "cell\nstate"], fontsize=PT_TICK)
    # -0.5 rather than -0.85: the left gutter held annotations that now sit on the right.
    ax.set_xlim(-0.5, 1.55); ax.set_ylim(0.15, 1.13)
    ax.set_ylabel("Spearman, majority\nranks minority", fontsize=PT_SMALL)
    ax.tick_params(axis="y", labelsize=PT_TICK)


def draw_d(ax):
    """Is the third condition merely the first restated? Same partition, so the answer means something."""
    g1 = pd.read_csv(os.path.join(P, "gate1_per_condition.csv"))
    cc = pd.read_csv(os.path.join(P, "disjoint", "gate3_disjoint_cellcycle_G1_vs_G2M.csv"))
    med = g1.groupby("cell_line").induced_cosine_G1_vs_G2M.median().rename("g1")
    j = cc.set_index("cell_line").join(med, how="inner").dropna(subset=["g1", "spearman_rho"])
    r, _ = spearmanr(j.g1, j.spearman_rho)
    ax.scatter(j.g1, j.spearman_rho, s=9, color=FOCAL_SOFT, alpha=0.7, lw=0)
    b = np.polyfit(j.g1, j.spearman_rho, 1)
    xs = np.linspace(j.g1.min(), j.g1.max(), 20)
    ax.plot(xs, np.polyval(b, xs), color=GREY, lw=0.9, ls=(0, (2.2, 1.6)))
    ax.set_xlabel("differential response\ninduced cosine (per line)", fontsize=PT_SMALL, labelpad=1.5)
    ax.set_ylabel("state-ordering\nSpearman (per line)", fontsize=PT_SMALL)
    ax.tick_params(labelsize=PT_TICK)
    # R^2 REMOVED 2026-09-01. The panel printed "$R^2$ = 0.38", which was r ** 2 where r is
    # SPEARMAN's rho. Two things were wrong with it. It is rho squared by construction, so it
    # carried no information the line above it did not. And it sat beside a least-squares line
    # whose actual R^2 is Pearson's, 0.606, not 0.385: a reader reads R^2 as the variance the
    # DRAWN line explains, and the printed value understated it by 0.22. Rho is the right
    # statistic for a monotone-association claim and it stays; the dashed line is a visual trend
    # guide, not the model rho describes.
    #
    # Removing it also resolves a type conflict. "$R^2$" is mathtext with a superscript, which
    # matplotlib renders at 0.7x nominal, so meeting the 6.5 pt floor needs PT_EQ 9.3 nominal,
    # which is above this figure's 7.2 pt cap on panel text and would have set the base R half
    # again as large as the text beside it. "$\rho$" carries no superscript and needs neither.
    ax.text(0.04, 0.96, f"$\\rho$ = {r:+.2f}\nn = {len(j)} lines",
            transform=ax.transAxes, fontsize=PT_SMALL, color=INK, va="top",
            linespacing=1.3)
    # The interpretive sentence that used to sit here overlapped the leftmost point and the
    # caption states it anyway; the rho and R2 above carry the panel.


TITLES = {"a": "Differential response:\nthe mixtures are the outlier",
          "b": "Recoverability: present,\nand out of reach",
          "c": "State-ordering agreement:\nmostly high, not always",
          "d": "Ordering agreement is not\ndifferential response restated"}


def build(apply_style_fn, panel_letter_fn):
    apply_style_fn(sizes=(7, 6.2, 5.6))
    fig = plt.figure(figsize=(FIG_W, FIG_H))
    fns = {"a": draw_a, "b": draw_b, "c": draw_c, "d": draw_d}
    for k, (x0, y0, w, h) in BOXES.items():
        ax = fig.add_axes([x0 / FIG_W, y0 / FIG_H, w / FIG_W, h / FIG_H])
        fns[k](ax)
        # No set_title. build() ends in strip_titles, so a title set here was removed again
        # before export and never reached the page; TITLES below stays as documentation of what
        # the four caption entries say, which is where those claims belong.
        panel_letter_fn(ax, k, case="lower", dx=-0.40 / w, dy=1.20)
    # See ed6.py: the caption carries four per-panel entries, so the drawn titles go and TITLES
    # stays as the declaration each panel is checked against.
    return strip_titles(soften_axes(fig))


if __name__ == "__main__":
    f = build(apply_style, panel_letter)
    save(f, os.path.join(HERE, STEM))
    print(f"wrote {STEM}.{{pdf,svg,png}}")
