"""The frozen visual vocabulary of Figure 1. Every panel imports from here; none redefines.

WHY THIS FILE EXISTS
--------------------
Figure 1 is the paper's visual thesis, and its eight panels have to read as one argument rather
than as eight correct small plots. Two things break that, and both broke it before: a colour that
means "population" in one panel and "candidate A" in the next, and a type size chosen per panel to
make that panel's own crowding go away. Both are settled here, once, and the panels import the
answer instead of each making their own.

COLOUR: FOUR ROLES, AND NOT A FIFTH
-----------------------------------
    POP     blue    population-level / distributional. The retained cell population, the
                    population score, and anything that is a consequence of keeping cells.
    MEAN    orange  mean-level / collapsed signature. The centroid, the cosine, the mean score,
                    and anything that is a consequence of averaging.
    SHARED  grey    the query, the candidate library, the ranking machinery: everything both
                    routes have in common. If two things are shared, they are this colour, which
                    is what makes the branch colours mean something.
    EXT     green   an evaluator the retrieval method never saw. Used in e and f only, because
                    those are the only panels where an outside judge exists.

A fifth functional colour is not available. If a panel needs to separate two things and has run
out, it separates them by shape, fill, or position, not by inventing a hue: the reader has been
taught four meanings by the time they reach panel e and a fifth one silently redefines the figure.

TYPE: A LADDER, NOT A BUDGET
----------------------------
Figure 1 is authored at 6.90 in, the width it prints at, so nominal point size IS printed point
size. The deck-wide floor is 5 pt (figstyle.MIN_PT), but 5 pt is a production limit, not a
legibility one, and Figure 1 is the figure an editor reads first. Its own floor is PT_FLOOR = 6.5,
enforced in fig1_assemble.build().

Note PT_EQ, and note how it is derived rather than chosen. Matplotlib renders a mathtext
sub/superscript at 0.7x nominal, so the smallest nominal size whose subscript still clears this
figure's floor is 6.5 / 0.7 = 9.286, rounded up to 9.3. It was 9.0 in the first cut of this file,
on the claim that 9.0 x 0.7 "clears this figure's floor"; 9.0 x 0.7 is 6.30, which does not, and
fig1_assemble._assert_floor would have rejected every panel that used it. Three panel authors
caught it independently and composed their subscripts by hand instead. Panels a and c still do,
setting the subscript as its own 6.5 pt artist, which lands a shade LARGER than mathtext would;
that is left alone rather than reverted, since nothing was shrunk to reach it.

At the 7.2 pt the rest of the deck uses for mathtext a subscript prints at 5.04 pt, which clears
Nature's floor and not ours.
"""
from __future__ import annotations

import os
import sys

import numpy as np
from matplotlib.patches import FancyArrowPatch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from figstyle import (COMP_SOFT, FOCAL_SOFT, GREEN_SOFT, GREY, INK,  # noqa: E402
                      LIGHT_GREY, META)

# ---------------------------------------------------------------------------------- colour
POP = FOCAL_SOFT            # #5185C0
MEAN = COMP_SOFT            # #E99D4E
SHARED = GREY               # #767676
EXT = GREEN_SOFT            # #55966B
FAINT = LIGHT_GREY          # #D4D4D4, structure that must be visible without being read
TEXT = INK                  # all body text; colour carries meaning through MARKS, not letters
SUBTLE = META               # units, provenance, "n = ...", never a claim

# ---------------------------------------------------------------------------------- type
PT_LETTER = 9.5             # bold panel letter, drawn by fig1_assemble, not by figstyle's default
PT_TITLE = 8.5              # the one phrase a panel is allowed to state over itself
PT_ANNOT = 7.2              # ordinary annotation
PT_TICK = 6.8               # axis tick labels
PT_EQ = 9.3                 # any label containing mathtext; see the note above
PT_SMALL = 6.5              # provenance and units only. This figure's floor; nothing goes lower.
PT_FLOOR = 6.5

# ---------------------------------------------------------------------------------- line weights
LW_HAIR = 0.6               # rules, guides, anything the eye should not stop on
LW_LINE = 1.0               # a plotted series
LW_ARROW = 0.9              # flow between stages
MS_ARROW = 7                # FancyArrowPatch mutation_scale


def cells(ax, cx, cy, n, rx, ry, color=SHARED, minority=None, rng=None,
          s=3.4, alpha=0.75, zorder=3):
    """A single-cell response population: n points filling an ellipse centred on (cx, cy).

    The bound is deliberate. A Gaussian cloud puts a few per cent of its points past 2 sigma, and
    at this figure's panel sizes those stragglers read as cells sitting OUTSIDE the population and
    push neighbouring glyphs apart. Sampling uniformly inside a disk keeps every cell inside the
    blob the reader is meant to see, which is all a schematic population has to do.

    ``minority``: (fraction, colour) draws that share of the cells as a distinguishable
    subpopulation, concentrated in the lower half so it reads as a state rather than as noise.
    Returns the (x, y) arrays so a caller can draw leaders from the actual points.
    """
    rng = rng or np.random.default_rng(7)
    t = rng.uniform(0, 2 * np.pi, n)
    rad = np.sqrt(rng.uniform(0, 1, n))
    x, y = cx + rad * np.cos(t) * rx, cy + rad * np.sin(t) * ry
    if minority is None:
        ax.scatter(x, y, s=s, c=color, alpha=alpha, lw=0, zorder=zorder)
        return x, y
    frac, mcol = minority
    k = int(round(n * frac))
    order = np.argsort(y)                      # the minority sits low, so it reads as a state
    mi, ma = order[:k], order[k:]
    ax.scatter(x[ma], y[ma], s=s, c=color, alpha=alpha, lw=0, zorder=zorder)
    ax.scatter(x[mi], y[mi], s=s * 1.25, c=mcol, alpha=0.95, lw=0, zorder=zorder + 1)
    return x, y


def centroid(ax, x, y, color=MEAN, size=34, zorder=6):
    """The one-vector representation: a filled marker with a white keyline so it reads as a POINT.

    Drawn identically wherever a population has been collapsed, in a, b, c, d and g, because the
    reader has to recognise "this population became one number" without reading a label.
    """
    ax.scatter([x], [y], s=size, c=color, edgecolors="white", lw=0.7, zorder=zorder,
               marker="D")


def arrow(ax, p0, p1, color=SHARED, lw=LW_ARROW, ms=MS_ARROW, zorder=4, style="-|>",
          connectionstyle=None):
    """Flow between stages. Colour says whose flow it is; SHARED means both routes take it."""
    kw = dict(arrowstyle=style, mutation_scale=ms, lw=lw, color=color, zorder=zorder)
    if connectionstyle:
        kw["connectionstyle"] = connectionstyle
    ax.add_patch(FancyArrowPatch(p0, p1, **kw))


def blank(ax):
    """A schematic panel: unit coordinates, no axes furniture, nothing clipped at the edges."""
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    return ax


def title(ax, text, x=0.0, y=1.0, ha="left", va="bottom", color=TEXT, weight="bold", **kw):
    """The single phrase a panel states over itself. Everything longer belongs in the caption."""
    return ax.text(x, y, text, transform=ax.transAxes, fontsize=PT_TITLE, ha=ha, va=va,
                   color=color, fontweight=weight, **kw)
