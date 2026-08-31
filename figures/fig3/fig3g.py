"""PopRetrieve Figure 3 panel 3g: on real data the coverage gain is a tail, not a shift.

WHAT THIS PANEL CLAIMS
----------------------
Across 239 real-data retrieval tasks the population-minus-mean minority-coverage difference sits
on zero, and the dataset with the LARGEST mean is the dataset with the SMALLEST SHARE of tasks
above zero. The constructed cross-line mixtures average +0.00426, ten times the next largest
dataset mean (Frangieh, +0.00042), yet only 17.8 per cent of their tasks are above zero and 81.1
per cent are exact ties; the natural within-line tasks average +0.00038 with 55.6 per cent above
zero. A mean of a handful of large positives is not an advantage held broadly, and the panel is
built so the two cannot be confused: the per-task dots and the task-split bar are drawn beside the
mean, never instead of it.

SHARE, NOT COUNT, AND THE TITLE SAYS SO. Cross-line has the smallest SHARE above zero (16 of 90,
17.8 per cent) but not the smallest COUNT: CD34+ has 6 of 12. An earlier title read "fewest tasks
above zero", which is false on the count reading and true only once a denominator is chosen. That
is the precise error this paper exists to criticise, so the title names the share, the bar draws
the share, and judgement call 4 records that the bar carries no n.

Source data: results/exp13_real_data_projection/projection.csv (the only file this module reads).
Gain per task = observed_dart_minority_cov - observed_mean_minority_cov.
Run standalone: python fig3g.py

HISTORY THIS FILE MUST NOT LOSE
-------------------------------
This panel has been wrong three times, and every correction is preserved as a guard in the code.

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
      it in 2 to 4 of 10 resamples. No count of threshold crossings is drawn here. See
      CORRECTIONS.md R13.

  v3 (2026-07-26): the distribution replaced a 5 x 90 heat map on which 43 per cent of cells were
      white on white and the only legible thing was the outlier.

  v4 (this rebuild): v3 printed one dot per task and one mean diamond per row, and the mean
      diamond was the only summary. On this data that says the opposite of what the tasks say:
      the largest mean belongs to the row with the fewest tasks above zero. The share of tasks on
      each side of zero is now drawn as well, and the row label carries the dataset name only.
      v3 also coloured each dot blue or orange by the SIGN of its own difference, which is the
      error fig3_style was written to stop: blue ink means a population-level object, never a
      difference that happens to be positive. The dots are SHARED grey and the sign lives in the
      half-plane wash behind them.

JUDGEMENT CALLS A READER COULD REASONABLY DISAGREE WITH
-------------------------------------------------------
1.  THE VIEW IS SYMMETRIC AT +/- 0.18, about twice the largest task (+0.0867). Zero is the visual
    centre because the sign is the quantity being read. The extra room is not padding for its own
    sake: the right quarter of the axes carries the summary column, and 0.18 is the smallest
    symmetric limit at which no task is drawn underneath a label. This is asserted below, so a
    change in the data cannot silently slide a dot under the text. The cost is real and is the
    panel's main compromise: 92 per cent of tasks fall within |0.005|, which is 1.4 per cent of
    the drawn width, so the per-task dots form a dense smear at zero rather than a separable
    swarm. That smear is the honest shape of this result at a symmetric linear scale, and no
    transform (symlog, a broken axis, a cropped view) is used to make the small differences look
    larger than they are.
2.  THE JITTER IS SEEDED UNIFORM NOISE, NOT A BEESWARM. A beeswarm that separated 90 tasks would
    need roughly 0.75 in of x for the exact-zero column alone; this panel has 0.68 in of HEIGHT
    in total. Overlap and alpha carry density instead, so the reader can see mass but cannot
    count dots. The counts are therefore given as the task-split bar, not left to the eye.
3.  THE TASK-SPLIT BAR GIVES EXACT TIES THEIR OWN SEGMENT. 102 of the 239 tasks have a difference
    of exactly zero: both methods select the same candidate. Folding those into either side, or
    reporting only "per cent > 0", would misstate the split, most severely for the cross-line
    row where the ties are 81 per cent. The bar is a share of TASKS and its width is not on the
    x scale; it is placed in a reserved column, past every dot, for that reason.
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
6.  MEANS ARE PRINTED TO FIVE DECIMALS. At four, two of the five datasets print as +0.0000, which
    reads as a fabricated zero for a mean that is genuinely 3e-05.
7.  THE TWO CONSTRUCTED BENCHMARKS ARE PUT ADJACENT AT THE TOP and daggered. Ordering by anything
    else (by mean, by n) would separate them, and the point of the panel is that the largest mean
    belongs to a benchmark that was built rather than measured.
8.  TASKS, NOT SEEDS, ARE THE UNIT. The 239 rows come from three exp13 seeds (79/80/80) that
    redraw which drugs are tested and recluster the minority subpopulation, so they are not
    replicates of one another and are not averaged over. All 239 dataset/task_id pairs are
    distinct, but 17 base drug-or-line tasks do recur under a second seed, so the 239 are not
    fully independent either. The panel draws one dot per row of the file and says n = 239;
    treating those 17 as independent slightly overstates the sample, and no test is run on it
    here, so nothing downstream depends on the independence assumption.
9.  The x label names the metric as "minority-state coverage gain". The metric's own values run
    about 0.89 to 0.99, so a difference of +0.004 is small relative to the metric's range as well
    as to the drawn axis. The caption carries that, not the panel.
10. THE SUMMARY COLUMN SITS OVER THE FAR RIGHT OF THE SCALE, at roughly +0.10 to +0.18 in data
    units, because the axes cannot be widened and the 0.10 in right pad cannot hold a number.
    The spine and the ticks are deliberately NOT truncated at the field edge, but for two
    different reasons, and the earlier note here ran them together. Truncating the SPINE would
    move zero off the centre of the drawn scale, which is the one thing this panel may not do.
    Truncating the +0.10 and +0.15 TICKS would not move zero at all; they are kept because a
    symmetric tick set is what makes the eye read zero as the centre, and they are the price of
    the column sitting over labelled scale. What says the column is not on the x scale is that
    the half-plane wash STOPS at COL_X0 and the column is painted white: the bars and the means
    sit on a field that is visibly not the data field. An earlier build put a white track under
    each bar instead, which was never visible at all, because the three shares sum to one and
    the segments covered it completely. A reader who still takes a bar for a value would read it
    as about +0.13. That residual risk is the price of keeping zero centred, and it is stated
    here rather than papered over.

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
                        title, zero_rule)

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

# ------------------------------------------------------------------ geometry, in axes fractions
# The summary column. x is in axes fraction (blended transform), so these numbers are shares of
# the 3.03 in axes: the bar is 0.23 in, the mean value 0.39 in at 6.8 pt, and FIELD_RIGHT is the
# rightmost fraction any task may be drawn at. XLIM is then the smallest symmetric limit that
# keeps every task left of FIELD_RIGHT, rounded up to a tick multiple, and the assertion below
# refuses to draw if the data outgrows it.
MEAN_X = 1.000          # dataset mean, right-aligned here
BAR_X1 = 0.850          # task-split bar, right edge
BAR_X0 = 0.775          # task-split bar, left edge
FIELD_RIGHT = 0.759     # no dot may be drawn at or right of this
XLIM = 0.18
XTICKS = [-0.15, -0.10, -0.05, 0.0, 0.05, 0.10, 0.15]

COL_X0 = 0.762          # the summary column starts here: wash stops, white field begins
BAR_H = 0.34            # task-split bar height, in row units
JITTER = 0.26           # vertical spread within a row, in row units
BAND_Y = 4.85           # the half-plane direction labels, in row units
YLIM = (5.35, -0.58)    # inverted: the first dataset is the top row
RNG_SEED = 0            # jitter is cosmetic and still seeded, so the panel is reproducible

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
        assert abs(stat[ds]["pos"] + stat[ds]["neg"] + stat[ds]["tie"] - 1.0) < 1e-12

    # The one phrase over the panel is a relationship, so it is asserted rather than asserted-by-
    # eye: if a data update ever moves the largest mean off the row with the smallest share above
    # zero, this raises instead of printing a caption that the data no longer supports. The unit
    # is the SHARE, which is what the bar draws; it is not the count, and on this data the two
    # disagree (cross-line is 16 of 90, CD34+ is 6 of 12), which is why the title says share.
    top_mean = max(rows, key=lambda k: stat[k]["mean"])
    fewest_pos = min(rows, key=lambda k: stat[k]["pos"])
    assert top_mean == fewest_pos, (
        f"The title says the largest mean has the smallest SHARE of tasks above zero. Largest "
        f"mean is now {top_mean} ({stat[top_mean]['mean']:+.5f}) and the smallest share above "
        f"zero is {fewest_pos} ({stat[fewest_pos]['pos']:.1%}). Retitle the panel from the data.")

    # Every task must sit left of the summary column, or a dot would hide under a label.
    dmax = float(p.delta.max())
    assert 0.5 + dmax / (2 * XLIM) < FIELD_RIGHT, (
        f"The largest task is {dmax:+.5f}, which lands at axes fraction "
        f"{0.5 + dmax / (2 * XLIM):.3f} and would be drawn under the summary column at "
        f"{FIELD_RIGHT}. Widen XLIM (and its ticks) or narrow the column.")
    assert abs(float(p.delta.min())) < XLIM, "a task falls outside the drawn view"

    # Half-planes first: which side of zero favours which representation. The dots on top of them
    # are SHARED grey, because a population-minus-mean difference is a signed quantity and not a
    # population-level object; the blue and the orange are the sign, and they are behind it.
    mean_half, pop_half = sign_field(ax, vertical=True, at=0.0, pop_side="right", zorder=0)
    # sign_field builds its washes with axvspan(-1e9, 0) and axvspan(0, 1e9). They draw correctly,
    # being clipped to the axes, but the reported patch extent is then about 1e11 px wide and a
    # layout audit cannot tell that wash from a real overhang. Re-cut both to the view; axvspan
    # blends x in data coordinates with y in axes coordinates, so the y bounds are 0 to 1. This is
    # the same clamp panels a, b and c apply, and it changes nothing that is drawn.
    mean_half.set_bounds(-XLIM, 0.0, XLIM, 1.0)
    pop_half.set_bounds(0.0, 0.0, XLIM, 1.0)
    zero_rule(ax, at=0.0, vertical=True, color=SUBTLE, lw=0.6, ls=(0, (2.4, 1.8)), zorder=1)

    # The summary column, painted white over the wash so the field it sits on is visibly not the
    # data field. Below the dots and the spine in z, above the wash. See judgement call 10.
    ax.add_patch(Rectangle((COL_X0, 0.0), 1.0 - COL_X0, 1.0, transform=ax.transAxes,
                           facecolor="white", edgecolor="none", zorder=1.5))

    rng = np.random.default_rng(RNG_SEED)
    blend = ax.get_yaxis_transform()          # x in axes fraction, y in data (row) units
    for i, ds in enumerate(rows):
        s = stat[ds]
        yy = i + rng.uniform(-JITTER, JITTER, size=s["n"])
        ax.scatter(s["d"], yy, s=2.8, c=SHARED, alpha=0.45, linewidths=0, zorder=3)
        ax.plot([s["mean"]], [i], marker="D", ms=2.4, mfc=TEXT, mec="white", mew=0.35, zorder=5)

        # Task-split bar: the share of tasks on each side of zero, ties in their own segment,
        # laid out left to right in the same sign order as the x axis. The three shares sum to
        # one, so the bar spans the reserved width exactly and its length carries no information.
        seg_x = BAR_X0
        for share, colour in ((s["neg"], MEAN), (s["tie"], FAINT), (s["pos"], POP)):
            w = share * (BAR_X1 - BAR_X0)
            if w > 0:
                ax.add_patch(Rectangle((seg_x, i - BAR_H / 2), w, BAR_H, transform=blend,
                                       facecolor=colour, edgecolor="none", zorder=5))
            seg_x += w

        ax.text(MEAN_X, i, f"{s['mean']:+.5f}", transform=blend, ha="right", va="center",
                fontsize=PT_TICK, color=TEXT, zorder=6)

    # Which half-plane is which, at the boundary it refers to. Italic and grey so the line cannot
    # be mistaken for a sixth dataset row.
    for lx, ha, txt in ((0.485, "right", "mean better"), (0.515, "left", "population better")):
        ax.text(lx, BAND_Y, txt, transform=blend, ha=ha, va="center", fontsize=PT_SMALL,
                color=SUBTLE, style="italic", zorder=6)

    ax.set_yticks(range(len(rows)))
    # The dagger marks a benchmark that was constructed rather than measured, and the note beside
    # the title is its key. The size is set after bare_axes, below, not here: bare_axes calls
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
    # n rides on the x label rather than beside the title: the title band holds the panel's one
    # phrase plus the dagger key, and at 8.5 pt those two already leave only 0.46 in of it.
    ax.set_xlabel(f"minority-state coverage gain, population $-$ mean; {len(p)} tasks",
                  fontsize=PT_ANNOT, color=TEXT, labelpad=1.6)

    title(ax, "Largest mean, smallest share above zero")
    ax.text(1.0, 1.0, f"{DAGGER} constructed", transform=ax.transAxes,
            ha="right", va="bottom", fontsize=PT_SMALL, color=SUBTLE)


if __name__ == "__main__":
    # apply_style first, with THIS figure's type ladder. Without it the preview falls back to
    # matplotlib's default face, which is about 12 per cent wider than the deck's, and the title
    # and the dagger key collide in the preview while the composite is clean.
    from figstyle import apply_style  # noqa: E402

    apply_style(sizes=(PT_TITLE, PT_ANNOT, PT_TICK))
    # The exact printed rect from fig3_assemble: 3.03 x 0.68 in of axes inside a 4.15 in box with
    # a 1.02 in left pad, a 0.10 in right pad, a 0.42 in bottom pad and a 0.24 in letter band.
    fig = plt.figure(figsize=(4.15, 1.34))
    fig.add_axes([1.02 / 4.15, 0.42 / 1.34, 3.03 / 4.15, 0.68 / 1.34])
    draw_3g(fig.axes[0])
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "3g.png")
    fig.savefig(out, dpi=400)
    print(f"wrote {out}")
