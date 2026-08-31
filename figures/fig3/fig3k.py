"""PopRetrieve Figure 3 panel 3k: the queries the two Class-B evaluators would need.

WHAT THIS PANEL SHOWS
---------------------
Two evaluators, one row each, on a log query axis: the open marker is what was analysed, the
filled marker is what 80% power would take, and the arrow runs from the first to the second.
Minority-state coverage would reach 80% power at 45 queries and 191 were analysed, so its arrow
points LEFT and its null is a measurement. MoA-nDCG would need 20,844 and 143 were analysed, so
its arrow points RIGHT across two decades and its null is uninformative. The two studies start
from nearly the same place, 191 and 143 queries, so the two open markers land 0.11 in apart and
the only thing left to compare between the rows is the LENGTH of the two dumbbells. That length
is the panel: one arrow spans 0.6 of a decade and the other 2.2, a factor of 3.5 in length, and
_numbers asserts both.

Every number here is recomputed from the source files at draw time, and every relationship the
panel or its caption asserts is checked before anything is drawn.

WHAT CHANGED IN THE 2026-08-31 PASS, AND WHY
--------------------------------------------
A panel states no conclusion. Two pieces of text were cut and not replaced:

  * the phrase "Noise, not gap size, sets the cost", which was this panel's conclusion sentence
    set in 8.5 pt over the marks. It now opens the caption entry, where it costs no page space
    and can be qualified properly. fig3_style.title() is deleted and fig3_assemble refuses to
    build a figure whose panels draw text above PT_ANNOT, so it cannot come back smaller either.
  * the drawn line "vs coverage: gap 1.8x smaller, s.d. 12x larger", which was the caption's
    sentence in the panel's ink. The geometry states it instead: the two dumbbells share a
    starting neighbourhood and differ in length by 1.5 decades on a log axis, and a difference in
    required n that survives near-equal starting points and near-equal gaps is a difference in
    noise. The two ratios are still COMPUTED and still ASSERTED in _numbers, at the precision the
    caption prints them to, so the caption cannot outlive the files either. An assertion is the
    right place for a claim the reader is asked to take on the caption's word.

Removing the sentences returned 0.42 in to the six rows, 0.06 in of it to this panel. It is spent
on the marks: _bands now seats two number rows and two marker rows instead of three text rows and
two marker rows, so every seam grew from about 1.0 pt to about 3.5 pt and each dumbbell reads as
one object rather than as ink crowded against its label.

WHY THE STRATUM IS NAMED ON THE PANEL, NOT ONLY IN THE CAPTION
--------------------------------------------------------------
Because all four drawn numbers are that stratum's. power_analysis.csv holds Q4 rows and no
others, and the per-stratum n and gaps in divergence_stratified.csv differ enough that a reader
who took 191 and 143 for the study totals (765 and 600 queries) would have the wrong panel in
mind. The stratum also guards the caption's gap ratio, which is true inside Q4 and nowhere else:
MoA-nDCG's mean gap is -0.0822 (Q1), -0.0411 (Q2), -0.0205 (Q3), +0.0032 (Q4) and -0.0371 over
all 600 queries, so read without the stratum "gap 1.8x smaller" would invert a sign. Q4 is not a
flattering subset picked after the fact: it is the stratum the pre-specified gate names and the
one panel j draws. The noise claim does not have this problem, the s.d. ratio being 12.4 over all
queries and 9.3 to 18.1 across the four strata. _numbers asserts against divergence_stratified.csv
that Q4 really is the highest-divergence quartile and that its n match the power file, exactly as
panel j does, so the x label cannot outlive the files.

SOURCE
------
results/exp17_true_divergence_subset/power_analysis.csv        the two Q4 rows that are drawn
results/exp17_true_divergence_subset/divergence_stratified.csv read only to ASSERT that Q4 is the
    highest-divergence quartile and that its per-metric n agree
Verified: minority_state_coverage n=191, mean gap +0.005608, s.d. 0.013496, n80 = 45.46;
moa_ndcg n=143, mean gap +0.003166, s.d. 0.163170, n80 = 20844.32.

JUDGEMENT CALLS A READER COULD DISAGREE WITH
--------------------------------------------
1. n80 = 20,844 is printed in full, not rounded. It is a point estimate built on an s.d.
   estimated from 143 queries, so its own uncertainty is wide and the honest reading is the
   order of magnitude rather than the exact integer. It is printed in full anyway because
   "roughly 20,000" reads as an idiom and the point is that the number is off the scale of any
   study of this kind. power_analysis.csv marks this row data_sufficient = False; that flag is
   about the MoA-nDCG null being uninformative, and it is the panel's message, not a caveat
   against it.
2. Both rows are drawn in SHARED grey. Neither is a retrieval method: both are evaluators
   judging the same rankings, so neither may take the blue or the orange. The retired Extended
   Data version (edfigs/ed_panels.draw_ed2b) drew MoA-nDCG in the mean-retrieval orange and
   minority coverage in the population blue, which said these were two methods. They are not.
3. Required versus observed is carried by FILL and by the arrow's direction, never by hue: open
   marker, the queries analysed; filled marker, the queries needed. The arrow runs from what
   exists to what would be needed, so a leftward arrow is an over-powered test. The head stops
   clear of the filled marker rather than inside it: at MS_DOT the marker is 2.9 pt in radius
   and a head tucked under it left only its base flare showing, which is the one cue the
   required-versus-observed reading rests on.
4. NOTHING WAS ADDED to tie the two open markers together, and this is the call most open to
   disagreement. Comparing two lengths presumes a common origin, so two candidates were drawn and
   rejected: a dotted hairline between the open markers, which crossed the 143 label and read as
   a scratch, and a pale vertical band spanning 143 to 191, which was tidy but is a mark a reader
   has to ask about, and this pass is about spending less ink on explanation rather than more.
   The two open markers are already 0.11 in apart on a 2.80 in axis, which the eye reads without
   help. What survives from the attempt is the assertion: _numbers now checks that the two n stay
   within a factor of 1.5, so if the two studies ever diverged in size the panel would fail rather
   than quietly invite a length comparison that no longer means what it means today.
5. The panel no longer prints the gap and s.d. ratios, so the "why" behind the two lengths is
   the caption's to carry. A reader who only looks at the marks learns that one study is
   over-powered and the other is 146-fold short, which is this panel's evidence; the
   decomposition into noise and effect size is an argument, and arguments belong in the legend.
   The arithmetic behind it is real: n80 goes as (s.d. / gap)^2, the variance ratio is 146 and
   the squared gap ratio is 3.1, so noise accounts for two orders of magnitude of the 458-fold
   difference in cost and the gap for half an order. _numbers asserts that dominance.
6. The x label says "needed for 80% power" rather than the bare "needed" the fill key would take.
   The four extra characters are the definition of the filled marker: without the power target,
   20,844 is a number with no operation behind it, and the rule that lets a panel keep its
   necessary statistics is the rule that keeps this one. It is written from TARGET_POWER, so the
   percentage cannot drift from the formula that produced the marker.
7. The x axis is queries on a log scale, and 45 versus 20,844 is only legible on one. A log
   axis flatters nothing here: it makes a 458-fold difference look like the two decades it is.
8. The two rows are not computed on the same queries: MoA-nDCG is undefined for 48 of the 191,
   so it is a 143-query subset of them. Both n are on the panel for that reason. It is also why
   the s.d. comparison is between two nested samples rather than one paired one.

Run standalone: python fig3k.py
"""
from __future__ import annotations

import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import norm

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fig3_style import (LW_LINE, MS_DOT, PT_ANNOT, PT_SMALL, PT_TICK, REPO,  # noqa: E402
                        SHARED, SUBTLE, TEXT, bare_axes)

SRC = os.path.join(REPO, "results", "exp17_true_divergence_subset", "power_analysis.csv")
STRAT_SRC = os.path.join(REPO, "results", "exp17_true_divergence_subset",
                         "divergence_stratified.csv")

STRATUM = "Q4"      # the label exp17 gives the top quartile of true_divergence
# The two Q4 rows, top row first. Names are the panel's, the keys are the file's. The drawn name
# is panel j's, verbatim: the two panels share a row and must not name one metric two ways.
METRICS = [("minority_state_coverage", "minority-state\ncoverage"), ("moa_ndcg", "MoA-nDCG")]

ALPHA = 0.05        # two-sided, the convention power_analysis.csv was computed under
TARGET_POWER = 0.80

# The view, and the decades labelled inside it. Both are asserted against the data in _numbers:
# a marker outside the view would be clipped and the panel would draw a number it does not show.
XLIM = (30.0, 45000.0)
XTICKS = (100, 1000, 10000)

# Marker radius in points, plus half its edge. The dumbbell ends, the label offsets and the arrow
# shrink all measure from it, so MS_DOT is the single place the marker size is set.
R_PT = (MS_DOT / np.pi) ** 0.5 + 0.45


def _numbers():
    """Read the Q4 power rows and verify every relationship the panel and its caption assert.

    Returns one dict per metric, in METRICS order, plus the two ratios the CAPTION prints. The
    ratios are no longer drawn, and they are checked here anyway: the panel's geometry is the
    reader's evidence for them, so if the files stopped supporting them the geometry would be
    making a claim the caption could no longer keep.
    """
    for path in (SRC, STRAT_SRC):
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"Figure 3k needs {path}, which does not exist. Run exp17 "
                f"(the true-divergence subset power analysis) before rebuilding this panel; this "
                f"module will not invent a number.")
    pw = pd.read_csv(SRC)
    st = pd.read_csv(STRAT_SRC)
    st = st[st["stratum"] != "ALL"]
    rows = []
    for key, _ in METRICS:
        sub = pw[(pw["metric"] == key) & (pw["stratum"] == STRATUM)]
        if len(sub) != 1:
            raise KeyError(
                f"power_analysis.csv holds {len(sub)} {STRATUM} rows for {key!r}, expected 1")
        r = sub.iloc[0]
        rows.append({"key": key, "n": int(r["n"]), "gap": float(r["observed_mean_gap"]),
                     "sd": float(r["sd_gap"]), "n80": float(r["n_for_80pct_power"]),
                     "power": float(r["achieved_power"]),
                     "sufficient": bool(r["data_sufficient"])})

        # The x label calls these the highest response-divergence quartile, and all four drawn
        # numbers are that stratum's: read as study totals they would be wrong, and the caption's
        # gap ratio would be sign-reversed. So the words are checked against the file that
        # defines the strata.
        sub_st = st[st["metric"] == key]
        top = str(sub_st.loc[sub_st["divergence_median"].idxmax(), "stratum"])
        assert top == STRATUM, (
            f"{key}: the highest-divergence stratum is {top}, not the {STRATUM} whose numbers "
            f"this panel draws under the words 'highest response-divergence quartile'")
        n_st = int(sub_st.loc[sub_st["stratum"] == STRATUM, "n"].iloc[0])
        assert n_st == rows[-1]["n"], (
            f"{key}: n disagrees between the two exp17 files, {n_st} vs {rows[-1]['n']}; the "
            f"panel prints one of them as the queries analysed")

    # The stored n80 must be the paired-test sample size for THIS gap and THIS s.d. A stale
    # column would otherwise be drawn as if it were current.
    zc = norm.ppf(1.0 - ALPHA / 2.0)
    z = zc + norm.ppf(TARGET_POWER)
    for r in rows:
        want = (z * r["sd"] / abs(r["gap"])) ** 2
        assert abs(want - r["n80"]) / r["n80"] < 5e-3, (
            f"{r['key']}: n_for_80pct_power = {r['n80']:.1f} in the file, but gap "
            f"{r['gap']:.6f} and s.d. {r['sd']:.6f} imply {want:.1f}. The column is stale.")
        # achieved_power is not drawn, but data_sufficient is, in the shape of the arrow's
        # direction and of the reading the docstring gives it, and this is the number behind
        # that flag. Two-sided, both tails, the convention ALPHA is set under.
        d = abs(r["gap"]) / (r["sd"] / np.sqrt(r["n"]))
        want_p = float(norm.cdf(d - zc) + norm.cdf(-d - zc))
        assert abs(want_p - r["power"]) < 1e-3, (
            f"{r['key']}: achieved_power = {r['power']:.4f} in the file, but n {r['n']}, gap "
            f"{r['gap']:.6f} and s.d. {r['sd']:.6f} imply {want_p:.4f}. The column is stale.")

    cov, moa = rows
    # The direction each arrow points, and the reading the docstring gives it.
    assert cov["n80"] < cov["n"], (
        "minority-state coverage is drawn as over-powered; the file disagrees")
    assert moa["n80"] > moa["n"], "MoA-nDCG is drawn as under-powered; the file disagrees"
    # The file's own verdict on whether each null can be read.
    assert cov["sufficient"] and not moa["sufficient"], (
        "the panel says the coverage null is a measurement and the MoA-nDCG null is not; "
        "power_analysis.csv marks data_sufficient "
        f"{cov['sufficient']} / {moa['sufficient']}")
    # The panel asks the reader to compare the LENGTH of two dumbbells, which is only a
    # comparison of cost if the two start from about the same place. They do, 191 queries and
    # the 143 of them MoA-nDCG is defined on, and the two open markers land 0.11 in apart on the
    # drawn axis. If the two studies ever diverged in size, length would stop being the thing to
    # read and the panel would need to say so.
    start_ratio = max(cov["n"], moa["n"]) / min(cov["n"], moa["n"])
    assert start_ratio < 1.5, (
        f"the two dumbbells are drawn to be compared by length, but the studies now differ "
        f"{start_ratio:.2f}-fold in size ({cov['n']} vs {moa['n']}), so the two lengths are no "
        f"longer a comparison of required n alone")

    # The two lengths the reader is asked to compare, in the units the docstring quotes them in:
    # on a log axis a dumbbell is log10 of its own n ratio. Quoted geometry is checked like a
    # drawn number, because it is the sentence the panel was allowed to stop printing.
    dec = [abs(np.log10(r["n80"] / r["n"])) for r in rows]
    assert 0.58 <= dec[0] <= 0.68 and 2.10 <= dec[1] <= 2.25, (
        f"the docstring reads the two dumbbells as 0.6 and 2.2 decades long, a factor of 3.5; "
        f"they are {dec[0]:.2f} and {dec[1]:.2f} decades, a factor of {dec[1] / dec[0]:.1f}")

    sd_ratio = moa["sd"] / cov["sd"]
    gap_ratio = cov["gap"] / moa["gap"]
    # The two ratios the CAPTION prints, at the precision it prints them to. The panel draws
    # neither; it draws the geometry that is the evidence for both.
    assert 11.5 <= sd_ratio < 12.5, f"the caption says 's.d. 12x larger'; it is {sd_ratio:.2f}x"
    assert 1.75 <= gap_ratio < 1.85, f"the caption says 'gap 1.8x smaller'; it is {gap_ratio:.2f}x"
    # The caption: noise, not gap size, is what sets the required n. n80 scales as (sd/gap)^2, so
    # the two contributions are sd_ratio^2 and gap_ratio^2, and the first must dominate.
    assert sd_ratio ** 2 > 10.0 * gap_ratio ** 2, (
        f"the caption claims noise dominates the cost, but the variance ratio "
        f"{sd_ratio ** 2:.0f} does not dominate the squared gap ratio {gap_ratio ** 2:.1f}")
    # The 458-fold the docstring quotes, so the prose cannot outlive the file either.
    cost_ratio = moa["n80"] / cov["n80"]
    assert 457.5 <= cost_ratio < 459.5, (
        f"the module docstring says the two required n differ 458-fold; they differ "
        f"{cost_ratio:.1f}-fold")
    # The view is fixed in XLIM, so a marker that moved outside it would be clipped and the panel
    # would print a number with nothing under it. The labelled decades must be inside it too.
    for r in rows:
        for what, value in (("queries analysed", float(r["n"])), ("n for 80% power", r["n80"])):
            assert XLIM[0] < value < XLIM[1], (
                f"{r['key']}: {what} is {value:,.0f}, outside the drawn view {XLIM}. The marker "
                f"would be clipped and its label would sit over empty axis. Widen XLIM.")
    assert all(XLIM[0] < t < XLIM[1] for t in XTICKS), f"XTICKS {XTICKS} leave the view {XLIM}"
    return rows, sd_ratio, gap_ratio


def _bands(ax):
    """Split the axes height into balanced bands, in points, and return the two row centres.

    The panel holds two number rows and two marker rows in 0.63 in. Placing them in data units
    left one seam at 0.5 pt and another at 4 pt, which looks like a mistake rather than a layout.
    The height is therefore divided at draw time: the ink is fixed, the five seams share what is
    left equally, and the panel stays balanced if the assemble ledger ever changes the row height.
    This is where the 0.06 in the deleted conclusion phrase returned to the row is spent, together
    with the line the third text row used to take: the seams went from about 1.0 pt to about
    3.5 pt. Nothing here shrinks type; if the height ever falls far enough for a seam to vanish,
    the assertion below says so instead of silently overlapping.
    """
    fig = ax.get_figure()
    h_pt = ax.get_position().height * fig.get_size_inches()[1] * 72.0
    r_pt = R_PT                                    # marker radius plus half its edge
    ink = 2 * PT_ANNOT + 4 * r_pt                  # two number rows, two marker rows
    gap = (h_pt - ink) / 5.0                       # top margin, three seams, bottom margin
    assert gap > 0.6, (
        f"panel k has {h_pt:.1f} pt of axes height and needs {ink + 5 * 0.6:.1f} pt to seat two "
        f"dumbbells and their four number labels. Cut a label into the caption; do not lower "
        f"the size.")
    top = h_pt - gap - PT_ANNOT - gap - r_pt       # centre of the upper marker row
    bottom = top - 2 * r_pt - 2 * gap - PT_ANNOT   # centre of the lower marker row
    return top / h_pt, bottom / h_pt, r_pt + gap


def draw_3k(ax):
    """Queries needed for 80% power against queries analysed, one dumbbell per evaluator."""
    rows, _sd_ratio, _gap_ratio = _numbers()

    ax.set_xscale("log")
    ax.set_xlim(*XLIM)
    ax.set_ylim(0.0, 1.0)                          # the y axis is a layout, not a quantity
    y_top, y_bot, off = _bands(ax)

    for r, y in zip(rows, (y_top, y_bot)):
        # From what exists to what would be needed: a leftward arrow is an over-powered test.
        # mutation_scale is set rather than inherited: matplotlib would otherwise size the head
        # from rcParams["font.size"], so the standalone preview and the composite would draw two
        # different heads. shrinkB clears the filled marker, so the whole head is visible; tucked
        # under it, only the base flare showed and the direction had to be guessed.
        ax.annotate("", xy=(r["n80"], y), xytext=(r["n"], y),
                    arrowprops=dict(arrowstyle="-|>,head_length=0.34,head_width=0.17",
                                    color=SHARED, lw=LW_LINE, mutation_scale=PT_ANNOT,
                                    shrinkA=R_PT + 0.4, shrinkB=R_PT + 0.4))
        ax.scatter([r["n"]], [y], s=MS_DOT, facecolor="white", edgecolor=SHARED,
                   linewidths=0.9, zorder=4)
        ax.scatter([r["n80"]], [y], s=MS_DOT, facecolor=SHARED, edgecolor=SHARED,
                   linewidths=0.9, zorder=4)
        for value, text in ((r["n"], f"{r['n']:d}"), (r["n80"], f"{r['n80']:,.0f}")):
            ax.annotate(text, xy=(value, y), xytext=(0, off), textcoords="offset points",
                        ha="center", va="bottom", fontsize=PT_ANNOT, color=TEXT)

    bare_axes(ax, keep=("bottom",))
    ax.set_xticks(list(XTICKS))
    # Plain integers, not 10^n: a mathtext exponent prints at 0.7x nominal and this figure's
    # floor is 6.5 pt, so the decade labels would have to be set at 9.3 pt to be legal. The
    # strings are formatted from the tick values, so a changed view cannot mislabel a decade.
    ax.set_xticklabels([f"{t:,d}" for t in XTICKS])
    ax.set_xticks([], minor=True)
    ax.set_yticks([y_top, y_bot])
    ax.set_yticklabels([label for _, label in METRICS], fontsize=PT_TICK, color=TEXT,
                       linespacing=1.15)
    ax.tick_params(axis="y", length=0, pad=2.0)
    # pad 1.6, not the house 3.5: the two-line x label needs the 2 pt to stay inside the panel
    # box that fig3_assemble gives this row.
    ax.tick_params(axis="x", labelsize=PT_TICK, pad=1.6)
    # Line 1 names the quantity and the stratum, in panel j's words. The stratum is not
    # decoration: all four drawn numbers are Q4's, and taken for study totals they would be
    # wrong. Line 2 is the fill key, written from TARGET_POWER so the percentage cannot drift
    # from the formula that placed the filled markers.
    ax.set_xlabel(f"queries, highest response-divergence quartile (log scale)\n"
                  f"open, analysed; filled, needed for {TARGET_POWER:.0%} power",
                  fontsize=PT_SMALL, color=SUBTLE, linespacing=1.15, labelpad=1.5)
    return ax


if __name__ == "__main__":
    # Reproduce the printed geometry exactly: the panel box fig3_assemble gives k is 3.70 in
    # wide and 0.17 + 1.01 in tall (letter block plus row), with a 0.80 in left pad and a
    # 0.38 in bottom pad, so the axes is 2.80 x 0.63 in and the preview is what the composite
    # prints. The row is 0.06 in taller than before this pass, and the letter block 0.07 in
    # shorter, because no panel states a conclusion over itself any more.
    BOX_W, BOX_H, LEFT, BOTTOM, AX_W, AX_H = 3.70, 1.18, 0.80, 0.38, 2.80, 0.63
    fig = plt.figure(figsize=(BOX_W, BOX_H))
    ax = fig.add_axes([LEFT / BOX_W, BOTTOM / BOX_H, AX_W / BOX_W, AX_H / BOX_H])
    draw_3k(ax)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "3k.png")
    fig.savefig(out, dpi=300)
    print(f"wrote {out}")
