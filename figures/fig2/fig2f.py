"""EvalShift Figure 2 panel 2f: the metric family drawn as one variance-sensitivity axis.

Source data: none, this is the synthesis schematic. The ordering it draws is the manuscript's
own statement that "energy, coverage and mean retrieval are one axis of variance sensitivity
rather than competing method classes, and mean-signature retrieval is its zero-variance
endpoint". The axis is an ordering, not a measured scale, so it carries no ticks.

Three choices are deliberate:
  * energy, MMD and sliced-Wasserstein share ONE rung. Nothing in the manuscript orders them by
    variance sensitivity, so drawing them on separate rungs would assert a ranking we have not
    measured. Energy sits with coverage_{K=1} because they are equal (panel e).
  * the collapse into mean retrieval is labelled lambda -> 0 for every member. beta -> 0 does NOT
    return mean-signature retrieval, it returns the mean-aggregated coverage value (0.7125 in
    panel e), so beta is drawn as the within-coverage span instead of as a second collapse edge.
  * the axis carries no ticks, because it is an ordering and not a measured scale.

Run standalone: python fig2f.py  (writes 2f.png)
"""
import os, numpy as np, matplotlib.pyplot as plt
import sys; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FOCAL, COMP, GREY = "#5185C0", "#E99D4E", "#7A7A7A"
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

_XAX = 0.175          # the vertical family axis
_XLAB = 0.245         # left edge of the member labels
_XARR = 0.905         # the collapse arrow


def draw_2f(ax):
    """One vertical axis of variance sensitivity, mean retrieval at its zero end."""
    ax.axis("off"); ax.set_xlim(0, 1); ax.set_ylim(0, 1)

    ax.annotate("", xy=(_XAX, 0.925), xytext=(_XAX, 0.075),
                arrowprops=dict(arrowstyle="-|>", lw=0.8, color="0.55", mutation_scale=8))
    ax.text(0.055, 0.51, "increasing sensitivity to\nwithin-population structure",
            rotation=90, ha="center", va="center", fontsize=6, color="0.4",
            linespacing=1.3)

    members = [
        (0.135, COMP, "mean retrieval (CMap cosine)", "zero-variance endpoint"),
        (0.480, FOCAL, "energy $=$ coverage$_{K=1}$,\nMMD, sliced-Wasserstein", None),
        (0.815, FOCAL, r"coverage aggregate, $\beta$", "mean aggregation $\\to$ worst case"),
    ]
    for y, col, lab, sub in members:
        ax.scatter([_XAX], [y], s=26, color=col, zorder=4)
        ax.text(_XLAB, y + (0.038 if sub else 0.0), lab, ha="left",
                va="bottom" if sub else "center", fontsize=6.5, color=col,
                linespacing=1.45)
        if sub:
            ax.text(_XLAB, y - 0.038, sub, ha="left", va="top", fontsize=6, color="0.4")

    # the collapse: every distributional member returns mean retrieval at lambda -> 0.
    # drawn as a bracket so the arrow is visibly gathered FROM the distributional rungs
    # and delivered INTO the orange endpoint, rather than floating at the panel edge.
    ax.plot([_XARR, _XARR], [0.135, 0.815], lw=1.0, color=COMP, alpha=0.8, zorder=2)
    for y in (0.815, 0.480):
        ax.plot([0.845, _XARR], [y, y], lw=0.8, color=COMP, alpha=0.6, zorder=2)
    ax.annotate("", xy=(0.800, 0.135), xytext=(_XARR, 0.135),
                arrowprops=dict(arrowstyle="-|>", lw=1.0, color=COMP, alpha=0.8,
                                mutation_scale=9))
    ax.text(_XARR + 0.035, 0.475, r"$\lambda\to0$", rotation=90, ha="center",
            va="center", fontsize=6.5, color=COMP)

    # A claim, not a label. Every other title in this deck states something the panel shows;
    # "One variance-sensitivity axis" only named the y axis, which the axis label already does.
    # What the graphic actually draws is the orange bracket gathering both distributional rungs
    # into the zero-variance endpoint, which is the caption's "every limit collapses to the mean".
    ax.set_title(r"Every member collapses to the mean at $\lambda\to0$", loc="left")


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(2.4, 1.9))
    draw_2f(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "2f.png"), dpi=200, bbox_inches="tight")
    print("wrote 2f.png")
