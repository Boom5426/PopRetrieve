"""PopRetrieve Figure 2 panel 2f: the Class-A gain belongs to the population-level FAMILY.

WHAT THE PANEL SHOWS
--------------------
Five different population-level scores, paired query by query against mean cosine, all give a
positive median regret reduction whose bootstrap 95% interval excludes zero. The claim is
therefore about the family and not about one lucky distributional metric. It is deliberately no
larger than that: this is a Class-A comparison, the criteria reward correspondence between
response populations, which is the information population-level retrieval uses. Whether the
retrieved neighbours are biologically better is Figure 3's question, not this panel's.

The second thing the panel shows, by arrangement rather than by a label, is that the two
subpopulation-coverage scores sit further right than the three global-distance scores. That
ordering is asserted at draw time so the layout cannot outlive it. It is an ordering of the five
POINT ESTIMATES and nothing stronger: the coverage-mean interval still overlaps the sliced-W
interval, so the panel is not claiming the two sub-families are separated.

WHAT CHANGED IN THE 2026-08-31 RESTRAINT AND RESIZE PASS
--------------------------------------------------------
The panel used to state its conclusion over itself, "All five intervals clear zero", set in ink
above the marks. Seven such sentences on one page is seven competing claims, so fig2_style.title()
was deleted and fig2_assemble._assert_no_titles now refuses to build a figure in which a panel
draws text above PT_ANNOT. That sentence now opens this panel's caption entry. Nothing on the
panel replaces it, and nothing about the data, the statistic, the row order or the colours moved:

  * The phrase is gone and so is COUNT_WORD, the lookup that spelled its "five" out loud. The
    inequality the phrase asserted is NOT gone: every lower bound is still required to exceed
    zero at draw time, which is a stronger guarantee than a sentence, because a sentence can only
    be read while an assertion can fail the build.
  * Because the fact is now carried by POSITION alone, it is also asserted as a printed distance.
    ZERO_CLEAR_PT demands that the nearest lower bound stand at least 4 printed points clear of
    the zero rule on this panel's resolved x scale; the tightest, energy at +0.037, stands 39.4 pt
    clear, so the margin is large, and a future file that halved every gain would still print a
    visible gap rather than five bars leaning on the datum.
  * The box shrank from 2.45 x 1.38 in to 2.45 x 1.06 in. The y ladder was positioned by a
    hardcoded ylim tuned against the old height; it is now RESOLVED at draw time from the axes'
    real printed height, so the note band is reserved in inches, the five rows take what is left,
    and the same file re-tunes itself if the ledger moves again. Printed row pitch is 10.8 pt
    against 14.9 pt before, and the sub-family gap 16.2 pt against 22.4 pt.
  * Two legibility floors were added, because 23 per cent less height is exactly where a ladder
    stops being readable without anything looking wrong: the row pitch must clear the y label
    type size with lead to spare, and the gap between the two sub-family blocks must exceed the
    within-block pitch by enough to still read as a block break.

WHICH FILE IT READS
-------------------
results/exp12_partial_observed_retrieval/per_query_scores.csv, restricted to the rows whose
recommendation_mode is DART_recommended: 627 of the file's 765 queries, each scored by all nine
methods, so 5,643 of its 6,885 rows. Paired on (split_type, cell_line, heldout_drug,
observed_library_fraction, seed), which is the key panel d uses. Panel c adds heldout_MoA to the
same list; each of the 144 held-out drugs in this file carries exactly one MoA, so that field
partitions nothing and the two keys pair the same queries. Regret reduction is
mean_cosine decision_regret minus the population scorer's decision_regret, so positive is better.

This panel previously read figures/source_data/fig2e_classA_robustness.csv, a hand-copied mirror
with no generator. It now reads the authoritative results file, the same correction panel c
received. The mirror is still checked against the recomputation by _crosscheck_mirror(), which
runs in the standalone __main__ block; as of 2026-08-31 the two agree on all five medians and all
five improved fractions exactly (largest median difference 2.8e-17, fractions identical), so
nothing was lost by the move.

n = 627 IS NOT A TYPO FOR PANEL c's 765
---------------------------------------
Panel c reports the headline on ALL 765 partial-observed queries, precisely so the headline is not
taken on a gate-selected subset. This panel reports the per-metric sweep on the 627 queries the
pre-specified gate recommended, which is the subset the sweep was run on. The n is stated on the
panel so the mismatch reads as a scope note rather than as an error.

That 627 was 621 before 2026-09-03. The gate's verdict is computed inside exp12 from quantities
that pass through the energy kernel, so the unbiased estimator moved six queries across the
threshold: 621 / 133 / 11 became 627 / 127 / 11.

JUDGEMENT CALLS A READER COULD REASONABLY DISAGREE WITH
-------------------------------------------------------
1. Rows are ordered by CONCEPTUAL FAMILY, not by value: energy, MMD, sliced-Wasserstein (global
   distances between two populations), then coverage-mean, coverage-worst (subpopulation
   coverage). Sorting by value would have made a tidier ladder and would have hidden the fact
   that the conceptual split and the performance split coincide.
2. The two sub-families are separated by POSITION (a wider gap between the groups) and by SHAPE
   (circle vs square), never by hue: all five are population-level scores and take one colour.
   Neither sub-family is drawn as secondary, which is why both markers are filled rather than one
   open: filled-versus-open would rank them, and this panel is not ranking them. A hairline group
   rule was tried and cut: drawn across the panel it competed with the zero datum, and drawn only
   in the left margin it read as a stray mark. The resize did not bring it back. The block break
   is a RATIO of two spacings, so losing height costs it nothing as long as the ratio holds, and
   GROUP_EXTRA_PT now asserts that it holds in printed points rather than in y units.
3. The sub-families are NOT named on the panel. Their names do not fit beside a 2.45 in plot at
   the 6.5 pt floor, and the y labels already read "coverage-" for the pair, so the naming is left
   to the caption rather than shrunk below the floor.
4. "sliced-W" abbreviates sliced-Wasserstein. Measured at PT_TICK the full word sets 0.79 in
   wide, against 0.87 in between the panel box edge and the right end of the y labels, so on that
   number alone it would fit. It does not fit the column it would have to live in: the assemble
   ledger reserves the leftmost 0.24 in of every panel box for the letter, which leaves 0.63 in,
   and "coverage-worst" at 0.64 in is already at that limit. The caption spells the word out.
5. The per-metric improved fractions (0.601, 0.605, 0.618, 0.644, 0.720 as of 2026-08-31) are
   computed here but not drawn. A second numeric column would fill the empty right half of the
   three distance rows, which is the emptiness that makes the coverage pair's rightward offset
   visible. That was true at 1.38 in and it is more true at 1.06 in.
6. The interval is a seeded percentile bootstrap of the median (fig2_style.boot_median_ci,
   4000 resamples, seed 0). Its endpoints move in the third decimal between seeds; the fact the
   panel rests on, that every lower bound is above zero, holds with margin (the tightest is
   energy at +0.037). What the interval IS stays named ON the panel rather than moving to the
   caption with the deleted phrase: an interval whose definition is unstated cannot be read at
   all, so the note is a statistic definition and not a conclusion. Panel d names its interval
   on-panel for the same reason.
7. The note keeps the headroom, and the marks pay for it. Two lines at the 6.5 pt floor set
   0.23 in of type, and with the air above them and the gap below the reserved band is 0.32 in of
   a 1.06 in box, just under a third of the panel. Moving the note under the x axis was
   tried and abandoned: the bottom pad in the assemble ledger is spent on the tick labels and the
   two-line axis name, so a note there would have overhung the panel box and enlarged the page.
   Splitting the note into the pocket right of the three distance rows was also abandoned: that
   pocket measures 1.08 in across and the note's first line measured 1.47 in when it still ended
   in "queries". Both lines were trimmed on 2026-09-03 to 1.17 and 1.09 in, to make room for the
   series labels on the same two lines; see the guard at the foot of draw_2e.
8. There is no direction hint such as "population better". The x axis name says the quantity is a
   regret REDUCTION against mean cosine, which fixes the sign, and this panel is the fifth place
   in the figure a reader meets that convention. A three-word hint would have cost another line
   of the headroom the note is already competing for.

Palette comes from fig2_style; do NOT re-declare hex values here. Every panel file used to carry
its own copy, which made figstyle's "one edit here recolours the whole deck" untrue: a recolour
meant editing 43 files and missing one was silent.

Run standalone: python fig2e.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import RendererAgg

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fig2_style import (LW_HAIR, MEAN, MS_DOT, POP, PT_SMALL, PT_TICK, REPO,  # noqa: E402
                        SUBTLE, TEXT, bare_axes, boot_median_ci, zero_rule)

# The tether to zero, at half strength against white. Derived from the row's own colour rather
# than declared as a hex, so a recolour of either family carries it. It has to be visible without
# competing with the interval: at equal weight the stem plus the interval read as one bar, which
# is the chart type this panel exists to avoid.
#
# ONE TINT PER SERIES since 2026-09-04, not one for the panel. There was a single STEM_TINT, mixed
# from POP, and both rows used it: the upper row's interval and marker are MEAN orange and its
# tether to zero was drawn in the blue of the OTHER series. On a panel whose entire key is "orange
# is the comparison against direction-only, blue is the comparison against magnitude-aware", that
# put one series' hue inside the other's row.
def _tint(colour):
    return tuple(0.45 * np.array(mcolors.to_rgb(colour)) + 0.55)


STEM_TINT_MEAN = _tint(MEAN)
STEM_TINT_POP = _tint(POP)

SRC = f"{REPO}/results/exp12_partial_observed_retrieval/per_query_scores.csv"
MIRROR = f"{REPO}/figures/source_data/fig2e_classA_robustness.csv"

QUERY_KEY = ["split_type", "cell_line", "heldout_drug", "observed_library_fraction", "seed"]
# TWO baselines since 2026-09-03, not one. Against mean cosine a population scorer is credited
# with everything it gains over a scorer that discarded response magnitude, and that is not
# evidence about population structure: the magnitude control takes 89 per cent of the equivalent
# step in panel a and correlates 0.80 with the energy distance in panel f. The reduction against
# the magnitude-aware mean is the one that can be called distribution-specific, so it is the one
# drawn in full ink. See docs/phase2/FIG2_MAGNITUDE_CONTROL_VERDICT.md.
BASELINE = "mean_cosine"             # the apparent gain
BASELINE2 = "mean_l2"                # the distribution-specific residue
MODE = "DART_recommended"
N_QUERIES = 627                      # the gate-recommended subset; see the module docstring

# Finalized Package 2 formal values for the reader-facing panel. These are copied from the
# existing cluster-aware audit table; drawing the panel does not recompute the inference.
FORMAL_N_QUERIES = 584
FORMAL_N_DRUGS = 141
FORMAL_STATS_MEAN_COSINE = {
    "DART_energy": (0.060016, 0.041631, 0.088902),
    "DART_mmd": (0.066340, 0.044996, 0.090287),
    "DART_sliced_wasserstein": (0.067636, 0.040340, 0.092432),
    "DART_coverage_mean": (0.044729, 0.019844, 0.064797),
    "DART_coverage_worst": (0.030419, 0.016422, 0.053867),
}
FORMAL_STATS_MEAN_L2 = {
    "DART_energy": (0.0, 0.0, 0.0),
    "DART_mmd": (0.0, 0.0, 0.0),
    "DART_sliced_wasserstein": (0.0, -0.001333, 0.0),
    "DART_coverage_mean": (-0.032430, -0.052012, -0.017206),
    "DART_coverage_worst": (-0.043813, -0.060337, -0.030712),
}

# (method column, y label, marker). Conceptual order, never value order: the three global
# distances between two populations first, then the two subpopulation-coverage scores.
DISTANCES = [("DART_energy", "energy"),
             ("DART_mmd", "MMD"),
             ("DART_sliced_wasserstein", "sliced-W")]
COVERAGE = [("DART_coverage_mean", "coverage-mean"),
            ("DART_coverage_worst", "coverage-worst")]

# The caption entry that took over the deleted on-panel phrase counts the rows out loud: "five
# population-level scores ... All five 95% bootstrap intervals exclude zero". COUNT_WORD used to
# keep that count honest by spelling it from the drawn data. With the phrase gone the count is no
# longer written anywhere on the panel, so it is pinned here instead: a sixth scorer added below
# would otherwise leave the caption quietly wrong.
N_ROWS = 5

# The y LADDER, in abstract units, top row first. The 1.5 gap between the last distance row and
# the first coverage row against a pitch of 1.0 within a block is what makes the two sub-families
# read as two blocks. These are ratios only: the inches they resolve to come from the axes.
Y_POS = [4.5, 3.5, 2.5, 1.0, 0.0]
# The scale now has to hold both baselines, and the residue against the magnitude-aware mean is
# negative for the two coverage scorers, so the left end is no longer a hair below zero.
X_MIN, X_MAX = -0.075, 0.115

# ------------------------------------------------------------------------------ geometry, inches
# Resolved against the axes' real printed height at draw time, so the ledger in fig2_assemble.py
# stays the single place the panel box is set. Nothing here is a fraction of the old 1.38 in box.
NOTE_TOP_IN = 0.02     # air above the two-line note, inside the axes
NOTE_LINESP = 1.25     # line spacing of the note, in multiples of its 6.5 pt type
NOTE_GAP_IN = 0.075    # air between the note's last line and the top row's marker. The marker is
                       # about 0.040 in of ink from its centre, so this leaves about 2.5 printed
                       # points of white; below that the note reads as a label of the energy row
BOTTOM_IN = 0.065      # air under the bottom row, so its marker does not sit on the x spine
RULE_HEAD = 0.5        # how far the zero datum reaches above the top row, in ladder units. It is
                       # trimmed rather than run to the axes top: at this height the reserved note
                       # band is 30 per cent of the box, and a full-height rule spent that third
                       # of its length as the strongest ink on the panel, next to no data at all,
                       # where it read as a second spine. fig3c trims both ends of its zero rule
                       # for the same reason; fig3d trims only the foot, because a wash reaches
                       # its axes top and the rule has data beside it the whole way up

# With no sentence over the panel, what the reader must take from POSITION alone is asserted as a
# printed distance on the resolved scale, the way panel 3h asserts its three.
ZERO_CLEAR_PT = 4.0    # printed points demanded between the zero rule and the nearest lower
                       # bound. The rule is 1.0 pt wide and the interval ends in a round cap on a
                       # 1.4 pt line, so ink meets ink at 0.5 + 0.7 = 1.2 pt of centre-to-centre.
                       # The floor sits well above that on purpose: with no text saying the
                       # intervals clear zero, the panel has to show a gap a reader SEES, not
                       # merely a gap that measures greater than nothing
LEAD_PT = 2.0          # printed points of lead demanded between two y labels, on top of their own
                       # 6.8 pt type size
BAND_CLEAR_PT = 4.0    # printed points of air demanded around a series label in the note band:
                       # from the note when the two share a line, and from the zero rule, which
                       # reaches up into the band. Measured at 9.2 and 5.4 pt as drawn
GROUP_EXTRA_PT = 3.0   # printed points by which the sub-family gap must exceed the within-block
                       # row pitch. Under this the block break reads as an uneven row rather than
                       # as a break, and the arrangement stops carrying judgement call 2


def paired_gains(baseline: str = BASELINE) -> "dict[str, np.ndarray]":
    """Per-query regret reduction of each population scorer against ``baseline``, on the subset.

    Returns one array per method, all of length N_QUERIES and all indexed by the same queries.
    """
    d = pd.read_csv(SRC)
    d = d[d["recommendation_mode"] == MODE]
    base = d[d["method"] == baseline].set_index(QUERY_KEY)["decision_regret"]
    assert base.index.is_unique, f"{baseline} is not one row per query on the recommended subset"

    out = {}
    for method, _ in DISTANCES + COVERAGE:
        s = d[d["method"] == method].set_index(QUERY_KEY)["decision_regret"]
        assert s.index.is_unique, f"{method} is not one row per query"
        j = pd.concat([base.rename("base"), s.rename("pop")], axis=1).dropna()
        assert len(j) == N_QUERIES, f"expected {N_QUERIES} paired queries for {method}, got {len(j)}"
        out[method] = (j["base"] - j["pop"]).to_numpy()
    return out


def draw_2e(ax):
    """Five population-level scores, median regret reduction vs mean cosine with bootstrap CIs."""
    stats = FORMAL_STATS_MEAN_COSINE
    stats2 = FORMAL_STATS_MEAN_L2

    # Against DIRECTION-ONLY mean cosine every interval clears zero, which is what this panel
    # used to say and still says. It is now the secondary series.
    lows = {m: lo for m, (_, lo, _) in stats.items()}
    assert all(lo > 0 for lo in lows.values()), f"an interval touches zero: {lows}"
    # And against the MAGNITUDE-AWARE mean it does not, which is the panel's subject. The
    # assertion is the finding: if a distributional scorer ever does clear zero here, the claim
    # this panel makes has changed and the caption must change with it.
    assert not all(lo > 0 for _, lo, _ in stats2.values()), (
        "every distribution-specific interval now clears zero against the magnitude-aware mean; "
        "that would be a positive result and this panel is drawn for a null one")
    both = [x for _, lo, hi in list(stats.values()) + list(stats2.values()) for x in (lo, hi)]
    assert X_MIN < min(both) and max(both) < X_MAX, (
        f"a bound runs past the drawn scale [{X_MIN}, {X_MAX}]: [{min(both):.4f}, {max(both):.4f}]")

    rows = [(m, lab, "o") for m, lab in DISTANCES] + [(m, lab, "s") for m, lab in COVERAGE]
    # zip() below would silently drop rows past the end of Y_POS, leaving the panel drawing fewer
    # scorers than it read and fewer than the caption counts.
    assert len(rows) == len(Y_POS), f"{len(rows)} scorers but {len(Y_POS)} y positions"
    assert len(rows) == N_ROWS, (
        f"the panel draws {len(rows)} scorers and the Fig. 2 caption entry for f says {N_ROWS}. "
        f"Edit the caption in the same commit as this constant, or the figure and its legend "
        f"disagree on how many scores the claim covers.")

    # ---- resolve the ladder against the printed box ------------------------------------------
    fig = ax.figure
    axw = ax.get_position().width * fig.get_figwidth()
    axh = ax.get_position().height * fig.get_figheight()
    note_h = 2 * PT_SMALL * NOTE_LINESP / 72.0          # two lines of note, in inches
    top_in = NOTE_TOP_IN + note_h + NOTE_GAP_IN         # axes top down to the top row's centre
    rows_in = axh - top_in - BOTTOM_IN                  # what is left for the five rows
    span = max(Y_POS) - min(Y_POS)
    assert rows_in > 0.30, (
        f"panel f is {axh:.2f} in tall and the note band plus the pads take {axh - rows_in:.2f} "
        f"in of it, leaving {rows_in:.2f} in for five rows. Shorten the note or take the height "
        f"back from the ledger; do not shrink the type.")
    unit_in = rows_in / span                            # inches per unit of the Y_POS ladder

    pitch_pt = 72.0 * unit_in * min(abs(a - b) for a, b in zip(Y_POS, Y_POS[1:]))
    group_pt = 72.0 * unit_in * max(abs(a - b) for a, b in zip(Y_POS, Y_POS[1:]))
    assert pitch_pt >= PT_TICK + LEAD_PT, (
        f"the rows print {pitch_pt:.1f} pt apart and each y label is {PT_TICK} pt tall, which "
        f"leaves under the {LEAD_PT:.1f} pt of lead five stacked labels need. The panel is too "
        f"short for five rows at this type size.")
    assert group_pt >= pitch_pt + GROUP_EXTRA_PT, (
        f"the sub-family gap prints {group_pt:.1f} pt against a row pitch of {pitch_pt:.1f} pt, "
        f"short of the {GROUP_EXTRA_PT:.1f} pt that keeps it reading as a block break rather "
        f"than as an uneven row.")

    scale_x = axw / (X_MAX - X_MIN)                     # inches per unit of regret reduction
    clear_pt = 72.0 * scale_x * min(lows.values())
    assert clear_pt >= ZERO_CLEAR_PT, (
        f"the nearest lower bound stands {clear_pt:.1f} printed pt from the zero rule, under the "
        f"{ZERO_CLEAR_PT:.1f} pt floor. No text on this panel says the intervals clear zero, so "
        f"the gap has to be visible; widen the panel or narrow the drawn scale.")

    # Zero first and darkest: it is the datum every point is read against, not a gridline. It
    # runs from the x spine, where the "0" tick names it, to just over the top row, and no
    # further: an axvline's y data is in AXES fraction, so the reach is resolved from the limits
    # computed above rather than from the data.
    y_lo = min(Y_POS) - BOTTOM_IN / unit_in
    y_hi = max(Y_POS) + top_in / unit_in
    rule = zero_rule(ax, 0.0, color=TEXT, lw=1.0, zorder=2)
    rule.set_ydata([0.0, (max(Y_POS) + RULE_HEAD - y_lo) / (y_hi - y_lo)])

    # Two series per row, offset so neither hides the other. The upper, in the mean colour, is
    # the gain over direction-only mean cosine; the lower, in full population ink, is what
    # survives once the magnitude-aware mean is the reference. The reader is meant to compare
    # them vertically within a row, which is why they share a row rather than a panel.
    DY = 0.22
    for y, (method, _, marker) in zip(Y_POS, rows):
        med, lo, hi = stats[method]
        ax.plot([0.0, med], [y + DY, y + DY], color=STEM_TINT_MEAN, lw=LW_HAIR,
                solid_capstyle="butt", zorder=3)
        ax.plot([lo, hi], [y + DY, y + DY], color=MEAN, lw=1.1, solid_capstyle="round", zorder=4)
        ax.scatter([med], [y + DY], s=MS_DOT * 0.6, marker=marker, color=MEAN, linewidths=0.5,
                   edgecolors="white", zorder=5)

        med2, lo2, hi2 = stats2[method]
        ax.plot([0.0, med2], [y - DY, y - DY], color=STEM_TINT_POP, lw=LW_HAIR,
                solid_capstyle="butt", zorder=3)
        ax.plot([lo2, hi2], [y - DY, y - DY], color=POP, lw=1.4, solid_capstyle="round", zorder=4)
        ax.scatter([med2], [y - DY], s=MS_DOT, marker=marker, color=POP, linewidths=0.6,
                   edgecolors="white", zorder=5)

    bare_axes(ax, keep=("bottom",))
    ax.set_yticks(Y_POS)
    ax.set_yticklabels([lab for _, lab, _ in rows], fontsize=PT_TICK, color=TEXT)
    ax.tick_params(axis="y", length=0, pad=2.0)
    ax.set_ylim(y_lo, y_hi)
    ax.set_xlim(X_MIN, X_MAX)
    ax.set_xticks([-0.05, 0.0, 0.05, 0.10])
    ax.set_xticklabels(["\u22120.05", "0", "0.05", "0.10"])
    ax.set_xlabel("median regret reduction, paired by query", linespacing=1.2)

    # Scope note in the band reserved for it above the top row, where it crosses no mark. It says
    # n and it says WHICH n, because panel c's 765 is a different and deliberate scope, and it
    # says what the interval is, because an unnamed interval cannot be read.
    n_drawn = FORMAL_N_QUERIES
    note = ax.text(1.0, 1.0 - NOTE_TOP_IN / axh,
                   f"formal n = {FORMAL_N_QUERIES}; {FORMAL_N_DRUGS} drug clusters\n"
                   "interval: cluster-bootstrap 95% CI",
                   transform=ax.transAxes, ha="right", va="top", fontsize=PT_SMALL, color=SUBTLE,
                   linespacing=NOTE_LINESP)
    # Direct labels for the two series, in the left half of the note band above the top row.
    # Beside the rows they landed on the top row's own markers, which are the widest on the panel.
    labels = [ax.text(X_MIN + 0.004, max(Y_POS) + dy, txt, ha="left", va="center",
                      fontsize=PT_SMALL, color=col)
              for dy, txt, col in ((0.78, "vs direction-only", MEAN),
                                   (0.36, "vs magnitude-aware", POP))]

    # THE NOTE BAND HOLDS FOUR STRINGS AND A RULE, AND NOTHING WAS MEASURING THEM, until
    # 2026-09-03. When the second baseline entered the panel the series labels gained a word each
    # and the note gained its second line, and the printed figure then carried two overlaps at
    # once: "vs magnitude-aware mean" ran through "interval: bootstrap 95% CI of the median", and
    # it also ran through the zero rule. Every one of those marks had a stated reason to be where
    # it was and none had a way to notice the others, which is what this checks.
    #
    # The note is what gave way, not the labels: it is provenance, they are the key without which
    # two series in two colours cannot be told apart. "queries" came off the first line (the x
    # axis name already says the pairing is by query) and "of the median" off the second (the same
    # axis name already says the quantity is a median), which bought 0.30 in. What each interval
    # IS still stands on the panel, per judgement call 6.
    r = RendererAgg(int(fig.get_figwidth() * fig.dpi), int(fig.get_figheight() * fig.dpi), fig.dpi)
    note_bb = note.get_window_extent(renderer=r)
    rule_x = ax.transData.transform((0.0, 0.0))[0] - 0.5 * rule.get_linewidth() / 72.0 * fig.dpi
    for t in labels:
        bb = t.get_window_extent(renderer=r)
        # ...against the zero rule, which reaches RULE_HEAD above the top row and so runs up
        # through the band. Both labels sit left of it and both had to be shortened to stay there:
        # the word "mean" came off each, and it is recoverable from the x axis name and from
        # panel a, where the same two scorers carry the same two tier words.
        rule_gap_pt = 72.0 * (rule_x - bb.x1) / fig.dpi
        assert rule_gap_pt >= BAND_CLEAR_PT, (
            f"the series label {t.get_text()!r} runs to within {rule_gap_pt:.1f} pt of the zero "
            f"rule, under the {BAND_CLEAR_PT:.1f} pt floor; the rule reaches into the band, so a "
            f"label that wide is drawn THROUGH the panel's datum.")
        # ...and against the note, when the two share a line of the band.
        if bb.y1 < note_bb.y0 or note_bb.y1 < bb.y0:      # different lines, no shared band
            continue
        gap_pt = 72.0 * (note_bb.x0 - bb.x1) / fig.dpi
        assert gap_pt >= BAND_CLEAR_PT, (
            f"the note and the series label {t.get_text()!r} share a line of the band and stand "
            f"{gap_pt:.1f} pt apart, under the {BAND_CLEAR_PT:.1f} pt floor. Shorten the NOTE, "
            f"not the labels: the labels are the only key to which series is which.")
    return {"stats": stats, "pitch_pt": pitch_pt, "group_pt": group_pt, "zero_clear_pt": clear_pt}


def _crosscheck_mirror():
    """Compare the recomputation against the hand-copied source_data mirror. Reports, not silent."""
    gains = paired_gains()
    mir = pd.read_csv(MIRROR).set_index("method")
    worst_med, worst_frac = 0.0, 0.0
    for method, _ in DISTANCES + COVERAGE:
        g = gains[method]
        worst_med = max(worst_med, abs(float(np.median(g)) - float(mir.loc[method, "median_regret_reduction"])))
        worst_frac = max(worst_frac, abs(float((g > 0).mean()) - float(mir.loc[method, "frac_improved"])))
        if int(mir.loc[method, "n"]) != len(g):
            print(f"  n moved for {method}: mirror {int(mir.loc[method, 'n'])}, now {len(g)} "
                  f"(the gate-recommended subset itself changed under the estimator repair)")
    # REPORTED, NOT ASSERTED, since 2026-09-03. The mirror is a hand-built view of the run that
    # preceded the estimator repair, so it holds V-statistic numbers; asserting agreement with it
    # would pin this panel to the biased estimator it was repaired away from. The difference is
    # printed so the size of the reissue is visible rather than hidden.
    print(f"mirror crosscheck (pre-repair view, reported not asserted): "
          f"max |median| diff {worst_med:.2e}, max |frac| diff {worst_frac:.2e}")


if __name__ == "__main__":
    # The standalone canvas reproduces the assemble ledger's panel f box, 2.45 x 1.06 in of axes
    # inside a 3.45 in half-row with a 0.90 in left pad and a 0.48 in bottom pad, so that what is
    # previewed here is what prints. fig2_assemble.py remains the authority on those numbers.
    _crosscheck_mirror()
    FIGW_, FIGH_, LEFT_, BOTTOM_ = 3.45, 1.54, 0.90, 0.48
    fig = plt.figure(figsize=(FIGW_, FIGH_))
    ax = fig.add_axes([LEFT_ / FIGW_, BOTTOM_ / FIGH_,
                       (FIGW_ - LEFT_ - 0.10) / FIGW_, (FIGH_ - BOTTOM_) / FIGH_])
    info = draw_2e(ax)
    print(f"row pitch {info['pitch_pt']:.1f} pt, sub-family gap {info['group_pt']:.1f} pt, "
          f"nearest lower bound {info['zero_clear_pt']:.1f} pt clear of zero")
    fig.savefig(os.path.join(os.path.dirname(__file__), "2e.png"), dpi=200)
    print("wrote 2e.png")
