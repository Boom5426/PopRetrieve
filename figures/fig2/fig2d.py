"""PopRetrieve Figure 2 panel 2d: the gate's recommendation against the Class-A gain it predicts.

WHAT THIS PANEL SHOWS
---------------------
Queries the pre-specified gate recommends and queries it does not recommend are drawn as two
median regret reductions with seeded bootstrap 95% intervals on one value axis, and beneath a
separator the quantity that carries the panel: the difference of those two medians, with its own
interval and a rank test, sitting on zero. "No enrichment" is therefore a bounded measurement
rather than an impression left by two marks that happen to look alike, and the panel asserts the
bound rather than only that the interval covers zero: the uncertainty about enrichment (at most
0.062) has to be smaller than the gains it is a null about (+0.119 and +0.122), or the honest
phrase would be "could not tell". That inequality is checked at draw time.

Scope: this is Figure 2, so the quantity is objective-aligned (Class A) throughout. Regret
reduction here compares two RETRIEVAL decisions against the same candidate library; nothing on
this panel says anything about whether the retrieved perturbation is biologically useful.

THE 2026-08-31 RESTRAINT PASS AND RESIZE
----------------------------------------
Two things happened to this panel at once, and neither touched the data, the statistic, the
asserted relationships or the colours.

1. THE SENTENCE IS GONE. The panel used to state "Recommendation does not enrich the gain" in
   ink above its own marks. Seven such phrases on one page is seven claims competing for one
   reader; the figure carries evidence and the legend carries the argument. fig2_style.title() is
   deleted and fig2_assemble._assert_no_titles caps panel text at PT_ANNOT, so it cannot come
   back smaller. The phrase now opens this panel's caption entry, where it can be qualified.
   Nothing on the panel replaces it. What the phrase asserted is still asserted in code, in the
   four assertions below that bound the difference, require both groups to have gained, require
   the interval to cover zero and require the test not to reject.

2. THE BOX SHRANK, from 2.63 x 1.43 in to 2.03 x 0.98 in. Panel d was measured as the second
   largest panel in the figure at 14.1 per cent of panel area, above panel c, which is one of the
   figure's two main results, and above every robustness panel. It is a diagnostic reporting a
   null, and it is now the smallest panel at 8.7 per cent. Every position below was re-measured
   against 2.03 x 0.98 in rather than scaled from the old constants.

WHAT WAS CUT TO FIT, AND WHY EACH LOSS IS SAFE
----------------------------------------------
  * THE INTERQUARTILE BANDS, their end rules, their dotted "the distribution continues"
    hairlines, and the "shading: middle half" key that decoded them. At 0.98 in of axes height a
    band is about four printed points tall, and its key was the panel's own admission that it did
    not read without a sentence of help. Dropping the bands also released the value axis: it ran
    to +0.525 only to hold q75 at +0.344, and now runs to +0.205, so the three intervals occupy
    the full width instead of the left two fifths. The spread belongs in the caption, which
    already has room to say it in words. The quartiles are no longer computed, so the assertion
    that they stayed inside the frame is gone with them; the assertions that the drawn intervals
    stay inside the frame remain, and now cover the difference interval too.
  * THE MEAN-SUFFICIENT ACCOUNTING LINE, "+ 11 mean-sufficient queries, not compared (765 in
    all)". The caption already carries the 11 and the reconciliation to 765. What the line
    protected is not lost: the three recommendation modes are still asserted to sum to 765 at
    draw time, and the pooled-144 guard below still refuses to build the panel if the verdict
    depends on setting those 11 aside.
  * THE PER-ROW n LABELS. There is nowhere left to put them. A row name and its n cannot both fit
    in the label gutter left of the zero rule at this width, and text may not sit on that rule;
    the assertion ZERO_CLEAR_IN enforces exactly that and is what rules the arrangement out
    rather than an eye judgement. Both n are still drawn, once, on the line that reports the test
    they are the n of: the Mann-Whitney compares 621 against 133.

SOURCE
------
results/exp12_partial_observed_retrieval/per_query_scores.csv, the per-query rows, paired inside
each query as mean_cosine decision_regret minus DART_coverage_worst decision_regret. This is the
same quantity panel c plots, computed the same way and from the same file, so the two panels
cannot drift apart.

The panel deliberately does NOT read results/exp12_partial_observed_retrieval/
recommendation_vs_outcome.csv, which an earlier cut of this panel used. That file holds
pre-aggregated medians only, so an interval drawn beside them would have had an n that was not
the n the panel plots. Every number drawn here, medians, intervals, counts and the rank test, is
recomputed from the per-query rows at draw time; there are no literals in any label.

THE 765 ADD UP, AND THE 11 DO NOT CHANGE THE ANSWER
---------------------------------------------------
The 765 paired partial-observed queries of panel c split three ways by recommendation_mode:
621 DART_recommended, 133 mean_or_no_call, and 11 mean_sufficient. Only the first two are the
manuscript's two-way comparison (NREC and NNONREC in the .tex); the 11 mean-sufficient queries
(median regret reduction exactly 0.000) are neither plotted nor named on the panel any more, so
the three counts are asserted to sum to 765 instead.

mean_sufficient is a third gate state and those 11 queries were also not recommended, so the set
of queries the gate declined is 144, not the 133 in the plotted row. The rows follow the
manuscript's defined terms and the caption is where those terms are defined. The risk this
creates is that the negative result could be an artefact of which queries were set aside, so the
panel refuses to depend on the choice: it recomputes the same difference over all 144
non-recommended queries and asserts that reading reaches the same verdict (+0.005, 95% CI -0.055
to +0.064, Mann-Whitney p = 0.81, against -0.003, -0.062 to +0.058, p = 0.97 for the plotted
133). Only the plotted reading is drawn; the pooled one is a guard.

JUDGEMENT CALLS A READER COULD REASONABLY DISAGREE WITH
-------------------------------------------------------
1. The difference of medians is drawn on the SAME value axis as the two group medians, below a
   separator, rather than on its own offset axis in the Gardner-Altman manner. Both quantities
   are in the same units and both are read against the same zero, so one axis is honest and buys
   the direct visual reading "the groups sit right of the rule, their difference sits on it". The
   cost is that a hurried reader could take the difference row for a third group; the separator,
   the grey diamond and the row name are what argue against that.
2. Both groups are drawn in the population colour, distinguished by filled versus open marker and
   by row. They are the same quantity (a population-level scorer's advantage over a mean-level
   one) measured on two sets of queries, so giving the two rows two hues would invent a family
   distinction the figure's vocabulary does not have.
3. THE LEFT THIRD OF THE VALUE AXIS IS A LABEL GUTTER. The axis runs from -0.17 although no mark
   reaches below -0.063, because the row names have to live inside the axes: panel d's left pad
   is 0.72 in and "Not recommended" is 0.85 in wide at PT_ANNOT, so it cannot be a y tick label,
   and fig2_assemble's pads are not this module's to change. Putting the names in the low-value
   region rather than above their rows is what let three rows, three marks and the statistics fit
   in 0.98 in of height. The tick at -0.1 keeps the gutter legible as axis rather than as margin.
4. THE ZERO RULE STOPS ABOVE THE STATISTICS, at ZERO_BOT, instead of running the full height as
   fig2_style.zero_rule draws it. It is a datum for the marks, and the three statistics lines are
   the only text wide enough to cross it. Breaking the rule where the marks stop was preferred to
   setting three lines of type over a hairline. The shared helper still draws it: axvline stores
   its ydata as an axes fraction, so the returned line is trimmed to [ZERO_BOT, 1.0] afterwards,
   which is how panel f trims the same rule. The WEIGHT is therefore the helper's own default.
   The COLOUR is not, and the deviation is deliberate: the helper defaults to SUBTLE, this rule is
   drawn one step lighter at FAINT because it runs behind more than half the panel height instead
   of under a single row of marks, and panel c draws the same datum for the same quantity at
   SUBTLE. A reader comparing the two panels is looking at one rule at two weights.
5. The Mann-Whitney P is printed on the panel but its caveat is not. Queries inside one cell line
   share a candidate library, so the test's independence assumption is violated and P is
   anticonservative. That bias runs towards rejecting; the test did not reject even so, which
   makes this negative result stronger rather than weaker, so a reader who takes P = 0.97 at face
   value is not misled in the direction the panel claims. The caveat belongs in the caption and
   is stated here.
6. QUERY_KEY is duplicated from fig2c rather than imported, so that a concurrent edit to a
   sibling panel cannot change what this panel pairs on. The pairing is guarded instead by the
   assertion that it yields exactly 765 queries and that each method's rows are unique on the key.
7. The difference is drawn top row minus bottom row, which is not a universal convention, so the
   direction is written out under the row name rather than left to be inferred from a sign. It is
   built from the row names themselves, so a renamed row cannot leave a stale direction behind.
8. The interval bounds are a seeded percentile bootstrap at n_boot = 4000. In the 133-query group
   the bootstrap median takes only about 38 distinct values, so the drawn lower cap moves between
   +0.0611 and +0.0657 across seeds, about 0.02 in of ink. The seed is fixed and the medians
   themselves are exact, but no CI bound from this panel should be quoted to four decimals.

Run standalone: python fig2d.py
"""
from __future__ import annotations

import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.backends.backend_agg import RendererAgg
from scipy.stats import mannwhitneyu

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fig2_style import (FAINT, HAIRLINE, LW_HAIR, LW_LINE, MS_DOT, POP,  # noqa: E402
                        PT_ANNOT, PT_SMALL, REPO, SHARED, SUBTLE, TEXT,
                        bare_axes, boot_median_ci, zero_rule)

# The query identity panel c pairs on. Duplicated rather than imported: see docstring note 6.
QUERY_KEY = ["split_type", "cell_line", "heldout_drug", "observed_library_fraction", "seed"]
N_QUERIES = 765
POP_METHOD, MEAN_METHOD = "DART_coverage_worst", "mean_cosine"

# The two compared modes, in drawing order, with the marker fill that separates them. The third
# mode (mean_sufficient) is counted and asserted, never plotted; see docstring.
GROUPS = [("DART_recommended", "Recommended", POP),
          ("mean_or_no_call", "Not recommended", "white")]
MEAN_SUFFICIENT = "mean_sufficient"
DIFF_LABEL = "Difference"

MINUS = "−"        # U+2212, not a hyphen and not mathtext: see figstyle.apply_style

# ---------------------------------------------------------------------------- geometry, 2.03 x 0.98 in
# XLIM[0] is a label gutter rather than a data range: the marks reach only to -0.063, and the
# extra room to the left is what the three row names sit in. Both bounds are re-derived below in
# printed inches and asserted, so neither can drift out of agreement with the type.
XLIM = (-0.17, 0.205)
XTICKS = [-0.1, 0.0, 0.1, 0.2]

# Vertical ledger, in axes-height units (ylim is 0..1, so one unit is the 0.98 in of axes). Set
# from a points-from-the-top budget at 0.98 in = 70.56 pt: rows at 6.5 / 18.0 pt, separator at
# 27.0, difference row at 35.5, statistics at 46.5 / 55.5 / 64.5.
ROW_Y = [0.908, 0.745]          # group rows: the name and the interval share one baseline
SEP_Y = 0.617                   # below it the quantity changes to a difference
DIFF_Y = 0.497
STAT_Y = [0.341, 0.213, 0.086]  # direction, estimate with interval, test with its n
ZERO_BOT = 0.430                # the zero rule stops here, above the statistics: note 4

CAP_H = 0.034                   # half-height of an interval end cap, ~2.4 printed pt at 0.98 in
LABEL_CLEAR_IN = 0.045          # printed inches demanded between a row name and its own interval
ZERO_CLEAR_IN = 0.030           # printed inches demanded between any mark-region text and x = 0
N_BOOT, SEED = 4000, 0


def _fmt(v: float, digits: int = 3) -> str:
    """Signed number with a typographic minus, so the panel does not mix hyphens and minuses."""
    return f"{v:+.{digits}f}".replace("-", MINUS)


def regret_reduction_by_mode() -> pd.DataFrame:
    """Per-query Class-A regret reduction with the gate's verdict attached.

    Returns one row per paired query: `rr` is mean-cosine decision regret minus coverage-worst
    decision regret, exactly as panel c defines it, and `mode` is the pre-specified
    recommendation the gate issued for that query.
    """
    d = pd.read_csv(f"{REPO}/results/exp12_partial_observed_retrieval/per_query_scores.csv")
    base = d[d.method == MEAN_METHOD].set_index(QUERY_KEY)
    pop = d[d.method == POP_METHOD].set_index(QUERY_KEY)
    for name, frame in (("mean", base), ("pop", pop)):
        assert not frame.index.has_duplicates, (
            f"{name} rows are not unique on {QUERY_KEY}; the pairing below would compare "
            f"mismatched queries.")
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
    """Percentile bootstrap CI for the difference of two independent medians, median(a) - median(b).

    Resamples each group at its own n, which is the right null for two groups of very different
    size (621 against 133): the interval then inherits the small group's imprecision instead of
    hiding it. Same estimator, seed and n_boot as fig2_style.boot_median_ci, so the difference
    interval and the two group intervals are drawn from one bootstrap convention.
    """
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    rng = np.random.default_rng(seed)
    draws = (np.median(rng.choice(a, size=(n_boot, a.size), replace=True), axis=1)
             - np.median(rng.choice(b, size=(n_boot, b.size), replace=True), axis=1))
    lo, hi = np.percentile(draws, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return float(np.median(a) - np.median(b)), float(lo), float(hi)


def _interval(ax, lo, hi, med, y, colour, face, marker):
    """One point estimate with its bootstrap interval, drawn as bar, end caps and marker."""
    ax.plot([lo, hi], [y, y], lw=LW_LINE, color=colour, solid_capstyle="butt", zorder=4)
    for b in (lo, hi):
        ax.plot([b, b], [y - CAP_H, y + CAP_H], lw=LW_LINE, color=colour, zorder=4)
    # Every marker in the panel carries the same 0.9 pt ring in its row's colour, so the filled
    # and the open marker print at the same diameter and the fill is the only difference between
    # them. Provenance by glyph, never by a second hue: fig2_style's rule.
    ax.scatter([med], [y], s=MS_DOT, marker=marker, facecolor=face, edgecolor=colour,
               linewidths=0.9, zorder=5)


def draw_2d(ax):
    """Median Class-A regret reduction inside and outside the gate's recommendation, and their difference."""
    j = regret_reduction_by_mode()
    counts = j["mode"].value_counts()
    n_ms = int(counts.get(MEAN_SUFFICIENT, 0))
    n_plot = [int(counts[m]) for m, _, _ in GROUPS]
    assert sum(n_plot) + n_ms == N_QUERIES, (
        f"the three recommendation modes must account for all {N_QUERIES} queries, "
        f"got {n_plot} + {n_ms}")

    # The frame is resolved FIRST, because every layout assertion below measures drawn type
    # against the value scale and that scale does not exist until the limits are set.
    bare_axes(ax, keep=("bottom",))
    ax.set_xlim(*XLIM)
    ax.set_ylim(0.0, 1.0)
    ax.set_xticks(XTICKS)
    ax.set_yticks([])
    ax.tick_params(axis="y", length=0)
    ax.spines["bottom"].set_bounds(XLIM[0], XLIM[1])
    ax.set_xlabel(f"regret reduction\n(mean cosine {MINUS} coverage-worst)", linespacing=1.2)

    # Zero is a datum for BOTH registers of this panel: no gain for a group row, no enrichment for
    # the difference row. The shared helper draws it at its own weight; the colour is overridden
    # one step lighter than the helper's SUBTLE default because the rule runs behind more than
    # half the panel height. Trimmed to stop at ZERO_BOT rather than run under the three
    # statistics lines: see docstring note 4.
    zero_rule(ax, 0.0, color=FAINT, zorder=1).set_ydata([ZERO_BOT, 1.0])

    stats, labels = [], []
    for (mode, label, face), y in zip(GROUPS, ROW_Y):
        x = j.loc[j["mode"] == mode, "rr"].values
        med, lo, hi = boot_median_ci(x, n_boot=N_BOOT, seed=SEED)
        stats.append((med, lo, hi))
        assert XLIM[0] < lo and hi < XLIM[1], f"{mode}: 95% CI leaves the axis {XLIM}"
        _interval(ax, lo, hi, med, y, POP, face, "o")
        labels.append((ax.text(XLIM[0], y, label, fontsize=PT_ANNOT, color=TEXT,
                               ha="left", va="center"), lo))

    (med_r, lo_r, hi_r), (med_n, lo_n, hi_n) = stats
    # Both groups having a gain is the premise of a null about ENRICHMENT of that gain: a
    # difference of zero between two groups that gained nothing would be a different panel making
    # a different claim. Asserted so the caption's phrase cannot outlive the data.
    assert lo_r > 0 and lo_n > 0, (
        f"both group intervals are supposed to exclude zero, got [{lo_r:.4f}, {hi_r:.4f}] and "
        f"[{lo_n:.4f}, {hi_n:.4f}]")
    assert lo_n < hi_r and lo_r < hi_n, "the two group intervals are supposed to overlap"

    ax.axhline(SEP_Y, color=HAIRLINE, lw=LW_HAIR, zorder=1)

    # ---- the panel's content: the difference, with its interval and the rank test
    a = j.loc[j["mode"] == GROUPS[0][0], "rr"].values
    b = j.loc[j["mode"] == GROUPS[1][0], "rr"].values
    diff, dlo, dhi = boot_diff_ci(a, b)
    p = float(mannwhitneyu(a, b, alternative="two-sided").pvalue)
    assert XLIM[0] < dlo and dhi < XLIM[1], (
        f"the difference interval [{dlo:.4f}, {dhi:.4f}] leaves the axis {XLIM}")
    assert dlo < 0.0 < dhi, (
        f"the panel draws the difference interval across zero; it is [{dlo:.4f}, {dhi:.4f}]")
    assert p > 0.05, f"the panel prints a rank test that did not reject; p = {p:.4f}"

    # "does not enrich" has to be a BOUNDED measurement, not a failure to measure. The bound is
    # taken from the data rather than from a chosen number: the uncertainty about enrichment must
    # be smaller than the gain it is a null about, otherwise the honest phrase would be "could not
    # tell" and the caption's opening sentence would be false.
    assert max(abs(dlo), abs(dhi)) < min(med_r, med_n), (
        f"the difference interval [{dlo:.4f}, {dhi:.4f}] is not small against the gains it is "
        f"supposed to be a null about ({med_r:+.4f}, {med_n:+.4f}); the panel would be reporting "
        f"an inconclusive test as a negative result")

    # The 11 mean-sufficient queries are queries the gate ALSO did not recommend; they sit outside
    # the plotted row because the manuscript's two-way comparison is 621 against 133. The panel's
    # claim must not depend on that choice, so the same difference is recomputed over all 144
    # non-recommended queries and required to reach the same verdict.
    b_all = j.loc[j["mode"] != GROUPS[0][0], "rr"].values
    _, dlo_all, dhi_all = boot_diff_ci(a, b_all)
    p_all = float(mannwhitneyu(a, b_all, alternative="two-sided").pvalue)
    assert dlo_all < 0.0 < dhi_all and p_all > 0.05, (
        f"the null holds only on the 133-query reading of 'not recommended'; pooling the "
        f"{n_ms} mean-sufficient queries in gives [{dlo_all:.4f}, {dhi_all:.4f}], p = {p_all:.4f}")

    _interval(ax, dlo, dhi, diff, DIFF_Y, SHARED, SHARED, "D")
    labels.append((ax.text(XLIM[0], DIFF_Y, DIFF_LABEL, fontsize=PT_ANNOT, color=TEXT,
                           ha="left", va="center"), dlo))

    # A signed number needs its direction defined, and the direction is built from the row names
    # so a renamed row cannot leave a stale definition behind.
    for y, s, colour in (
            (STAT_Y[0], f"{GROUPS[0][1].lower()} {MINUS} {GROUPS[1][1].lower()}", SUBTLE),
            (STAT_Y[1], f"{_fmt(diff)}, 95% CI {_fmt(dlo)} to {_fmt(dhi)}", TEXT),
            (STAT_Y[2], f"Mann-Whitney $P$ = {p:.2f}, n = {n_plot[0]} vs {n_plot[1]}", SUBTLE)):
        ax.text(XLIM[0], y, s, fontsize=PT_SMALL, color=colour, ha="left", va="center")

    # ---- the arrangement, measured in printed inches rather than eyeballed -------------------
    # Three things have to hold at 2.03 in or the panel is lying about its own layout: no row name
    # may run into the interval it names, no text in the mark region may sit on the zero rule, and
    # no drawn line may leave the axes. All three are properties of TYPE against a resolved value
    # scale, so they are measured with a renderer instead of assumed from the constants above.
    fig = ax.get_figure()
    r = RendererAgg(int(fig.get_figwidth() * fig.dpi), int(fig.get_figheight() * fig.dpi), fig.dpi)
    ax_x0_in = ax.get_position().x0 * fig.get_figwidth()
    axw_in = ax.get_position().width * fig.get_figwidth()

    def span_in(t):
        """The printed inches a drawn label occupies, measured from the axes' left edge."""
        bb = t.get_window_extent(renderer=r)
        return bb.x0 / fig.dpi - ax_x0_in, bb.x1 / fig.dpi - ax_x0_in

    def x_in(v):
        """Printed inches from the axes' left edge, at value ``v`` on the resolved scale."""
        return (v - XLIM[0]) / (XLIM[1] - XLIM[0]) * axw_in

    for t, ink in labels:
        gap = x_in(ink) - span_in(t)[1]
        assert gap >= LABEL_CLEAR_IN, (
            f"row name {t.get_text()!r} leaves only {gap:.3f} in before its own interval starts, "
            f"under the {LABEL_CLEAR_IN} in this width demands. Widen the gutter by lowering "
            f"XLIM[0], or the name and the mark will read as one object.")

    z_in = x_in(0.0)
    for t in ax.texts:
        x0, x1 = span_in(t)
        assert -0.002 <= x0 and x1 <= axw_in + 0.002, (
            f"{t.get_text()!r} spans {x0:.3f} to {x1:.3f} in and the axes are {axw_in:.3f} in "
            f"wide; it would print outside the panel box.")
        if t.get_position()[1] > ZERO_BOT:
            assert x1 <= z_in - ZERO_CLEAR_IN, (
                f"{t.get_text()!r} reaches {x1:.3f} in, within {ZERO_CLEAR_IN} in of the zero "
                f"rule at {z_in:.3f} in. Text in the mark region may not sit on the datum.")


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from figstyle import apply_style
    from fig2_style import PT_TICK, PT_TITLE

    apply_style(sizes=(PT_TITLE, PT_ANNOT, PT_TICK))
    fig = plt.figure(figsize=(2.85, 1.67))
    ax = fig.add_axes([0.72 / 2.85, 0.52 / 1.67, 2.03 / 2.85, 0.98 / 1.67])
    draw_2d(ax)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "2d.png")
    fig.savefig(out, dpi=300)
    print(f"wrote {out}")
