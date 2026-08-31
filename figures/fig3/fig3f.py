"""Figure 3 panel f: the gate's decline verdict is inverted on 133 queries and right on 11.

WHAT THIS PANEL CLAIMS
----------------------
The pre-specified information-condition gate issues one verdict per query, and the point of that
verdict is to say when a query is divergent enough for population-level retrieval to be worth its
cost. Split the 765 stratified queries by that verdict and the gate is wrong in the direction it
cares about. The 133 queries it declined with ``mean_or_no_call`` are MORE divergent than the 621
it recommended, not less: medians 1.69 against 1.66, Mann-Whitney two-sided p = 0.001, and a
recommended query is the more divergent of a random pair only 41 per cent of the time (bootstrap
95 per cent interval 0.36 to 0.46, entirely below the 0.5 the gate's premise requires). The 11
queries it declined as ``mean_sufficient`` sit far below both other groups: every one of them is
under the fifth percentile of the recommended queries (1.03) and of the no-call queries (1.48), and
their median is 0.51. On those eleven the gate was right. Both facts are drawn: the 133 as the
lower silhouette, the 11 as their own eleven ticks.

This is supporting evidence for panels d and e, not a fifth headline. None of the figure's four
skeleton numbers (+0.129, 0.000, +0.276, +0.097) appears here. Panel e shows the gate's continuous
reliability axis running opposite to divergence; this panel shows that its thresholded verdict
inherits that inversion on the arm where it is actually used.

THE POOLED READING IS A NULL, AND THAT NULL IS AN ARTEFACT OF THE POOLING
-------------------------------------------------------------------------
Pool the two decline verdicts into one group of 144 and the comparison collapses to Mann-Whitney
p = 0.09 with a common-language effect size of 0.455, interval 0.40 to 0.51, straddling 0.5. That
looks like an absence, and an earlier cut of this panel drew it as one under the phrase "two
verdicts, one distribution". It is not an absence. It is two opposite effects cancelling: 133
queries stochastically ABOVE the recommended group and 11 far BELOW it, in a group whose smaller
arm is 7.6 per cent of the pool and lies entirely under the fifth percentile of both other groups.
A Kolmogorov-Smirnov test
rejects the equal-distribution reading the old phrase asserted (D = 0.154, p = 0.007), and the old
title's own guard, |CLES - 0.5| < 0.05, was never a test of that phrase: two distributions can be
arbitrarily different and still cross at one half.

Manufacturing a null by pooling a mixture is the error this paper exists to criticise, so the
pooled reading is not drawn. It is recomputed and asserted in ``_load`` and ``draw_3f``, and the
assertion fires if pooling ever STOPS moving the answer, because at that point this docstring and
the caption would both need rewriting.

WHICH GROUPS ARE DRAWN, AND WHY THEY MATCH PANEL d
--------------------------------------------------
``recommendation_mode`` takes three values: DART_recommended (621), mean_or_no_call (133) and
mean_sufficient (11). The manuscript's two-way comparison, and the comparison panel d plots, is
621 against 133; panel d states the same three counts and asserts the same decomposition. This
panel now draws the same split, so d and f no longer disagree on what "not recommended" denotes.
The eleven mean-sufficient queries are neither dropped nor merged: they are drawn as eleven ticks
on the lower baseline and labelled, so a reader can see exactly which queries a pooled reading
would fold in. The arithmetic 144 = 133 + 11 is asserted and belongs in the Fig. 3 caption, along
with the pooled statistic; there is no room for either on a 1.60 x 0.58 in axes, and the rule for
this figure is to cut into the caption rather than to shrink type.

SOURCE
------
results/exp16_gate_diagnosis/_merged_query_divergence.csv, columns ``recommendation_mode`` and
``true_divergence``, one row per query key (split_type, cell_line, heldout_drug,
observed_library_fraction, seed), n = 765. figures/source_data/fig3ef_gate_divergence.csv is a
hand-built column view of the same file and is deliberately NOT read here, so the panel cannot
drift from the analysis output. Every number drawn is computed at draw time; the counts, the
direction of the median difference, the effect size, the separation of the eleven and the fact
that pooling changes the answer are all asserted, so the wording and the phrase cannot outlive
the data.

COLOUR
------
Both silhouettes are SHARED grey and identically styled, and the eleven ticks are TEXT ink like
the median ticks, because they are individual observations rather than a summary. Neither group
is a retrieval family: this is the gate's own verdict, which is grey in this figure's vocabulary
wherever it appears. There is no ``sign_field``, because the x axis carries a level (true response
divergence), not a signed population-minus-mean advantage; blue and orange would be a claim about
sign and no sign is plotted. The groups are separated by position and by their direct labels,
never by hue.

JUDGEMENT CALLS A READER COULD REASONABLY DISAGREE WITH
-------------------------------------------------------
1. THE ELEVEN ARE DRAWN AS RAW POINTS, NOT AS A THIRD DENSITY. Eleven observations do not support
   a kernel estimate at any bandwidth this panel could justify, and a third row does not fit in
   0.58 in without two-line labels colliding. Ticks show every one of the eleven at its own value,
   which is more information than a density would have carried.
2. THE DRAWN TEST EXCLUDES THE ELEVEN. It is the manuscript's pre-specified two-way comparison and
   the one panel d plots, so this is not a subset chosen after seeing the answer. The excluded
   queries are nonetheless on the panel, and the pooled statistic is asserted in code and stated
   in the caption, which is the disclosure the exclusion requires.
3. MIRRORED KERNEL DENSITIES RATHER THAN BOXES. A box at this size is five summary statistics per
   group; the shapes plus an interquartile bar and a median tick on each baseline carry the same
   information and let the reader see how far the two silhouettes overlap.
4. ONE ABSOLUTE BANDWIDTH FOR BOTH SILHOUETTES, Silverman's rule on all 765 queries, rather than
   each group's own rule. Per-group rules differ by (621/133) ** 0.2 = 1.36, so the smaller group
   would be drawn smoother and part of any apparent shape difference would be the estimator. The
   medians, the interquartile bars and the test, which carry the claim, do not depend on it.
5. EACH DENSITY IS SCALED TO ITS OWN MAXIMUM, so the two silhouettes are comparable in shape and
   NOT in area. The n is stated in words on each row instead.
6. THE WORD "inverted" RATHER THAN "no better than chance". The effect is small in divergence
   units, 0.029 of median, but its direction is the whole point: the interval on the effect size
   excludes 0.5 from below, so the ordering the gate delivers is the reverse of the one it
   promises, not merely absent. The p is printed and no significance star is drawn.
7. THE WORD "Right" FOR THE ELEVEN. On this panel's own axis the gate declined eleven queries that
   all sit below the fifth percentile of both other groups, which is what its premise says it
   should do. They are not the eleven lowest queries in the study: six recommended queries also
   fall below 0.66, and the panel draws that overlap rather than hiding it. Whether the eleven
   also lost nothing in outcome is panel d's measurement, not this one's; panel d reports their
   median regret reduction as exactly 0.000.
8. NOT DRAWN: the gate's 0.40 decision threshold and its reliability axis. Those are panel e.
   What is at issue here is the verdict, not the axis, and one panel should carry one of them.
9. MIRRORED HALVES, ON A FIGURE WHOSE VOCABULARY USES HALF-PLANES FOR SIGN. Up and down here are
   two groups, not two signs. Three things hold them apart: there is no wash behind either half,
   both halves are the same grey, and the x axis carries a level rather than a signed advantage,
   so there is no zero for a half-plane to be defined against.

Run standalone: python fig3f.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd
from scipy.stats import gaussian_kde, mannwhitneyu

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fig3_style import (FAINT, LW_HAIR, PT_ANNOT, PT_SMALL, REPO,  # noqa: E402
                        SHARED, TEXT, bare_axes, title)

SRC = os.path.join(REPO, "results", "exp16_gate_diagnosis", "_merged_query_divergence.csv")

# One row per query. The merged file is already unique on this key; the de-duplication is a
# guarantee, not a repair, and it is asserted below rather than trusted.
QUERY_KEY = ["split_type", "cell_line", "heldout_drug", "observed_library_fraction", "seed"]

N_QUERIES = 765                     # the count this figure's README and the Fig. 3 caption quote
RECOMMENDED = "DART_recommended"    # the gate's positive verdict
NO_CALL = "mean_or_no_call"         # the manuscript's "not recommended" arm; panel d plots it too
SUFFICIENT = "mean_sufficient"      # the third verdict: also a decline, drawn as eleven ticks
N_RECOMMENDED = 621
N_NO_CALL = 133
N_SUFFICIENT = 11
N_DECLINED = N_NO_CALL + N_SUFFICIENT   # every non-recommended verdict, the caption's 144

# Panel geometry, in units where one unit is the height of a full-scale density.
BAND = 0.30      # half-height of the data-free middle strip: the statistic, the eleven, the label
VH = 0.34        # drawn height of each density at its own maximum
ROW_Y = BAND + VH / 2.0   # centre of a group's row: its name outside, its n and median inside
TICK_IN = 0.08   # how close a median tick comes to the horizontal centre line
TICK_OUT = 0.50  # how far past the centre line the median tick runs, i.e. across its baseline
RUG_H = 0.11     # height of one mean-sufficient tick, standing on the lower baseline
STAT_Y = 0.12    # the test statistic, in the upper part of the data-free strip
RUG_LABEL_Y = -0.185    # the eleven ticks' direct label, level with them
LABEL_X = 0.015         # axes fraction: where a row's own text starts
RUG_LABEL_X = 0.235     # axes fraction: clear of the rightmost tick, asserted in draw_3f
HEAD = 1.10      # head-room factor, so the tallest point of a density clears the frame
GRID_N = 400


def _load():
    """Return the one-row-per-query view, split into (recommended, no_call, sufficient) arrays."""
    raw = pd.read_csv(SRC)
    u = raw.dropna(subset=["recommendation_mode", "true_divergence"])
    u = u.drop_duplicates(subset=QUERY_KEY)
    assert len(u) == len(raw), (
        f"{SRC} was expected to hold one complete row per query key; "
        f"{len(raw)} rows collapsed to {len(u)}.")
    assert len(u) == N_QUERIES, (
        f"panel f is drawn and captioned for n = {N_QUERIES} queries, found {len(u)}. "
        f"Update the caption and this constant together, or the panel is lying about its n.")

    modes = set(u["recommendation_mode"].unique())
    assert modes == {RECOMMENDED, NO_CALL, SUFFICIENT}, (
        f"panel f draws one group per gate verdict and knows of "
        f"{sorted([RECOMMENDED, NO_CALL, SUFFICIENT])}; the file now carries {sorted(modes)}. "
        f"A new verdict must be placed deliberately, not folded into an existing group.")

    out = {m: u.loc[u["recommendation_mode"] == m, "true_divergence"].to_numpy(float)
           for m in (RECOMMENDED, NO_CALL, SUFFICIENT)}
    counts = {m: len(v) for m, v in out.items()}
    expected = {RECOMMENDED: N_RECOMMENDED, NO_CALL: N_NO_CALL, SUFFICIENT: N_SUFFICIENT}
    assert counts == expected, (
        f"panel f, panel d and the Fig. 3 caption all quote {expected}; this file now has "
        f"{counts}. Re-check both panels and the caption before redrawing.")
    assert sum(counts.values()) == N_QUERIES
    assert counts[NO_CALL] + counts[SUFFICIENT] == N_DECLINED, (
        f"the caption states that {N_DECLINED} queries were not recommended and that this splits "
        f"as {N_NO_CALL} plus {N_SUFFICIENT}; the file now splits it "
        f"{counts[NO_CALL]} plus {counts[SUFFICIENT]}.")
    return out[RECOMMENDED], out[NO_CALL], out[SUFFICIENT]


def _cles(a, b):
    """P(a random draw from ``a`` exceeds one from ``b``), ties split, with the two-sided p.

    The gate's premise needs this above 0.5 for recommended against declined queries.
    """
    u_stat, pval = mannwhitneyu(a, b, alternative="two-sided")
    return float(u_stat) / (len(a) * len(b)), float(pval)


def _pooled_bandwidth(values):
    """Silverman's rule on all 765 queries: one absolute kernel width for both silhouettes.

    Returned in data units, so each group is handed ``h / sd`` as gaussian_kde's ``bw_method``
    and both silhouettes are smoothed identically (judgement call 4).
    """
    sd = float(np.std(values, ddof=1))
    q1, q3 = np.percentile(values, [25, 75])
    spread = min(sd, (q3 - q1) / 1.349)
    assert spread > 0.0, "true_divergence has no spread; a density estimate would be meaningless."
    return 0.9 * spread * len(values) ** (-0.2)


def _half(ax, values, sign, h):
    """Draw one group: a density silhouette, its interquartile bar, its median tick, its label.

    The silhouette is evaluated only over the group's OWN observed range, so no density is drawn
    where that group has no query; the flat stretch each curve runs along its baseline is a real
    near-zero density, not a rule added for decoration.
    """
    grid = np.linspace(values.min(), values.max(), GRID_N)
    density = gaussian_kde(values, bw_method=h / float(np.std(values, ddof=1)))(grid)
    density = density / density.max()

    base = sign * BAND
    top = sign * (BAND + VH * density)
    ax.fill_between(grid, base, top, color=FAINT, lw=0, zorder=1)
    ax.plot(grid, top, color=SHARED, lw=LW_HAIR, zorder=2, solid_capstyle="round")

    q1, med, q3 = (float(v) for v in np.percentile(values, [25, 50, 75]))
    ax.plot([q1, q3], [base, base], color=SHARED, lw=1.5, zorder=3, solid_capstyle="butt")
    ax.plot([med, med], [sign * TICK_IN, sign * TICK_OUT], color=TEXT, lw=1.0, zorder=4,
            solid_capstyle="butt")

    # The n and the median sit ON the group's own row, level with its name in the margin, in the
    # left half of the row where this group's density is flat against its baseline.
    ax.text(LABEL_X, sign * ROW_Y, f"n = {len(values)}, median {med:.2f}",
            transform=ax.get_yaxis_transform(), ha="left", va="center",
            fontsize=PT_SMALL, color=TEXT)
    return med


def draw_3f(ax):
    """True response divergence by gate verdict: 621 recommended, 133 no-call, 11 sufficient."""
    rec, no_call, suff = _load()

    cles, pval = _cles(rec, no_call)
    med_rec, med_nc, med_suf = (float(np.median(v)) for v in (rec, no_call, suff))

    # The phrase says the drawn comparison is INVERTED, so both its direction and its strength are
    # pinned here: the declined arm is the more divergent one, and the effect size is on the wrong
    # side of the half the gate's premise needs.
    assert med_rec < med_nc, (
        f"the panel states that the queries the gate declined for no call are the MORE divergent "
        f"ones, but the recommended median {med_rec:.4f} is not below {med_nc:.4f}. "
        f"Rewrite the docstring and the phrase before redrawing.")
    assert cles < 0.5 and pval < 0.01, (
        f"the panel calls the {N_NO_CALL}-query comparison inverted, which needs an effect size "
        f"below 0.5 at a p this panel is willing to print; found CLES = {cles:.4f}, "
        f"p = {pval:.3g}.")
    assert 0.0005 <= pval < 0.995, (
        f"p is printed to three decimals and p = {pval:.3g} would print uninformatively.")

    # The eleven are drawn apart from the lower silhouette, so the panel asserts that they really
    # are a separate low cluster rather than a slice of the same population.
    assert suff.max() < np.percentile(rec, 5) and suff.max() < np.percentile(no_call, 5), (
        f"the panel draws the {N_SUFFICIENT} mean-sufficient queries as a separate low cluster "
        f"and calls the gate right about them; their maximum {suff.max():.4f} is no longer below "
        f"the fifth percentile of both other groups "
        f"({np.percentile(rec, 5):.4f}, {np.percentile(no_call, 5):.4f}).")
    assert med_suf < med_rec and med_suf < med_nc

    # The pooled reading is the one this panel refuses to draw, so the reason it refuses is a
    # test, not a sentence: pooling has to move the answer, and if it stops moving it the
    # docstring and the Fig. 3 caption are both wrong.
    declined = np.concatenate([no_call, suff])
    cles_pool, p_pool = _cles(rec, declined)
    assert len(declined) == N_DECLINED
    assert cles_pool > cles and p_pool > 0.05 > pval, (
        f"this panel does not draw the pooled {N_DECLINED}-query reading because pooling the "
        f"{N_SUFFICIENT} mean-sufficient queries cancels the effect: CLES {cles:.4f} -> "
        f"{cles_pool:.4f}, p {pval:.3g} -> {p_pool:.3g}. Pooling no longer does that, so the "
        f"docstring's argument and the caption's pooled statistic must be rewritten.")

    pooled = np.concatenate([rec, declined])
    lo, hi = float(pooled.min()), float(pooled.max())
    pad = 0.045 * (hi - lo)
    h = _pooled_bandwidth(pooled)

    drawn_rec = _half(ax, rec, +1, h)
    drawn_nc = _half(ax, no_call, -1, h)
    # The medians tested above and the medians labelled on the panel must be the same two numbers.
    assert abs(drawn_rec - med_rec) < 1e-12 and abs(drawn_nc - med_nc) < 1e-12, (
        f"the drawn medians ({drawn_rec:.6f}, {drawn_nc:.6f}) are not the tested medians "
        f"({med_rec:.6f}, {med_nc:.6f}).")

    # Every mean-sufficient query, one tick each, standing on the lower group's baseline. Raw
    # observations rather than a summary, so they take TEXT ink like the median ticks.
    ax.vlines(suff, -BAND, -BAND + RUG_H, color=TEXT, lw=0.7, zorder=4)

    ax.set_xlim(lo - pad, hi + pad)
    ax.set_ylim(-(BAND + HEAD * VH), BAND + HEAD * VH)

    # The ticks' direct label must start to the RIGHT of the rightmost tick, or it would sit on
    # the observations it names. Checked against the axes actually set, not assumed.
    x0, x1 = ax.get_xlim()
    assert (suff.max() - x0) / (x1 - x0) < RUG_LABEL_X, (
        f"the eleven mean-sufficient ticks now reach axes fraction "
        f"{(suff.max() - x0) / (x1 - x0):.3f}, at or past their own label at {RUG_LABEL_X}.")
    ax.text(RUG_LABEL_X, RUG_LABEL_Y, f"$+$ {len(suff)} {SUFFICIENT.replace('_', ' ')}",
            transform=ax.get_yaxis_transform(), ha="left", va="center",
            fontsize=PT_SMALL, color=TEXT)

    # The test statistic sits in the strip between the two silhouettes, which holds no data ink,
    # and compares exactly the two silhouettes it sits between.
    ax.text(LABEL_X, STAT_Y, f"Mann$-$Whitney $p$ = {pval:.3f}",
            transform=ax.get_yaxis_transform(), ha="left", va="center",
            fontsize=PT_ANNOT, color=TEXT)

    ax.set_xticks([0.5, 1.0, 1.5])
    ax.set_yticks([ROW_Y, -ROW_Y])
    ax.set_yticklabels(["recommended", "mean or\nno call"], linespacing=1.12)
    bare_axes(ax, keep=("bottom",))
    ax.spines["bottom"].set_bounds(lo, hi)
    ax.tick_params(axis="y", length=0, pad=2.0)

    ax.set_xlabel("true response divergence", fontsize=PT_ANNOT, labelpad=1.5)
    # Both halves of the phrase are asserted above: "inverted on 133" by the direction of the
    # medians and an effect size below one half, "right on 11" by those eleven sitting under the
    # fifth percentile of both other groups on the axis the gate exists to track.
    title(ax, f"Inverted on {len(no_call)}, right on {len(suff)}")
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
    draw_3f(fig.add_axes([0.70 / 2.40, 0.42 / 1.24, 1.60 / 2.40, 0.58 / 1.24]))
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "3f.png")
    fig.savefig(out, dpi=300)
    print(f"wrote {out}")
