"""PopRetrieve Figure 2 panel 2f: the Class-A gain belongs to the population-level FAMILY.

WHAT THE PANEL CLAIMS
---------------------
Five different population-level scores, paired query by query against mean cosine, all give a
positive median regret reduction whose bootstrap 95% interval excludes zero. The claim is
therefore about the family and not about one lucky distributional metric. It is deliberately no
larger than that: this is a Class-A comparison, the criteria reward correspondence between
response populations, which is the information population-level retrieval uses. Whether the
retrieved neighbours are biologically better is Figure 3's question, not this panel's.

The second thing the panel shows, by arrangement rather than by a label, is that the two
subpopulation-coverage scores sit further right than the three global-distance scores. That
ordering is asserted at draw time so the layout cannot outlive it. It is an ordering of the five
POINT ESTIMATES and nothing stronger: the coverage-mean interval still overlaps the sliced-W
interval, so the panel is not claiming the two sub-families are separated.

WHICH FILE IT READS
-------------------
results/exp12_partial_observed_retrieval/per_query_scores.csv, restricted to the rows whose
recommendation_mode is DART_recommended: 621 of the file's 765 queries, each scored by all nine
methods, so 5,589 of its 6,885 rows. Paired on (split_type, cell_line, heldout_drug,
observed_library_fraction, seed) exactly as panels c and d pair theirs. Regret reduction is
mean_cosine decision_regret minus the population scorer's decision_regret, so positive is better.

This panel previously read figures/source_data/fig2f_classA_robustness.csv, a hand-copied mirror
with no generator. It now reads the authoritative results file, the same correction panel c
received. The mirror is still checked against the recomputation by _crosscheck_mirror(), which
runs in the standalone __main__ block; as of 2026-08-31 the two agree on all five medians and all
five improved fractions exactly (largest median difference 2.8e-17, fractions identical), so
nothing was lost by the move.

n = 621 IS NOT A TYPO FOR PANEL c's 765
---------------------------------------
Panel c reports the headline on ALL 765 partial-observed queries, precisely so the headline is not
taken on a gate-selected subset. This panel reports the per-metric sweep on the 621 queries the
pre-specified gate recommended, which is the subset the sweep was run on. The n is stated on the
panel so the mismatch reads as a scope note rather than as an error.

JUDGEMENT CALLS A READER COULD REASONABLY DISAGREE WITH
-------------------------------------------------------
1. Rows are ordered by CONCEPTUAL FAMILY, not by value: energy, MMD, sliced-Wasserstein (global
   distances between two populations), then coverage-mean, coverage-worst (subpopulation
   coverage). Sorting by value would have made a tidier ladder and would have hidden the fact
   that the conceptual split and the performance split coincide.
2. The two sub-families are separated by POSITION (a wider gap between the groups) and by SHAPE
   (circle vs square), never by hue: all five are population-level scores and take one colour.
   Neither sub-family is drawn as secondary, which is why both markers are filled rather than one
   open: filled-versus-open would rank them, and this panel is not ranking them. A hairline group
   rule was tried and cut: drawn across the panel it competed with the zero datum, and drawn only
   in the left margin it read as a stray mark.
3. The sub-families are NOT named on the panel. Their names do not fit beside a 2.45 in plot at
   the 6.5 pt floor, and the y labels already read "coverage-" for the pair, so the naming is left
   to the caption rather than shrunk below the floor.
4. "sliced-W" abbreviates sliced-Wasserstein. The full word needs 1.0 in of the 0.86 in available
   left of the axes; the caption spells it out.
5. The per-metric improved fractions (0.601, 0.605, 0.618, 0.644, 0.720 as of 2026-08-31) are
   computed here but not drawn. A second numeric column would fill the empty right half of the three distance rows,
   which is the emptiness that makes the coverage pair's rightward offset visible.
6. The interval is a seeded percentile bootstrap of the median (fig2_style.boot_median_ci,
   4000 resamples, seed 0). Its endpoints move in the third decimal between seeds; the assertion
   the panel rests on, that every lower bound is above zero, holds with margin (the tightest is
   energy at +0.037). What the interval IS is named on the panel rather than left to the caption:
   the phrase over the panel makes a statistical claim about the intervals, and a claim about an
   unnamed interval is not readable. Panel d names its interval on-panel for the same reason.
7. The count word in the phrase is derived from the number of rows drawn, and the row count is
   asserted against the y positions. Writing "five" as a literal let the phrase outlive the data:
   adding a sixth scorer would have been silently truncated by zip() and the panel would have gone
   on claiming five.

Palette comes from fig2_style; do NOT re-declare hex values here. Every panel file used to carry
its own copy, which made figstyle's "one edit here recolours the whole deck" untrue: a recolour
meant editing 43 files and missing one was silent.

Run standalone: python fig2f.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fig2_style import (LW_HAIR, MS_DOT, POP, PT_SMALL, PT_TICK, REPO,  # noqa: E402
                        SUBTLE, TEXT, bare_axes, boot_median_ci, title, zero_rule)

# The tether to zero is the same POP hue at half strength, derived from POP rather than declared
# as a second hex, so a recolour of the family carries it. It has to be visible without competing
# with the interval: at equal weight the stem plus the interval read as one bar, which is the
# chart type this panel exists to avoid.
STEM_TINT = tuple(0.45 * np.array(mcolors.to_rgb(POP)) + 0.55)

SRC = f"{REPO}/results/exp12_partial_observed_retrieval/per_query_scores.csv"
MIRROR = f"{REPO}/figures/source_data/fig2f_classA_robustness.csv"

QUERY_KEY = ["split_type", "cell_line", "heldout_drug", "observed_library_fraction", "seed"]
BASELINE = "mean_cosine"
MODE = "DART_recommended"
N_QUERIES = 621                      # the gate-recommended subset; see the module docstring

# (method column, y label, marker). Conceptual order, never value order: the three global
# distances between two populations first, then the two subpopulation-coverage scores.
DISTANCES = [("DART_energy", "energy"),
             ("DART_mmd", "MMD"),
             ("DART_sliced_wasserstein", "sliced-W")]
COVERAGE = [("DART_coverage_mean", "coverage-mean"),
            ("DART_coverage_worst", "coverage-worst")]

# y positions, top row first. The 1.5 gap between the last distance row and the first coverage
# row is what makes the two sub-families read as two blocks; within a block the pitch is 1.0.
Y_POS = [4.5, 3.5, 2.5, 1.0, 0.0]
X_MAX = 0.155                        # a stated scale, round above the largest upper bound

# The phrase over the panel counts the rows out loud, so the word comes from the row count and
# never from a literal. An unlisted count is a KeyError at draw time, which is the intent.
COUNT_WORD = {2: "both", 3: "all three", 4: "all four", 5: "all five", 6: "all six"}


def paired_gains() -> "dict[str, np.ndarray]":
    """Per-query regret reduction of each population scorer against mean cosine, on the subset.

    Returns one array per method, all of length N_QUERIES and all indexed by the same queries.
    """
    d = pd.read_csv(SRC)
    d = d[d["recommendation_mode"] == MODE]
    base = d[d["method"] == BASELINE].set_index(QUERY_KEY)["decision_regret"]
    assert base.index.is_unique, "mean_cosine is not one row per query on the recommended subset"

    out = {}
    for method, _ in DISTANCES + COVERAGE:
        s = d[d["method"] == method].set_index(QUERY_KEY)["decision_regret"]
        assert s.index.is_unique, f"{method} is not one row per query"
        j = pd.concat([base.rename("base"), s.rename("pop")], axis=1).dropna()
        assert len(j) == N_QUERIES, f"expected {N_QUERIES} paired queries for {method}, got {len(j)}"
        out[method] = (j["base"] - j["pop"]).to_numpy()
    return out


def draw_2f(ax):
    """Five population-level scores, median regret reduction vs mean cosine with bootstrap CIs."""
    gains = paired_gains()
    stats = {m: boot_median_ci(gains[m]) for m, _ in DISTANCES + COVERAGE}

    # The phrase over the panel says every interval clears zero, so the panel refuses to draw
    # itself if that stops being true of the file it just read.
    lows = {m: lo for m, (_, lo, _) in stats.items()}
    assert all(lo > 0 for lo in lows.values()), f"an interval touches zero: {lows}"
    # The arrangement claims the coverage pair sits further right than the distance trio. If that
    # ever reverses, the conceptual ordering stops being legible and the panel needs redesigning.
    assert (min(stats[m][0] for m, _ in COVERAGE)
            > max(stats[m][0] for m, _ in DISTANCES)), "coverage no longer leads the distances"
    hi_max = max(hi for _, _, hi in stats.values())
    assert hi_max < X_MAX, f"an upper bound {hi_max:.4f} runs past the drawn scale {X_MAX}"

    rows = [(m, lab, "o") for m, lab in DISTANCES] + [(m, lab, "s") for m, lab in COVERAGE]
    # zip() below would silently drop rows past the end of Y_POS, leaving the phrase over the
    # panel counting scorers that were never drawn.
    assert len(rows) == len(Y_POS), f"{len(rows)} scorers but {len(Y_POS)} y positions"

    # Zero first and darkest: it is the datum every point is read against, not a gridline.
    zero_rule(ax, 0.0, color=TEXT, lw=1.0, zorder=2)

    for y, (method, _, marker) in zip(Y_POS, rows):
        med, lo, hi = stats[method]
        # thin stem from zero to the median, thicker interval on top of it
        ax.plot([0.0, med], [y, y], color=STEM_TINT, lw=LW_HAIR, solid_capstyle="butt", zorder=3)
        ax.plot([lo, hi], [y, y], color=POP, lw=1.4, solid_capstyle="round", zorder=4)
        ax.scatter([med], [y], s=MS_DOT, marker=marker, color=POP, linewidths=0.6,
                   edgecolors="white", zorder=5)

    bare_axes(ax, keep=("bottom",))
    ax.set_yticks(Y_POS)
    ax.set_yticklabels([lab for _, lab, _ in rows], fontsize=PT_TICK, color=TEXT)
    ax.tick_params(axis="y", length=0, pad=2.0)
    ax.set_ylim(-0.55, 6.10)
    ax.set_xlim(-0.010, X_MAX)
    ax.set_xticks([0.0, 0.05, 0.10, 0.15])
    ax.set_xticklabels(["0", "0.05", "0.10", "0.15"])
    ax.set_xlabel("median regret reduction\nvs mean cosine, paired by query", linespacing=1.2)

    # Scope note in the headroom above the top row, where it crosses no mark. It says n and it
    # says which n, because panel c's 765 is a different and deliberate scope.
    n_drawn = len(next(iter(gains.values())))
    ax.text(X_MAX, 5.45,
            f"n = {n_drawn} gate-recommended queries\ninterval: bootstrap 95% CI of the median",
            ha="right", va="center", fontsize=PT_SMALL, color=SUBTLE, linespacing=1.3)
    title(ax, f"{COUNT_WORD[len(rows)].capitalize()} intervals clear zero")


def _crosscheck_mirror():
    """Compare the recomputation against the hand-copied source_data mirror. Reports, not silent."""
    gains = paired_gains()
    mir = pd.read_csv(MIRROR).set_index("method")
    worst_med, worst_frac = 0.0, 0.0
    for method, _ in DISTANCES + COVERAGE:
        g = gains[method]
        worst_med = max(worst_med, abs(float(np.median(g)) - float(mir.loc[method, "median_regret_reduction"])))
        worst_frac = max(worst_frac, abs(float((g > 0).mean()) - float(mir.loc[method, "frac_improved"])))
        assert int(mir.loc[method, "n"]) == len(g), f"mirror n disagrees for {method}"
    print(f"mirror crosscheck: max |median| diff {worst_med:.2e}, max |frac| diff {worst_frac:.2e}")
    assert worst_med < 1e-9 and worst_frac < 1e-9, "the source_data mirror has drifted from results/"


if __name__ == "__main__":
    _crosscheck_mirror()
    fig, ax = plt.subplots(figsize=(3.45, 2.12))
    draw_2f(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "2f.png"), dpi=200, bbox_inches="tight")
    print("wrote 2f.png")
