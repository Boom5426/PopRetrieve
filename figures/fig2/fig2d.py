"""PopRetrieve Figure 2 panel 2d: the pre-specified gate does not enrich the Class-A gain.

WHAT THIS PANEL CLAIMS
----------------------
One claim, and it is a negative: queries the gate recommends and queries it does not recommend
show the SAME per-query regret reduction. The panel draws two median estimates with seeded
bootstrap 95% intervals on a shared value axis, and underneath them the quantity that carries the
claim: the difference of the two medians with its own interval, straddling zero. "No enrichment"
is therefore a bounded measurement rather than an impression left by two bars that happen to look
alike, and the panel asserts the bound rather than asserting only that the interval covers zero:
the uncertainty about enrichment (at most 0.062) has to be smaller than the gains it is a null
about (+0.119 and +0.122), or the honest phrase would be "could not tell" and the title false.

Scope: this is Figure 2, so the quantity is objective-aligned (Class A) throughout. Regret
reduction here compares two RETRIEVAL decisions against the same candidate library; nothing on
this panel says anything about whether the retrieved perturbation is biologically useful.

SOURCE
------
results/exp12_partial_observed_retrieval/per_query_scores.csv, the per-query rows, paired inside
each query as mean_cosine decision_regret minus DART_coverage_worst decision_regret. This is the
same quantity panel c plots, computed the same way and from the same file, so the two panels
cannot drift apart.

The panel deliberately does NOT read results/exp12_partial_observed_retrieval/
recommendation_vs_outcome.csv, which the previous cut of this panel used. That file holds
pre-aggregated medians only, so an interval drawn beside them would have had an n that was not
the n the panel plots. Every number drawn here, medians, intervals, quartiles, counts and the
rank test, is recomputed from the per-query rows at draw time.

THE 765 ADD UP, AND THE 11 DO NOT CHANGE THE ANSWER
---------------------------------------------------
The 765 paired partial-observed queries of panel c split three ways by recommendation_mode:
621 DART_recommended, 133 mean_or_no_call, and 11 mean_sufficient. Only the first two are the
manuscript's two-way comparison (NREC and NNONREC in the .tex); the 11 mean-sufficient queries
(median regret reduction exactly 0.000) are named on the panel rather than plotted, so 621 + 133
does not silently fail to reach 765. The three counts are asserted to sum to 765 at draw time.

Note what the drawn row label does NOT say. mean_sufficient is a third gate state and those 11
queries were also not recommended, so the set of queries the gate declined is 144, not the 133 in
the plotted row. The row follows the manuscript's defined term, and the caption is where that term
is defined. The risk this creates is that the negative result could be an artefact of which
queries were set aside, so the panel refuses to depend on the choice: it recomputes the same
difference over all 144 non-recommended queries and asserts that reading reaches the same verdict
(+0.005, 95% CI -0.055 to +0.065, Mann-Whitney p = 0.81, against -0.003, -0.062 to +0.058,
p = 0.97 for the plotted 133). Only the plotted reading is drawn; the pooled one is a guard.

JUDGEMENT CALLS A READER COULD REASONABLY DISAGREE WITH
-------------------------------------------------------
1. The difference of medians is drawn on the SAME value axis as the two group medians, below a
   separator, rather than on its own offset axis in the Gardner-Altman manner. Both quantities are
   in the same units and both are read against the same zero, so one axis is honest and buys the
   direct visual reading "the groups sit right of zero, their difference sits on it". The cost is
   that a hurried reader could take the difference row for a third group; the separator, the grey
   diamond and the row label are what argue against that.
2. Both groups are drawn in the population colour, distinguished by filled versus open marker and
   by row. They are the same quantity (a population-level scorer's advantage over a mean-level
   one) measured on two sets of queries, so giving the two rows two hues would invent a family
   distinction the figure's vocabulary does not have.
3. The spread behind each interval is shown as the interquartile range only, as a pale bar, with
   a dotted hairline running to the frame on each side to say the distribution continues. A
   symmetric violin would misdescribe these distributions, which are strongly right-skewed
   (q25 at 0.000, median +0.119, q75 +0.328, maximum +2.82 for the recommended group). Showing
   the full range instead would need an axis about six times wider (the pooled range runs from
   −1.09 to +2.82), on which the difference interval this panel exists to show would be under
   0.1 in long and unreadable. So the tails are
   deliberately outside the frame, and the dotted continuations say so. The panel asserts that
   both quartiles of both groups lie inside the axis, so the bar itself is never silently clipped.
4. The Mann-Whitney p is printed on the panel but its caveat is not. Queries inside one cell line
   share a candidate library, so the test's independence assumption is violated and p is
   anticonservative. That bias runs towards rejecting; the test did not reject even so, which
   makes this negative result stronger rather than weaker, so a reader who takes p = 0.97 at face
   value is not misled in the direction the panel claims. The caveat belongs in the caption and
   is stated here; it was not worth a fourth line of type over the difference row.
5. QUERY_KEY is duplicated from fig2c rather than imported, so that a concurrent edit to a
   sibling panel cannot change what this panel pairs on. The pairing is guarded instead by the
   assertion that it yields exactly 765 queries and that each method's rows are unique on the key.
6. The difference is drawn top row minus bottom row, which is not a universal convention, so the
   direction is written out under the row label rather than left to be inferred from a sign. It is
   built from the row labels themselves, so a renamed row cannot leave a stale direction behind.
7. The interval bounds are a seeded percentile bootstrap at n_boot = 4000. In the 133-query group
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
from scipy.stats import mannwhitneyu

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fig2_style import (FAINT, HAIRLINE, LW_HAIR, LW_LINE, MS_DOT, POP,  # noqa: E402
                        POP_WASH, PT_ANNOT, PT_SMALL, REPO, SHARED, SUBTLE, TEXT,
                        bare_axes, boot_median_ci, title, zero_rule)

# The query identity panel c pairs on. Duplicated rather than imported: see docstring note 5.
QUERY_KEY = ["split_type", "cell_line", "heldout_drug", "observed_library_fraction", "seed"]
N_QUERIES = 765
POP_METHOD, MEAN_METHOD = "DART_coverage_worst", "mean_cosine"

# The two compared modes, in drawing order, with the marker fill that separates them. The third
# mode (mean_sufficient) is counted and named, never plotted; see docstring.
GROUPS = [("DART_recommended", "Recommended", POP),
          ("mean_or_no_call", "Not recommended", "white")]
MEAN_SUFFICIENT = "mean_sufficient"

XLIM = (-0.135, 0.525)
XTICKS = [-0.1, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
ROW_Y = [0.845, 0.590]          # the two group rows, in axes-height units (ylim is 0..1)
LAB_Y = [0.955, 0.700]          # the label line above each row
NOTE_Y = 0.455                  # the mean-sufficient accounting line
SEP_Y = 0.360                   # separator: below it the quantity changes to a difference
DIFF_LAB_Y = 0.250
DIFF_Y = 0.135
STAT_X = 0.10                   # left edge of the difference readout, in data units
N_X_FRAC = 0.34                 # where the per-row n starts, clear of the longest row name
BAR_H = 0.030                   # half-height of the interquartile bar
CAP_H = 0.022                   # half-height of an interval end cap
N_BOOT, SEED = 4000, 0


def _frac_x(frac: float) -> float:
    """A horizontal position given as a fraction of the axes width, in data units."""
    return XLIM[0] + frac * (XLIM[1] - XLIM[0])


def _fmt(v: float, digits: int = 3) -> str:
    """Signed number with a typographic minus, so the panel does not mix hyphens and minuses."""
    return f"{v:+.{digits}f}".replace("-", "−")


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


def draw_2d(ax):
    """Median Class-A regret reduction inside and outside the gate's recommendation, and their difference."""
    j = regret_reduction_by_mode()
    counts = j["mode"].value_counts()
    n_ms = int(counts.get(MEAN_SUFFICIENT, 0))
    n_plot = [int(counts[m]) for m, _, _ in GROUPS]
    assert sum(n_plot) + n_ms == N_QUERIES, (
        f"the three recommendation modes must account for all {N_QUERIES} queries, "
        f"got {n_plot} + {n_ms}")

    # Zero is a datum for BOTH registers of this panel: no gain for a group row, no enrichment
    # for the difference row. It is drawn lighter than fig2_style.zero_rule's default because it
    # runs the full height of the panel here, and at META grey it would out-weigh the marks.
    zero_rule(ax, 0.0, vertical=True, color=FAINT, lw=0.8, zorder=1)

    stats = []
    for (mode, label, face), y, ylab, n in zip(GROUPS, ROW_Y, LAB_Y, n_plot):
        x = j.loc[j["mode"] == mode, "rr"].values
        med, lo, hi = boot_median_ci(x, n_boot=N_BOOT, seed=SEED)
        q25, q75 = (float(v) for v in np.percentile(x, [25, 75]))
        stats.append((med, lo, hi))

        # Nothing about the bar may be silently clipped: if a quartile ever leaves the frame the
        # pale bar would understate the spread without saying so.
        assert XLIM[0] < q25 and q75 < XLIM[1], (
            f"{mode}: interquartile range [{q25:.3f}, {q75:.3f}] leaves the axis {XLIM}")
        assert XLIM[0] < lo and hi < XLIM[1], f"{mode}: 95% CI leaves the axis {XLIM}"

        # Middle half of the queries. Both q25 sit within 0.0001 of zero, so a plain filled bar
        # would read as a bar chart rooted at the origin, which is the one reading this panel
        # must not invite. The two vertical end rules and the dotted continuations make it a
        # bounded band with the distribution running out of the frame on both sides.
        ax.add_patch(plt.Rectangle((q25, y - BAR_H), q75 - q25, 2 * BAR_H,
                                   facecolor=POP_WASH, edgecolor="none", zorder=2))
        for q in (q25, q75):
            ax.plot([q, q], [y - BAR_H, y + BAR_H], lw=LW_HAIR, color=FAINT, zorder=3)
        # the distribution continues past both ends of the frame; it is not drawn, it is declared
        for x0, x1 in ((XLIM[0] + 0.006, q25), (q75, XLIM[1] - 0.006)):
            ax.plot([x0, x1], [y, y], ls=(0, (1.2, 1.6)), lw=LW_HAIR, color=FAINT, zorder=2)

        ax.plot([lo, hi], [y, y], lw=LW_LINE, color=POP, solid_capstyle="butt", zorder=4)
        for b in (lo, hi):
            ax.plot([b, b], [y - CAP_H, y + CAP_H], lw=LW_LINE, color=POP, zorder=4)
        ax.scatter([med], [y], s=MS_DOT, facecolor=face, edgecolor=POP, linewidths=0.9,
                   zorder=5)

        ax.text(XLIM[0], ylab, label, fontsize=PT_ANNOT, color=TEXT, ha="left", va="center")
        ax.text(_frac_x(N_X_FRAC), ylab, f"n = {n}", fontsize=PT_SMALL, color=SUBTLE,
                ha="left", va="center")

    # Named once, at the far right of the first label line, where it is clearly a note about the
    # marks and not part of a row name: the shaded band is a quartile span, not a value bar.
    # It governs both rows.
    ax.text(XLIM[1], LAB_Y[0], "shading: middle half", fontsize=PT_SMALL, color=SUBTLE,
            ha="right", va="center")

    (med_r, lo_r, hi_r), (med_n, lo_n, hi_n) = stats
    # The title says the recommendation does not enrich THE GAIN, so both groups having a gain is
    # its premise: a difference of zero between two groups that gained nothing would be a
    # different panel making a different claim. Asserted so the title cannot outlive the data.
    assert lo_r > 0 and lo_n > 0, (
        f"both group intervals are supposed to exclude zero, got [{lo_r:.4f}, {hi_r:.4f}] and "
        f"[{lo_n:.4f}, {hi_n:.4f}]")
    assert lo_n < hi_r and lo_r < hi_n, "the two group intervals are supposed to overlap"

    ax.text(XLIM[0], NOTE_Y,
            f"+ {n_ms} mean-sufficient queries, not compared ({len(j)} in all)",
            fontsize=PT_SMALL, color=SUBTLE, ha="left", va="center")
    ax.axhline(SEP_Y, color=HAIRLINE, lw=LW_HAIR, zorder=1)

    # ---- the headline: the difference, with its interval and the rank test
    a = j.loc[j["mode"] == GROUPS[0][0], "rr"].values
    b = j.loc[j["mode"] == GROUPS[1][0], "rr"].values
    diff, dlo, dhi = boot_diff_ci(a, b)
    p = float(mannwhitneyu(a, b, alternative="two-sided").pvalue)
    assert dlo < 0.0 < dhi, (
        f"the panel states that the difference interval contains zero; it is [{dlo:.4f}, {dhi:.4f}]")
    assert p > 0.05, f"the panel prints a rank test that did not reject; p = {p:.4f}"
    assert XLIM[0] < dlo and dhi + 0.012 < STAT_X, (
        f"the difference interval [{dlo:.4f}, {dhi:.4f}] would run into its own readout at "
        f"x = {STAT_X}")

    # "does not enrich" has to be a BOUNDED measurement, not a failure to measure. The bound is
    # taken from the data rather than from a chosen number: the uncertainty about enrichment must
    # be smaller than the gain it is a null about, otherwise the honest phrase would be "could not
    # tell" and this title would be false.
    assert max(abs(dlo), abs(dhi)) < min(med_r, med_n), (
        f"the difference interval [{dlo:.4f}, {dhi:.4f}] is not small against the gains it is "
        f"supposed to be a null about ({med_r:+.4f}, {med_n:+.4f}); the panel would be reporting "
        f"an inconclusive test as a negative result")

    # The 11 mean-sufficient queries are queries the gate ALSO did not recommend; they sit outside
    # the plotted row because the manuscript's two-way comparison is 621 against 133. The panel's
    # claim must not depend on that choice, so the same difference is recomputed over all 144
    # non-recommended queries and required to reach the same verdict. Without this, "Recommendation
    # does not enrich the gain" could be an artefact of which queries were set aside.
    b_all = j.loc[j["mode"] != GROUPS[0][0], "rr"].values
    _, dlo_all, dhi_all = boot_diff_ci(a, b_all)
    p_all = float(mannwhitneyu(a, b_all, alternative="two-sided").pvalue)
    assert dlo_all < 0.0 < dhi_all and p_all > 0.05, (
        f"the title holds only on the 133-query reading of 'not recommended'; pooling the "
        f"{n_ms} mean-sufficient queries in gives [{dlo_all:.4f}, {dhi_all:.4f}], p = {p_all:.4f}")

    ax.plot([dlo, dhi], [DIFF_Y, DIFF_Y], lw=LW_LINE, color=SHARED, solid_capstyle="butt",
            zorder=4)
    for bnd in (dlo, dhi):
        ax.plot([bnd, bnd], [DIFF_Y - CAP_H, DIFF_Y + CAP_H], lw=LW_LINE, color=SHARED, zorder=4)
    ax.scatter([diff], [DIFF_Y], s=MS_DOT, marker="D", facecolor=SHARED, edgecolor="none",
               zorder=5)

    ax.text(XLIM[0], DIFF_LAB_Y, "Difference", fontsize=PT_ANNOT, color=TEXT, ha="left",
            va="center")
    # A signed number needs a direction. Set flush with the numeric readout below it rather than
    # with the n column above, so the three lines of the difference block share one left edge and
    # this reads as a definition of the number, not as a third group.
    ax.text(STAT_X, DIFF_LAB_Y, f"{GROUPS[0][1].lower()} − {GROUPS[1][1].lower()}",
            fontsize=PT_SMALL, color=SUBTLE, ha="left", va="center")
    ax.text(STAT_X, DIFF_Y,
            f"{_fmt(diff)}   95% CI {_fmt(dlo)} to {_fmt(dhi)}\nMann-Whitney p = {p:.2f}",
            fontsize=PT_SMALL, color=TEXT, ha="left", va="center", linespacing=1.45)

    # ---- frame
    bare_axes(ax, keep=("bottom",))
    ax.set_xlim(*XLIM)
    ax.set_ylim(0.0, 1.0)
    ax.set_xticks(XTICKS)
    ax.set_yticks([])
    ax.tick_params(axis="y", length=0)
    ax.spines["bottom"].set_bounds(XLIM[0], XLIM[1])
    ax.set_xlabel("regret reduction (mean cosine $-$ coverage-worst)")
    title(ax, "Recommendation does not enrich the gain")


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from figstyle import apply_style
    from fig2_style import PT_TICK, PT_TITLE

    apply_style(sizes=(PT_TITLE, PT_ANNOT, PT_TICK))
    fig = plt.figure(figsize=(3.45, 1.95))
    ax = fig.add_axes([0.72 / 3.45, 0.52 / 1.95, 2.63 / 3.45, 1.43 / 1.95])
    draw_2d(ax)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "2d.png")
    fig.savefig(out, dpi=300)
    print(f"wrote {out}")
