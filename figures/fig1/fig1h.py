"""PopRetrieve Figure 1 panel 1h: population scoring is itself a continuum.

WHAT THE PANEL HAS TO MAKE VISIBLE
----------------------------------
The measurement is a monotone curve of an aggregate against a temperature, and a reader who meets
it cold reads "a parameter was swept". That is not the claim. The claim is about what the
temperature DECIDES: whether the score averages the discrepancy over every response state, or
reports the single worst-matched one. Those are two different questions to ask about a drug, and
they are the two ends of one score family rather than two method classes.

So the strip does not describe the weighting, it IS the weighting. Four tracks, one per response
state, each a whole unit of weight; the bar inside a track is the share that state actually
receives. Three frames read left to right at three temperatures, and the same four tracks change
shape between them: four quarter-full tracks, then a graded tilt, then one full track and three
empty. A reader who takes nothing else away has seen a weight budget slide onto one state, which
is the panel. The tick and the cross say which state that is and why it wins the budget: the
candidate matches three of the query's states and misses the fourth, and the bar that fills its
track in the last frame is the one standing under the cross.

The curve underneath is those three frames made continuous, and the two axes are bound by colour
rather than by a caption: the strip's leftmost frame is orange and so is the low dashed rule, its
rightmost frame is blue and so is the high one, and the curve is measured travelling from the one
to the other in the direction the strip is read. The two regime PHRASES stay upstairs, where the
bars that earn them are; the curve repeats only the two temperature tokens, each hung under the
rule it names, which is the whole bridge the reader needs.

WHERE THE FOUR STATES COME FROM, AND WHY THEY ARE NOT INVENTED
--------------------------------------------------------------
STATES holds the four per-state distances of the Prop-3 construction in
src/experiments/exp06_theory_limits.py, which is what produced beta_interpolation.csv. The CSV
records only their aggregate, so the vector itself has to be named here; it is then CHECKED
against the file rather than trusted. _states() asserts that its mean and max are the file's own
mean and max columns and that its log-sum-exp aggregate reproduces every measured D_beta row, so
the cartoon is the measured object and not a drawing of one. If the experiment ever changes that
vector, this panel stops building instead of quietly illustrating a construction that no longer
exists.

The states are drawn in ascending order. D_beta is a symmetric function of the four distances, so
the order is free, and sorting is what lets "the worst-matched state" be a position the eye can
hold across three frames instead of a value it has to look up.

Every bar height is softmax(beta * d), which is the exact weight state k receives: it is the
gradient of D_beta with respect to d_k. The two labelled frames are the analytic limits, uniform
and one-hot, which is why their bars are exactly a quarter and exactly full. The middle frame is
a MEASURED row of the file, chosen as the one whose weight profile is furthest from both limits,
so "intermediate" is a property of the data rather than a value picked to look good.

The K = 1 property is the panel's third statement and its smallest. It is an analytic identity
(Methods), checked here against degenerate_limit_real.csv before it is drawn: coverage_K1 and
global_energy agree exactly in every row, and if they ever stop agreeing the panel raises instead
of drawing the claim. It is set at the floor, in SUBTLE, in the corner the rising curve has left
behind, which is what the identity is worth on the page: something a reader may pick up and never
has to.

TYPE, AND THE ONE DECISION THAT WAS REVERSED
--------------------------------------------
The 0.90 in portrait cut of this panel set the y axis in words ("interpolated distance") and put
the symbol in the caption, on the grounds that a PT_EQ label would be the largest in the figure.
The four-rows-of-two layout settles it the other way. The curve axes is 0.71 in tall and the
composite reserves 0.46 in of furniture beside it; a rotated two-line PT_ANNOT phrase plus
four-character tick labels does not fit that band, and no shorter phrase names the quantity. The
symbol does, in 0.13 in, and the caption already introduces it as $D_\\beta$. PT_EQ = 9.3 exists
for exactly this: 9.3 x 0.7 = 6.51 pt, so the subscript clears the figure's 6.5 pt floor.

Everything else avoids mathtext by using the unicode beta, as panel g uses the unicode lambda:
it keeps the strip's beta and the axis label's beta the same letter in the same face, and it
keeps three frame labels off a 9.3 pt line they have no room for.

Run standalone: python3 fig1h.py
"""
from __future__ import annotations

import csv
import os
import sys

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fig1_style import (FAINT, LW_HAIR, LW_LINE, MEAN, POP, PT_ANNOT, PT_EQ,  # noqa: E402
                        PT_SMALL, PT_TICK, SHARED, SUBTLE, TEXT, blank)

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RESULTS = os.path.join(REPO, "results", "exp06_theory_limits")
BETA_CSV = os.path.join(RESULTS, "beta_interpolation.csv")
DEGEN_CSV = os.path.join(RESULTS, "degenerate_limit_real.csv")

# The axes the composite hands this panel, in inches. Needed in the module and not only in the
# preview: the strip is 3.4 times wider than it is tall, so every glyph that must be square on the
# PAGE is sized in inches here and divided by these.
AX_W, AX_H = 2.67, 0.71
TOP_W, TOP_H = 2.67, 0.78

# The per-state distances behind beta_interpolation.csv (exp06_theory_limits.prop3_interpolation).
# Checked against the file in _states(); see the module docstring for why they live here at all.
STATES = (0.20, 0.55, 1.30, 0.80)

# ------------------------------------------------------------------ cartoon strip
# Rows, in inches from the TOP of the strip, so the stack is read in the order it is written and
# a change to one band cannot silently eat another. The bar zone is what is left over, and it is
# the largest band, because it is the only one carrying the argument.
Y_TITLE = 0.005
Y_MARK = 0.190              # centre of the state row: index digit and match mark, side by side
TRACK_TOP, TRACK_BOT = 0.235, 0.512
Y_BETA = 0.537              # top of the temperature token
Y_PHRASE = 0.660            # top of the regime phrase, on the two named frames only
MARK_IN = 0.048             # tick / cross, drawn as paths: a mark at cell scale, not type
MARK_GAP = 0.019            # digit to mark, within one state's slot
# Three frames across 2.67 in. This is the number the first cut got wrong: at 0.80 in of bars the
# 0.135 in between frames was barely twice the 0.07 in between bars inside one, and twelve tracks
# read as a single row. At 0.72 in the gap is 0.255 in against 0.065 in, four times, and three
# groups of four read as three.
GROUP_W, BAR_W = 0.72, 0.115
GROUP_X0 = (0.0, (TOP_W - GROUP_W) / 2.0, TOP_W - GROUP_W)

# ------------------------------------------------------------------ curve axes
# The y window is SOLVED from the file's two endpoint columns: the mean rule is pinned at F_MEAN
# and the max rule at F_MAX, which reserves a band under the mean rule for its temperature token
# and leaves the lower right, the corner the rising curve has left behind, for the K = 1 inset.
# Written as fractions those bands survive the file changing; written as y limits they would
# quietly stop being bands.
F_MEAN, F_MAX = 0.200, 0.900
X_PAD = 1.7                 # one factor, applied in log space to both ends of the measured grid
DASH = (0, (2.6, 1.6))
MS_POINT = 2.6              # the measured beta grid: present, not what is being read
INSET_XY = (0.985, 0.520)   # top RIGHT corner of the K = 1 inset, in axes fractions


def _u(y_in):
    """Strip units for a distance measured in inches down from the strip's top edge."""
    return 1.0 - y_in / TOP_H


def _beta_interpolation():
    """(finite betas, their D_beta, the mean endpoint, the max endpoint) from the measured file."""
    with open(BETA_CSV, newline="") as fh:
        rows = list(csv.DictReader(fh))
    beta = np.array([float(r["beta"]) for r in rows])
    dist = np.array([float(r["D_beta"]) for r in rows])
    mean_col = np.array([float(r["mean"]) for r in rows])
    max_col = np.array([float(r["max"]) for r in rows])
    if np.ptp(mean_col) or np.ptp(max_col):
        raise ValueError(f"{BETA_CSV}: mean/max are the analytic endpoints and must be constant "
                         f"down the file; got {set(mean_col)} and {set(max_col)}.")
    lo, hi = float(mean_col[0]), float(max_col[0])

    # The file's first and last rows carry beta = 1e-9 and 1e9 and their D_beta equals the mean and
    # the max exactly. They are the analytic limits written as rows, not measurements: plotting
    # them would ask a log axis to span eighteen decades to show two points that are already on the
    # page as the dashed rules. They are identified by that exact equality rather than by a
    # hard-coded beta cut, and asserted to be the two ends of the file.
    at_limit = (dist == lo) | (dist == hi)
    if not (at_limit[0] and at_limit[-1] and at_limit.sum() == 2):
        raise ValueError(f"{BETA_CSV}: expected exactly the first and last rows to sit on the "
                         f"analytic endpoints; rows on a limit: {np.flatnonzero(at_limit)}.")
    return beta[~at_limit], dist[~at_limit], lo, hi


def _d_beta(states, beta):
    """The coverage aggregate of ``states`` at ``beta``, as src/retrieval/metrics.py defines it."""
    s = states.mean()
    c = states - s
    if beta * np.abs(c).max() < 1e-3:          # the small-beta expansion metrics.py uses
        return s + 0.5 * beta * (c * c).mean()
    return s + (np.log(np.exp(beta * c).sum()) - np.log(len(states))) / beta


def _states(beta, dist, lo, hi):
    """The four per-state distances, ascending, verified against every row of the measured file.

    float32 is what wrote the CSV, so agreement is asserted at 1e-5 absolute rather than exactly;
    the observed disagreement is 8e-8, which is that rounding and nothing else.
    """
    st = np.sort(np.asarray(STATES, dtype=float))
    if not (np.isclose(st.mean(), lo, atol=1e-5) and np.isclose(st.max(), hi, atol=1e-5)):
        raise ValueError(f"STATES has mean {st.mean():.6f} and max {st.max():.6f}, but "
                         f"{BETA_CSV} reports {lo:.6f} and {hi:.6f}.")
    got = np.array([_d_beta(st, b) for b in beta])
    if not np.allclose(got, dist, atol=1e-5):
        raise ValueError(f"STATES no longer reproduces {BETA_CSV}: worst row differs by "
                         f"{np.max(np.abs(got - dist)):.2e}. The strip would be drawing a "
                         f"construction the experiment has stopped running.")
    return st


def _weights(states, beta):
    """The share of the aggregate each state receives: softmax(beta * d), the gradient of D_beta."""
    w = np.exp(beta * (states - states.max()))
    return w / w.sum()


def _regimes(states, beta):
    """The three frames: the two analytic limits, and the measured beta furthest from both.

    "Intermediate" is decided by the data. Every finite beta in the file is scored by how far its
    weight profile sits from BOTH limits, and the frame takes the argmax; picking a beta by eye
    would be picking the shape the panel wants to show.
    """
    n = len(states)
    w_mean, w_worst = np.full(n, 1.0 / n), np.eye(n)[-1]
    scored = [min(np.linalg.norm(_weights(states, b) - w_mean),
                  np.linalg.norm(_weights(states, b) - w_worst)) for b in beta]
    b_mid = float(beta[int(np.argmax(scored))])
    # Colour, and why the middle frame is not a fifth one. The two ends own the vocabulary's two
    # meanings: beta -> 0 averages the per-state discrepancies, which is MEAN, and beta -> infinity
    # keeps the one worst state instead of averaging it away, which is POP. Those two are the
    # curve's two dashed rules below. The interior of the family belongs to neither and is drawn in
    # SHARED, the neutral, so the strip reads orange -> grey -> blue in the direction the curve
    # travels; what separates the three frames is their SHAPE and their position, not a new hue.
    return ((w_mean, MEAN, "β → 0", "mean aggregation", "left", 0.0),
            (_weights(states, b_mid), SHARED, f"β = {b_mid:g}", None, "center", 0.5),
            (w_worst, POP, "β → ∞", "worst-state emphasis", "right", 1.0))


def _k1_identity_holds():
    """True only if coverage at K = 1 equals the global distance in every row of the real file."""
    with open(DEGEN_CSV, newline="") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        raise ValueError(f"{DEGEN_CSV} is empty; the K = 1 identity has no evidence behind it.")
    return all(float(r["global_energy"]) == float(r["coverage_K1"]) for r in rows)


def _mark(ax, cx, cy, matched):
    """A tick or a cross, drawn as paths so the two are told apart by SHAPE and not by colour.

    Paths rather than a text glyph: this is a mark at the scale of the figure's cells, it must be
    square on a strip that is 3.4 times wider than tall, and a font's check mark is not available
    in every face the deck may fall back to.
    """
    hx, hy = MARK_IN / 2.0 / TOP_W, MARK_IN / 2.0 / TOP_H
    kw = dict(color=SHARED, lw=0.75, solid_capstyle="round", solid_joinstyle="miter", zorder=4)
    if matched:
        ax.plot([cx - hx, cx - 0.25 * hx, cx + hx],
                [cy + 0.10 * hy, cy - 0.85 * hy, cy + 0.95 * hy], **kw)
    else:
        for sign in (1, -1):
            ax.plot([cx - 0.8 * hx, cx + 0.8 * hx], [cy - sign * 0.8 * hy, cy + sign * 0.8 * hy],
                    **kw)


def _frame(ax, x0, weights, colour, states):
    """One temperature: four tracks of one unit of weight each, filled by the share it receives."""
    slot = GROUP_W / len(weights)
    full = TRACK_BOT - TRACK_TOP
    worst = int(np.argmax(states))
    # One floor per frame, spanning only that frame's four tracks. It is what turns three groups
    # of four into three objects: the eye takes a shared baseline as a shared scale.
    ax.plot([x0 / TOP_W, (x0 + GROUP_W) / TOP_W], [_u(TRACK_BOT)] * 2, lw=LW_HAIR, color=SHARED,
            solid_capstyle="butt", zorder=4)
    for k, w in enumerate(weights):
        cx = (x0 + (k + 0.5) * slot) / TOP_W
        # The track is a WHOLE unit of weight, so a quarter-filled track and a full one are read
        # off one scale. Without it the last frame is a lone bar and says nothing about the three
        # states that were given nothing.
        ax.add_patch(mpl.patches.Rectangle((cx - BAR_W / 2 / TOP_W, _u(TRACK_BOT)),
                                           BAR_W / TOP_W, full / TOP_H, facecolor=FAINT,
                                           edgecolor="none", alpha=0.55, zorder=2))
        if w > 0:
            ax.add_patch(mpl.patches.Rectangle((cx - BAR_W / 2 / TOP_W, _u(TRACK_BOT)),
                                               BAR_W / TOP_W, w * full / TOP_H, facecolor=colour,
                                               edgecolor="none", zorder=3))
        # Index and match mark share one row: two rows would cost 0.09 in of a 0.78 in strip, and
        # the bar zone is where that height does the panel more good.
        dx = (MARK_GAP + MARK_IN) / 2.0 / TOP_W
        ax.text(cx - dx, _u(Y_MARK), str(k + 1), ha="center", va="center", fontsize=PT_SMALL,
                color=SUBTLE)
        _mark(ax, cx + dx, _u(Y_MARK), k != worst)


def _cartoon(ax, states, beta):
    """The state weighting itself: three temperatures, one weight budget, four tracks."""
    blank(ax)
    # No phrase: the caption says "Population scoring is itself a continuum", and the panel
    # shows the three weightings and the curve between the two analytic endpoints.

    for x0, (weights, colour, token, phrase, ha, xa) in zip(GROUP_X0, _regimes(states, beta)):
        _frame(ax, x0, weights, colour, states)
        # The outer two frames are flush with the strip's edges and so are their labels, which is
        # what lets "worst-state emphasis" be set at PT_ANNOT at all: centred under its own frame
        # it would run 0.10 in past the axes and widen the composite.
        ax.text(xa, _u(Y_BETA), token, ha=ha, va="top", fontsize=PT_ANNOT, color=TEXT)
        if phrase:
            ax.text(xa, _u(Y_PHRASE), phrase, ha=ha, va="top", fontsize=PT_ANNOT, color=TEXT)


def _curve(ax, beta, dist, lo, hi):
    """The measured aggregate, travelling between the two endpoints the strip has just named."""
    span = (hi - lo) / (F_MAX - F_MEAN)
    y_lo = lo - F_MEAN * span
    ax.set_ylim(y_lo, y_lo + span)
    ax.set_xscale("log")
    ax.set_xlim(beta.min() / X_PAD, beta.max() * X_PAD)

    # dash_capstyle butt: a projecting cap puts the rule's ink past the spine, which widens the
    # composite by the linewidth on both sides for no visible gain. The two colours are the two
    # outer frames of the strip directly above, so the endpoints are recognised, not read.
    for y, colour in ((lo, MEAN), (hi, POP)):
        ax.axhline(y, color=colour, lw=LW_HAIR, ls=DASH, zorder=2, dash_capstyle="butt")
    ax.plot(beta, dist, "-o", color=POP, lw=LW_LINE, ms=MS_POINT, zorder=4)

    # The only tokens on the curve. Each hangs under the rule it names, on the left, where the
    # curve has not arrived: the strip's leftmost and rightmost frames are found again as the
    # bottom and the top of this axes. The two regime phrases stay in the strip, because at 0.71 in
    # tall there is room under a rule for one line and not for two.
    for y_frac, token in ((F_MEAN, "β → 0"), (F_MAX, "β → ∞")):
        ax.text(0.012, y_frac - 0.025, token, transform=ax.transAxes, ha="left", va="top",
                fontsize=PT_ANNOT, color=TEXT)

    ax.set_yticks([lo, hi])
    ax.set_yticklabels([f"{lo:.2f}", f"{hi:.2f}"])
    ax.set_xticks([0.1, 1, 10, 100])
    # Written out rather than left to LogFormatter, which sets the decades as mathtext
    # superscripts: at PT_TICK those print at 4.76 pt, under this figure's floor.
    ax.set_xticklabels(["0.1", "1", "10", "100"])
    ax.xaxis.set_minor_locator(mpl.ticker.NullLocator())
    ax.tick_params(labelsize=PT_TICK, pad=1.2)
    ax.set_xlabel("temperature β", fontsize=PT_ANNOT, labelpad=0.5)
    # The symbol, not a phrase: see the module docstring. PT_EQ is the vocabulary's size for any
    # label carrying mathtext, and it is the only label here that does.
    ax.set_ylabel(r"$D_\beta$", fontsize=PT_EQ, labelpad=1.5, rotation=0, ha="right", va="center")
    # The left spine spans the family, from the mean endpoint to the worst one, so the band under
    # the mean rule reads as a reserved margin rather than as unused axis.
    ax.spines["left"].set_bounds(lo, hi)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)

    if not _k1_identity_holds():
        raise ValueError(
            f"{DEGEN_CSV}: coverage_K1 no longer equals global_energy, so panel h may not state "
            f"the identity. Drop the inset from the panel rather than softening its wording.")
    # The K = 1 property, kept and demoted: an analytic identity (Methods), checked just above
    # against the real-cell file, parked in the corner the rising curve has left behind. SUBTLE and
    # at the floor, as panel g sets its own verified identity, so a reader who never reads it has
    # still read the panel. That is the whole reason it is a corner inset and not a sentence.
    ax.text(INSET_XY[0], INSET_XY[1], "Special case, K = 1:\ncoverage = global distance",
            transform=ax.transAxes, ha="right", va="top", fontsize=PT_SMALL, color=SUBTLE,
            linespacing=1.15)


def draw_1h(ax, ax_top):
    """Panel h: the population score is a continuum, and beta says what it aggregates over."""
    beta, dist, lo, hi = _beta_interpolation()
    _cartoon(ax_top, _states(beta, dist, lo, hi), beta)
    _curve(ax, beta, dist, lo, hi)


if __name__ == "__main__":
    import re

    import matplotlib.text as mtext
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from figstyle import apply_style, pin_canvas, soften_axes
    from fig1_style import PT_FLOOR, PT_TITLE

    # The composite's own geometry for panel h (fig1_assemble.py, four rows of two): 0.46 in of y
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
    draw_1h(ax, ax_top)
    soften_axes(fig)

    for a, want in ((ax, (AX_W, AX_H)), (ax_top, (TOP_W, TOP_H))):
        got = (a.get_position().width * FW, a.get_position().height * FH)
        assert np.allclose(got, want, atol=1e-9), f"axes is {got}, the composite gives it {want}"
    fig.canvas.draw()                  # every tick label exists only once the figure is drawn
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
        print(f"  outside {name} [{kind}] {label!r}: "
              + ", ".join(f"{k} {v:+.3f} in" for k, v in over.items()))
    assert not [h for h in hangs if not h[2]], "in-panel artist leaves its axes; pull it back in"
    for _, label, _, over in hangs:
        assert over.get("left", 0) <= Y_FURNITURE, f"{label!r} overruns the y-furniture band"
        assert over.get("below", 0) <= DATA_BELOW, f"{label!r} overruns the x-furniture band"
        assert over.get("right", 0) <= PAD and over.get("above", 0) <= PAD, \
            f"{label!r} would widen the composite: {over}"
    print("containment: every in-panel artist inside its axes; furniture within its budget")

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "1h.png")
    fig.savefig(out, dpi=400)
    print(f"wrote {out}  (axes {AX_W} x {AX_H} in, strip {TOP_W} x {TOP_H} in)")
