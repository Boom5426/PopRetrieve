"""PopRetrieve Figure 2 panel a: the Hit@1 ladder, grouped by representation family.

WHAT THIS PANEL CLAIMS
----------------------
One thing, and it is a claim about RETRIEVAL, not about biology: scorers that keep the retained
cell population retrieve the right response population more often than scorers that first collapse
that population into a signature. The claim is carried by a separation, not by a winner. Every
population-level scorer sits above every mean-level scorer on macro-average Hit@1, so the ladder
is sorted by value and grouped by family at the same time and the grouping costs the sort nothing.
That separation is ASSERTED at draw time (`_load`), because it is the whole design: if new data
broke it, the grouping, the family washes and the panel phrase would all start lying quietly.

Everything here is objective-aligned (Class A). Hit@1 rewards correspondence between response
populations, which is the information population-level retrieval uses. Whether that information is
biologically valuable is Figure 3's question and is deliberately absent from this panel.

SOURCE
------
results/exp08_signature_baselines/summary.csv, the only file this module reads. Eight scorers x
seven task x setting cells: controlled x {K562, A549, MCF7}, cross-line x {K562+A549, A549+MCF7,
K562+MCF7}, and Frangieh x {Control+IFNg}. The plotted quantity is the UNWEIGHTED macro-mean of
hit@1 over those seven cells; the cell count is read from the file and asserted to be seven for
every method, and it is interpolated into the x axis label so the label cannot outlive the data.

Every number drawn is computed here. Nothing is typed as a literal, and nothing is read from a
summary table that could drift away from the source.

JUDGEMENT CALLS A READER COULD REASONABLY DISAGREE WITH
-------------------------------------------------------
1.  UNWEIGHTED macro-mean over the seven cells, so a 30-query cell counts as much as a 360-query
    cell. The query-weighted variant is larger (energy 0.887 vs collapsed cosine 0.421) and is
    quoted in the manuscript text. Unweighted is plotted because the seven cells are seven
    experimental conditions rather than seven samples of one population, and weighting would let
    the three 360-query cross-line cells set the headline almost by themselves. Every claim this
    panel STATES survives either weighting: the families still separate (weakest population
    0.595 against strongest mean 0.499), the two collapsed-cosine scorers are still tied, and the
    bracketed pair is still the widest. One thing the panel draws without claiming it does not
    survive: query weighting lifts CMap WTCS (0.499) past PCA-mean (0.482) and swaps the fifth
    and sixth rungs. It is named here rather than hidden under a blanket "nothing changes".
2.  pca_dist is drawn as a POPULATION scorer. It is an energy distance between two point clouds
    that happens to live in a PCA latent, so its input is the retained population. An earlier cut
    coloured it "other", which put a distributional statistic outside the distributional family
    and weakened the very claim the panel exists to make.
3.  cmap_cosine and mean_cosine are IDENTICAL, not merely close: they agree to full precision in
    every numeric column of all seven cells, which this module asserts. The asserted pair is the
    pair the tie marker is drawn beside, read out of the sort rather than typed, so the marker
    cannot come to rest against two rows the assertion never looked at. Their order in the ladder
    is therefore a tie with no data-driven answer, and it is broken deterministically by ascending
    method name (cmap_cosine above mean_cosine). The tie is marked on the panel rather than left
    for the reader to notice two equal bars, and the marker points at panel g, where the agreement
    is measured per query-candidate pair rather than per cell. The panel prints no number for that
    correlation: it is not in this file, and quoting it here would be laundering it.
4.  The two CMap rows are PUBLISHED baselines. That is PROVENANCE, not representation, so it is
    marked with a dagger and never with a colour; see the fig2_style docstring on why a third
    family colour would contradict what panel g measures.
5.  The left-hand family labels read "Population" and "Mean", derived by stripping the "-level"
    suffix from fig2_style.FAMILY_NAME rather than retyped. The full names do not fit: rotated at
    PT_SMALL, "Population-level" sets 0.65 in against a four-row group 0.62 in tall, and the floor
    forbids shrinking it. The unabbreviated names belong in the caption.
6.  The headline bracket compares the best population scorer with the worst mean scorer, which is
    the widest honest pair on the panel. The narrowest pair, the two rows either side of the
    family gap, is visible as a gap the reader can read off the same axis, and the panel phrase
    states the separation that holds for ALL pairs.
7.  The difference is printed from unrounded values, +0.448, not as the difference of the two
    printed three-decimal values, which would read +0.449.

Run standalone: python fig2a.py
"""
from __future__ import annotations

import os
import sys

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Rectangle

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fig2_style import (FAMILY_NAME, HAIRLINE, LW_HAIR, MEAN, MEAN_WASH,  # noqa: E402
                        POP, POP_WASH, PT_ANNOT, PT_SMALL, PT_TICK, PT_TITLE,
                        SCORERS, SHARED, SUBTLE, TEXT, title)

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC = os.path.join(REPO, "results", "exp08_signature_baselines", "summary.csv")

# ------------------------------------------------------------------------------ geometry
# Authored against the composite's own box for panel a: 5.88 x 1.34 in. The tracks deliberately
# do NOT run the full width. x = 1 (the attainable Hit@1 maximum) sits at TRACK_IN inches, and
# everything right of it is the headline block, so the panel reads as bars on the left and the
# claim on the right.
TRACK_IN = 3.55             # inches spanned by Hit@1 = 0 .. 1
AXES_IN = 5.88              # the panel's axes width, from fig2_assemble's ledger
XMAX = AXES_IN / TRACK_IN   # right edge of the axes, in Hit@1 units

def _u(inches: float) -> float:
    """Inches on the printed page -> x-axis (Hit@1) units. Keeps the ledger readable."""
    return inches / TRACK_IN

FAM_GAP = 0.60              # blank rows between the two family blocks
BAR_H, BAR_H_HEAD = 0.46, 0.66
X_LABEL_R = -_u(0.062)      # right edge of the scorer-name column
X_DAGGER = -_u(0.030)       # the published-baseline glyph, on its own fixed column
X_FAMILY = -_u(0.845)       # the rotated family label
X_SWATCH = -_u(0.740)       # the family swatch, a rule the length of the group
X_VALUE_R = 1.0 + _u(0.300)  # right edge of the value column
X_BRACKET = 1.0 + _u(0.500)  # the headline bracket's spine
X_ARM = 1.0 + _u(0.375)     # where the bracket's arms stop, clear of the value column
X_HEAD = 1.0 + _u(0.620)    # left edge of the headline text
LW_HEAD = 0.7               # headline bracket: one notch above LW_HAIR, so the two brackets rank


def _load():
    """Macro-mean Hit@1 per scorer, family-grouped and value-sorted, with the claims asserted."""
    s = pd.read_csv(SRC)
    n = len(s[["task", "setting"]].drop_duplicates())
    assert n == 7, f"the manuscript's design is 7 task x setting cells; summary.csv has {n}"
    assert set(s["method"]) == set(SCORERS), (
        f"summary.csv scorers {sorted(set(s['method']))} do not match fig2_style.SCORERS")
    # The GRID, not merely the row count. A macro-mean over seven rows means nothing unless the
    # seven rows are the same seven cells for every scorer; otherwise the ladder would rank
    # scorers measured on different conditions and no rung would be comparable to any other.
    grid = s.groupby(["method", "task", "setting"]).size()
    assert grid.eq(1).all() and len(grid) == len(SCORERS) * n, (
        f"every method must cover all {n} cells exactly once; the method x cell grid has "
        f"{len(grid)} of {len(SCORERS) * n} slots filled, with row counts "
        f"{sorted(grid.unique().tolist())}")

    # Both levels, because averaging hides the first. Hit@1 is a rate, so a source cell outside
    # [0, 1] is corrupt even when the seven-cell mean it feeds still lands on the track.
    assert s["hit@1"].between(0.0, 1.0).all(), (
        "hit@1 is a rate; summary.csv has a cell outside [0, 1], so the macro-mean plotted "
        "against the 0..1 track would be built from a number that cannot be a Hit@1")
    agg = s.groupby("method")["hit@1"].mean()
    assert agg.between(0.0, 1.0).all(), (
        "the full-extent track states 0..1 as the attainable range; a value left it")

    # Ties broken by ascending method name, so the ladder is reproducible run to run.
    order = sorted(SCORERS, key=lambda m: (0 if SCORERS[m]["family"] == "pop" else 1,
                                           -agg[m], m))
    pop = [m for m in order if SCORERS[m]["family"] == "pop"]
    mean = [m for m in order if SCORERS[m]["family"] == "mean"]
    assert min(agg[m] for m in pop) > max(agg[m] for m in mean), (
        "panel a is grouped by family AND sorted by value only because the families separate; "
        f"weakest population {min(agg[m] for m in pop):.6f} is not above strongest mean "
        f"{max(agg[m] for m in mean):.6f}. Regroup or restate the panel, do not redraw it.")

    # The tie marker is drawn beside whichever rows share the bottom of the mean family, so the
    # pair is READ OUT OF THE SORT here and the assertion below checks that same pair. Naming the
    # two scorers as literals instead would let a data change slide the marker to a pair whose
    # identity was never tested, and the panel would keep saying "identical" without evidence.
    tied = [m for m in mean if float(agg[m]) == float(agg[mean[-1]])]
    assert len(tied) == 2, f"the tie marker assumes exactly two equal scorers, found {len(tied)}"

    # And the marked tie is stronger than equal macro-means: the two scorers agree to full
    # precision in every numeric column of every cell. Assert that, because the panel says so.
    num = [c for c in s.columns if c not in ("task", "setting", "method")]
    key = ["task", "setting"]
    a, b = (s[s["method"] == m].sort_values(key).reset_index(drop=True) for m in tied)
    assert (a[key].values == b[key].values).all(), (
        f"{tied[0]} and {tied[1]} are not scored on the same {n} cells, so the panel cannot "
        "call them identical on all of them")
    assert (a[num].values == b[num].values).all(), (
        f"the panel marks {tied[0]} and {tied[1]} as identical on all {n} settings; they are not")

    # The bracketed pair is the extremes of the whole ladder, so name them from the sort.
    best, worst = pop[0], mean[-1]
    assert agg[best] == agg.max() and agg[worst] == agg.min(), (
        "the bracket labels itself as the panel's widest pair; the sort disagrees")
    return agg, pop, mean, tied, best, worst, n


def draw_2a(ax):
    """The Hit@1 ladder: every population-level scorer above every mean-level one."""
    agg, pop, mean, tied, best, worst, n_cells = _load()
    rows = [(m, "pop") for m in pop] + [(m, "mean") for m in mean]
    ys = {m: (i if f == "pop" else i + FAM_GAP) for i, (m, f) in enumerate(rows)}
    head = {best, worst}

    # One pale block per family, running the full attainable range. It is both the group wash and
    # the full-extent track: the block's right edge IS Hit@1 = 1, so each bar is read against the
    # ceiling without the eye travelling to the axis.
    for members, wash in ((pop, POP_WASH), (mean, MEAN_WASH)):
        y0 = ys[members[0]] - 0.5
        ax.add_patch(Rectangle((0.0, y0), 1.0, (ys[members[-1]] + 0.5) - y0,
                               facecolor=wash, edgecolor="none", zorder=0))

    for m, fam in rows:
        v, y = float(agg[m]), ys[m]
        big = m in head
        ax.barh(y, v, height=BAR_H_HEAD if big else BAR_H, color=POP if fam == "pop" else MEAN,
                linewidth=0, zorder=2)
        # Scorer name, right-aligned into the panel's left pad. The letters are never coloured:
        # the bar carries the family and the type stays above the contrast floor.
        ax.text(X_LABEL_R, y, SCORERS[m]["label"], fontsize=PT_TICK, color=TEXT,
                fontweight="bold" if big else "normal", ha="right", va="center", clip_on=False)
        if SCORERS[m]["published"]:
            # Provenance, on its own column and in a separate channel from representation.
            ax.text(X_DAGGER, y, "†", fontsize=PT_SMALL, color=SUBTLE, ha="center",
                    va="center", clip_on=False)
        # Value column, right-aligned past the end of the block rather than chasing each bar tip.
        ax.text(X_VALUE_R, y, f"{v:.3f}", ha="right", va="center", clip_on=False,
                fontsize=PT_ANNOT if big else PT_SMALL, color=TEXT if big else SUBTLE,
                fontweight="bold" if big else "normal")

    # Family labels: ink letters plus a swatch, which is the one place this figure lets a label
    # name a family. The letters are NOT set in the family colour, because MEAN on white is a
    # 2:1 contrast ratio at 6.5 pt; the swatch beside them carries the hue at mark scale instead.
    for members, fam in ((pop, "pop"), (mean, "mean")):
        y0, y1 = ys[members[0]] - 0.5, ys[members[-1]] + 0.5
        ax.text(X_FAMILY, 0.5 * (y0 + y1), FAMILY_NAME[fam].replace("-level", ""), rotation=90,
                fontsize=PT_SMALL, color=TEXT, ha="center", va="center", clip_on=False)
        ax.add_patch(Rectangle((X_SWATCH - _u(0.014), y0), _u(0.028), y1 - y0, clip_on=False,
                               facecolor=POP if fam == "pop" else MEAN, edgecolor="none",
                               zorder=3))

    # ---------------------------------------------------------------- the tie, marked not implied
    # `tied` comes from _load, which asserted these two rows identical in every column of every
    # cell. The marker and the assertion therefore always point at the same pair.
    y_hi, y_lo = ys[tied[0]], ys[tied[-1]]
    x_t = float(agg[tied[0]]) + _u(0.130)
    ax.plot([x_t, x_t], [y_hi, y_lo], color=SHARED, lw=LW_HAIR, zorder=3, clip_on=False)
    for y in (y_hi, y_lo):
        ax.plot([x_t - _u(0.045), x_t], [y, y], color=SHARED, lw=LW_HAIR, zorder=3, clip_on=False)
    ax.text(x_t + _u(0.045), 0.5 * (y_hi + y_lo),
            f"identical on all {n_cells} settings (panel g)", fontsize=PT_SMALL, color=TEXT,
            ha="left", va="center")

    # ---------------------------------------------------------------- the headline comparison
    d = float(agg[best]) - float(agg[worst])          # unrounded, so this prints +0.448 not +0.449
    ratio = float(agg[best]) / float(agg[worst])
    y_b, y_w = ys[best], ys[worst]
    ax.plot([X_BRACKET, X_BRACKET], [y_b, y_w], color=SHARED, lw=LW_HEAD, zorder=3,
            clip_on=False)
    for y in (y_b, y_w):
        ax.plot([X_ARM, X_BRACKET], [y, y], color=SHARED, lw=LW_HEAD, zorder=3, clip_on=False)
    y_mid = 0.5 * (y_b + y_w)
    ax.text(X_HEAD, y_mid - 0.55, f"+{d:.3f} Hit@1", fontsize=PT_TITLE, fontweight="bold",
            color=TEXT, ha="left", va="center", clip_on=False)
    ax.text(X_HEAD, y_mid + 0.55,
            f"{SCORERS[best]['label']} above {SCORERS[worst]['label']}, {ratio:.2f}x",
            fontsize=PT_SMALL, color=SUBTLE, ha="left", va="center", clip_on=False)

    # ---------------------------------------------------------------- axes furniture
    ax.set_xlim(0.0, XMAX)
    ax.set_ylim(ys[rows[-1][0]] + 0.56, ys[rows[0][0]] - 0.56)     # inverted: best scorer on top
    ax.set_xticks([0.0, 0.25, 0.5, 0.75, 1.0])
    ax.set_yticks([])
    ax.set_xlabel(f"Hit@1, macro-average across {n_cells} task settings")
    # Centred under the TRACK rather than under the axes, which extends past it.
    ax.xaxis.set_label_coords(0.5 / XMAX, -0.175)
    ax.tick_params(axis="y", length=0)
    ax.tick_params(axis="x", length=2.2, width=0.6, color=HAIRLINE, labelcolor=TEXT,
                   labelsize=PT_TICK)
    for sp in ("left", "right", "top"):
        ax.spines[sp].set_visible(False)
    ax.spines["bottom"].set_color(HAIRLINE)
    ax.spines["bottom"].set_linewidth(LW_HAIR)
    ax.spines["bottom"].set_bounds(0.0, 1.0)       # the scale exists only under the tracks
    # Key for the provenance glyph, kept off the ladder and out of a legend box.
    ax.text(1.0, -0.175, "† published baseline", transform=ax.transAxes, fontsize=PT_SMALL,
            color=SUBTLE, ha="right", va="center")

    title(ax, "Every population scorer beats every mean scorer")


if __name__ == "__main__":
    sys.path.insert(0, os.path.join(REPO, "figures"))
    from figstyle import apply_style
    apply_style(sizes=(PT_TITLE, PT_ANNOT, PT_TICK))
    fig = plt.figure(figsize=(6.90, 1.60))
    ax = fig.add_axes([0.94 / 6.90, 0.46 / 1.60, 5.88 / 6.90, 1.34 / 1.60])
    draw_2a(ax)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "2a.png")
    fig.savefig(out, dpi=300)
    print(f"wrote {out}")
