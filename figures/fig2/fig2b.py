"""PopRetrieve Figure 2 panel 2b: the per-task advantage, and the one task where it reverses.

WHAT THIS PANEL CLAIMS
----------------------
Exactly one thing, and it is a restraint: the SHAPE of the three-tier ladder in panel a is not the
same on every task. Restoring response magnitude to a mean signature buys +0.52 on the controlled
mixture and +0.41 across cell lines and +0.01 on Frangieh; adding the full distribution on top of
it buys +0.03, +0.09 and -0.03. On Frangieh, the only natural biological dataset here, the ladder
is flat and mean L2 is the best of all nine scorers. Those six numbers are recomputed and redrawn
from the source file on every build. The claim is about response matching under the retrieval
objective and nothing else; whether the Frangieh reversal matters biologically is Figure 3's
question, not this panel's.

SOURCE
------
results/exp08_signature_baselines/summary_by_task.csv, the only file this module reads. Every
number drawn (the three signed differences, the three n, all 24 Hit@1 values) is computed from
that file at draw time. Nothing plotted is typed as a literal, and every relationship the drawn
labels assert is asserted in code first, so a data change breaks the build rather than quietly
producing a false panel:

  * mean_cosine and cmap_cosine are numerically identical on every task, which is why the orange
    marker is labelled "mean cosine" while cmap_cosine sits in the grey background: they are the
    same score, so drawing both at full weight would double-count one representation.
  * energy beats mean cosine on both constructed tasks and loses on Frangieh, which is what the
    three signed difference labels say, in sign and in size.
  * on Frangieh, mean cosine is the maximum over ALL EIGHT scorers, which is what "mean wins"
    says. If it were only beating energy, that label would be too strong and the assert fires.
  * that reversal is at most SMALL_REVERSAL wide, which is what judgement call 7 tells the reader.
  * the background column holds exactly six scorers, which is the number printed beside it.
  * the two protagonists still belong to the families whose colours they are drawn in, as
    fig2_style classifies them and panel a draws them.
  * no Hit@1 value falls outside the fixed y range, so no dot is clipped without a trace.

THE RESTRAINT PASS (2026-08-31)
-------------------------------
One piece of text is gone: the phrase "Large on both mixtures, reversed on Frangieh", set over the
axes at PT_TITLE by the fig2_style.title() helper that this pass deleted. It is not preserved
anywhere on the panel. It was a conclusion, the figure's panels carry evidence and its caption
carries the argument, and the caption entry already carries what the phrase said, in numbers
rather than in the word: "The advantage is +0.56 on the controlled mixture and +0.50 on the
cross-line mixture, and reverses to -0.02 on Frangieh". The word "large" itself now appears in no
caption and on no panel; it survives as prose in this module's opening claim and in
figures/fig2/README.md's panel-b row. See the comment block in fig2_style where title() used
to be.

Nothing else moved. The panel BOX lost 0.09 in from the top, all of it the band the phrase sat in
above the axes; the axes rect is 2.63 x 1.08 in, exactly what it was, so every constant tuned
against it (XLIM, LABEL_DX, the n line's -0.275, the separator's 0.52 top) still holds against the
measurement that set it and none was rescaled. The standalone canvas below was re-cut from 1.84 to
1.75 in so that running this file alone reproduces the printed box rather than the old one.

What the deletion cost, and what pays for it: the phrase named the two mixture gains "large" and
the Frangieh result "reversed". The marks say both without it. Large is the two connectors that
climb most of the axis with "+0.56" and "+0.50" written beside them; reversed is the one connector
that falls, its "-0.02" set bold, and "mean wins" under it. What is genuinely no longer on the
panel is the word "large" itself, which was a judgement about the size and not a reading of it.
LARGE_GAIN survives the phrase deliberately: it now guards the two prose statements named
above rather than a drawn label, so the word cannot outlive the numbers just because it moved
off the panel.

JUDGEMENT CALLS A READER COULD REASONABLY DISAGREE WITH
-------------------------------------------------------
1. The two protagonists are dodged horizontally rather than plotted at the same x. A shared x
   with a vertical connector is the more usual construction, but at this panel's printed scale
   one Hit@1 unit is about 1.2 in, so the Frangieh pair is 0.03 in apart vertically and the two
   markers would sit on top of each other at exactly the task the panel exists to show. The dodge
   costs the reader a small amount of alignment and buys the reversal being visible at all.
2. Mean is drawn LEFT and population RIGHT, so a rising connector means the population score
   gains. That orientation is a choice; it makes the Frangieh connector the only one that falls.
3. The other six scorers are drawn as one faint column per task with no per-scorer identity. They
   are benchmark context, and identifying them here would compete with the three differences.
   Panel a is where the nine scorers are individually named and ranked.
4. cmap_cosine is kept in that background column even though it is identical to the orange mean
   marker, so the column honestly holds "the other six scorers". Its dot therefore sits at exactly
   the orange marker's height, one dodge step to the left, on all three tasks.
5. The constructed-versus-natural distinction is carried quietly, by three things that cost no
   space: the task names ("... mixture" twice, "Frangieh" once), the word "natural" on Frangieh's
   n line, and a hairline group separator between the mixtures and Frangieh. A labelled bracket
   rule under the axis would be more explicit, but the panel's bottom band is 0.50 in and already
   holds a two-line task name and the n line; a fourth row would have pushed text below the
   figure's 6.5 pt floor or outside the panel box.
6. "mean wins" and the bold "-0.02" beside it are now the heaviest ink on the panel, with the
   conclusion phrase that used to outweigh them gone. That is deliberate and it is the one place
   the panel points: Frangieh is the task this panel exists to show. The Frangieh MARKERS are
   still drawn at exactly the same size and weight as every other task's: size is not a channel
   this figure uses, and enlarging the winning marker would read as a larger value.
7. The reversal is written as -0.02 and it is small in absolute terms: 2 of Frangieh's 90 queries.
   This panel draws no interval, because the source table carries none, so "mean wins" is a
   statement about the point estimates that are drawn and must not be read as a tested difference.
   The magnitude is asserted below so that the word cannot outlive a number that stays this small.

WHAT THIS PANEL LEARNED THE HARD WAY, AND MUST NOT UNLEARN
-----------------------------------------------------------
  * It is not a colour-scaled heatmap. A heatmap hides a 0.02 reversal; a paired layout with the
    signed difference written out cannot.
  * The connector between the pair is neutral grey. A coloured stem was once the heaviest ink on
    the panel, and it duplicated what the two endpoint markers already say.
  * The n line is placed in the xaxis transform at a NEGATIVE y. At +0.128 it sat 13% up the axes,
    on top of the controlled-task data.
  * No colour is declared in this file: every hue comes from fig2_style, so that one edit there
    recolours the deck. The two point sizes are MS_DOT from fig2_style for the marks that carry
    the claim, and the module-level MS_CONTEXT below for the background column, which is the one
    size no other panel needs.
  * The difference labels once sat at a wider offset, where "+0.50" cleared the group separator by
    0.001 in and "+0.56" was closer to the NEXT task's scorer column than to its own pair. The
    offset is now the measured value; see the note on LABEL_DX.

Run standalone: python fig2b.py
"""
from __future__ import annotations

import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# The vocabulary is frozen in fig2_style; this file declares no colour of its own, and takes both
# the marker size that carries a claim and the two scorer names it prints in ink from there. Every
# panel used to carry its own copy of the palette, which made "one edit recolours the deck" untrue.
from fig2_style import (FAINT, HAIRLINE, LW_HAIR, LW_LINE, MAGNITUDE, MEAN,  # noqa: E402
                        MS_DOT, POP, PT_ANNOT, PT_SMALL, PT_TICK, SCORERS, SHARED,
                        SUBTLE, TEXT, TIER)

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC = "results/exp08_signature_baselines/summary_by_task.csv"

# task key -> (tick label, is a constructed mixture rather than a natural dataset)
TASKS = [("controlled", "Controlled\nmixture", True),
         ("crossline", "Cross-line\nmixture", True),
         ("frangieh", "Frangieh", False)]
# THREE protagonists since 2026-09-03, not two. The panel used to draw energy against mean
# cosine, which is a comparison that cannot separate response magnitude from population
# structure; with the magnitude control in it, the same three tasks split into three regimes
# instead of into a win and a loss. See docs/phase2/FIG2_MAGNITUDE_CONTROL_VERDICT.md.
DIR_METHOD, MAG_METHOD, POP_METHOD = "mean_cosine", "mean_l2", "global_energy"
PROTAG = (DIR_METHOD, MAG_METHOD, POP_METHOD)
PROTAG_COLOUR = {DIR_METHOD: MEAN, MAG_METHOD: MAGNITUDE, POP_METHOD: POP}
CONTEXT = ["coverage_mean", "coverage_worst", "pca_dist", "pca_mean", "cmap_wtcs", "cmap_cosine"]
MEAN_METHOD = DIR_METHOD    # kept: the identical-to-CMap assertion below is about this scorer
ANCHOR = "controlled"       # the slot the two direct labels hang off; see the note where drawn

# The word "large" is no longer drawn: it survives in this module's opening claim and in
# figures/fig2/README.md's panel-b row, and it stands on this threshold in both. It is a choice,
# not a measurement, so it is named and asserted rather than left implicit: both mixture gains
# currently clear it, at +0.56 and +0.50. The assert outlives the drawn phrase because prose off
# the panel goes stale exactly as easily, and nothing else would catch it. The manuscript caption
# for b states the three differences as numbers and uses no such word, so it needs no guard here
# beyond the three drawn values themselves.
LARGE_GAIN = 0.40
# The reversal is asserted to stay this small, so nobody can inherit the restrained wording of the
# panel for a gap that has grown into a finding. 0.05 of 90 queries is between 4 and 5 of them.
SMALL_REVERSAL = 0.05

# Hard x range. The right end is not slack: the widest thing in the panel's right margin is the
# second line of the Frangieh block, "mean wins", which is wider than the number it sits under, and
# 2.66 is the smallest end that keeps it inside the axes with air to spare (0.027 in). At 2.62 it
# hung 0.002 units past the axis.
XLIM = (-0.58, 2.66)
# Drops below the axis, in INCHES. They were 0.40 and 0.275 of the axes height, which printed as
# 0.432 and 0.297 in at the 1.08 in axes this panel had until 2026-09-01; those printed values are
# what is preserved here. Both must stay inside fig2_assemble's 0.50 in bottom pad for b.
SEP_DROP_IN, N_LINE_IN = 0.43, 0.30

# Hard y range, so the axis does not breathe with the data. Every value drawn is asserted to lie
# inside it: a scorer that fell below the floor would otherwise be clipped in silence and the
# background column would quietly show five dots under a label that says six.
YLIM = (0.10, 1.02)

# Within-slot x offsets, in data units. One unit is about 0.82 in printed, so these are, left to
# right: the background column, the mean marker, the population marker, and the difference label.
# LABEL_DX is the tightest of the four and is a measured compromise, not a taste: it has to clear
# the population marker on Frangieh, where the pair is flat and the label cannot sit between the
# two dots, and it must not push the label into the next task. At 0.30 the Frangieh label clears
# the blue marker by 0.042 in, "+0.50" clears the group separator by 0.029 in, and "+0.56" sits
# 0.062 in from its own connector against 0.093 in from the next task's scorer column, so every
# label is nearer its own pair than its neighbour's data. At the 0.335 this once used, that last
# ratio was inverted and "+0.50" touched the separator.
# Four columns per task slot now: the background cloud, then the three protagonists in tier
# order, then the two step labels. One unit is about 0.82 in printed.
CLOUD_DX, DIR_DX, MAG_DX, POP_DX, LABEL_DX = -0.42, -0.20, -0.02, 0.16, 0.32
MS_CONTEXT = 7              # the background column: a quarter of MS_DOT's area, read as a group


def draw_2b(ax):
    """Per-task Hit@1: the direction/magnitude/distribution ladder, over the other six scorers."""
    # EVERYTHING BELOW THE AXIS IS MEASURED IN INCHES, since 2026-09-01. The separator rule and
    # the n line were positioned in AXES FRACTION on the xaxis transform, so their descent below
    # the axis was 0.40 and 0.275 of the axes HEIGHT. That was invisible while the height never
    # moved. When this panel went from a 1.08 in axes to 2.04 in, the separator dropped 0.816 in
    # against a 0.50 in pad and hung 0.316 in into the row below, and no gate could see it:
    # _assert_floor and _assert_no_titles read font sizes, not positions. fig2a had the same
    # defect and lost it on 2026-08-31; this is the same fix, one panel later.
    fig_w, fig_h = ax.figure.get_size_inches()
    ax_h = ax.get_position().height * fig_h
    def _below(inches: float) -> float:
        """Inches below the axis -> the negative axes fraction the xaxis transform wants."""
        return -inches / ax_h
    sbt = pd.read_csv(os.path.join(REPO, SRC))
    hit = sbt.pivot_table(index="method", columns="task", values="hit@1")
    nq = sbt.pivot_table(index="method", columns="task", values="n_queries")
    tasks = [t for t, _, _ in TASKS]
    assert set(hit.index) == set(list(PROTAG) + CONTEXT), \
        f"the nine scorers of this comparison changed: {sorted(hit.index)}"
    assert set(hit.columns) == set(tasks), f"the three tasks changed: {sorted(hit.columns)}"
    # The background column is labelled "six other scorers" in ink. Six is a drawn number.
    assert len(CONTEXT) == 6, f"the background column no longer holds six scorers: {len(CONTEXT)}"
    # The three protagonists are coloured by TIER, which fig2_style owns and panel a draws the
    # same way. A scorer reclassified there must not keep its old hue here.
    assert [TIER[m] for m in PROTAG] == ["direction", "magnitude", "population"], \
        f"2b's three protagonists are no longer one per tier: {[TIER[m] for m in PROTAG]}"
    # Nothing may fall outside the fixed y range, or it would be clipped without a trace.
    assert hit.values.min() >= YLIM[0] and hit.values.max() <= YLIM[1], \
        f"a Hit@1 value is outside the fixed y range {YLIM}: [{hit.values.min()}, {hit.values.max()}]"
    # mean cosine and the CMap cosine baseline apply the same operation to the same collapsed
    # signature and score identically: Spearman rho = 1.000 over 54,180 query-candidate scores,
    # measured in panel f (it was Extended Data Fig. 1 until the ED deck was retired, and now sits
    # in the same float as the claim). The orange marker is labelled "mean cosine" only because of
    # that, so it has to be true before the label is drawn.
    assert np.allclose(hit.loc[MEAN_METHOD, tasks].values, hit.loc["cmap_cosine", tasks].values), \
        "mean_cosine and cmap_cosine are no longer identical; relabel the orange marker in 2b"
    # n is a property of the task, not of the scorer; the n line below each tick says so.
    assert (nq.nunique(axis=0) == 1).all(), "n_queries differs between scorers within a task"

    v = {m: hit.loc[m, tasks].astype(float) for m in PROTAG}
    mag_step = v[MAG_METHOD] - v[DIR_METHOD]      # what response magnitude buys
    dist_step = v[POP_METHOD] - v[MAG_METHOD]     # what the rest of the distribution buys
    # The three regimes this panel exists to show, asserted so none can outlive the data.
    assert (mag_step[["controlled", "crossline"]] > LARGE_GAIN).all(), (
        f"the magnitude step on the two mixtures is no longer above {LARGE_GAIN}; it is "
        f"{mag_step.to_dict()}, and this module's opening claim says it is the large one")
    assert (dist_step[["controlled", "crossline"]] > 0).all(), (
        f"the distributional step is no longer positive on the mixtures: {dist_step.to_dict()}")
    assert (dist_step[["controlled", "crossline"]] < mag_step[["controlled", "crossline"]] / 3).all(), (
        "the panel draws the distributional step as the smaller of the two; measured it is not")
    assert dist_step["frangieh"] < 0, (
        "the distributional step no longer reverses on Frangieh, which is the whole of the third "
        "regime this panel draws")
    # Frangieh's best scorer is the magnitude-aware mean, not the direction-only one it used to
    # be. The panel labels that row, so it has to be true before the label is drawn.
    assert v[MAG_METHOD]["frangieh"] >= hit["frangieh"].max() - 1e-12, (
        "mean L2 is no longer the best of the nine on Frangieh; the drawn label is wrong")
    assert -SMALL_REVERSAL <= dist_step["frangieh"] < 0, (
        f"the Frangieh reversal is {dist_step['frangieh']:+.3f}, no longer the small one 2b "
        f"describes")

    for i, (task, _, _) in enumerate(TASKS):
        # The other six scorers: one faint column per task, no identity, behind everything. They
        # say what the benchmark field looks like and are not meant to be read one by one.
        ax.scatter([i + CLOUD_DX] * len(CONTEXT), hit.loc[CONTEXT, task].values,
                   s=MS_CONTEXT, color=FAINT, linewidths=0, zorder=1.5)
        # The connector is neutral machinery grey, not a coloured stem: which end is higher is
        # already carried by the endpoint markers, and a coloured stem was once the heaviest ink
        # in this panel. Two segments now, one per step.
        xs = [i + DIR_DX, i + MAG_DX, i + POP_DX]
        ax.plot(xs, [v[m][task] for m in PROTAG],
                color=SHARED, lw=LW_LINE, solid_capstyle="round", zorder=2)
        for x, mth in zip(xs, PROTAG):
            ax.scatter([x], [v[mth][task]], s=MS_DOT, color=PROTAG_COLOUR[mth],
                       linewidths=0, zorder=4)
        # The two steps, stacked, in the order they are taken. Sign always shown, two decimals
        # always shown. The distributional step is bold only where it reverses, which is the one
        # thing on this panel a reader must not miss.
        ymid = (v[DIR_METHOD][task] + v[POP_METHOD][task]) / 2
        ax.text(i + LABEL_DX, ymid + 0.065, f"{mag_step[task]:+.2f}", ha="center", va="center",
                fontsize=PT_ANNOT, color=MAGNITUDE)
        ax.text(i + LABEL_DX, ymid - 0.065, f"{dist_step[task]:+.2f}", ha="center", va="center",
                fontsize=PT_ANNOT, color=POP,
                fontweight="bold" if dist_step[task] < 0 else "normal")

    # Constructed mixtures | natural dataset. A hairline group separator, the lightest rule in the
    # vocabulary, because this split is context for the reversal and not the reading itself. It
    # runs from under the n line up to just below the cross-line difference label and stops there:
    # a full-height rule crossed that label, and the number has to read as the cross-line pair's.
    ax.plot([1.5, 1.5], [_below(SEP_DROP_IN), 0.52], transform=ax.get_xaxis_transform(),
            color=HAIRLINE, lw=LW_HAIR, zorder=1, clip_on=False, solid_capstyle="butt")

    # Direct labels on the anchor pair instead of a legend: the controlled task is the only one
    # with clear space beside both of its markers, and a legend key placed inside the plot would
    # put two unattached dots in a task's column. The x is written relative to the anchor's slot
    # rather than as an absolute, so the labels follow the task if TASKS is ever reordered. The
    # two names are read out of fig2_style, so this panel cannot call a scorer something panel a
    # does not.
    a = [t for t, _, _ in TASKS].index(ANCHOR)
    # Direct labels on the anchor pair. Energy and mean L2 are within 0.033 of each other there,
    # so their labels cannot both sit beside their own dots; energy's goes above, mean L2's below,
    # and each is coloured to its own mark rather than relying on proximity.
    # mean L2 is labelled to the LEFT of its dot; to the right it lands on the step labels, which
    # sit in the same band. Energy goes above its dot and mean cosine below its own.
    for dx, mth, dy, ha, va in ((POP_DX, POP_METHOD, 0.055, "left", "bottom"),
                                (MAG_DX, MAG_METHOD, 0.055, "right", "bottom"),
                                (DIR_DX, DIR_METHOD, -0.065, "left", "top")):
        off = 0.05 if ha == "left" else -0.05
        ax.text(a + dx + off, v[mth][ANCHOR] + dy, SCORERS[mth]["label"],
                ha=ha, va=va, fontsize=PT_ANNOT, color=PROTAG_COLOUR[mth])
    # Below the clouds, not above them: the top-left band now carries the mean L2 direct label,
    # and two grey strings in one band read as one.
    ax.text(-0.55, 0.135, "six other scorers", ha="left", va="center",
            fontsize=PT_SMALL, color=SUBTLE)

    # Task name on the tick in ink, n on a grey line below it. The single middle-dot line this
    # style prefers needs about 0.55 in per slot and there are three slots in 2.63 in, so the
    # names are set on two lines and the n gets its own row.
    ax.set_xticks(range(len(TASKS)))
    ax.set_xticklabels([lab for _, lab, _ in TASKS], fontsize=PT_TICK, color=TEXT,
                       linespacing=1.15)
    for i, (task, _, constructed) in enumerate(TASKS):
        n = int(nq.loc[POP_METHOD, task])
        # Below the tick labels, by a measured inch drop rather than by a fraction of a height
        # that has now moved once. "natural" is carried on Frangieh's n line rather than on a
        # fourth row of furniture; see judgement call 5 in the module docstring.
        ax.text(i, _below(N_LINE_IN), f"n = {n}" if constructed else f"natural, n = {n}",
                transform=ax.get_xaxis_transform(), ha="center", va="top",
                fontsize=PT_SMALL, color=SUBTLE)

    ax.set_xlim(*XLIM)
    ax.set_ylim(*YLIM)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_ylabel("Hit@1")
    ax.tick_params(axis="x", length=0, labelsize=PT_TICK, labelcolor=TEXT)
    ax.tick_params(axis="y", length=2.2, width=LW_HAIR, color=HAIRLINE, labelcolor=TEXT,
                   labelsize=PT_TICK)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(HAIRLINE)
        ax.spines[side].set_linewidth(LW_HAIR)


if __name__ == "__main__":
    sys.path.insert(0, os.path.join(REPO, "figures"))
    from figstyle import apply_style

    from fig2_style import PT_TITLE
    apply_style(sizes=(PT_TITLE, PT_ANNOT, PT_TICK))
    # The printed box: 2.63 x 1.08 in of axes, with fig2_assemble's pads and its 0.17 in
    # letter band around it. It was 1.84 in tall while the panel also stated a conclusion.
    fig = plt.figure(figsize=(3.45, 1.75))
    ax = fig.add_axes([0.72 / 3.45, 0.50 / 1.75, 2.63 / 3.45, 1.08 / 1.75])
    draw_2b(ax)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "2b.png")
    fig.savefig(out, dpi=300)
    print(f"wrote {out}")
