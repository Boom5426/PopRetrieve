"""The frozen visual vocabulary of Figure 4. Every panel imports from here; none redefines.

WHY THIS FILE EXISTS, AND WHY IT ARRIVED LAST
---------------------------------------------
Figures 1, 2 and 3 each got one of these; Figure 4 did not, and by 2026-08-31 the difference was
measurable rather than a matter of tidiness. This figure was still running on the deck defaults,
which set a 5 pt production floor and a (8, 7, 6) type ladder, while its three neighbours had moved
to a 6.5 pt floor and a (8.5, 7.2, 6.8) ladder. The result: 336 text artists below 6.5 pt, 21 of
them at exactly 5.0 pt, which is what Nature Portfolio REJECTS rather than what a reader can take
in at 183 mm. A reader turning from Figure 3 to Figure 4 watched the type shrink.

WHAT THIS FIGURE ARGUES, AND THEREFORE WHAT ITS COLOURS MEAN
------------------------------------------------------------
Figure 4 asks whether an external evaluator is automatically neutral, and answers no twice: from
inside a synthetic benchmark where the oracle is known and circularity can be MEASURED rather than
argued about, and from outside, by checking a benchmark we constructed against tissue nobody
assembled. So its colour axis is not population versus mean; it is what a number was computed FROM.

    POP     blue    distributional / population-level retrieval, and the observable, honest arm
                    of a comparison: features available at query time, an out-of-fold estimate.
    MEAN    orange  mean-signature retrieval, and the evaluator-derived, circular arm: features
                    that saw the oracle, an in-sample or leaky estimate.
    EXT     green   an external readout or a control that performs no retrieval.
    SHARED  grey    context, machinery, reference lines, thresholds, and anything neither arm.

The blue/orange pairing therefore carries two related meanings in this figure, population versus
mean and honest versus circular, and they line up: the leaky arm of panel b is the same orange as
the mean-signature bars of panel c, because in both cases the number is inflated by information the
method should not have had. That is the figure's whole subject, so the reuse is deliberate. It is
recorded here because it is the kind of overload that becomes a lie if a later panel uses orange
for a third thing.

TYPE
----
Authored at 6.90 in, the width it prints at, so nominal point size IS printed point size.
PT_FLOOR is 6.5, asserted in fig4_assemble._assert_floor. Mathtext is measured at its effective
0.7x, which is why PT_EQ is 9.3 and not the 7.2 the deck's other figures use for mathtext.

There is no title() helper here, and there never was: this figure's panels have never stated their
own conclusions. fig4_assemble._assert_no_titles keeps it that way, capping panel text at PT_ANNOT
so a phrase cannot arrive later.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from figstyle import (COMP_SOFT, FOCAL_SOFT, GREEN_SOFT, GREY, INK,  # noqa: E402
                      LIGHT_GREY, META, RULE, TRACK)

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# ---------------------------------------------------------------------------------- colour
POP = FOCAL_SOFT            # #5185C0  population-level, and the observable / honest arm
MEAN = COMP_SOFT            # #E99D4E  mean-signature, and the evaluator-derived / circular arm
EXT = GREEN_SOFT            # #55966B  external readout, or a control that performs no retrieval
SHARED = GREY               # #767676  context, thresholds, reference lines
FAINT = LIGHT_GREY          # #D4D4D4  structure visible without being read
BAR_TRACK = TRACK
HAIRLINE = RULE
TEXT = INK
SUBTLE = META

POP_WASH = "#E4EDF6"
MEAN_WASH = "#FBF0E4"

# ---------------------------------------------------------------------------------- type
PT_LETTER = 9.5             # bold panel letter, drawn by fig4_assemble
PT_ANNOT = 7.2              # ordinary annotation, and the cap on all panel text
PT_TICK = 6.8               # axis tick labels
PT_EQ = 9.3                 # any label containing mathtext; 6.5 / 0.7 = 9.286
PT_SMALL = 6.5              # provenance, n, units. This figure's floor.
PT_FLOOR = 6.5
PT_TITLE = 8.5              # passed to apply_style only; no panel may draw at this size

# ---------------------------------------------------------------------------------- weights
LW_HAIR = 0.6
LW_LINE = 1.1
MS_DOT = 26
