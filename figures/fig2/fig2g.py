"""PopRetrieve Figure 2 panel 2g: the eight scorers are two families, and the families do not talk.

WHAT THE PANEL CLAIMS
---------------------
One claim, about SCORING RULES and nothing else: the six scorers this export covers split into two
blocks whose members agree strongly inside a block and essentially not at all across blocks. Every
within-family Spearman rho is at least 0.72; the largest cross-family |rho| is 0.076 over nine
pairs. That is why Figure 2 draws two colour families instead of eight separate methods.

Two cells carry the panel and are ringed:
  * mean cosine / CMap cosine = 1.00. It is the largest off-diagonal value in the matrix and it
    equals a diagonal cell to within 1e-10, so it is drawn exactly as dark as a self-correlation.
    This is why panel a treats the two as ONE baseline rather than two.
  * coverage-mean / coverage-worst = 0.97, the closest pair inside the population family.
Both are asserted to be the largest off-diagonal value of their own block at draw time, so the
rings cannot end up on the wrong cells if the export is regenerated.

WHAT THE PANEL DOES NOT CLAIM, AND THIS MATTERS
-----------------------------------------------
This is a similarity between SCORING RULES. Two rules can agree perfectly and both be wrong. The
panel is therefore NOT independent evidence that population-level retrieval works; that evidence
is panels a to f, and whether the retrieved neighbours are biologically better is Figure 3. The
phrase over the panel and the note under it both say "scoring rules", never "retrieval", for that
reason. Nothing here reaches past response matching.

WHICH FILE IT READS
-------------------
figures/source_data/ed1_metric_correlation.csv, a 6 x 6 Spearman matrix. Per
figures/source_data/README.md this file is PRIMARY: it is an input with no upstream parent in
results/, so unlike panels c, d and f there is no authoritative file to move onto. Every number
drawn is read out of it at draw time; none is typed.

COVERAGE, STATED BECAUSE IT IS INCOMPLETE
-----------------------------------------
The export holds six of the eight scorers panel a ranks. pca_dist and pca_mean, the two PCA-latent
baselines, are NOT in it and are not invented here: the panel counts what is present, names the two
that are missing on its own bottom line, and refuses to draw if the missing set stops being exactly
those two. So the block structure shown is a statement about six rules, not about all eight.

The correlation is over 54,180 query-candidate scored pairs (1,260 queries against 43 candidates
each; the unit is the scored PAIR, not the query, which is the correction CORRECTIONS.md R29
makes). That n is NOT printed on the panel, because this CSV is a bare 6 x 6 matrix and does not
carry it: printing it here would mean typing a literal copied from the manuscript, which is exactly
the laundering this deck forbids. The n lives in the caption and in Methods, where it is checkable.

JUDGEMENT CALLS A READER COULD REASONABLY DISAGREE WITH
-------------------------------------------------------
 1. HUE IS FAMILY, SHADE IS |rho|. The Extended Data ancestor of this panel (ed_panels.draw_ed1c)
    used the deck's diverging map, which runs orange to white to blue over rho = -1 to +1. Inside
    Figure 2 that map is unusable: blue means population-level and orange means mean-level here, so
    a diverging map would have painted the mean-cosine block BLUE and said the opposite of what the
    panel measures. Each cell is instead filled with its own family's colour at alpha = 0.85|rho|.
    The cost is that sign is no longer in the colour, which is paid for by note 2.
 2. SIGN IS CARRIED BY THE PRINTED NUMBER, NOT BY THE COLOUR. Legitimate only because every
    off-diagonal value with |rho| >= 0.5 is positive, which is asserted: no dark cell hides a
    negative. The four negative values in the matrix are all cross-family and all above -0.06, so
    they are drawn as very nearly white either way.
 3. CROSS-FAMILY CELLS ARE GREY. Grey is this figure's SHARED colour and there is deliberately no
    third family hue. A cross-family pair that did correlate would still go visibly dark, in grey,
    so the encoding cannot hide a contradiction of the panel's own claim.
 4. THE NINE CROSS-FAMILY NUMBERS ARE NOT PRINTED. One computed line, "9 cross-family pairs / max
    |rho| = 0.076", stands over that block instead. Nine near-zero numbers would have been the
    densest text on the panel while carrying the least information, and the bound is the stronger
    statement. Both the count and the maximum are computed from the file. A reader who wants the
    nine values has them in the source CSV, which is why that CSV is released.
 5. BOTH TRIANGLES ARE COLOURED, NUMBERS APPEAR IN THE LOWER ONE ONLY. The full square is what
    makes the two dark blocks and the two white blocks read as a 2 x 2 arrangement in one glance;
    printing the values twice would double the text for nothing. The upper triangle is a mirror by
    construction, and symmetry is asserted to 1e-12.
 6. THE DIAGONAL IS DRAWN AT FULL STRENGTH even though rho = 1 there is trivial. It is what the
    ringed 1.00 cell is read against: the point is that the mean-cosine / CMap-cosine cell is
    indistinguishable from a self-correlation.
 7. ORDER WITHIN A FAMILY IS CHOSEN, NOT SORTED. mean cosine, CMap cosine, CMap WTCS and then
    energy, coverage-mean, coverage-worst. That ordering puts each family's closest pair
    immediately below the diagonal, so both rings sit on the sub-diagonal. Sorting by value
    instead would have scattered them.
 8. "cov-mean" AND "cov-worst" ARE ABBREVIATED. Six columns share 2.49 in, so a column is 0.40 in
    and the string "coverage-" alone measures 0.427 in at 6.8 pt: the full names do not fit and
    shrinking them below the 6.5 pt floor is not an option. Panel f abbreviates sliced-Wasserstein
    for the same reason. The caption spells both out. The abbreviation is a SUBSTITUTION on the
    fig2_style label ("coverage-" to "cov-"), not a second spelling stored here, and the number of
    labels it fires on is asserted; a rename in fig2_style therefore reaches panel g or breaks the
    build, and cannot leave a and g naming one scorer two ways. Every other label is
    fig2_style.SCORERS verbatim.
 9. NO aspect="equal". At 2.49 x 1.36 in a square matrix would be a small square in a wide box.
    Cells are 0.40 x 0.178 in; a symmetric correlation matrix has no geometric content that
    square cells would preserve, and the rectangle lets every printed value sit at 7.2 pt.
10. NO COLORBAR. Every within-family value is printed and the cross block carries its bound, so a
    ramp would only restate them. The one-line key "cell shade = |rho|" replaces it.

Palette comes from fig2_style; do NOT re-declare hex values here.

Run standalone: python fig2g.py
"""
from __future__ import annotations

import os
import sys

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Rectangle

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fig2_style import (FAMILY_COLOUR, FAMILY_NAME, PT_ANNOT,  # noqa: E402
                        PT_SMALL, PT_TICK, REPO, SCORERS, SHARED, SUBTLE, TEXT,
                        title)

SRC = f"{REPO}/figures/source_data/ed1_metric_correlation.csv"

# Row/column order: the two families, each with its closest pair adjacent to the diagonal. The
# FAMILY of each key is not restated here; it is read from fig2_style.SCORERS and asserted, so a
# regrouping of the vocabulary cannot leave this panel silently mislabelled.
ORDER = ["mean_cosine", "cmap_cosine", "cmap_wtcs",
         "global_energy", "coverage_mean", "coverage_worst"]

# The one shortening applied to a fig2_style label, written as a SUBSTITUTION rather than as a
# second vocabulary: if panel a renames the coverage scorers, panel g renames them the same way or
# the count assertion in draw_2g fires. See docstring note 8.
LONG, SHORT = "coverage-", "cov-"
N_ABBREV = 2         # coverage-mean and coverage-worst, the only labels too wide for a column

# ------------------------------------------------------------------------------ drawing constants
ALPHA_MAX = 0.85     # fill alpha at |rho| = 1. Above this, 7.2 pt ink on POP blue loses contrast.
SHADE_MID = 0.5      # the midpoint of the shading ramp; the block gap is asserted to straddle it
GUT_X, GUT_Y = 0.090, 0.055        # white gutter between the two families, in inches
MATRIX_BOTTOM = 0.240              # inches above the axes floor, reserved for the column labels
CELL_EDGE = 0.5                    # white hairline articulating the cells inside a dark block

LAB_GAP = 0.050      # row label to matrix, in inches
COL_GAP = 0.045      # matrix floor to the top of the column labels
FAM_GAP = 0.050      # column labels to the family key
NOTE_GAP = 0.045     # family key to the first note line
NOTE_STEP = 0.100    # note line pitch
SW_W, SW_H = 0.075, 0.055          # family swatch, in inches
SW_GAP = 0.030


def _stack(label: str) -> str:
    """Break a scorer label into at most two lines, at the space or after the hyphen.

    A column is 0.40 in wide and the longest single token after the break ("coverage" is already
    abbreviated away) is 0.29 in at 6.8 pt, so two lines always clear their column.
    """
    if " " in label:
        head, tail = label.split(" ", 1)
        return f"{head}\n{tail}"
    if "-" in label:
        head, tail = label.split("-", 1)
        return f"{head}-\n{tail}"
    return label


def load_matrix() -> "tuple[pd.DataFrame, list[str]]":
    """The 6 x 6 Spearman matrix in family order, plus the labels of the scorers it does not cover.

    Everything the panel later states about shape is checked here: that the file is a symmetric
    correlation matrix, that its six columns are exactly ORDER, and that ORDER is the two
    fig2_style families in one block each.
    """
    raw = pd.read_csv(SRC, index_col=0)
    assert list(raw.index) == list(raw.columns), f"{SRC} is not a square labelled matrix"
    assert set(raw.columns) == set(ORDER), (
        f"the correlation export no longer holds exactly {sorted(ORDER)}: {sorted(raw.columns)}")

    m = raw.loc[ORDER, ORDER]
    v = m.to_numpy(dtype=float)
    assert np.allclose(v, v.T, rtol=0.0, atol=1e-12), "the correlation matrix is not symmetric"
    assert np.allclose(np.diag(v), 1.0, rtol=0.0, atol=1e-12), "the diagonal is not 1"
    assert np.all(np.abs(v) <= 1.0 + 1e-12), "a value outside [-1, 1]"

    fams = [SCORERS[k]["family"] for k in ORDER]
    assert fams == ["mean"] * 3 + ["pop"] * 3, (
        f"ORDER is no longer two contiguous fig2_style families: {fams}")

    missing = [SCORERS[k]["label"] for k in SCORERS if k not in raw.columns]
    assert sorted(missing) == ["PCA-dist", "PCA-mean"], (
        f"the panel's coverage note names PCA-dist and PCA-mean; the export is missing {missing}")
    return m, missing


def draw_2g(ax):
    """Spearman agreement among six retrieval scoring rules, blocked by representation family."""
    m, missing = load_matrix()
    v = m.to_numpy(dtype=float)
    n = len(ORDER)
    fams = [SCORERS[k]["family"] for k in ORDER]
    labels = [SCORERS[k]["label"].replace(LONG, SHORT) for k in ORDER]
    assert sum(SCORERS[k]["label"].startswith(LONG) for k in ORDER) == N_ABBREV, (
        f"the {LONG!r} prefix no longer names exactly {N_ABBREV} of {ORDER}; panel g would stop "
        "naming a scorer the way panel a names it")

    lower = [(i, j) for i in range(n) for j in range(i)]
    within = [(i, j) for i, j in lower if fams[i] == fams[j]]
    cross = [(i, j) for i, j in lower if fams[i] != fams[j]]
    assert len(within) == 6 and len(cross) == 9, "the 3 + 3 blocking changed shape"

    # The panel's whole claim, refusing to draw itself if the file stops supporting it: every
    # within-family pair sits above the middle of the shading ramp and every cross-family pair
    # below it, so the two dark blocks and the two white blocks are a property of the data.
    w_min = min(v[i, j] for i, j in within)
    c_max = max(abs(v[i, j]) for i, j in cross)
    assert w_min > SHADE_MID > c_max, (
        f"the blocks no longer separate across the shading midpoint: weakest within-family "
        f"{w_min:.4f}, strongest cross-family |rho| {c_max:.4f}")
    # Sign is carried by the printed number, not by the colour; that is only honest while nothing
    # dark is negative. See docstring note 2.
    assert all(v[i, j] > 0 for i, j in lower if abs(v[i, j]) >= SHADE_MID), \
        "a strongly correlated pair is NEGATIVE, so |rho| shading would hide its sign"

    # The two ringed cells: each family's closest pair, which must be the one just under the
    # diagonal for the ring to sit where the layout puts it.
    ring_mean = max((p for p in within if fams[p[0]] == "mean"), key=lambda p: v[p])
    ring_pop = max((p for p in within if fams[p[0]] == "pop"), key=lambda p: v[p])
    assert ring_mean == (1, 0) and ring_pop == (5, 4), (
        f"the closest pair moved off the sub-diagonal: {ring_mean}, {ring_pop}")
    assert abs(v[ring_mean] - 1.0) < 1e-10, (
        f"mean cosine and CMap cosine no longer agree at every pair (rho = {v[ring_mean]:.10f}); "
        "the panel draws that cell as dark as a self-correlation and panel a merges the two")
    assert v[ring_mean] == max(v[p] for p in lower), "1.00 is no longer the largest off-diagonal"

    # -------------------------------------------------------------------- geometry, in inches
    fig = ax.figure
    w_in = ax.get_position().width * fig.get_figwidth()
    h_in = ax.get_position().height * fig.get_figheight()
    ax.set_xlim(0.0, w_in)
    ax.set_ylim(0.0, h_in)          # one data unit is one inch on both axes
    ax.set_xticks([])
    ax.set_yticks([])
    for side in ("left", "right", "top", "bottom"):
        ax.spines[side].set_visible(False)
    ax.set_facecolor("none")

    cw = (w_in - GUT_X) / n
    ch = (h_in - MATRIX_BOTTOM - GUT_Y) / n
    grp_x = [j * cw + (GUT_X if j >= 3 else 0.0) for j in range(n)]          # cell left edges
    grp_y = [h_in - i * ch - (GUT_Y if i >= 3 else 0.0) for i in range(n)]   # cell top edges

    def cell_xy(i, j):
        """Bottom-left corner of cell (row i, column j), in axes inches."""
        return grp_x[j], grp_y[i] - ch

    # -------------------------------------------------------------------- cells
    for i in range(n):
        for j in range(n):
            base = FAMILY_COLOUR[fams[i]] if fams[i] == fams[j] else SHARED
            fill = mcolors.to_rgba(base, ALPHA_MAX * abs(v[i, j]))
            x0, y0 = cell_xy(i, j)
            ax.add_patch(Rectangle((x0, y0), cw, ch, facecolor=fill, edgecolor="white",
                                   linewidth=CELL_EDGE, zorder=2))

    # values, lower triangle only, within-family cells only
    for i, j in within:
        x0, y0 = cell_xy(i, j)
        heavy = (i, j) in (ring_mean, ring_pop)
        ax.text(x0 + cw / 2, y0 + ch / 2, f"{v[i, j]:.2f}", ha="center", va="center",
                fontsize=PT_ANNOT, color=TEXT, fontweight="bold" if heavy else "normal",
                zorder=4)

    # the nine cross-family pairs, as one computed bound instead of nine near-zero numbers
    cx = (grp_x[0] + grp_x[2] + cw) / 2
    cy = (grp_y[3] + grp_y[5] - ch) / 2
    ax.text(cx, cy, f"{len(cross)} cross-family pairs\nmax $|\\rho|$ = {c_max:.3f}",
            ha="center", va="center", fontsize=PT_ANNOT, color=TEXT, linespacing=1.25, zorder=4)

    # the two rings: emphasis by keyline and weight, never by a third colour
    for i, j in (ring_mean, ring_pop):
        x0, y0 = cell_xy(i, j)
        ax.add_patch(Rectangle((x0, y0), cw, ch, facecolor="none", edgecolor=TEXT,
                               linewidth=0.9, zorder=5))

    # -------------------------------------------------------------------- labels
    for i, lab in enumerate(labels):
        ax.text(-LAB_GAP, grp_y[i] - ch / 2, lab, ha="right", va="center",
                fontsize=PT_TICK, color=TEXT, clip_on=False)

    col_top = MATRIX_BOTTOM - COL_GAP
    for j, lab in enumerate(labels):
        ax.text(grp_x[j] + cw / 2, col_top, _stack(lab), ha="center", va="top",
                fontsize=PT_TICK, color=TEXT, linespacing=1.05, clip_on=False)

    # family key: a swatch at the left edge of each block of columns, at the same strength the
    # block itself is drawn at. This is the one place colour may sit beside letters, because the
    # label names a whole family and has no mark of its own.
    fam_top = col_top - 2 * PT_TICK * 1.05 / 72 - FAM_GAP
    for start, fam in ((0, "mean"), (3, "pop")):
        ax.add_patch(Rectangle((grp_x[start], fam_top - SW_H - 0.012), SW_W, SW_H,
                               facecolor=mcolors.to_rgba(FAMILY_COLOUR[fam], ALPHA_MAX),
                               edgecolor="none", clip_on=False, zorder=3))
        ax.text(grp_x[start] + SW_W + SW_GAP, fam_top, FAMILY_NAME[fam], ha="left", va="top",
                fontsize=PT_TICK, color=TEXT, clip_on=False)

    # Three grey lines, in the order a reader needs them: what the number is, how to read the
    # drawing, what the drawing does not cover. The coverage line counts the scorers rather than
    # stating a total, so it cannot outlive a change to the export.
    notes = ["Spearman $\\rho$ between scoring rules, not retrieval evidence",
             "Cell shade = $|\\rho|$; the ring marks each family's closest pair",
             f"{n} of the {len(SCORERS)} scorers in panel a; "
             f"{' and '.join(missing)} absent"]
    y = fam_top - PT_TICK / 72 - NOTE_GAP
    for line in notes:
        ax.text(0.0, y, line, ha="left", va="top", fontsize=PT_SMALL, color=SUBTLE,
                clip_on=False)
        y -= NOTE_STEP

    title(ax, "Score families agree within, not across")


if __name__ == "__main__":
    # The standalone preview is drawn at panel g's real box and real pads, so the inch geometry
    # above is the geometry on the page. These four numbers mirror fig2_assemble's ledger for g
    # (half of a 6.90 in canvas; PADS["g"] = 0.86 left, 0.10 right, 0.50 bottom; the 1.86 in row
    # plus its 0.26 in letter block) and are duplicated rather than imported because importing
    # fig2_assemble would import every sibling panel.
    BOX_W, BOX_H = 3.45, 2.12
    fig = plt.figure(figsize=(BOX_W, BOX_H))
    ax = fig.add_axes([0.86 / BOX_W, 0.50 / BOX_H, 2.49 / BOX_W, 1.36 / BOX_H])
    draw_2g(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "2g.png"), dpi=300)
    print("wrote 2g.png")
