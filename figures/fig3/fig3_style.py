"""The frozen visual vocabulary of Figure 3. Every panel imports from here; none redefines.

WHY THIS FILE EXISTS, AND THE ERROR IT FIXES
--------------------------------------------
Figure 3 carries the paper's reversal: population-level retrieval captures more response
information, and that advantage weakens or changes direction once the judge stops sharing the
retrieval objective. Thirteen panels argue it, and before this file they argued it in eight chart
idioms and three conflicting colour semantics.

The worst of those was not an aesthetic problem. In the old panel a, BOTH violins are the same
quantity, the population-minus-mean advantage on the same 480 queries; the only thing that differs
between them is the metric doing the judging. They were drawn blue and orange, the deck's colours
for population retrieval and mean retrieval, so the panel said the right-hand distribution was the
mean method. It is not. The colour encoded the wrong variable, in the figure's most important
panel. Panel e coloured the gate's own reliability axis orange, and panels j and k coloured the
MoA-nDCG evaluator orange; none of the three is a mean-signature retriever.

SO THE RULE IS ABOUT SIGN, NOT ABOUT OBJECTS
--------------------------------------------
    POP    blue     population-level retrieval is favoured. As an object where methods are
                    genuinely being compared (h, i, l); as a HALF-PLANE or a bar direction
                    wherever a signed advantage is plotted against zero (a, b, c, g).
    MEAN   orange   mean-signature retrieval is favoured. Same two uses, mirrored.
    EXT    green    a control that performs no retrieval, or an external readout the retriever
                    never saw: the response-magnitude scalar, the potency match, GDSC2.
    SHARED grey     everything that is neither: the evaluator, the pre-specified gate and its
                    axes, reference lines, observed-n markers, and any distribution whose sign
                    is the thing being read rather than its identity.

One consequence, stated because it is easy to get wrong: a violin, an ECDF or a dot that plots
"population minus mean" is NOT blue. It is SHARED grey, and the blue and orange live in the
half-planes behind it. Blue ink means an object that is population-level, never a difference that
happens to be positive.

CELL LINES ARE A SHAPE, NEVER A HUE
-----------------------------------
A549 circle, K562 square, MCF7 triangle, in SHARED grey unless the mark also carries a family.
Three cell lines drawn in three strong colours is what made panel b look like a method contrast
when it is a within-method stratification, and Figure 3 cannot afford to spend its only two
meaningful hues on a nuisance variable.

DRAW THE EFFECT, NOT THE METHOD
-------------------------------
Where a panel can plot the signed difference instead of two levels, it does. The figure's question
is how much the population representation buys, so the quantity on the axis should be that, and
zero should be a datum rather than a corner of the frame.

TYPE
----
Authored at 6.90 in, the width it prints at, so nominal point size IS printed point size. This
figure holds thirteen panels on one page, so it is the deck's tightest, and the floor is where the
tightness has to stop: PT_FLOOR = 6.5, asserted in fig3_assemble._assert_floor, above the deck's
5 pt production limit. Mathtext is measured at its effective 0.7x, which is why PT_EQ is 9.3
(6.5 / 0.7 = 9.286) and not the 7.2 the rest of the deck uses.

When a panel does not fit, CUT the annotation into the caption. Nothing is shrunk.
"""
from __future__ import annotations

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from figstyle import (COMP_SOFT, FOCAL_SOFT, GREEN_SOFT, GREY, INK,  # noqa: E402
                      LIGHT_GREY, META, RULE)

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# ---------------------------------------------------------------------------------- colour
POP = FOCAL_SOFT            # #5185C0  population-level retrieval favoured
MEAN = COMP_SOFT            # #E99D4E  mean-signature retrieval favoured
EXT = GREEN_SOFT            # #55966B  no-retrieval control, or an external readout
SHARED = GREY               # #767676  the evaluator, the gate, references, signed differences
FAINT = LIGHT_GREY          # #D4D4D4  structure visible without being read
HAIRLINE = RULE             # #E6E6E6  spines and guides
TEXT = INK
SUBTLE = META

# Half-plane washes: which side of zero favours which representation. Contrast of INK on either
# is about 14:1, so a label may sit on one; a wash may never be the only thing separating two
# regions, and no coloured text may sit on one.
POP_WASH = "#E4EDF6"
MEAN_WASH = "#FBF0E4"

# ---------------------------------------------------------------------------------- type
PT_LETTER = 9.5
PT_TITLE = 8.5              # RETIRED with title(); kept only so the gate can name it
PT_ANNOT = 7.2
PT_TICK = 6.8
PT_EQ = 9.3                 # any label containing mathtext; 6.5 / 0.7 = 9.286
PT_SMALL = 6.5              # provenance, n, units. This figure's floor.
PT_FLOOR = 6.5

# ---------------------------------------------------------------------------------- weights
LW_HAIR = 0.6
LW_LINE = 1.1
LW_STEM = 0.9
MS_DOT = 26                 # a point estimate carrying a claim

# ---------------------------------------------------------------------------------- shapes
# Cell line identity. Shape only; the colour slot stays free for the sign or the family.
CELL_MARKER = {"A549": "o", "K562": "s", "MCF7": "^"}

# The metric-class ladder this figure walks. Class is a FILL, not a hue: the same retrieval
# result is judged by evaluators of increasing independence, so the evaluator must not borrow a
# colour that already means a retrieval family.
CLASS_FILL = {"A": "full", "B": "left", "C": "none"}
CLASS_NAME = {"A": "objective-aligned", "B": "task-proximal biological",
              "C": "external functional"}


# THERE IS NO title() HELPER, AND THAT IS THE POINT.
#
# The 2026-08-31 cut of this figure gave every panel one bold phrase stating its conclusion:
# "Only the evaluator changes; the advantage disappears", "Gate does not enrich", "Noise, not gap
# size, sets the cost", and ten more. Thirteen conclusion sentences on one page is thirteen claims
# competing for the reader's attention, and it is not what a Nature-family main figure does: the
# figure carries visual evidence and the legend carries the argument. Every one of those phrases
# now opens its panel's caption entry, where it costs no space and can be qualified properly.
#
# So the helper is deleted rather than deprecated, and fig3_assemble._assert_no_titles enforces
# what its absence intends: no panel may draw text above PT_ANNOT. Only four kinds of text are
# allowed on a panel now.
#
#   1. the panel letter          drawn by fig3_assemble, not by the panel
#   2. axis and group names      what the quantity is, and what the rows or groups are
#   3. necessary statistics      median, rho, P, n, and the values being compared
#   4. a very short direction    "mean better" / "population better", two or three words
#
# Anything else belongs in the caption. When a panel feels like it needs a sentence, that is the
# signal that the drawing is not carrying its own weight yet.


def sign_field(ax, vertical=True, at=0.0, pop_side="right", alpha=1.0, zorder=0):
    """Wash the two half-planes of a signed-advantage axis and return the two patch handles.

    ``vertical`` washes left and right of a vertical rule at x = ``at`` (use for an x axis that
    carries the signed quantity); otherwise above and below a horizontal rule. ``pop_side`` says
    which side population-level retrieval is favoured on, because not every panel puts it right.
    """
    lo_c, hi_c = (MEAN_WASH, POP_WASH) if pop_side in ("right", "top") else (POP_WASH, MEAN_WASH)
    if vertical:
        lo = ax.axvspan(-1e9, at, color=lo_c, lw=0, zorder=zorder, alpha=alpha)
        hi = ax.axvspan(at, 1e9, color=hi_c, lw=0, zorder=zorder, alpha=alpha)
    else:
        lo = ax.axhspan(-1e9, at, color=lo_c, lw=0, zorder=zorder, alpha=alpha)
        hi = ax.axhspan(at, 1e9, color=hi_c, lw=0, zorder=zorder, alpha=alpha)
    return lo, hi


def zero_rule(ax, at=0.0, vertical=True, color=SUBTLE, lw=0.8, zorder=2, ls="-"):
    """The line a signed quantity is read against. Darker than a spine, because it is a datum."""
    f = ax.axvline if vertical else ax.axhline
    return f(at, color=color, lw=lw, zorder=zorder, ls=ls)


def bare_axes(ax, keep=("left", "bottom")):
    """House axes: hairline spines on the sides that carry a scale, nothing on the others."""
    for side in ("top", "right", "left", "bottom"):
        ax.spines[side].set_visible(side in keep)
        if side in keep:
            ax.spines[side].set_color(HAIRLINE)
            ax.spines[side].set_linewidth(LW_HAIR)
    ax.tick_params(length=2.2, width=0.6, color=HAIRLINE, labelcolor=TEXT, labelsize=PT_TICK)
    return ax


def boot_ci(x, stat=np.median, n_boot=4000, seed=0, alpha=0.05):
    """Percentile bootstrap CI for any statistic of one sample. Seeded, so the drawn interval
    is reproducible and the panel, this repository's READMEs and the caption cannot disagree."""
    x = np.asarray(x, dtype=float)
    rng = np.random.default_rng(seed)
    draws = rng.choice(x, size=(n_boot, x.size), replace=True)
    vals = stat(draws, axis=1)
    lo, hi = np.percentile(vals, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return float(stat(x)), float(lo), float(hi)
