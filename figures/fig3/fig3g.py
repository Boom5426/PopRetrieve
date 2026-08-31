"""PopRetrieve Figure 3 panel 3g: on real data the coverage gain is a tail, not a shift.

WHAT THIS PANEL SHOWS
---------------------
Across 239 real-data retrieval tasks the population-minus-mean minority-coverage difference sits
on zero. The constructed cross-line mixtures average +0.00426, ten times the next largest dataset
mean (Frangieh, +0.00042), yet only 17.8 per cent of their tasks are above zero and 81.1 per cent
are exact ties; the natural within-line tasks average +0.00038 with 55.6 per cent above zero. A
mean of a handful of large positives is not an advantage held broadly, and the panel is built so
the two cannot be confused: the per-task dots and the task-split bar are drawn beside the mean,
never instead of it.

THE 2026-08-31 PASS: A PANEL STATES NO CONCLUSION
-------------------------------------------------
This panel used to set one bold phrase over itself, "Largest mean, smallest share above zero".
Thirteen such phrases on one page is thirteen claims competing for attention, so every one of them
moved into the caption and fig3_style.title() was deleted; fig3_assemble._assert_no_titles now
refuses to build a figure in which any panel draws text above PT_ANNOT. What is left here is the
four permitted kinds of text: axis and column names, the computed means, the dagger key, and the
two-word direction hints.

Four things followed from the deletion, and they are the substance of this revision.

  * THE PHRASE WAS DOING WORK, AND THE DRAWING HAS TAKEN IT OVER. It was the only thing naming
    the task-split bar and the only thing naming the number beside it. The summary column now
    carries its own two headers, "share of tasks" and "mean", so the bar is readable as a
    proportion of tasks rather than as an unexplained mark, and the "mean" header carries a
    diamond so that the mark drawn at each row's mean is keyed to the number beside it: without
    it the diamond is an unnamed summary sitting on zero while the column prints +0.00426, which
    is a contradiction until the reader knows both are the mean at different scales. The
    relationship the phrase asserted is still asserted in code (see the top_mean / fewest_pos
    check), where it guards the caption instead of a title.
  * THE RELATIONSHIP MUST BE VISIBLE, NOT ONLY TRUE. The positive segments are drawn last in each
    bar, so they share a right edge across all five rows and their lengths compare directly; the
    means are right-aligned in a column beside them. A drawn-inches assertion now refuses to build
    if the smallest positive share is not visibly shorter than the next smallest, because a reader
    who is no longer told the relationship has to be able to see it.
  * n MOVED TO THE CAPTION. The x label named 239 tasks because the title band was full; the band
    is no longer full, but per-panel n belongs in the caption, and the right-hand column now
    carries the mean only. Per-dataset n was already caption material, for the reason in
    judgement call 4.
  * THE ROWS GAINED 0.08 in, from 0.68 to 0.76 in of axes height, and it is spent on marks: more
    vertical room per row for the jittered dots, a larger dot and mean diamond, and a taller
    task-split bar whose positive tip is now legible on the cross-line row where it is shortest.

SHARE, NOT COUNT, AND THE CODE STILL SAYS SO. Cross-line has the smallest SHARE above zero (16 of
90, 17.8 per cent) but not the smallest COUNT: CD34+ has 6 of 12. An earlier title read "fewest
tasks above zero", which is false on the count reading and true only once a denominator is chosen.
That is the precise error this paper exists to criticise, so the assertion names the share, the
bar draws the share, the column header says "share of tasks", and judgement call 4 records that
the bar carries no n.

Source data: results/exp13_real_data_projection/projection.csv (the only file this module reads).
Gain per task = observed_dart_minority_cov - observed_mean_minority_cov.
Every number drawn here is computed from that file at draw time; none is a literal.
Run standalone: python fig3g.py

HISTORY THIS FILE MUST NOT LOSE
-------------------------------
This panel has been wrong four times, and every correction is preserved as a guard in the code.

  v1: titled "37 real tasks all mean-sufficient", axis label hard-coded "(0 / 37
      PopRetrieve-dominant)". 37 is the task count of exp13's QUICK *sanity* configuration; the
      FULL configuration builds 239, and a sanity run had been quoted as the real-data result.
      The length guard below is what remains of that error.

  v2: "11 of 215 are distributionally dominant". Wrong denominator (the like-for-like figure is
      11 of 239), and worse, it presented a count of threshold crossings as a finding. The 0.01
      threshold sits at 0.77 sd of the nonzero-difference distribution, i.e. INSIDE its noise
      band, and the seed in exp13 is not a replicate (it re-draws which drugs are tested and
      re-clusters the minority subpopulation). Under resampling only 2 of the 10 threshold
      crossing cross-line tasks survive, while drugs that do NOT cross in the recorded run cross
      it in 1 to 4 of 10 resamples (median 3). No count of threshold crossings is drawn here.
      That control range is itself a correction: R13 first reported it as "2 to 4 of 10" from a
      control set selected by task_id, whose :sN suffix let a drug appear in both the dominant
      set and its own control. See CORRECTIONS.md R13, which is the authority for both numbers.

  v3 (2026-07-26): the distribution replaced a 5 x 90 heat map on which 43 per cent of cells were
      white on white and the only legible thing was the outlier.

  v4: v3 printed one dot per task and one mean diamond per row, and the mean diamond was the only
      summary. On this data that says the opposite of what the tasks say: the largest mean belongs
      to the row with the smallest share of tasks above zero. The share of tasks on each side of
      zero is now drawn as well. v3 also coloured each dot blue or orange by the SIGN of its own
      difference, which is the error fig3_style was written to stop: blue ink means a
      population-level object, never a difference that happens to be positive. The dots are SHARED
      grey and the sign lives in the half-plane wash behind them.

  v5 (this pass): the note under judgement call 6 said that at four decimals "two of the five
      datasets print as +0.0000". That is not true of this data and never was: only the predicted
      row does (+0.00003). The real cost of four decimals is a COLLISION, Frangieh (+0.00042) and
      within-line (+0.00038) both printing +0.0004, which would make two datasets look identical
      in the one column a reader compares. The note is corrected and the requirement is now
      asserted rather than argued: the printed strings must be distinct across rows and must each
      round-trip to the computed mean.

JUDGEMENT CALLS A READER COULD REASONABLY DISAGREE WITH
-------------------------------------------------------
1.  THE VIEW IS SYMMETRIC AT +/- 0.18, about twice the largest task (+0.0867). Zero is the visual
    centre because the sign is the quantity being read, and the room on both sides of it is the
    point: it is what lets the reader see how tightly the tasks hug zero. The width is not free
    padding, though. The right quarter of the axes carries the summary column, and 0.18 is the
    smallest symmetric limit at which no task is drawn underneath a label. This is asserted below,
    so a change in the data cannot silently slide a dot under the text. The cost is real and is
    the panel's main compromise: 92 per cent of tasks fall within |0.005|, a band 0.010 wide on
    a drawn range of 0.36 and so 2.8 per cent of the width, which makes the per-task dots a dense
    smear at zero rather than a separable swarm. That smear is the honest shape of this result at
    a symmetric linear scale, and no transform (symlog, a broken axis, a cropped view) is used to
    make the small differences look larger than they are.
2.  THE JITTER IS SEEDED UNIFORM NOISE, NOT A BEESWARM. A beeswarm cannot spread coincident
    points along x without falsifying their values, so it spreads them along the ROW axis, and
    that is the axis this panel has none of. The largest exact-zero column is the 73 cross-line
    ties; at the drawn dot diameter (area 3.2 pt^2, so 2.02 pt = 0.028 in) stacking them clear of
    one another needs about 2.0 in, against the 0.078 in of jitter band a row actually has
    (2 x JITTER row units at 0.131 in per row unit) and 0.76 in for all five rows together.
    About three of the 73 would separate. Overlap and alpha carry density instead, so the reader
    can see mass but cannot count dots. The counts are therefore given as the task-split bar,
    not left to the eye.
3.  THE TASK-SPLIT BAR GIVES EXACT TIES THEIR OWN SEGMENT. 102 of the 239 tasks have a difference
    of exactly zero: both methods select the same candidate. Folding those into either side, or
    reporting only "per cent > 0", would misstate the split, most severely for the cross-line
    row where the ties are 81 per cent. The bar is a share of TASKS and its width is not on the
    x scale; it is placed in a reserved column, past every dot, for that reason. Its three shares
    sum to one, so the bar always fills the reserved width and its total length says nothing.
    The hairline frame is NOT what makes the pale tie segment read as a segment rather than a
    gap: it is drawn in FAINT, the tie segment's own fill colour, so against that segment it is
    invisible, and what separates the tie from white is the fill itself. What the frame draws is
    the reserved track, and with it the shared right edge the five positive segments are compared
    against, as a line rather than as the coincidence of five fills. It costs each bar 0.2 pt at
    each end, 0.0023 in, which is the same at every row and so leaves the comparison intact.
    A share this small does not resolve, and the panel does not pretend otherwise: the cross-line
    negative share is 1 of 90, which is 0.003 in of bar, under a printed hairline, so that row
    can read as having no negative task at all. The caption carries the three shares as numbers.
4.  THE BAR IS A PROPORTION AND CARRIES NO SAMPLE SIZE. CD34+ (n=12) and cross-line (n=90) get
    the same bar length. Per-dataset n is in the caption, not on the panel, because the row must
    hold the dataset name alone. A reader comparing the CD34+ and cross-line bars is comparing
    12 tasks with 90 and the panel does not say so.
5.  ROW NAMES SIT AT 6.8 pt, the x-tick size, not at the 6.5 pt floor. An earlier build passed
    fontsize=PT_SMALL to set_yticklabels and then called bare_axes, whose tick_params(labelsize=
    PT_TICK) silently overrode it, so the note here claimed a 6.5 pt that was never drawn and a
    0.87 in width that was in fact the 6.8 pt measurement. Measured on the real canvas at 6.8 pt,
    the daggered "SciPlex3 cross-line" is 0.870 in wide, clears the panel box by 0.122 in and the
    bold panel letter by 0.042 in, so nothing is gained by shrinking to the floor and the size is
    now set explicitly, after bare_axes, where it takes effect. The alternative, had it not fit,
    was to drop "SciPlex3" from three of the five rows, which would have cost the reader the
    provenance of the majority of the tasks.
6.  MEANS ARE PRINTED TO FIVE DECIMALS, because four collide: see v5 above.
7.  THE TWO CONSTRUCTED BENCHMARKS ARE PUT ADJACENT AT THE TOP and daggered. Ordering by anything
    else (by mean, by n) would separate them, and the point of the panel is that the largest mean
    belongs to a benchmark that was built rather than measured. The dagger key sits at the left
    of the letter band, over the two rows it keys.
8.  TASKS, NOT SEEDS, ARE THE UNIT. The 239 rows come from three exp13 seeds (79/80/80) that
    redraw which drugs are tested and recluster the minority subpopulation, so they are not
    replicates of one another and are not averaged over. All 239 dataset/task_id pairs are
    distinct, but 17 base drug-or-line tasks do recur under a second seed, so the 239 are not
    fully independent either. The panel draws one dot per row of the file; treating those 17 as
    independent slightly overstates the sample, and no test is run on it here, so nothing
    downstream depends on the independence assumption.
9.  The x label names the metric as "minority-state coverage gain". The metric's own values run
    about 0.89 to 0.99, so a difference of +0.004 is small relative to the metric's range as well
    as to the drawn axis. The caption carries that, not the panel.
10. THE SUMMARY COLUMN SITS OVER THE FAR RIGHT OF THE SCALE, at roughly +0.09 to +0.18 in data
    units, because the axes cannot be widened and the 0.10 in right pad cannot hold a number.
    The spine and the ticks are deliberately NOT truncated at the field edge, but for two
    different reasons, and an earlier note here ran them together. Truncating the SPINE would
    move zero off the centre of the drawn scale, which is the one thing this panel may not do.
    Truncating the +0.10 and +0.15 TICKS would not move zero at all; they are kept because a
    symmetric tick set is what makes the eye read zero as the centre, and they are the price of
    the column sitting over labelled scale. What says the column is not on the x scale is that
    the half-plane wash STOPS at COL_X0 and the column is painted white: the bars, the means and
    their two headers sit on a field that is visibly not the data field. An earlier build put a
    white track under each bar instead, which was never visible at all, because the three shares
    sum to one and the segments covered it completely. A reader who still takes a bar for a value
    would read it as about +0.13. That residual risk is the price of keeping zero centred, and it
    is stated here rather than papered over.
11. THE COLUMN HEADER "share of tasks" IS 0.60 in WIDE AND THE BAR IT NAMES IS 0.24 in, so it
    is right aligned on the bar's right edge, which is the edge the positive segments are read
    against, and overhangs about 0.36 in to the left into the letter band above the data field.
    It is drawn in the band, where no task is plotted, and nothing else is drawn there. The
    shorter alternatives measured ("task split", 0.38 in; "share", 0.23 in) name the mark without
    naming the denominator, which is exactly the distinction this panel exists to keep.

The README line for this panel ("positive tail only in the constructed cross-line mixtures") is
not exactly right and this panel does not repeat it: the natural within-line tasks hold the third
largest positive task in the file (+0.0498) and the largest negative task (-0.0578). The two tasks
above it, +0.0867 and +0.0583, are both cross-line.
"""
from __future__ import annotations

import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Rectangle

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fig3_style import (FAINT, MEAN, POP, PT_ANNOT, PT_SMALL, PT_TICK,  # noqa: E402
                        PT_TITLE, REPO, SHARED, SUBTLE, TEXT, bare_axes, sign_field,
                        zero_rule)

PROJ = os.path.join(REPO, "results", "exp13_real_data_projection", "projection.csv")

# Constructed benchmarks first and adjacent, natural data below. See judgement call 7.
DS_ORDER = ["sciplex3_cross_line", "sciplex3_predicted_mean",
            "sciplex3_within_line", "frangieh", "cd34"]
CONSTRUCTED = {"sciplex3_cross_line", "sciplex3_predicted_mean"}
DAGGER = "†"
DS_LAB = {"sciplex3_cross_line": "SciPlex3 cross-line",
          "sciplex3_predicted_mean": "SciPlex3 predicted",
          "sciplex3_within_line": "SciPlex3 within-line",
          "frangieh": "Frangieh",
          "cd34": "CD34+"}
DEC = 5                 # decimals on the printed mean; four collide, see v5 in the docstring

# ------------------------------------------------------------------ geometry, in axes fractions
# The summary column. x is in axes fraction (blended transform), so these numbers are shares of
# the 3.03 in axes: the bar is 0.24 in, the mean value 0.38 in at 6.8 pt, and FIELD_RIGHT is the
# rightmost fraction any task may be drawn at. XLIM is then the smallest symmetric limit that
# keeps every task left of FIELD_RIGHT, rounded up to a tick multiple, and the assertion below
# refuses to draw if the data outgrows it.
MEAN_X = 1.000          # dataset mean, right-aligned here
BAR_X1 = 0.850          # task-split bar, right edge
BAR_X0 = 0.770          # task-split bar, left edge
FIELD_RIGHT = 0.759     # no dot may be drawn at or right of this
XLIM = 0.18
XTICKS = [-0.15, -0.10, -0.05, 0.0, 0.05, 0.10, 0.15]

COL_X0 = 0.762          # the summary column starts here: wash stops, white field begins
BAR_H = 0.42            # task-split bar height, in row units
JITTER = 0.30           # vertical spread within a row, in row units
BAND_Y = 4.82           # the half-plane direction labels, in row units
POP_SIDE = "right"      # the half-plane population-level retrieval is favoured on
YLIM = (5.32, -0.50)    # inverted: the first dataset is the top row
RNG_SEED = 0            # jitter is cosmetic and still seeded, so the panel is reproducible

# The smallest difference between two bar segments a reader can be expected to see at print size.
# Used below to check that the panel's central comparison is legible and not merely correct.
MIN_VISIBLE_IN = 0.010

# The mean key in the header band: the marker slot left of the word "mean". See draw_3g.
KEY_X = 0.895
KEY_Y = 1.045

# The column layout is what keeps a dot from being drawn under a label, so it is checked at import
# rather than trusted: dots stop at FIELD_RIGHT, the white field starts after it, and the bar and
# the mean sit inside that field. Editing one constant without the others now breaks the build.
assert 0.5 < FIELD_RIGHT < COL_X0 < BAR_X0 < BAR_X1 <= MEAN_X <= 1.0, (
    "summary-column geometry is inconsistent: need FIELD_RIGHT < COL_X0 < BAR_X0 < BAR_X1 <= "
    f"MEAN_X <= 1, got {FIELD_RIGHT}, {COL_X0}, {BAR_X0}, {BAR_X1}, {MEAN_X}.")
# The panel prints a dagger key, so at least one row must actually carry a dagger.
assert CONSTRUCTED and CONSTRUCTED <= set(DS_LAB) <= set(DS_ORDER), (
    "the daggered datasets must all have a row and a label, or the key keys nothing.")


def draw_3g(ax):
    p = pd.read_csv(PROJ)
    p["delta"] = p.observed_dart_minority_cov - p.observed_mean_minority_cov

    if len(p) < 200:
        raise ValueError(
            f"{PROJ} has only {len(p)} tasks: that is the QUICK sanity configuration, and the "
            f"FULL run builds 239. Re-run exp13 without QUICK=1. This panel will not present a "
            f"sanity run as the real-data result.")
    unknown = set(p.dataset.unique()) - set(DS_ORDER)
    if unknown:
        raise ValueError(f"{PROJ} carries datasets this panel has no row for: {sorted(unknown)}. "
                         f"Add them to DS_ORDER and DS_LAB rather than dropping tasks silently.")

    rows = [d for d in DS_ORDER if (p.dataset == d).any()]
    stat = {}
    for ds in rows:
        d = p.loc[p.dataset == ds, "delta"].to_numpy()
        stat[ds] = dict(d=d, n=d.size, mean=float(d.mean()),
                        pos=float((d > 0).mean()), neg=float((d < 0).mean()),
                        tie=float((d == 0).mean()))
        stat[ds]["label"] = f"{stat[ds]['mean']:+.{DEC}f}"
        assert abs(stat[ds]["pos"] + stat[ds]["neg"] + stat[ds]["tie"] - 1.0) < 1e-12

    # The relationship the deleted title stated is now the caption's opening sentence, so it is
    # checked here rather than left to a reader of the caption: if a data update ever moves the
    # largest mean off the row with the smallest share above zero, this raises instead of letting
    # a caption stand that the data no longer supports. The unit is the SHARE, which is what the
    # bar draws; it is not the count, and on this data the two disagree (cross-line is 16 of 90,
    # CD34+ is 6 of 12), which is why every wording of it says share.
    top_mean = max(rows, key=lambda k: stat[k]["mean"])
    fewest_pos = min(rows, key=lambda k: stat[k]["pos"])
    assert top_mean == fewest_pos, (
        f"The caption for this panel says the largest mean has the smallest SHARE of tasks above "
        f"zero. Largest mean is now {top_mean} ({stat[top_mean]['mean']:+.{DEC}f}) and the "
        f"smallest share above zero is {fewest_pos} ({stat[fewest_pos]['pos']:.1%}). Rewrite the "
        f"caption from the data.")

    # A printed number must not be able to outlive its data, and it must not merge two datasets
    # into one string: at four decimals Frangieh and within-line both print +0.0004.
    for ds in rows:
        assert abs(float(stat[ds]["label"]) - stat[ds]["mean"]) <= 0.5 * 10 ** (-DEC), (
            f"the {DEC}-decimal label {stat[ds]['label']} does not round-trip to the computed "
            f"mean {stat[ds]['mean']!r} for {ds}.")
    labels = [stat[ds]["label"] for ds in rows]
    assert len(set(labels)) == len(labels), (
        f"two datasets print the same mean at {DEC} decimals ({sorted(labels)}), so the column a "
        f"reader compares cannot tell them apart. Add a decimal.")

    # Every task must sit left of the summary column, or a dot would hide under a label.
    dmax = float(p.delta.max())
    assert 0.5 + dmax / (2 * XLIM) < FIELD_RIGHT, (
        f"The largest task is {dmax:+.5f}, which lands at axes fraction "
        f"{0.5 + dmax / (2 * XLIM):.3f} and would be drawn under the summary column at "
        f"{FIELD_RIGHT}. Widen XLIM (and its ticks) or narrow the column.")
    assert abs(float(p.delta.min())) < XLIM, "a task falls outside the drawn view"

    # With no sentence on the panel, the reader has to SEE that the largest mean belongs to the
    # shortest positive segment, so the drawn difference is checked in inches on the printed page.
    fig = ax.get_figure()
    ax_w_in = float(fig.get_size_inches()[0]) * float(ax.get_position().width)
    bar_w_in = (BAR_X1 - BAR_X0) * ax_w_in
    pos_sorted = sorted(stat[ds]["pos"] for ds in rows)
    assert (pos_sorted[1] - pos_sorted[0]) * bar_w_in >= MIN_VISIBLE_IN, (
        f"the two smallest positive shares are {pos_sorted[0]:.3f} and {pos_sorted[1]:.3f}, which "
        f"differ by {(pos_sorted[1] - pos_sorted[0]) * bar_w_in:.4f} in of drawn bar, under the "
        f"{MIN_VISIBLE_IN} in a reader can see. The panel no longer states this relationship in "
        f"words, so it has to be legible as a mark: widen the bar or rethink the summary.")

    # Half-planes first: which side of zero favours which representation. The dots on top of them
    # are SHARED grey, because a population-minus-mean difference is a signed quantity and not a
    # population-level object; the blue and the orange are the sign, and they are behind it.
    mean_half, pop_half = sign_field(ax, vertical=True, at=0.0, pop_side=POP_SIDE, zorder=0)
    # sign_field builds its washes with axvspan(-1e9, 0) and axvspan(0, 1e9). They draw correctly,
    # being clipped to the axes, but the reported patch extent is then about 1e11 px wide and a
    # layout audit cannot tell that wash from a real overhang. Re-cut both to the view; axvspan
    # blends x in data coordinates with y in axes coordinates, so the y bounds are 0 to 1. This is
    # the same clamp panels a, b and c apply, and it changes nothing that is drawn.
    mean_half.set_bounds(-XLIM, 0.0, XLIM, 1.0)
    pop_half.set_bounds(0.0, 0.0, XLIM, 1.0)
    # The datum the whole panel is read against, so it is drawn heavier than a spine and denser
    # than a guide. It stays under the dots: 73 of the cross-line tasks are exact ties and pile on
    # it, and that pile is evidence the rule may not paint over.
    zero_rule(ax, at=0.0, vertical=True, color=SUBTLE, lw=0.8, ls=(0, (2.6, 1.6)), zorder=2)

    # The summary column, painted white over the wash so the field it sits on is visibly not the
    # data field. Below the dots and the spine in z, above the wash. See judgement call 10.
    ax.add_patch(Rectangle((COL_X0, 0.0), 1.0 - COL_X0, 1.0, transform=ax.transAxes,
                           facecolor="white", edgecolor="none", zorder=1.5))

    rng = np.random.default_rng(RNG_SEED)
    blend = ax.get_yaxis_transform()          # x in axes fraction, y in data (row) units
    for i, ds in enumerate(rows):
        s = stat[ds]
        yy = i + rng.uniform(-JITTER, JITTER, size=s["n"])
        ax.scatter(s["d"], yy, s=3.2, c=SHARED, alpha=0.42, linewidths=0, zorder=3)
        ax.plot([s["mean"]], [i], marker="D", ms=2.8, mfc=TEXT, mec="white", mew=0.4, zorder=5)

        # Task-split bar: the share of tasks on each side of zero, ties in their own segment,
        # laid out left to right in the same sign order as the x axis. The three shares sum to
        # one, so the bar spans the reserved width exactly and its length carries no information.
        # The positive segment is drawn last and therefore ends at BAR_X1 on every row, which is
        # what lets the five blue lengths be compared against one shared edge.
        seg_x = BAR_X0
        for share, colour in ((s["neg"], MEAN), (s["tie"], FAINT), (s["pos"], POP)):
            w = share * (BAR_X1 - BAR_X0)
            if w > 0:
                ax.add_patch(Rectangle((seg_x, i - BAR_H / 2), w, BAR_H, transform=blend,
                                       facecolor=colour, edgecolor="none", zorder=5))
            seg_x += w
        # The full extent, so a pale tie segment reads as a segment and not as an unfilled gap.
        ax.add_patch(Rectangle((BAR_X0, i - BAR_H / 2), BAR_X1 - BAR_X0, BAR_H, transform=blend,
                               facecolor="none", edgecolor=FAINT, lw=0.4, zorder=5.5))

        ax.text(MEAN_X, i, s["label"], transform=blend, ha="right", va="center",
                fontsize=PT_TICK, color=TEXT, zorder=6)

    # Which half-plane is which, at the boundary it refers to. Italic and grey so the line cannot
    # be mistaken for a sixth dataset row. The assertion binds each WORD to a side and not only
    # the two x positions: swapping the two strings leaves the geometry valid and makes the panel
    # say the opposite of the wash behind it, which is the failure v3 made with the dot colours.
    hints = ((0.485, "right", "mean better"), (0.515, "left", "population better"))
    (mean_hint_x, _, mean_hint), (pop_hint_x, _, pop_hint) = hints
    assert (POP_SIDE == "right" and mean_hint_x < 0.5 < pop_hint_x
            and mean_hint.startswith("mean") and pop_hint.startswith("population")), (
        f"the direction hints must name the half-planes sign_field(pop_side={POP_SIDE!r}) washes: "
        f"mean-better left of zero and population-better right of it, but the panel draws "
        f"{mean_hint!r} at {mean_hint_x} and {pop_hint!r} at {pop_hint_x}.")
    for lx, ha, txt in hints:
        ax.text(lx, BAND_Y, txt, transform=blend, ha=ha, va="center", fontsize=PT_SMALL,
                color=SUBTLE, style="italic", zorder=6)

    ax.set_yticks(range(len(rows)))
    # The dagger marks a benchmark that was constructed rather than measured, and the key in the
    # letter band is its key. The size is set after bare_axes, below, not here: bare_axes calls
    # tick_params(labelsize=PT_TICK), which overrides any fontsize passed to set_yticklabels.
    ax.set_yticklabels([DS_LAB[d] + (" " + DAGGER if d in CONSTRUCTED else "")
                        for d in rows])
    ax.set_ylim(*YLIM)
    ax.set_xlim(-XLIM, XLIM)
    ax.set_xticks(XTICKS)
    ax.set_xticklabels(["0" if abs(v) < 1e-12 else
                        ("−" if v < 0 else "+") + f"{abs(v):.2f}" for v in XTICKS])
    bare_axes(ax, keep=("bottom",))
    ax.tick_params(axis="x", pad=1.4)
    # 6.8 pt, the x-tick size, measured to fit: see judgement call 5.
    ax.tick_params(axis="y", length=0, pad=2.0, labelsize=PT_TICK)
    # The axis names the quantity and its direction, and nothing else: n = 239 is in the caption.
    # The minus is U+2212 in the panel's own face, not mathtext: mathtext.fontset resolves to
    # DejaVu Sans while this deck's face is Arial, so a $-$ would set one glyph of the label in a
    # different family from the rest of it and from the U+2212 the x tick labels above already
    # use, and it would drag the label into the PT_EQ rule fig3_style applies to mathtext. This
    # is the same call fig3b judgement call 5 records.
    ax.set_xlabel("minority-state coverage gain, population − mean",
                  fontsize=PT_ANNOT, color=TEXT, labelpad=1.6)

    # The two summary columns name themselves, in the band the deleted phrase used to occupy.
    # Without these the bar is an unexplained mark and the number is an unnamed statistic.
    ax.text(BAR_X1, 1.0, "share of tasks", transform=ax.transAxes,
            ha="right", va="bottom", fontsize=PT_SMALL, color=SUBTLE)
    ax.text(MEAN_X, 1.0, "mean", transform=ax.transAxes,
            ha="right", va="bottom", fontsize=PT_SMALL, color=SUBTLE)
    # The diamond drawn at each row's mean is the same quantity as the number beside it, so the
    # header keys both: one mark, no words. KEY_X is a fixed fraction rather than a measured
    # offset because no renderer exists at draw time. Measured on the real canvas, "mean" at
    # 6.5 pt is 0.230 in wide, so its left edge sits at 0.924 and the marker, drawn out to 0.901,
    # clears it by 0.069 in. The bar header is right
    # aligned on BAR_X1 for the same reason, so both headers grow LEFTWARDS into empty band if a
    # fallback face measures wider, and neither can grow into the key. KEY_Y centres the marker
    # on the header's x-height.
    ax.plot([KEY_X], [KEY_Y], marker="D", ms=2.8, mfc=TEXT, mec="white", mew=0.4,
            transform=ax.transAxes, clip_on=False, zorder=6)
    # The key sits at the left of the band, over the two rows that carry the dagger.
    ax.text(0.0, 1.0, f"{DAGGER} constructed", transform=ax.transAxes,
            ha="left", va="bottom", fontsize=PT_SMALL, color=SUBTLE)


if __name__ == "__main__":
    # apply_style first, with THIS figure's type ladder. Without it the preview falls back to
    # matplotlib's default face, which is about 12 per cent wider than the deck's, and the column
    # headers collide in the preview while the composite is clean.
    from figstyle import apply_style  # noqa: E402

    apply_style(sizes=(PT_TITLE, PT_ANNOT, PT_TICK))
    # The exact printed rect from fig3_assemble: 3.03 x 0.76 in of axes inside a 4.15 in box with
    # a 1.02 in left pad, a 0.10 in right pad, a 0.42 in bottom pad and a 0.17 in letter band.
    fig = plt.figure(figsize=(4.15, 1.35))
    fig.add_axes([1.02 / 4.15, 0.42 / 1.35, 3.03 / 4.15, 0.76 / 1.35])
    draw_3g(fig.axes[0])
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "3g.png")
    fig.savefig(out, dpi=400)
    print(f"wrote {out}")
