"""PopRetrieve Figure 2 panel 2e: the population advantage across the controlled mixing sweep.

WHAT THIS PANEL SHOWS
---------------------
Three advantage curves, one per cell line, over the five-point alpha sweep, drawn under a strip
that shows what alpha does to the query. Exactly one of the three falls monotonically, by more
than 0.5 Hit@1; the other two end at or above where they started. The panel does not SAY that,
because a panel states no conclusion (see fig2_style, where title() used to be); it draws it, and
it asserts it in code so the emphasis on the falling line cannot outlive the data. The panel says
nothing about whether the advantage is biologically useful: this is Figure 2, and every criterion
here is objective-aligned (Class A).

WHAT IT READS
-------------
results/exp01_sciplex3_controlled/metrics_summary.csv, the file the experiment writes.
NOT figures/source_data/fig2d_alpha_crossover.csv, a hand-copied mirror with no generator. The
two agreed exactly on their two shared columns when this panel was rebuilt (15 rows, both
mean_cosine_hit@1 and global_energy_hit@1 identical), so nothing is lost by dropping the mirror;
the mirror is simply one more copy that can drift and no longer has a reader.

Constants that are properties of the experiment rather than of the drawing (n_seeds, the alpha
grid, the cell lines, the query size n_total, and the two mechanism-of-action classes) are parsed
out of the declaring source with ast, not typed here:
    src/experiments/exp01_sciplex3_controlled.py :: run
    src/retrieval/tasks.py :: ControlledMixtureTask.__init__
If a default there changes, this panel's labels change with it or the parse fails loudly.

WHAT ALPHA ACTUALLY IS, AND A CORRECTION TO AN EARLIER VERSION
--------------------------------------------------------------
ControlledMixtureTask.build takes n_maj = round(alpha * n_total) cells from the first
mechanism-of-action pool and n_total - n_maj from the second. The two response states are fixed
and orthogonal at every alpha; what alpha changes is the IMBALANCE between them, from a
200 / 200 query at alpha = 0.5 to a 360 / 40 query at alpha = 0.9. The minority state becomes
rare; it does not become similar to the majority state.

An earlier version of this panel carried the x label "(higher = more merged)", and its docstring
said "the two constructed subpopulations overlap more". That is not what the code does, and the
composition strip above the curves is drawn to the code: two rows whose SEPARATION is constant
across the sweep and whose COUNTS change. Nothing in the sweep merges. That correction is
CORRECTIONS.md R45, and it is the reason the strip survives every squeeze on this panel: it is
what makes alpha's meaning visible. The same wrong wording survives in fig2_assemble's own
docstring ("merging the two states"); that file belongs to another author and is not edited here.

THE RESTRAINT PASS AND THE RESIZE (2026-08-31)
----------------------------------------------
The page was compacted from 234 mm to 197 mm and the panel hierarchy was corrected, so this panel
is now WIDER and much SHORTER: curve axes 3.23 x 0.58 in where it was 2.63 x 0.95, with the
composition strip at 3.23 x 0.34 in where it was 2.63 x 0.42. Nothing was scaled by eye; every
constant that was tuned against the old height was re-derived against the new one, and the two
that govern legibility are now asserted against the measured axes rather than trusted.

Gone from the panel, and preserved nowhere on it:

  * The conclusion phrase, "K562 collapses; A549 and MCF7 do not". Seven panels each stating a
    conclusion is seven claims competing for one page; the figure carries evidence and the legend
    carries the argument. fig2_style.title() is deleted and fig2_assemble._assert_no_titles caps
    all panel text at PT_ANNOT, so it cannot return at a smaller size. The phrase opens this
    panel's caption entry, where it costs no space and can be qualified properly.
  * "one seed = 0.05", the resolution note that rode along with n. It is a reading instruction,
    not a statistic, and it belongs beside the caption's own sentence about seed granularity. The
    warning it carried still holds and is restated under judgement call 5 below: the smallest step
    this panel can draw is one seed changing its mind, so do not read the small steps.

What the resize forced, item by item:

  * The y view tightened from [-0.05, 1.18] to [-0.04, 1.06]. The old top margin existed to hold
    the n line inside the axes; with 39 per cent less height that margin costs more than the data
    it frames, so the n moved below the x axis and the view closed to the data. The consequence is
    measured, not hoped for: the collapsing line's fall now spans 86 per cent of the drawn view,
    and LOSS_MIN_SPAN asserts it stays above half, so a later retune cannot shrink the panel's
    one visible relationship into a wiggle.
  * The three direct end labels no longer fit at their exact line ends. At alpha = 0.9 the two
    non-collapsing lines are 0.20 Hit@1 apart, which was 11.1 pt of paper at the old height and
    is 7.6 pt at the new one, under one 7.2 pt line of type. They are now placed by _spread(), which
    pushes labels apart to a minimum gap DERIVED from the measured axes height and the type size
    rather than from a constant, and never reorders them. On the current data it moves exactly one
    label, A549, by 0.03 Hit@1; MAX_LABEL_NUDGE asserts no label is moved far enough to be read
    against the wrong line.
  * The y axis name broke to three short lines and lost the scorer pair (judgement call 8).
  * The strip's two rows were re-tuned: JITTER_Y from 0.052 to 0.040 of the strip height, and the
    row centres from 0.60 / 0.16 to 0.52 / 0.14, so that the clouds keep a clear lane between them
    and clear the counts line above at 0.34 in. The question of whether two rows of dots still
    read at that height is not left to the eye: the dots are generated before they are plotted
    and the panel measures THEM, edge of dot to edge of dot, refusing to build if the rows would
    merge. At the current numbers the lane between them is 3.3 pt and the guard needs 1.0 pt.

JUDGEMENT CALLS A READER COULD DISAGREE WITH
--------------------------------------------
1. The panel plots the DIFFERENCE, global_energy_hit@1 minus mean_cosine_hit@1, as three curves
   rather than the two levels as six. The difference is the quantity the manuscript's caption
   discusses. The cost is real: a reader can no longer see that, for instance, both scorers move
   at alpha = 0.9 in one line. Those levels are in the source file and belong in the caption.
2. All three curves are POP blue. The plotted quantity is signed towards the population family,
   and there is no third family colour, so the three cell lines are separated by marker shape and
   by a direct end label rather than by hue. The one line that falls additionally carries a
   heavier stroke and filled markers; the two that do not carry open markers, which groups them
   as one visual gesture. Emphasis therefore falls on the line that behaves as the naive
   expectation predicts, which is a defensible choice only because the two open-marker lines are
   the ones the claim rests on and read as a pair.
3. The falling line's NAME is set bold, and the other two are not. That is weight, not colour, so
   it does not touch the rule that marks carry colour and letters do not; it exists so the label
   matches the stroke weight of the line it names. A reader could call it a residue of the deleted
   phrase. The counter-argument is that the two open-marker lines would otherwise be labelled in
   the same weight as the line they are being contrasted with.
4. Straight segments between the five measured points, no smoothing and no fitted trend. The
   claim is non-monotonicity; a smooth curve would argue against it.
5. "Falls" and "does not fall" are the same threshold, COLLAPSE_DROP, applied in both directions.
   An earlier version tested the falling line for a drop of at least 0.5 Hit@1 but tested the
   other two only on their endpoints, so a line could give up 0.49 between two alphas and still
   pass as one that does not fall. The binding case is real: MCF7 gives up 0.45 over the last step
   and clears the guard by one seed. A reader who calls that step a collapse in progress is not
   contradicted by the panel; what the drawing shows is that it is smaller than K562's fall and
   that MCF7 ends above where it started.
6. No error bars. exp01 writes a second file, per_query_scores.csv, which carries a seed column
   and from which a per-seed distribution could be rebuilt, but that file is not in results/ in
   this checkout: metrics_summary.csv is all there is, and it holds only the seed-averaged Hit@1.
   An interval would therefore have to be invented, so none is drawn. The panel states n instead.
   Each Hit@1 is a multiple of 1 / n_seeds, so their difference is too, and the smallest step the
   panel can draw is one seed changing its mind. Do not read the small steps.
7. The strip draws one dot per CELLS_PER_DOT cells, so the rows are subsampled 10:1. The exact
   counts are printed at the two ends, so the subsampling cannot be mistaken for the population
   size.
8. The y axis name is "Population advantage (Delta Hit@1)" and no longer names the two scorers in
   the rotated label: at 0.58 in no line of that label may exceed about 13 characters, and four
   lines of rotated type would eat the whole left pad. The pair is not dropped, because WHICH
   population scorer matters here (coverage-worst, one of the other three in the same file, goes
   NEGATIVE for K562 at alpha = 0.9 where this pair is still +0.05). It is printed once, below the
   x axis, on the same line as n. The names come from fig2_style.SCORERS, so this panel and panel
   a's ladder cannot drift apart, and the families are checked: "advantage" is the right word only
   for a population scorer minus a mean-level one, and swapping in a same-family pair fails here
   rather than flipping the sign silently.
9. The strip's row labels, the counts, the n line and "no advantage" are set at PT_SMALL, the
   figure floor. They are provenance and datum labels rather than claims, and the 0.72 in left pad
   does not hold "HDAC" at PT_ANNOT beside a three-line rotated axis name.

Run standalone: python fig2d.py
"""
from __future__ import annotations

import ast
import os
import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fig2_style import (FAINT, LW_HAIR, POP, PT_ANNOT, PT_SMALL, PT_TICK,  # noqa: E402
                        REPO, SCORERS, SHARED, SUBTLE, TEXT, bare_axes)

METRICS = f"{REPO}/results/exp01_sciplex3_controlled/metrics_summary.csv"
EXP_SRC = f"{REPO}/src/experiments/exp01_sciplex3_controlled.py"
TASK_SRC = f"{REPO}/src/retrieval/tasks.py"

# The two scorers whose difference IS the plotted quantity. See judgement call 8: they are named
# on the panel, below the x axis, and the family of each is checked here.
POP_SCORER, MEAN_SCORER = "global_energy", "mean_cosine"
POP_COL, MEAN_COL = f"{POP_SCORER}_hit@1", f"{MEAN_SCORER}_hit@1"
assert SCORERS[POP_SCORER]["family"] == "pop", f"{POP_SCORER} is not a population-level scorer"
assert SCORERS[MEAN_SCORER]["family"] == "mean", f"{MEAN_SCORER} is not a mean-level scorer"

# What "falls" means, ONCE, for both halves of the contrast the marks draw: a loss of this many
# Hit@1. The heavily stroked line has to fall by at least this much; the two open-marker lines
# have to stay inside it between EVERY pair of alphas, not merely end where they began. On the
# current data the binding case is MCF7, which gives up 0.45 over the last step: it clears the
# guard by 0.05, which is one seed. If a rerun moves that step by two seeds the panel stops
# building, which is the correct outcome, because the emphasis would stop being true.
COLLAPSE_DROP = 0.5

# The fall has to be VISIBLE, not merely present. It is the one relationship this panel exists to
# carry, so it must span at least this fraction of the drawn y view; the guard is what stops a
# later y retune from compressing it into a wiggle. At the current view it spans 0.86.
LOSS_MIN_SPAN = 0.5

# The drawing box, in data coordinates. Both axes share this x range so a reader can drop a
# vertical line from a composition cloud to the point below it. The left margin holds the strip's
# two row labels and the right margin holds the three end labels.
XLO, XHI = 0.40, 0.985
# Re-cut for the 0.58 in axes: closed onto the data (0.05 to 1.00) with just enough room below
# zero for the datum spine to read as a line rather than as the frame.
YLO, YHI = -0.04, 1.06

# Direct end labels. _spread pushes them apart to LABEL_LEAD line-heights of PT_ANNOT, measured
# against the axes as drawn; MAX_LABEL_NUDGE is how far a label may travel from its own line
# before it stops being that line's label.
LABEL_LEAD = 1.20
MAX_LABEL_NUDGE = 0.10

# Composition strip. Two rows at a FIXED separation, because the two response states do not move.
# Re-tuned for 0.34 in: at the old spread the two clouds would have shared a lane and the counts
# line would have sat on the upper one. _assert_strip_reads checks both against the drawn size.
Y_MAJ, Y_MIN = 0.52, 0.14
JITTER_X, JITTER_Y = 0.011, 0.040     # cloud spread, in x data units and y axes fraction
MS_STRIP = 1.5                        # one dot, in points
CELLS_PER_DOT = 10
DOT_SEED = 7                          # the cloud layout is jitter, so it is seeded and fixed

# How far below the axes the provenance line sits, in points, and the lead that has to survive
# under the x axis name. This was the one clearance on the panel that was chosen rather than
# measured, and it was the tightest thing on it: at 25.0 pt the two lines cleared each other by
# 2.4 pt, which is less lead than a paragraph gets, so the axis name and the provenance read as
# one block. _n_line_lead() now derives the stack the line has to clear from the type ladder and
# from where the zero spine sits in the view, and the panel refuses to build if the lead goes.
N_LINE_PT = 26.5
N_LINE_LEAD = 2.0

OPEN_MARKERS = ("s", "^")             # for the lines that do not fall; the one that does
FALL_MARKER = "o"                     # gets a filled marker and a heavier stroke


def _signature_defaults(path: str, qualname: str) -> dict:
    """Keyword defaults of a function or method, read out of the declaring source with ast.

    Used instead of importing, because importing exp01 pulls in the data loader. Raises if the
    target is missing, so a rename upstream fails here rather than silently freezing a label.
    """
    tree = ast.parse(open(path, encoding="utf-8").read())
    parts = qualname.split(".")
    node = tree
    for i, name in enumerate(parts):
        want = (ast.ClassDef,) if i < len(parts) - 1 else (ast.FunctionDef, ast.AsyncFunctionDef)
        found = [c for c in ast.iter_child_nodes(node)
                 if isinstance(c, want) and c.name == name]
        if not found:
            raise LookupError(f"{path}: no {'.'.join(parts[:i + 1])} to read defaults from")
        node = found[0]
    pos = node.args.args[len(node.args.args) - len(node.args.defaults):]
    out = {a.arg: ast.literal_eval(d) for a, d in zip(pos, node.args.defaults)}
    for a, d in zip(node.args.kwonlyargs, node.args.kw_defaults):
        if d is not None:
            out[a.arg] = ast.literal_eval(d)
    return out


def _load():
    """The advantage table, plus the experiment constants the labels quote."""
    run = _signature_defaults(EXP_SRC, "run")
    task = _signature_defaults(TASK_SRC, "ControlledMixtureTask.__init__")
    alphas = tuple(float(a) for a in run["alphas"])
    lines = tuple(run["lines"])
    n_seeds, n_total = int(run["n_seeds"]), int(run["n_total"])

    m = pd.read_csv(METRICS)
    assert sorted(m["cell_line"].unique()) == sorted(lines), \
        f"{METRICS} holds {sorted(m['cell_line'].unique())}, run() declares {sorted(lines)}"
    assert sorted(round(float(a), 6) for a in m["alpha"].unique()) == sorted(alphas), \
        f"{METRICS} alpha grid does not match the sweep run() declares"

    adv = {}
    for cl in lines:
        d = m[m["cell_line"] == cl].sort_values("alpha")
        assert len(d) == len(alphas), f"{cl}: expected one row per alpha in {METRICS}"
        adv[cl] = (d["alpha"].to_numpy(float), (d[POP_COL] - d[MEAN_COL]).to_numpy(float))
    return adv, alphas, lines, n_seeds, n_total, str(task["class_a"]), str(task["class_b"])


def _axes_height_pt(ax) -> float:
    """The drawn height of an axes in points, from the figure ledger rather than a renderer.

    Every legibility constant below is derived from this rather than tuned against a remembered
    canvas, which is what made the previous version of this panel wrong the moment the page was
    compacted from 234 to 197 mm.
    """
    return float(ax.get_position().height * ax.figure.get_figheight() * 72.0)


def _spread(ys, min_gap):
    """Push labels apart to ``min_gap`` in data units, lowest first, without reordering them."""
    out = list(map(float, ys))
    rank = sorted(range(len(out)), key=lambda i: out[i])
    for lo, hi in zip(rank[:-1], rank[1:]):
        if out[hi] - out[lo] < min_gap:
            out[hi] = out[lo] + min_gap
    return out


def _n_line_lead(ax) -> float:
    """Points of white between the x axis name and the provenance line, from the type ladder.

    Matplotlib hangs the x tick labels off the BOTTOM SPINE, and this panel moves that spine onto
    the zero datum, so the whole stack under the axes rides on where zero sits in the view. Every
    term below is an rcParam or a size from fig2_style; none of it is a remembered canvas. The
    1.1 factor is the ascender-to-descender ink of one line of this face, which is what has to
    clear, rather than the nominal size.
    """
    zero_pt = (0.0 - YLO) / (YHI - YLO) * _axes_height_pt(ax)   # zero, above the axes bottom
    depth = plt.rcParams["xtick.major.size"] + plt.rcParams["xtick.major.pad"] - zero_pt
    depth += PT_TICK + plt.rcParams["axes.labelpad"] + PT_ANNOT * 1.1
    return N_LINE_PT - depth


def _assert_strip_reads(ax_top, clouds):
    """Refuse to draw a composition strip whose two response states no longer read as two rows.

    The strip is the panel's answer to CORRECTIONS.md R45, so it survives the shrink; what it may
    not do is survive it illegibly. The clouds are SEEDED jitter, so their extent is not a
    property of chance and does not have to be approximated: they are generated before this runs
    and this measures them, edge of dot to edge of dot, against the strip AS DRAWN. An earlier
    version guarded a nominal 2 sigma instead, which over-states the lane by 0.6 pt at this size,
    because 200 draws across five clouds reach well past 2 sigma.
    """
    h_pt = _axes_height_pt(ax_top)
    r = MS_STRIP / 2.0
    lower = [ys for y0, _, ys in clouds if y0 == Y_MIN]
    upper = [ys for y0, _, ys in clouds if y0 == Y_MAJ]
    assert lower and upper, "the strip must draw both response states"
    top_of_min = max(float(ys.max()) for ys in lower) * h_pt + r
    bot_of_maj = min(float(ys.min()) for ys in upper) * h_pt - r
    lane = bot_of_maj - top_of_min
    assert lane >= 1.0, (
        f"at {h_pt / 72:.2f} in the two response-state rows leave {lane:.1f} pt between them; "
        "two rows of dots that touch are one row, and a strip that cannot be read should be "
        "reported rather than drawn")
    assert min(float(ys.min()) for ys in lower) * h_pt - r >= 0.0, (
        "the minority row is clipped by the bottom of the strip")
    assert max(float(ys.max()) for ys in upper) * h_pt + r <= h_pt - PT_SMALL - 1.0, (
        "the counts line would sit on the majority row")


def draw_2d(ax, ax_top):
    """Population advantage vs alpha, over a strip showing what alpha does to the query."""
    adv, alphas, lines, n_seeds, n_total, class_a, class_b = _load()

    # ---- what the marks assert, asserted before they are drawn ------------------------------
    eps = 1e-9
    falling = [cl for cl in lines
               if all(adv[cl][1][i] >= adv[cl][1][i + 1] - eps
                      for i in range(len(alphas) - 1))]
    assert len(falling) == 1, (
        "the panel gives ONE line the heavy stroke that marks it as the one that falls; the data "
        f"now has {len(falling)} monotonically non-increasing: {falling}")
    fall = falling[0]
    drop = float(adv[fall][1][0] - adv[fall][1][-1])
    assert drop >= COLLAPSE_DROP, (
        f"{fall} falls by only {drop:.2f} Hit@1, which is a drift and not a collapse; "
        "the emphasis this panel puts on that line no longer holds")
    holds = [cl for cl in lines if cl != fall]
    for cl in holds:
        y = adv[cl][1]
        assert y[-1] >= y[0] - eps, (
            f"{cl} ends at {y[-1]:.2f} below its alpha = {alphas[0]} value {y[0]:.2f}; "
            "the panel draws it as a line that does not fall")
        worst = max(float(y[i] - y[j]) for i in range(len(y)) for j in range(i, len(y)))
        assert worst < COLLAPSE_DROP, (
            f"{cl} gives up {worst:.2f} Hit@1 between two alphas, which is the size of fall "
            f"this same panel marks as a collapse in {fall}; the drawing would be using one "
            "stroke weight to mean two different things")

    # The view has to contain the data and the datum, and the fall has to be big enough on paper
    # to be the thing a reader sees first. Both are properties of the RESIZE, not of the data.
    flat = np.concatenate([adv[cl][1] for cl in lines])
    assert YLO < flat.min() and flat.max() < YHI, (
        f"the [{YLO}, {YHI}] view clips the data, which runs {flat.min():.2f} to {flat.max():.2f}")
    assert YLO <= 0.0 <= YHI, "the zero datum the y axis is read against is outside the view"
    assert drop / (YHI - YLO) >= LOSS_MIN_SPAN, (
        f"{fall}'s fall spans only {drop / (YHI - YLO):.0%} of the drawn view; the panel's one "
        "visible relationship has been compressed into a wiggle by the y range")

    # ---- the composition strip: what alpha does to the query -------------------------------
    # Two response states at a CONSTANT separation, with the minority state thinning out. The
    # guides make the constancy legible: the rows do not move, only the clouds on them.
    lab_x = alphas[0] - 2.6 * JITTER_X
    for y0 in (Y_MAJ, Y_MIN):
        ax_top.plot([lab_x + 0.008, XHI], [y0, y0], color=FAINT, lw=LW_HAIR, zorder=1,
                    solid_capstyle="butt")
    rng = np.random.default_rng(DOT_SEED)
    minority, clouds = [], []
    for a in alphas:
        n_maj = int(round(a * n_total))
        n_min = n_total - n_maj
        assert n_maj + n_min == n_total, f"alpha = {a}: the strip must draw all {n_total} cells"
        minority.append(n_min)
        for y0, n in ((Y_MAJ, n_maj), (Y_MIN, n_min)):
            k = int(round(n / CELLS_PER_DOT))
            clouds.append((y0, a + rng.normal(0.0, JITTER_X, k),
                           y0 + rng.normal(0.0, JITTER_Y, k)))
        if a in (alphas[0], alphas[-1]):
            ax_top.text(a, 1.0, f"{n_maj} : {n_min}" + (" cells" if a == alphas[0] else ""),
                        ha="center", va="top", fontsize=PT_SMALL, color=SUBTLE)
    assert all(b < c for b, c in zip(minority[1:], minority[:-1])), (
        f"the strip draws the minority state thinning out; it now runs {minority}")
    # Measured before a single dot is committed to the canvas, so an unreadable strip is reported
    # rather than drawn. The draw order below is unchanged, so the picture is unchanged.
    _assert_strip_reads(ax_top, clouds)
    for y0, xs, ys in clouds:
        ax_top.plot(xs, ys, ls="none", marker="o", ms=MS_STRIP, mfc=SHARED, mec="none",
                    alpha=0.85, zorder=3)
    for y0, name in ((Y_MAJ, class_a), (Y_MIN, class_b)):
        ax_top.text(lab_x, y0, name, ha="right", va="center", fontsize=PT_SMALL, color=TEXT)
    ax_top.set_xlim(XLO, XHI)
    ax_top.set_ylim(0.0, 1.0)
    ax_top.set_xticks([])
    ax_top.set_yticks([])
    for side in ("top", "right", "left", "bottom"):
        ax_top.spines[side].set_visible(False)

    # ---- the curves ------------------------------------------------------------------------
    # One hue for all three: the plotted quantity belongs to the population family. The cell
    # lines are told apart by marker shape and by a direct end label, never by hue alone.
    order = [fall] + holds
    for i, cl in enumerate(order):
        x, y = adv[cl]
        if cl == fall:
            ax.plot(x, y, "-", marker=FALL_MARKER, color=POP, ms=3.0, lw=1.5, mfc=POP,
                    mec=POP, zorder=6, clip_on=False)
        else:
            ax.plot(x, y, "-", marker=OPEN_MARKERS[i - 1], color=POP, ms=2.8, lw=0.9,
                    mfc="white", mec=POP, mew=0.9, zorder=5, clip_on=False)

    # Direct labels, placed against the axes AS DRAWN rather than at a remembered height. At
    # 0.58 in the two non-falling lines end 7.6 pt apart, which is under one line of PT_ANNOT.
    min_gap = LABEL_LEAD * PT_ANNOT / _axes_height_pt(ax) * (YHI - YLO)
    ends = [float(adv[cl][1][-1]) for cl in order]
    placed = _spread(ends, min_gap)
    for cl, y_end, y_lab in zip(order, ends, placed):
        assert abs(y_lab - y_end) <= MAX_LABEL_NUDGE, (
            f"{cl}'s label had to move {abs(y_lab - y_end):.2f} Hit@1 to clear its neighbours, "
            "which is far enough that a reader could read it against the wrong line")
        assert YLO <= y_lab <= YHI, f"{cl}'s label was pushed outside the drawn view"
        ax.text(adv[cl][0][-1] + 0.014, y_lab, cl, ha="left", va="center", fontsize=PT_ANNOT,
                color=TEXT, fontweight="bold" if cl == fall else "normal")

    # The zero datum is the bottom spine, moved to y = 0 below; fig2_style.zero_rule is
    # deliberately NOT also called, because two lines on the same datum is one line too many.
    ax.text(0.012, 0.02, "no advantage", transform=ax.get_yaxis_transform(), ha="left",
            va="bottom", fontsize=PT_SMALL, color=SUBTLE)

    ax.set_xlim(XLO, XHI)
    ax.set_ylim(YLO, YHI)
    ax.set_xticks(list(alphas))
    ax.set_xticklabels([f"{a:g}" for a in alphas])
    ax.set_yticks([0.0, 0.5, 1.0])
    ax.set_yticklabels(["0", "0.5", "1.0"])
    ax.set_xlabel(f"$\\alpha$, fraction of query cells in the {class_a} state")
    # Three short lines because no line of a rotated label may exceed the 0.58 in axes; the
    # scorer pair it used to carry is printed below the x axis instead. See judgement call 8.
    ax.set_ylabel("Population\nadvantage\n($\\Delta$ Hit@1)", linespacing=1.15)
    bare_axes(ax)
    ax.spines["left"].set_bounds(0.0, 1.0)
    # The bottom spine IS the zero datum, so it sits at y = 0 and takes the darker SUBTLE grey
    # that fig2_style reserves for a value line rather than the hairline grey of a frame.
    ax.spines["bottom"].set_position(("data", 0.0))
    ax.spines["bottom"].set_color(SUBTLE)
    ax.spines["bottom"].set_linewidth(0.8)

    # What the difference is, and how many seeds each point averages, on one line under the axis
    # names. The offset is in points below the axes, converted through the drawn height, so it
    # does not have to be retuned again when the box changes; the lead it leaves under the x axis
    # name is derived rather than trusted, because that was the tightest clearance on the panel.
    lead = _n_line_lead(ax)
    assert lead >= N_LINE_LEAD, (
        f"the provenance line would clear the x axis name by {lead:.1f} pt, under the "
        f"{N_LINE_LEAD} pt lead that keeps two lines saying different things from reading as one "
        "block; raise N_LINE_PT, or move the line into the caption")
    ax.text(1.0, -(N_LINE_PT / _axes_height_pt(ax)),
            f"{SCORERS[POP_SCORER]['label']} $-$ {SCORERS[MEAN_SCORER]['label']}, "
            f"n = {n_seeds} seeds per point",
            transform=ax.transAxes, ha="right", va="top", fontsize=PT_SMALL, color=SUBTLE)



if __name__ == "__main__":
    # Mirrors fig2_assemble's ledger for this panel: a 4.05 x 1.67 in box, 0.17 in of letter
    # band, a 0.34 in strip, a 0.08 in gap, a 0.58 in curve axes and a 0.50 in bottom pad.
    BW, BH, LEFT, RIGHT = 4.05, 1.67, 0.72, 0.10
    BAND, STRIP, GAP, CURVE = 0.17, 0.34, 0.08, 0.58
    fig = plt.figure(figsize=(BW, BH))
    w = (BW - LEFT - RIGHT) / BW
    a_top = fig.add_axes([LEFT / BW, 1.0 - (BAND + STRIP) / BH, w, STRIP / BH])
    a_cur = fig.add_axes([LEFT / BW, 1.0 - (BAND + STRIP + GAP + CURVE) / BH, w, CURVE / BH])
    draw_2d(a_cur, a_top)
    fig.savefig(os.path.join(os.path.dirname(__file__), "2e.png"), dpi=300)
    print("wrote 2e.png")
