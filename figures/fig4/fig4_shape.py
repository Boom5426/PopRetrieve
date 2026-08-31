"""Figure 4 panel c: the oracle's SHAPE picks the winner.

Source: results/upgrade/oracle_shape_test.json (analysis/class_c/oracle_shape_test.py)

THE PANEL IN ONE SENTENCE
------------------------
Same 218,331 cells, same 20 surface proteins, same two RNA rankings, byte-identical across the two
columns; the only thing that changes is whether the protein oracle is computed as a MEAN (cosine of
mean protein deltas) or as a DISTRIBUTION (energy distance between protein-response cell clouds).
The winner swaps.

This is the sharpest result in the paper because no scorer can see either oracle. Class-A
circularity is a method grading its own objective; this is something else and worse: two EXTERNAL,
independent, blind criteria, built from the same measurements, handing victory to opposite methods
purely because of their own statistical form.

The magnitude scalar is drawn as a third bar and it is not decoration. Both distributional objects
here are energy distances, and an energy distance tracks a candidate's own response magnitude
(rho = +0.791), so a magnitude-to-magnitude channel could have produced the swap with no
distribution ever compared. It does not, quite: the scalar climbs steeply under the distributional
oracle (+0.125 -> +0.352, the confound behaving exactly as predicted), but energy still leads it by
+0.177 there against +0.022 under the mean-shaped oracle. Dropping the scalar would leave the
reader unable to see either fact.

TYPOGRAPHY, 2026-08-31: RAISED TO THIS FIGURE'S 6.5 pt FLOOR
------------------------------------------------------------
This panel held 19 text artists under the floor, the joint worst in Figure 4: the six bar value
labels at 5.6 pt, the three legend entries and the two "wins" words at 5.8 pt, the five y tick
labels at 6.0, and the two x tick labels and the y-axis label at 6.2. Nothing here is set below
PT_TICK now, and only the tick labels are that small: every piece of text the panel draws itself
is at PT_ANNOT, which is both this figure's ordinary annotation size and its cap. Sizes are
imported from fig4_style; no point size is typed in this file.

WHAT PAID FOR THE LARGER TYPE
  * The legend box is deleted. Figures 1 to 3 contain no legend at all, and this one sat inside
    the axes over the upper left bars. The three series are named on their own bars instead, each
    once, in the column where that series flies no winner flag and where its own bar is shorter:
    "energy" and "magnitude scalar" over the mean-oracle column, "mean cosine" over the
    distributional one.
  * The six value labels are set ROTATED. At PT_ANNOT "+0.529" prints 21.5 pt long while
    neighbouring bar centres are 17.2 pt apart, so horizontal value labels cannot clear each other
    at any size at or above the floor in a 1.93 in axes carrying six bars. Turned on their side
    each label is 6.7 pt of printed width and clears its neighbour by 10.5 pt.
  * The annotation stack above each bar is measured rather than guessed: _len_pt() reads the
    printed length of each string from the font metrics, so the value label, the winner triangle
    and the word above it are placed by what they actually measure. _assert_fits then refuses to
    draw a stack that would leave the axes.

WHAT WAS CUT, AND WHERE THE CAPTION MUST TAKE IT
  * The three parenthetical glosses that were legend text: "energy (distributional)",
    "mean cosine (incumbent)", "magnitude scalar (control)". The bars are now named "energy",
    "mean cosine" and "magnitude scalar", so the caption entry for c has to say that energy is the
    energy distance between protein-response cell clouds, that mean cosine is the pre-specified
    incumbent, and that the magnitude scalar is the CONTROL that compares no distributions at all,
    drawn open for that reason.
  * The open-versus-filled encoding is no longer named on the panel, because the legend named it.
    The caption states it: filled = a score that compares a response representation, open = the
    scalar control.

NEW BOX, 2026-08-31: 1.93 x 1.75 in, from 2.07 x 1.46
  The axes is 0.14 in narrower and 0.29 in taller, so the constants measured against the old box
  were re-derived rather than nudged. The y limit is no longer 0.76: it is YMAX, chosen so the
  tallest annotation stack (the distributional column's energy bar, which carries a value label, a
  winner triangle and a word) clears the top of the axes, and _assert_fits checks that for all six
  bars at the resolved axes height. The left spine is bounded to YTICKS[-1], the range the data
  occupy, so the quarter of the axis that exists only to hold annotation does not advertise itself
  as scale. The x tick labels were re-broken. The pitch between the two group centres is 0.92 in.
  At PT_TICK the old break puts "evaluator built as a" on one line, 0.79 in, which clears its
  neighbour by only 0.13 in; the break now falls after "built", whose longest line is the 0.66 in
  of "as a distribution" and which clears by 0.26 in. Both breaks fit; this one fits with the
  margin the larger type needs.

COLOUR is fig4_style's, imported: POP blue for the distributional score, MEAN orange for the
mean-signature incumbent, SHARED grey for the magnitude scalar, which is neither arm. The panel no
longer declares a hex value of its own (it carried an unused private GREEN_SOFT).
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.textpath import TextPath

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fig4_style import MEAN, POP, PT_ANNOT, PT_TICK, REPO, SHARED, TEXT  # noqa: E402

SRC = f"{REPO}/results/upgrade/oracle_shape_test.json"

# The three series. Each carries the column index in which its NAME is drawn: a series is named
# once, on the bar that has room for it, which is the column where it flies no winner flag and
# where its own bar is shorter. Grey is SHARED because the scalar is neither arm of the comparison.
ROWS = [("energy", "energy", POP, 0),
        ("mean", "mean cosine", MEAN, 1),
        ("magmatch", "magnitude scalar", SHARED, 0)]
# The two columns: the JSON suffix that selects the oracle, the stem of its winner field, and the
# tick label. Broken across two lines at PT_TICK; on one line the second label is 1.27 in against a
# 0.92 in pitch between the two group centres, i.e. it would run into its neighbour.
COLS = [("MEAN", "mean", "evaluator built\nas a mean"),
        ("DIST", "dist", "evaluator built\nas a distribution")]

BAR_W = 0.26                 # bar width in x units; adjacent bar centres are one BAR_W apart
YMAX = 0.85                  # top of the axes. Set by the tallest annotation stack, not by the data
YTICKS = (0.0, 0.2, 0.4, 0.6)
GAP_BAR_PT = 2.5             # bar top -> the foot of its rotated value label
GAP_NAME_PT = 6.5            # value label -> the series name, wide enough that the two do not read
                             # as one string ("+0.146 energy" is a value and a name, not a quantity)
GAP_STACK_PT = 4.0           # between the winner triangle and what sits either side of it
MS_WIN = 4.0                 # winner triangle, in points


def _len_pt(s: str, size: float) -> float:
    """Printed length of ``s`` in points, from the font metrics of the house face.

    Read from a TextPath rather than from a renderer so the placement is the same under every
    backend the deck exports through, and so it is computed rather than a constant that would
    silently stop being true when the type ladder moved.
    """
    return TextPath((0, 0), s, size=size, prop=FontProperties(size=size)).get_extents().width


def _height_pt(s: str, size: float) -> float:
    """Printed height of ``s`` in points, from the same metrics. Used for text set horizontally."""
    return TextPath((0, 0), s, size=size, prop=FontProperties(size=size)).get_extents().height


def _assert_fits(tops: list[tuple[float, str]]) -> None:
    """Refuse to draw an annotation stack that would leave the axes.

    The stack heights are fixed in POINTS while the axes is measured in data units, so a change to
    the panel's rectangle or to the type ladder can push the tallest column through the top of the
    axes. That has to fail here rather than reach the composite, where the overhang would enlarge
    the pinned canvas.
    """
    over = [(round(t, 3), lab) for t, lab in tops if t > YMAX]
    assert not over, (
        f"panel c: {len(over)} annotation stacks reach past the axes top ({YMAX}): {over}. "
        f"Raise YMAX or cut the annotation into the caption; do not lower the type.")


def draw_shape(ax):
    if not os.path.exists(SRC):
        raise FileNotFoundError(
            f"{SRC} missing. Run analysis/class_c/oracle_shape_test.py.")
    d = json.load(open(SRC))

    x = np.arange(len(COLS))   # 0 = mean-shaped oracle, 1 = distribution-shaped oracle
    ax.set_xlim(-0.55, len(COLS) - 0.45)
    ax.set_ylim(0.0, YMAX)
    # Data units per printed point, resolved from the rectangle the composite actually gave this
    # panel. Everything stacked above a bar is sized in points and placed through this.
    upt = YMAX / (ax.get_position().height * ax.figure.get_figheight() * 72.0)

    # Which series wins each column is READ from the result file, not listed here, and is checked
    # against the three values drawn in that column: a file whose stated winner is not the argmax
    # of its own numbers must stop the build rather than put the flag on the wrong bar.
    winners = []
    for suffix, stem, _ in COLS:
        vals = {key: d[f"{key}_vs_oracle{suffix}"] for key, _, _, _ in ROWS}
        stated = d[f"winner_under_{stem}_oracle"]
        best = max(vals, key=vals.get)
        assert stated == best, (
            f"{SRC} says {stated!r} wins under the {suffix} oracle, but the largest value in that "
            f"column is {best!r} ({vals[best]:+.3f} against {vals[stated]:+.3f}).")
        # The bounded left spine below stops at YTICKS[-1], so a bar taller than that would rise
        # past the end of its own scale and be read against nothing.
        assert max(vals.values()) <= YTICKS[-1], (
            f"the {suffix} oracle column reaches {max(vals.values()):+.3f}, past the top tick "
            f"{YTICKS[-1]}. Extend YTICKS (and YMAX with it); the spine may not stop short of a bar.")
        winners.append(stated)

    tops = []
    for i, (key, name, col, name_at) in enumerate(ROWS):
        v = [d[f"{key}_vs_oracle{suffix}"] for suffix, _, _ in COLS]
        off = (i - 1) * BAR_W
        # The control series is an OPEN bar, not a hatched one. Open-versus-filled is the
        # encoding the rest of the deck now uses for "this series performs no retrieval"
        # (Fig. 3h) and "this is what a supervised probe reaches" (Fig. 4d), and a "///" hatch
        # under a 0.88 alpha fill was two extra visual channels for the same binary.
        control = key == "magmatch"
        ax.bar(x + off, v, BAR_W, color="white" if control else col, zorder=3,
               edgecolor=col, linewidth=0.8)
        for xi, vv in zip(x, v):
            # three decimals, because these are the six numbers the caption quotes verbatim
            lab = f"{vv:+.3f}"
            ax.text(xi + off, vv + GAP_BAR_PT * upt, lab, ha="center", va="bottom",
                    rotation=90, fontsize=PT_ANNOT, color=TEXT, zorder=6)
            top = vv + (GAP_BAR_PT + _len_pt(lab, PT_ANNOT)) * upt
            if xi == name_at:
                # The direct label that replaced the legend: the series name, on its own bar. The
                # control's name is set in its own SHARED grey rather than in ink, which is the
                # convention Fig. 3h uses for a subordinate row and which here also hands the one
                # unfilled series the colour that identifies it in the other column.
                ax.text(xi + off, top + GAP_NAME_PT * upt, name, ha="center", va="bottom",
                        rotation=90, fontsize=PT_ANNOT, color=SHARED if control else TEXT,
                        zorder=6)
                top += (GAP_NAME_PT + _len_pt(name, PT_ANNOT)) * upt
            if key == winners[xi]:
                # the swap is the finding: mark which bar wins in each column, and say so in words
                # rather than leaving a bare triangle for the reader to decode. The triangle is the
                # coloured mark and points back down the column at the bar it belongs to; the word
                # is ink, because in this deck the marks carry the colour and the text does not.
                ax.plot(xi + off, top + (GAP_STACK_PT + 0.5 * MS_WIN) * upt, marker="v",
                        ms=MS_WIN, color=col, zorder=6, clip_on=False)
                top += (GAP_STACK_PT + MS_WIN + GAP_STACK_PT) * upt
                ax.text(xi + off, top, "wins", ha="center", va="bottom", fontsize=PT_ANNOT,
                        color=TEXT, zorder=6)
                top += _height_pt("wins", PT_ANNOT) * upt   # the word is horizontal: its height
            tops.append((top, f"{name} under {COLS[xi][0]}"))
    _assert_fits(tops)

    # above the bars: the bars carry a white edge, which was punching gaps in a baseline drawn
    # underneath them and leaving black only in the inter-bar gutters
    ax.axhline(0, lw=0.8, color=TEXT, zorder=5)
    ax.set_xticks(x)
    # Sentence case, plain weight. Bold all-caps tick labels are a slide idiom and were the
    # heaviest text in the panel, competing with the numbers the panel exists to report.
    ax.set_xticklabels([lab for _, _, lab in COLS], fontsize=PT_TICK, linespacing=1.25)
    # Two lines: rotated, the one-line version is 1.69 in of text at PT_ANNOT against a 1.75 in
    # axes, i.e. it would run the full height of the panel with 0.06 in to spare. labelpad stays
    # at 1.5, which is as tight to the tick labels as it goes: this label and panel b's colour-bar
    # label share the 0.80 in gutter between the two axes, the label block is 0.23 in of it, and
    # at 1.5 the two clear each other by 1.8 pt with the label 1.5 pt off its own tick labels.
    # There is no slack left on either side of it, so a third line or a larger size here would
    # have to come out of a neighbour.
    ax.set_ylabel("Spearman $\\rho$ with\nthe protein evaluator", fontsize=PT_ANNOT,
                  linespacing=1.20, labelpad=1.5)
    ax.set_yticks(list(YTICKS))
    # the axis runs to YMAX to hold the annotation stacks, but the data stop inside YTICKS[-1];
    # the spine is bounded so it does not advertise a scale that carries nothing
    ax.spines["left"].set_bounds(0.0, YTICKS[-1])
    for s in ("right", "top"):
        ax.spines[s].set_visible(False)


if __name__ == "__main__":
    # Drawn at the exact rectangle fig4_assemble.RECTS gives panel c, so a standalone preview is
    # the printed panel and not a differently shaped one.
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from figstyle import apply_style, soften_axes   # noqa: E402
    from fig4_style import PT_TITLE                 # noqa: E402

    apply_style(sizes=(PT_TITLE, PT_ANNOT, PT_TICK))
    fig = plt.figure(figsize=(2.90, 2.40))
    ax = fig.add_axes([0.58 / 2.90, 0.45 / 2.40, 1.93 / 2.90, 1.75 / 2.40])
    draw_shape(ax)
    soften_axes(fig)
    out = os.path.join(os.path.dirname(__file__), "4shape.png")
    fig.savefig(out, dpi=300)
    print(f"wrote {out}")
