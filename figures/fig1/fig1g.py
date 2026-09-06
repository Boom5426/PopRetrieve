"""PopRetrieve Figure 1 panel 1g: the population representation contains the mean as a limit.

WHAT THE LIMIT ACTUALLY IS, AND WHAT IT IS NOT
----------------------------------------------
At lambda = 0 the population distance equals ``two_dmu``, and exp06 defines that as 2||mu_P -
mu_T||: TWICE the Euclidean distance between the two means. The factor of two is what the energy
distance between two point masses carries (Methods), it is constant in lambda, and it cannot
reorder candidates, so the panel draws the limit as PROPORTIONAL to the mean-only distance rather
than equal to it. Saying "equal" here is the one thing this panel must not do, because the
Methods state the constant explicitly and the two would then contradict each other. So the endpoint of this curve is the
magnitude-aware mean score of panel a, and it is not the cosine. The cosine discards the length
of that difference, so it is a further coarsening of the mean and not the limit of anything drawn
here. The panel said "mean retrieval is the zero-variance limit" until 2026-09-03, which left a
reader to attach the identity to whichever mean score they had in mind, and the one most of them
have in mind is the CMap-style cosine. The correct statement is about the REPRESENTATION: a
population contains its own mean as its zero-variance limit, and which score reads that mean is a
separate choice (panel a).

WHAT THE PANEL HAS TO MAKE VISIBLE
----------------------------------
Contract the residual of two response populations by a scale lambda: at lambda = 0 the population
distance IS the mean-only distance, up to that constant factor, and it falls away from it as
variation is restored.
The identity was never in doubt; the reading was. The claim is geometric, so the panel has to be geometric: one horizontal orange rule
for what means alone can see, one blue curve for what the population sees, and a gap between them
that closes to nothing at a single point. A reader who takes only the shape away has taken the
claim away, and the caption does not have to rescue it.

THE AXIS RUNS 0 ON THE LEFT TO 1 ON THE RIGHT, WHICH IS A FIX
-------------------------------------------------------------
The 2026-08-30 cut ran lambda from 1 down to 0 so that the limit landed at the end of the reading
direction. That was backwards for everything else about the panel. It put the zero of a scale on
the right, and it made the curve climb INTO the rule, so the reader met the mean-only case last,
as a destination, when it is the panel's starting premise: mean retrieval is the degenerate corner
you begin from and then leave. Running 0 -> 1 puts the collapsed endpoint at the origin, where a
reader looks first, and the curve then descends away from the rule as variation is restored. The
growing wedge between the two IS "what the mean cannot see", and it grows in the direction of
reading. Both ends of the axis are named for what they are, not only numbered, because "0" and "1"
of a residual scale mean nothing to a reader arriving from panel f.

THE STRIP IS BOUND TO THE CURVE, NOT STACKED ON IT
--------------------------------------------------
Three population glyphs sit directly over the three x positions they describe, each on its own
hairline guide, so the cartoon and the measurement are one explanation read vertically:

    lambda = 0    two populations collapsed onto their centroids: no cells left, only means
    lambda = 0.5  the same two samples, contracted off each other, no longer overlapping
    lambda = 1    the same two samples at full spread, visibly overlapping

The two orange centroids never move and the dashed orange segment between them is the same length
in all three glyphs, because the construction (src/experiments/exp06_theory_limits.py) is
P(lambda) = mu_P + lambda (P - mu_P): the mean is fixed and only the residual moves. That segment
is the cartoon's version of the flat orange rule below it, seen end on, and a reader who notices
the three are identical has read why the rule is flat without being told.

The glyphs are drawn with the figure's own cells() and centroid(), so they are recognisably the
same objects as in panels a to d. Query cells are SHARED grey and candidate cells are POP blue:
the vocabulary assigns the query to SHARED, and two colours are what make two heavily overlapping
populations still read as two at lambda = 1. The pair is laid out left-to-right rather than
stacked, because the strip is 2.67 in wide and 0.78 in tall and a vertical pair would have to
share both its axis and its ink with the vertical guide that binds it to the curve.

MEASURED, AND DEMOTED ON PURPOSE
--------------------------------
Source: results/exp06_theory_limits/degenerate_limit_synthetic.csv, rows prop1_spread. t_spread is
lambda, energy is the population distance, two_dmu is the constant mean-only endpoint. Nothing is
typed in, including the y window, which is solved backwards from the two numbers the file holds so
the reserved bands stay reserved whatever the file says next.

The agreement of the two floats verifies an analytic identity (Methods), not a biological result,
so it is printed once, at PT_SMALL, in SUBTLE, in a corner: "98.50 = 98.50", both sides read from
the file. The panel's assertion is the geometry above it. The old cut promoted that agreement to
an annotation and set the formal statement in mathtext next to it; both are gone, and the wedge
closing to a point says the same thing without a glyph of type.

Run standalone: python3 fig1g.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fig1_style import (FAINT, LW_HAIR, LW_LINE, MEAN, POP, PT_ANNOT,  # noqa: E402
                        PT_SMALL, PT_TICK, SHARED, SUBTLE, TEXT, blank, cells,
                        centroid)

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CSV = os.path.join(REPO, "results", "exp06_theory_limits", "degenerate_limit_synthetic.csv")

# The axes this panel is given in the composite, in inches. Needed here and not only in the
# preview: the cartoon's clouds are sized on the PAGE, so their unit radii depend on the strip's
# aspect, and the glyph spacing has to be checked against the strip's actual width.
AX_W, AX_H = 2.67, 0.71
TOP_W, TOP_H = 2.67, 0.78

# ------------------------------------------------------------------ curve axes
# Padded symmetrically in lambda so the two endpoint glyphs are drawn clear of the strip's edges;
# see the assertion below, which is what actually fixes this number.
X_PAD = 0.14
XLIM = (-X_PAD, 1.0 + X_PAD)
# The y window is SOLVED from the data, not chosen: the mean-only rule is pinned at F_RULE and the
# lowest measured point at F_FLOOR, which reserves a band above the rule for its label and a band
# under the curve for the identity note. Written as fractions, those bands survive the file
# changing; written as y limits, they would silently stop being bands.
F_RULE, F_FLOOR = 0.825, 0.185
TICK_STEP = 30.0            # three ticks across a 0.71 in axes: a scale, without a ladder
MS_POINT = 2.6              # the measured lambda grid: present, not what is being read
MS_LIMIT = 4.6              # lambda = 0 is where the claim lands, so it is the one enlarged mark
# The wedge is a wash, not a third mark: POP at this alpha over white is lighter than FAINT, so
# the gap is visible without ever competing with the two lines that bound it.
WEDGE_ALPHA = 0.11

# ------------------------------------------------------------------ cartoon strip
GLYPH_LAMBDA = (0.0, 0.5, 1.0)
# Derived from XLIM rather than written out again: the glyphs sitting over their own x positions is
# the thing that ties the cartoon to the measurement, and a second copy of these numbers would let
# that alignment drift the first time the limits are touched.
GLYPH_X = tuple((lm - XLIM[0]) / (XLIM[1] - XLIM[0]) for lm in GLYPH_LAMBDA)
PAIR_DX = 0.215             # in, mean-to-mean distance: FIXED, identical in all three glyphs
RX1, RY1 = 0.160, 0.155     # in, cloud radii at lambda = 1
CELL_R = 0.015              # in, half a cell marker: real ink, so it counts against the edges
# The binding constraint is horizontal, not vertical: the outer glyphs are centred on lambda = 0
# and lambda = 1, which sit X_PAD from the strip's edges, and a cloud may not cross one.
assert min(GLYPH_X) * TOP_W >= PAIR_DX / 2 + RX1 + CELL_R, "the left glyph leaves the strip"
assert (1 - max(GLYPH_X)) * TOP_W >= PAIR_DX / 2 + RX1 + CELL_R, "the right glyph leaves the strip"
CY = 0.400                  # strip units, cloud centre height: clear of the title and the guides
N_CELL = 22                 # enough to read as a population at 0.32 in across
# Re-seeded per glyph, so all three glyphs draw the SAME two samples at three scales. If they were
# three draws the reader would be looking at sampling noise with no way to tell it from lambda.
SEED_QUERY, SEED_CAND = 546, 323
# centroid()'s 34 pt^2 default is sized for the 3.00 in schematics of rows 1 and 2. Here it would
# be as wide as the cloud it summarises; at 12 pt^2 it is a point inside one. Shape, fill and
# colour stay the helper's.
CENTROID_S = 12
GUIDE_TOP = 0.17            # strip units, where the guides start: below the clouds, not through


def _limit_curve():
    """lambda ascending, the population distance at each lambda, and the mean-only endpoint."""
    d = pd.read_csv(CSV)
    sp = (d[d["prop"] == "prop1_spread"].dropna(subset=["t_spread"])
          .sort_values("t_spread"))
    two_dmu = sp["two_dmu"].to_numpy(dtype=float)
    # The rule is drawn as a single constant, so the file has to actually hold a constant; a
    # per-row endpoint would make the rule a summary rather than the quantity it claims to be.
    assert np.allclose(two_dmu, two_dmu[0]), f"two_dmu is not constant in {CSV}"
    lam = sp["t_spread"].to_numpy(dtype=float)
    energy = sp["energy"].to_numpy(dtype=float)
    assert set(GLYPH_LAMBDA) <= set(lam), f"{CSV} has no rows at lambda = {GLYPH_LAMBDA}"
    return lam, energy, two_dmu[0]


def _window(energy, two_dmu):
    """The y limits that put the rule at F_RULE and the lowest measured point at F_FLOOR."""
    span = (two_dmu - energy.min()) / (F_RULE - F_FLOOR)
    lo = energy.min() - F_FLOOR * span
    return lo, lo + span


def _glyph(ax, cx, lam):
    """One population pair at residual scale ``lam``: two clouds contracting onto two fixed means.

    ``cx`` is an axes fraction and the radii are inches, so a glyph is round on the page rather
    than round in the strip's unit box, which is 3.4 times wider than it is tall.
    """
    dx = PAIR_DX / 2.0 / TOP_W
    for sign, seed, colour in ((-1, SEED_QUERY, SHARED), (+1, SEED_CAND, POP)):
        if lam > 0:
            cells(ax, cx + sign * dx, CY, N_CELL, RX1 * lam / TOP_W, RY1 * lam / TOP_H,
                  color=colour, rng=np.random.default_rng(seed))
    # The mean-to-mean distance, identical in all three glyphs: the flat orange rule below, seen
    # end on. Drawn over the cells, because at lambda = 1 it runs through both of them.
    ax.plot([cx - dx, cx + dx], [CY, CY], lw=LW_HAIR, ls="--", color=MEAN, zorder=5,
            dash_capstyle="butt")
    centroid(ax, cx - dx, CY, size=CENTROID_S)
    centroid(ax, cx + dx, CY, size=CENTROID_S)


def draw_1g(ax, ax_top):
    lam, energy, two_dmu = _limit_curve()
    y_lo, y_hi = _window(energy, two_dmu)

    # ---------------------------------------------------------------- cartoon strip
    blank(ax_top)
    # No phrase: the caption says that the population representation contains its own mean as
    # the zero-variance limit, and that the endpoint is the mean-to-mean EUCLIDEAN distance, so
    # the magnitude-aware mean score rather than the cosine. The panel shows the wash closing to
    # nothing at lambda = 0; the naming of the endpoint is argued where it can be qualified.
    # Provenance, in the panel's own top corner and at the floor: this is a construction, and a
    # reader must not carry it away as a measurement on cells. It never becomes a claim, so it is
    # SUBTLE and it is the smallest thing here.
    ax_top.text(1.0, 0.99, "Synthetic\nconstruction", ha="right", va="top",
                fontsize=PT_SMALL, color=SUBTLE, linespacing=1.15)

    for cx, lm in zip(GLYPH_X, GLYPH_LAMBDA):
        _glyph(ax_top, cx, lm)
        # The guide starts BELOW the cloud rather than at the centroids: run through the glyph it
        # would cross the orange mean-to-mean segment at its midpoint and make a plus sign of it.
        ax_top.plot([cx, cx], [GUIDE_TOP, 0.0], lw=LW_HAIR, color=FAINT, zorder=1,
                    solid_capstyle="butt")

    # ---------------------------------------------------------------- curve axes
    # The same three guides, continued from the top of the curve axes down to the point each glyph
    # describes. The 0.10 in gap between the two axes is the only break in them, and the eye closes
    # it; drawing them across the gap would mean an artist outside its axes.
    for cx, lm in zip(GLYPH_X, GLYPH_LAMBDA):
        ax.plot([lm, lm], [y_hi, energy[lam == lm][0]], lw=LW_HAIR, color=FAINT, zorder=1,
                solid_capstyle="butt")

    # The wedge is the panel's argument: everything the population score sees that the mean-only
    # score cannot. It opens as variation is restored and closes to a point at lambda = 0, which is
    # the identity, drawn rather than asserted. A wash, so it never competes with the two lines.
    ax.fill_between(lam, energy, two_dmu, color=POP, alpha=WEDGE_ALPHA, lw=0, zorder=2)
    # dash_capstyle butt: a projecting cap puts the rule's ink past the spine, which widens the
    # composite by the linewidth on both sides for no visible gain.
    ax.axhline(two_dmu, ls="--", lw=LW_HAIR, color=MEAN, zorder=3, dash_capstyle="butt")
    ax.plot(lam, energy, "-", color=POP, lw=LW_LINE, zorder=4)
    # The enlarged mark is selected by VALUE, not by position in the sorted array: which end of
    # that array holds the limit is decided by a sort argument thirty lines away, and the one point
    # this panel exists to show is not a thing to leave to that.
    at_limit = lam == lam.min()
    ax.plot(lam[~at_limit], energy[~at_limit], "o", color=POP, ms=MS_POINT, zorder=4)
    ax.plot(lam[at_limit], energy[at_limit], "o", color=POP, ms=MS_LIMIT, mec="white",
            mew=0.7, zorder=6)

    # The rule is named directly, in the widest span the guides leave clear: 0.87 in of type in
    # the 1.04 in between the lambda = 0.5 and lambda = 1 guides, so no guide runs through it. It
    # is the only in-plot label; the curve is named by the y axis and the ends by the x ticks.
    ax.text((GLYPH_X[1] + GLYPH_X[2]) / 2, 0.998, "2 \u00d7 distance between means",
            transform=ax.transAxes,
            ha="center", va="top", fontsize=PT_ANNOT, color=TEXT)
    # The identity, verified and demoted: an analytic check (Methods), both sides read from the
    # file, in the corner the curve has left empty. A reader who never reads it has read the panel.
    #
    # It named its two sides only from 2026-09-04. It printed "98.50 = 98.50", which is a true
    # statement about nothing: two identical numbers with no subject, in grey, in a corner. A
    # reader who did read it learned less than one who did not, which is the opposite of demoted.
    # Both sides are now named in the words already on the panel, the y axis and the dashed rule,
    # and the number is printed once because the two sides are equal, which is the whole point.
    ax.text(0.012, 0.02,
            f"at λ = 0, population distance = 2 × distance between means = "
            f"{energy[at_limit][0]:.2f}",
            transform=ax.transAxes, ha="left", va="bottom", fontsize=PT_SMALL, color=SUBTLE)

    ax.set_xlim(*XLIM)
    ax.set_ylim(y_lo, y_hi)
    ax.set_xticks(list(GLYPH_LAMBDA))
    # The ends are named, not only numbered: "0" and "1" of a residual scale say nothing on their
    # own, and these two words are what the strip's outer glyphs are showing.
    ax.set_xticklabels(["0\nmean only", "0.5", "1\nfull spread"], linespacing=1.02)
    # Ticks are stepped from the window rather than listed, so they cannot outlive the data.
    ax.set_yticks(np.arange(np.ceil(y_lo / TICK_STEP), y_hi / TICK_STEP) * TICK_STEP)
    ax.tick_params(labelsize=PT_TICK, pad=1.2)
    ax.set_xlabel("residual scale λ", fontsize=PT_ANNOT, labelpad=0.5)
    # Two lines: "population distance" set on one is 1.10 in of type on a 0.71 in axes, and a
    # rotated label that long hangs into the cartoon strip above and the x labels below.
    ax.set_ylabel("population\ndistance", fontsize=PT_ANNOT, labelpad=1.5, linespacing=1.15)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)


if __name__ == "__main__":
    import re

    import matplotlib.text as mtext
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from figstyle import apply_style, pin_canvas, soften_axes
    from fig1_style import PT_FLOOR, PT_TITLE

    # The composite's own geometry for panel g (fig1_assemble.py, four rows of two): 0.46 in of y
    # furniture beside the axes, 0.37 in under the curve for the x labels, 0.10 in between the two
    # axes. A position tuned against these is the position the panel ships with.
    Y_FURNITURE, DATA_BELOW, GAP, PAD = 0.46, 0.37, 0.10, 0.06
    FW = Y_FURNITURE + AX_W + PAD
    FH = PAD + TOP_H + GAP + AX_H + DATA_BELOW

    apply_style(sizes=(PT_TITLE, PT_ANNOT, PT_TICK))
    fig = plt.figure(figsize=(FW, FH))
    # apply_style pins savefig.bbox="tight", which would crop the preview to its ink and save a
    # different canvas from the one the assertions below measure. pin_canvas makes tight == canvas.
    pin_canvas(fig)
    ax_top = fig.add_axes([Y_FURNITURE / FW, 1.0 - (PAD + TOP_H) / FH, TOP_W / FW, TOP_H / FH])
    ax = fig.add_axes([Y_FURNITURE / FW, DATA_BELOW / FH, AX_W / FW, AX_H / FH])
    draw_1g(ax, ax_top)
    soften_axes(fig)
    fig.canvas.draw()
    rend = fig.canvas.get_renderer()

    # ---- 1. type floor, scored the way fig1_assemble scores it ------------------------------
    subsup = re.compile(r"\$[^$]*[\^_][^$]*\$")
    sizes = []
    for t in fig.findobj(mtext.Text):
        s = str(t.get_text())
        if not s.strip() or not t.get_visible():
            continue
        sizes.append((t.get_fontsize() * (0.7 if subsup.search(s) else 1.0),
                      s.replace("\n", " / ")[:34]))
    worst = min(sizes)
    assert worst[0] >= PT_FLOOR - 1e-6, f"under the {PT_FLOOR} pt floor: {sorted(sizes)[:4]}"
    print(f"smallest effective size: {worst[0]:.2f} pt  ({worst[1]!r})")

    # ---- 2. containment ---------------------------------------------------------------------
    # Tick labels and axis labels live in the furniture bands the composite reserves for them
    # (0.46 in left, 0.37 in below), so they are measured against those budgets instead of against
    # the axes rect. Everything else must sit inside the axes it was drawn into.
    hangs, furniture = [], set()
    for a, name in ((ax_top, "ax_top"), (ax, "ax")):
        box = a.get_window_extent()
        art = list(a.texts) + list(a.lines) + list(a.collections) + list(a.patches)
        if a.axison:                       # blank() axes keep visible tick Texts they never draw
            furn = (list(a.get_xticklabels()) + list(a.get_yticklabels())
                    + [a.xaxis.label, a.yaxis.label])
            furniture |= {id(o) for o in furn}
            art += furn
        for o in art:
            if not o.get_visible() or (isinstance(o, mtext.Text) and not str(o.get_text()).strip()):
                continue
            bb = o.get_window_extent(renderer=rend) if isinstance(o, mtext.Text) \
                else o.get_tightbbox(rend)
            if bb is None:
                continue
            out = dict(left=(box.x0 - bb.x0), right=(bb.x1 - box.x1),
                       below=(box.y0 - bb.y0), above=(bb.y1 - box.y1))
            over = {k: v / fig.dpi for k, v in out.items() if v > 0.5}   # 0.5 px of ink
            if over:
                label = str(o.get_text())[:22] if isinstance(o, mtext.Text) else type(o).__name__
                hangs.append((name, label, id(o) in furniture,
                              {k: round(v, 3) for k, v in over.items()}))

    for name, label, is_furniture, over in hangs:
        kind = "furniture" if is_furniture else "IN-PANEL"
        print(f"  outside {name} [{kind}] {label!r}: " +
              ", ".join(f"{k} {v:+.3f} in" for k, v in over.items()))
    assert not [h for h in hangs if not h[2]], "in-panel artist leaves its axes; pull it back in"
    for _, label, _, over in hangs:
        assert over.get("left", 0) <= Y_FURNITURE, f"{label!r} overruns the y-furniture band"
        assert over.get("below", 0) <= DATA_BELOW, f"{label!r} overruns the x-furniture band"
        assert over.get("right", 0) <= PAD and over.get("above", 0) <= PAD, \
            f"{label!r} would widen the composite: {over}"
    print("containment: every in-panel artist inside its axes; furniture within its budget")

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "1g.png")
    fig.savefig(out, dpi=400)
    print(f"wrote {out}  (axes {AX_W} x {AX_H} in, strip {TOP_W} x {TOP_H} in)")
