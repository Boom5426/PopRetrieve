"""PopRetrieve Figure 2 panel a: the Hit@1 ladder, read as an information hierarchy.

WHAT THIS PANEL CLAIMS
----------------------
One thing: most of the retrieval information a mean-cosine scorer misses is response MAGNITUDE,
and population structure adds a smaller residue on top of it. Three scorers carry that claim and
the other six are reference points:

    mean cosine     direction only                      0.3885
    mean L2         direction + magnitude               0.7877     +0.3992
    energy          + the rest of the distribution      0.8357     +0.0480

WHAT THIS PANEL USED TO CLAIM, AND WHY IT STOPPED
--------------------------------------------------
Until 2026-09-03 it claimed that every population-level scorer sits above every mean-level one on
macro-average Hit@1, grouped the ladder into two family blocks, washed each block in its family
colour, and ASSERTED the separation at draw time so that new data could not break it quietly.

New data broke it. `mean_l2` is a mean-family scorer and it lands at 0.7877, above three of the
four population scorers; only the energy distance stays above it. The assertion fired, which is
the gate working. It is removed rather than repaired, and the family washes and the rotated family
labels went with it, because the separation they drew was a property of which mean scorer was in
the panel and not of the two representation families.

The replacement is not a different grouping. It is a different axis: what a scorer KEEPS, in
three tiers, direction then magnitude then distribution. `fig2_style.TIER` assigns it by
construction rather than by result, so no scorer's tier can move when its number does.

SOURCE
------
results/exp08_signature_baselines/summary.csv, the only file this module reads. Nine scorers x
seven task x setting cells: controlled x {K562, A549, MCF7}, cross-line x {K562+A549, A549+MCF7,
K562+MCF7}, and Frangieh x {Control+IFNg}. The plotted quantity is the UNWEIGHTED macro-mean of
hit@1 over those seven cells; the cell count is read from the file and asserted to be seven for
every method, and it is interpolated into the x axis label so the label cannot outlive the data.

Every number drawn is computed here. Nothing is typed as a literal.

JUDGEMENT CALLS A READER COULD REASONABLY DISAGREE WITH
-------------------------------------------------------
1.  UNWEIGHTED macro-mean over the seven cells, so a 30-query cell counts as much as a 360-query
    cell. Unweighted is plotted because the seven cells are seven experimental conditions rather
    than seven samples of one population.
2.  The two increments are drawn as brackets between three rungs, not as a stacked bar. A stack
    would imply the three tiers partition one quantity; they do not, because the ladder is sorted
    by value and the three primaries are not adjacent in it.
3.  The magnitude step is the panel's largest quantity and it is drawn as such. That is the
    result, not an emphasis choice: at +0.3992 against +0.0480 it is eight times the step above
    it, and a panel that gave them equal weight would be the one making a claim.
4.  cmap_cosine and mean_cosine are IDENTICAL, not merely close: they agree to full precision in
    every numeric column of all seven cells, which this module asserts. The tie is marked, and
    the marked pair is read out of the sort so the marker cannot come to rest against two rows
    the assertion never looked at.
5.  The two CMap rows are PUBLISHED baselines. That is PROVENANCE, not representation, so it is
    marked with a dagger and never with a colour.
6.  Secondary scorers are drawn in one neutral tone rather than in tier colours. Colouring all
    nine by tier would put four blue bars and four grey-blue bars on the panel and lose the three
    the argument runs through. The tier of every scorer is in the caption.

Run standalone: python fig2a.py
"""
from __future__ import annotations

import os
import sys

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Rectangle

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fig2_style import (BAR_TRACK, FAINT, HAIRLINE, LW_HAIR, MAGNITUDE, MEAN,  # noqa: E402
                        POP, PRIMARY, PT_ANNOT, PT_SMALL, PT_TICK, PT_TITLE,
                        SCORERS, SHARED, SUBTLE, TEXT, TIER, TIER_NAME)

# One colour per tier, and only the three primaries get one. TIER_COLOUR is keyed by tier rather
# than by scorer so a scorer cannot be given a colour its tier does not have.
TIER_COLOUR = {"direction": MEAN, "magnitude": MAGNITUDE, "population": POP}

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC = os.path.join(REPO, "results", "exp08_signature_baselines", "summary.csv")

# ------------------------------------------------------------------------------ geometry
# Authored against the composite's own box for panel a: 2.95 x 1.94 in, which is fig2_assemble's
# row height 2.54 less its 0.60 in bottom pad. The tracks deliberately do NOT run the full width.
# x = 1 (the attainable Hit@1 maximum) sits at TRACK_IN inches, and everything right of it is the
# value column and the headline block, so the panel reads as bars on the left and the comparison
# on the right.
#
# THE PANEL STOPPED BEING FULL WIDTH ON 2026-09-01, and these four numbers are the whole of it.
# It was 5.88 x 1.20 in: a 4.9:1 strip whose longest bar was 3.00 in of 6.9 pt ink, 44:1, and
# whose xlim ran to 1.656 so that 2.33 in of the axes, 40 per cent, sat beyond the data holding
# the value column, the headline and the provenance key. That width was spent, not wasted, which
# is why folding the column back in does not fix the panel: at full width the only alternative to
# dead space is a longer track and thinner bars.
#
# What the new numbers cost, stated plainly: the longest bar is 1.47 in rather than 3.00, and the
# horizontal distance between the population floor (coverage-worst, 0.589) and the mean ceiling
# (PCA-mean, 0.518) is 0.124 in rather than 0.253. The RATIO the panel argues from is unchanged;
# the absolute separation is 3.2 mm rather than 6.4, still an order of magnitude above visual
# acuity. What is bought back is the aspect, 4.90:1 to 1.52:1, and a row pitch of 15.8 pt against
# the old 9.8, so the bars are 0.101 in thick rather than 0.068.
#
# The value column stays OUTSIDE the track. Folding it inside the wash's Hit@1 = 1 ceiling would
# buy TRACK_IN 2.10 instead of 1.75, i.e. 0.6 mm more separation, but figstyle's presentation
# layer states that value labels sit right-aligned past the end of the track, and every other
# value column in the deck does. 0.6 mm is not worth being the one panel that reads differently.
TRACK_IN = 1.75             # inches spanned by Hit@1 = 0 .. 1
AXES_IN = 2.95              # the panel's axes width, from fig2_assemble's ledger
AXES_H_IN = 1.62            # the panel's axes height, same ledger
XMAX = AXES_IN / TRACK_IN   # right edge of the axes, in Hit@1 units

def _u(inches: float) -> float:
    """Inches on the printed page -> x-axis (Hit@1) units. Keeps the ledger readable."""
    return inches / TRACK_IN

FAM_GAP = 0.0               # the family blocks are gone; the ladder is one run of rows
Y_PAD = 0.50                # air above the top wash and below the bottom one, in row units
# Row units, so a bar's printed height follows the pitch. Raised with the 2026-09-04 compaction so
# that the ladder keeps the ink-to-white ratio it was drawn with: 0.100 and 0.122 in at the
# 0.180 in pitch, against 0.101 and 0.128 in at the 0.220 in pitch it had before.
BAR_H, BAR_H_HEAD = 0.555, 0.680
assert BAR_H_HEAD < 1.0, "a bar taller than the row pitch would touch its neighbour"

# The y axis is measured in ROW UNITS, one per scorer, so the printed pitch is whatever the box
# height divides into. It is derived here rather than left implicit, because the box lost 0.14 in
# and the pitch is what has to clear the scorer names.
Y_SPAN = (len(SCORERS) - 1) + FAM_GAP + 2 * Y_PAD
ROW_IN = AXES_H_IN / Y_SPAN          # printed inches per row unit: 0.1800 at 1.62 in
assert ROW_IN * 72.0 >= PT_TICK * 1.30, (
    f"the ladder's row pitch is {ROW_IN * 72.0:.2f} pt and the scorer names set at {PT_TICK} pt; "
    "adjacent rows would crowd. Drop a row, widen the box, or take the names into the caption.")

def _v(inches: float) -> float:
    """Inches -> y-axis (row) units. The box height moved once; it can move again."""
    return inches / ROW_IN

X_LABEL_R = -_u(0.062)      # right edge of the scorer-name column
X_DAGGER = -_u(0.030)       # the published-baseline glyph, on its own fixed column
# The family column is gone. What used to be 0.845 in of rotated family label and swatch is now
# axes width: the ladder needs no left apparatus beyond the scorer names and the dagger column.
# The block right of the track is 1.20 in wide (AXES_IN - TRACK_IN) and holds three things in
# order: the value column, the bracket, the headline. Every offset below is inches past the track.
X_VALUE_R = 1.0 + _u(0.280)  # right edge of the value column; "0.837" sets 0.23 in
X_ARM = 1.0 + _u(0.330)      # where the bracket's arms stop, clear of the value column
X_BRACKET = 1.0 + _u(0.420)   # the magnitude step's spine
X_BRACKET2 = 1.0 + _u(0.780)  # the distribution step's spine, in its own column
X_HEAD = 1.0 + _u(0.470)     # left edge of the headline text
# ONE PRECISION FOR THE WHOLE PANEL, and it is the manuscript's. The value column set three
# decimals and the two step brackets set four, so the panel printed "0.836", "0.788" and
# "+0.0480" together: a reader who subtracted the two printed values got +0.048 and was shown a
# number with a digit the values it came from do not carry. The manuscript's macros are worse
# than a mismatch inside the panel, they are a mismatch with it: \HITSTEPDIST is +0.048 and
# \HITSTEPMAG is +0.399, three decimals, so the same two quantities appeared at two precisions
# in one paper. Both now read from here. The step is still computed unrounded; only its display
# changes, so +0.399 remains the difference of the underlying values and not of their roundings.
VALUE_DP = 3
LW_HEAD = 0.9               # headline bracket: above LW_HAIR, and inked, so the brackets rank
FOOT_IN = 0.245             # drop of the x axis label below the axes, in inches
# The provenance key gets its own baseline. At full width it shared FOOT_IN with the x label,
# which was possible only because there were 2.33 in to spread them across; at 2.95 in the x
# label alone sets 2.06 in and the key 0.84 in, so they cannot share a line.
KEY_IN = 0.42


def _load():
    """Macro-mean Hit@1 per scorer, family-grouped and value-sorted, with the claims asserted."""
    s = pd.read_csv(SRC)
    n = len(s[["task", "setting"]].drop_duplicates())
    assert n == 7, f"the manuscript's design is 7 task x setting cells; summary.csv has {n}"
    assert set(s["method"]) == set(SCORERS), (
        f"summary.csv scorers {sorted(set(s['method']))} do not match fig2_style.SCORERS")
    # The GRID, not merely the row count. A macro-mean over seven rows means nothing unless the
    # seven rows are the same seven cells for every scorer; otherwise the ladder would rank
    # scorers measured on different conditions and no rung would be comparable to any other.
    grid = s.groupby(["method", "task", "setting"]).size()
    assert grid.eq(1).all() and len(grid) == len(SCORERS) * n, (
        f"every method must cover all {n} cells exactly once; the method x cell grid has "
        f"{len(grid)} of {len(SCORERS) * n} slots filled, with row counts "
        f"{sorted(grid.unique().tolist())}")

    # Both levels, because averaging hides the first. Hit@1 is a rate, so a source cell outside
    # [0, 1] is corrupt even when the seven-cell mean it feeds still lands on the track.
    assert s["hit@1"].between(0.0, 1.0).all(), (
        "hit@1 is a rate; summary.csv has a cell outside [0, 1], so the macro-mean plotted "
        "against the 0..1 track would be built from a number that cannot be a Hit@1")
    agg = s.groupby("method")["hit@1"].mean()
    assert agg.between(0.0, 1.0).all(), (
        "the full-extent track states 0..1 as the attainable range; a value left it")

    # Sorted by value alone, ties broken by ascending method name so the ladder is reproducible.
    # There is no family grouping and no family assertion: the assertion that every population
    # scorer beats every mean scorer FIRED on 2026-09-03 when the magnitude control entered the
    # panel, and it is removed rather than repaired. See this module's docstring.
    order = sorted(SCORERS, key=lambda m: (-agg[m], m))

    # The three rungs the panel argues along, checked to be one scorer per tier so the hierarchy
    # cannot silently acquire two of anything.
    tiers = [TIER[m] for m in PRIMARY]
    assert sorted(tiers) == ["direction", "magnitude", "population"], (
        f"PRIMARY must hold exactly one scorer per tier; it holds {dict(zip(PRIMARY, tiers))}")
    prim = {TIER[m]: m for m in PRIMARY}
    assert agg[prim["direction"]] < agg[prim["magnitude"]] < agg[prim["population"]], (
        "the panel draws the three tiers as a rising ladder and labels the two steps between "
        f"them; measured they are {agg[prim['direction']]:.4f}, {agg[prim['magnitude']]:.4f}, "
        f"{agg[prim['population']]:.4f}, which is not rising. Restate the panel, do not reorder "
        "it: a non-monotone hierarchy is a finding.")

    # The tie marker's pair is READ OUT OF THE SORT rather than named as literals, so a data
    # change cannot slide the marker onto two rows whose identity was never tested.
    lowest = agg.min()
    tied = sorted([m for m in SCORERS if float(agg[m]) == float(lowest)])
    assert len(tied) == 2, f"the tie marker assumes exactly two equal scorers, found {len(tied)}"

    # And the marked tie is stronger than equal macro-means: the two scorers agree to full
    # precision in every numeric column of every cell. Assert that, because the panel says so.
    num = [c for c in s.columns if c not in ("task", "setting", "method")]
    key = ["task", "setting"]
    a, b = (s[s["method"] == m].sort_values(key).reset_index(drop=True) for m in tied)
    assert (a[key].values == b[key].values).all(), (
        f"{tied[0]} and {tied[1]} are not scored on the same {n} cells, so the panel cannot "
        "call them identical on all of them")
    assert (a[num].values == b[num].values).all(), (
        f"the panel marks {tied[0]} and {tied[1]} as identical on all {n} settings; they are not")

    return agg, order, prim, tied, n


def draw_2a(ax):
    """The Hit@1 ladder, read as direction then magnitude then distribution."""
    # Everything below is positioned in INCHES and converted through ROW_IN, _u and _v, so the
    # panel is only correct inside the box it was authored for. fig2_assemble owns that box and
    # cannot be imported here (it imports this module), so the ledger is checked against the axes
    # actually handed in.
    fig_w, fig_h = ax.figure.get_size_inches()
    box = ax.get_position()
    got_w, got_h = box.width * fig_w, box.height * fig_h
    assert abs(got_w - AXES_IN) < 0.01 and abs(got_h - AXES_H_IN) < 0.01, (
        f"panel a is authored against a {AXES_IN} x {AXES_H_IN} in axes and was handed "
        f"{got_w:.3f} x {got_h:.3f} in. Update AXES_IN / AXES_H_IN from fig2_assemble's ledger "
        "and re-measure FOOT_IN and the headline offsets; do not let the inch constants drift.")
    agg, order, prim, tied, n_cells = _load()
    ys = {m: i for i, m in enumerate(order)}
    head = set(prim.values())

    # One full-extent track behind the whole ladder, not one wash per family. Its right edge IS
    # Hit@1 = 1, so every bar is read against the ceiling without the eye travelling to the axis,
    # and no block of rows is shaded as though it were a group.
    ax.add_patch(Rectangle((0.0, -0.5), 1.0, len(order), facecolor=BAR_TRACK,
                           edgecolor="none", zorder=0))

    for m in order:
        v, y = float(agg[m]), ys[m]
        big = m in head
        # Only the three primaries carry a tier colour. The other six are one neutral tone: they
        # are reference points, and colouring them by tier would put eight coloured bars on the
        # panel and lose the three the argument runs through.
        ax.barh(y, v, height=BAR_H_HEAD if big else BAR_H,
                color=TIER_COLOUR[TIER[m]] if big else FAINT, linewidth=0, zorder=2)
        ax.text(X_LABEL_R, y, SCORERS[m]["label"], fontsize=PT_TICK, color=TEXT,
                fontweight="bold" if big else "normal", ha="right", va="center", clip_on=False)
        if SCORERS[m]["published"]:
            ax.text(X_DAGGER, y, "\u2020", fontsize=PT_SMALL, color=SUBTLE, ha="center",
                    va="center", clip_on=False)
        ax.text(X_VALUE_R, y, f"{v:.{VALUE_DP}f}", ha="right", va="center", clip_on=False,
                fontsize=PT_SMALL, color=TEXT if big else SUBTLE,
                fontweight="bold" if big else "normal")
        # The tier name sits inside the bar of the primary it belongs to, which is the one place
        # a tier is named without a legend and without a margin column.
        if big:
            ax.text(_u(0.055), y, TIER_NAME[TIER[m]], fontsize=PT_SMALL, color="white",
                    ha="left", va="center", zorder=3)

    # ---------------------------------------------------------------- the tie, marked not implied
    y_hi, y_lo = ys[tied[0]], ys[tied[-1]]
    x_t = float(agg[tied[0]]) + _u(0.130)
    ax.plot([x_t, x_t], [y_hi, y_lo], color=SHARED, lw=LW_HAIR, zorder=3, clip_on=False)
    for y in (y_hi, y_lo):
        ax.plot([x_t - _u(0.045), x_t], [y, y], color=SHARED, lw=LW_HAIR, zorder=3, clip_on=False)
    ax.text(x_t + _u(0.045), 0.5 * (y_hi + y_lo),
            f"identical, {n_cells}/{n_cells} (f)", fontsize=PT_SMALL, color=TEXT,
            ha="left", va="center")

    # ---------------------------------------------------------------- the two steps
    # These are the panel. Each bracket spans two of the three primaries and carries the step
    # between them, computed unrounded so the printed difference is the difference of the values
    # and not the difference of their printed roundings.
    steps = (("direction", "magnitude", X_BRACKET), ("magnitude", "population", X_BRACKET2))
    for lo_t, hi_t, x in steps:
        lo, hi = prim[lo_t], prim[hi_t]
        d = float(agg[hi]) - float(agg[lo])
        y_a, y_b = ys[hi], ys[lo]
        ax.plot([x, x], [y_a, y_b], color=TEXT, lw=LW_HEAD, zorder=3, clip_on=False)
        for y in (y_a, y_b):
            ax.plot([X_ARM, x], [y, y], color=TEXT, lw=LW_HEAD, zorder=3, clip_on=False)
        ax.text(x + _u(0.050), 0.5 * (y_a + y_b), f"+{d:.{VALUE_DP}f}", fontsize=PT_ANNOT,
                fontweight="bold", color=TEXT, ha="left", va="center", clip_on=False)

    # ---------------------------------------------------------------- axes furniture
    ax.set_xlim(0.0, XMAX)
    ax.set_ylim(len(order) - 1 + Y_PAD, -Y_PAD)          # inverted: best scorer on top
    ax.set_xticks([0.0, 0.25, 0.5, 0.75, 1.0])
    ax.set_yticks([])
    ax.set_xlabel(f"Hit@1, macro-average across {n_cells} task settings")
    ax.xaxis.set_label_coords(0.5 / XMAX, -FOOT_IN / AXES_H_IN)
    ax.tick_params(axis="y", length=0)
    ax.tick_params(axis="x", length=2.2, width=0.6, color=HAIRLINE, labelcolor=TEXT,
                   labelsize=PT_TICK)
    for sp in ("left", "right", "top"):
        ax.spines[sp].set_visible(False)
    ax.spines["bottom"].set_color(HAIRLINE)
    ax.spines["bottom"].set_linewidth(LW_HAIR)
    ax.spines["bottom"].set_bounds(0.0, 1.0)       # the scale exists only under the track
    ax.text(1.0, -KEY_IN / AXES_H_IN, "\u2020 published baseline", transform=ax.transAxes,
            fontsize=PT_SMALL, color=SUBTLE, ha="right", va="center")


if __name__ == "__main__":
    sys.path.insert(0, os.path.join(REPO, "figures"))
    from figstyle import apply_style
    apply_style(sizes=(PT_TITLE, PT_ANNOT, PT_TICK))
    fig = plt.figure(figsize=(3.97, 2.54))   # the box fig2_assemble gives this panel
    ax = fig.add_axes([0.94 / 3.97, 0.60 / 2.54, AXES_IN / 3.97, AXES_H_IN / 2.54])
    draw_2a(ax)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "2a.png")
    fig.savefig(out, dpi=300)
    print(f"wrote {out}")
