"""PopRetrieve Figure 4 panel i: the three HIR-Bench sanity checks against their thresholds.

Source data: results/exp11_hir_benchmark/sanity_checks.csv
Run standalone: python ed6_panel_e.py

Every value, threshold and pass flag drawn here is read from that file at draw time. Nothing in
this module is a transcribed number, so a re-run of exp11_hir_benchmark moves the panel.

2026-08-31, THE 6.5 pt PASS AND THE 1.28 in BOX
-----------------------------------------------
This panel was the last of Figure 4's nine still carrying type below the figure's floor. Six
artists were under it, all at 5.8 pt, and all six are now on the fig4_style ladder:

  RAISED  the three "<value> PASS" labels          5.8 -> PT_ANNOT (7.2)
  RAISED  the three two-line category labels       5.8 -> PT_TICK  (6.8)

Nothing was lowered to make room. Two things were cut instead, and the caption carries them:

  CUT  the third category's second line, "distributional=mean", which at PT_TICK measured 0.80 in
       against the 0.88 in of gutter this panel has for its category labels, i.e. it would have
       been flush with panel h. The row now reads "pred-mean: / Hit@1 gap", which names the
       quantity the check actually computes (see exp11_hir_benchmark: the check is the absolute
       Hit@1 difference between energy and mean_cosine retrieval under the predicted-mean
       information condition). That distributional and mean-signature retrieval AGREE there is
       the conclusion, so it belongs in the caption rather than on the axis.
  CUT  the trailing zeros of the x tick labels, 0.00/0.50/1.00 -> 0/0.5/1. At the old width the
       "1.00" label was interior; at 1.28 in with the axis ending just past the track it hangs
       0.07 in past the axes into the 0.07 in this panel has to the canvas edge.

WHAT THE NARROWER, TALLER BOX FORCED
------------------------------------
The axes went from 1.48 x 1.46 in to 1.28 x 1.75 in, and both of the constants that placed the
value labels had been measured against the old box in DATA units:

  * LAB_W = 0.22, described as "the label's own width in data units at 5.8 pt", was wrong even
    then: "0.272 PASS" sets 0.394 in in Arial at that size, and the old box put 1.0423 in on a
    data unit, so the label spanned 0.378 data units, not 0.22. It never protected the labels it
    was meant to protect. It is gone. The label width is now MEASURED from the rendered text, so
    it stays correct at any size and any box.
  * xlim = 1.42 was head-room for those labels. On a box 0.20 in narrower it left a third of the
    axes empty, which is a third of the length every bar could have been. The limit is now solved
    for: _solve_layout finds the smallest axis that holds the track, the marks, the labels and a
    printed pad, with the label width converted through the axes' own width in inches. It lands at
    1.0159, which puts 1.2600 in on a data unit against the old box's 1.0423 in: every bar is 21
    per cent longer IN PRINT. (It is 40 per cent longer as a fraction of the axis, which is not
    the same thing and is not what a reader sees, because the axis itself lost 0.20 in.)

ax_w_in is read from ax.get_position() when draw_ed6d runs, so the caller must not resize the axes
afterwards. fig4_assemble does not: it places panel i with add_axes at a fixed rect. ed6.py, which
still draws this function as its panel d, calls subplots_adjust AFTER drawing, taking that axes
from 2.431 to 2.210 in; there the track is what binds the limit and the labels end an inch inside
the axes, so nothing overflows, but the solved limit is 9 per cent off the box it printed on.

The label anchor rule itself is unchanged in intent: sit just past the bar, and past the threshold
mark only when that mark would otherwise fall inside the label. Anchored to the bar alone the label
printed on top of the mark for the two checks whose threshold sits just beyond a short bar;
anchored to max(bar, threshold) unconditionally it flew to x = 1.03 on the boundary-margin row,
most of the axis away from the bar it belongs to.

The threshold mark stays in TEXT ink rather than SHARED grey: the x-axis label draws a "|" as its
key, and a key set in a different colour from the thing it stands for is a legibility bug. It is
a reference mark in the axis' own ink, not one of the four data hues.

No title. The panel states no conclusion; TITLES["i"] in fig4_assemble holds the claim and the
caption is what a reader sees.
"""
import os
import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(_HERE))
sys.path.insert(0, os.path.join(os.path.dirname(_HERE), "fig4"))
# Palette and type ladder come from the house-style modules; do NOT re-declare a hex or a point
# size here. Every panel file used to carry its own copy of the palette, which made figstyle's
# "one edit here recolours the whole deck" untrue: a recolour meant editing 43 files and missing
# one was silent. fig4_style is the same arrangement for Figure 4's type.
from fig4_style import BAR_TRACK, MEAN, POP, PT_ANNOT, PT_TICK, TEXT  # noqa: E402

REPO = os.path.abspath(os.path.join(_HERE, "..", ".."))
H = os.path.join(REPO, "results", "exp11_hir_benchmark")

# Every check is scored on the same 0-1 scale, so the track states it once and each bar reads as a
# fraction of it. Without the track the three bars were three unrelated lengths against a distant
# axis, and the threshold marks had nothing to sit against.
TRACK_MAX = 1.0
BAR_H = 0.5
GAP_IN = 0.045          # printed gap from a bar end, or a threshold mark, to the label that follows
PAD_IN = 0.020          # printed room past the longest label before the axis ends
LABS = {
    "no_conflict_flip_rate": "no-conflict\nflip rate",
    "median_boundary_margin": "median\nboundary margin",
    # "distributional=mean" is the conclusion and lives in the caption; this names the quantity.
    "predicted_mean_dart_eq_mean": "pred-mean:\nHit@1 gap",
}


def _text_width_in(ax, s, pt):
    """Width of ``s`` at ``pt``, in inches, as the renderer will actually set it."""
    fig = ax.figure
    if not hasattr(fig.canvas, "get_renderer"):
        raise RuntimeError(
            "this panel measures its own labels and needs a renderer; draw it on an Agg-backed "
            f"canvas rather than {type(fig.canvas).__name__}")
    t = fig.text(0, 0, s, fontsize=pt)
    width = t.get_window_extent(renderer=fig.canvas.get_renderer()).width / fig.dpi
    t.remove()
    return width


def _solve_layout(sc, lab_w_in, ax_w_in):
    """Solve the x limit and the three label anchors together.

    The anchors are in data units and the label is a fixed width in INCHES, so each depends on the
    other through the axis limit. One is not derivable from the other in closed form once the
    "past the threshold mark as well" branch is in play, so this iterates on ``u``, the data units
    per printed inch, and asserts that it settled rather than assuming it did.
    """
    thr_max = float(sc["threshold"].max())
    u = TRACK_MAX / ax_w_in                     # seed: an axis that ends exactly at the track
    for _ in range(64):
        xs = []
        for _, row in sc.iterrows():
            x = row["value"] + GAP_IN * u
            if x <= row["threshold"] <= x + lab_w_in * u:
                x = row["threshold"] + GAP_IN * u
            xs.append(x)
        # The thresholds are in this max in their own right. The branch above only widens the
        # axis for a mark that lands INSIDE a label; a mark further out than that, which a re-run
        # of exp11_hir_benchmark could produce, would otherwise be drawn past the axis and clipped
        # with no error, leaving a check on the panel with no threshold to read it against.
        xmax = max(TRACK_MAX, thr_max, max(x + lab_w_in * u for x in xs)) + PAD_IN * u
        if abs(xmax / ax_w_in - u) < 1e-9:
            return xs, xmax
        u = xmax / ax_w_in
    raise RuntimeError("sanity-check label placement did not converge; check GAP_IN / PAD_IN")


def draw_ed6d(ax):
    """The three benchmark sanity checks, each as a value against its threshold mark."""
    sc = pd.read_csv(f"{H}/sanity_checks.csv")
    ys = np.arange(len(sc))
    labels = [f"{row['value']:.3f} {'PASS' if row['pass'] == 1 else 'FAIL'}"
              for _, row in sc.iterrows()]
    ax_w_in = ax.get_position().width * ax.figure.get_figwidth()
    lab_w_in = max(_text_width_in(ax, s, PT_ANNOT) for s in labels)
    xs, xmax = _solve_layout(sc, lab_w_in, ax_w_in)

    for y, (_, row), x_lab, lab in zip(ys, sc.iterrows(), xs, labels):
        passed = row["pass"] == 1
        ax.barh(y, TRACK_MAX, color=BAR_TRACK, height=BAR_H, lw=0, zorder=1)
        ax.barh(y, row["value"], color=POP if passed else MEAN, height=BAR_H, zorder=2)
        ax.plot(row["threshold"], y, "|", ms=10, color=TEXT, mew=1.0, zorder=3)
        # PASS/FAIL is already a word, so it does not also need a hue; the bar beside it is the
        # coloured mark. A failing check would be the exception worth weighting, and there is none
        # in this table, so weight is left alone rather than being spent on the pass case.
        ax.text(x_lab, y, lab, va="center", fontsize=PT_ANNOT, color=TEXT, zorder=4)

    ax.set_yticks(ys)
    ax.set_yticklabels([LABS.get(c, c) for c in sc["check"]], fontsize=PT_TICK)
    ax.set_xlabel("value (| = threshold)")
    ax.set_xlim(0, xmax)
    ticks = [0.0, 0.25, 0.5, 0.75, 1.0]
    ax.set_xticks(ticks)
    ax.set_xticklabels([f"{t:g}" for t in ticks], fontsize=PT_TICK)
    ax.spines["bottom"].set_bounds(0, TRACK_MAX)   # the axis is the track
    for sp in ("right", "top"):
        ax.spines[sp].set_visible(False)


if __name__ == "__main__":
    # The same ladder the composite sets, so a standalone preview is legible at the size it prints.
    sys.path.insert(0, os.path.dirname(_HERE))
    from figstyle import apply_style, soften_axes
    from fig4_style import PT_TITLE

    apply_style(sizes=(PT_TITLE, PT_ANNOT, PT_TICK))
    fig = plt.figure(figsize=(6.9, 7.97))
    ax = fig.add_axes([5.55 / 6.9, 0.63 / 7.97, 1.28 / 6.9, 1.75 / 7.97])   # fig4_assemble RECTS
    draw_ed6d(ax)
    soften_axes(fig)
    fig.savefig(os.path.join(_HERE, "ed6d.png"), dpi=300, bbox_inches="tight")
    print("wrote ed6d.png")
