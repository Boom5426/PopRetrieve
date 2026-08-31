"""PopRetrieve Figure 2 panel 2e: the population advantage across the controlled mixing sweep.

WHAT THIS PANEL CLAIMS
----------------------
Raising alpha does NOT produce a universal collapse of the population advantage. Exactly one of
the three cell lines falls monotonically (its advantage drops by more than 0.5 Hit@1); the other
two end at or above where they started. That, and only that, is asserted at draw time, so the
drawn phrase cannot outlive the data. The panel says nothing about whether the advantage is
biologically useful: this is Figure 2, and every criterion here is objective-aligned (Class A).

WHAT IT READS
-------------
results/exp01_sciplex3_controlled/metrics_summary.csv, the file the experiment writes.
NOT figures/source_data/fig2e_alpha_crossover.csv, a hand-copied mirror with no generator. The
two agreed exactly on their two shared columns when this panel was rebuilt (15 rows, both
mean_cosine_hit@1 and global_energy_hit@1 identical), so nothing is lost by dropping the mirror;
the mirror is simply one more copy that can drift and no longer has a reader.

Constants that are properties of the experiment rather than of the drawing (n_seeds, the alpha
grid, the cell lines, the query size n_total, and the two mechanism-of-action classes) are parsed
out of the declaring source with ast, not typed here:
    src/experiments/exp01_sciplex3_controlled.py :: run
    src/retrieval/tasks.py :: ControlledMixtureTask.__init__
If a default there changes, this panel's labels change with it or the parse fails loudly.

WHAT ALPHA ACTUALLY IS, AND A CORRECTION TO THE PREVIOUS VERSION
----------------------------------------------------------------
ControlledMixtureTask.build takes n_maj = round(alpha * n_total) cells from the first
mechanism-of-action pool and n_total - n_maj from the second. The two response states are fixed
and orthogonal at every alpha; what alpha changes is the IMBALANCE between them, from a
200 / 200 query at alpha = 0.5 to a 360 / 40 query at alpha = 0.9. The minority state becomes
rare; it does not become similar to the majority state.

The version of this panel that this one replaces carried the x label "(higher = more merged)",
and its docstring said "the two constructed subpopulations overlap more". That is not what the
code does, and the schematic strip above the curves is drawn to the code: two clouds whose
SEPARATION is constant across the sweep and whose COUNTS change. Nothing in the sweep merges.
The same wording survives in fig2_assemble's own docstring ("merging the two states"); that file
belongs to another author and is not edited here.

JUDGEMENT CALLS A READER COULD DISAGREE WITH
--------------------------------------------
1. The panel plots the DIFFERENCE, global_energy_hit@1 minus mean_cosine_hit@1, as three curves
   rather than the two levels as six. The difference is the quantity the manuscript's caption
   discusses. The cost is real: a reader can no longer see that, for instance, both scorers move
   at alpha = 0.9 in one line. Those levels are in the source file and belong in the caption.
2. All three curves are POP blue. The plotted quantity is signed towards the population family,
   and there is no third family colour, so the three cell lines are separated by marker shape and
   by a direct end label rather than by hue. The one line that collapses additionally carries a
   heavier stroke and filled markers; the two that do not carry open markers, which groups them
   as one visual gesture. Emphasis therefore falls on the line that behaves as the naive
   expectation predicts, which is a defensible choice only because the two open-marker lines are
   the ones the claim rests on and read as a pair.
3. Straight segments between the five measured points, no smoothing and no fitted trend. The
   claim is non-monotonicity; a smooth curve would argue against it.
4. "Collapses" and "does not collapse" are the same threshold, COLLAPSE_DROP, applied in both
   directions. The earlier version of this panel tested the falling line for a drop of at least
   0.5 Hit@1 but tested the other two only on their endpoints, so a line could give up 0.49
   between two alphas and still be called one that does not collapse. The binding case is real:
   MCF7 gives up 0.45 over the last step and clears the guard by one seed. A reader who calls
   that step a collapse in progress is not contradicted by the panel; what the panel claims is
   that it is smaller than K562's fall and that MCF7 ends above where it started.
5. No error bars. exp01 writes a second file, per_query_scores.csv, which carries a seed column
   and from which a per-seed distribution could be rebuilt, but that file is not in results/ in
   this checkout: metrics_summary.csv is all there is, and it holds only the seed-averaged Hit@1.
   An interval would therefore have to be invented, so none is drawn. Instead the panel states n
   and states the resolution it buys: each Hit@1 is a multiple of 1 / n_seeds, so their difference
   is too, and the smallest step the panel can draw is one seed changing its mind. Do not read the
   small steps.
6. The schematic draws one dot per CELLS_PER_DOT cells, so the clouds are subsampled 10:1. The
   exact counts are printed at the two ends, so the subsampling cannot be mistaken for the
   population size.
7. The strip's row labels and the counts are set at PT_SMALL, the figure floor. They are
   provenance for the x axis rather than a claim, and the 0.45 in left margin does not hold
   "HDAC" at PT_ANNOT.

Run standalone: python fig2e.py
"""
from __future__ import annotations

import ast
import os
import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fig2_style import (FAINT, LW_HAIR, POP, PT_ANNOT, PT_SMALL, REPO,  # noqa: E402
                        SCORERS, SHARED, SUBTLE, TEXT, bare_axes, title)

METRICS = f"{REPO}/results/exp01_sciplex3_controlled/metrics_summary.csv"
EXP_SRC = f"{REPO}/src/experiments/exp01_sciplex3_controlled.py"
TASK_SRC = f"{REPO}/src/retrieval/tasks.py"

# The two scorers whose difference IS the plotted quantity, named on the y axis rather than
# left to the caption: metrics_summary.csv carries three population-level scorers, and
# "population advantage" is a different curve for each of them (coverage-worst, for one, goes
# NEGATIVE for K562 at alpha = 0.9, where the pair drawn here is still +0.05). The printed names
# come from fig2_style.SCORERS, so this axis and panel a's ladder cannot drift apart, and the
# families are checked: "advantage" is the right word only for a population scorer minus a
# mean-level one, and swapping in a same-family pair must fail here rather than flip the sign.
POP_SCORER, MEAN_SCORER = "global_energy", "mean_cosine"
POP_COL, MEAN_COL = f"{POP_SCORER}_hit@1", f"{MEAN_SCORER}_hit@1"
assert SCORERS[POP_SCORER]["family"] == "pop", f"{POP_SCORER} is not a population-level scorer"
assert SCORERS[MEAN_SCORER]["family"] == "mean", f"{MEAN_SCORER} is not a mean-level scorer"

# What "collapses" means, ONCE, for both halves of the panel's phrase: a fall of this many
# Hit@1. The line the phrase names has to fall by at least this much; the two it says do not
# collapse have to stay inside it between EVERY pair of alphas, not merely end where they began.
# On the current data the binding case is MCF7, which gives up 0.45 over the last step: it
# clears the guard by 0.05, which is one seed. If a rerun moves that step by two seeds the
# panel stops building, which is the correct outcome, because the phrase would stop being true.
COLLAPSE_DROP = 0.5

# The drawing box, in data coordinates. The left margin holds the strip's two row labels and the
# right margin holds the three end labels; both axes share this x range so a reader can drop a
# vertical line from a cloud to the point below it.
XLO, XHI = 0.40, 0.985
YLO, YHI = -0.05, 1.18

# Schematic strip. Two rows at a FIXED separation, because the two response states do not move.
Y_MAJ, Y_MIN = 0.60, 0.16
JITTER_X, JITTER_Y = 0.011, 0.052     # cloud spread, in x data units and y axes fraction
CELLS_PER_DOT = 10
DOT_SEED = 7                          # the cloud layout is jitter, so it is seeded and fixed

OPEN_MARKERS = ("s", "^")             # for the lines that do not collapse; the one that does
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


def draw_2e(ax, ax_top):
    """Population advantage vs alpha, over a strip showing what alpha does to the query."""
    adv, alphas, lines, n_seeds, n_total, class_a, class_b = _load()

    # ---- the claim, asserted before it is drawn -------------------------------------------
    eps = 1e-9
    falling = [cl for cl in lines
               if all(adv[cl][1][i] >= adv[cl][1][i + 1] - eps
                      for i in range(len(alphas) - 1))]
    assert len(falling) == 1, (
        "the panel's phrase names ONE collapsing cell line; the data now has "
        f"{len(falling)} monotonically non-increasing: {falling}")
    fall = falling[0]
    drop = float(adv[fall][1][0] - adv[fall][1][-1])
    assert drop >= COLLAPSE_DROP, (
        f"{fall} falls by only {drop:.2f} Hit@1, which is a drift and not a collapse; "
        "the panel's phrase no longer holds")
    holds = [cl for cl in lines if cl != fall]
    for cl in holds:
        y = adv[cl][1]
        assert y[-1] >= y[0] - eps, (
            f"{cl} ends at {y[-1]:.2f} below its alpha = {alphas[0]} value {y[0]:.2f}; "
            "the panel's phrase claims it does not fall")
        worst = max(float(y[i] - y[j]) for i in range(len(y)) for j in range(i, len(y)))
        assert worst < COLLAPSE_DROP, (
            f"{cl} gives up {worst:.2f} Hit@1 between two alphas, which is the size of fall "
            f"this same panel calls a collapse in {fall}; the phrase would be using the word "
            "to mean two different things in one sentence")

    # ---- the schematic strip: what alpha does to the query ---------------------------------
    # Two response states at a CONSTANT separation, with the minority state thinning out. The
    # guides make the constancy legible: the rows do not move, only the clouds on them.
    lab_x = alphas[0] - 2.6 * JITTER_X
    for y0 in (Y_MAJ, Y_MIN):
        ax_top.plot([lab_x + 0.008, XHI], [y0, y0], color=FAINT, lw=LW_HAIR, zorder=1,
                    solid_capstyle="butt")
    rng = np.random.default_rng(DOT_SEED)
    for a in alphas:
        n_maj = int(round(a * n_total))
        n_min = n_total - n_maj
        for y0, n in ((Y_MAJ, n_maj), (Y_MIN, n_min)):
            k = int(round(n / CELLS_PER_DOT))
            ax_top.plot(a + rng.normal(0.0, JITTER_X, k), y0 + rng.normal(0.0, JITTER_Y, k),
                        ls="none", marker="o", ms=1.5, mfc=SHARED, mec="none", alpha=0.85,
                        zorder=3)
        if a in (alphas[0], alphas[-1]):
            ax_top.text(a, 1.0, f"{n_maj} : {n_min}" + (" cells" if a == alphas[0] else ""),
                        ha="center", va="top", fontsize=PT_SMALL, color=SUBTLE)
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
            ax.plot(x, y, "-", marker=FALL_MARKER, color=POP, ms=3.2, lw=1.5, mfc=POP,
                    mec=POP, zorder=6, clip_on=False)
        else:
            ax.plot(x, y, "-", marker=OPEN_MARKERS[i - 1], color=POP, ms=2.9, lw=0.9,
                    mfc="white", mec=POP, mew=0.9, zorder=5, clip_on=False)
        ax.text(x[-1] + 0.014, y[-1], cl, ha="left", va="center", fontsize=PT_ANNOT,
                color=TEXT, fontweight="bold" if cl == fall else "normal")

    # The zero datum is the bottom spine, moved to y = 0 below; fig2_style.zero_rule is
    # deliberately NOT also called, because two lines on the same datum is one line too many.
    ax.text(0.012, 0.02, "no advantage", transform=ax.get_yaxis_transform(), ha="left",
            va="bottom", fontsize=PT_SMALL, color=SUBTLE)
    # n, and the resolution that n buys. One seed is 1 / n_seeds of a Hit@1, so it is also
    # 1 / n_seeds of the difference: the smallest step the panel can draw is not a finding.
    ax.text(1.0, YHI - 0.05, f"n = {n_seeds} seeds per point; one seed = {1 / n_seeds:.3g}",
            transform=ax.get_yaxis_transform(), ha="right", va="top", fontsize=PT_SMALL,
            color=SUBTLE)

    ax.set_xlim(XLO, XHI)
    ax.set_ylim(YLO, YHI)
    ax.set_xticks(list(alphas))
    ax.set_xticklabels([f"{a:g}" for a in alphas])
    ax.set_yticks([0.0, 0.5, 1.0])
    ax.set_yticklabels(["0", "0.5", "1.0"])
    ax.set_xlabel(f"$\\alpha$, fraction of query cells in the {class_a} state")
    ax.set_ylabel(f"Population advantage,\n{SCORERS[POP_SCORER]['label']} $-$ "
                  f"{SCORERS[MEAN_SCORER]['label']}\n($\\Delta$ Hit@1)", linespacing=1.15)
    bare_axes(ax)
    ax.spines["left"].set_bounds(0.0, 1.0)
    # The bottom spine IS the zero datum, so it sits at y = 0 and takes the darker SUBTLE grey
    # that fig2_style reserves for a value line rather than the hairline grey of a frame.
    ax.spines["bottom"].set_position(("data", 0.0))
    ax.spines["bottom"].set_color(SUBTLE)
    ax.spines["bottom"].set_linewidth(0.8)

    title(ax_top, f"{fall} collapses; {holds[0]} and {holds[1]} do not")


if __name__ == "__main__":
    # Mirrors fig2_assemble's ledger for this panel: a 3.45 x 2.21 in box, 0.26 in of letter
    # band, a 0.42 in strip, a 0.08 in gap, a 0.95 in curve axes and a 0.50 in bottom pad.
    BW, BH, LEFT, RIGHT = 3.45, 2.21, 0.72, 0.10
    BAND, STRIP, GAP, CURVE = 0.26, 0.42, 0.08, 0.95
    fig = plt.figure(figsize=(BW, BH))
    w = (BW - LEFT - RIGHT) / BW
    a_top = fig.add_axes([LEFT / BW, 1.0 - (BAND + STRIP) / BH, w, STRIP / BH])
    a_cur = fig.add_axes([LEFT / BW, 1.0 - (BAND + STRIP + GAP + CURVE) / BH, w, CURVE / BH])
    draw_2e(a_cur, a_top)
    fig.savefig(os.path.join(os.path.dirname(__file__), "2e.png"), dpi=300)
    print("wrote 2e.png")
