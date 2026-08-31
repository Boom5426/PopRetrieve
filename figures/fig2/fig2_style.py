"""The frozen visual vocabulary of Figure 2. Every panel imports from here; none redefines.

WHY THIS FILE EXISTS
--------------------
Figure 2 answers one question: does a single-cell population carry retrievable information that
its mean signature does not? Seven panels answer it from seven angles, and the reader has to see
them as one answer. That breaks the same two ways Figure 1 broke, so it is settled the same way,
once, here: a colour that means one thing in panel a and another in panel f, and a type size
chosen per panel to make that panel's own crowding go away.

COLOUR: TWO FAMILIES, AND THE REASON THERE IS NO THIRD
------------------------------------------------------
    POP     blue    a score computed from the RETAINED cell population. Four of the eight
                    scorers on panel a: global energy, PCA-latent energy, and the two
                    subpopulation-coverage variants.
    MEAN    orange  a score computed from a COLLAPSED per-perturbation signature. The other
                    four: PCA-latent cosine, CMap WTCS, CMap cosine, mean cosine.
    SHARED  grey    context, machinery, and anything both families have in common.
    FAINT   pale    structure that must be visible without being read.

The first draft of this figure had three families, splitting the two CMap baselines off as
"reference". That was dropped for a reason that is about the science rather than about the
palette. The CMap-style cosine baseline applies the same operation to the same mean differential
expression vector as mean cosine and scores identically to it (Spearman rho = 1.000 over 54,180
query-candidate scores, panel g), and CMap WTCS is rank enrichment on the same collapsed
signature. All three are mean-representation methods. Colouring them as a separate family would
say the opposite of what panel g measures, in the same figure.

What survives of the distinction is real and is carried by a different channel: the two CMap rows
are PUBLISHED baselines, and panel a marks them with a glyph rather than a hue. Provenance and
representation are two different facts about a scorer, and they get two different channels.

The families are worth colouring at all only because they SEPARATE. Every population-level
scorer's macro-mean Hit@1 (down to 0.589) is above every mean-level scorer's (up to 0.518), so
the ladder in panel a is simultaneously sorted by value and grouped by family, and the grouping
costs the sort nothing. That is a measured property of the data, asserted at draw time in fig2a.

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
from figstyle import (COMP_SOFT, FOCAL_SOFT, GREY, INK, LIGHT_GREY,  # noqa: E402
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
POP_WASH = "#E4EDF6"
MEAN_WASH = "#FBF0E4"

# ---------------------------------------------------------------------------------- type
PT_LETTER = 9.5             # bold panel letter, drawn by fig2_assemble
PT_TITLE = 8.5              # the one phrase a panel is allowed to state over itself
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
# The eight scorers of panel a, by REPRESENTATION. `published` is provenance and is deliberately
# a separate field: see the module docstring. Order within a family is by value at draw time,
# never by this dict.
SCORERS = {
    "global_energy":  dict(label="energy",         family="pop",  published=False),
    "pca_dist":       dict(label="PCA-dist",       family="pop",  published=False),
    "coverage_mean":  dict(label="coverage-mean",  family="pop",  published=False),
    "coverage_worst": dict(label="coverage-worst", family="pop",  published=False),
    "pca_mean":       dict(label="PCA-mean",       family="mean", published=False),
    "cmap_wtcs":      dict(label="CMap WTCS",      family="mean", published=True),
    "cmap_cosine":    dict(label="CMap cosine",    family="mean", published=True),
    "mean_cosine":    dict(label="mean cosine",    family="mean", published=False),
}
FAMILY_COLOUR = {"pop": POP, "mean": MEAN}
FAMILY_NAME = {"pop": "Population-level", "mean": "Mean-level"}


def title(ax, text, x=0.0, y=1.0, ha="left", va="bottom", color=TEXT, weight="bold", **kw):
    """The single phrase a panel states over itself. Everything longer belongs in the caption.

    Drawn ink, not an rc title: figstyle.strip_titles clears rc titles from every composite, and
    this figure wants the phrase to survive that on purpose. It must be literally true of what is
    drawn, short enough for one line at half width, and never a restatement of the axis label.
    """
    return ax.text(x, y, text, transform=ax.transAxes, fontsize=PT_TITLE, ha=ha, va=va,
                   color=color, fontweight=weight, **kw)


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
