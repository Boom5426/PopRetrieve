"""PopRetrieve Figure 1, panel a: the task, and the single fork the paper is about.

WHAT THIS PANEL HAS TO SAY
--------------------------
One query population, one candidate library, one ranking machine. The only thing that differs
between the two routes is whether the query's single-cell responses are collapsed to one vector or
kept as a population, and that one difference is allowed to change the ranked list. Panel a is also
where the figure's colour vocabulary is declared: MEAN orange for the collapsed route, POP blue for
the population route, SHARED grey for everything both routes have in common.

WHY THE PANEL IS DRAWN AND NOT WRITTEN
--------------------------------------
The previous cut said all of that in labels next to arrows, which is a process sketch: correct, and
nothing in it could be seen. Four things are now structural rather than stated.

  * The query is a big cloud with two response states inside it. Nothing rings or names the states.
    Their only job is that the population visibly HAS structure, so that "population information"
    has something to refer to when the collapse throws it away.
  * The collapse is a physical contraction. A fan of leaders leaves the whole population and pinches
    into one orange diamond. Directly below, at the same scale and drawn from the SAME cells, the
    retain route carries every cell across on parallel rays and delivers the identical constellation.
    Converging versus parallel is the panel's argument, and it survives deleting every word.
  * The library is four different distributions, not four identical blobs: two states, broad, narrow,
    shifted. The dashed orange rule through them is the query mean, which is all the collapse route
    brings to the comparison; the reader can see the narrow candidate sitting exactly on it while the
    two-state candidate straddles it, which is why the two routes disagree.
  * The endpoint is two ranked stacks whose rank-1 rows are tinted and whose top two entries are
    joined by crossing hairlines. The swap is a shape on the page.

WHY THE TWO RANKINGS ARE COMPUTED, NOT TYPED
--------------------------------------------
Every population in the panel, the query and the four candidates, is one Gaussian mixture in a
single response coordinate (QUERY_STATES and CANDIDATES, below). One table draws the candidate
silhouettes AND
produces both ranked lists: the collapse ranking from |mean difference|, the population ranking from
the 1D Wasserstein distance between the full distributions. So the shapes on the page and the lists
under them cannot drift apart, and RANK_MEAN[0] != RANK_POP[0] is asserted at import rather than
asserted in the caption. Nothing here is measured; it is a construction, and the caption says so.

WHY THE LAYOUT IS THIS SHAPE
----------------------------
The axes is 3.15 x 1.60 in, landscape at about 2:1, so the pipeline runs left to right in four
stations, query -> two representations -> one library -> two rankings, and x carries the stages
while y carries only the fork. The previous portrait cut stacked the two routes as rows and put the
rankings in a table underneath; at 3.15 in wide that arrangement wastes the reading direction.

The two representations sit in ONE column at x = APEX_X: the diamond above, the retained population
directly below it. That vertical pairing is what makes the contraction measurable by eye.

WHY SUBSCRIPTS ARE COMPOSED FROM TWO ARTISTS
--------------------------------------------
Matplotlib renders a mathtext sub/superscript at 0.7x nominal, so "$d_1$" set at PT_EQ (9.3) puts
its subscript on the page at 6.51 pt, a hundredth of a point over this figure's floor and hostage to
any rounding. Writing the base at PT_EQ and the subscript as its own artist at PT_SMALL prints the
subscript at 6.5 pt exactly, which is LARGER than mathtext would set it. Nothing is shrunk to fit;
the pair is measured and set snug by _run().

Run standalone: python3 fig1a.py
"""
from __future__ import annotations

import os
import sys
from math import erf, sqrt

import numpy as np
from matplotlib.patches import FancyBboxPatch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fig1_style import (FAINT, LW_HAIR, MEAN, POP, PT_ANNOT, PT_EQ,  # noqa: E402
                        PT_SMALL, SHARED, TEXT, arrow, blank, cells, centroid, title)

# ---------------------------------------------------------------- the one response coordinate
# Every population in this panel is a Gaussian mixture of (weight, mean, sd) in one response
# coordinate, with the query's own mean at 0. This table is the panel's only free construction: it
# draws the four candidate silhouettes and it produces both ranked lists (see _rank_orders).
QUERY_STATES = ((0.5, -0.62, 0.32), (0.5, 0.62, 0.32))

# The library. Each candidate is a different KIND of population, which is the point of drawing them
# rather than listing them: a mean can describe only the third column of this table.
CANDIDATES = {
    "1": ((0.5, -0.60, 0.30), (0.5, 0.50, 0.30)),   # two states, like the query: the population match
    "2": ((1.0, 0.45, 0.70),),                      # broad, and centred off the query mean
    "3": ((1.0, 0.00, 0.34),),                      # narrow, sitting exactly on the query mean
    "4": ((1.0, 0.95, 0.34),),                      # the same width, shifted off it
}

# ---------------------------------------------------------------- layout, in axes units
# Four stations across a 3.15 x 1.60 in axes. x is the reading direction.
Q_CX, Q_CY = 0.088, 0.560   # the query population's centre
Q_MAG = 0.046               # axes-x units per response unit, for the QUERY ONLY. The query is drawn
                            # magnified because it is the one population whose internal structure has
                            # to be legible; the four candidates share one smaller scale among
                            # themselves, which is what makes "broader" and "shifted" comparable
                            # across the library. No axis is shared between the two, so no reader is
                            # invited to measure one against the other.
STATE_SPREAD = 2.6          # cells() fills a disk uniformly, so a state's drawn radius is set at
                            # 2.6 sd: the extent a Gaussian visibly occupies, not its sd.
N_CELLS = 96                # split between the states by weight; enough dots to read as a population
DX, DY = 0.230, -0.230      # query -> retained copy. The retain route is a pure translation; the
                            # rays cross the gap this leaves.
APEX_X, APEX_Y = 0.318, 0.870           # the collapsed query: one diamond
COPY_CX, COPY_CY = Q_CX + DX, Q_CY + DY  # the retained population sits DIRECTLY below the diamond,
                                        # so the two representations are one column and the eye
                                        # compares them without moving sideways
LIB_CX, LIB_HALF = 0.520, 0.078         # the candidate silhouettes' centre and half width
LIB_ROWS = (0.720, 0.570, 0.420, 0.270)  # baselines, top candidate first
LIB_H = 0.095                           # height of the tallest candidate density. The four are
                                        # normalised together, so they are four densities on one
                                        # scale: the broad one is FLATTER as well as wider, which is
                                        # the reading a per-row rescale would have thrown away.
LIB_LABEL_GAP = 0.014                   # silhouette right edge -> its d label
X_JOIN = 0.430              # where both routes' arrows stop: the library's left flank
JOIN_SPREAD = 0.014         # half the gap between the two arrowheads there. Both arrive inside the
                            # empty band between two candidate rows, so neither reads as picking a
                            # row: choosing is what the stacks are for.
RANK_PITCH = 0.135          # one rank step in the ranked stacks
RANK_HEAD_Y = 0.880         # the two stack headings, va top
RANK_RIGHT = 0.992          # right edge of the whole panel's ink
RANK_GAP = 0.030            # between the two headings; they are what sets the columns apart
CHIP_W, CHIP_H = 0.052, 0.092           # the tint behind a rank-1 entry
Y_QUERY = 0.800             # "query Q", just over the query population
Y_RETAIN = 0.170            # "retain cells", just under the population that survives the lower route
Y_COLLAPSE = 0.995          # "collapse", above the diamond
Y_LIB_HEAD = 0.990          # "candidate library", over the library column
Y_CLOSE = 0.190             # the phrase the panel exists to say, bottom right

# ---------------------------------------------------------------- drawing constants
# Per-state drawing, aligned with QUERY_STATES: y radius, y offset, marker area, alpha, seed.
# The two states differ in weight of ink and in position, never in hue: the query belongs to BOTH
# routes, so colouring one of its states POP or MEAN would hand the query to one of them. The
# offsets are a second, latent direction; only the x separation carries response units.
STATE_DRAW = ((0.100, +0.038, 3.2, 0.55, 11),
              (0.090, -0.038, 3.6, 0.90, 23))
N_FAN, N_RAYS = 14, 18      # leaders in each stream. The fan drains the population's CROWN, one
                            # cell per vertical band, so its mouth is as wide as the population and
                            # the pinch into one point is a contraction of the whole cloud. The rays
                            # leave the right FLANK, one cell per horizontal band. Drawn from a
                            # common rim instead, the two streams cross in the gap and the contrast
                            # between them, which is the panel's argument, is what gets lost.
LEAD_SPLIT = 0.020          # the rays take the flank below the population's midline; the crown above
                            # it is the fan's. The overlap is this deep, so cells near the midline
                            # send a leader BOTH ways and the cloud is seen to fork rather than split.
LEAD_ALPHA = 0.55           # leaders sit UNDER the cells, so the fan reads as coming from them
LEAD_CLEAR = 0.004          # a leader starts this far outside the population it leaves, so neither
                            # cloud is drawn through and both stay readable as populations
DIAMOND_CLEAR = 0.030       # a leader stops this far short of the diamond, so the point stays a point
SUB_DROP_EM = 0.22          # subscript baseline drop, in ems of the base size, as mathtext sets it
GRID = np.linspace(-6.0, 6.0, 24001)    # response grid for the mixture CDF; +-6 sd covers every tail
UGRID = np.linspace(0.001, 0.999, 3000)  # quantile grid for the 1D Wasserstein distance
_ERF = np.vectorize(erf)


# ---------------------------------------------------------------- the two rankings, derived
def _mean(comps):
    return float(sum(w * m for w, m, _ in comps))


def _pdf(comps, x):
    return sum(w * np.exp(-0.5 * ((x - m) / s) ** 2) / (s * sqrt(2 * np.pi)) for w, m, s in comps)


def _cdf(comps, x):
    return sum(w * 0.5 * (1.0 + _ERF((x - m) / (s * sqrt(2.0)))) for w, m, s in comps)


def _quantiles(comps):
    """The mixture's quantile function on UGRID, by inverting its CDF on a fixed grid.

    Deterministic and seedless, unlike sampling: the ranked lists this panel prints must be the same
    on every machine that rebuilds the figure.
    """
    return np.interp(UGRID, _cdf(comps, GRID), GRID)


def _rank_orders():
    """Rank the one library twice, from the table that also draws it.

    Collapse route: the distance between two collapsed populations is the distance between their
    means, which in one dimension is |mean difference|.
    Population route: the distance between the full distributions, taken as the 1D Wasserstein
    distance, the mean gap between matched quantiles. It is one member of the family panel c names.
    """
    q = _quantiles(QUERY_STATES)
    qm = _mean(QUERY_STATES)
    d_mean = {k: abs(_mean(c) - qm) for k, c in CANDIDATES.items()}
    d_pop = {k: float(np.mean(np.abs(_quantiles(c) - q))) for k, c in CANDIDATES.items()}
    return (tuple(sorted(CANDIDATES, key=d_mean.get)), tuple(sorted(CANDIDATES, key=d_pop.get)))


RANK_MEAN, RANK_POP = _rank_orders()
# The panel exists because these two disagree. If a candidate is ever retuned so that they do not,
# the panel has stopped making its point and should fail loudly rather than draw a tautology.
assert RANK_MEAN[0] != RANK_POP[0], (
    f"panel a has nothing to show: both routes rank d_{RANK_MEAN[0]} first")


# ---------------------------------------------------------------- geometry helpers
def _axes_in(ax):
    """The axes box in inches. Read from the figure so the panel is correct at any size."""
    w, h = ax.get_position().size * ax.figure.get_size_inches()
    return float(w), float(h)


def _pt2y(ax, pt):
    """Points to axes-y units."""
    return pt / 72.0 / _axes_in(ax)[1]


def _renderer(ax):
    fig = ax.figure
    fig.canvas.draw()
    return fig.canvas.get_renderer()


def _run(ax, x, y, parts, rend, ha="left", zorder=8):
    """Set a run of fragments left to right on one baseline, spaced by MEASURED width.

    ``parts`` is ((text, pt, is_subscript, colour), ...). Subscript fragments are dropped by
    SUB_DROP_EM and carry their own size, which is how this panel gets a subscript that prints at the
    figure's floor instead of at 0.7x PT_EQ. Measuring rather than hard-coding an advance keeps the
    pair snug if the fallback font is not the one this was tuned on.

    Returns the run's width in axes units.
    """
    drop = _pt2y(ax, PT_EQ * SUB_DROP_EM)
    inv = ax.transData.inverted()
    arts, cur = [], 0.0
    gid = "run-%d-%d" % (round(x * 1e4), round(y * 1e4))   # one expression, so QA can pair it up
    for txt, pt, is_sub, colour in parts:
        t = ax.text(cur, y - (drop if is_sub else 0.0), txt, ha="left", va="baseline",
                    fontsize=pt, color=colour, zorder=zorder, gid=gid)
        bb = t.get_window_extent(renderer=rend)
        cur += inv.transform((bb.x1, 0.0))[0] - inv.transform((bb.x0, 0.0))[0]
        arts.append(t)
    shift = {"left": x, "center": x - cur / 2.0, "right": x - cur}[ha]
    for t in arts:
        t.set_x(t.get_position()[0] + shift)
    return cur


def _sym_parts(base, sub):
    """One subscripted symbol, base at PT_EQ and subscript at the floor. See the module note."""
    return (("$%s$" % base, PT_EQ, False, TEXT), ("$%s$" % sub, PT_SMALL, True, TEXT))


def _text_w(ax, rend, s, pt, weight="normal"):
    """The printed width of a string in axes units, so columns can be set from measurement."""
    t = ax.text(0.0, -1.0, s, fontsize=pt, fontweight=weight)
    bb = t.get_window_extent(renderer=rend)
    inv = ax.transData.inverted()
    t.remove()
    return float(inv.transform((bb.x1, 0.0))[0] - inv.transform((bb.x0, 0.0))[0])


# ---------------------------------------------------------------- the populations
def _lobes(cx, cy):
    """The two drawn states of a population centred at (cx, cy), as (x, y, rx, ry) ellipses.

    One function, used by the drawing, by the corridor the rays cross and by the point at which a
    leader leaves the cloud, so the three can never disagree about where the population ends.
    """
    return tuple((cx + Q_MAG * mu, cy + dy, Q_MAG * sd * STATE_SPREAD, ry)
                 for (_, mu, sd), (ry, dy, _, _, _) in zip(QUERY_STATES, STATE_DRAW))


def _inside(cx, cy, px, py):
    """Is (px, py) inside the population drawn at (cx, cy): inside either of its two states."""
    return any(((px - lx) / rx) ** 2 + ((py - ly) / ry) ** 2 <= 1.0
               for lx, ly, rx, ry in _lobes(cx, cy))


def _rim_x(cx, cy, y, side):
    """Where that population ends horizontally at height y (side = -1 left, +1 right)."""
    xs = [lx + side * rx * sqrt(max(0.0, 1.0 - ((y - ly) / ry) ** 2))
          for lx, ly, rx, ry in _lobes(cx, cy) if abs(y - ly) < ry]
    return (max(xs) if side > 0 else min(xs)) if xs else cx


def _exit_t(cx, cy, p0, p1):
    """The fraction along p0 -> p1 at which the line finally leaves that population.

    Solved by walking the segment rather than by a quadratic: the population is a UNION of two
    ellipses, and the union's boundary is not a conic.
    """
    ts = np.linspace(0.0, 1.0, 240)
    pts = p0 + np.outer(ts, p1 - p0)
    inside = [i for i, (px, py) in enumerate(pts) if _inside(cx, cy, px, py)]
    return ts[max(inside)] if inside else 0.0


def _population(ax, cx, cy, colour, zorder=3):
    """One response population: two states, drawn as two overlapping lobes.

    Both calls use the same seeds, so the population the retain route delivers is the query's own
    constellation translated, not a fresh draw of the same size. "The same cells come out" is then a
    fact about the drawing, checked by the caller, rather than a claim in the caption.
    """
    xs, ys = [], []
    for (w, _, _), (_, _, s, alpha, seed), (lx, ly, rx, ry) in zip(QUERY_STATES, STATE_DRAW,
                                                                   _lobes(cx, cy)):
        x, y = cells(ax, lx, ly, int(round(N_CELLS * w)), rx, ry, color=colour,
                     rng=np.random.default_rng(seed), s=s, alpha=alpha, zorder=zorder)
        xs.append(x)
        ys.append(y)
    return np.concatenate(xs), np.concatenate(ys)


def _leaders(x, y):
    """The cells that carry a visible leader: the crown for the fan, the lower flank for the rays.

    Banding rather than sampling at random is what keeps each mouth as wide as the stream it drains;
    a random dozen cells would clump, and a fan that starts narrow has nothing to contract.
    Returns (fan, rays).
    """
    crown = np.array([b[np.argmax(y[b])]
                      for b in np.array_split(np.argsort(x), N_FAN) if len(b)])
    flank = np.array([b[np.argmax(x[b])]
                      for b in np.array_split(np.argsort(y), N_RAYS) if len(b)])
    return crown, flank[y[flank] <= Q_CY + LEAD_SPLIT]


def _collapse(ax, x, y, lead):
    """The collapse route: many cells in, one vector out, drawn as a contraction.

    Each leader starts where its own line leaves the cloud and stops short of the diamond. Both ends
    are clearances rather than decoration: a leader drawn through the population turns the cloud into
    hatching, and a leader run into the diamond turns the point into a blot. A mouth as wide as the
    population, pinching to a point that stays a point, is the whole claim.
    """
    apex = np.array([APEX_X, APEX_Y])
    for i in lead:
        p0 = np.array([x[i], y[i]])
        d = apex - p0
        step = d / np.hypot(*d)
        a = p0 + d * _exit_t(Q_CX, Q_CY, p0, apex) + step * LEAD_CLEAR
        b = apex - step * DIAMOND_CLEAR
        ax.plot([a[0], b[0]], [a[1], b[1]], color=MEAN, lw=LW_HAIR, alpha=LEAD_ALPHA,
                solid_capstyle="round", zorder=2)
    centroid(ax, APEX_X, APEX_Y, color=MEAN)


def _retain(ax, x, y, lead):
    """The retain route: many cells in, the same many cells out.

    Every ray carries one cell to its own image under the SAME vector, so the rays are parallel and
    equal in length by construction and the population that arrives is the one that left. Set against
    the fan directly above, the reader compares a shape that pinches to a point with one that does
    not change at all.
    """
    shift = np.array([DX, DY])
    for i in lead:
        p0 = np.array([x[i], y[i]])
        p1 = p0 + shift
        step = shift / np.hypot(*shift)
        a = p0 + shift * _exit_t(Q_CX, Q_CY, p0, p1) + step * LEAD_CLEAR
        b = p1 - shift * _exit_t(COPY_CX, COPY_CY, p1, p0) - step * LEAD_CLEAR
        ax.plot([a[0], b[0]], [a[1], b[1]], color=POP, lw=LW_HAIR, alpha=LEAD_ALPHA,
                solid_capstyle="round", zorder=2)
    xc, yc = _population(ax, COPY_CX, COPY_CY, POP)
    assert np.allclose(xc - x, DX) and np.allclose(yc - y, DY), (
        "the retain route must deliver the query's own cells translated, not a redraw")
    return xc, yc


# ---------------------------------------------------------------- the library
def _lib_mid():
    """The library's vertical middle: what the routes aim at and what the stacks straddle."""
    return (LIB_ROWS[-1] + LIB_ROWS[0] + LIB_H) / 2


def _lib_scale():
    """Response units -> axes-x units for the library, and where the query mean lands in it.

    The span is read off the candidate table rather than chosen, so a retuned candidate cannot
    quietly grow out of its row: the widest candidate sets the scale for all four. STATE_SPREAD is
    reused for how far a Gaussian is drawn, so a query state and a candidate tail are cut off at the
    same multiple of their own sd.
    """
    lo = min(m - STATE_SPREAD * s for c in CANDIDATES.values() for _, m, s in c)
    hi = max(m + STATE_SPREAD * s for c in CANDIDATES.values() for _, m, s in c)
    scale = 2 * LIB_HALF / (hi - lo)
    x0 = LIB_CX - LIB_HALF
    return lo, hi, scale, x0 + (_mean(QUERY_STATES) - lo) * scale


def _library(ax, rend):
    """One library, shared, and four populations that differ in ways a mean cannot describe.

    They are drawn as densities on ONE scale, so two states, broad, narrow and shifted are four
    visibly different objects rather than four blobs with different labels. The dashed rule is the
    query mean, in MEAN orange because a mean is all the collapse route carries here: the narrow
    candidate sits exactly on it while the two-state candidate straddles it, which is the mechanism
    behind the disagreement in the stacks, drawn instead of asserted.
    """
    lo, hi, scale, x_mu = _lib_scale()
    xs = np.linspace(lo, hi, 400)
    peak = max(float(_pdf(c, xs).max()) for c in CANDIDATES.values())
    x_ax = (LIB_CX - LIB_HALF) + (xs - lo) * scale

    ax.plot([x_mu, x_mu], [LIB_ROWS[-1] - 0.010, LIB_ROWS[0] + LIB_H + 0.014], color=MEAN,
            lw=LW_HAIR, ls=(0, (2.0, 1.6)), alpha=0.85, zorder=2)
    for name, y0 in zip(CANDIDATES, LIB_ROWS):
        h = y0 + LIB_H * _pdf(CANDIDATES[name], xs) / peak
        ax.fill_between(x_ax, y0, h, color=SHARED, alpha=0.28, lw=0, zorder=3)
        ax.plot(x_ax, h, color=SHARED, lw=LW_HAIR, zorder=4)
        ax.plot([x_ax[0], x_ax[-1]], [y0, y0], color=FAINT, lw=LW_HAIR, zorder=3)
        _run(ax, LIB_CX + LIB_HALF + LIB_LABEL_GAP, y0 + 0.010, _sym_parts("d", name), rend)


# ---------------------------------------------------------------- the two rankings
def _rankings(ax, rend):
    """The endpoint: the same four candidates, ranked twice, disagreeing at rank 1.

    The columns are placed from the MEASURED width of their headings, because "Population" is nearly
    twice "Mean" and a pair of hard-coded centres would either collide or drift apart under a
    different fallback font.
    """
    w_pop = _text_w(ax, rend, "Population", PT_ANNOT, "bold")
    w_mean = _text_w(ax, rend, "Mean", PT_ANNOT, "bold")
    x_pop = RANK_RIGHT - w_pop / 2
    x_mean = x_pop - w_pop / 2 - RANK_GAP - w_mean / 2
    mid = _lib_mid()
    rows = [mid + (1.5 - i) * RANK_PITCH for i in range(len(CANDIDATES))]

    # One library, ranked twice: the machinery both routes share, so the arrow into it is SHARED.
    # It starts at the silhouettes' edge rather than past the d labels: the arrow rides the empty
    # band between two candidate rows, where the label column has nothing in it, and the run it wins
    # that way is what stops it reading as a stray arrowhead.
    arrow(ax, (LIB_CX + LIB_HALF + 0.016, mid), (x_mean - w_mean / 2 - 0.016, mid), color=SHARED)

    for x, head, order, colour in ((x_mean, "Mean", RANK_MEAN, MEAN),
                                   (x_pop, "Population", RANK_POP, POP)):
        ax.text(x, RANK_HEAD_Y, head, transform=ax.transAxes, fontsize=PT_ANNOT, ha="center",
                va="top", color=TEXT, fontweight="bold")
        # Rank 1 is tinted in the route's own colour, so the eye lands on the two top rows and finds
        # different names in them. The letters stay INK: colour travels through marks, not type.
        ax.add_patch(FancyBboxPatch((x - CHIP_W / 2, rows[0] - CHIP_H / 2), CHIP_W, CHIP_H,
                                    boxstyle="round,pad=0,rounding_size=0.012",
                                    fc=colour, ec="none", alpha=0.22, zorder=1))
        for name, yy in zip(order, rows):
            _run(ax, x, yy - 0.014, _sym_parts("d", name), rend, ha="center")

    # Every candidate the two routes place differently is joined across the columns, so the crossing
    # is drawn from the disagreement rather than from a pair of names typed in here. FAINT, because
    # it is structure to be seen rather than a mark to be read.
    for name in CANDIDATES:
        y0, y1 = rows[RANK_MEAN.index(name)], rows[RANK_POP.index(name)]
        if y0 == y1:
            continue
        ax.plot([x_mean + CHIP_W / 2 + 0.004, x_pop - CHIP_W / 2 - 0.004], [y0, y1],
                color=FAINT, lw=LW_HAIR, zorder=1)


# ---------------------------------------------------------------- the panel
def draw_1a(ax):
    """Draw panel a into ``ax``. The axes is 3.15 x 1.60 in in the composite."""
    blank(ax)
    rend = _renderer(ax)

    xq, yq = _population(ax, Q_CX, Q_CY, SHARED)
    fan, rays = _leaders(xq, yq)
    _collapse(ax, xq, yq, fan)
    _retain(ax, xq, yq, rays)
    _library(ax, rend)
    _rankings(ax, rend)

    # Both routes reach for the same library, so the two arrows converge on one flank of it. They
    # stop in the empty band between two candidate rows: an arrowhead level with a row would read as
    # that route choosing that candidate, which is the stacks' job and not the library's.
    mid = _lib_mid()
    arrow(ax, (APEX_X + 0.026, APEX_Y - 0.026), (X_JOIN, mid + JOIN_SPREAD), color=MEAN)
    # The lower arrow leaves the copy's upper shoulder rather than its side, so it climbs to the
    # library at the angle its partner descends at instead of standing vertically under it.
    y_out = COPY_CY + 0.105
    arrow(ax, (_rim_x(COPY_CX, COPY_CY, y_out, +1) + 0.010, y_out),
          (X_JOIN, mid - JOIN_SPREAD), color=POP)

    # Every name sits against the thing it names, on the side that stream is not using: no label has
    # to be traced back across the panel to find its glyph.
    ax.text(0.0, Y_QUERY, "query Q", transform=ax.transAxes, fontsize=PT_ANNOT,
            ha="left", va="top", color=TEXT)
    ax.text(COPY_CX, Y_RETAIN, "retain cells", transform=ax.transAxes, fontsize=PT_ANNOT,
            ha="center", va="top", color=TEXT, fontweight="bold")
    ax.text(APEX_X, Y_COLLAPSE, "collapse", transform=ax.transAxes, fontsize=PT_ANNOT,
            ha="center", va="top", color=TEXT, fontweight="bold")
    ax.text(LIB_CX, Y_LIB_HEAD, "candidate\nlibrary", transform=ax.transAxes, fontsize=PT_ANNOT,
            ha="center", va="top", color=TEXT, linespacing=1.15)
    title(ax, "same library,\ndifferent ranking", x=RANK_RIGHT, y=Y_CLOSE, ha="right", va="top",
          linespacing=1.15)
    return ax


if __name__ == "__main__":
    import re

    import matplotlib
    matplotlib.use("agg")
    import matplotlib.pyplot as plt
    import matplotlib.text as mtext
    from matplotlib.collections import Collection
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    from matplotlib.transforms import Bbox

    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from figstyle import apply_style
    from fig1_style import PT_FLOOR, PT_TICK, PT_TITLE

    # EXACTLY the axes the composite gives this panel: 3.15 x 1.60 in with no subplot margins.
    # A panel tuned at another size is wrong in the figure that ships.
    AXW, AXH = 3.150, 1.600
    apply_style(sizes=(PT_TITLE, PT_ANNOT, PT_TICK))
    fig, ax = plt.subplots(figsize=(AXW, AXH))
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    draw_1a(ax)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "1a.png")
    fig.savefig(out, dpi=400, bbox_inches=Bbox([[0.0, 0.0], [AXW, AXH]]), pad_inches=0.0)

    # ---- gate 1: nothing prints below this figure's 6.5 pt floor -------------------------
    subsup = re.compile(r"\$[^$]*[\^_][^$]*\$")
    sizes = []
    for t in fig.findobj(mtext.Text):
        s = str(t.get_text())
        if not s.strip() or not t.get_visible():
            continue
        sizes.append((t.get_fontsize() * (0.7 if subsup.search(s) else 1.0), s[:30]))
    worst = min(sizes)
    assert worst[0] >= PT_FLOOR - 1e-6, f"below the {PT_FLOOR} pt floor: {worst}"

    # ---- gate 2: nothing hangs outside the axes rect -------------------------------------
    rend = fig.canvas.get_renderer()
    axbb = ax.get_window_extent(renderer=rend)
    skip = {ax.patch, *ax.spines.values()}
    over = []
    for art in ax.get_children():
        if art in skip or not art.get_visible():
            continue
        if not isinstance(art, (mtext.Text, Line2D, Collection, Patch)):
            continue
        if isinstance(art, mtext.Text) and not str(art.get_text()).strip():
            continue
        bb = art.get_tightbbox(rend)
        if bb is None:
            continue
        d = max(axbb.x0 - bb.x0, bb.x1 - axbb.x1, axbb.y0 - bb.y0, bb.y1 - axbb.y1)
        if d > 0.5:                       # half a device pixel of tolerance on the rect itself
            label = str(art.get_text())[:28] if isinstance(art, mtext.Text) else type(art).__name__
            over.append((round(d / fig.dpi * 72, 2), label,
                         [round(axbb.x0 - bb.x0, 1), round(bb.x1 - axbb.x1, 1),
                          round(axbb.y0 - bb.y0, 1), round(bb.y1 - axbb.y1, 1)]))
    for row in sorted(over, reverse=True):
        print(f"  OUTSIDE by {row[0]} pt  {row[1]!r}  [L,R,B,T px] {row[2]}")
    assert not over, f"{len(over)} artist(s) leave the axes; they would widen the composite"

    # ---- gate 3: no two text artists overlap ---------------------------------------------
    labels = [t for t in ax.get_children()
              if isinstance(t, mtext.Text) and str(t.get_text()).strip()]
    clashes = []
    for i, a in enumerate(labels):
        for b in labels[i + 1:]:
            # Fragments of one expression are meant to touch: a subscript sits against its base.
            if a.get_gid() is not None and a.get_gid() == b.get_gid():
                continue
            ba, bb2 = a.get_tightbbox(rend), b.get_tightbbox(rend)
            if ba is None or bb2 is None:
                continue
            ov = min(ba.x1, bb2.x1) - max(ba.x0, bb2.x0), min(ba.y1, bb2.y1) - max(ba.y0, bb2.y0)
            if min(ov) > 0.5:
                clashes.append((round(min(ov), 1), str(a.get_text())[:18], str(b.get_text())[:18]))
    for c in sorted(clashes, reverse=True):
        print(f"  OVERLAP {c[0]} px: {c[1]!r} / {c[2]!r}")
    assert not clashes, f"{len(clashes)} overlapping label pair(s)"

    print(f"wrote {out}  ({AXW} x {AXH} in axes)")
    print(f"mean ranking  d_{'  d_'.join(RANK_MEAN)}")
    print(f"pop  ranking  d_{'  d_'.join(RANK_POP)}")
    print(f"smallest effective text size: {worst[0]:.2f} pt  ({worst[1]!r})")
    print(f"text artists: {len(sizes)}   all inside the axes: True")
