"""PopRetrieve Figure 1 panel e: objective-utility mismatch.

Schematic; no external data. The panel states the paper's central conceptual claim, that a
retrieval method can be graded by the very quantity it was optimised to maximise, and that such a
grade cannot tell us whether the retrieved candidate is a better candidate.

WHY THE PANEL IS BUILT AS TWO STACKED LANES
-------------------------------------------
The claim is a COMPARISON, so it is drawn as one. Both lanes run through the same three stage
positions, carry the same stage glyph geometry and the same arrow style, and differ in exactly two
places: the colour of the third stage, and what the lane does after it. Everything a reader has to
compare therefore sits at the same x, one lane above the other, and the two differences are the
only things that move.

The top lane closes: the third stage is POP, the same colour as the first, because a
population-distance regret and a population-distance score are one statistical objective evaluated
twice. The bracket over the two ends names that, and the concrete instance under the stages shows
it literally, since "population distance" is spelled out at both ends of the chain. The bottom lane
does not close: the third stage is EXT, an evaluator the retrieval score never saw, and the lane
ends in a fork rather than a return arrow.

WHY THE STAGE LABELS SIT UNDER THE STAGE MARKS RATHER THAN INSIDE THEM
---------------------------------------------------------------------
The axes is 1.652 in wide. Wrapped onto two lines each, "Retrieval score", "Ranked candidates" and
"Evaluation" set at PT_ANNOT come to 0.85 of that width as bare text and 0.96 once each is boxed,
which leaves about 3 pt for each connecting arrow; the flow would be implied by adjacency rather
than drawn. Setting the type
smaller is not available (this figure's floor is 6.5 pt and lowering a size to fit is the failure
mode the ladder exists to prevent), so the stage MARK and the stage NAME were separated: a small
coloured node carries the colour and the flow, and the name sits under it with the full panel width
to wrap into. The arrows are then 0.23 in long and legible.

WHY THE MIDDLE STAGE IS DRAWN AS THREE BARS
-------------------------------------------
It is the ranked candidate list, and it is the one object the two lanes literally share: the same
ranking is handed to the independent evaluator unchanged. Drawing it as a list glyph rather than as
another plain node lets the reader see the same object in both lanes, which is what "FIXED RANKING"
asserts in words.

Run standalone: python3 fig1e.py
"""
from __future__ import annotations

import os
import sys

import matplotlib.pyplot as plt
from matplotlib.colors import to_rgba
from matplotlib.patches import Rectangle

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fig1_style import (EXT, FAINT, LW_HAIR, POP, PT_ANNOT,  # noqa: E402
                        PT_SMALL, PT_TITLE, SHARED, TEXT, arrow, blank, title)

# --------------------------------------------------------------------------- shared geometry
# The three stage positions. Both lanes use them, which is what makes the lanes comparable.
# X1 and X3 sit 0.17 of the width in from the edges because the widest name centred on either of
# them ("Evaluation", "population", both 0.30 of the width) must not cross the axes boundary.
X1, X2, X3 = 0.17, 0.50, 0.83
CHIP_W, CHIP_H = 0.17, 0.036          # the stage node, identical in both lanes
CHIP_GAP = 0.012                      # node edge -> arrow tail, so the head never touches the node

# --------------------------------------------------------------------------- top lane, y
# The ladder is solved, not chosen. Each lane's fixed heights (an 8.5 pt header, a 0.036 node, two
# or three text lines per row, the arc's sag) were added up, the gaps were set to the smallest
# value that still separates two rows at this size, and whatever was left over went to the pivot
# band in the middle, because that band is the one thing the brief asks to be given room.
Y_HEAD_T = 0.998
Y_SPAN_LABEL = 0.953
Y_SPAN = 0.920
SPAN_TICK = 0.010
Y_CHIP_T = 0.882                      # node centre
Y_NAME_T = 0.852
Y_INSTANCE = 0.778                    # 0.074 in below the names: any less and the 6.5 pt instance
                                      # reads as a third line of the 7.2 pt name above it
Y_RETURN = 0.689                      # the return arrow's two endpoints
# Negative rad bows the arc DOWNWARD, away from the instance row it would otherwise cross. The
# sag is |rad| x chord / 2 = 0.13 in here, deep enough to read as a return and not as a bracket.
RETURN_RAD = -0.24
Y_RETURN_LABEL = 0.642
Y_VERDICT = 0.597
X_VERDICT_BAR = 0.391                 # the verdict sets flush off this rule and runs to the
                                      # right edge, so the lane closes where the panel does

# --------------------------------------------------------------------------- pivot, y
Y_RULE_T, Y_RULE_B = 0.535, 0.368
Y_QUESTION = 0.4515

# --------------------------------------------------------------------------- bottom lane, y
Y_HEAD_B = 0.352
Y_CHIP_B = 0.289
Y_NAME_B = 0.259
Y_EVAL_TOP, Y_EVAL_BOT = 0.162, 0.094
Y_FORK = 0.088
Y_OUTCOME = 0.036
X_FORK, X_OK, X_FLIP = 0.54, 0.30, 0.78

TINT = 0.14                           # a wash of the stage's own hue, never a fifth colour
TINT_EMPH = 0.26


def _chip(ax, cx, cy, color, emphasis=False, ranked=False):
    """One stage node. Square corners: a rounded corner in an axes whose x unit is 1.652 in and
    whose y unit is 3.7 in comes out as an ellipse unless the mutation aspect is fought, and the
    corner radius carries no meaning worth that."""
    lw = 1.5 if emphasis else 0.8
    ax.add_patch(Rectangle((cx - CHIP_W / 2, cy - CHIP_H / 2), CHIP_W, CHIP_H,
                           fc=to_rgba(color, TINT_EMPH if emphasis else TINT),
                           ec=color, lw=lw, zorder=3))
    if not ranked:
        return
    # Three bars = the ranked list. Same three bars in both lanes, because it is the same list.
    bh, pitch = 0.0055, 0.0115
    for i in (-1, 0, 1):
        ax.add_patch(Rectangle((cx - 0.055, cy + i * pitch - bh / 2), 0.110, bh,
                               fc=color, ec="none", zorder=4))


def _stage_arrows(ax, y):
    """The two connectors of one lane. SHARED, because the flow is what both routes have."""
    x_edge = CHIP_W / 2 + CHIP_GAP
    arrow(ax, (X1 + x_edge, y), (X2 - x_edge, y), color=SHARED, ms=5.5)
    arrow(ax, (X2 + x_edge, y), (X3 - x_edge, y), color=SHARED, ms=5.5)


def _name(ax, x, y, text, weight="normal", boxed=False):
    """A stage name, centred under its node.

    ``boxed`` is spent once, on FIXED RANKING, and deliberately not mirrored in the lane above.
    The two lanes are already parallel through the thing that has to be compared, the stage nodes,
    which are identical in geometry at identical x. A rule drawn round the middle name in BOTH
    lanes was tried and removed: it made every name in both lanes read as boxed, so the one place
    the panel wants to shout, that the SAME ranking is handed on unchanged, no longer did.
    """
    bbox = None
    if boxed:
        bbox = dict(boxstyle="round,pad=0.30", fc=to_rgba(SHARED, TINT), ec=SHARED, lw=1.1)
    return ax.text(x, y, text, ha="center", va="top", fontsize=PT_ANNOT, color=TEXT,
                   fontweight=weight, linespacing=1.15, bbox=bbox, zorder=5)


def _top_lane(ax):
    title(ax, "Coupled evaluation", x=0.0, y=Y_HEAD_T, va="top")

    # The span names why the first and third stages share a colour. It is drawn in POP for the
    # same reason they are: it is a statement about the objective, not about the flow.
    ax.text(0.5, Y_SPAN_LABEL, "same statistical objective", ha="center", va="top",
            fontsize=PT_ANNOT, color=TEXT)
    ax.plot([X1, X3], [Y_SPAN, Y_SPAN], lw=LW_HAIR, color=POP, zorder=2)
    for x in (X1, X3):
        ax.plot([x, x], [Y_SPAN, Y_SPAN - SPAN_TICK], lw=LW_HAIR, color=POP, zorder=2)

    _chip(ax, X1, Y_CHIP_T, POP)
    _chip(ax, X2, Y_CHIP_T, SHARED, ranked=True)
    _chip(ax, X3, Y_CHIP_T, POP)
    _stage_arrows(ax, Y_CHIP_T)

    _name(ax, X1, Y_NAME_T, "Retrieval\nscore")
    _name(ax, X2, Y_NAME_T, "Ranked\ncandidates")
    _name(ax, X3, Y_NAME_T, "Evaluation")

    # The concrete instance. Column 1 and column 3 repeat the same two words on purpose: that
    # repetition is the claim the span above states in the abstract.
    for x, s in ((X1, "population\ndistance"), (X2, "ranking"),
                 (X3, "population\ndistance\nregret")):
        ax.text(x, Y_INSTANCE, s, ha="center", va="top", fontsize=PT_SMALL, color=TEXT,
                linespacing=1.15)

    arrow(ax, (X3, Y_RETURN), (X1, Y_RETURN), color=POP,
          connectionstyle=f"arc3,rad={RETURN_RAD}")
    ax.text(0.5, Y_RETURN_LABEL, "objective-aligned", ha="center", va="top",
            fontsize=PT_ANNOT, color=TEXT)

    ax.plot([X_VERDICT_BAR, X_VERDICT_BAR], [Y_VERDICT - 0.003, Y_VERDICT - 0.051],
            lw=1.2, color=POP, solid_capstyle="butt", zorder=4)
    ax.text(X_VERDICT_BAR + 0.016, Y_VERDICT, "Apparent gain is built\ninto the criterion",
            ha="left", va="top", fontsize=PT_ANNOT, color=TEXT, linespacing=1.15)


def _pivot(ax):
    """The question the paper exists to answer, and the two hairlines that give it a band.

    The rules are FAINT because they are structure: they hold the question apart from the two
    lanes without being read as a boundary between two results.
    """
    for y in (Y_RULE_T, Y_RULE_B):
        ax.plot([0, 1], [y, y], lw=LW_HAIR, color=FAINT, zorder=1)
    title(ax, "Does better\nrepresentation lead to\nbetter candidate choice?",
          x=0.5, y=Y_QUESTION, ha="center", va="center", linespacing=1.25)


def _bottom_lane(ax):
    title(ax, "Independent evaluation", x=0.0, y=Y_HEAD_B, va="top")

    _chip(ax, X1, Y_CHIP_B, POP)
    _chip(ax, X2, Y_CHIP_B, SHARED, emphasis=True, ranked=True)
    _chip(ax, X3, Y_CHIP_B, EXT)
    _stage_arrows(ax, Y_CHIP_B)

    _name(ax, X1, Y_NAME_B, "same\nretrieval\nscore")
    _name(ax, X2, Y_NAME_B, "FIXED\nRANKING", weight="bold", boxed=True)
    _name(ax, X3, Y_NAME_B, "Outside\nevaluator")

    # What the outside evaluator reads. It needs the panel width, so it sits centred under the
    # whole lane and is tied back to the green stage by a green connector rather than by position.
    ax.add_patch(Rectangle((0.185, Y_EVAL_BOT), 0.63, Y_EVAL_TOP - Y_EVAL_BOT,
                           fc=to_rgba(EXT, TINT), ec=EXT, lw=0.8, zorder=3))
    ax.text(0.5, (Y_EVAL_TOP + Y_EVAL_BOT) / 2, "MoA, protein, viability,\nfunctional response",
            ha="center", va="center", fontsize=PT_SMALL, color=TEXT, linespacing=1.2, zorder=5)
    arrow(ax, (0.80, Y_NAME_B - 0.058), (0.80, Y_EVAL_TOP + 0.002), color=EXT, ms=5.0)

    # The fork. This is the whole difference from the lane above: the chain ends in two possible
    # verdicts instead of returning to its own starting point.
    arrow(ax, (X_FORK, Y_FORK), (X_OK, Y_OUTCOME + 0.026), color=EXT, ms=5.0)
    arrow(ax, (X_FORK, Y_FORK), (X_FLIP, Y_OUTCOME + 0.026), color=EXT, ms=5.0)

    # tick = the ranking survives an evaluator that never saw the score
    ax.plot([0.135, 0.157, 0.190], [Y_OUTCOME, Y_OUTCOME - 0.010, Y_OUTCOME + 0.014],
            lw=1.1, color=EXT, solid_capstyle="round", solid_joinstyle="miter", zorder=5)
    ax.text(0.200, Y_OUTCOME, "confirmed", ha="left", va="center", fontsize=PT_ANNOT, color=TEXT)

    # opposed pair = the order of two candidates swaps, which is what "reversed" means
    arrow(ax, (0.600, Y_OUTCOME + 0.009), (0.700, Y_OUTCOME + 0.009), color=EXT, ms=4.5)
    arrow(ax, (0.700, Y_OUTCOME - 0.009), (0.600, Y_OUTCOME - 0.009), color=EXT, ms=4.5)
    ax.text(0.716, Y_OUTCOME, "reversed", ha="left", va="center", fontsize=PT_ANNOT, color=TEXT)


def draw_1e(ax):
    blank(ax)
    _top_lane(ax)
    _pivot(ax)
    _bottom_lane(ax)
    return ax


if __name__ == "__main__":
    import re

    import matplotlib.axis as maxis
    import matplotlib.spines as mspines
    import matplotlib.text as mtext

    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from figstyle import apply_style, pin_canvas

    from fig1_style import PT_FLOOR, PT_TICK

    apply_style(sizes=(PT_TITLE, PT_ANNOT, PT_TICK))

    # The axes is exactly the rect fig1_assemble gives panel e (0.28 of a 6.90 in figure, less the
    # 0.24 in letter gutter and the 0.04 in right margin, by 3.70 in). A panel tuned at any other
    # size is tuned for a figure that does not ship.
    AX_W, AX_H = 1.652, 3.700
    fig = plt.figure(figsize=(AX_W, AX_H))
    pin_canvas(fig)
    ax = fig.add_axes([0, 0, 1, 1])
    draw_1e(ax)
    fig.canvas.draw()
    rend = fig.canvas.get_renderer()

    # 1. type floor, at EFFECTIVE size: matplotlib renders a mathtext sub/superscript at 0.7x.
    subsup = re.compile(r"\$[^$]*[\^_][^$]*\$")
    sizes = []
    for t in fig.findobj(mtext.Text):
        s = str(t.get_text())
        if not s.strip() or not t.get_visible():
            continue
        sizes.append((t.get_fontsize() * (0.7 if subsup.search(s) else 1.0),
                      s.replace("\n", "/")[:34]))
    smallest = min(sizes)
    assert smallest[0] >= PT_FLOOR - 1e-6, f"below the {PT_FLOOR} pt floor: {sorted(sizes)[:5]}"
    print(f"smallest effective size: {smallest[0]:.2f} pt  ({smallest[1]!r})")

    # 2. nothing may hang outside the axes: an overhang widens the composite.
    box = ax.get_window_extent(renderer=rend)
    over = []
    # blank() turns the axes furniture off but leaves the Spine and Axis artists parented to the
    # axes, and their extents are not ink. Only drawn children can widen the composite.
    furniture = (mspines.Spine, maxis.Axis)
    for art in ax.get_children():
        if isinstance(art, furniture) or not art.get_visible():
            continue
        if isinstance(art, mtext.Text) and not str(art.get_text()).strip():
            continue
        try:
            bb = art.get_tightbbox(rend)
        except TypeError:
            bb = art.get_window_extent(renderer=rend)
        if bb is None or bb.width <= 0:
            continue
        d = (box.x0 - bb.x0, bb.x1 - box.x1, box.y0 - bb.y0, bb.y1 - box.y1)
        if max(d) > 0.5:                    # half a pixel of tolerance on the tight bbox
            lab = str(art.get_text())[:28] if isinstance(art, mtext.Text) else type(art).__name__
            over.append((lab.replace("\n", "/"),
                         [round(v / fig.dpi, 4) for v in d]))     # inches, L R B T
    for lab, d in over:
        print(f"  hangs out  {lab!r:34s} L{d[0]:+.3f} R{d[1]:+.3f} B{d[2]:+.3f} T{d[3]:+.3f} in")
    assert not over, f"{len(over)} artist(s) outside the axes"
    print("all artists inside the axes")

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "1e.png")
    fig.savefig(out, dpi=400)
    print(f"wrote {out}  (axes {AX_W} x {AX_H} in)")
