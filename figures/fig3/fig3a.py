"""PopRetrieve Figure 3 panel a: the headline reversal, drawn as ONE quantity judged twice.

WHAT THIS PANEL CLAIMS
----------------------
Both rows are the SAME signed quantity, the population-minus-mean retrieval advantage, on the
SAME 600 paired leave-drug-out queries. Nothing is retrained between the rows; only the metric
doing the judging changes. Judged by response matching, the advantage has median +0.129 and 73
per cent of queries favour population retrieval. Judged by mechanism recovery, the median is
exactly 0.000 and 34 per cent of queries favour population retrieval. That is the reversal the
whole figure exists to carry, and it is two of the figure's four skeleton numbers.

SOURCE
------
results/exp12_partial_observed_retrieval/per_query_scores.csv, read directly. Rows are restricted
to ``split_type == leave_drug_out`` and paired on
(split_type, cell_line, heldout_drug, observed_library_fraction, seed), which is unique within
that split; the pairing is asserted to yield exactly 600 queries. Class A (response matching) is
``mean_cosine`` decision_regret minus ``DART_coverage_worst`` decision_regret, and Class B
(mechanism recovery) is ``DART_coverage_worst`` moa_ndcg minus ``mean_cosine`` moa_ndcg. The two
subtractions run in opposite directions because the two metrics do: decision_regret is a
non-negative loss where lower is better, moa_ndcg is a gain in [0, 1] where higher is better, so
only these two orders make a POSITIVE value mean "population retrieval was better" on both rows.
Both properties are asserted before either difference is formed, because the half-plane labels,
the row statistics and the caption all depend on that shared sign convention.

Every number drawn is computed from that file at draw time; there are no literals in any label,
and the relationships the labels assert are checked in code below so a label cannot outlive the
data.

THE GATE-SELECTED SUBSET, FIXED (2026-08-31)
--------------------------------------------
Until this revision the panel read figures/source_data/fig3a_classA_vs_classB.csv, which holds 480
rows. Those 480 are the leave-drug-out queries INTERSECTED with the information-condition gate's
``recommendation_mode == "DART_recommended"`` verdict, with no column, README line or generator
recording the restriction. The manuscript reports this analysis on all 600 leave-drug-out queries
("Among the 600 partial-observation queries"), precisely so that the paper's headline does not
rest on a subset chosen by the diagnostic that panels d, e and f show does not work. The panel was
stale against its own text, and the identical defect was found and fixed in Figure 2c first; its
docstring records that history.

The fix is the same one: read the authoritative per-query results file, pair on the query key, and
assert n == 600 so a subset cannot silently return. What moved: mechanism recovery goes from 35.0
to 34.2 per cent of queries favouring population and its paired Wilcoxon p from 1.13e-03 to
2.46e-04; response matching goes from median +0.1292 to +0.1288 and from mean +0.2881 to +0.2752.
The direction, the collapse and the reversal are unchanged, which is why the old panel was wrong
rather than misleading. The 600-query values now drawn are the manuscript's.

Panel b carried the same defect and has since had the same fix: it reads per_query_scores.csv and
asserts the balanced 200 / 200 / 200 per-cell-line design, so a and b are drawn from one table
again. What still carries the old subset is the MANUSCRIPT CAPTION entry for this panel, which as
of this writing reads "the same 480 paired queries", 35 per cent favouring population, mean
+0.288, 5 per cent beyond the plotted view and p = 1.1e-03. All five are the gate-selected
values; the drawn panel now says 600, 34 per cent, +0.275, 4 per cent and (in the caption's own
sentence) p = 2.4e-04, and the Results paragraph beside that caption already reports the 600-query
numbers. The caption is not this module's to change. It is named here so the divergence is on the
record rather than found at proof stage.

THE RESTRAINT PASS (2026-08-31)
-------------------------------
Two pieces of text are gone, and neither is preserved anywhere on the panel.

  * The conclusion phrase, "Only the evaluator changes; the advantage disappears". Thirteen panels
    each stating a conclusion is thirteen claims competing for one page; the figure carries
    evidence and the legend carries the argument. fig3_style.title() is deleted and
    fig3_assemble._assert_no_titles caps panel text at PT_ANNOT so it cannot return smaller.
  * The "same rankings" connector, an arrow down the far left of the view carrying no data. What
    it asserted, that the two rows are one query set judged twice, is now carried by the drawing
    itself: the two rows share one x axis, one quantity name, and one n stated once beneath both,
    and the row names are evaluators rather than methods, so nothing suggests two experiments. A
    wordless arrow inside the data field would have been undecodable ink, and a worded one is the
    caption's sentence in a smaller size.

The 0.42 in those sentences returned to the six rows reaches this panel as 0.08 in of extra axes
height (0.84 to 0.92 in). All of it went to the marks: the density ridges grew from 15.0 to 22.0
pt, the interquartile bars and the median dots grew with them, and no text was added.

JUDGEMENT CALLS A READER COULD REASONABLY DISAGREE WITH
-------------------------------------------------------
1. ORIENTATION. The advantage runs along x, and the two evaluators are stacked rows, so the sign
   semantics read left/right rather than up/down. The panel is 3.16 x 0.92 in. On a vertical value
   axis the whole claim, a median shift of +0.129 against 0.000, would print as about 3 pt of
   offset; along x it prints as 11.7 pt. The argument has to be visible in three seconds, so the
   long side of the axes carries the quantity that carries it.
2. NOTHING LINKS THE TWO ROWS EXPLICITLY, now that the connector is gone. A reader who does not
   read the caption could take the rows for two separate experiments. The alternative was ink or
   words that state a construction rather than a measurement, and the shared axis, the single n
   and the evaluator-named rows were judged enough. The caption says it in one clause.
3. THE VIEW STOPS AT +1.42 while Class A runs to +2.82. Opening the view to the maximum would
   compress the region where every median, quartile and tie actually lives into the left third.
   The truncation is stated on the panel (the fraction beyond the view and the true maximum) and
   marked with a chevron at the right end of the response-matching baseline; nothing is silently
   amputated. Nothing is truncated on the left, and mechanism recovery is fully inside the view;
   both facts are asserted below, because "to +2.82" would otherwise be a claim about which side
   is cut that the data could stop supporting.
4. COMMON DENSITY SCALE, NOT EQUAL VIOLIN WIDTHS. Both rows have the same n, so the two densities
   are drawn on one scale: mechanism recovery peaks about twice as high because it is genuinely
   more concentrated. Per-row normalisation to equal maximum width, matplotlib's violinplot
   default, would have made an artefact of that difference.
5. A KERNEL DENSITY CANNOT DRAW AN ATOM. 147 of the 600 mechanism-recovery queries, 24.5 per cent,
   are EXACT ties: the same candidate scores identically under both retrievers. The kernel smooths
   that spike into a finite peak, so the tie fraction is stated in text rather than left to the
   shape. The panel prints it as 24 per cent, the whole-per-cent form every other percentage on it
   takes; 24.5 is the one value on this panel that sits on a rounding boundary, and the exact
   fraction belongs in the caption, which is where the manuscript already reports it.
6. HALF-VIOLINS (density upward from a baseline) rather than symmetric violins. At 0.92 in the
   two-sided form spends half its height mirroring information it already showed, and the baseline
   is needed anyway to carry the interquartile bar, the median dot and the truncation chevron.
7. NO MATHTEXT, ANYWHERE ON THE PANEL. The signs and the two arrows are literal U+2212, "+",
   U+2190 and U+2192 in the deck's body face. Measured in that face (Arial) at PT_ANNOT, a mathtext
   "$-$" prints 6.48 pt wide against 4.32 pt for U+2212, which is 90 per cent of the face's own em
   dash: in a label that names a subtraction, "population - mean", it reads as one. Mathtext also
   resolves through mathtext.fontset, left at dejavusans deck-wide, so each such glyph was DejaVu
   set beside Arial digits. The panel draws no italic statistic symbol, the one thing that would
   earn mathtext, so the rule here is absolute and is asserted on the drawn labels. fig3d and
   fig3e found and fixed the same defect; the alternative the house PT_EQ rule offers, 9.3 pt, is
   above the 7.2 pt cap fig3_assemble._assert_no_titles applies to all panel text.
8. ALL ANNOTATION IS SET IN INK, with size as the only secondary channel. The half-plane washes
   run the full height of the axes, so every label sits on one; META grey on POP_WASH is about
   3.5:1, under any legibility threshold worth naming at 6.5 pt, while INK is about 14:1.

CUT INTO THE CAPTION (this panel is 3.16 x 0.92 in and nothing here is shrunk to fit)
-------------------------------------------------------------------------------------
That the two rows are one set of rankings handed to a second judge, with nothing retrained. The
share of queries favouring MEAN retrieval (20 per cent under response matching, 41 per cent under
mechanism recovery; neither pair sums to 100 because both rows carry exact ties, 7.3 per cent under
response matching and 24.5 per cent under mechanism recovery). The per-cell-line composition, 200
queries each for A549, K562 and MCF7. The paired Wilcoxon p = 2.5e-04 for the mechanism-recovery
distribution, which is significant in the direction that favours MEAN retrieval; that p counts the
600 as independent, and they are not. They are the same 130 held-out drugs in each of three cell
lines, 390 distinct drug-by-cell-line settings drawn unevenly across five seeds (219 settings
appear once, 141 twice, 21 three times, 9 four times, 120 queries per seed), so the queries are
clustered by drug and by setting and the p is anticonservative. The effect it certifies has a
median of exactly zero.

Run standalone: python fig3a.py
"""
from __future__ import annotations

import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.backends.backend_agg import RendererAgg
from matplotlib.colors import to_hex
from scipy.stats import gaussian_kde

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fig3_style import (HAIRLINE, MEAN_WASH, POP_WASH, PT_ANNOT, PT_SMALL,  # noqa: E402
                        REPO, SHARED, TEXT, bare_axes, sign_field, zero_rule)

SRC = os.path.join(REPO, "results", "exp12_partial_observed_retrieval", "per_query_scores.csv")

# The pairing contract. Within leave_drug_out this key is unique per method (asserted), so the two
# retrievers can be joined query by query; heldout_MoA is a function of heldout_drug and is left
# out of the key rather than trusted, and observed_library_fraction is kept in it so that a future
# partial-library leave_drug_out run cannot pair a full-library query against a partial one.
QUERY_KEY = ["split_type", "cell_line", "heldout_drug", "observed_library_fraction", "seed"]
SPLIT = "leave_drug_out"
BASELINE, VARIANT = "mean_cosine", "DART_coverage_worst"
N_QUERIES = 600          # the manuscript's partial-observation set; see the docstring

# The view. XMAX is also the truncation cut: it is where the drawn density of the response-matching
# row stops and where its chevron sits.
XMIN, XMAX = -1.10, 1.42

# The vertical ledger, in POINTS measured down from the top of the axes. Written out because at
# 0.92 in of height every one of these is spent against the others, and a reader of this file
# should be able to add them up: 0.5 + 7.8 (truncation note) sits over the low-density right end
# of row A; RIDGE_MAX below each baseline is the room its density may claim; each summary line is
# about 8.6 pt of PT_ANNOT. The measured checks at the foot of draw_3a are what prove the
# arithmetic against the renderer rather than against this comment.
T_NOTE = 0.5        # the truncation note, right-aligned over the response-matching tail
T_BASE_A = 18.5     # response-matching baseline; its density grows upward from here
T_STAT_A = 21.9     # response-matching summary line (top of the text)
T_BASE_B = 53.5     # mechanism-recovery baseline
T_STAT_B = 56.9     # mechanism-recovery summary line
RIDGE_MAX = 22.0    # points of height given to the LARGER of the two density peaks
# Below the axes, measured downward from it: tick labels, then the two half-plane labels flanking
# zero, then the quantity. fig3_assemble.PADS["a"] owns that depth (0.42 in); the harness is what
# proves this ledger stays inside it.
T_SIGN = 12.8
T_XLAB = 21.0
ROW_LABELS = ("Response\nmatching", "Mechanism\nrecovery")

# Every sign and arrow on this panel is a literal Unicode glyph in the deck's body face, never
# mathtext. Two reasons, both measured in the resolved face (Arial) rather than assumed. A mathtext
# "$-$" prints 6.48 pt wide at PT_ANNOT against 4.32 pt for U+2212, which is 90 per cent of this
# face's em dash (7.20 pt) and reads as one, in a label whose whole job is to name a subtraction;
# fig3d and fig3e found and fixed that same defect and carry the same two measurements. And
# mathtext resolves through mathtext.fontset, which this deck leaves at dejavusans, so every
# mathtext glyph here was DejaVu Sans set beside Arial digits. Only a statistic's italic symbol
# would earn mathtext, and this panel draws none. The absence is asserted at the foot of draw_3a.
MINUS, PLUS = "\u2212", "+"
ARROW_L, ARROW_R = "\u2190", "\u2192"


def _signed(v, nd=3):
    """A signed number whose sign is computed, never typed, and set in the body face."""
    if abs(v) < 0.5 * 10 ** (-nd):
        return f"{0.0:.{nd}f}"
    return (PLUS if v > 0 else MINUS) + f"{abs(v):.{nd}f}"


def class_a_b():
    """The two signed advantages, paired query by query over the 600 leave-drug-out queries.

    Returns ``(a, b)``: ``a`` is the Class-A response-matching advantage (mean_cosine regret minus
    coverage-worst regret) and ``b`` is the Class-B mechanism-recovery advantage (coverage-worst
    MoA-nDCG minus mean_cosine MoA-nDCG), aligned element by element on the same queries.
    """
    d = pd.read_csv(SRC)
    d = d[d["split_type"] == SPLIT]
    assert len(d) > 0, f"{SRC} holds no {SPLIT} rows"
    # The two sign conventions this panel is built on. If either metric ever stopped being read in
    # this direction, both differences below would invert and every label on the panel, including
    # the two half-plane names, would become false without changing shape.
    assert d["decision_regret"].notna().all() and (d["decision_regret"] >= 0).all(), (
        "decision_regret is documented as a non-negative loss (lower is better); the Class-A "
        "subtraction below assumes it.")
    assert d["moa_ndcg"].notna().all() and d["moa_ndcg"].between(0.0, 1.0).all(), (
        "moa_ndcg is documented as a gain in [0, 1] (higher is better); the Class-B subtraction "
        "below assumes it.")

    cols = {}
    for method, name in ((BASELINE, "mean"), (VARIANT, "pop")):
        s = d[d["method"] == method].set_index(QUERY_KEY)[["decision_regret", "moa_ndcg"]]
        assert len(s) > 0, f"no {method} rows in {SPLIT}"
        assert not s.index.has_duplicates, (
            f"{method} rows are not unique on {QUERY_KEY}; the pairing below would compare "
            f"mismatched queries.")
        cols[name] = s.add_prefix(f"{name}_")
    j = pd.concat([cols["mean"], cols["pop"]], axis=1).dropna()
    # The assertion the whole revision exists for: 480 of these are the ones the information-
    # condition gate recommended, and a panel that quietly drew those would be reporting the
    # paper's headline on a subset its own diagnostic chose.
    assert len(j) == N_QUERIES, (
        f"expected {N_QUERIES} paired {SPLIT} queries, got {len(j)}; a gate-selected or otherwise "
        f"filtered subset must not reach this panel.")
    assert (j.index.get_level_values("observed_library_fraction") == 1.0).all(), (
        "the panel draws the full-library regime")
    a = (j["mean_decision_regret"] - j["pop_decision_regret"]).to_numpy(dtype=float)
    b = (j["pop_moa_ndcg"] - j["mean_moa_ndcg"]).to_numpy(dtype=float)
    return a, b


def _clamp_span(patch, x0, x1):
    """Redraw one sign_field half-plane on FINITE coordinates.

    fig3_style.sign_field builds its washes with axvspan(-1e9, 0) and axvspan(0, 1e9). They render
    correctly, being clipped to the axes, but their reported window extent is about 1e11 px wide,
    which any layout audit that measures artist extents reads as ink outside the panel. The patch
    is in the x-data / y-axes blended transform axvspan uses, so clamping it to the view changes
    nothing that is drawn. Called only after the limits are fixed.
    """
    patch.set_bounds(x0, 0.0, x1 - x0, 1.0)


def draw_3a(ax):
    """Same 600 paired queries, two evaluators, one signed advantage."""
    a, b = class_a_b()
    n = a.size

    med_a, med_b = float(np.median(a)), float(np.median(b))
    mean_a, mean_b = float(a.mean()), float(b.mean())
    pos_a, pos_b = float((a > 0).mean()), float((b > 0).mean())
    tie_b = float((b == 0).mean())
    # The panel's claim: the same advantage, judged by mechanism recovery, is centred on zero and
    # favours population retrieval far less often. If either of these ever stopped holding, the
    # labels below would still be computed but the panel would no longer be this figure's reversal.
    assert med_a > med_b, f"response matching no longer leads: {med_a} vs {med_b}"
    assert pos_a > pos_b, f"population is no longer favoured less often: {pos_a} vs {pos_b}"
    assert abs(med_b) < 5e-4, f"mechanism-recovery median is no longer 0.000: {med_b}"
    assert tie_b > 0, "the exact-tie statement needs exact ties"

    # Only the response-matching row leaves the view, and only on the right. The truncation note
    # says "beyond view, max <max>", which is a claim about WHICH side is cut.
    assert a.max() > XMAX > b.max(), "the truncation note assumes only row A exceeds the view"
    assert min(a.min(), b.min()) > XMIN, "nothing may leave the view on the left unannounced"
    beyond = float((a > XMAX).mean())
    assert beyond > 0, "the truncation note needs something beyond the view"

    fig = ax.get_figure()
    h_pt = ax.get_position().height * fig.get_figheight() * 72.0
    w_in = ax.get_position().width * fig.get_figwidth()

    def yat(t):
        """Axes-fraction y for a ledger position given in points below the axes top."""
        return 1.0 - t / h_pt

    def ybelow(t):
        """Axes-fraction y for a ledger position given in points BELOW the axes bottom."""
        return -t / h_pt

    def xfrac(x):
        return (x - XMIN) / (XMAX - XMIN)

    ax.set_xlim(XMIN, XMAX)
    ax.set_ylim(0.0, 1.0)
    ax.set_autoscale_on(False)
    # Before the ticks are configured, not after: bare_axes ends in a tick_params call that resets
    # label size and tick length on BOTH axes, so calling it later silently undoes the row labels'
    # size and puts the suppressed y ticks back.
    bare_axes(ax, keep=("bottom",))

    # ---------------------------------------------------------------- sign, not object
    # Blue and orange are half-planes here. The distributions themselves are grey, because a
    # signed difference is not a method.
    lo, hi = sign_field(ax, vertical=True, at=0.0, pop_side="right", zorder=0)
    assert to_hex(lo.get_facecolor()) == MEAN_WASH.lower(), "left wash is not the mean wash"
    assert to_hex(hi.get_facecolor()) == POP_WASH.lower(), "right wash is not the population wash"
    _clamp_span(lo, XMIN, 0.0)
    _clamp_span(hi, 0.0, XMAX)
    zero_rule(ax, at=0.0, vertical=True, zorder=2)

    # ---------------------------------------------------------------- the two densities
    kdes = [gaussian_kde(a), gaussian_kde(b)]
    grids = [np.linspace(max(XMIN, v.min()), min(XMAX, v.max()), 512) for v in (a, b)]
    dens = [k(g) for k, g in zip(kdes, grids)]
    peak = max(float(d.max()) for d in dens)          # ONE scale for both rows: same n, same units

    base_t = (T_BASE_A, T_BASE_B)
    for v, g, d, tb in zip((a, b), grids, dens, base_t):
        y0 = yat(tb)
        y1 = y0 + (d / peak) * (RIDGE_MAX / h_pt)
        ax.plot([g[0], g[-1]], [y0, y0], color=HAIRLINE, lw=0.6, zorder=2, solid_capstyle="butt")
        ax.fill_between(g, y0, y1, color=SHARED, alpha=0.50, lw=0, zorder=3)
        ax.plot(g, y1, color=SHARED, lw=0.7, zorder=4)
        q1, q3 = np.percentile(v, [25, 75])
        ax.hlines(y0, q1, q3, color=TEXT, lw=2.4, zorder=5, capstyle="butt")
        ax.plot(np.median(v), y0, "o", ms=3.8, mfc="white", mec=TEXT, mew=0.9, zorder=6,
                clip_on=False)
    # The response-matching row continues past the view; say so in ink as well as in words.
    ax.plot(XMAX, yat(T_BASE_A), marker=">", ms=3.2, color=SHARED, mec="none", zorder=5,
            clip_on=False)

    # ---------------------------------------------------------------- the two evaluators
    ax.set_yticks([yat(T_BASE_A), yat(T_BASE_B)])
    ax.set_yticklabels(ROW_LABELS, fontsize=PT_ANNOT, linespacing=1.15)
    ax.tick_params(axis="y", length=0, pad=2)
    # Sit each row name ON TOP of its baseline rather than centred across it, so it is level with
    # the density it names and cannot be read as the opening words of the summary line that starts
    # just inside the axes at the same height.
    for lab in ax.get_yticklabels():
        lab.set_va("bottom")

    # ---------------------------------------------------------------- words
    # The half-plane key sits UNDER the axis, flanking zero, so each phrase is directly under the
    # wash it names and the axes height is left to the distributions.
    ax.text(xfrac(0.0) - 0.022, ybelow(T_SIGN), f"{ARROW_L} mean better", transform=ax.transAxes,
            ha="right", va="top", fontsize=PT_SMALL, color=TEXT)
    ax.text(xfrac(0.0) + 0.022, ybelow(T_SIGN), f"population better {ARROW_R}",
            transform=ax.transAxes, ha="left", va="top", fontsize=PT_SMALL, color=TEXT)
    # "of this row": only response matching is cut, and 4 per cent is 4 per cent OF IT. Read as a
    # panel-wide fraction the same number would be false, and the assertion above is what makes
    # "this row" the true one.
    note = ax.text(1.0, yat(T_NOTE),
                   f"{beyond:.0%} of this row beyond view, max {_signed(a.max(), 2)}",
                   transform=ax.transAxes, ha="right", va="top", fontsize=PT_SMALL, color=TEXT)
    # Lead with the MEDIAN on both rows, in identical form, because the panel's whole claim is the
    # comparison of these two lines and a reader can only compare them at a glance if they are
    # built the same way; the denominator both percentages take is the n stated under both rows.
    # The mean is secondary because on both rows it differs from the median for the same
    # uninteresting reason, a tail.
    stat_al = ax.text(0.0, yat(T_STAT_A),
                      f"median {_signed(med_a)}, {pos_a:.0%} favour population",
                      transform=ax.transAxes, ha="left", va="top", fontsize=PT_ANNOT, color=TEXT)
    stat_ar = ax.text(1.0, yat(T_STAT_A), f"mean {_signed(mean_a)}", transform=ax.transAxes,
                      ha="right", va="top", fontsize=PT_SMALL, color=TEXT)
    stat_bl = ax.text(0.0, yat(T_STAT_B),
                      f"median {_signed(med_b)}, {pos_b:.0%} favour population",
                      transform=ax.transAxes, ha="left", va="top", fontsize=PT_ANNOT, color=TEXT)
    stat_br = ax.text(1.0, yat(T_STAT_B),
                      f"mean {_signed(mean_b)}, {tie_b:.0%} exact ties", transform=ax.transAxes,
                      ha="right", va="top", fontsize=PT_SMALL, color=TEXT)

    ax.set_xticks([-1.0, -0.5, 0.0, 0.5, 1.0])
    ax.set_xticklabels([f"{MINUS}1.0", f"{MINUS}0.5", "0", f"{PLUS}0.5", f"{PLUS}1.0"])
    ax.tick_params(axis="x", pad=1.5)
    # Drawn rather than set_xlabel: the half-plane key already occupies the strip matplotlib would
    # measure the label pad from, and this row's depth is spent to 0.1 in.
    ax.text(0.5, ybelow(T_XLAB), f"population {MINUS} mean advantage, n = {n} paired queries",
            transform=ax.transAxes, ha="center", va="top", fontsize=PT_ANNOT, color=TEXT)

    # ---------------------------------------------------------------- glyphs, asserted
    # The rule the MINUS/PLUS constants exist for, enforced on what was actually drawn rather than
    # on the source: a mathtext minus reads as an em dash at this size and sets Arial digits beside
    # a DejaVu sign, so no label on this panel may carry a "$".
    drawn = ([t.get_text() for t in ax.texts]
             + [t.get_text() for t in ax.get_xticklabels() + ax.get_yticklabels()])
    assert not [t for t in drawn if "$" in t], (
        f"mathtext is back on panel a: {[t for t in drawn if '$' in t]}. Use MINUS/PLUS/ARROW_*.")

    # ---------------------------------------------------------------- geometry, asserted
    # Measured, not estimated. Four things have to hold at this size or the panel is lying about
    # its own layout: neither summary line may run into itself, the truncation note must clear the
    # density it sits over, the mechanism-recovery ridge must clear the line above it, and the
    # bottom summary line must stay inside the axes.
    r = RendererAgg(int(fig.get_figwidth() * fig.dpi), int(fig.get_figheight() * fig.dpi), fig.dpi)

    def _pt_h(artist):
        """Height of a drawn label, in points."""
        return artist.get_window_extent(renderer=r).height / fig.dpi * 72.0

    for left, right, row in ((stat_al, stat_ar, "A"), (stat_bl, stat_br, "B")):
        gap = (right.get_window_extent(renderer=r).x0
               - left.get_window_extent(renderer=r).x1) / fig.dpi
        assert gap > 0.02, (f"row {row} summary line overruns itself by "
                            f"{-gap:.3f} in at {w_in:.2f} in")

    def _data_span(bbox):
        """The x range a drawn label occupies, in data units on this axes."""
        x_ax = ax.get_position().x0 * fig.get_figwidth()
        return [XMIN + (XMAX - XMIN) * (px / fig.dpi - x_ax) / w_in for px in (bbox.x0, bbox.x1)]

    def _ridge_top_t(i, span):
        """Ledger position (points below the axes top) of row i's density over an x range."""
        d = dens[i][(grids[i] >= span[0]) & (grids[i] <= span[1])]
        h = 0.0 if d.size == 0 else RIDGE_MAX * float(d.max()) / peak
        return base_t[i] - h

    clear = _ridge_top_t(0, _data_span(note.get_window_extent(renderer=r))) - (T_NOTE + _pt_h(note))
    assert clear > 0.5, f"truncation note sits {clear:.2f} pt into the density it annotates"
    clear = _ridge_top_t(1, _data_span(stat_al.get_window_extent(renderer=r))) - (
        T_STAT_A + _pt_h(stat_al))
    assert clear > 0.5, f"the mechanism-recovery ridge reaches {clear:.2f} pt into the line above"
    slack = h_pt - (T_STAT_B + _pt_h(stat_bl))
    assert slack > 0.5, f"the mechanism-recovery summary line overruns the axes by {-slack:.2f} pt"


if __name__ == "__main__":
    from figstyle import apply_style
    from fig3_style import PT_TICK, PT_TITLE

    apply_style(sizes=(PT_TITLE, PT_ANNOT, PT_TICK))
    fig = plt.figure(figsize=(4.00, 1.60))
    # The printed rect: 3.16 x 0.92 in of axes, with fig3_assemble's pads around it.
    fig.add_axes([0.74 / 4.00, 0.42 / 1.60, 3.16 / 4.00, 0.92 / 1.60])
    draw_3a(fig.axes[0])
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "3a.png")
    fig.savefig(out, dpi=400)
    print(f"wrote {out}")
