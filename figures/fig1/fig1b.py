"""PopRetrieve Figure 1 panel b: why averaging can fail.

WHAT THIS PANEL HAS TO SAY, AND WHY IT IS DRAWN RATHER THAN WRITTEN
------------------------------------------------------------------
Two drugs, one population of cells. Drug A moves every cell. Drug B moves only the responsive
majority and leaves a resistant minority exactly where it started. The population mean is the same
under both, so a mean signature cannot tell them apart, while the cells plainly can.

The earlier cut of this panel stated that in words over three scatter rows: the reader had to read
"identical mean response" and then verify it against the marks. The panel now carries it as
structure, and the words that remain name things rather than argue for them:

  * THE GHOST. Each treated lane keeps a FAINT copy of the untreated population at baseline, drawn
    from the same seeded draw, so every lane shows where its cells came from. Under Drug A the
    ghost is empty of blue: everyone left. Under Drug B the blue minority is still sitting inside
    it. "Resistance" is then a thing the reader SEES at one location, not an inference from two.
  * THE ARROWS. One per STATE that moved, leaving that state's own height inside the ghost. Drug A
    has two, parallel and equal, so its population travels intact. Drug B has one, visibly longer,
    which is the overshoot that keeps the two means equal, and the second arrow is missing. That
    missing arrow, at the height where the lane above it has one, is resistance drawn rather than
    asserted.
  * THE SHARED RULE. Both treated centroids sit on one vertical dashed rule, labelled "same mean".
    Under Drug A that rule passes through the middle of an intact population. Under Drug B it
    passes through a gap that contains no cell at all. That contrast is the panel's whole thesis
    and it needs no sentence.
  * THE BRACKET. The 80 / 20 split is named the way a biology figure names a subpopulation, with a
    two-segment bracket beside the untreated cells, rather than the way a statistics plot does,
    with a boxed key. The bracket's break is placed at the boundary between the cells that were
    actually drawn, so it measures the picture instead of asserting over it.

Nothing here is measured data. The arithmetic that makes the two means equal, 0.8 x 1.25 + 0.2 x 0
= 1.0, belongs to the caption and deliberately does not appear on the panel.

WHY THE GEOMETRY IS A CONSTRUCTION AND NOT A COINCIDENCE
-------------------------------------------------------
"Same mean" is the panel's claim, so it is enforced on the marks rather than trusted:

  * R_MAJ_B is derived from the minority fraction, not typed in. If the minority does not move,
    the majority must overshoot by exactly 1 / (1 - f) to hold the population mean fixed.
  * A seeded draw of 60 cells misses its own centre by a percent or two, which is invisible in one
    lane and, across two, is the difference between a rule through both diamonds and one through
    neither. So every cloud, ghosts included, is translated rigidly until the mean of its own
    drawn cells lands on the response value it is meant to sit at.

That single correction is enough for both claims at once, and only because 60 cells split 48 / 12
matches the 0.8 / 0.2 the mean is taken with. The Drug B lane's mean is then
0.8 x (majority mean + shift) + 0.2 x (minority mean), which is the undisturbed cloud's own mean
plus one unit of response, so the correction Drug B needs is the SAME number the untreated lane
and the ghosts need. Every cloud moves by that one number, which is why the Drug B minority can
land on the ghost to the last decimal instead of a hair off it. Were the fraction ever changed to
something the cell count does not divide, the assertion at the foot of this file would catch it.

LAYOUT, FOR A 3.15 x 1.60 IN AXES
---------------------------------
Landscape, so the response axis runs across the width and the three lanes stack in the height.
Condition names sit in a left column, in the lane band they belong to, which keeps the drawing area
free of text; the shared rule and its two words sit at the top right, over the two centroids they
carry. Every coordinate below is written in INCHES on the printed page and converted, because the
panel is a physical layout, not a unit square: a cloud drawn wider than tall, so its spread reads
along the response axis, and a label gap that clears a descender are both statements about inches.

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
                        SUBTLE, TEXT, arrow, blank, cells, centroid)

# ------------------------------------------------------------------ the page, in inches
# The rect fig1_assemble gives panel b in the four-rows-of-two layout. Everything else in this
# module is an inch measured against these two numbers, so the panel is correct at this size and
# is not a unit square that happens to have been viewed at it.
AX_W, AX_H = 3.15, 1.60


def _fx(x_in: float) -> float:
    """Inches from the axes LEFT edge to an axes fraction."""
    return x_in / AX_W


def _fy(y_in: float) -> float:
    """Inches from the axes TOP edge to an axes fraction. Down is the reading order here."""
    return 1.0 - y_in / AX_H


def _dx(w_in: float) -> float:
    """A horizontal LENGTH in inches, as an axes fraction."""
    return w_in / AX_W


def _dy(h_in: float) -> float:
    """A vertical LENGTH in inches, as an axes fraction."""
    return h_in / AX_H


# ------------------------------------------------------------------ the population, as drawn
N_CELLS = 60                # divides by the minority fraction exactly, so 48 / 12 cells
MINOR_FRAC = 0.20
S_CELL = 3.0                # marker area; at this blob size 60 cells read as a cloud, not a row
A_CELL = 0.70               # the majority is context, so it sits back from the blue minority
S_GHOST, A_GHOST = 2.4, 0.85    # the population left behind: present to the eye, never read
RX_IN, RY_IN = 0.14, 0.08   # blob radii in inches, so the cloud is the same shape in every lane

# ------------------------------------------------------------------ the response axis
R_BASE = 0.0                # untreated, and where a cell that does not respond stays
R_TREATED = 1.0             # the response Drug A produces in every cell
# What the majority must reach under Drug B for the population mean to be unchanged when the
# minority does not move at all. Derived, not typed: this identity is the panel's claim, and a
# literal 1.25 would let the fraction and the overshoot drift apart in a later edit.
R_MAJ_B = R_TREATED / (1.0 - MINOR_FRAC)

GUTTER_IN = 0.90            # the condition-name column; 0.85 in is the widest phrase it carries
EDGE_IN = 0.08              # right margin, wide enough that a marker radius still clears the axes
X_BASE_IN = GUTTER_IN + RX_IN               # the untreated blob, tight against the name column
X_MAX_IN = AX_W - EDGE_IN - RX_IN           # the Drug B majority, the furthest any cell travels
X_SCALE_IN = (X_MAX_IN - X_BASE_IN) / R_MAJ_B

# ------------------------------------------------------------------ vertical score, inches down
Y_PHRASE_TOP = 0.012        # the rule's name, hung from the top edge so the rule hangs from it
Y_RULE_TOP = 0.245
LANE_CY = (0.335, 0.735, 1.135)     # even pitch: three lanes of one population, not three plots
DY_MEAN = 0.135             # cells -> centroid, clear of the blob it summarises by about 1 pt
DY_NAME = 0.062             # half the leading of the two-line condition block in the left column
Y_AXIS = 1.430
Y_AXIS_LABEL = 1.540

# Each state's arrow leaves at its own height inside the blob, in inches from the lane centre, so
# it reads as that state moving rather than as the lane moving. The offsets are unequal because
# the states are: cells() gives the minority the lowest fifth of a uniform disk, whose boundary
# sits about half a radius below centre, so -0.038 leaves from the middle of the blue and +0.028
# from the bulk of the grey above it.
DY_ARROW = (0.028, -0.038)

BRACKET_DX = 0.035          # blob edge -> bracket spine
BRACKET_SERIF = 0.030       # the little inward return that makes a line read as a bracket
BRACKET_ARM = 0.100         # spine -> where the leader meets its label
DY_BRACKET_LABEL = 0.085    # lane centre -> label centre; the two labels then clear each other

# name, phrase under the name, lane centre, majority response, minority response. The untreated
# lane carries no phrase because it makes no claim; it is the reference the other two are read
# against, and the bracket beside it is the only thing it has to say.
LANES = (
    ("Untreated", None, LANE_CY[0], R_BASE, R_BASE),
    ("+ Drug A", "uniform response", LANE_CY[1], R_TREATED, R_TREATED),
    ("+ Drug B", "minority resistance", LANE_CY[2], R_MAJ_B, R_BASE),
)

SEED = 11                   # one draw of 60 cells, reused by every lane and every ghost


def _x(r: float) -> float:
    """Response units to an axes fraction. One mapping, so all three lanes share one axis."""
    return _fx(X_BASE_IN + X_SCALE_IN * r)


def _shift(coll: PathCollection, dx: float) -> None:
    """Translate a drawn population along the response axis, changing nothing else about it."""
    off = np.asarray(coll.get_offsets(), dtype=float).copy()
    off[:, 0] += dx
    coll.set_offsets(off)


def _xs(coll: PathCollection) -> np.ndarray:
    return np.asarray(coll.get_offsets(), dtype=float)[:, 0]


def _centre(colls, x_target: float) -> float:
    """Translate a set of collections together until their cells' mean x is ``x_target``.

    Rigid, so it changes no structure inside a lane: it moves where the population sits, never how
    it is spread. Returns the target, which is the drawn mean once the call has run.
    """
    drawn = np.concatenate([_xs(c) for c in colls])
    for coll in colls:
        _shift(coll, x_target - drawn.mean())
    return x_target


def _ghost(ax: plt.Axes, cy_in: float) -> PathCollection:
    """The untreated population, left behind at baseline in a treated lane.

    Drawn from the same seed as every lane, so it is not a similar cloud but literally the same
    cells at the same coordinates. That is what lets the Drug B minority land ON it rather than
    near it, and it is why the ghost is drawn without a minority colour: what the reader has to
    see at baseline under Drug B is which cells are still there, in blue, over a grey residue.
    """
    cells(ax, _x(R_BASE), _fy(cy_in), N_CELLS, _dx(RX_IN), _dy(RY_IN), color=FAINT,
          rng=np.random.default_rng(SEED), s=S_GHOST, alpha=A_GHOST, zorder=2)
    ghost = ax.collections[-1]
    _centre([ghost], _x(R_BASE))
    return ghost


def _lane(ax: plt.Axes, cy_in: float, r_maj: float, r_min: float) -> float:
    """Draw one lane's cells at their two response positions; return the drawn mean's x.

    The lane starts as ONE population glyph at baseline and is then placed, rather than sampled
    per state, because the biological claim is that these are the same cells in every lane.
    cells() puts the minority in the lower part of the blob, so the two states come back as two
    collections that can be carried to different response values: equal under Drug A, which keeps
    the population intact, and split under Drug B, which tears it.
    """
    first = len(ax.collections)
    cells(ax, _x(R_BASE), _fy(cy_in), N_CELLS, _dx(RX_IN), _dy(RY_IN), color=SHARED,
          minority=(MINOR_FRAC, POP), rng=np.random.default_rng(SEED), s=S_CELL, alpha=A_CELL)
    maj, mnr = ax.collections[first:]
    for coll, r in ((maj, r_maj), (mnr, r_min)):
        _shift(coll, _x(r) - _x(R_BASE))
    # The population mean this lane is built to have, which is where its centroid must end up.
    return _centre((maj, mnr), _x((1.0 - MINOR_FRAC) * r_maj + MINOR_FRAC * r_min))


def _bracket(ax: plt.Axes, maj: PathCollection, mnr: PathCollection, cy_in: float) -> None:
    """The 80 / 20 split, named beside the untreated cells the way a biology figure names one.

    A boxed key would put the two states in a corner and make the reader carry them back to the
    cells. The bracket puts them where the cells are, and its break sits at the boundary between
    the cells that were actually drawn, so the two arms are as long as the states they enclose.
    """
    sx = _fx(X_BASE_IN + RX_IN + BRACKET_DX)
    serif = _dx(BRACKET_SERIF)
    y_maj = np.asarray(maj.get_offsets())[:, 1]
    y_mnr = np.asarray(mnr.get_offsets())[:, 1]
    pad, gap = _dy(0.008), _dy(0.010)       # enclose the outermost cell; part at the boundary
    y_split = 0.5 * (y_maj.min() + y_mnr.max())
    spans = ((SHARED, y_maj.max() + pad, y_split + gap, "80% responsive", DY_BRACKET_LABEL),
             (POP, y_split - gap, y_mnr.min() - pad, "20% resistant", -DY_BRACKET_LABEL))
    for colour, y_hi, y_lo, label, dy_label in spans:
        ax.plot([sx - serif, sx, sx, sx - serif], [y_hi, y_hi, y_lo, y_lo],
                lw=LW_HAIR, color=colour, solid_joinstyle="miter", zorder=5)
        y_lab = _fy(cy_in) + _dy(dy_label)
        ax.plot([sx, sx + _dx(BRACKET_ARM)], [0.5 * (y_hi + y_lo), y_lab],
                lw=LW_HAIR, color=colour, zorder=5)
        ax.text(sx + _dx(BRACKET_ARM + 0.015), y_lab, label, ha="left", va="center",
                fontsize=PT_ANNOT, color=TEXT)


def draw_1b(ax: plt.Axes) -> None:
    """Draw panel b into ``ax``, which the composite sizes at AX_W x AX_H inches.

    Nothing is clipped and nothing is drawn outside the axes: in the composite an overhang widens
    the whole figure rather than being cropped away.
    """
    blank(ax)

    # ---------------- the rule the two treated means share, and its two words ----------------
    # Two words, at the top of the rule rather than the top of the panel, so the dashes hang from
    # them. Everything else this panel could say about the mean is the caption's job.
    #
    # This is the one phrase on Figure 1 that survived the 2026-09-01 pass, and it survived because
    # it is not a claim: it NAMES the dashed rule it sits on, the way an axis label names an axis,
    # and without it the reader meets an unexplained orange line. It is set at PT_ANNOT like every
    # other direct label on this figure rather than at the old PT_TITLE, because it is a label.
    #
    # It read "same mean" until 2026-09-03, and two words were one too few. The two treated
    # populations here share their whole mean vector, direction AND magnitude, so this lane pair
    # is the case that defeats BOTH mean scores of panel a and not only the cosine. Naming only
    # "the mean" left a reader who had just learned that ladder to guess which rung was tied.
    x_mean = _x(R_TREATED)
    ax.text(x_mean, _fy(Y_PHRASE_TOP), "same mean direction\nand magnitude",
            transform=ax.transAxes, fontsize=PT_ANNOT, ha="center", va="top", color=TEXT,
            fontweight="bold", linespacing=1.15)
    ax.plot([x_mean, x_mean], [_fy(Y_RULE_TOP), _fy(LANE_CY[-1] + DY_MEAN + 0.075)],
            ls=(0, (2.6, 2.0)), lw=LW_HAIR, color=MEAN, zorder=1)

    # Baseline, running down through all three untreated populations. Unlabelled on purpose: it
    # exists so that "the minority stayed exactly put" is a geometric fact and not a phrase.
    ax.plot([_x(R_BASE)] * 2, [_fy(LANE_CY[0] - RY_IN - 0.012), _fy(LANE_CY[-1] + RY_IN + 0.012)],
            lw=LW_HAIR, color=FAINT, zorder=0)

    # ---------------- the three lanes ----------------
    for name, phrase, cy_in, r_maj, r_min in LANES:
        y_lane = _fy(cy_in)
        # The condition column. Name and phrase stack inside the lane's own band, so the drawing
        # area carries marks only; in a 3.15 in wide panel the width for this is free, and the
        # height it would have cost under the cells is not.
        dy = _dy(DY_NAME) if phrase else 0.0
        ax.text(_fx(0.02), y_lane + dy, name, ha="left", va="center", fontsize=PT_ANNOT,
                color=TEXT, fontweight="bold")
        if phrase:
            ax.text(_fx(0.02), y_lane - dy, phrase, ha="left", va="center", fontsize=PT_ANNOT,
                    color=TEXT)
            # Where the cells came from, and what each STATE did about it. One arrow per state
            # rather than a leader per cell: the reader needs the direction and the DISTANCE, and
            # the two lanes then differ in the count of arrows as well as their length. Drug A
            # sends both states the same way, so its two arrows run parallel and the population
            # arrives intact. Drug B sends one, longer, because the majority has to overshoot to
            # hold the mean; the second arrow is simply absent, which is the whole of resistance.
            _ghost(ax, cy_in)
            for colour, dy, r in ((SHARED, DY_ARROW[0], r_maj), (POP, DY_ARROW[1], r_min)):
                if r == R_BASE:
                    continue
                arrow(ax, (_fx(X_BASE_IN + RX_IN + BRACKET_DX), y_lane + _dy(dy)),
                      (_fx(X_BASE_IN + X_SCALE_IN * r - RX_IN - 0.045), y_lane + _dy(dy)),
                      color=colour, zorder=2)

        first = len(ax.collections)
        x_mean_drawn = _lane(ax, cy_in, r_maj, r_min)
        if phrase is None:
            # The untreated lane makes no claim, so it gets no centroid; it gets the bracket that
            # defines the two states every other lane is drawn from.
            _bracket(ax, *ax.collections[first:], cy_in)
            continue
        # Below the cells rather than on them: at the frozen centroid size the diamond covers the
        # middle of a blob this small, which under Drug A is the middle of the very population it
        # stands for. Below, the same offset in both lanes, it reads against the rule instead.
        centroid(ax, x_mean_drawn, _fy(cy_in + DY_MEAN))

    # ---------------- the one response axis all three lanes are read against ----------------
    arrow(ax, (_fx(GUTTER_IN + 0.02), _fy(Y_AXIS)), (_fx(AX_W - EDGE_IN), _fy(Y_AXIS)),
          color=SHARED)
    ax.text(_fx(0.5 * (GUTTER_IN + AX_W)), _fy(Y_AXIS_LABEL), "single-cell response",
            ha="center", va="center", fontsize=PT_ANNOT, color=SUBTLE)


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


def _by_colour(ax, cy_in, *colours):
    """Every drawn cell in one lane whose mark carries one of ``colours``, as an (n, 2) array.

    The checks below read the PICTURE rather than the constants that produced it, so a lane that
    stopped landing on the rule would fail here instead of shipping under a bold claim.
    """
    from matplotlib.colors import to_hex
    want = {c.lower() for c in colours}
    got = []
    for coll in ax.collections:
        off = np.asarray(coll.get_offsets(), dtype=float)
        if off.shape[0] < 2 or to_hex(coll.get_facecolor()[0]).lower() not in want:
            continue
        if abs(off[:, 1].mean() - _fy(cy_in)) < _dy(RY_IN):
            got.append(off)
    return np.vstack(got) if got else np.empty((0, 2))


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from figstyle import apply_style
    from fig1_style import PT_TICK

    # The AXES is the size the composite gives this panel, and the rc sizes are the ones
    # fig1_assemble sets. A panel tuned at any other size is wrong in the figure that ships.
    apply_style(sizes=(PT_TITLE, PT_ANNOT, PT_TICK))
    fig = plt.figure(figsize=(AX_W, AX_H))
    ax = fig.add_axes([0, 0, 1, 1])
    draw_1b(ax)

    # 1. The minority is a fifth of the cells, exactly, so the bracket does not round.
    assert abs(round(N_CELLS * MINOR_FRAC) - N_CELLS * MINOR_FRAC) < 1e-12, N_CELLS

    # 2. Both treated lanes really do land on the rule the panel draws through them.
    means = {}
    for name, phrase, cy_in, _, _ in LANES:
        pts = _by_colour(ax, cy_in, SHARED, POP)
        assert len(pts) == N_CELLS, (name, len(pts))
        means[name] = float(pts[:, 0].mean())
    treated = [means[n] for n, p, _, _, _ in LANES if p]
    assert max(treated) - min(treated) < 1e-12, means
    assert abs(treated[0] - _x(R_TREATED)) < 1e-12, (treated, _x(R_TREATED))

    # 3. The Drug B minority sits ON the ghost, to the last decimal, and not merely near it. This
    #    is the panel's second claim, and it is the one a rigid lane correction would have broken.
    cy_b = LANES[-1][2]
    ghost = _by_colour(ax, cy_b, FAINT)
    blue = _by_colour(ax, cy_b, POP)
    assert len(ghost) == N_CELLS and len(blue) == round(N_CELLS * MINOR_FRAC), (len(ghost),
                                                                               len(blue))
    lodge = np.array([np.abs(ghost - b).sum(axis=1).min() for b in blue])
    assert lodge.max() < 1e-12, lodge.max()

    # 4. And the ghost really is the untreated population, cell for cell, rather than a second
    #    cloud that resembles it. If this ever failed, the panel would be inviting a comparison
    #    between baseline and the ghosts that its own marks do not support.
    base = _by_colour(ax, LANES[0][2], SHARED, POP)
    order = lambda a: a[np.lexsort((a[:, 1], a[:, 0]))]  # noqa: E731
    assert np.abs(order(base)[:, 0] - order(ghost)[:, 0]).max() < 1e-12
    print(f"drawn population means (axes x): { {k: round(v, 6) for k, v in means.items()} }")
    print(f"Drug B minority to ghost, worst cell: {lodge.max():.2e} axes fractions")

    print(f"smallest effective type: {_check_type(fig):.2f} pt")
    print(f"all artists inside the axes: {_check_bbox(fig, ax)}")
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "1b.png")
    fig.savefig(out, dpi=400)
    print(f"wrote {out}  (axes {AX_W} x {AX_H:.2f} in)")
