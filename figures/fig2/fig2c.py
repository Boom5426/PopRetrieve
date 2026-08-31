"""PopRetrieve Figure 2 panel 2c: per-query regret reduction, ECDF over ALL 765 queries.

WHAT THE PANEL CLAIMS
---------------------
On a query-by-query basis, retrieval scored on the retained cell POPULATION reaches a lower
decision regret than retrieval scored on the COLLAPSED mean signature: 72% of queries improve,
21% get worse, 7% tie exactly, median +0.118, paired Wilcoxon p = 1.6e-66. Every one of those
numbers is computed at draw time from the source file, and the relationships the panel states in
words are asserted below so a label cannot outlive the data.

This is a Class-A (objective-aligned) statement about response matching only. `decision_regret` is
the regret of the decision taken from the retrieved candidate under the retrieval objective; the
panel says nothing about whether the retrieved perturbation is biologically preferable, which is
Figure 3's question.

SOURCE
------
results/exp12_partial_observed_retrieval/per_query_scores.csv, paired per query on the SIX-column
key that `src/experiments/exp12_partial_observed_retrieval.py` documents as identifying a query
(split_type, cell_line, heldout_drug, heldout_MoA, observed_library_fraction, seed), as
(mean_cosine decision_regret) minus (DART_coverage_worst decision_regret). `decision_regret` is
defined there as U[library-oracle] minus U[selected] and is therefore non-negative, with lower
better; that is asserted below, because it is what makes a POSITIVE difference mean the
population-level scorer left LESS regret, i.e. that population retrieval was better. A shorter key
mispairs rows (the partial_library queries repeat one drug at three library fractions), and the
experiment records that a short key once put a wrong median into this figure.

Scope note, and the reason this panel reads the raw per-query file: it previously plotted
figures/source_data/fig2c_regret_reduction.csv, which holds only the 621 gate-recommended queries
(annotated "n=621, p=4e-56"). The manuscript caption and Results text both report panel c on ALL
765 partial-observed queries, precisely so the headline is not taken on a gate-selected subset.
The panel now computes the full 765-query set from the authoritative results file and asserts
n == 765 so a subset cannot silently return.

JUDGEMENT CALLS A READER COULD DISAGREE WITH
--------------------------------------------
1. The curve is INK, not POP blue. The plotted quantity is a signed DIFFERENCE between the two
   families, so it belongs to neither; and the two half-plane washes already spend both family
   colours here. A blue curve would fuse with the blue wash on the right and contrast with the
   orange on the left, which would say the curve is a population-level score, which it is not.
   The washes carry the families; the curve carries the data and is the strongest ink in the box.
2. The half-planes are named in family language ("mean retrieval" / "population retrieval") while
   the axis definition line names the two exact scorers ("mean-cosine regret - coverage-worst
   regret"). The panel compares one population-level scorer, not the whole family; panel f is what
   generalises the result across the five. Naming the family in the wash and the scorer on the axis
   keeps the fast read plain and the precise read available in the same 2.63 in.
3. The mean (+0.258) is NOT drawn. At this x scale it lands 0.09 in from the median rule, so two
   central-tendency rules would read as one thick rule, and the reason the mean exceeds the median
   (a long right tail out to +2.82) is already the most conspicuous feature of the ECDF's upper
   arm. The caption carries the mean; the panel shows the tail that explains it.
4. The ECDF is drawn as a true step function over the full data range rather than as an
   interpolated line, and both tails are kept in view (xlim spans the observed min and max). That
   costs horizontal room in the crowded region near zero, and buys an honest picture of how far the
   right tail runs.
5. The ties are labelled at 7% next to the vertical step at the origin rather than left implicit,
   so that "72% better" and "21% worse" are not read as a pair that should sum to 100.
6. "Survives partial observation": 600 of the 765 queries are leave_drug_out, where the library is
   fully observed (observed_library_fraction == 1.0) and only the optimal drug is hidden, which is
   this project's information condition. Only 165 queries have an incomplete library. The panel
   phrase is therefore asserted TWICE: over all 765, and over the 165 with fraction < 1 (median
   +0.087, 68% improved), so it holds under either reading of the phrase.

Run standalone: python fig2c.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fig2_style import (FAINT, LW_HAIR, LW_LINE, MEAN, MEAN_WASH, MS_DOT,  # noqa: E402
                        POP, POP_WASH, PT_ANNOT, PT_SMALL, REPO, SHARED, SUBTLE,
                        TEXT, bare_axes, title, zero_rule)

QUERY_KEY = ["split_type", "cell_line", "heldout_drug", "heldout_MoA",
             "observed_library_fraction", "seed"]
N_QUERIES = 765          # all partial-observed queries; see module docstring
N_INCOMPLETE = 165       # of those, the ones whose library is genuinely incomplete
SRC = "results/exp12_partial_observed_retrieval/per_query_scores.csv"

XLIM = (-1.35, 2.95)     # must contain both tails; asserted against the data in draw_2c
YLIM = (-0.03, 1.05)
WASH_ALPHA = 0.6        # the half-plane tint; see draw_2c


def regret_reduction():
    """Paired per-query regret reduction, mean-cosine minus coverage-worst, all 765 queries.

    Returns a Series indexed by QUERY_KEY, so the observed_library_fraction of every query stays
    attached to its value and the partial-library subset can be checked without a second read.
    """
    d = pd.read_csv(os.path.join(REPO, SRC))
    assert d["decision_regret"].notna().all() and (d["decision_regret"] >= 0).all(), (
        "decision_regret is documented as a non-negative regret (lower is better); if that "
        "changes, the sign of every difference plotted here inverts and both half-plane labels "
        "become false.")
    cols = {}
    for method, name in (("mean_cosine", "mean"), ("DART_coverage_worst", "pop")):
        s = d[d.method == method].set_index(QUERY_KEY)["decision_regret"]
        assert not s.index.has_duplicates, (
            f"{method} rows are not unique on {QUERY_KEY}; the pairing below would compare "
            f"mismatched queries.")
        cols[name] = s
    j = pd.concat([cols["mean"].rename("mean"), cols["pop"].rename("pop")], axis=1).dropna()
    assert len(j) == N_QUERIES, f"expected {N_QUERIES} paired queries, got {len(j)}"
    return j["mean"] - j["pop"]


def draw_2c(ax):
    """ECDF of the Class-A per-query regret reduction over all 765 partial-observed queries."""
    rr_s = regret_reduction()
    rr = rr_s.to_numpy(dtype=float)
    n = rr.size

    med = float(np.median(rr))
    f_up = float((rr > 0).mean())
    f_dn = float((rr < 0).mean())
    f_ti = float((rr == 0).mean())
    p = float(wilcoxon(rr).pvalue)

    # ---- the relationships this panel states in words, asserted so a label cannot outlive them
    assert abs(f_up + f_dn + f_ti - 1.0) < 1e-12, "the three signs must partition the queries"
    pct = {k: f"{v:.0%}" for k, v in (("up", f_up), ("dn", f_dn), ("ti", f_ti))}
    assert sum(int(s.rstrip("%")) for s in pct.values()) == 100, (
        f"the three drawn percentages {pct} do not sum to 100, so the panel would have to "
        f"explain the remainder; re-word before drawing.")
    assert med > 0 and f_up > f_dn and p < 1e-6, (
        f"the panel phrase says the gain survives; median {med:.4f}, up {f_up:.3f}, "
        f"down {f_dn:.3f}, p {p:.2e} do not support it.")
    frac_obs = rr_s.index.get_level_values("observed_library_fraction").to_numpy(dtype=float)
    part = rr[frac_obs < 1.0]
    assert part.size == N_INCOMPLETE, f"expected {N_INCOMPLETE} incomplete-library queries"
    assert (float(np.median(part)) > 0 and float((part > 0).mean()) > 0.5
            and float(wilcoxon(part).pvalue) < 1e-6), (
        "the gain does not hold on the queries whose library is genuinely incomplete, so the "
        "panel phrase must not say it survives partial observation.")
    assert XLIM[0] < rr.min() and rr.max() < XLIM[1], "the x range clips a tail"

    # ---- the two half-planes: zero is the centre of the reading, and each side is named
    # WASH_ALPHA keeps the frozen wash hues but takes them down to a tint that names the
    # half-plane without competing with the curve; at full strength they read as two filled bars.
    ax.axvspan(XLIM[0], 0.0, color=MEAN_WASH, alpha=WASH_ALPHA, lw=0, zorder=0)
    ax.axvspan(0.0, XLIM[1], color=POP_WASH, alpha=WASH_ALPHA, lw=0, zorder=0)
    zero_rule(ax, 0.0, color=SUBTLE, lw=0.8, zorder=3)

    # ---- the ECDF itself, a true step over the full observed range
    xs = np.sort(rr)
    ys = np.arange(1, n + 1) / n
    ax.plot(np.concatenate([[XLIM[0]], xs, [XLIM[1]]]), np.concatenate([[0.0], ys, [1.0]]),
            drawstyle="steps-post", color=TEXT, lw=LW_LINE, zorder=6,
            solid_joinstyle="round", solid_capstyle="butt")

    # ---- the median, as a primary annotation: a rule, the 50% crossing, and a direct label
    ax.plot([med, med], [YLIM[0], 0.5], ls=(0, (1.6, 1.6)), lw=0.8, color=SHARED, zorder=4)
    ax.plot([XLIM[0], med], [0.5, 0.5], ls=(0, (1.6, 1.6)), lw=LW_HAIR, color=FAINT, zorder=4)
    ax.scatter([med], [0.5], s=MS_DOT, color=TEXT, zorder=7, linewidths=0)
    ax.text(med + 0.06, 0.36, f"median +{med:.3f}", fontsize=PT_ANNOT, color=TEXT,
            ha="left", va="center", zorder=7)

    # ---- the ties: the flat step at the origin, named at the MIDDLE of the step it explains,
    # so the leader lands on the riser rather than on the corner where the curve turns
    y_tie = f_dn + f_ti / 2.0
    ax.plot([-0.42, -0.015], [y_tie, y_tie], lw=LW_HAIR, color=SHARED, zorder=4)
    ax.text(-0.46, y_tie, f"{pct['ti']} tied", fontsize=PT_SMALL, color=SUBTLE,
            ha="right", va="center", zorder=7)

    # ---- the two half-plane blocks. The bar is the mark that carries the family colour; every
    # letter stays ink or grey. Each block sits inside the half-plane it names, so position and
    # colour say the same thing twice.
    ax.plot([0.030, 0.115], [0.975, 0.975], transform=ax.transAxes, lw=2.2, color=MEAN,
            solid_capstyle="butt", zorder=5, clip_on=False)
    ax.text(0.030, 0.955, pct["dn"], transform=ax.transAxes, fontsize=PT_ANNOT, color=TEXT,
            fontweight="bold", ha="left", va="top", zorder=7)
    ax.text(0.030, 0.845, "mean retrieval\nbetter", transform=ax.transAxes, fontsize=PT_SMALL,
            color=TEXT, ha="left", va="top", linespacing=1.25, zorder=7)

    ax.plot([0.885, 0.970], [0.845, 0.845], transform=ax.transAxes, lw=2.2, color=POP,
            solid_capstyle="butt", zorder=5, clip_on=False)
    ax.text(0.970, 0.825, pct["up"], transform=ax.transAxes, fontsize=PT_ANNOT, color=TEXT,
            fontweight="bold", ha="right", va="top", zorder=7)
    ax.text(0.970, 0.715, "population retrieval\nbetter", transform=ax.transAxes,
            fontsize=PT_SMALL, color=TEXT, ha="right", va="top", linespacing=1.25, zorder=7)

    ax.text(0.970, 0.030, f"n = {n} queries", transform=ax.transAxes, fontsize=PT_SMALL,
            color=SUBTLE, ha="right", va="bottom", zorder=7)

    # ---- axes
    ax.set_xlim(*XLIM)
    ax.set_ylim(*YLIM)
    ax.set_xticks([-1, 0, 1, 2])
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels(["0", "0.25", "0.50", "0.75", "1.00"])
    ax.set_ylabel("cumulative fraction", fontsize=PT_ANNOT)
    bare_axes(ax)

    # The plain-language reading leads; the definition follows a size down, so two method names
    # never have to share the axis title. Neither line carries a sub/superscript, so neither is
    # printed at 0.7x and both stand at their nominal size.
    ax.text(0.5, -0.19, "Regret reduction vs mean retrieval", transform=ax.transAxes,
            fontsize=PT_ANNOT, color=TEXT, ha="center", va="top")
    ax.text(0.5, -0.30, "mean-cosine regret $-$ coverage-worst regret", transform=ax.transAxes,
            fontsize=PT_SMALL, color=SUBTLE, ha="center", va="top")

    title(ax, "The gain survives partial observation")


if __name__ == "__main__":
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    from figstyle import apply_style
    from fig2_style import PT_TICK, PT_TITLE

    # the real printed box: a half-width column of Figure 2, drawn at 1:1
    apply_style(sizes=(PT_TITLE, PT_ANNOT, PT_TICK))
    BOX_W, BOX_H, PAD_L, PAD_B, AX_W, AX_H = 3.45, 1.84, 0.72, 0.50, 2.63, 1.08
    fig = plt.figure(figsize=(BOX_W, BOX_H))
    ax = fig.add_axes([PAD_L / BOX_W, PAD_B / BOX_H, AX_W / BOX_W, AX_H / BOX_H])
    draw_2c(ax)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "2c.png")
    fig.savefig(out, dpi=300)
    print(f"wrote {out}")
