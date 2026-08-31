"""PopRetrieve Figure 1 panel e: the objective-utility mismatch, drawn as two judging scenarios.

Schematic. No measured value is plotted and no data file stands behind this panel; it states the
paper's central conceptual claim, that a retrieval method can be graded by the very quantity it
was optimised to maximise, and that a grade of that kind cannot say whether the retrieved
candidate is the better candidate.

WHY TWO JUDGING SCENARIOS AND NOT A FLOWCHART
---------------------------------------------
The previous cut drew the claim as box -> box -> box with a curved arrow under it and then wrote
the conclusion out in a sentence. The structure lived in the words; the drawing only carried
them. The claim is about WHO HOLDS THE INSTRUMENT, so the drawing is now about that:

  * The retriever and the coupled evaluator are the SAME MARK. One circle, one fill, one colour,
    and inside each of them the same small instrument: two response populations with a gap
    between them, which is what a population distance measures. The reader sees the same object
    at both ends of the chain before reading a word, so "the scorer is judging itself" is seen
    rather than asserted.
  * The coupled lane CLOSES. A return path leaves the evaluator, runs back under the chain and
    points up into the retriever, and the words "shared objective" sit inside the loop it makes.
    A closed circuit is the one figure a reader cannot mistake for a pipeline.
  * The independent lane does not close. Its third stage is a rectangle rather than a circle, in
    EXT green rather than POP blue, and it holds pictures of things the retrieval score never
    saw: a target, a protein with a ligand in its pocket, a dose-response curve. It opens to the
    right onto two outcomes instead of returning.

Everything else is held identical on purpose. Both lanes use the same three stage centres, the
same stage footprint, the same grey flow arrows and the same three numbered candidate cards, so
the only differences a reader can find are the two the panel is about: one lane closes on itself,
the other opens onto a different kind of judge.

WHAT WAS CUT, AND WHAT THE CAPTION MUST NOW CARRY
-------------------------------------------------
Three things were cut so the marks could be drawn large enough to be read as marks.

  * The green judge's three icons are unlabelled. A bullseye, a bound protein and a sigmoid at
    0.11 in do not name themselves, so the caption has to say what they are: mechanism of action,
    target engagement, and viability from GDSC2 dose response.
  * "Retriever" and "Evaluator" are written once, in the coupled lane only. The independent lane
    inherits them from the column: same centre, same mark, therefore the same object.
  * The word "ranking" under the coupled lane's middle stage is gone. Three numbered cards ARE a
    ranking, and the independent lane still names it, because "fixed ranking" is the assertion
    that the SAME list is handed on unchanged.

The old verdict sentence "Apparent gain is built into the criterion" is gone as well. It read as
a conclusion the reader had to accept; "objective-aligned gain" is a label on what the coupled
lane produces, and the caption can argue from it.

TYPE AND SPACE
--------------
The axes is 3.15 x 2.03 in, so the panel is landscape and the two scenarios stack as two lanes of
roughly one inch each. Positions are held in inches and converted at draw time, rather than
written as axes fractions, because every constraint in this panel is a collision between a point
size and a length, and point sizes are inches. Nothing is set below PT_SMALL; where a phrase did
not fit it was cut, not shrunk.

Run standalone: python3 fig1e.py
"""
from __future__ import annotations

import os
import sys

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import to_rgba
from matplotlib.patches import Ellipse, Polygon, Rectangle

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fig1_style import (EXT, LW_ARROW, LW_HAIR, POP, PT_ANNOT,  # noqa: E402
                        PT_SMALL, PT_TITLE, SHARED, TEXT, arrow, blank, cells, title)

# --------------------------------------------------------------------------------- the canvas
# The rect fig1_assemble gives panel e: half of the 6.90 in page less the 0.24 in letter gutter
# and the 0.06 in right margin, by the 2.03 in row height of the e/f row.
AX_W, AX_H = 3.15, 2.03


def _fx(x_in):
    return x_in / AX_W


def _fy(y_in):
    return y_in / AX_H


# ------------------------------------------------------------------------- stages, x in inches
# The three stage centres. Both lanes use them, which is what makes the lanes comparable at a
# glance. X1 is far enough in that the retriever's own two-line instance label clears the axes
# edge; X3 is far enough left that the widest instance line ("population distance", 0.80 in)
# still ends before the verdict column starts.
X1, X2, X3 = 0.34, 0.97, 1.60
D_STAGE = 0.36                  # circle diameter, and the height the card stack is built to match
CARD_W, CARD_H, CARD_PITCH = 0.34, 0.095, 0.128     # 3 cards at this pitch stand 0.351 in tall
CARD_BAR_H = 0.022              # the candidate's signature inside its card
JUDGE_W, JUDGE_H = 0.46, 0.36   # the green judge: a stage's height, and a different shape
X_FLOW_GAP = 0.035              # mark edge -> arrow tail, so no head ever touches a mark

# The instrument drawn inside every POP circle: two populations and the gap between them. The
# clouds sit 0.068 in apart edge to edge, which is the smallest gap that still reads as a gap
# once the dots are 0.019 in across, and each cloud is tight enough to read as one population
# rather than as scatter.
ICON_R, ICON_DX, ICON_N = 0.036, 0.070, 13

# ------------------------------------------------------------------------- verdicts, x in inches
X_VERDICT_END = 1.975           # where a lane's verdict arrow stops
X_VERDICT_MARK = 2.085          # the verdict mark's centre
X_MARK_HALF = 0.070             # half a verdict mark. The swap needs two shafts long enough to
                                # be shafts: below 0.10 in the pair renders as two bare heads.
X_VERDICT_TEXT = 2.190          # the verdict's words, set flush left; 0.96 in of run remains,
                                # which holds "objective-aligned" (0.78 in), the widest of them

# ------------------------------------------------------------------------------- y, in inches
# Solved rather than chosen: each row's fixed height (an 8.5 pt headline, two 7.2 pt lines, a
# 6.5 pt two-line instance, a 0.36 in stage, the loop, the verdict fan) was added up and the
# remainder was spent on the gap between the two lanes, because that gap is what makes them read
# as two scenarios rather than one six-stage pipeline.
Y_HEADLINE = 2.026              # va="top"
Y_HEAD_A = 1.856                # lane name. 0.055 in under the headline's descenders: any less
                                # and two bold lines read as one two-line title.
Y_ROLE_A = 1.718                # Retriever / Evaluator
Y_INST_A = 1.606                # their concrete instance, tight under the role it belongs to
Y_STAGE_A = 1.202               # stage centres
Y_LOOP_LABEL = 0.950            # inside the loop, between the card stack and the return run
Y_RETURN = 0.875                # the return path's horizontal run
Y_HEAD_B = 0.812
Y_INST_B = 0.694
Y_STAGE_B = 0.370
DY_FAN = 0.180                  # the two outcomes, above and below the independent lane's axis

TINT = 0.14                     # a wash of the mark's own hue, never a fifth colour
TINT_JUDGE = 0.10               # the green card carries three icons, so its fill sits back


# ------------------------------------------------------------------------------------- marks
def _instrument(ax, cx, cy):
    """Two response populations with a gap between them: what a population distance measures.

    Drawn identically inside every POP circle, with the same two seeds every time, so the
    retriever and the coupled evaluator are the same object down to the dot pattern. That
    identity is the panel's first claim and it is made without a word.
    """
    for dx, seed in ((-ICON_DX, 11), (ICON_DX, 12)):
        cells(ax, _fx(cx + dx), _fy(cy), ICON_N, _fx(ICON_R), _fy(ICON_R), color=POP,
              rng=np.random.default_rng(seed), s=1.8, alpha=0.9, zorder=5)


def _stage_circle(ax, cx, cy):
    """The retriever, and the coupled evaluator. One shape, one fill, one instrument."""
    ax.add_patch(Ellipse((_fx(cx), _fy(cy)), _fx(D_STAGE), _fy(D_STAGE),
                         fc=to_rgba(POP, TINT), ec=POP, lw=1.0, zorder=3))
    _instrument(ax, cx, cy)


def _cards(ax, cx, cy):
    """The ranked candidate list: three numbered cards, identical in both lanes.

    It is the one object the two scenarios literally share, so it is drawn from the same code at
    the same size at the same x in both, and the independent lane's "fixed ranking" says in words
    only what the reader can already check by eye.
    """
    for i, rank in enumerate(("1", "2", "3")):
        y = cy + (1 - i) * CARD_PITCH
        ax.add_patch(Rectangle((_fx(cx - CARD_W / 2), _fy(y - CARD_H / 2)),
                               _fx(CARD_W), _fy(CARD_H),
                               fc=to_rgba(SHARED, TINT), ec=SHARED, lw=0.7, zorder=3))
        ax.text(_fx(cx - CARD_W / 2 + 0.050), _fy(y), rank, ha="center", va="center",
                fontsize=PT_SMALL, color=TEXT, zorder=5)
        ax.add_patch(Rectangle((_fx(cx - CARD_W / 2 + 0.090), _fy(y - CARD_BAR_H / 2)),
                               _fx(CARD_W - 0.128), _fy(CARD_BAR_H),
                               fc=to_rgba(SHARED, 0.55), ec="none", zorder=4))


def _target(ax, cx, cy):
    """Mechanism of action: did the retrieved compound hit the target it was supposed to."""
    for r in (0.055, 0.030):
        ax.add_patch(Ellipse((_fx(cx), _fy(cy)), _fx(2 * r), _fy(2 * r),
                             fc="none", ec=EXT, lw=0.7, zorder=5))
    ax.add_patch(Ellipse((_fx(cx), _fy(cy)), _fx(0.020), _fy(0.020), fc=EXT, ec="none", zorder=5))


def _protein(ax, cx, cy):
    """A protein with a ligand in its pocket: target engagement, measured on the protein itself.

    The outline is a circle modulated by cos(3 theta), which puts three concavities on it; the
    ligand sits in the one that faces down and right, so the two marks read as bound rather than
    as a blob with a dot beside it.
    """
    th = np.linspace(0, 2 * np.pi, 180)
    r = 0.048 * (1 + 0.24 * np.cos(3 * th + 0.6))
    ax.add_patch(Polygon(np.column_stack([_fx(cx + r * np.cos(th)), _fy(cy + r * np.sin(th))]),
                         closed=True, fc=to_rgba(EXT, 0.28), ec=EXT, lw=0.7, zorder=5))
    th_pocket = (np.pi - 0.6) / 3 + 4 * np.pi / 3      # a minimum of r(theta), facing down-right
    r_pocket = 0.048 * 0.76 + 0.011
    ax.add_patch(Ellipse((_fx(cx + r_pocket * np.cos(th_pocket)),
                          _fy(cy + r_pocket * np.sin(th_pocket))),
                         _fx(0.026), _fy(0.026), fc=EXT, ec="white", lw=0.5, zorder=6))


def _dose(ax, cx, cy):
    """A dose-response curve: viability, the readout the retrieval score is furthest from."""
    w, h = 0.180, 0.090
    x0, y0 = cx - w / 2, cy - h / 2
    ax.plot([_fx(x0), _fx(x0), _fx(x0 + w)], [_fy(y0 + h), _fy(y0), _fy(y0)],
            lw=LW_HAIR, color=EXT, zorder=5, solid_capstyle="butt")
    t = np.linspace(0, 1, 60)
    xs = x0 + 0.016 + t * (w - 0.022)
    ys = y0 + 0.012 + (h - 0.020) / (1 + np.exp(9 * (t - 0.5)))
    ax.plot(_fx(xs), _fy(ys), lw=0.9, color=EXT, zorder=6, solid_capstyle="round")


def _judge(ax, cx, cy):
    """The evaluator the method never saw: a rectangle of measured biology, not a score.

    Deliberately not a circle and deliberately not blue. The reader has been taught by the lane
    above that a POP circle is the retrieval objective; this stage has to be a different kind of
    object at a glance, so it differs in shape, in colour and in what it contains.
    """
    ax.add_patch(Rectangle((_fx(cx - JUDGE_W / 2), _fy(cy - JUDGE_H / 2)),
                           _fx(JUDGE_W), _fy(JUDGE_H),
                           fc=to_rgba(EXT, TINT_JUDGE), ec=EXT, lw=1.0, zorder=3))
    _target(ax, cx - 0.108, cy + 0.072)
    _protein(ax, cx + 0.108, cy + 0.072)
    _dose(ax, cx, cy - 0.082)


# ------------------------------------------------------------------------------------- flow
def _flow(ax, y, x3_half):
    """The two connectors of one lane, in SHARED grey because the flow is what both lanes share.

    ``x3_half`` is the half width of whatever occupies the third stage, so the arrow stops on the
    mark's own edge in each lane and the two lanes still start their arrows at the same x.
    """
    arrow(ax, (_fx(X1 + D_STAGE / 2 + X_FLOW_GAP), _fy(y)),
          (_fx(X2 - CARD_W / 2 - X_FLOW_GAP), _fy(y)), color=SHARED, ms=6.0)
    arrow(ax, (_fx(X2 + CARD_W / 2 + X_FLOW_GAP), _fy(y)),
          (_fx(X3 - x3_half - X_FLOW_GAP), _fy(y)), color=SHARED, ms=6.0)


def _return_path(ax):
    """The coupled lane closing on itself: down from the evaluator, back, and up into the scorer.

    Rectilinear rather than a bowed arc. An arc deep enough to clear the label would have hung
    0.20 in below the stages and crowded the lane beneath it; three straight segments close the
    circuit in 0.15 in and leave a clean interior for the two words that name it.
    """
    y_bot = Y_STAGE_A - D_STAGE / 2
    ax.plot([_fx(X3)] * 2, [_fy(y_bot), _fy(Y_RETURN)], lw=LW_ARROW, color=POP, zorder=2,
            solid_capstyle="butt")
    ax.plot([_fx(X3), _fx(X1)], [_fy(Y_RETURN)] * 2, lw=LW_ARROW, color=POP, zorder=2,
            solid_capstyle="butt")
    arrow(ax, (_fx(X1), _fy(Y_RETURN)), (_fx(X1), _fy(y_bot - 0.004)), color=POP, ms=6.0)


# ---------------------------------------------------------------------------------- verdicts
def _verdict_arrow(ax, x_from, y_from, y_to, color):
    arrow(ax, (_fx(x_from), _fy(y_from)), (_fx(X_VERDICT_END), _fy(y_to)), color=color, ms=5.5)


def _gain_mark(ax, y):
    """The coupled lane's single outcome: a rise, in the colour of the objective that scored it."""
    arrow(ax, (_fx(X_VERDICT_MARK), _fy(y - 0.072)), (_fx(X_VERDICT_MARK), _fy(y + 0.072)),
          color=POP, ms=7.0, lw=1.1)


def _tick_mark(ax, y):
    """The ranking survives a judge that never saw the score."""
    ax.plot(_fx(np.array([X_VERDICT_MARK - X_MARK_HALF, X_VERDICT_MARK - 0.020,
                          X_VERDICT_MARK + X_MARK_HALF])),
            _fy(np.array([y + 0.006, y - 0.030, y + 0.048])),
            lw=1.3, color=EXT, solid_capstyle="round", solid_joinstyle="miter", zorder=5)


def _swap_mark(ax, y):
    """Two candidates changing places: what an independent judge is allowed to do to a ranking."""
    arrow(ax, (_fx(X_VERDICT_MARK - X_MARK_HALF), _fy(y + 0.026)),
          (_fx(X_VERDICT_MARK + X_MARK_HALF), _fy(y + 0.026)), color=EXT, ms=3.8)
    arrow(ax, (_fx(X_VERDICT_MARK + X_MARK_HALF), _fy(y - 0.026)),
          (_fx(X_VERDICT_MARK - X_MARK_HALF), _fy(y - 0.026)), color=EXT, ms=3.8)


def _verdict_text(ax, y, text):
    ax.text(_fx(X_VERDICT_TEXT), _fy(y), text, ha="left", va="center", fontsize=PT_ANNOT,
            color=TEXT, linespacing=1.15, zorder=5)


# ------------------------------------------------------------------------------------- lanes
def _lane_name(ax, y, text):
    ax.text(0.0, _fy(y), text, ha="left", va="top", fontsize=PT_ANNOT, fontweight="bold",
            color=TEXT, zorder=5)


def _coupled(ax):
    _lane_name(ax, Y_HEAD_A, "Coupled evaluation")

    for x, role in ((X1, "Retriever"), (X3, "Evaluator")):
        ax.text(_fx(x), _fy(Y_ROLE_A), role, ha="center", va="top", fontsize=PT_ANNOT,
                color=TEXT, zorder=5)
    # The concrete instance, small, under the role it instantiates. The first and third columns
    # repeat the same two words on purpose: that repetition is the whole claim of the lane.
    for x, s in ((X1, "population\ndistance"), (X3, "population distance\nregret")):
        ax.text(_fx(x), _fy(Y_INST_A), s, ha="center", va="top", fontsize=PT_SMALL, color=TEXT,
                linespacing=1.15, zorder=5)

    _stage_circle(ax, X1, Y_STAGE_A)
    _cards(ax, X2, Y_STAGE_A)
    _stage_circle(ax, X3, Y_STAGE_A)
    _flow(ax, Y_STAGE_A, D_STAGE / 2)

    _return_path(ax)
    # Inside the loop, which is the only place these two words can sit and still mean the circuit
    # around them rather than the stage above them.
    ax.text(_fx(X2), _fy(Y_LOOP_LABEL), "shared objective", ha="center", va="center",
            fontsize=PT_ANNOT, color=TEXT, zorder=5)

    _verdict_arrow(ax, X3 + D_STAGE / 2 + X_FLOW_GAP, Y_STAGE_A, Y_STAGE_A, POP)
    _gain_mark(ax, Y_STAGE_A)
    _verdict_text(ax, Y_STAGE_A, "objective-aligned\ngain")


def _independent(ax):
    _lane_name(ax, Y_HEAD_B, "Independent evaluation")

    # The one label the lane needs: the list is not re-ranked, it is handed over as it stands.
    # Set at the weight of the coupled lane's role names, not at the lane name's: it sits in
    # the same row as "Retriever" and "Evaluator" and is the same kind of label, and a second
    # bold line under a bold lane name reads as a two-line heading.
    ax.text(_fx(X2), _fy(Y_INST_B), "fixed ranking", ha="center", va="top", fontsize=PT_ANNOT,
            color=TEXT, zorder=5)

    _stage_circle(ax, X1, Y_STAGE_B)
    _cards(ax, X2, Y_STAGE_B)
    _judge(ax, X3, Y_STAGE_B)
    _flow(ax, Y_STAGE_B, JUDGE_W / 2)

    x_from = X3 + JUDGE_W / 2 + X_FLOW_GAP
    _verdict_arrow(ax, x_from, Y_STAGE_B, Y_STAGE_B + DY_FAN, EXT)
    _verdict_arrow(ax, x_from, Y_STAGE_B, Y_STAGE_B - DY_FAN, EXT)
    _tick_mark(ax, Y_STAGE_B + DY_FAN)
    _verdict_text(ax, Y_STAGE_B + DY_FAN, "ranking\nsupported")
    _swap_mark(ax, Y_STAGE_B - DY_FAN)
    _verdict_text(ax, Y_STAGE_B - DY_FAN, "ranking\noverturned")


def draw_1e(ax):
    blank(ax)
    # The panel's own phrase. It is a question, not a finding: the finding is panels g and h.
    # "Better representation, better decision?" and not the phrasing this panel was briefed
    # with, "Better representation is not better decision?", which is missing an article and
    # reads as a statement wearing a question mark. The comma form poses the question the
    # paper exists to answer and is two words shorter, which the headline needs at 8.5 pt.
    title(ax, "Better representation, better decision?", x=0.0, y=_fy(Y_HEADLINE),
          va="top")
    _coupled(ax)
    _independent(ax)
    return ax


# ------------------------------------------------------------------------------------ preview
if __name__ == "__main__":
    import re

    import matplotlib as mpl
    import matplotlib.axis as maxis
    import matplotlib.spines as mspines
    import matplotlib.text as mtext

    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from figstyle import apply_style

    from fig1_style import PT_FLOOR, PT_TICK

    apply_style(sizes=(PT_TITLE, PT_ANNOT, PT_TICK))

    fig, ax = plt.subplots(figsize=(AX_W, AX_H))
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)    # the axes IS the composite's rect
    draw_1e(ax)
    fig.canvas.draw()
    rend = fig.canvas.get_renderer()

    got = ax.get_window_extent(renderer=rend)
    assert (round(got.width / fig.dpi, 3), round(got.height / fig.dpi, 3)) == (AX_W, AX_H), (
        f"previewed at {got.width / fig.dpi:.3f} x {got.height / fig.dpi:.3f} in, but the "
        f"composite gives panel e {AX_W} x {AX_H} in; a panel tuned at another size is wrong")
    print(f"axes {AX_W} x {AX_H} in")

    # 1. the type floor, at EFFECTIVE size: matplotlib renders a mathtext sub/superscript at 0.7x
    subsup = re.compile(r"\$[^$]*[\^_][^$]*\$")
    sizes = []
    for t in fig.findobj(mtext.Text):
        s = str(t.get_text())
        if not s.strip() or not t.get_visible():
            continue
        sizes.append((t.get_fontsize() * (0.7 if subsup.search(s) else 1.0),
                      s.replace("\n", "/")[:36]))
    smallest = min(sizes)
    assert smallest[0] >= PT_FLOOR - 1e-6, f"below the {PT_FLOOR} pt floor: {sorted(sizes)[:5]}"
    print(f"smallest effective size: {smallest[0]:.2f} pt  ({smallest[1]!r})")

    # 2. nothing may hang outside the axes: an overhang widens the composite. blank() switched
    # the spines and the two Axis objects off, and an invisible Axis still reports an extent.
    over = []
    for art in ax.get_children():
        if isinstance(art, (mspines.Spine, maxis.Axis)) or not art.get_visible():
            continue
        if isinstance(art, mtext.Text) and not str(art.get_text()).strip():
            continue
        try:
            bb = art.get_tightbbox(rend)
        except TypeError:
            bb = art.get_window_extent(renderer=rend)
        if bb is None or bb.width <= 0:
            continue
        d = (got.x0 - bb.x0, bb.x1 - got.x1, got.y0 - bb.y0, bb.y1 - got.y1)
        if max(d) > 0.5:                    # half a display pixel, below the export's resolution
            lab = str(art.get_text())[:30] if isinstance(art, mtext.Text) else type(art).__name__
            over.append((lab.replace("\n", "/"), [round(v / fig.dpi, 4) for v in d]))
    for lab, d in over:
        print(f"  hangs out  {lab!r:32s} L{d[0]:+.3f} R{d[1]:+.3f} B{d[2]:+.3f} T{d[3]:+.3f} in")
    assert not over, f"{len(over)} artist(s) outside the axes"
    print("all artists inside the axes")

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "1e.png")
    # savefig.bbox is "tight" deck-wide; here it would crop the preview to its ink and the PNG
    # would no longer be the 3.15 x 2.03 in rect the composite hands this panel.
    with mpl.rc_context({"savefig.bbox": None, "savefig.pad_inches": 0.0}):
        fig.savefig(out, dpi=400)
    print(f"wrote {out}  (axes {AX_W} x {AX_H} in)")
