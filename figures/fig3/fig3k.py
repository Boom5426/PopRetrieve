"""PopRetrieve Figure 3 panel 3k: how strongly the energy ranking tracks candidate magnitude.

WHAT THIS PANEL SHOWS
---------------------
For each of the 103 leave-one-drug-out queries, the energy DISTANCE between the query population
and a candidate population is Spearman-correlated, across that query's candidates, with the
CANDIDATE'S OWN response magnitude. The panel draws the distribution of those 103 per-query
correlations: median +0.780, with 95 of 103 queries positive and 76 above +0.5. Ranking candidates
nearest-first therefore reproduces, to a large degree, ranking them by how small their own response
is. Nothing here measures retrieval quality, and nothing here is a comparison between retrieval
families.

WHAT CHANGED IN THE 2026-08-31 PASS, AND WHY
--------------------------------------------
The panel used to set the phrase "Energy ranks largely by magnitude" over itself at PT_TITLE. It
is deleted, along with the fig3_style.title() helper that drew it: thirteen conclusion sentences
on one page is thirteen claims competing for attention, and in a Nature-family main figure the
panels carry evidence while the legend carries the argument. The claim moved to this panel's
caption entry, where it can be qualified properly, and fig3_assemble._assert_no_titles refuses to
build a figure in which any panel draws text above PT_ANNOT, so it cannot come back at a smaller
size.

Be precise about where each number now lives, because the assertions below name the file a
maintainer must edit when one fires. The CAPTION (manuscript/latex, Fig. 3 entry m) carries the
median and the fact of the left tail, and nothing more: "the per-query Spearman correlation
between the query-candidate energy distance and the candidate's own response magnitude, median
+0.780. The distribution has a left tail reaching below zero, so this describes the typical query
and not every one." The three COUNTS, 95 positive, 76 above +0.5 and 8 at or below zero, are
prose in this docstring and in figures/fig3/README.md; they have never been in the caption and
they are not drawn. The assertions that policed the deleted phrase were not deleted with it, and
each one now names its own reader.

Removing the phrases returned 0.42 in to the six rows, and this axes grew from 0.64 to 0.69 in.
All of it went into the marks, none into text. The label band that used to sit above the density,
holding the title and the median value, is gone: the median value now sits INSIDE the panel, in
the empty wedge to the left of the median rule, which is empty because the density there never
exceeds 0.53 of its peak (asserted in _assert_label_clear). The density therefore stands 0.43 in
rather than 0.36, and the rug 0.14 in rather than 0.09, so the eight left-tail queries are 48 per
cent taller than they were. Four things are drawn and nothing else: the density, the rug, the
median with its value, and the zero rule.

WHERE IT SITS, AND THE INFERENCE IT MUST NOT LICENSE
----------------------------------------------------
Row 6 is l | m. Panel l scores four rankings against ABSOLUTE potency: energy lands at -0.520
while the ranking that sorts candidates by their own response magnitude, comparing no
distributions at all, sits highest at +0.692. This panel is l's mechanism. Energy distance grows
with the candidate's own magnitude, so nearest-first hands back the weakest candidates, which is
why energy inverts once the endpoint becomes "which candidate kills hardest".

It is NOT the mechanism for panel h, and drawing it beside h's number would be a misreading the
docstring has to forestall. Panel h reports energy at +0.276 against drug-drug functional
similarity and +0.097 after partialling out MAGNITUDE MATCH, the query-dependent ranking by
-|mag(c) - mag(q)|, whose own median on that oracle is +0.232. What is drawn here is the coupling
to the candidate's own magnitude, a query-INDEPENDENT quantity: scored on h's oracle that ranking
reaches median -0.506, on the far side of zero from energy's +0.265, and its per-query
correlations are essentially unrelated to magnitude match (Pearson r = +0.007 across the 103
queries). A median rho of +0.780 says the two candidate ORDERINGS largely agree; it does not say
that energy's external win is a magnitude effect, and the control refuses that reading. Running
this module standalone prints both functional-oracle medians from the file, so the paragraph above
can be checked rather than believed.

THE LEFT TAIL IS REAL AND IS DRAWN
----------------------------------
The median describes the typical query, not every query. Eight of the 103 queries sit at or below
zero (minimum -0.242): for those, the energy distance carries no candidate-magnitude information
at all. The rug beneath the density plots all 103 queries individually and the zero rule is drawn,
so those eight are visible and countable rather than smoothed away by the density. _assert_claims
checks the median, the sign counts and the size of the left tail, so the caption's hedge cannot
quietly stop being a hedge.

Source data: figures/source_data/fig3hi_class_c_potency.csv, column energydist_vs_candmag_rho
(the v2 analysis with the corrected energy sign; 103 rows = 35 held-out query drugs x 3 cell
lines, minus two combinations absent from the table). The column is computed from the retrieval
scores and the candidate magnitudes ALONE and never touches an oracle, so nothing about it depends
on the absolute-potency endpoint that panel h retired; it is the same energy ranking h and i are
graded on. One caveat that belongs on the record: for 5 of the 103 queries, all MCF7, the
functional analysis drops candidates lacking a GDSC2 profile, so its pool is 33 or 30 where this
file has 34. The other 98 pools are identical.

JUDGEMENT CALLS A READER COULD REASONABLY DISAGREE WITH
-------------------------------------------------------
1. COLOUR. fig3_style lists the response-magnitude scalar among the EXT (green) objects. This
   panel is nonetheless drawn entirely in SHARED grey, because what is plotted is a correlation
   between two properties of the energy score's own candidate ranking, not the magnitude scalar
   competing as a retriever. Neither blue nor orange can apply: no population-versus-mean
   comparison happens here, and colouring a strong positive correlation blue would be exactly the
   error fig3_style was written to stop.
2. DENSITY ESTIMATOR. A Gaussian KDE at Scott's bandwidth, reflected about rho = +1. Spearman rho
   is bounded at 1 and 41 of the 103 queries sit above +0.9, so an unreflected KDE droops at the
   right edge and visually understates the pile-up that is the panel's whole point. The reflection
   is a boundary correction, not a smoothing choice, and it does not manufacture the mode: the
   unreflected estimate already peaks at rho = +0.92, where 41 of the 103 queries lie above
   +0.9. No reflection is applied at the lower end, where the nearest datum sits 0.76 rho units
   from the -1 bound, 5.7 bandwidths away, so the -1 boundary bites nothing. Scott's bandwidth here is 0.134, wide enough to smooth the gap between the
   left-tail queries and the main mass; the rug is the unsmoothed sample and shows that gap.
3. NO CELL-LINE ENCODING. The three lines agree closely (median rho A549 +0.762, K562 +0.885,
   MCF7 +0.771) and no claim here is per line, so the rug is one undifferentiated grey series.
   Drawing 103 marks in three shapes on a 2.48 in axis would add ink a reader cannot resolve.
4. LINE WEIGHT AS HIERARCHY. The three weights that carry the hierarchy are all fig3_style's:
   LW_HAIR (0.6) for the baseline and the rho = +1 bound, which are guides; LW_STEM (0.9) for the
   density outline, which is the panel's principal mark; LW_LINE (1.1) for the median rule, which
   is the one thing carrying a number. With the title gone the density has to read as the subject
   on its own, and a hairline outline over a 0.43 in curve did not. No new constant was invented
   for this. Two further weights are drawn and are NOT fig3_style constants, so they are named
   here rather than passed off as house values: the rug is 0.7, which is what fig3f sets its rug
   to, and the zero rule is 0.8, which is fig3_style.zero_rule's own default and what panels a to
   l pass. Both are figure-wide conventions carried by repetition, not by a constant.
5. THE VERTICAL AXIS IS A DENSITY AND SAYS SO. It is normalised to a peak of 1 and carries no
   claim, so it gets no ticks. It is labelled "query density" rather than "queries" because the
   height is not a count of anything and an untick-ed axis labelled with the sample unit invites
   a reader to read it as one. Note that fig3_assemble.PADS reserves 0.72 in on this panel's left
   for "a rotated label plus numeric ticks"; roughly half of that is unused here.
6. The queries within one cell line share a candidate pool, so the 103 values are not independent.
   This panel therefore quotes no p value and no confidence interval, only the observed median.
   Panel i states the same pseudo-replication caveat for the paired test it does report.

Run standalone: python fig3k.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fig3_style import (FAINT, HAIRLINE, LW_HAIR, LW_LINE, LW_STEM, MS_DOT,  # noqa: E402
                        PT_ANNOT, REPO, SHARED, SUBTLE, TEXT, bare_axes, zero_rule)

SRC = os.path.join(REPO, "figures", "source_data", "fig3hi_class_c_potency.csv")
FUNCTIONAL = os.path.join(REPO, "figures", "source_data", "fig3hi_class_c_functional.csv")
COL = "energydist_vs_candmag_rho"

N_QUERIES = 103             # panel j reads the same file and states the same n; keep them equal

RHO_BOUND = 1.0             # Spearman rho cannot exceed this; the density is reflected about it
XLO, XHI = -0.38, 1.02      # the view; asserted below to contain every observation
YTOP = 1.10                 # density peak is normalised to 1.0; this is headroom, not a text band
RUG_TOP, RUG_BOT = -0.13, -0.45

# Where the median's value is set, and the room it needs. The label hangs to the LEFT of the
# median rule, inside the panel, in the wedge under the rising right shoulder of the density.
# _assert_label_clear refuses to draw if the density has risen into that box, so the placement
# cannot outlive the shape it was chosen for.
#
# The room is declared in PRINTED INCHES and converted through the axes rect at draw time, not
# frozen in rho units. A label's width and height are properties of the string and of PT_ANNOT;
# they become rho units and density units only by way of this panel's printed size and its view.
# The earlier constants (0.46 rho wide, floor at 0.66) were measured on a 2.48 x 0.69 in axes
# with a 1.40 rho view and silently assumed all three, so a change to fig3_assemble's ROWS or
# PADS would have left the guard checking a box the label no longer occupied. Deriving them
# instead means the guard follows the panel.
MED_LABEL_Y = 0.80
MED_LABEL_DX = 0.03         # rho units between the label's right edge and the median rule
# Per-character advance as a fraction of the em, and half the em box as an ink half-height. Both
# are deliberate over-estimates, so the guarded box is larger than the ink and the derived floor
# sits below it: "median +0.791" measures 0.538 em per character in the deck's Arial at PT_ANNOT,
# and its ink runs 0.72 em tall because the string is digits and lowercase with no descender.
LABEL_EM_W = 0.62
LABEL_EM_H = 0.50


def _load():
    if not os.path.exists(SRC):
        raise FileNotFoundError(
            f"{SRC} does not exist. Run analysis/class_c/class_c_potency_audit.py first.")
    d = pd.read_csv(SRC)
    if COL not in d.columns:
        raise KeyError(f"{SRC} has no column {COL!r}; columns are {list(d.columns)}")
    if len(d) != N_QUERIES:
        raise ValueError(f"{SRC} has {len(d)} queries; panel 3k, panel 3j and the caption all say "
                         f"{N_QUERIES}. Fix one or the other, do not draw the mismatch.")
    v = d[COL].to_numpy(dtype=float)
    if not np.isfinite(v).all():
        raise ValueError(f"{COL} carries {int((~np.isfinite(v)).sum())} non-finite values; "
                         "this panel will not drop rows silently")
    return d, v


def _assert_claims(v, med):
    """Refuse to draw a number, or hand the caption one, the data no longer support.

    The panel itself now states only the median, computed at draw time, so its ink cannot lie.
    The prose goes further, quoting the sign counts and the size of the left tail, and those are
    checked here: a data change must break the build rather than leave prose describing a panel
    that no longer looks like that. Each message names the text it guards, because they guard
    two different texts: the caption carries the median and the fact of the tail, while the three
    counts live only in this module's docstring and in figures/fig3/README.md.
    """
    n_pos = int((v > 0).sum())
    n_strong = int((v > 0.5).sum())
    n_le0 = int((v <= 0).sum())

    assert med >= 0.5, (
        f"the caption claims a strong positive coupling, but the median rho is {med:+.3f}. "
        "Restate the caption from the data.")
    assert n_pos > v.size / 2, (
        f"the caption claims the typical query is magnitude-ordered, but only {n_pos} of "
        f"{v.size} queries have rho > 0.")
    # The docstring's three counts. They are recomputed, never typed into the prose from memory.
    assert (n_pos, n_strong, n_le0) == (95, 76, 8), (
        f"this module's docstring and figures/fig3/README.md say 95 of 103 positive, 76 above "
        f"+0.5 and 8 at or below zero; the file now gives {n_pos}, {n_strong} and {n_le0}. "
        "Update both. The caption quotes none of these three, so it needs no edit for this.")
    # The caption's "largely" is a hedge and must stay one: a left tail that vanished would make
    # the sentence weaker than the data, and one that swelled would make it stronger.
    assert 0 < n_le0 < 0.25 * v.size, (
        f"the caption hedges with \"a left tail reaching below zero\" because {n_le0} of "
        f"{v.size} queries carry no coupling. At this count the hedge no longer describes the "
        "panel; restate the claim from the data.")
    assert v.max() <= RHO_BOUND + 1e-9, (
        f"{COL} reaches {v.max():+.4f}; a Spearman rho cannot exceed {RHO_BOUND}, so the "
        "reflection boundary and the source file disagree.")
    assert XLO <= v.min() and v.max() <= XHI, (
        f"the view [{XLO}, {XHI}] clips the data [{v.min():+.3f}, {v.max():+.3f}]; widen the "
        "view rather than cropping queries out of the panel")


def _label_box(ax, med, label):
    """The rho window and the density floor the median's label occupies, in DATA units.

    The width and the height enter in inches, from ``label`` and PT_ANNOT, and are converted
    through this axes' printed size. ``YTOP - (RUG_BOT - 0.05)`` is the y range draw_3k sets
    below, quoted here because the guard runs before set_ylim.
    """
    w_in = ax.figure.get_figwidth() * ax.get_position().width
    h_in = ax.figure.get_figheight() * ax.get_position().height
    span = len(label) * LABEL_EM_W * (PT_ANNOT / 72.0) / w_in * (XHI - XLO)
    half = LABEL_EM_H * (PT_ANNOT / 72.0) / h_in * (YTOP - (RUG_BOT - 0.05))
    hi = med - MED_LABEL_DX
    return hi - span, hi, MED_LABEL_Y - half


def _assert_label_clear(grid, dens, lo, hi, floor):
    """Refuse to set the median's value on top of the curve it describes, or off the panel.

    The label sits inside the panel rather than in a band above it, which is only legible because
    the density is low everywhere to the left of the median. That is a property of this sample,
    so it is checked against this sample at draw time.
    """
    assert lo >= XLO, (
        f"the median label would start at rho {lo:+.3f}, left of the view edge {XLO}. It is set "
        "inside the panel, so it has to fit inside the panel.")
    win = (grid >= lo) & (grid <= hi)
    peak = float(dens[win].max())
    assert peak < floor, (
        f"the median label occupies rho [{lo:+.3f}, {hi:+.3f}] down to a normalised density of "
        f"{floor:.3f}, but the curve now reaches {peak:.3f} there and the text would sit on the "
        "distribution. Move the label rather than letting it overlap.")


def _density(v, grid):
    """Scott-bandwidth Gaussian KDE, reflected about the rho = +1 bound. See docstring note 2."""
    kde = gaussian_kde(v)
    return kde(grid) + kde(2.0 * RHO_BOUND - grid)


def draw_3k(ax):
    d, v = _load()
    med = float(np.median(v))
    q1, q3 = (float(x) for x in np.percentile(v, [25, 75]))
    n_le0 = int((v <= 0).sum())
    _assert_claims(v, med)

    # --- the distribution: a half-violin standing on the baseline, SHARED grey ----------------
    grid = np.linspace(XLO, RHO_BOUND, 601)
    dens = _density(v, grid)
    dens = dens / dens.max()
    med_label = f"median {med:+.3f}"
    lo, hi, floor = _label_box(ax, med, med_label)
    _assert_label_clear(grid, dens, lo, hi, floor)
    # Fill and outline are drawn separately so the polygon's closing verticals do not inherit
    # the curve's weight: the density is genuinely cut off at the rho = +1 bound, and a full-weight
    # stroke there reads as a drawn wall rather than as the edge of the statistic's range.
    ax.fill_between(grid, 0.0, dens, facecolor=FAINT, lw=0, zorder=3)
    ax.plot(grid, dens, color=SHARED, lw=LW_STEM, zorder=4)
    ax.plot([RHO_BOUND, RHO_BOUND], [0.0, dens[-1]], color=HAIRLINE, lw=LW_HAIR, zorder=4)
    ax.plot([XLO, RHO_BOUND], [0.0, 0.0], color=HAIRLINE, lw=LW_HAIR, zorder=4)

    # --- the 103 queries themselves, unsmoothed, beneath it ------------------------------------
    ax.vlines(v, RUG_BOT, RUG_TOP, color=SHARED, lw=0.7, alpha=0.55, zorder=3)

    # --- zero is the datum: no coupling. Eight queries sit at or below it. ---------------------
    zero_rule(ax, at=0.0, vertical=True, color=SUBTLE, lw=0.8, zorder=4, ls=(0, (2.4, 1.8)))

    # --- one emphasised mark: the median, drawn through the whole panel and labelled ----------
    ax.plot([med, med], [RUG_BOT, YTOP - 0.05], color=TEXT, lw=LW_LINE, zorder=6,
            solid_capstyle="butt")
    ax.scatter([med], [0.0], s=MS_DOT, color=TEXT, zorder=7, linewidths=0)
    ax.text(hi, MED_LABEL_Y, med_label, ha="right", va="center",
            fontsize=PT_ANNOT, color=TEXT, zorder=7)

    # --- frame -------------------------------------------------------------------------------
    bare_axes(ax, keep=("bottom",))
    ax.set_xlim(XLO, XHI)
    ax.set_ylim(RUG_BOT - 0.05, YTOP)
    ax.set_xticks([0.0, 0.25, 0.50, 0.75, 1.00])
    ax.set_xticklabels(["0", "0.25", "0.5", "0.75", "1"])
    ax.set_yticks([])
    # Two lines because one is 3.28 in wide on a 2.48 in axis. "the candidate's own" is the part a
    # reader must not lose: the correlation is with the CANDIDATE's response magnitude, not the
    # query's, and that is what makes nearest-first a magnitude ranking.
    ax.set_xlabel("Spearman " r"$\rho$" ": energy distance vs\nthe candidate's own response "
                  "magnitude", fontsize=PT_ANNOT, color=TEXT, labelpad=1.6, linespacing=1.18)
    # Two lines rather than one: "query density" set on a single line stands 0.62 in tall and
    # would all but fill the 0.69 in axes, reading as a rule down the left edge.
    ax.set_ylabel("query\ndensity", fontsize=PT_ANNOT, color=TEXT, labelpad=2.0,
                  linespacing=1.10)

    return {"n": int(v.size), "median": med, "q1": q1, "q3": q3,
            "n_pos": int((v > 0).sum()), "n_at_or_below_zero": n_le0,
            "min": float(v.min()), "max": float(v.max()),
            "per_line_median": {ln: float(g[COL].median()) for ln, g in d.groupby("cell_line")}}


def _cross_endpoint():
    """Check the docstring's "this is not h's channel" paragraph against the functional file.

    The paragraph exists to stop a reader crediting energy's +0.276 to the coupling this panel
    draws, and it rests on two medians and one correlation that live in another file. They are
    verified here rather than asserted in draw_3k, because a panel must not refuse to render for
    a fact about a file it does not plot; the same split is what fig3j does.
    """
    if not os.path.exists(FUNCTIONAL):
        raise FileNotFoundError(f"{FUNCTIONAL} does not exist; the guard in this module's "
                                "docstring cannot be checked without it.")
    f = pd.read_csv(FUNCTIONAL)
    e, only, match = (float(f[c].median()) for c in
                      ("energy_rho", "magnitude_only_rho", "magnitude_match_rho"))
    r = float(np.corrcoef(f["magnitude_only_rho"], f["magnitude_match_rho"])[0, 1])
    assert only < 0 < e, (
        f"the docstring says the candidate-magnitude ranking and energy land on OPPOSITE sides "
        f"of zero on the functional oracle; they now give {only:+.3f} and {e:+.3f}.")
    assert abs(r) < 0.10, (
        f"the docstring says the two magnitude channels are essentially unrelated across queries; "
        f"they now correlate at r = {r:+.3f}.")
    return e, only, match, r


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from figstyle import apply_style  # noqa: E402
    from fig3_style import PT_TICK, PT_TITLE  # noqa: E402

    apply_style(sizes=(PT_TITLE, PT_ANNOT, PT_TICK))
    # The panel BOX on the printed page: 3.30 x 1.24 in (row 6 is 1.07 in plus fig3_assemble's
    # 0.17 in letter block), with fig3_assemble.PADS["m"] holding the axes inside it.
    fig = plt.figure(figsize=(3.30, 1.24))
    ax = fig.add_axes([0.72 / 3.30, 0.38 / 1.24, 2.48 / 3.30, 0.69 / 1.24])
    st = draw_3k(ax)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "3k.png")
    fig.savefig(out, dpi=300)
    print(f"wrote {out}")
    print(f"n = {st['n']}  median {st['median']:+.4f}  IQR [{st['q1']:+.3f}, {st['q3']:+.3f}]  "
          f"range [{st['min']:+.3f}, {st['max']:+.3f}]")
    print(f"{st['n_pos']} of {st['n']} queries above zero; "
          f"{st['n_at_or_below_zero']} at or below it")
    print("per cell line median: "
          + ", ".join(f"{k} {x:+.3f}" for k, x in st["per_line_median"].items()))

    e, only, match, r = _cross_endpoint()
    print("\nGUARD, on the functional oracle this panel is NOT evidence about:")
    print(f"  energy {e:+.3f} | candidate-magnitude ranking {only:+.3f} | "
          f"magnitude match (the channel h partials out) {match:+.3f}")
    print(f"  the two magnitude channels correlate at r = {r:+.3f} across queries, so the "
          "coupling drawn here is not h's partial.")
