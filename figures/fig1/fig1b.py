"""PopRetrieve Figure 1 panel b: why averaging can fail.

WHAT THIS PANEL HAS TO SAY
--------------------------
Two drugs, one population of cells. Drug A moves every cell, Drug B moves only the responsive
majority and leaves a resistant minority sitting at baseline. The population mean is the same
under both, so a mean signature cannot tell them apart, while the cells plainly can.

The panel is BIOLOGICAL, not statistical. It is about the fate of the same cells under two
drugs, so the reader should see one population being carried across intact (Drug A) and the same
population being torn in two (Drug B). That is why the three lanes are drawn from ONE glyph:
lanes 1 and 2 are the same cells at two positions on the response axis, and lane 3 is those same
cells with only the majority moved. Nothing here is measured; the arithmetic that makes the two
means equal belongs in the caption, and deliberately does not appear on the panel.

WHY THE GEOMETRY IS A CONSTRUCTION AND NOT A MEASUREMENT
-------------------------------------------------------
"Identical mean response" is the panel's whole claim, so it has to be a fact about the picture
rather than a caption the picture almost supports. Two things enforce it:

  * R_MAJ_B is derived from the minority fraction, not typed in. If the minority does not move,
    the majority has to overshoot by exactly 1 / (1 - f) to hold the population mean fixed.
  * Each lane is translated RIGIDLY, as a whole, so that the mean of its drawn cells lands
    exactly on the shared dashed rule. A seeded uniform draw of 60 cells misses its own centre by
    a percent or two, which is invisible on one lane and, across two lanes, is the difference
    between a rule that passes through both diamonds and one that misses both. The translation
    moves every cell of a lane by the same amount, so it changes no within-lane structure.

The single dashed rule is the only place the two treated lanes touch, and it is what makes the
Drug B diamond damning: it sits in the empty gap between the two fragments, on a response value
no cell in that lane has.

Layout, for a 1.376 x 3.00 in axes: the key is at the top left, the panel's phrase sits directly
above the rule it labels so the dashes hang from the words, and the three lanes read downward
against one horizontal response axis at the foot.

Run standalone: python fig1b.py
"""
from __future__ import annotations

import os
import re
import sys

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import PathCollection

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# The frozen vocabulary. Nothing here is redefined locally, and no colour is imported from
# figstyle: fig1_style is the one place that maps a hue to a meaning for this figure.
from fig1_style import (FAINT, LW_HAIR, MEAN, POP, PT_ANNOT, PT_TITLE, SHARED,  # noqa: E402
                        SUBTLE, TEXT, arrow, blank, cells, centroid, title)

# ------------------------------------------------------------------ the population, as drawn
N_CELLS = 60                # divides by the minority fraction exactly, so 48 / 12 cells
MINOR_FRAC = 0.20
S_CELL = 3.0                # marker area; at this panel's blob size 60 cells read as a cloud
A_CELL = 0.70               # the majority is context, so it sits back from the blue minority
RX, RY = 0.085, 0.025       # blob radii in axes fractions; 0.117 x 0.075 in, so it reads round

# ------------------------------------------------------------------ the response axis
R_BASE = 0.0                # untreated, and where a cell that does not respond stays
R_TREATED = 1.0             # the response Drug A produces in every cell
# What the majority must reach under Drug B for the population mean to be unchanged when the
# minority does not move at all. Derived, not typed: this identity is the panel's claim, and a
# literal 1.25 would let the fraction and the overshoot drift apart in a later edit.
R_MAJ_B = R_TREATED / (1.0 - MINOR_FRAC)

X_BASE, X_MAJ_B = 0.155, 0.865     # baseline and the far end of the Drug B majority, in axes x
X_SCALE = (X_MAJ_B - X_BASE) / R_MAJ_B

# ------------------------------------------------------------------ vertical score, axes fractions
Y_KEY = (0.975, 0.928)      # the two state definitions
# The phrase is set over the rule, not over the panel, and it wraps because at PT_TITLE in bold
# it is 1.40 in wide on one line and the axes is 1.376 in. Wrapping is the only way to keep the
# stated size; shrinking it to fit is what the type ladder exists to forbid.
Y_TITLE, X_TITLE = 0.845, 0.985
Y_RULE_TOP = 0.797          # just under the phrase, so the dashes hang from the words
Y_AXIS, Y_AXIS_LABEL = 0.093, 0.038

X_KEY_SWATCH, X_KEY_TEXT = 0.045, 0.088
X_TRACK = (0.055, 0.985)    # each lane's stretch of the shared response axis
DY_BLOB = 0.072             # lane name -> cells
DY_MEAN = 0.046             # cells -> the mean diamond, which sits clear of the cells it summarises
DY_PHRASE = 0.078           # cells -> the phrase under a treated lane

# name, name y, majority response, minority response, phrase under the lane. The three names are
# spaced to leave EQUAL WHITESPACE between blocks rather than equal distance between names: the
# untreated lane carries no phrase and is a third shorter, so even centres put all of its missing
# line into one gap and the panel came apart into "lane 1" and "lanes 2 and 3".
LANES = (
    ("Untreated", 0.784, R_BASE, R_BASE, None),
    ("+ Drug A", 0.594, R_TREATED, R_TREATED, "uniform response"),
    ("+ Drug B", 0.335, R_MAJ_B, R_BASE, "minority resistance"),
)


def _x(r: float) -> float:
    """Response units to axes x. One mapping, so all three lanes share one response axis."""
    return X_BASE + X_SCALE * r


def _shift(coll: PathCollection, dx: float) -> None:
    """Translate a drawn population rigidly along the response axis."""
    off = np.asarray(coll.get_offsets(), dtype=float).copy()
    off[:, 0] += dx
    coll.set_offsets(off)


def _lane(ax: plt.Axes, rng: np.random.Generator, cy: float, r_maj: float,
          r_min: float) -> float:
    """Draw one lane's cells at their two response positions; return the drawn mean's x.

    The lane starts as ONE population glyph at baseline and is then placed, rather than being
    sampled separately per state, because the biological claim is that these are the same cells
    in every lane. cells() puts the minority in the lower part of the blob, so the majority and
    the minority come back as two collections that can be carried to different response values:
    equal for Drug A, which keeps the blob intact, and split for Drug B, which tears it.
    """
    first = len(ax.collections)
    cells(ax, _x(R_BASE), cy, N_CELLS, RX, RY, color=SHARED, minority=(MINOR_FRAC, POP),
          rng=rng, s=S_CELL, alpha=A_CELL)
    maj, mnr = ax.collections[first:]
    for coll, r in ((maj, r_maj), (mnr, r_min)):
        _shift(coll, _x(r) - _x(R_BASE))

    # The rigid correction. The target is the population mean the construction implies; the drawn
    # mean is what 60 seeded draws actually landed on, and the whole lane moves by the difference.
    target = _x((1.0 - MINOR_FRAC) * r_maj + MINOR_FRAC * r_min)
    drawn = np.concatenate([np.asarray(c.get_offsets())[:, 0] for c in (maj, mnr)])
    for coll in (maj, mnr):
        _shift(coll, target - drawn.mean())
    return target


def draw_1b(ax: plt.Axes) -> None:
    """Draw panel b into ``ax``, which the composite sizes at 1.376 x 3.00 in.

    Everything is placed in axes fractions, so the panel is correct only at that size: RX and RY
    are chosen to draw a round cell blob at that width-to-height ratio, and nothing is clipped or
    drawn outside the axes, because in the composite an overhang widens the whole figure.
    """
    blank(ax)

    # ---------------- the two cellular states, defined once ----------------
    # Drawn with the same helper and the same marker size as the lanes, so the key is a sample of
    # the panel rather than a legend about it.
    # The two swatches carry 12 and 3 cells, the same 4:1 the words state and the same 4:1 the
    # lanes draw, so the key cannot read as two equal groups.
    for y, colour, n, s, alpha, label in (
            (Y_KEY[0], SHARED, 12, S_CELL, A_CELL, "Responsive majority, 80%"),
            (Y_KEY[1], POP, 3, S_CELL * 1.25, 0.95, "Resistant minority, 20%")):
        cells(ax, X_KEY_SWATCH, y, n, 0.028, 0.009, color=colour, rng=np.random.default_rng(3),
              s=s, alpha=alpha)
        ax.text(X_KEY_TEXT, y, label, ha="left", va="center", fontsize=PT_ANNOT, color=TEXT)

    # ---------------- the phrase, and the rule it labels ----------------
    # Set at the top of the rule rather than at the top of the panel: the dashes then hang from
    # the words, which is the only thing tying the claim to the geometry that makes it true.
    # Flush right, so the block straddles the rule it names as closely as the panel width allows.
    title(ax, "Identical mean\nresponse", x=X_TITLE, y=Y_TITLE, ha="right", va="center",
          linespacing=1.1)
    x_mean = _x(R_TREATED)
    # Both ends are derived from the lane score rather than typed, so a lane that moves cannot
    # leave the rule stopping short of the diamond it is supposed to carry.
    y_foot = LANES[-1][1] - DY_BLOB - DY_MEAN - 0.024
    ax.plot([x_mean, x_mean], [Y_RULE_TOP, y_foot], ls=(0, (2.6, 2.0)), lw=LW_HAIR, color=MEAN,
            zorder=1)
    # Baseline, running down from the untreated population that defines it. Unlabelled on
    # purpose: it exists so that "the minority stayed put" is a geometric fact, not a phrase.
    ax.plot([_x(R_BASE)] * 2, [LANES[0][1] - DY_BLOB, y_foot], lw=LW_HAIR, color=FAINT, zorder=1)

    # ---------------- the three lanes ----------------
    for name, y_name, r_maj, r_min, phrase in LANES:
        ax.text(0.0, y_name, name, ha="left", va="center", fontsize=PT_ANNOT, color=TEXT,
                fontweight="bold")
        y_cells = y_name - DY_BLOB
        # The lane's own stretch of the one response axis. It is what ties a name at the left
        # edge to cells two thirds of the way across, and it makes "the same axis three times"
        # something the eye gets for free rather than something the caption has to assert.
        ax.plot(list(X_TRACK), [y_cells] * 2, lw=LW_HAIR, color=FAINT, zorder=0)
        # One generator, re-seeded per lane, so every lane draws the same 60 cells and the
        # reader is watching one population under three conditions.
        x_mean_drawn = _lane(ax, np.random.default_rng(11), y_cells, r_maj, r_min)
        if phrase is None:                     # untreated carries no claim and gets no marker
            continue
        # Below the cells rather than on them: at the default centroid size the diamond covers
        # the middle of a blob this small, and under Drug A that is the middle of the very
        # population it is standing for.
        centroid(ax, x_mean_drawn, y_cells - DY_MEAN)
        ax.text(0.0, y_cells - DY_PHRASE, phrase, ha="left", va="center", fontsize=PT_ANNOT,
                color=TEXT)

    # ---------------- the one response axis all three lanes are read against ----------------
    arrow(ax, (0.055, Y_AXIS), (0.985, Y_AXIS), color=SHARED)
    ax.text(0.5, Y_AXIS_LABEL, "single-cell response", ha="center", va="center",
            fontsize=PT_ANNOT, color=SUBTLE)


# ---------------------------------------------------------------------------- preview and gates
_SUBSUP = re.compile(r"\$[^$]*[\^_][^$]*\$")


def _check_type(fig, floor=6.5):
    """Smallest EFFECTIVE point size on the panel. Mathtext sub/superscripts print at 0.7x."""
    found = []
    for t in fig.findobj(plt.Text):
        s = str(t.get_text())
        if not s.strip() or not t.get_visible():
            continue
        found.append((round(t.get_fontsize() * (0.7 if _SUBSUP.search(s) else 1.0), 3), s))
    bad = [f for f in found if f[0] < floor - 1e-6]
    assert not bad, f"below the {floor} pt floor: {sorted(bad)}"
    return min(found)[0]


def _check_bbox(fig, ax, tol_in=0.0005):
    """Nothing may hang outside the axes: in the composite an overhang widens the whole figure."""
    fig.canvas.draw()
    rend = fig.canvas.get_renderer()
    box = ax.get_window_extent(rend)
    out = []
    furniture = (ax.patch, ax.xaxis, ax.yaxis, *ax.spines.values())
    for art in ax.get_children():
        # The axis and spine artists still report a tight bbox under ax.axis("off"), and they
        # draw nothing, so measuring them would report an overhang that cannot exist in print.
        if art in furniture or not art.get_visible():
            continue
        bb = art.get_tightbbox(rend)
        if bb is None or bb.width <= 0:
            continue
        over = max(box.x0 - bb.x0, bb.x1 - box.x1, box.y0 - bb.y0, bb.y1 - box.y1) / fig.dpi
        if over > tol_in:
            what = art.get_text() if hasattr(art, "get_text") else ""
            out.append((round(over, 4), type(art).__name__, str(what)[:34]))
    for row in sorted(out, reverse=True):
        print(f"  OUTSIDE by {row[0]:.4f} in: {row[1]} {row[2]!r}")
    assert not out, f"{len(out)} artist(s) hang outside the axes"
    return True


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from figstyle import apply_style
    from fig1_style import PT_TICK

    # The AXES is the size the composite gives this panel, and the rc sizes are the ones
    # fig1_assemble sets. A panel tuned at any other size is wrong in the figure that ships.
    apply_style(sizes=(PT_TITLE, PT_ANNOT, PT_TICK))
    fig = plt.figure(figsize=(1.376, 3.0))
    ax = fig.add_axes([0, 0, 1, 1])
    draw_1b(ax)

    # The identity the panel asserts, measured off the cells that were actually drawn rather
    # than off the constants they came from. This is the one claim panel b makes, so it is
    # checked against the picture: if a lane ever stopped landing on the rule, the panel would
    # be asserting in bold something its own marks do not do.
    assert abs(round(N_CELLS * MINOR_FRAC) - N_CELLS * MINOR_FRAC) < 1e-12, N_CELLS
    means = {}
    for name, y_name, _, _, phrase in LANES:
        y_lane = y_name - DY_BLOB
        pts = [o for c in ax.collections for o in np.asarray(c.get_offsets())
               if abs(o[1] - y_lane) <= RY + 1e-9 and len(c.get_offsets()) > 1]
        assert len(pts) == N_CELLS, (name, len(pts))
        means[name] = float(np.mean([q[0] for q in pts]))
    treated = [v for (n, _, _, _, p), v in zip(LANES, means.values()) if p]
    assert max(treated) - min(treated) < 1e-12, means
    assert abs(treated[0] - _x(R_TREATED)) < 1e-12, (treated, _x(R_TREATED))
    print(f"drawn population means (axes x): "
          f"{ {k: round(v, 6) for k, v in means.items()} }")

    print(f"smallest effective type: {_check_type(fig):.2f} pt")
    print(f"all artists inside the axes: {_check_bbox(fig, ax)}")
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "1b.png")
    fig.savefig(out, dpi=400)
    print(f"wrote {out}  (axes 1.376 x 3.00 in)")
