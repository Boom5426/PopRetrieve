"""PopRetrieve Figure 3 panel 3d: the queries the pre-specified gate recommends and the queries it
declines carry the same per-query regret reduction.

WHAT THIS PANEL SHOWS
---------------------
Two median estimates with seeded bootstrap 95 per cent intervals on one signed axis, one row per
gate verdict, and under them the quantity that decides the question: the difference of the two
medians and the two-sided rank test on them. The evidence is that the two rows land in the same
place, well clear of zero, with intervals that overlap along most of their length.

The panel states no conclusion. "The gate does not enrich" is a caption sentence, and the caption
also carries what a bounded null needs and this panel cannot hold: the difference interval, the
name of the test, the quartiles, the pooled reading of "not recommended", and the independence
caveat behind the p.

THE 2026-08-31 RESTRAINT PASS
-----------------------------
Three things changed, and none of them is a number.

  * THE PHRASE IS GONE. This panel used to set "Gate does not enrich" over itself at PT_TITLE.
    Thirteen such phrases on one page is thirteen claims competing for the reader, so fig3_style
    deleted title() outright and fig3_assemble._assert_no_titles now refuses to build a figure in
    which any panel draws text above PT_ANNOT. The phrase opens this panel's caption entry.
  * THE AXES GREW, 0.58 to 0.65 in, because the six rows got back the 0.42 in the phrases held.
    It went to the marks: the rows are further apart and the interval caps are taller, both set in
    INCHES so that the next change to the row height does not silently rescale them.
  * THE STATISTICS ARE ONE LINE, not two, and it holds the difference and its p. The difference
    interval and the name of the test came off with the phrase.

Everything that came off the panel is still COMPUTED and asserted here, including the difference
interval and the 144-query pooled reading, and draw_3d still returns all of it, so the caption
cannot drift away from the data it describes.

WHY IT IS IN FIGURE 3, HAVING ALREADY APPEARED IN FIGURE 2
----------------------------------------------------------
This is the same measurement as Fig. 2 panel d, shown for a different reason. Fig. 2d asks
whether the pre-specified diagnostic finds the RESPONSE-MATCHING gain, inside the figure where
that gain is the result. Here it is the first of three panels (d, e, f) showing that the same
diagnostic fails, inside the figure about biological evaluation: it does not enrich for the gain
(d), its own reliability axis runs opposite to true divergence (e), and its binary verdict does
not sort queries by divergence (f). The numbers, the direction of subtraction and the group names
are identical to Fig. 2d by intent; only the size of the panel and what it is used to argue differ.

SCOPE. The quantity is objective-aligned (Class A) throughout, exactly as in Fig. 2d. Regret
reduction compares two RETRIEVAL decisions against the same candidate library. Nothing on this
panel says whether the retrieved perturbation is biologically useful; that is what h, i, l and m
are for. What the panel adds to Figure 3 is that the gate cannot be used to tell in advance which
queries the population representation helps.

SOURCE
------
results/exp12_partial_observed_retrieval/per_query_scores.csv, the per-query rows, paired inside
each query on split_type, cell_line, heldout_drug, observed_library_fraction and seed, as
mean_cosine decision_regret minus DART_coverage_worst decision_regret. Every number drawn or
written here (medians, intervals, counts, the difference and the rank test) is recomputed from
those rows at draw time; nothing is a literal.

results/exp12_partial_observed_retrieval/recommendation_vs_outcome.csv, which an earlier cut of
this panel read, is deliberately NOT read. It holds pre-aggregated medians only, so an interval
drawn beside them would carry an n that is not the n the panel plots.

THE 765 ADD UP, AND THE 11 DO NOT CHANGE THE ANSWER
---------------------------------------------------
The 765 paired queries split three ways by recommendation_mode: 621 DART_recommended, 133
mean_or_no_call, 11 mean_sufficient. The first two are the manuscript's two-way comparison; the
11 mean-sufficient queries (median regret reduction exactly 0.000) are neither plotted nor named
on this panel, and the three counts are asserted to sum to 765 so they cannot be lost silently.

mean_sufficient is a third gate state, and those 11 queries were also not recommended, so the set
of queries the gate declined is 144 rather than the plotted 133. The plotted row follows the
manuscript's defined term. Because the negative result could otherwise be an artefact of which
queries were set aside, the panel recomputes the same difference over all 144 declined queries
and asserts that reading reaches the same verdict (+0.005, 95% CI -0.055 to +0.065, Mann-Whitney
p = 0.81, against -0.003, -0.062 to +0.058, p = 0.97 for the plotted 133). Only the plotted
reading is drawn; the pooled one is a guard.

JUDGEMENT CALLS A READER COULD REASONABLY DISAGREE WITH
-------------------------------------------------------
 1. BOTH ROWS ARE SHARED GREY, NOT BLUE. Each row plots a signed difference (a population-level
    scorer's advantage over a mean-level one), and in this figure's vocabulary blue and orange
    are a statement about SIGN, carried by the half-planes behind a neutral mark, never about a
    positive difference. Fig. 2d draws the same two rows in the population blue under Fig. 2's
    older convention. Same numbers, different ink; the two rows are told apart by fill and by
    position, as they are there.
 2. THE DIFFERENCE IS STATED, NOT PLOTTED. Fig. 2d gives it a third row with its own marker and
    interval. This axes is 1.24 x 0.65 in; a third row would cost the interval geometry that
    makes the panel readable, and it would put a third row name on a panel whose point is that
    there are two groups and no difference between them. The trade is acceptable because both
    estimates share one axis, so a reader SEES that the two medians coincide rather than only
    reading that they do.
 3. NO SPREAD IS DRAWN. Both distributions are strongly right-skewed (q25 +0.0000 and +0.0001,
    medians +0.119 and +0.122, q75 +0.328 and +0.344, ranges -1.02 to +2.82 and -0.42 to +1.75).
    Reaching q75 and still leaving the n column clear needs a view running to about +0.47, half
    as wide again as the one drawn, and the two intervals this panel exists to compare would lose
    a third of their length on it. So the panel says nothing at all about spread, and the
    quartiles live here and in the caption. Fig. 2d, at twice the width, draws them.
 4. THE DIFFERENCE INTERVAL IS NOT PRINTED, and neither is the test's name. Of everything cut
    here the interval is the one deletion that costs evidence rather than rhetoric, because a null
    is a statement about an effect size and not about a p value. Two things make it survivable.
    The bound is still ASSERTED (the difference interval must be small against the gains it is a
    null about), so the caption's claim cannot outlive the data; and the precision behind it is
    DRAWN, the two group intervals being 0.04 and 0.12 wide on medians of +0.12, which is what
    tells a reader this is a measured null rather than an underpowered one. The written interval
    never fitted on one line anyway: 2.22 in at the 6.5 pt floor in a 2.10 in box, so the old
    panel bought it with a second line of statistics, and a second line of statistics is what
    this pass removes.
 5. THE ROW LABELS SIT IN THE BOX'S LEFT PAD, left-aligned with the statistics line so the panel
    has one text margin. At PT_TICK "Not recommended" is 0.776 in against 0.755 in of usable pad,
    so its last glyph ends about 0.02 in into the mean-side wash. (Measure it against the vector
    metrics: a 100 dpi raster quantises the same string to 0.770 in and understates it.)
    Right-aligning the column instead, which is the forest plot convention, would push it out of
    the panel box, and dropping it to PT_SMALL, where the string is 0.740 in, would make it fit
    by shrinking a group name, which this figure does not do.
 6. THE WASH AND THE ZERO RULE ARE CUT TO THE ROWS BAND rather than running the full height of
    the axes, so the statistics line below them sits on white and does not cross the sign
    boundary. Panel c lets its notes sit on its wash, but c's negative half-plane is a 2 per cent
    sliver; here it is 17 per cent of the axis width and a line of text would run straight
    through the boundary.
 7. THE p IS PRINTED AND ITS CAVEAT IS NOT. The test is a two-sided Mann-Whitney, named in the
    caption. Queries inside one cell line share a candidate library, so its independence
    assumption is violated and p is anticonservative. That bias runs towards rejecting; the test
    did not reject even so, which makes this negative stronger rather than weaker, so a reader who
    takes p = 0.97 at face value is not misled in the direction the panel supports. The caveat
    belongs in the caption.
 8. NEITHER HALF-PLANE IS LABELLED "population better". Panels a and g, both above this one on the
    page, label theirs; this panel is 1.24 in wide, its axis name already states the direction of
    the subtraction, and the sign of the gain is not what it is about. A reader who reads the
    washes as decoration still reads this panel correctly.
 9. QUERY_KEY IS DUPLICATED from fig2c rather than imported, so that a concurrent edit
    to a sibling panel cannot change what this panel pairs on. The pairing is guarded instead by
    asserting that it yields exactly 765 queries, that each method's rows are unique on the key,
    and that the gate's verdict is a property of the query rather than of the scorer.
10. EVERY STATED DIRECTION IS BUILT FROM WHAT IT DESCRIBES. The axis label is built from
    METHOD_LABEL, keyed by the method ids the subtraction actually uses, so a renamed method
    raises at import rather than printing an inverted direction. The tick labels are formatted
    from XTICKS. And the sign convention behind the half-planes is asserted against the
    method_family column rather than trusted from the method names: mean_cosine must be
    mean_signature and coverage-worst must be DART_coverage, or the washes label the wrong
    retrievers.

    The statistics line no longer names the two rows it subtracts (the old two-line block opened
    "Recommended - not recommended"), which is the price of one line. What replaces that naming is
    an assertion: the printed difference must be smaller than either drawn interval is wide, so it
    can never become a number whose SIGN a reader would want to act on. If it ever does, the
    assertion fires and the direction has to go back onto the panel.

    The minus in the axis label and in the difference is the literal U+2212, not mathtext. In this
    deck's body face (Arial, or Liberation Sans as its metric clone) a mathtext $-$ prints 6.48 pt
    wide at 7.2 pt nominal against 4.32 pt for U+2212, which is 90 per cent of an em dash: it reads
    as one, and it made this panel print two different minus glyphs for the same operation.
11. THE INTERVAL BOUNDS ARE A SEEDED PERCENTILE BOOTSTRAP at n_boot = 4000, the same estimator,
    seed and count as Fig. 2d, so the two panels cannot print different intervals for the same
    data. In the 133-query group the bootstrap median takes only about 38 distinct values, so the
    drawn lower cap moves by about 0.005 across seeds. The medians themselves are exact; no CI
    bound from this panel should be quoted to four decimals.

Run standalone: python3 fig3d.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd
from matplotlib.backends.backend_agg import RendererAgg
from scipy.stats import mannwhitneyu

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fig3_style import (LW_HAIR, LW_LINE, MS_DOT, PT_ANNOT, PT_SMALL,  # noqa: E402
                        PT_TICK, REPO, SHARED, SUBTLE, TEXT, bare_axes, boot_ci,
                        sign_field, zero_rule)

SRC = os.path.join(REPO, "results", "exp12_partial_observed_retrieval", "per_query_scores.csv")

# The query identity Fig. 2c and Fig. 2d pair on. Duplicated rather than imported: docstring 9.
QUERY_KEY = ["split_type", "cell_line", "heldout_drug", "observed_library_fraction", "seed"]
N_QUERIES = 765
POP_METHOD, MEAN_METHOD = "DART_coverage_worst", "mean_cosine"
POP_FAMILY, MEAN_FAMILY = "DART_coverage", "mean_signature"

# The reader-facing name of each method, keyed BY the id, so the axis label cannot outlive a
# renamed constant: that label states the direction of the subtraction, and a stale direction
# would invert the claim the half-planes make. A rename raises KeyError at import.
METHOD_LABEL = {MEAN_METHOD: "mean cosine", POP_METHOD: "coverage-worst"}
XLABEL = f"regret reduction,\n{METHOD_LABEL[MEAN_METHOD]} − {METHOD_LABEL[POP_METHOD]}"

# The two compared gate states, in drawing order, with the marker fill that separates them.
# Hue is not available to separate them: both rows plot a signed difference, so both are grey.
GROUPS = [("DART_recommended", "Recommended", SHARED),
          ("mean_or_no_call", "Not recommended", "white")]
MEAN_SUFFICIENT = "mean_sufficient"

# ---- the view. Every number here is asserted against the data before anything is drawn --------
XLO, XHI = -0.06, 0.29
XTICKS = [0.0, 0.1, 0.2]
ROW_Y = [0.80, 0.50]        # the two rows, in axes-height units (ylim is 0..1)
WASH_BOT = 0.30             # the sign wash and the zero rule stop here; below is type, on white
CAP_HALF_IN = 0.030         # half-height of an interval cap, in INCHES, so the row height of the
                            # panel can change without rescaling the marks
N_X = 0.73                  # left edge of the per-row n, clear of the widest interval cap
STAT_Y = 0.10               # baseline of the one statistics line
TEXT_INSET = 0.005          # how far inside the panel box's left edge the type starts, in inches
MIN_LEFT_PAD = 0.60         # the label column does not fit in less than this much pad, in inches
MAX_STAT_IN = 2.05          # the statistics line must stay inside the 2.10 in panel box, which
                            # is what limits how much wording it can carry
N_BOOT, SEED = 4000, 0


def _left_margin(ax) -> float:
    """x of the panel box's left edge plus TEXT_INSET, in axes-width units.

    Measured from the axes rather than written down, so that a change to the inch ledger in
    fig3_assemble.PADS moves this panel's text column instead of pushing it out of the panel box.

    It assumes panel d is the leftmost panel of its row, which is what makes the box's left edge
    the figure's left edge; that is true in fig3_assemble.ROWS and in the standalone preview
    below. Both ends of that assumption are asserted. Too little pad and the label column does
    not fit; more pad than the axes is wide means this is no longer the leftmost panel, the
    measured offset is then most of a row rather than one panel's pad, and the text column would
    start outside the panel box instead.
    """
    fig_w = ax.figure.get_figwidth()
    pos = ax.get_position()
    left_in, width_in = pos.x0 * fig_w, pos.width * fig_w
    assert MIN_LEFT_PAD <= left_in < width_in, (
        f"this panel sets its row labels and its statistics line in the {left_in:.2f} in of pad "
        f"to the left of its {width_in:.2f} in axes; it needs at least {MIN_LEFT_PAD} in of it, "
        f"and a pad wider than the axes means panel d is no longer the leftmost panel of its row")
    return -(left_in - TEXT_INSET) / width_in


def _fmt(v: float, digits: int = 3) -> str:
    """Signed number with a typographic minus, so the panel never mixes hyphens and minuses."""
    return f"{v:+.{digits}f}".replace("-", "−")


def regret_reduction_by_mode() -> pd.DataFrame:
    """Per-query Class-A regret reduction with the gate's verdict attached.

    One row per paired query. ``rr`` is mean-cosine decision regret minus coverage-worst decision
    regret, so it is positive where the population-level scorer decided better, and ``mode`` is
    the pre-specified recommendation the gate issued for that query.
    """
    d = pd.read_csv(SRC)

    # The half-planes behind the rows say which side favours which representation, so the sign
    # convention has to be checked rather than inferred from the two method names.
    fam = d.groupby("method")["method_family"].unique()
    assert list(fam[MEAN_METHOD]) == [MEAN_FAMILY], (
        f"{MEAN_METHOD} is not in the {MEAN_FAMILY} family ({fam[MEAN_METHOD]}); the orange "
        f"half-plane would be labelling the wrong retriever")
    assert list(fam[POP_METHOD]) == [POP_FAMILY], (
        f"{POP_METHOD} is not in the {POP_FAMILY} family ({fam[POP_METHOD]}); the blue half-plane "
        f"claims population-level retrieval is favoured, and would be labelling something else")

    base = d[d.method == MEAN_METHOD].set_index(QUERY_KEY)
    pop = d[d.method == POP_METHOD].set_index(QUERY_KEY)
    for name, frame in (("mean", base), ("pop", pop)):
        assert not frame.index.has_duplicates, (
            f"{name} rows are not unique on {QUERY_KEY}; the pairing below would compare "
            f"mismatched queries")
    j = pd.concat([base["decision_regret"].rename("mean"),
                   pop["decision_regret"].rename("pop"),
                   pop["recommendation_mode"].rename("mode"),
                   base["recommendation_mode"].rename("mode_base")], axis=1).dropna()
    assert len(j) == N_QUERIES, f"expected {N_QUERIES} paired queries, got {len(j)}"
    assert (j["mode"] == j["mode_base"]).all(), (
        "the gate's verdict differs between the two methods' rows for the same query; the split "
        "is supposed to be a property of the query, not of the scorer")
    j["rr"] = j["mean"] - j["pop"]
    return j.drop(columns=["mode_base"])


def boot_diff_ci(a, b, n_boot: int = N_BOOT, seed: int = SEED, alpha: float = 0.05):
    """Percentile bootstrap CI for median(a) - median(b), each group resampled at its own n.

    Resampling each group at its own n is the right null for two groups of very different size
    (621 against 133): the interval then inherits the small group's imprecision instead of hiding
    it. Same estimator, seed and n_boot as fig3_style.boot_ci, so the difference interval and the
    two group intervals come from one bootstrap convention.
    """
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    rng = np.random.default_rng(seed)
    draws = (np.median(rng.choice(a, size=(n_boot, a.size), replace=True), axis=1)
             - np.median(rng.choice(b, size=(n_boot, b.size), replace=True), axis=1))
    lo, hi = np.percentile(draws, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return float(np.median(a) - np.median(b)), float(lo), float(hi)


def draw_3d(ax):
    """Median regret reduction inside and outside the gate's recommendation, and the difference."""
    j = regret_reduction_by_mode()
    counts = j["mode"].value_counts()
    n_ms = int(counts.get(MEAN_SUFFICIENT, 0))
    n_plot = [int(counts[m]) for m, _, _ in GROUPS]
    assert sum(n_plot) + n_ms == N_QUERIES, (
        f"the three recommendation modes must account for all {N_QUERIES} queries, "
        f"got {n_plot} + {n_ms}")

    stats = []
    for (mode, _, _), n in zip(GROUPS, n_plot):
        x = j.loc[j["mode"] == mode, "rr"].values
        assert len(x) == n, f"{mode}: counted {n} queries and then selected {len(x)}"
        stats.append(boot_ci(x, stat=np.median, n_boot=N_BOOT, seed=SEED))
    (med_r, lo_r, hi_r), (med_n, lo_n, hi_n) = stats

    a = j.loc[j["mode"] == GROUPS[0][0], "rr"].values
    b = j.loc[j["mode"] == GROUPS[1][0], "rr"].values
    diff, dlo, dhi = boot_diff_ci(a, b)
    p = float(mannwhitneyu(a, b, alternative="two-sided").pvalue)

    # ---- everything the panel and its caption are about to say, asserted first ----------------
    # The caption says the gate does not ENRICH, so both groups having a gain is its premise: a
    # difference of zero between two groups that gained nothing would be a different panel.
    assert lo_r > 0 and lo_n > 0, (
        f"both group intervals are supposed to exclude zero, got [{lo_r:.4f}, {hi_r:.4f}] and "
        f"[{lo_n:.4f}, {hi_n:.4f}]")
    assert lo_n < hi_r and lo_r < hi_n, "the two group intervals are supposed to overlap"
    assert dlo < 0.0 < dhi, (
        f"the caption states that the difference interval contains zero; it is "
        f"[{dlo:.4f}, {dhi:.4f}]")
    assert p > 0.05, f"the panel prints a p from a rank test that did not reject; p = {p:.4f}"
    # "Does not enrich" has to be a BOUNDED measurement rather than a failure to measure, and the
    # bound comes from the data rather than from a chosen number. The interval itself is no longer
    # printed (docstring 4), so this assertion is now the only thing standing between the caption
    # and an inconclusive test read as a negative result.
    assert max(abs(dlo), abs(dhi)) < min(med_r, med_n), (
        f"the difference interval [{dlo:.4f}, {dhi:.4f}] is not small against the gains it is "
        f"supposed to be a null about ({med_r:+.4f}, {med_n:+.4f}); the panel would be reporting "
        f"an inconclusive test as a negative result")
    # The statistics line prints the difference without naming which row is subtracted from which
    # (docstring 10). That is only safe while the number is too small to have a readable sign.
    assert abs(diff) < min(hi_r - lo_r, hi_n - lo_n), (
        f"the printed difference {diff:+.4f} is no longer smaller than the narrower drawn "
        f"interval ({min(hi_r - lo_r, hi_n - lo_n):.4f} wide); its sign now means something and "
        f"the line has to name the direction of the subtraction again")
    assert abs(diff) < 1.0, (
        f"the difference {diff:+.4f} would print wider than the fixed +0.xxx this panel's one "
        f"statistics line was measured against")
    # The 11 mean-sufficient queries were also declined by the gate. The claim must not depend on
    # which of the two readings of "not recommended" is plotted, so the other one is recomputed.
    b_all = j.loc[j["mode"] != GROUPS[0][0], "rr"].values
    diff_all, dlo_all, dhi_all = boot_diff_ci(a, b_all)
    p_all = float(mannwhitneyu(a, b_all, alternative="two-sided").pvalue)
    assert dlo_all < 0.0 < dhi_all and p_all > 0.05, (
        f"the negative holds only on the {len(b)}-query reading of 'not recommended'; pooling the "
        f"{n_ms} mean-sufficient queries in gives [{dlo_all:.4f}, {dhi_all:.4f}], p = {p_all:.4f}")

    # ---- the view ----------------------------------------------------------------------------
    assert XLO < 0.0 < XHI, "zero must be a datum inside the frame, not an edge of it"
    assert XLO < min(lo_r, lo_n) and max(hi_r, hi_n) < XHI, (
        f"the view clips an interval: [{min(lo_r, lo_n):.4f}, {max(hi_r, hi_n):.4f}] outside "
        f"[{XLO}, {XHI}]")
    n_col_x = XLO + N_X * (XHI - XLO)
    assert max(hi_r, hi_n) + 0.010 < n_col_x, (
        f"the widest interval reaches {max(hi_r, hi_n):.4f} and would run into the n column at "
        f"{n_col_x:.4f}")

    ax.set_xlim(XLO, XHI)
    ax.set_ylim(0.0, 1.0)
    label_x = _left_margin(ax)
    cap = CAP_HALF_IN / (ax.get_position().height * ax.figure.get_figheight())

    # Sign, not object: each row plots a signed difference, so the rows are drawn in SHARED grey
    # and blue/orange live in the half-planes behind them.
    lo_wash, hi_wash = sign_field(ax, vertical=True, at=0.0, pop_side="right")
    # sign_field spans the plane to +/-1e9. Cut both washes to the view, and to the band that
    # holds the rows, so the statistics line below sits on white instead of straddling the sign
    # boundary. x is in data coordinates and y is in axes coordinates: axvspan blends the two.
    lo_wash.set_bounds(XLO, WASH_BOT, -XLO, 1.0 - WASH_BOT)
    hi_wash.set_bounds(0.0, WASH_BOT, XHI, 1.0 - WASH_BOT)
    zero_rule(ax, at=0.0, vertical=True, color=TEXT, lw=0.8).set_ydata([WASH_BOT, 1.0])

    # ---- the two point estimates -------------------------------------------------------------
    for (_, label, face), y, (med, lo, hi), n in zip(GROUPS, ROW_Y, stats, n_plot):
        ax.plot([lo, hi], [y, y], lw=LW_LINE, color=SHARED, solid_capstyle="butt", zorder=4)
        for bnd in (lo, hi):
            ax.plot([bnd, bnd], [y - cap, y + cap], lw=LW_LINE, color=SHARED, zorder=4)
        ax.scatter([med], [y], s=MS_DOT, facecolor=face, edgecolor=SHARED, linewidths=0.9,
                   zorder=5)
        ax.text(label_x, y, label, transform=ax.transAxes, fontsize=PT_TICK, color=TEXT,
                ha="left", va="center")
        ax.text(N_X, y, f"n = {n}", transform=ax.transAxes, fontsize=PT_SMALL, color=SUBTLE,
                ha="left", va="center")

    # ---- the one statistic the marks cannot show: how far apart the two rows are --------------
    stat = ax.text(label_x, STAT_Y, f"difference {_fmt(diff)}, p = {p:.2f}",
                   transform=ax.transAxes, fontsize=PT_ANNOT, color=TEXT, ha="left", va="bottom")

    # ---- frame -------------------------------------------------------------------------------
    bare_axes(ax, keep=("bottom",))
    ax.set_xticks(XTICKS)
    ax.set_xticklabels([f"{t:g}" for t in XTICKS], fontsize=PT_TICK)
    ax.set_yticks([])
    ax.tick_params(axis="y", length=0)
    ax.spines["bottom"].set_linewidth(LW_HAIR)
    # The bottom pad this panel is given is 0.42 in, and a two-line 7.2 pt label under 6.8 pt
    # tick numbers needs 0.424 in of it at the deck's default tick pad. The 1.5 pt of tick pad
    # and of label pad recovered here are what keep the label's descenders inside the panel box;
    # the alternative was a smaller label, and this figure does not shrink type.
    ax.tick_params(axis="x", pad=2.0)
    ax.set_xlabel(XLABEL, fontsize=PT_ANNOT, labelpad=1.0)

    # The statistics line starts at the panel box's left edge, so its width is what decides
    # whether ink leaves the box. Measured, not estimated: a p that needed another digit or a
    # longer wording would overrun the box silently otherwise. The renderer is built here, as in
    # fig3a, rather than taken from fig.canvas, so the measurement neither forces a draw of a
    # half-assembled figure nor assumes which backend fig3_assemble is building under.
    fig = ax.figure
    r = RendererAgg(int(fig.get_figwidth() * fig.dpi), int(fig.get_figheight() * fig.dpi), fig.dpi)
    stat_bb = stat.get_window_extent(renderer=r)
    stat_in = stat_bb.width / fig.dpi
    assert stat_in <= MAX_STAT_IN, (
        f"the statistics line prints {stat_in:.3f} in wide and this panel's box allows "
        f"{MAX_STAT_IN} in; shorten the wording before dropping either number")
    # Docstring 6: the line has to sit on WHITE, below the wash band, or it runs through the sign
    # boundary the two rows are read against. STAT_Y, PT_ANNOT and WASH_BOT are three independent
    # numbers, so the clearance is measured rather than assumed.
    ax_bb = ax.get_window_extent(renderer=r)
    stat_top = (stat_bb.y1 - ax_bb.y0) / ax_bb.height
    assert stat_top < WASH_BOT, (
        f"the statistics line reaches {stat_top:.3f} of the axes height and the sign wash starts "
        f"at {WASH_BOT}; the line would straddle the zero boundary instead of sitting on white")

    return {"n": {lab: n for (_, lab, _), n in zip(GROUPS, n_plot)},
            "n_mean_sufficient": n_ms,
            "recommended": (med_r, lo_r, hi_r), "not_recommended": (med_n, lo_n, hi_n),
            "difference": (diff, dlo, dhi), "p": p,
            "difference_pooled_144": (diff_all, dlo_all, dhi_all), "p_pooled_144": p_all}


if __name__ == "__main__":
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from figstyle import apply_style
    from fig3_style import PT_TITLE

    apply_style(sizes=(PT_TITLE, PT_ANNOT, PT_TICK))
    # apply_style sets savefig.bbox = "tight", which would crop the preview back to its ink and
    # hand back a PNG at a different scale from the printed panel. This preview is a 1:1
    # reproduction of the panel BOX this panel occupies in fig3_assemble, so keep the canvas.
    plt.rcParams["savefig.bbox"] = None
    fig = plt.figure(figsize=(2.10, 1.24))
    ax = fig.add_axes([0.76 / 2.10, 0.42 / 1.24, 1.24 / 2.10, 0.65 / 1.24])
    stats_out = draw_3d(ax)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "3d.png")
    fig.savefig(out, dpi=300)
    print(stats_out)
    print(f"wrote {out}")
