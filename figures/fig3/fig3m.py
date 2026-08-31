"""PopRetrieve Figure 3 panel 3m: the energy ranking is, for most queries, a magnitude ordering.

WHAT THIS PANEL CLAIMS
----------------------
For each of the 103 leave-one-drug-out queries, the energy DISTANCE between the query population
and a candidate population is Spearman-correlated, across that query's candidates, with the
CANDIDATE'S OWN response magnitude. The panel draws the distribution of those 103 per-query
correlations. Its claim is the median, +0.791, with 95 of 103 queries positive and 78 above +0.5.
Ranking candidates nearest-first therefore reproduces, to a large degree, ranking them by how
small their own response is. Nothing here measures retrieval quality, and nothing here is a
comparison between retrieval families.

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
reaches median -0.330, on the far side of zero from energy's +0.276, and its per-query
correlations are essentially unrelated to magnitude match (Pearson r = +0.007 across the 103
queries). A median rho of +0.791 says the two candidate ORDERINGS largely agree; it does not say
that energy's external win is a magnitude effect, and the control refuses that reading. Running
this module standalone prints both functional-oracle medians from the file, so the paragraph above
can be checked rather than believed.

THE LEFT TAIL IS REAL AND IS DRAWN
----------------------------------
"Largely" is a statement about the MEDIAN, not about every query. Eight of the 103 queries sit at
or below zero (minimum -0.242): for those, the energy distance carries no candidate-magnitude
information at all. The rug beneath the density plots all 103 queries individually and the zero
rule is drawn, so those eight are visible and countable rather than smoothed away by the density.
_assert_claims checks the median, the sign counts and the size of the left tail, so the hedge
cannot quietly stop being a hedge.

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
   unreflected estimate already peaks at rho = +0.92 and the top histogram bin holds those 41
   queries. No reflection is applied at the lower end, where the nearest datum is 1.2 rho units
   from the -1 bound. Scott's bandwidth here is 0.134, wide enough to smooth the gap between the
   left-tail queries and the main mass; the rug is the unsmoothed sample and shows that gap.
3. NO CELL-LINE ENCODING. The three lines agree closely (median rho A549 +0.762, K562 +0.885,
   MCF7 +0.771) and no claim here is per line, so the rug is one undifferentiated grey series.
   Drawing 103 marks in three shapes on a 2.48 in axis would add ink a reader cannot resolve.
4. THE VERTICAL AXIS IS A DENSITY AND SAYS SO. It is normalised to a peak of 1 and carries no
   claim, so it gets no ticks. It is labelled "query density" rather than "queries" because the
   height is not a count of anything and an untick-ed axis labelled with the sample unit invites
   a reader to read it as one. Note that fig3_assemble.PADS reserves 0.72 in on this panel's left
   for "a rotated label plus numeric ticks"; roughly half of that is unused here.
5. The queries within one cell line share a candidate pool, so the 103 values are not independent.
   This panel therefore quotes no p value and no confidence interval, only the observed median and
   counts. Panel i states the same pseudo-replication caveat for the paired test it does report.

Run standalone: python fig3m.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fig3_style import (FAINT, HAIRLINE, LW_HAIR, LW_LINE, MS_DOT, PT_ANNOT,  # noqa: E402
                        REPO, SHARED, SUBTLE, TEXT, bare_axes, title, zero_rule)

SRC = os.path.join(REPO, "figures", "source_data", "fig3hi_class_c_potency.csv")
FUNCTIONAL = os.path.join(REPO, "figures", "source_data", "fig3hi_class_c_functional.csv")
COL = "energydist_vs_candmag_rho"

N_QUERIES = 103             # panel l reads the same file and states the same n; keep them equal

RHO_BOUND = 1.0             # Spearman rho cannot exceed this; the density is reflected about it
XLO, XHI = -0.38, 1.02      # the view; asserted below to contain every observation
YTOP = 1.32                 # density peak is normalised to 1.0, so this is the free label band
RUG_TOP, RUG_BOT = -0.16, -0.40

# The one phrase this panel states over itself: what a median of +0.791 MEANS. The subject is
# named because row 6's other panel draws four rankings, one of which IS the magnitude scalar,
# and an unowned "a magnitude ranking" could be read as that row rather than as energy's.
# "Largely" is load-bearing and is what _assert_claims checks: the median, the sign counts and
# the left tail, not every query.
TITLE_3M = "Energy ranks largely by magnitude"


def _load():
    if not os.path.exists(SRC):
        raise FileNotFoundError(
            f"{SRC} does not exist. Run analysis/class_c/class_c_potency_audit.py first.")
    d = pd.read_csv(SRC)
    if COL not in d.columns:
        raise KeyError(f"{SRC} has no column {COL!r}; columns are {list(d.columns)}")
    if len(d) != N_QUERIES:
        raise ValueError(f"{SRC} has {len(d)} queries; panel 3m, panel 3l and the caption all say "
                         f"{N_QUERIES}. Fix one or the other, do not draw the mismatch.")
    v = d[COL].to_numpy(dtype=float)
    if not np.isfinite(v).all():
        raise ValueError(f"{COL} carries {int((~np.isfinite(v)).sum())} non-finite values; "
                         "this panel will not drop rows silently")
    return d, v


def _assert_claims(v, med):
    """Refuse to draw a title, or hand a caption a number, the data no longer support.

    Every number this panel draws is computed at draw time, so the only way the ink can lie is if
    the drawn median stops meaning what the title says. The docstring and the caption go further
    than the ink does, quoting the sign counts and the size of the left tail, so those are checked
    here too: a data change must break the build rather than leave prose describing a panel that
    no longer looks like that.
    """
    n_pos = int((v > 0).sum())
    n_strong = int((v > 0.5).sum())
    n_le0 = int((v <= 0).sum())

    assert med >= 0.5, (
        f"{TITLE_3M!r} claims a strong positive coupling, but the median rho is {med:+.3f}. "
        "Retitle the panel from the data; do not keep the phrase.")
    assert n_pos > v.size / 2, (
        f"{TITLE_3M!r} claims the typical query is magnitude-ordered, but only {n_pos} of "
        f"{v.size} queries have rho > 0.")
    # The docstring's three counts. They are recomputed, never typed into the prose from memory.
    assert (n_pos, n_strong, n_le0) == (95, 78, 8), (
        f"the docstring and caption say 95 of 103 positive, 78 above +0.5 and 8 at or below "
        f"zero; the file now gives {n_pos}, {n_strong} and {n_le0}. Update the prose.")
    # "Largely" is a hedge and must stay one: a left tail that vanished would make the title
    # weaker than the data, and one that swelled would make it stronger.
    assert 0 < n_le0 < 0.25 * v.size, (
        f"{TITLE_3M!r} is hedged because {n_le0} of {v.size} queries carry no coupling. At this "
        "count the hedge no longer describes the panel; restate the claim from the data.")
    assert v.max() <= RHO_BOUND + 1e-9, (
        f"{COL} reaches {v.max():+.4f}; a Spearman rho cannot exceed {RHO_BOUND}, so the "
        "reflection boundary and the source file disagree.")
    assert XLO <= v.min() and v.max() <= XHI, (
        f"the view [{XLO}, {XHI}] clips the data [{v.min():+.3f}, {v.max():+.3f}]; widen the "
        "view rather than cropping queries out of the panel")


def _density(v, grid):
    """Scott-bandwidth Gaussian KDE, reflected about the rho = +1 bound. See docstring note 2."""
    kde = gaussian_kde(v)
    return kde(grid) + kde(2.0 * RHO_BOUND - grid)


def draw_3m(ax):
    d, v = _load()
    med = float(np.median(v))
    q1, q3 = (float(x) for x in np.percentile(v, [25, 75]))
    n_le0 = int((v <= 0).sum())
    _assert_claims(v, med)

    # --- the distribution: a half-violin standing on the baseline, SHARED grey ----------------
    grid = np.linspace(XLO, RHO_BOUND, 601)
    dens = _density(v, grid)
    dens = dens / dens.max()
    # Fill and outline are drawn separately so the polygon's closing verticals do not inherit
    # the curve's weight: the density is genuinely cut off at the rho = +1 bound, and a full-weight
    # stroke there reads as a drawn wall rather than as the edge of the statistic's range.
    ax.fill_between(grid, 0.0, dens, facecolor=FAINT, lw=0, zorder=3)
    ax.plot(grid, dens, color=SHARED, lw=LW_HAIR, zorder=4)
    ax.plot([RHO_BOUND, RHO_BOUND], [0.0, dens[-1]], color=HAIRLINE, lw=LW_HAIR, zorder=4)
    ax.plot([XLO, RHO_BOUND], [0.0, 0.0], color=HAIRLINE, lw=LW_HAIR, zorder=4)

    # --- the 103 queries themselves, unsmoothed, beneath it ------------------------------------
    ax.vlines(v, RUG_BOT, RUG_TOP, color=SHARED, lw=0.7, alpha=0.55, zorder=3)

    # --- zero is the datum: no coupling. Eight queries sit at or below it. ---------------------
    zero_rule(ax, at=0.0, vertical=True, color=SUBTLE, lw=0.8, zorder=4, ls=(0, (2.4, 1.8)))

    # --- one emphasised mark: the median, drawn through the whole panel and labelled ----------
    ax.plot([med, med], [RUG_BOT, YTOP - 0.20], color=TEXT, lw=LW_LINE, zorder=6,
            solid_capstyle="butt")
    ax.scatter([med], [0.0], s=MS_DOT, color=TEXT, zorder=7, linewidths=0)
    ax.text(med - 0.03, YTOP - 0.155, f"median {med:+.3f}", ha="right", va="center",
            fontsize=PT_ANNOT, color=TEXT)

    # --- frame -------------------------------------------------------------------------------
    bare_axes(ax, keep=("bottom",))
    ax.set_xlim(XLO, XHI)
    ax.set_ylim(RUG_BOT - 0.06, YTOP)
    ax.set_xticks([0.0, 0.25, 0.50, 0.75, 1.00])
    ax.set_xticklabels(["0", "0.25", "0.5", "0.75", "1"])
    ax.set_yticks([])
    # Two lines because one is 2.6 in wide on a 2.48 in axis. "the candidate's own" is the part a
    # reader must not lose: the correlation is with the CANDIDATE's response magnitude, not the
    # query's, and that is what makes nearest-first a magnitude ranking.
    ax.set_xlabel("Spearman " r"$\rho$" ": energy distance vs\nthe candidate's own response "
                  "magnitude", fontsize=PT_ANNOT, color=TEXT, labelpad=1.6, linespacing=1.18)
    # Two lines rather than one: "query density" set on a single line stands 0.62 in tall inside
    # a 0.64 in axes and reads as crowding it.
    ax.set_ylabel("query\ndensity", fontsize=PT_ANNOT, color=TEXT, labelpad=2.0,
                  linespacing=1.10)
    title(ax, TITLE_3M)

    return {"n": int(v.size), "median": med, "q1": q1, "q3": q3,
            "n_pos": int((v > 0).sum()), "n_at_or_below_zero": n_le0,
            "min": float(v.min()), "max": float(v.max()),
            "per_line_median": {ln: float(g[COL].median()) for ln, g in d.groupby("cell_line")}}


def _cross_endpoint():
    """Check the docstring's "this is not h's channel" paragraph against the functional file.

    The paragraph exists to stop a reader crediting energy's +0.276 to the coupling this panel
    draws, and it rests on two medians and one correlation that live in another file. They are
    verified here rather than asserted in draw_3m, because a panel must not refuse to render for
    a fact about a file it does not plot; the same split is what fig3l does.
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
    fig = plt.figure(figsize=(3.30, 1.26))
    ax = fig.add_axes([0.72 / 3.30, 0.38 / 1.26, 2.48 / 3.30, 0.64 / 1.26])
    st = draw_3m(ax)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "3m.png")
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
