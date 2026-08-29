"""Extended Data Fig. 7: the three conditions re-measured on unconstructed material.

SINCE 2026-08-29 these four panels are Extended Data Fig. 3e-h, drawn by
edfigs/ed_consolidated.py. build() here still assembles the standalone preview.

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
BOXES = {
    "a": (0.52, 0.52, 1.30, 1.20),
    "b": (2.28, 0.52, 1.24, 1.20),
    "c": (4.02, 0.52, 1.18, 1.20),
    "d": (5.72, 0.52, 1.06, 1.20),
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
    for x, lab, col, yf in [(0.014, "constructed mixtures", COMP_SOFT, 0.97),
                            (0.205, "real cells, state split", GREY, 0.97),
                            (0.566, "patient tissue", PURPLE_SOFT, 0.97),
                            (1.0, "additive ceiling", INK, 0.97)]:
        ax.axvline(x, color=col, lw=0.8, ls=(0, (2.2, 1.6)))
        ax.text(x - 0.022, top * yf, lab, ha="right", va="top", rotation=90,
                fontsize=5.0, color=INK)
    ax.text(float(np.median(c)) + 0.025, top * 0.97, f"median {np.median(c):.2f}",
            ha="left", va="top", rotation=90, fontsize=5.4, color=INK)
    ax.set_xlim(-0.12, 1.06)
    ax.set_xlabel("induced response cosine\nbetween subpopulations", fontsize=6.2, labelpad=1.5)
    ax.set_ylabel(f"conditions (n = {len(c):,})", fontsize=6.2)
    ax.tick_params(labelsize=5.6)


def draw_b(ax):
    """Recoverability: the information is there and off-the-shelf clustering does not reach it."""
    g2 = pd.read_csv(os.path.join(P, "g2panel", "gate2_clusterer_panel.csv"))
    ax.scatter(g2.best_unsupervised, g2.supervised_ceiling, s=2.0, color=FOCAL_SOFT,
               alpha=0.28, lw=0, zorder=2)
    ax.plot([0.45, 1.0], [0.45, 1.0], ls=(0, (2.2, 1.6)), lw=0.8, color=GREY, zorder=1)
    ax.text(0.985, 0.965, "no gap", fontsize=5.2, color=GREY, ha="right", va="top", rotation=41)
    # Staggered by hand: the three reference points sit within 0.16 of each other in x and
    # 0.23 in y, so a common label offset put "patient tissue" straight through
    # "constructed, drug vs drug". Each is pushed to the side with room.
    for x, y, lab, col, dx, dy, ha, va in [
            (0.674, 0.692, "constructed,\npooled", COMP_SOFT, -0.020, 0.0, "right", "center"),
            (0.837, 0.879, "constructed,\ndrug vs drug", COMP_SOFT, 0.018, -0.010, "left", "top"),
            (0.777, 0.923, "patient tissue", PURPLE_SOFT, -0.018, 0.010, "right", "bottom")]:
        ax.plot([x], [y], "D", ms=3.4, color=col, mec="white", mew=0.5, zorder=4)
        ax.text(x + dx, y + dy, lab, fontsize=5.2, color=INK, ha=ha, va=va,
                linespacing=1.15, zorder=4)
    med = (g2.best_unsupervised.median(), g2.supervised_ceiling.median())
    ax.plot([med[0]], [med[1]], "o", ms=4.6, color=FOCAL_SOFT, mec="white", mew=0.7, zorder=5)
    # Below and to the RIGHT of the median marker. Right-aligned above it, the two-line label is
    # 0.165 in data units wide against a left limit of 0.45, so its left edge fell outside the
    # axes and landed on the y tick labels; and its top line ran into "patient tissue".
    ax.text(med[0] + 0.016, med[1] - 0.012, f"Tahoe median\ngap {g2.gap_vs_best.median():.3f}",
            fontsize=5.3, color=INK, ha="left", va="top", linespacing=1.2, zorder=5)
    ax.set_xlim(0.45, 1.0); ax.set_ylim(0.45, 1.02)
    ax.set_xlabel("best unsupervised accuracy", fontsize=6.2, labelpad=1.5)
    ax.set_ylabel("supervised ceiling", fontsize=6.2)
    ax.tick_params(labelsize=5.6)
    # Bottom-right, not bottom-left: no point can fall below the diagonal (the ceiling is never
    # beaten by an unsupervised method it upper-bounds), so that corner is empty by construction
    # while the bottom-left is dense.
    ax.text(0.97, 0.03, f"n = {len(g2)} drug pairs\n{g2.cell_line.nunique()} cell lines",
            transform=ax.transAxes, fontsize=5.3, color=GREY, va="bottom", ha="right",
            linespacing=1.2)


def draw_c(ax):
    """State-ordering agreement: two partitions, both on disjoint cell sets, against the tissue value."""
    cc = pd.read_csv(os.path.join(P, "disjoint", "gate3_disjoint_cellcycle_G1_vs_G2M.csv"))
    st = pd.read_csv(os.path.join(P, "disjoint", "gate3_disjoint_controlstate_k2.csv"))
    rng = np.random.default_rng(0)
    for i, (d, lab, col) in enumerate([(cc, "cell cycle", FOCAL_SOFT), (st, "cell state", PURPLE_SOFT)]):
        y = d.spearman_rho.to_numpy()
        ax.scatter(np.full(len(y), i) + rng.uniform(-0.16, 0.16, len(y)), y,
                   s=5, color=col, alpha=0.55, lw=0, zorder=2)
        ax.plot([i - 0.30, i + 0.30], [np.median(y)] * 2, color=col, lw=1.4, zorder=3)
        ax.text(i, 1.035, f"{np.median(y):.3f}", ha="center", va="bottom",
                fontsize=5.8, color=INK)
    ax.axhline(0.835, color=PURPLE_SOFT, lw=0.8, ls=(0, (2.2, 1.6)), zorder=1)
    ax.text(-0.82, 0.848, "tissue 0.835", fontsize=5.2, color=INK, ha="left", va="bottom")
    ax.axhline(0.5, color=GREY, lw=0.7, ls=":", zorder=1)
    ax.text(-0.44, 0.5, "0.5", fontsize=5.2, color=GREY, ha="right", va="center")
    n_open = int((st.spearman_rho < 0.5).sum())
    # Annotation moved off the x axis region: at y 0.30 it sat on top of the "cell state" tick
    # label. It now points at the two outliers from the left, where the panel is empty.
    # No leader line: it has to reach two points at different heights, and either target left
    # the line ending in empty space. The two low points are unambiguous on their own.
    ax.text(-0.82, 0.27, f"{n_open} of {len(st)}\ncontexts\nbelow 0.5", fontsize=5.2, color=INK,
            ha="left", va="center", linespacing=1.25)
    ax.set_xticks([0, 1]); ax.set_xticklabels(["cell\ncycle", "cell\nstate"], fontsize=5.6)
    # Left margin widened from -0.5 to -0.85 purely to make room for the two left-hand
    # annotations. At -0.5 the tissue label ran from x -0.46 to about x 0.05 and crossed the
    # cell-cycle points, whose jitter starts at -0.16; the tissue line sits at 0.835 and the
    # cell-cycle median at 0.841, so there is no vertical room to separate them instead.
    ax.set_xlim(-0.85, 1.5); ax.set_ylim(0.15, 1.06)
    ax.set_ylabel("Spearman, majority response\nranks minority response", fontsize=6.2)
    ax.tick_params(axis="y", labelsize=5.6)


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
    ax.set_xlabel("differential response\ninduced cosine (per line)", fontsize=6.2, labelpad=1.5)
    ax.set_ylabel("state-ordering\nSpearman (per line)", fontsize=6.2)
    ax.tick_params(labelsize=5.6)
    ax.text(0.04, 0.96, f"$\\rho$ = {r:+.2f}\n$R^2$ = {r ** 2:.2f}\nn = {len(j)} lines",
            transform=ax.transAxes, fontsize=5.5, color=INK, va="top", linespacing=1.3)
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
        ax.set_title(TITLES[k], loc="left", fontsize=7)
        panel_letter_fn(ax, k, case="lower", dx=-0.40 / w, dy=1.20)
    # See ed6.py: the caption carries four per-panel entries, so the drawn titles go and TITLES
    # stays as the declaration each panel is checked against.
    return strip_titles(soften_axes(fig))


if __name__ == "__main__":
    f = build(apply_style, panel_letter)
    save(f, os.path.join(HERE, STEM))
    print(f"wrote {STEM}.{{pdf,svg,png}}")
