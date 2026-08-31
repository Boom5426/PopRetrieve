"""PopRetrieve Figure 1 panel 1g: mean retrieval is the zero-variance limit, not a rival method.

WHAT THIS PANEL HAS TO DO THAT THE OLD ONE DID NOT
--------------------------------------------------
The measurement was never in doubt: contract the residual of two response populations by a scale
lambda and the population distance rises to meet the mean-to-mean distance, exactly, at lambda = 0.
What failed was the reading. Drawn as a lone curve with a dashed rule, it looked like one more
synthetic result, and nothing on it said that the x axis is the same collapse that panels a to d
draw with cells and centroids. A reader arriving from c had to be told in the caption that the
axis they were looking at was the operator they had just been shown.

So the panel is two axes. The strip on top is the schematic: the SAME two populations at three
values of lambda, drawn with the figure's own cells() and centroid() so they are recognisably the
same objects as in a, b, c and d, contracting onto the two centroids that never move. The curve
below is the measurement of exactly that. The three glyphs sit over the three x ticks they
correspond to, which is why the x axis runs 1 -> 0 rather than the conventional 0 -> 1: the
reading direction and the direction of the limit are made the same, and the claim, the meeting of
blue and orange, lands at the end of the line rather than in the middle of it.

WHY THE MEANS ARE DRAWN IN THE SAME PLACE THREE TIMES
-----------------------------------------------------
The construction (src/experiments/exp06_theory_limits.py) is P(lambda) = mu_P + lambda (P - mu_P).
The mean is fixed by construction and only the residual moves, which is the whole reason the
orange rule in the curve is flat. Drawing the two orange centroids at identical positions in all
three glyphs, with a dashed orange hairline between them of identical length, states that in the
cartoon; a reader who sees it does not need to be told the dashed rule is constant.

Query cells are SHARED grey and candidate cells are POP blue, per the frozen vocabulary, which is
also what makes two heavily overlapping populations readable as two at 0.19 in across. A fifth
colour is not available and was not needed.

MEASURED. Source: results/exp06_theory_limits/degenerate_limit_synthetic.csv, rows prop1_spread.
t_spread is lambda, energy is the population distance, two_dmu is the mean-to-mean endpoint. The
panel hard-codes none of them, including the two numbers in the agreement line.

The agreement is an analytic identity (Methods), so the panel reports it as verification and not
as a result: PT_SMALL, in SUBTLE, at the bottom, under a curve whose shape is the actual claim.
The two floats agree to 6 significant figures (98.50160 against 98.50164, a relative difference of
4e-7, which is float noise on an identity), and both sides are printed from the file.

SUBSCRIPTS ARE COMPOSED, NOT SET AS MATHTEXT
--------------------------------------------
PT_EQ cannot carry a mathtext subscript in this figure. fig1_assemble._assert_floor scores a
mathtext sub/superscript at 0.7x nominal against PT_FLOOR = 6.5, and 9.0 x 0.7 = 6.3, so
"$D_{\\mathrm{pop}}$" set at PT_EQ fails the build; the floor would need PT_EQ >= 9.29 to admit
one. fig1_style has no such token and this module may not add one, so the panel's one equation is
laid out as fragments: the base at PT_EQ and each subscript as its own Text at PT_SMALL, the
figure's floor. Panel c resolves the same conflict the same way, which is why it is done here
rather than by spelling the subscripts out as words.

Run standalone: python3 fig1g.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.textpath import TextToPath

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fig1_style import (LW_HAIR, LW_LINE, MEAN, POP, PT_ANNOT, PT_EQ,  # noqa: E402
                        PT_SMALL, PT_TICK, SHARED, SUBTLE, TEXT, blank, cells,
                        centroid, title)

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CSV = os.path.join(REPO, "results", "exp06_theory_limits", "degenerate_limit_synthetic.csv")

# The axes this panel is given in the composite, in inches. Kept here because the cartoon's cell
# clouds are drawn round on the PAGE, which needs the strip's aspect, not its unit box.
AX_W, AX_H = 0.896, 1.95
TOP_W, TOP_H = 0.896, 1.00

# ------------------------------------------------------------------ curve axes
# x runs 1 -> 0 so the strip's three glyphs sit over the ticks they describe, and so the limit is
# reached at the end of the reading direction. The 0.15 pads are what put lambda = 1 and lambda = 0
# at 0.115 and 0.885 of the axes, which is exactly where the outer two glyphs can be centred and
# still fit; a tighter pad puts the glyphs off their ticks or their cells outside the strip.
XLIM = (1.15, -0.15)
# Headroom above the orange rule for the provenance line, and a clear band under the curve for the
# agreement line. Neither band is decoration: without them both notes would sit on the data.
YLIM = (20.0, 116.0)
YTICKS = (40, 60, 80, 100)
MS_POINT = 2.8              # the measured lambda grid: present, but not what is being read
MS_LIMIT = 5.0              # lambda = 0 alone carries the claim, so it is the one enlarged mark

# ------------------------------------------------------------------ cartoon strip
GLYPH_LAMBDA = (1.0, 0.5, 0.0)
# Derived from XLIM rather than written out again: the glyphs sitting over their own x ticks is
# the thing that ties the cartoon to the measurement, and a second copy of these three numbers
# would let that alignment drift the first time the limits are touched.
GLYPH_X = tuple((XLIM[0] - lm) / (XLIM[0] - XLIM[1]) for lm in GLYPH_LAMBDA)
Y_QUERY, Y_CAND = 0.605, 0.460      # the two means: FIXED, identical in all three glyphs
R_X, R_Y = 0.103, 0.125             # cloud radii at lambda = 1, in strip units
# R_X is what three glyphs fit across 0.896 in without touching, and it is the binding constraint
# here, not the strip's height. R_Y is set a little larger rather than to the round-cloud value
# (R_X * TOP_W / TOP_H = 0.092) so the clouds are slightly tall: the separation being measured is
# vertical, and at 2 R_Y = 0.23 in the two populations overlap visibly at lambda = 1 and are
# visibly apart at lambda = 0.5, which is the whole content of the cartoon.
assert min(GLYPH_X) >= R_X and max(GLYPH_X) + R_X <= 1.0, "a cloud would leave the strip"
N_CELL = 14                         # a dozen or so: enough to read as a population at 0.19 in
# Re-seeded per glyph, so all three glyphs draw the SAME two samples. These two seeds are chosen,
# not arbitrary: each puts its 14-cell sample mean within 0.014 r of the centre, so the centroid
# marker sits where the drawn cells say it does, fills its disk to 0.99 r, and leaves no two cells
# closer than 0.20 r, which at 0.19 in across is the difference between a population and a smudge.
SEED_QUERY, SEED_CAND = 546, 323
# centroid()'s 34 pt^2 default is sized for the 3.00 in panels of row 1. At 0.048 in across it is
# a point inside a 0.19 in cloud; at the default it is as wide as the cloud's minor axis and hides
# the population it is meant to summarise. Shape, fill and colour are the helper's, unchanged.
CENTROID_S = 12
Y_LAMBDA_ROW = 0.262
Y_NOTE = 0.008

# The one equation, as fragments: True marks a subscript. Composed rather than set as mathtext so
# every glyph prints at or above the floor; see the module docstring.
EQ_FRAGS = (("$D$", False), ("pop", True), (" \u2192 ", False), ("$D$", False), ("mean", True))
EQ_X, EQ_BASELINE = 0.015, 0.740    # left edge and baseline, in axes fractions of the curve axes
SUB_DROP = 0.20                     # subscript baseline drop, as a fraction of the base size

_T2P = TextToPath()


def _limit_curve():
    """lambda, the population distance at each lambda, and the constant mean-to-mean endpoint."""
    d = pd.read_csv(CSV)
    sp = (d[d["prop"] == "prop1_spread"].dropna(subset=["t_spread"])
          .sort_values("t_spread", ascending=False))
    two_dmu = sp["two_dmu"].to_numpy(dtype=float)
    # The dashed rule is drawn as a single constant, so the file has to actually hold a constant;
    # a per-row endpoint would make the rule a summary rather than the quantity it claims to be.
    assert np.allclose(two_dmu, two_dmu[0]), f"two_dmu is not constant in {CSV}"
    return sp["t_spread"].to_numpy(dtype=float), sp["energy"].to_numpy(dtype=float), two_dmu[0]


def _equation(ax, x_frac, y_frac, frags, base=PT_EQ, sub=PT_SMALL, color=TEXT):
    """Draw a subscripted expression as one Text per fragment, and return its width in inches.

    Fragment widths come from the font metrics rather than from a renderer, so the run lays itself
    out before the first draw and on any backend. Hard-coding the offsets instead would be correct
    for exactly one axes width and one font, and would overlap silently when either changed.
    """
    w_in, h_in = ax.figure.get_size_inches()
    box = ax.get_position()
    ax_w_pt, ax_h_pt = box.width * w_in * 72.0, box.height * h_in * 72.0

    x = x_frac
    for text, is_sub in frags:
        size = sub if is_sub else base
        prop = FontProperties(family=["sans-serif"], size=size)
        width = _T2P.get_text_width_height_descent(text, prop, text.startswith("$"))[0]
        ax.text(x, y_frac - (SUB_DROP * base / ax_h_pt if is_sub else 0.0), text,
                transform=ax.transAxes, fontsize=size, color=color, ha="left", va="baseline")
        x += width / ax_w_pt
    return (x - x_frac) * ax_w_pt / 72.0


def _glyph(ax, cx, lam):
    """One population pair at residual scale ``lam``: two clouds contracting onto two fixed means.

    Re-seeding per glyph is the point. The three glyphs must be the same two samples at three
    scales, not three draws; if they were three draws the reader would be looking at sampling
    noise and would have no way to tell it from the effect of lambda.
    """
    if lam > 0:
        cells(ax, cx, Y_QUERY, N_CELL, R_X * lam, R_Y * lam, color=SHARED,
              rng=np.random.default_rng(SEED_QUERY))
        cells(ax, cx, Y_CAND, N_CELL, R_X * lam, R_Y * lam, color=POP,
              rng=np.random.default_rng(SEED_CAND))
    # The mean-to-mean distance, identical in all three glyphs. Dashed, in MEAN, because it is
    # the same quantity as the dashed rule in the curve below, seen end on; a reader who notices
    # that the three of these are the same length has read why that rule is flat.
    ax.plot([cx, cx], [Y_CAND, Y_QUERY], lw=LW_HAIR, ls="--", color=MEAN, zorder=5,
            dash_capstyle="butt")
    centroid(ax, cx, Y_QUERY, size=CENTROID_S)
    centroid(ax, cx, Y_CAND, size=CENTROID_S)


def draw_1g(ax, ax_top):
    lam, energy, two_dmu = _limit_curve()

    # ---------------------------------------------------------------- cartoon strip
    blank(ax_top)
    title(ax_top, "Mean retrieval\nis a limit case", y=0.995, va="top", linespacing=1.05)

    for cx, lm in zip(GLYPH_X, GLYPH_LAMBDA):
        _glyph(ax_top, cx, lm)

    # Unicode lambda rather than "$\\lambda$", for two reasons. The vocabulary sets any label
    # carrying mathtext at PT_EQ, and three of these at 9.0 pt do not fit across 0.896 in without
    # touching; and unicode keeps the glyph in the panel's own face, so the strip's lambda and the
    # x axis label's lambda are the same letter rather than two fonts' idea of one.
    for cx, lm, ha in zip((0.0, 0.5, 1.0), GLYPH_LAMBDA, ("left", "center", "right")):
        ax_top.text(cx, Y_LAMBDA_ROW, f"λ = {lm:g}", ha=ha, va="center",
                    fontsize=PT_ANNOT, color=TEXT)
    ax_top.text(1.0, Y_NOTE, "mean-only\nendpoint", ha="right", va="bottom",
                fontsize=PT_SMALL, color=TEXT, linespacing=1.1)

    # ---------------------------------------------------------------- curve axes
    # dash_capstyle butt: a projecting cap puts the rule's ink past the spine, which widens the
    # composite by the linewidth on both sides for no visible gain.
    ax.axhline(two_dmu, ls="--", lw=LW_HAIR, color=MEAN, zorder=2, dash_capstyle="butt")
    ax.plot(lam, energy, "-", color=POP, lw=LW_LINE, zorder=3)
    # The enlarged mark is selected by VALUE, not by position in the sorted array: which end of
    # that array holds the limit is decided by a sort argument twenty lines away, and the one
    # point this panel exists to show is not a thing to leave to that.
    at_limit = lam == lam.min()
    ax.plot(lam[~at_limit], energy[~at_limit], "o", color=POP, ms=MS_POINT, zorder=3)
    ax.plot(lam[at_limit], energy[at_limit], "o", color=POP, ms=MS_LIMIT, mec="white",
            mew=0.7, zorder=5)

    # The one annotation, and it states the claim rather than a number. It sits in the wedge
    # between the rising curve and the rule, so the arrow it contains points at the corner where
    # the two meet; a leader drawn to that corner would have to cross the curve to reach it.
    eq_w = _equation(ax, EQ_X, EQ_BASELINE, EQ_FRAGS)
    assert EQ_X + eq_w / AX_W <= 1.0, f"the equation run is {eq_w:.3f} in and leaves the axes"

    # Provenance and verification, both SUBTLE and both at the floor: the agreement is an analytic
    # identity being confirmed, not a biological result, and a reader who never reads it has still
    # read the panel.
    ax.text(0.99, 0.985, "Synthetic\nconstruction", transform=ax.transAxes, ha="right",
            va="top", fontsize=PT_SMALL, color=SUBTLE, linespacing=1.1)
    ax.text(0.99, 0.02, f"matched exactly:\n{energy[at_limit][0]:.2f} = {two_dmu:.2f}",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=PT_SMALL,
            color=SUBTLE, linespacing=1.1)

    ax.set_xlim(*XLIM)
    ax.set_ylim(*YLIM)
    ax.set_xticks(list(GLYPH_LAMBDA))
    # written as the strip writes them, so the tick under a glyph and the glyph's own label agree
    ax.set_xticklabels([f"{lm:g}" for lm in GLYPH_LAMBDA])
    ax.set_yticks(list(YTICKS))
    ax.tick_params(labelsize=PT_TICK)
    ax.set_xlabel("residual scale λ", fontsize=PT_ANNOT)
    ax.set_ylabel("population distance", fontsize=PT_ANNOT)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)


if __name__ == "__main__":
    import re

    import matplotlib.text as mtext
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from figstyle import apply_style, pin_canvas, soften_axes
    from fig1_style import PT_FLOOR, PT_TITLE

    # The composite's own geometry for panel g, so a position tuned here is correct there:
    # 0.44 in of y furniture, 0.55 in under the curve for the x labels, 0.20 in between the axes.
    Y_FURNITURE, DATA_BELOW, GAP, PAD = 0.44, 0.55, 0.20, 0.06
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
    # (0.44 in left, 0.55 in below), so they are measured against those budgets instead of
    # against the axes rect. Everything else must sit inside the axes it was drawn into.
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
