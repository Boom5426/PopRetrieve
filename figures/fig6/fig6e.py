"""DART Figure 6 panel 6e: Gate 2. Is the structure UNRECOVERABLE, or merely unclustered?

Source data: results/upgrade/gate2_supervised_upper_bound.csv (real separation, s = 1.0)

WHAT CHANGED, AND WHY IT MATTERS
--------------------------------
This panel used to show nine columns of adjusted Rand index, all near 0.1, and conclude that
subpopulations "cannot be reliably identified". Two things were wrong with that.

  1. Every method tested was centroid- or Gaussian-based (k-means, GMM, PCA variants). The
     obvious objection, that graph-based (Leiden) and density-based (HDBSCAN) clustering are
     the field's actual defaults and were never run, was left open. They are run here.

  2. There was NO SUPERVISED UPPER BOUND, so the result could not distinguish
       (a) the information is absent from the representation, from
       (b) the information is present and unsupervised methods cannot find it.
     These have opposite implications: (a) is an information ceiling no method can beat,
     (b) is a solvable engineering problem. Concluding (a) from clustering failure alone is
     the same species of error this paper criticizes elsewhere.

Every method is now scored in the SAME unit, best-permutation accuracy against the true
labels, with the label matching given to each clusterer for free (an over-partitioning method
is never penalised for splitting a true class). The supervised ceiling is a classifier handed
the ground-truth partition, with the representation fit INSIDE the training fold so nothing
leaks; the unsupervised methods get the easier transductive representation, which biases the
comparison against the conclusion drawn.

THE ANSWER: ceiling 0.692, best unsupervised 0.674, gap 0.018. Unsupervised clustering already
extracts essentially everything this representation contains about this partition, so WITHIN THIS
CONSTRUCTED MIXTURE the limit is informational rather than algorithmic. Nonlinear learners (forest
0.669, kNN 0.605) do not beat the linear probe (0.685), so it is not a hidden nonlinear boundary.

THAT QUALIFIER IS EVERYTHING, AND WE ONLY FOUND OUT LATER. This HDAC-versus-JAK mixture is one WE
BUILT. Run the identical protocol on patient glioblastoma (analysis/natural/zhao_two_gates.py) and
the ceiling is 0.964 with off-the-shelf Leiden at 0.949. Real subpopulations are NOT hard to tell
apart; the ones we constructed were. The general claim once drawn from this panel, that
identifiability is an information limit, is WITHDRAWN. See main-text Fig. 5c and CORRECTIONS.md R18.

Run standalone: python fig6e.py
"""
import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

FOCAL, COMP, GREY, INK = "#5185C0", "#E99D4E", "#7A7A7A", "#1A1A1A"
GREEN = "#55966B"
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC = f"{REPO}/results/upgrade/gate2_supervised_upper_bound.csv"

# Tick labels are data labels and cannot move to the caption, so they must be legible (>= 5.5 pt).
# "(true $k$ given)" is dropped from the k-means / GMM ticks to make room; that concession is
# stated in the Fig. 6e caption ("both handed the true $k$"), so no information is lost.
UNSUP = [("acc_kmeans_k2", "$k$-means"),
         ("acc_gmm_k2",    "Gaussian\nmixture"),
         ("acc_leiden",    "Leiden\n(graph)"),
         ("acc_hdbscan",   "HDBSCAN\n(density)")]
SUP = [("probe_knn_acc",    "kNN"),
       ("probe_forest_acc", "random\nforest"),
       ("probe_linear_acc", "logistic")]


def draw_6e(ax):
    if not os.path.exists(SRC):
        raise FileNotFoundError(
            f"{SRC} does not exist. Run analysis/identifiability/gate2_supervised_upper_bound.py. "
            f"This panel will not render a placeholder ceiling.")
    d = pd.read_csv(SRC)
    d = d[d.separation_scale == 1.0]                       # the real-data regime
    if d.empty:
        raise ValueError("no rows at separation_scale == 1.0 (the real-data regime).")

    ceiling = float(d.probe_acc.median())
    best_unsup = max(float(d[c].median()) for c, _ in UNSUP)

    xs = np.arange(len(UNSUP) + len(SUP))
    vals = [float(d[c].median()) for c, _ in UNSUP] + [float(d[c].median()) for c, _ in SUP]
    labs = [l for _, l in UNSUP] + [l for _, l in SUP]
    cols = [FOCAL] * len(UNSUP) + [GREEN] * len(SUP)

    ax.bar(xs, vals, width=0.66, color=cols, alpha=0.85, zorder=3)
    for x, v in zip(xs, vals):
        ax.text(x, v + 0.006, f"{v:.3f}", ha="center", va="bottom", fontsize=5.0,
                fontweight="bold", color=INK)

    ax.axhline(0.5, ls="--", lw=0.9, color=GREY, zorder=2)
    ax.text(len(xs) - 0.45, 0.503, "chance", ha="right", va="bottom", fontsize=5.0, color=GREY)
    ax.axhline(ceiling, ls="-", lw=1.1, color=INK, zorder=2)
    ax.text(-0.45, ceiling + 0.004, f"supervised ceiling {ceiling:.3f}", ha="left", va="bottom",
            fontsize=5.2, fontweight="bold", color=INK)

    # the gap IS the finding. Draw it in the gutter between the two groups, not over a bar.
    gx = len(UNSUP) - 0.5
    ax.annotate("", xy=(gx, ceiling), xytext=(gx, best_unsup),
                arrowprops=dict(arrowstyle="<->", lw=1.0, color=COMP), zorder=6)
    ax.text(gx + 0.12, (ceiling + best_unsup) / 2,
            f"gap {ceiling - best_unsup:+.3f}:\nclustering is\nalready at\nthe ceiling",
            ha="left", va="center", fontsize=5.0, color=COMP, fontweight="bold", zorder=6,
            bbox=dict(fc="white", ec="none", alpha=0.85, pad=0.8))

    ax.set_xticks(xs)
    ax.set_xticklabels(labs, fontsize=5.5)
    ax.set_ylabel("accuracy recovering the true partition", fontsize=6)
    ax.set_ylim(0.44, 0.75)
    ax.tick_params(axis="y", labelsize=5.6)
    for sp in ("right", "top"):
        ax.spines[sp].set_visible(False)

    for x0, txt, col in [(1.5, "unsupervised", FOCAL),
                         (5.0, "supervised (given the labels)", GREEN)]:
        ax.text(x0, 0.4525, txt, ha="center", va="bottom", fontsize=5.3, color=col,
                fontweight="bold", zorder=6,
                bbox=dict(fc="white", ec="none", alpha=0.9, pad=1.0))
    # The methods footnote that used to sit here (at 4.5 pt, illegible in print) has been moved
    # to the Fig. 6e caption. It is load-bearing (it is the leakage control), so it must NOT be
    # dropped: "All methods are scored in one unit, and clusterers are given best-permutation
    # label matching for free; every supervised bar, not only the ceiling, fits its
    # representation inside the training fold, so no test information leaks into any of them."


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(4.3, 3.0))
    draw_6e(ax)
    ax.set_title("The information is not there to be found", loc="left", fontsize=8)
    fig.savefig(os.path.join(os.path.dirname(__file__), "6e.png"), dpi=200, bbox_inches="tight")
    print("wrote 6e.png")
