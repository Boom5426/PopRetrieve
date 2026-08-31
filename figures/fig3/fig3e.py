"""Figure 3 panel e: the gate's own reliability axis runs opposite to true response divergence.

WHAT THIS PANEL CLAIMS
----------------------
The pre-specified information-condition gate scores each query on a composite
``structure_reliability_score``, and ``src/experiments/exp16_17_verdict.py`` states the design
assumption in one line: "structure_reliability should rise with divergence; if it falls, the gate
is mis-wired on its reliability axis." It falls. Over all 765 stratified queries the rank
association between the diagnostic and the true response divergence it is meant to track is
Spearman rho = -0.21 (p = 3.8e-09), and the binned conditional medians drop from about 0.57 at the
low-divergence end to about 0.46 at the high-divergence end. A diagnostic anti-correlated with the
quantity it exists to detect cannot be a valid trust signal, which is why panels d and f find no
gain concentration and no verdict separation: this panel is the mechanism for both.

That association is a level difference between the sparse low-divergence tail and the dense bulk
rather than a gradient inside the bulk. Judgement call 3 gives the numbers; the distinction makes
the gate look worse, not better, so the panel states the pooled number the title paraphrases and
the docstring carries the anatomy.

The panel supports the figure's skeleton rather than competing with it. None of the four headline
numbers (+0.129, 0.000, +0.276, +0.097) appears here; this is a diagnosis of the gate that was
supposed to tell a user when population-level retrieval is worth it.

SOURCE
------
results/exp16_gate_diagnosis/_merged_query_divergence.csv, columns
``structure_reliability_score`` and ``true_divergence``, one row per query key
(split_type, cell_line, heldout_drug, observed_library_fraction, seed), n = 765.
figures/source_data/fig3ef_gate_divergence.csv is a hand-built column view of the same file and is
deliberately NOT read here, so the panel cannot drift from the analysis output.
Every number drawn is computed at draw time; the label sign, the direction of the binned medians
and the row count are asserted, so the wording cannot outlive the data.

COLOUR (and the error this fixes)
---------------------------------
The gate is not a retrieval method and is neither family, so it takes no side of the blue/orange
sign vocabulary. The previous version of this panel drew the cloud and its fit in COMP_SOFT, the
deck's colour for mean-signature retrieval, which said the gate was the mean method. Everything
here is SHARED grey. Nothing on this panel is a signed difference either, so there is no
``sign_field``: both axes are levels, not advantages.

JUDGEMENT CALLS A READER COULD REASONABLY DISAGREE WITH
-------------------------------------------------------
1. BINNED MEDIANS, NOT A REGRESSION LINE. The claim is a rank association, and a least-squares
   line invites reading an inferential linear model that was never fitted or checked. The binned
   medians estimate the same conditional-centre function without that promise, and they show the
   wiggle a straight line hides.
2. EQUAL-WIDTH BINS, NOT EQUAL-COUNT BINS. true_divergence is strongly left-skewed: 78 per cent of
   queries sit above 1.5 and the whole lower tail is 22 per cent. Equal-count bins would put six
   of ten points inside the rightmost 15 per cent of a 1.6 in axis and nine of ten inside the
   rightmost 30 per cent, unreadable at this size, and would sample the conditional median almost
   nowhere else. Equal-width bins sample it evenly across the drawn range, at the cost of unequal
   precision: bin counts run from 7 (around divergence 0.9) to 308 (the top bin). The cloud behind
   the points shows that imbalance directly, and the caption carries the counts. A reader who
   prefers equal precision should read the quantile-binned version, where the ten medians fall
   from 0.548 to 0.460 and the decline is concentrated below divergence 1.55, with the dense bulk
   above it roughly flat; the global rho is the same statistic either way, and it is the statistic
   quoted.
3. WHERE THE ASSOCIATION LIVES. Reported here because it is the first thing an adversarial
   reader will test, and because quoting a pooled number while a subset says something else is the
   error this paper exists to criticise. The pooled rho is carried by the contrast between the
   sparse low-divergence tail and the dense bulk, not by a gradient inside either: above divergence
   1.5 (598 of the 765 queries) rho = +0.02, p = 0.58; at or below it (167 queries) rho = -0.15,
   p = 0.053. So what the panel actually shows is that the diagnostic sits systematically LOWER on
   the high-divergence bulk than on the sparse low-divergence tail, and carries no gradient at all
   inside the range where nearly every query lands. The title claims only the end-to-end fall,
   which the pooled statistic and the drawn medians both support, and the flat right-hand end is
   drawn rather than hidden: the top two medians are level.
4. HETEROGENEITY BY SPLIT. The sign is stable across cell lines (A549 -0.29, K562 -0.25,
   MCF7 -0.37, each p < 1e-4) and across the two large split types (leave_drug_out -0.25,
   leave_MoA_out -0.26), but it REVERSES on partial_library (n = 45, rho = +0.34, p = 0.02). The
   panel plots the pooled gate because the gate is specified once for all queries, and cell line
   is a shape and never a hue in this figure, so no stratification is drawn. The reversal belongs
   in the caption if a reader challenges the pooled number.
5. EACH POINT SITS AT ITS BIN'S MEDIAN x, not at the bin centre, so no marker is drawn where the
   data are not.
6. THE INTERVAL IS THE BIN'S INTERQUARTILE RANGE, a spread, not a confidence interval. It says how
   wide the diagnostic's distribution is at that divergence, which is the honest counterweight to
   a summary line: the bins overlap heavily and the shift is a shift of a broad distribution.
7. THE MEDIANS ARE CONNECTED. A connector at this panel size keeps ten dots from reading as a
   second cloud. It is a path through drawn points, not a fit, and it is drawn thin and behind the
   markers for that reason.
8. THE DECLINE IS NOT MONOTONE and the panel does not pretend it is: counting bins from the low
   end, the median ticks up at bins 2, 5, 7 and 10. The title says the axis falls end to end,
   which is what is drawn and asserted.
9. THE GATE'S 0.40 DECISION THRESHOLD IS NOT DRAWN. It would need a label this panel has no room
   for, and the gate's verdict is panels d and f. What is at issue here is the axis, not the cut.
10. NOT SHOWN, because it is a component-level explanation rather than the claim: the negative sign
   comes from the bootstrap rank-stability term (weight 0.40, rho = -0.42 against divergence), not
   from the energy-disagreement term (weight 0.35, rho = +0.35), so it is not an artifact of the
   retrieval circularity that analysis/audit/audit_circularity.py tested for and did not confirm.

Run standalone: python fig3e.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fig3_style import (LW_HAIR, MS_DOT, PT_ANNOT, REPO, SHARED,  # noqa: E402
                        TEXT, bare_axes, title)

SRC = os.path.join(REPO, "results", "exp16_gate_diagnosis", "_merged_query_divergence.csv")

# The title's "assumed to rise" is not a property of the data; it is the design assumption the
# verdict script states in one line. Pinned here so the title cannot outlive its source either.
VERDICT_SRC = os.path.join(REPO, "src", "experiments", "exp16_17_verdict.py")
DESIGN_ASSUMPTION = ("structure_reliability should rise with divergence; if it falls, the gate "
                     "is mis-wired on its reliability axis.")

# One row per query. The merged file is already unique on this key; the de-duplication is a
# guarantee, not a repair, and it is asserted below rather than trusted.
QUERY_KEY = ["split_type", "cell_line", "heldout_drug", "observed_library_fraction", "seed"]

N_QUERIES = 765      # the count this figure's README and the Fig. 3 caption both quote
N_BINS = 10          # equal-width bins of true_divergence; see judgement call 2
MIN_PER_BIN = 5      # below this a median is not worth drawing, so the panel refuses to draw


def _load():
    """Return the one-row-per-query view of the gate diagnosis table."""
    raw = pd.read_csv(SRC)
    kept = raw.dropna(subset=["structure_reliability_score", "true_divergence"])
    assert len(kept) == len(raw), (
        f"{SRC} was expected to score every query on both axes; {len(raw) - len(kept)} of "
        f"{len(raw)} rows are missing structure_reliability_score or true_divergence. Decide what "
        f"a missing score means before this panel summarises the rest.")
    u = kept.drop_duplicates(subset=QUERY_KEY)
    assert len(u) == len(kept), (
        f"{SRC} was expected to hold one row per query key; "
        f"{len(kept)} rows collapsed to {len(u)}.")
    assert len(u) == N_QUERIES, (
        f"panel e is drawn and captioned for n = {N_QUERIES} queries, found {len(u)}. "
        f"Update the caption and this constant together, or the panel is lying about its n.")
    return u


def _assert_design_assumption():
    """Pin the title's "assumed to rise" to the line of code that states it.

    The panel's phrase asserts what the gate was DESIGNED to do, which no column of the data can
    confirm. If that sentence leaves the verdict script, the phrase has lost its source and has to
    change with it, so the panel refuses to draw rather than quoting a design that is gone.
    """
    with open(VERDICT_SRC, encoding="utf-8") as fh:
        flat = " ".join(fh.read().replace("#", " ").split())
    assert DESIGN_ASSUMPTION in flat, (
        f"panel e's title says the gate's reliability axis was ASSUMED to rise, on the authority "
        f"of one sentence in {VERDICT_SRC}, which no longer states it. Re-source the title or "
        f"rewrite it.")


def _binned_medians(x, y):
    """Conditional median and interquartile range of ``y`` in N_BINS equal-width bins of ``x``.

    Returns (x at the bin median, y median, y first quartile, y third quartile, count).
    """
    edges = np.linspace(x.min(), x.max(), N_BINS + 1)
    which = np.clip(np.digitize(x, edges[1:-1]), 0, N_BINS - 1)
    xm, ym, lo, hi, n = [], [], [], [], []
    for b in range(N_BINS):
        m = which == b
        assert m.sum() >= MIN_PER_BIN, (
            f"bin {b} of true_divergence holds {int(m.sum())} queries, under the {MIN_PER_BIN} "
            f"this panel will summarise; re-choose N_BINS rather than drawing the median anyway.")
        xm.append(np.median(x[m]))
        ym.append(np.median(y[m]))
        q1, q3 = np.percentile(y[m], [25, 75])
        lo.append(q1)
        hi.append(q3)
        n.append(int(m.sum()))
    return (np.array(xm), np.array(ym), np.array(lo), np.array(hi), np.array(n))


def draw_3e(ax):
    """The gate's structure-reliability axis against the divergence it is meant to track."""
    _assert_design_assumption()
    u = _load()
    x = u["true_divergence"].to_numpy(dtype=float)
    y = u["structure_reliability_score"].to_numpy(dtype=float)

    rho, pval = spearmanr(x, y)
    # The title says the axis was assumed to rise and falls instead, and the label states the rank
    # correlation. Both are pinned to the data here so neither can outlive it.
    assert rho < 0.0 and pval < 0.05, (
        f"panel e states a significant NEGATIVE rank association, found rho = {rho:+.4f}, "
        f"p = {pval:.3g}. Rewrite the title and the label before redrawing.")

    xm, ym, q1, q3, _ = _binned_medians(x, y)
    assert ym[-1] < ym[0], (
        f"the title claims the binned medians fall across the divergence range, but the top bin "
        f"median {ym[-1]:.4f} is not below the bottom bin median {ym[0]:.4f}.")

    # The raw cloud stays behind everything: it is what makes the unequal bin counts visible.
    ax.scatter(x, y, s=2.2, color=SHARED, alpha=0.20, edgecolors="none", linewidths=0, zorder=1)

    # Interquartile range of the diagnostic inside each divergence bin: a spread, not a CI.
    ax.vlines(xm, q1, q3, color=SHARED, lw=0.9, alpha=0.55, zorder=3)
    # A path through the drawn medians, not a fitted line (judgement call 7).
    ax.plot(xm, ym, color=SHARED, lw=LW_HAIR, alpha=0.55, zorder=3, solid_capstyle="round")
    ax.scatter(xm, ym, s=MS_DOT, color=SHARED, edgecolors="white", linewidths=0.45, zorder=4)

    ax.set_xlim(0.33, 1.88)
    ax.set_ylim(0.265, 0.888)     # head-room above the highest query for the one label
    ax.set_xticks([0.5, 1.0, 1.5])
    ax.set_yticks([0.3, 0.5, 0.7])
    bare_axes(ax)
    # The view carries the label, so the spines stop where the data do.
    ax.spines["left"].set_bounds(y.min(), y.max())
    ax.spines["bottom"].set_bounds(x.min(), x.max())

    ax.set_xlabel("true response divergence", fontsize=PT_ANNOT, labelpad=1.5)
    ax.set_ylabel("gate structure\nreliability", fontsize=PT_ANNOT, labelpad=1.5, linespacing=1.15)

    ax.text(0.995, 0.995, f"Spearman $\\rho = {rho:.2f}$", transform=ax.transAxes,
            fontsize=PT_ANNOT, color=TEXT, ha="right", va="top")
    title(ax, "Assumed to rise, it falls")
    return ax


if __name__ == "__main__":
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    sys.path.insert(0, os.path.join(REPO, "figures"))
    from figstyle import apply_style
    from fig3_style import PT_TICK, PT_TITLE

    apply_style(sizes=(PT_TITLE, PT_ANNOT, PT_TICK))
    fig = plt.figure(figsize=(2.40, 1.24))
    draw_3e(fig.add_axes([0.70 / 2.40, 0.42 / 1.24, 1.60 / 2.40, 0.58 / 1.24]))
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "3e.png")
    fig.savefig(out, dpi=300)
    print(f"wrote {out}")
