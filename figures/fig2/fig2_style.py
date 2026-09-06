"""The frozen visual vocabulary of Figure 2. Every panel imports from here; none redefines.

WHY THIS FILE EXISTS
--------------------
Figure 2 answers one question: does a single-cell population carry retrievable information that
its mean signature does not? Seven panels answer it from seven angles, and the reader has to see
them as one answer. That breaks the same two ways Figure 1 broke, so it is settled the same way,
once, here: a colour that means one thing in panel a and another in panel f, and a type size
chosen per panel to make that panel's own crowding go away.

COLOUR: THREE TIERS, AND THE TWO-FAMILY READING THEY REPLACED
------------------------------------------------------------
    MEAN       orange  DIRECTION only: a score that discards response magnitude. Four of the nine
                       scorers on panel a: mean cosine, CMap cosine, CMap WTCS, PCA-latent cosine.
    MAGNITUDE  slate   direction AND magnitude, and nothing higher. One scorer: mean L2.
    POP        blue    the retained cell POPULATION. The other four: global energy, PCA-latent
                       energy, and the two subpopulation-coverage variants.
    SHARED     grey    context, machinery, and anything the tiers have in common.
    FAINT      pale    structure that must be visible without being read.

Until 2026-09-03 this figure had two colours because it argued a two-way split, mean
representation against population representation, and the split was worth colouring because it
SEPARATED: every population scorer's macro-mean Hit@1 sat above every mean scorer's, so panel a's
ladder was sorted by value and grouped by family at once, and fig2a asserted it at draw time.

The magnitude control ended that. mean_l2 is a mean-representation scorer and it reaches 0.788,
above three of the four population scorers; it takes 89 per cent of the step the figure used to
attribute to population structure; and it correlates 0.80 with the energy distance where mean
cosine correlates 0.06. The assertion was removed rather than repaired, and the grouping with it:
what it protected was a property of WHICH mean scorer was in the panel, not of two representation
families. See docs/phase2/FIG2_MAGNITUDE_CONTROL_VERDICT.md, which was written before any panel
was touched, and the TIER map at the foot of this file.

The tiers are assigned by construction, never by result: a cosine discards magnitude whatever it
scores, and a distance between point clouds retains the distribution whatever latent it lives in.
That is what makes panel f's ordering a prediction the matrix can contradict rather than a
restatement of it.

MEAN and POP keep their hues under the new reading because a direction-only scorer is exactly the
mean-family scorer the figure always drew orange, and a population scorer exactly the one it drew
blue. What changed is that a third mark now stands between them.

The first draft of this figure had a different third group, splitting the two CMap baselines off
as "reference". That was dropped for a reason that is about the science rather than about the
palette. The CMap-style cosine baseline applies the same operation to the same mean differential
expression vector as mean cosine and scores identically to it (Spearman rho = 1.000 over 54,180
query-candidate scores, panel f), and CMap WTCS is rank enrichment on the same collapsed
signature. All three are direction-only methods. Colouring them as a separate group would say the
opposite of what panel f measures, in the same figure.

What survives of the distinction is real and is carried by a different channel: the two CMap rows
are PUBLISHED baselines, and panel a marks them with a glyph rather than a hue. Provenance and
what a scorer keeps are two different facts about it, and they get two different channels.

TYPE: A LADDER, NOT A BUDGET
----------------------------
Authored at 6.90 in, the width it prints at, so nominal point size IS printed point size. The
deck-wide floor is 5 pt (figstyle.MIN_PT), which is what production rejects rather than what a
reader can take in. Figure 2 sets its own floor at 6.5 pt, the same as Figure 1, enforced in
fig2_assemble._assert_floor. Reaching it is what the two-panels-per-row layout bought: the
previous cut ran three panels across the same canvas and paid for the third with 5.6 pt.

PT_EQ is derived rather than chosen. Matplotlib renders a mathtext sub/superscript at 0.7x
nominal, so the smallest nominal size whose subscript still clears 6.5 pt is 6.5 / 0.7 = 9.286,
rounded up to 9.3. At the 7.2 pt the rest of the deck uses for mathtext a subscript prints at
5.04 pt, which clears Nature's floor and not this figure's.
"""
from __future__ import annotations

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from figstyle import (COMP_SOFT, FOCAL_SOFT, GREY, INK, LIGHT_GREY, SLATE, TRACK,  # noqa: E402
                      META, RULE, TRACK)

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# ---------------------------------------------------------------------------------- colour
POP = FOCAL_SOFT            # #5185C0  population-level representation
MEAN = COMP_SOFT            # #E99D4E  mean-level / collapsed signature
SHARED = GREY               # #767676  context and machinery
FAINT = LIGHT_GREY          # #D4D4D4  structure visible without being read
BAR_TRACK = TRACK           # #EDEDED  the full-extent track a value bar sits on
HAIRLINE = RULE             # #E6E6E6  group separators, zero rules, axis spines
TEXT = INK                  # all body text; colour carries meaning through MARKS, not letters
SUBTLE = META               # units, n, provenance; never a claim

# Washes, for naming a REGION rather than a mark: panel a's two family bands, panel c's two
# half-planes, panel d's interquartile bands.
#
# The first draft of this comment said "used only behind marks, never behind text that has to be
# read at speed", and three panels then broke it in the same week, each with a stated reason and
# each reported by its auditor rather than hidden. That is a rule nobody could follow, because a
# wash that names a region has to sit behind that region's label or the label belongs to nothing.
# What actually matters is contrast, so the rule is now the measurable one: INK on either wash
# holds about 14:1, so text may sit on a wash, but a wash may never be the only thing separating
# two regions and no COLOURED text may sit on one.
# THE THIRD TIER, ADDED 2026-09-03.
#
# Figure 2 used to argue a two-way split, mean representation against population representation,
# and its colour axis had two hues because the argument had two sides. The magnitude control
# measured on 2026-09-03 ends that: a magnitude-aware mean scorer takes 89 per cent of the step
# the panel attributed to population structure, and it correlates 0.80 with the energy distance
# where mean cosine correlates 0.06 (docs/phase2/FIG2_MAGNITUDE_CONTROL_VERDICT.md). The axis the
# scorers actually separate on is what they KEEP, so the figure now carries three tiers and needs
# a third mark for the middle one.
#
# SLATE is the deck's "filled bar carrying no family semantics", which is exactly what is wanted:
# the magnitude tier is not a third competing family, it is the control that sits between the
# other two. Figure 5 panel b already draws mean_l2 in it, so the two figures agree on sight.
MAGNITUDE = SLATE           # #4F6D7A  direction + magnitude, and nothing higher
BAR_TRACK = TRACK           # #EDEDED  the full-extent track a value bar is drawn on

POP_WASH = "#E4EDF6"
MEAN_WASH = "#FBF0E4"

# ---------------------------------------------------------------------------------- type
PT_LETTER = 9.5             # bold panel letter, drawn by fig2_assemble
PT_TITLE = 8.5              # RETIRED with title(); kept only so the gate can name it
PT_ANNOT = 7.2              # ordinary annotation
PT_TICK = 6.8               # axis tick labels
PT_EQ = 9.3                 # any label containing mathtext; see the note above
PT_SMALL = 6.5              # provenance, n, units. This figure's floor; nothing goes lower.
PT_FLOOR = 6.5

# ---------------------------------------------------------------------------------- weights
LW_HAIR = 0.6               # rules, guides, anything the eye should not stop on
LW_LINE = 1.1               # a plotted series
LW_STEM = 0.9               # a lollipop stem
MS_DOT = 26                 # a point estimate carrying a claim

# ---------------------------------------------------------------------------------- families
# The nine scorers of panel a, by REPRESENTATION. `published` is provenance and is deliberately
# a separate field: see the module docstring. Order within a family is by value at draw time,
# never by this dict.
SCORERS = {
    "global_energy":  dict(label="energy",         family="pop",  published=False),
    "pca_dist":       dict(label="PCA-dist",       family="pop",  published=False),
    "coverage_mean":  dict(label="coverage-mean",  family="pop",  published=False),
    "coverage_worst": dict(label="coverage-worst", family="pop",  published=False),
    "pca_mean":       dict(label="PCA-mean",       family="mean", published=False),
    "cmap_wtcs":      dict(label="CMap WTCS",      family="mean", published=True),
    # NOT marked published. The canonical CMap score is WTCS (above); this row is a cosine
    # applied to the same mean signatures, which is the score the equivalence result concerns
    # and which the main text calls "the implemented CMap-style cosine". Carrying the dagger
    # here would present a cosine baseline built in this study as the canonical CMap score.
    "cmap_cosine":    dict(label="CMap-style cos.", family="mean", published=False),
    "mean_cosine":    dict(label="mean cosine",    family="mean", published=False),
    # The magnitude control. Its family is "mean" because that is what it is computed from; its
    # tier is "magnitude" because that is what it keeps, and after 2026-09-03 the tier is the
    # axis this figure argues along. Keeping both fields is deliberate: panel d still asks which
    # representation a scorer is built on, and that question has not changed.
    "mean_l2":        dict(label="mean L2",        family="mean", published=False),
}
FAMILY_COLOUR = {"pop": POP, "mean": MEAN}
FAMILY_NAME = {"pop": "Population-level", "mean": "Mean-level"}

# What each scorer KEEPS, which is the axis Figure 2 now argues along. Assigned by construction,
# not by result: a cosine discards magnitude whatever it scores, and a distance between point
# clouds retains the distribution whatever latent it lives in.
TIER = {
    "mean_cosine": "direction", "cmap_cosine": "direction", "cmap_wtcs": "direction",
    "pca_mean": "direction",
    "mean_l2": "magnitude",
    "global_energy": "population", "pca_dist": "population",
    "coverage_mean": "population", "coverage_worst": "population",
}
TIER_NAME = {"direction": "direction only", "magnitude": "+ magnitude",
             "population": "+ distribution"}
# The three scorers that carry the argument. Everything else on the panel is a reference point.
PRIMARY = ("mean_cosine", "mean_l2", "global_energy")


# THERE IS NO title() HELPER, AND THAT IS THE POINT.
#
# Every panel used to state one bold phrase over itself: "Every population scorer beats every mean
# scorer", "Gate does not enrich", and five more. Seven conclusion sentences on one page is seven
# claims competing for the reader's attention, and it is not what a Nature-family main figure does:
# the figure carries visual evidence and the legend carries the argument. Each of those phrases now
# opens its panel's caption entry, where it costs no space and can be qualified properly. Figure 3
# was cleared the same way on the same day.
#
# The helper is deleted rather than deprecated, and fig2_assemble._assert_no_titles enforces what
# its absence intends: no panel may draw text above PT_ANNOT. Only four kinds of text are allowed.
#
#   1. the panel letter          drawn by fig2_assemble, not by the panel
#   2. axis and group names      what the quantity is, and what the rows or groups are
#   3. necessary statistics      median, rho, P, n, and the values being compared
#   4. a very short direction    "mean better" / "population better", two or three words
#
# Anything else belongs in the caption. When a panel feels like it needs a sentence, that is the
# signal that the drawing is not carrying its own weight yet.
#
# One casualty is worth naming. Panel a's "+0.448 Hit@1" was set at PT_TITLE, because it is the
# headline number of the whole figure rather than a sentence. It now sets at PT_ANNOT like every
# other statistic. It is still the most prominent thing on that panel, carried by weight, by
# isolation in the right-hand block, and by the bracket that ties it to the two rows it compares,
# rather than by being the only large type on the page.


def zero_rule(ax, x=0.0, vertical=True, color=SUBTLE, lw=0.8, zorder=2, ls="-"):
    """The line a signed quantity is read against. Darker than a spine, because it is a datum."""
    f = ax.axvline if vertical else ax.axhline
    return f(x, color=color, lw=lw, zorder=zorder, ls=ls)


def bare_axes(ax, keep=("left", "bottom")):
    """House axes: hairline spines on the sides that carry a scale, nothing on the others."""
    for side in ("top", "right", "left", "bottom"):
        ax.spines[side].set_visible(side in keep)
        if side in keep:
            ax.spines[side].set_color(HAIRLINE)
            ax.spines[side].set_linewidth(LW_HAIR)
    ax.tick_params(length=2.2, width=0.6, color=HAIRLINE, labelcolor=TEXT, labelsize=PT_TICK)
    return ax


def boot_median_ci(x, n_boot=4000, seed=0, alpha=0.05):
    """Percentile bootstrap CI for a median. Seeded, so the drawn interval is reproducible.

    Every interval in this figure is computed here rather than read from a summary table, so the
    n behind it is the n the panel plots and the two cannot drift.
    """
    x = np.asarray(x, dtype=float)
    rng = np.random.default_rng(seed)
    draws = rng.choice(x, size=(n_boot, x.size), replace=True)
    lo, hi = np.percentile(np.median(draws, axis=1), [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return float(np.median(x)), float(lo), float(hi)
