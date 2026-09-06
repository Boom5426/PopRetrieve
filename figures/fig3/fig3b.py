"""PopRetrieve Figure 3 panel 3b: the mechanism-recovery null, one ECDF per cell line.

WHAT THIS PANEL SHOWS
---------------------
Panel a reports one number for mechanism recovery on the paired leave-drug-out queries: a median
population-minus-mean MoA-nDCG gain of exactly 0.000. A single median can be produced by a handful
of large values on either side, or by one cell line dragging two others. This panel shows it is
neither. The whole cumulative distribution is drawn for each cell line separately, and all three
cross the 0.5 level inside the same vertical step at zero, so each of the three medians is exactly
0.000 on its own. The step itself is the second fact: between 20 and 29 per cent of queries per
cell line score IDENTICALLY under population-level and mean-signature retrieval, which is a
property of the data and not a plotting artifact.

The panel does NOT show a distribution symmetric about zero. It is not: the pooled mean is
-0.0371, 41.3 per cent of queries are below zero against 34.2 per cent above, and the left tail is
longer than the right. That is panel a's business, and here it shows as the long shallow left
approach: every curve has already climbed to between 0.375 and 0.470 by the time it reaches the
step, and the ink right of the step is squeezed into a shorter x range (+0.546 at the most,
against -0.788 on the left). No curve is above 0.5 anywhere left of zero, which is the same fact
the median assertion states. What is drawn as a number is only the median and the tie mass, and
both are asserted in code before anything is drawn.

SOURCE
------
results/exp12_partial_observed_retrieval/per_query_scores.csv, rows with
``split_type == 'leave_drug_out'``, paired on (cell_line, heldout_drug, seed). The gain is
``DART_coverage_worst`` ``moa_ndcg`` minus ``mean_cosine`` ``moa_ndcg``, so positive is a
population-level win; that orientation comes from the subtraction this module performs, and it is
stated in the x label rather than assumed.

The design is MATCHED across cell lines, which is more than balanced and is what a panel that
compares three curves needs: n = 600 pairs, 200 per cell line, and the SAME 130 held-out drugs in
each of the three, each drug contributing the same number of queries in every line (73 drugs once,
47 twice, 7 three times, 3 four times). 22 MoA classes, ``observed_library_fraction`` 1.0
throughout. ``seed`` takes five values, so replication is uneven ACROSS drugs; it is even across
cell lines, and that is the direction this panel reads, so the unevenness cannot produce a
difference between the three curves. Both facts are asserted at draw time, not assumed. Verified
there too: n 200 / 200 / 200; medians 0.000, 0.000, 0.000; ties 20.0%, 28.5%, 25.0% (40, 57 and 50
tied queries); F(0-) 0.470, 0.395, 0.375; pooled range -0.788 to +0.546.

2026-08-31, THE SOURCE FIX
--------------------------
This panel used to read figures/source_data/fig3a_classA_vs_classB.csv, a 480-row table that is
leave-drug-out INTERSECTED WITH the gate's recommended verdict. That intersection is not a neutral
subset: the gate selected it, and it selected unequally, 157 / 146 / 177 per cell line. A panel
whose whole argument is "all three cell lines do the same thing" cannot be drawn on a per-cell-line
sample size the diagnostic under test chose. The module now reads the experiment output directly
and asserts the balanced 200 / 200 / 200. The headline survived the change (three medians still
exactly 0.000) and the tie mass moved, from 21.7 / 25.3 / 26.0 to 20.0 / 28.5 / 25.0, so the
printed range moved with it, from 21-26% to 20-29%.

2026-08-31, THE RESTRAINT PASS
------------------------------
The panel used to set the phrase "Median exactly zero in every cell line" above itself at 8.5 pt.
It is deleted, along with fig3_style.title() and the twelve sibling phrases: a panel carries
visual evidence, the legend carries the argument, and thirteen conclusion sentences on one page is
thirteen claims competing for the reader. The sentence now opens this panel's caption entry.

Deleting it returned height to the row, so the axes grew from 0.82 to 0.90 in, and the whole of
that went to the marks. What remains on the panel is four things: the axis names, the three cell
line names, the three medians, and the size of the step at zero. The step label was cut from
"step at zero: 20-29% exact ties" to "20-29% exact ties" and moved down to sit directly above the
feature it counts, so proximity does the work the deleted words were doing. One open ring is drawn
at (0, 0.5), the single point all three curves pass through; it is the crossing the median claim
is read off, and it is asserted, not placed by eye.

JUDGEMENT CALLS A READER COULD DISAGREE WITH
--------------------------------------------
1. The three cell lines are ONE grey with three dash patterns. They used to be three tints of the
   deck's population blue, which spent the figure's most meaningful hue on a nuisance variable
   and invited a method contrast to be read into a within-method stratification. The colour slot
   belongs to the sign of the difference, so the half-planes carry it and the curves do not.
   Cost: three dash patterns are harder to tell apart at 2.10 in than three hues would be. That
   is accepted, because which curve is which barely matters here; the claim is that all three do
   the same thing. Markers were considered instead of dashes and rejected: the three steps at zero
   top out at 0.625, 0.670 and 0.680, closer together than a legible marker is wide.
2. The medians are stated as a column in the key rather than marked on the curves. All three sit
   at the same point, (0, 0.5), so three markers would land on top of each other and read as one.
   The key is the honest form: it names each line and prints its own median beside it. The ONE
   ring drawn at that point is deliberately not three.
3. The ring at (0, 0.5) is annotation, not an observation. It is drawn unfilled so the step it
   marks runs through it, and it is placed from the asserted median rather than from a coordinate
   typed by hand. A reader who wants no non-data marks on a distribution panel would drop it; the
   trade accepted here is that without it "the medians are zero" has to be assembled from a tick,
   a hairline and a key instead of being seen at once.
4. The x view is symmetric at +/- 1.03 x the largest absolute value, so no query is clipped and
   zero is the geometric centre of the panel. This leaves the far right visibly emptier than the
   far left. That asymmetry is real (the longest tail is a mean-side loss of -0.788) and is left
   visible rather than cropped away.
5. The minus signs are U+2212, set in the panel's own sans face, not mathtext. A mathtext minus
   would render in a different family at this size for no gain, and it drags the label into the
   PT_EQ rule the figure applies to anything carrying mathtext.
6. Only three x ticks are labelled. At this width the -0.25 and -0.5 labels are wider than the
   gap between them, and a tick grid the reader cannot resolve is worse than a coarse one; minor
   ticks mark the quarter points.
7. The tie range on the panel is rounded OUTWARD to whole per cent (20-29), not to nearest (which
   would print 20-28 and exclude K562's own 28.5). A printed interval has to contain the data it
   summarises; the exact three are in the SOURCE block above and belong in the caption. Both
   endpoints are floor and ceiling of an exact ratio of integer counts, so neither can be moved by
   float error: A549's 40/200 differenced as two ECDF levels lands on either side of 0.200
   depending on the bits, and a floor of that would print 19 or 20 for the same forty queries.
8. Per-line n is not on the panel. A third key column does not fit beside the medians at 7.2 pt,
   and between the two the medians are what the panel exists to state. The three n are equal by
   design and belong in the caption as one number.
9. The zero rule is drawn FAINT rather than at the usual SUBTLE weight, and under the curves.
   The three steps lie exactly ON x = 0, so a darker rule there would compete with the data it
   marks. Zero is still unmistakable: it is the boundary between the two half-plane washes, a
   labelled tick, and the x position of the largest feature in the panel.
10. The 0.5 hairline is drawn. It is not data; it is the level at which an ECDF gives the median,
   and without it "the medians are zero" is a claim the reader has to take on trust rather than
   read off the crossing. It runs clear of the key: the word "median" sits just above it (ink
   from 0.531 to 0.629 in axes fraction) and the three rows well below, so the hairline passes
   through the gap between the head and the first row rather than through either.
11. No "mean better / population better" words are drawn. The x label already names the
   subtraction, and the two words would only fit where they would sit on the curves or on the
   tick labels. A reader who wants the half-plane meaning on the panel rather than in the caption
   would spend the width differently.

HONESTY NOTE ON THE UNIT
------------------------
The unit is the QUERY, one (cell line, held-out drug, seed) triple, and it was checked rather than
assumed. Collapsing the seeds first, one mean per (cell line, drug), leaves every median exactly
0.000 as well, so the panel's headline does not depend on the choice. The tie percentage does
depend on it (18.5 / 20.0 / 21.5 at drug level against 20.0 / 28.5 / 25.0 here), so the tie label
counts QUERIES, and the caption has to say so along with n.

Run standalone: python fig3b.py
"""
from __future__ import annotations

import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fig3_style import (FAINT, LW_HAIR, LW_LINE, PT_ANNOT, PT_SMALL, PT_TICK,  # noqa: E402
                        REPO, SHARED, SUBTLE, TEXT, bare_axes, sign_field, zero_rule)

SRC = os.path.join(REPO, "results", "exp12_partial_observed_retrieval", "per_query_scores.csv")
SPLIT = "leave_drug_out"
POP_METHOD = "DART_coverage_worst"      # population-level retrieval
MEAN_METHOD = "mean_cosine"             # mean-signature retrieval
METRIC = "moa_ndcg"
PAIR_KEYS = ["cell_line", "heldout_drug", "seed"]
N_QUERIES = 600                         # the balanced leave-drug-out design
N_PER_LINE = 200

# Cell line, dash pattern. Order is the order of the key, top to bottom. Shape and stroke only:
# see fig3_style, a cell line is never a hue.
LINES = [("A549", (0, ())), ("K562", (0, (3.0, 1.5))), ("MCF7", (0, (0.8, 1.3)))]

VIEW_PAD = 1.03      # the symmetric x view, as a multiple of the largest absolute gain
X_TICKS = (-0.5, 0.0, 0.5)             # labelled; every one of these must fit the view
# The unlabelled quarter-marks. They are a GRID OFFER rather than a fixed set: the view is
# data-driven, and on 2026-09-03 the largest absolute gain fell from 0.73 to 0.68 under the
# unbiased estimator, which put +/-0.75 outside the axes. Ticks outside a view are not drawn but
# they are still SET, and a reader who compares this panel across versions would be comparing two
# different grids without being told. The draw filters them to the view and the labelled ticks
# stay pinned, so losing a labelled tick is still a build failure.
X_TICKS_MINOR = (-0.75, -0.25, 0.25, 0.75)

# The two text blocks, in axes fraction. They sit where the curves cannot reach, and _numbers
# proves that from the data instead of from one reading of one rendering: no curve may rise above
# ANN_FLOOR anywhere left of zero, and none may fall below KEY_TOP anywhere right of KEY_X0. Both
# bounds are set clear of the blocks' measured ink (0.753 and 0.629), so a data change that would
# put a curve through a label breaks the build instead of printing over it.
ANN_X, ANN_Y, ANN_FLOOR = 0.480, 0.805, 0.720
KEY_X0, KEY_X1, KEY_NAME_X, KEY_NUM_X = 0.580, 0.660, 0.683, 0.845
KEY_TOP, KEY_HEAD_Y, KEY_Y0, KEY_DY = 0.660, 0.580, 0.400, 0.160

MEDIAN_LEVEL = 0.5   # the ECDF level a median is read off, and the y of the crossing ring


def _numbers():
    """Read the per-cell-line gains and verify everything the panel's labels assert.

    Returns (per-line dicts in LINES order, view half-width, tie percentage endpoints). Nothing
    is drawn until these hold, so a printed median cannot outlive the file it came from.
    """
    if not os.path.exists(SRC):
        raise FileNotFoundError(
            f"Figure 3b needs {SRC}, which does not exist. Rerun exp12_partial_observed_retrieval "
            f"before rebuilding this panel; this module will not invent a distribution.")
    raw = pd.read_csv(SRC)
    need = set(PAIR_KEYS) | {"split_type", "method", METRIC, "observed_library_fraction"}
    missing = sorted(need - set(raw.columns))
    assert not missing, f"{SRC} is missing columns {missing}; it holds {list(raw.columns)}"

    tab = raw.loc[raw["split_type"] == SPLIT]
    assert not tab.empty, f"{SRC} holds no rows with split_type == {SPLIT!r}"
    frac = set(tab["observed_library_fraction"].unique())
    assert frac == {1.0}, (
        f"the panel and its caption state a fully observed library; this split carries "
        f"observed_library_fraction {sorted(frac)}")

    pop = tab.loc[tab["method"] == POP_METHOD].set_index(PAIR_KEYS)[METRIC]
    mean = tab.loc[tab["method"] == MEAN_METHOD].set_index(PAIR_KEYS)[METRIC]
    for name, s in ((POP_METHOD, pop), (MEAN_METHOD, mean)):
        assert s.index.is_unique, (
            f"{name} repeats a {PAIR_KEYS} key in {SRC}; the pairing is unsafe")
    assert set(pop.index) == set(mean.index), (
        f"{POP_METHOD} and {MEAN_METHOD} do not cover the same queries: "
        f"{len(set(pop.index) ^ set(mean.index))} keys differ, so the difference is not paired")
    gain = (pop - mean.reindex(pop.index)).rename("gain").reset_index()
    assert gain["gain"].notna().all(), "a paired difference came out NaN; the join lost a query"
    assert len(gain) == N_QUERIES, (
        f"the panel is drawn on the balanced {N_QUERIES}-query {SPLIT} design; this file gives "
        f"{len(gain)}")

    want = {name for name, _ in LINES}
    have = set(gain["cell_line"].unique())
    assert have == want, f"the panel draws {sorted(want)}; the file holds {sorted(have)}"

    # Equal n is not a matched comparison. Three curves that are read against each other have
    # to stand on the same held-out drugs with the same number of seeds each, or a difference
    # between them could be a difference in which drugs they were asked about.
    per_line = {name: tuple(sorted(sub.groupby("heldout_drug").size().items()))
                for name, sub in gain.groupby("cell_line")}
    ref_name = sorted(per_line)[0]
    for name, design in per_line.items():
        assert design == per_line[ref_name], (
            f"{name} and {ref_name} are not asked the same questions: they differ on "
            f"{len(set(design) ^ set(per_line[ref_name]))} (drug, count) entries, so the three "
            f"ECDFs are not a matched comparison")

    half = VIEW_PAD * float(np.max(np.abs(gain["gain"].to_numpy(dtype=float))))
    assert half > max(abs(t) for t in X_TICKS), (
        f"the view is +/- {half:.3f} and no longer holds every LABELLED tick {X_TICKS}; the "
        f"panel would print a scale a reader cannot locate. Re-choose X_TICKS, do not widen "
        f"VIEW_PAD to make room for a tick.")
    key_x0 = (2.0 * KEY_X0 - 1.0) * half     # where the key starts, in data units

    rows = []
    for name, dash in LINES:
        v = np.sort(gain.loc[gain["cell_line"] == name, "gain"].to_numpy(dtype=float))
        n = v.size
        # Balance is the whole reason this panel moved off the gate-selected table: three curves
        # that are compared to each other have to be read on three equal samples.
        assert n == N_PER_LINE, (
            f"{name} contributes {n} queries, not the balanced {N_PER_LINE}; the three ECDFs "
            f"would no longer be comparable")
        med = float(np.median(v))
        # The key prints this median to three decimals. It is exactly zero, not rounded to it,
        # and the panel says so; a shift of even one query would trip this.
        assert med == 0.0, f"the key prints {name} median 0.000, but it is {med:.6f}"
        # Counted, not differenced. The printed range is floor/ceil of these, and
        # F(0) - F(0-) in floating point lands either side of 0.200 depending on the bits,
        # which would print 19 or 20 for the same 40 tied queries.
        n_below = int((v < 0.0).sum())         # queries left of the step
        n_tie = int((v == 0.0).sum())          # the step at zero itself
        f_below = n_below / n                  # ECDF just left of the step
        f_at = (n_below + n_tie) / n           # ECDF at the top of the step
        # The visual claim: each curve crosses the drawn 0.5 hairline inside the step at zero,
        # so the single ring at (0, 0.5) is on all three. This is what makes "median 0.000"
        # readable off the panel rather than only off the key.
        assert f_below < MEDIAN_LEVEL <= f_at, (
            f"{name} does not cross {MEDIAN_LEVEL} inside the step at zero: F(0-) = {f_below:.4f}, "
            f"F(0) = {f_at:.4f}")
        # "exact ties" names the largest single jump in each curve. Check that it is.
        _, counts = np.unique(v, return_counts=True)
        assert counts.max() == n_tie, (
            f"{name}: the step at zero holds {n_tie} queries but the tallest step "
            f"holds {counts.max()}, so it is not the feature the label counts")
        assert v[0] >= -half and v[-1] <= half, (
            f"{name} runs outside the drawn view; the panel would clip data silently")
        # The two text blocks stand where this curve is not. Left of zero the curve tops out at
        # f_below; right of the key's left edge it never comes back down.
        assert f_below < ANN_FLOOR, (
            f"{name} reaches {f_below:.3f} left of zero, into the tie label at {ANN_FLOOR}")
        f_key = float((v <= key_x0).mean())
        assert f_key > KEY_TOP, (
            f"{name} is at {f_key:.3f} where the key starts, below its top edge {KEY_TOP}")
        rows.append({"name": name, "dash": dash, "v": v, "n": n, "med": med,
                     "f_below": f_below, "f_at": f_at, "n_tie": n_tie})

    # The panel prints ONE range for three cell lines, so its endpoints are rounded OUTWARD.
    # Rounding the high end to nearest would print 28 for K562's 28.5 and state an interval that
    # does not contain its own data, which is the exact move this paper exists to object to.
    # Both endpoints are integer floor and ceiling of an exact ratio of counts, so the two
    # numbers on the panel are decided by the data and not by the last bit of a float.
    lo_pct = min((100 * r["n_tie"]) // r["n"] for r in rows)
    hi_pct = max(-((-100 * r["n_tie"]) // r["n"]) for r in rows)
    for r in rows:
        assert lo_pct * r["n"] <= 100 * r["n_tie"] <= hi_pct * r["n"], (
            f"the panel prints {lo_pct}-{hi_pct}% exact ties, which excludes {r['name']} at "
            f"{100 * r['n_tie'] / r['n']:.2f}%")
    return rows, half, (lo_pct, hi_pct)


def _tick(v):
    """A tick label formatted from the coordinate it sits under, with a typographic minus.

    Typing the labels out would let them drift from the ticks: change X_TICKS and the panel
    would keep printing the old numbers under the new positions.
    """
    return f"{v:g}".replace("-", "\u2212")


def _ecdf(v, left, right):
    """Step coordinates for the empirical CDF of ``v``, drawn with drawstyle 'steps-post'.

    Ties are kept as a single vertical rise at their shared value, which is the whole point of
    this panel: the jump at zero must be one step of its true height, not a stack of hairlines.
    """
    xs, counts = np.unique(v, return_counts=True)
    ys = np.cumsum(counts) / v.size
    x = np.concatenate([[left], xs, [right]])
    y = np.concatenate([[0.0], ys, [ys[-1]]])
    return x, y


def draw_3b(ax):
    """Per-cell-line ECDF of the population-minus-mean MoA-nDCG gain, against zero."""
    rows, half, (lo_pct, hi_pct) = _numbers()

    # The sign lives in the background, never in the curves: mean-signature retrieval is
    # favoured left of zero, population-level retrieval right of it.
    mean_half, pop_half = sign_field(ax, vertical=True, at=0.0, pop_side="right", zorder=0)
    # sign_field spans +/- 1e9 in data units and relies on axes clipping, so no ink escapes; but
    # an unclipped window extent that wide is reported as ink outside the panel box by the
    # per-panel QA harness. The two patches are trimmed to the view set below, which changes
    # nothing that is drawn and makes the reported extent the truth. Their y is in axes
    # fraction (axvspan uses get_xaxis_transform), so the height is 0 to 1.
    mean_half.set_bounds(-half, 0.0, half, 1.0)
    pop_half.set_bounds(0.0, 0.0, half, 1.0)
    zero_rule(ax, at=0.0, vertical=True, color=FAINT, lw=0.8, zorder=1)
    # The level at which an ECDF reads out the median.
    ax.axhline(MEDIAN_LEVEL, color=FAINT, lw=LW_HAIR, zorder=1)

    for r in rows:
        x, y = _ecdf(r["v"], -half, half)
        ax.plot(x, y, drawstyle="steps-post", color=SHARED, lw=LW_LINE, ls=r["dash"],
                solid_capstyle="butt", dash_capstyle="butt", zorder=3)

    # The one point all three curves pass through. Its x is the asserted median, its y is the
    # level a median is read off, and it is drawn unfilled so the step runs through it.
    ax.plot([rows[0]["med"]], [MEDIAN_LEVEL], marker="o", ms=4.2, mfc="none", mec=SHARED,
            mew=1.0, ls="none", zorder=4)

    # The step at zero, counted once, directly above it. It sits where _numbers has already
    # proved the curves are not: none reaches ANN_FLOOR anywhere left of zero.
    # En dash, not a hyphen: this is a numeric range and the manuscript sets its ranges with one
    # (120--150, 34--35). A hyphen here made one paper punctuate the same construction two ways.
    ax.text(ANN_X, ANN_Y, f"{lo_pct}\u2013{hi_pct}% exact ties", transform=ax.transAxes, ha="right",
            va="center", fontsize=PT_ANNOT, color=TEXT, zorder=5)

    # The key IS the median statement: each cell line, its dash, and its own median, one place,
    # one size. Same guarantee mirrored: _numbers has proved every curve is above KEY_TOP by the
    # time it reaches KEY_X0, so the lower right is empty ink too. The 0.5 hairline runs through
    # the gap between the head and the first row, striking neither.
    ax.text(KEY_NUM_X, KEY_HEAD_Y, "median", transform=ax.transAxes, ha="left", va="center",
            fontsize=PT_SMALL, color=SUBTLE, zorder=5)
    for i, r in enumerate(rows):
        y = KEY_Y0 - KEY_DY * i
        ax.add_line(Line2D([KEY_X0, KEY_X1], [y, y], transform=ax.transAxes, color=SHARED,
                           lw=LW_LINE, ls=r["dash"], solid_capstyle="butt",
                           dash_capstyle="butt", zorder=5))
        ax.text(KEY_NAME_X, y, r["name"], transform=ax.transAxes, ha="left", va="center",
                fontsize=PT_ANNOT, color=TEXT, zorder=5)
        ax.text(KEY_NUM_X, y, f"{r['med']:.3f}", transform=ax.transAxes, ha="left", va="center",
                fontsize=PT_ANNOT, color=TEXT, zorder=5)

    bare_axes(ax)
    ax.set_xlim(-half, half)
    ax.set_ylim(0.0, 1.0)
    ax.set_xticks(list(X_TICKS))
    ax.set_xticklabels([_tick(t) for t in X_TICKS], fontsize=PT_TICK)
    ax.set_xticks([t for t in X_TICKS_MINOR if abs(t) < half], minor=True)
    ax.tick_params(axis="x", which="minor", length=1.3, width=0.6, color=FAINT)
    Y_TICKS = (0.0, MEDIAN_LEVEL, 1.0)
    ax.set_yticks(list(Y_TICKS))
    ax.set_yticklabels([_tick(t) for t in Y_TICKS], fontsize=PT_TICK)
    ax.set_xlabel("MoA-nDCG gain\npopulation − mean", fontsize=PT_ANNOT, color=TEXT,
                  linespacing=1.20, labelpad=1.5)
    ax.set_ylabel("cumulative\nfraction", fontsize=PT_ANNOT, color=TEXT, linespacing=1.20,
                  labelpad=1.5)
    return ax


if __name__ == "__main__":
    # Reproduce the printed geometry exactly: panel box 2.90 x 1.51 in, axes 2.10 x 0.90 in at
    # the pads fig3_assemble gives panel b, so the preview is what the composite prints.
    BOX_W, BOX_H, LEFT, BOTTOM, AX_W, AX_H = 2.90, 1.51, 0.70, 0.44, 2.10, 0.90
    fig = plt.figure(figsize=(BOX_W, BOX_H))
    ax = fig.add_axes([LEFT / BOX_W, BOTTOM / BOX_H, AX_W / BOX_W, AX_H / BOX_H])
    draw_3b(ax)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "3b.png")
    fig.savefig(out, dpi=300)
    print(f"wrote {out}")
