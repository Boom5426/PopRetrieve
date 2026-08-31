"""PopRetrieve Figure 3 panel 3b: the mechanism-recovery null, one ECDF per cell line.

WHAT THIS PANEL CLAIMS
----------------------
Panel a reports one number for mechanism recovery on the 480 paired queries: a median
population-minus-mean MoA-nDCG gain of exactly 0.000. A single median can be produced by a
handful of large values on either side, or by one cell line dragging two others. This panel shows
it is neither. The whole cumulative distribution is drawn for each cell line separately, and all
three cross the 0.5 level inside the same vertical step at zero, so each of the three medians is
exactly 0.000 on its own. The step itself is the second fact: between 21 and 26 per cent of
queries per cell line score IDENTICALLY under population-level and mean-signature retrieval, which
is a property of the data and not a plotting artifact.

The panel does NOT claim the distribution is symmetric about zero. It is not: the pooled mean is
negative and the left tail is longer than the right. That is panel a's business, and here it shows
as the long shallow left approach: every curve has already climbed to between 0.37 and 0.46 by the
time it reaches the step, and the ink right of the step is squeezed into a shorter x range (+0.55
at the most, against -0.79 on the left). No curve is above 0.5 anywhere left of zero, which is the
same fact the median assertion states. What is claimed is only what is labelled, the median and the
tie mass, and both are asserted in code before anything is drawn.

SOURCE
------
figures/source_data/fig3a_classA_vs_classB.csv, column ``classB_moa_ndcg_gain``, split by
``cell_line``. The same 480 rows panel a draws, one row per (cell line, held-out drug, seed),
no key repeated. 127 distinct held-out drugs overall, 109 / 107 / 120 per cell line;
``seed`` takes five values, but the design is UNBALANCED, one to four seeds per (cell line, drug)
rather than five, so a drug contributes between one and four rows. ``observed_library_fraction``
is 1.0 throughout. Verified at draw time: A549 n=157, K562 n=146, MCF7 n=177; medians 0.000,
0.000, 0.000; ties 21.7%, 25.3%, 26.0%; pooled range -0.788 to +0.546.

The unit therefore matters, and it was checked rather than assumed. Collapsing the seeds first,
one mean per (cell line, drug), leaves every median exactly 0.000 as well, so the panel's headline
does not depend on the choice. The tie percentage does depend on it (19.3 / 20.6 / 25.0 at drug
level against 21.7 / 25.3 / 26.0 here), so the tie label counts QUERIES, and the caption has to
say so along with the three n. The column is signed population minus mean, so positive is a
population-level win; that orientation comes from the column's definition, not from anything this
module can recompute, and it is stated in the x label rather than assumed.

JUDGEMENT CALLS A READER COULD DISAGREE WITH
--------------------------------------------
1. The three cell lines are ONE grey with three dash patterns. They used to be three tints of the
   deck's population blue, which spent the figure's most meaningful hue on a nuisance variable
   and invited a method contrast to be read into a within-method stratification. The colour slot
   belongs to the sign of the difference, so the half-planes carry it and the curves do not.
   Cost: three dash patterns are harder to tell apart at 2.10 in than three hues would be. That
   is accepted, because which curve is which barely matters here; the claim is that all three do
   the same thing.
2. The medians are stated as a column in the key rather than marked on the curves. All three sit
   at the same point, (0, 0.5), so three markers would land on top of each other and read as one.
   The key is the honest form: it names each line and prints its own median beside it.
3. The x view is symmetric at +/- 1.03 x the largest absolute value, so no query is clipped and
   zero is the geometric centre of the panel. This leaves the far right visibly emptier than the
   far left. That asymmetry is real (the longest tail is a mean-side loss of -0.788) and is left
   visible rather than cropped away.
4. The minus signs are U+2212, set in the panel's own sans face, not mathtext. A mathtext minus
   would render in a different family at this size for no gain, and it drags the label into the
   PT_EQ rule the figure applies to anything carrying mathtext.
5. Only three x ticks are labelled. At this width the -0.25 and -0.5 labels are wider than the
   gap between them, and a tick grid the reader cannot resolve is worse than a coarse one; minor
   ticks mark the quarter points.
6. The tie range on the panel is rounded OUTWARD to whole per cent (21-26), not to nearest
   (which would print 22-26 and exclude A549's own 21.7). A printed interval has to contain the
   data it summarises; the exact three are in the SOURCE block above and belong in the caption.
7. Per-line n is not on the panel. A third key column does not fit beside the medians at 7.2 pt,
   and between the two the medians are what the panel exists to state. The three n belong in the
   caption.
8. The zero rule is drawn FAINT rather than at the usual SUBTLE weight, and under the curves.
   The three steps lie exactly ON x = 0, so a darker rule there would compete with the data it
   marks. Zero is still unmistakable: it is the boundary between the two half-plane washes, a
   labelled tick, and the x position of the largest feature in the panel.
9. The 0.5 hairline is drawn. It is not data; it is the level at which an ECDF gives the median,
   and without it "the medians are zero" is a claim the reader has to take on trust rather than
   read off the crossing.

Run standalone: python fig3b.py
"""
from __future__ import annotations

import math
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fig3_style import (FAINT, LW_HAIR, LW_LINE, PT_ANNOT, PT_SMALL, PT_TICK,  # noqa: E402
                        REPO, SHARED, SUBTLE, TEXT, bare_axes, sign_field, title, zero_rule)

SRC = os.path.join(REPO, "figures", "source_data", "fig3a_classA_vs_classB.csv")
COL = "classB_moa_ndcg_gain"

# Cell line, dash pattern. Order is the order of the key, top to bottom. Shape and stroke only:
# see fig3_style, a cell line is never a hue.
LINES = [("A549", (0, ())), ("K562", (0, (2.6, 1.3))), ("MCF7", (0, (0.9, 1.2)))]

VIEW_PAD = 1.03      # the symmetric x view, as a multiple of the largest absolute gain
X_TICKS = (-0.5, 0.0, 0.5)             # labelled
X_TICKS_MINOR = (-0.75, -0.25, 0.25, 0.75)

# The two text blocks, in axes fraction. They sit in corners the curves cannot reach, and
# _numbers proves that from the data instead of from one reading of one rendering: no curve may
# rise above ANN_FLOOR anywhere left of zero, and none may fall below KEY_TOP anywhere right of
# KEY_X0. Both bounds are set well clear of the blocks' measured ink (0.69 and 0.62), so a data
# change that would put a curve through a label breaks the build instead of printing over it.
ANN_X, ANN_TOP, ANN_FLOOR = 0.475, 0.97, 0.66
KEY_X0, KEY_X1, KEY_NAME_X, KEY_NUM_X = 0.545, 0.615, 0.638, 0.800
KEY_TOP, KEY_HEAD_Y, KEY_Y0, KEY_DY = 0.66, 0.585, 0.44, 0.145


def _numbers():
    """Read the per-cell-line gains and verify everything the panel's labels assert.

    Returns (per-line dicts in LINES order, view half-width, tie percentage endpoints). Nothing
    is drawn until these hold, so a printed median cannot outlive the file it came from.
    """
    if not os.path.exists(SRC):
        raise FileNotFoundError(
            f"Figure 3b needs {SRC}, which does not exist. Rebuild the Figure 3 source tables "
            f"before rebuilding this panel; this module will not invent a distribution.")
    tab = pd.read_csv(SRC)
    if COL not in tab.columns:
        raise KeyError(f"{SRC} has no column {COL!r}; it holds {list(tab.columns)}")
    want = {name for name, _ in LINES}
    have = set(tab["cell_line"].unique())
    assert have == want, f"the panel draws {sorted(want)}; the file holds {sorted(have)}"

    half = VIEW_PAD * float(np.max(np.abs(tab[COL].to_numpy(dtype=float))))
    assert half > max(abs(t) for t in X_TICKS + X_TICKS_MINOR), (
        f"the view is +/- {half:.3f}, narrower than the tick grid the panel sets")
    key_x0 = (2.0 * KEY_X0 - 1.0) * half     # where the key starts, in data units

    rows = []
    for name, dash in LINES:
        v = np.sort(tab.loc[tab["cell_line"] == name, COL].to_numpy(dtype=float))
        n = v.size
        assert n > 3, f"{name} has {n} queries, too few for an ECDF"
        med = float(np.median(v))
        # The key prints this median to three decimals. It is exactly zero, not rounded to it,
        # and the panel says so; a shift of even one query would trip this.
        assert med == 0.0, f"the key prints {name} median 0.000, but it is {med:.6f}"
        f_below = float((v < 0.0).mean())      # ECDF just left of the step
        f_at = float((v <= 0.0).mean())        # ECDF at the top of the step
        # The visual claim: each curve crosses the drawn 0.5 hairline inside the step at zero.
        # This is what makes "median 0.000" readable off the panel rather than only off the key.
        assert f_below < 0.5 <= f_at, (
            f"{name} does not cross 0.5 inside the step at zero: F(0-) = {f_below:.4f}, "
            f"F(0) = {f_at:.4f}")
        ties = f_at - f_below
        # "the step at zero" names the largest single jump in each curve. Check that it is.
        _, counts = np.unique(v, return_counts=True)
        assert counts.max() == round(ties * n), (
            f"{name}: the step at zero holds {round(ties * n)} queries but the tallest step "
            f"holds {counts.max()}, so it is not the feature the label points at")
        assert v[0] >= -half and v[-1] <= half, (
            f"{name} runs outside the drawn view; the panel would clip data silently")
        # The two text blocks stand in the corners this curve leaves empty. Left of zero the
        # curve tops out at f_below; right of the key's left edge it never comes back down.
        assert f_below < ANN_FLOOR, (
            f"{name} reaches {f_below:.3f} left of zero, into the tie annotation at {ANN_FLOOR}")
        f_key = float((v <= key_x0).mean())
        assert f_key > KEY_TOP, (
            f"{name} is at {f_key:.3f} where the key starts, below its top edge {KEY_TOP}")
        rows.append({"name": name, "dash": dash, "v": v, "n": n, "med": med,
                     "f_below": f_below, "f_at": f_at, "ties": ties})

    # The panel prints ONE range for three cell lines, so its endpoints are rounded OUTWARD.
    # Rounding the low end to nearest would print 22 for A549's 21.7 and state an interval that
    # does not contain its own data, which is the exact move this paper exists to object to.
    lo, hi = min(r["ties"] for r in rows), max(r["ties"] for r in rows)
    lo_pct, hi_pct = int(math.floor(100 * lo)), int(math.ceil(100 * hi))
    for r in rows:
        assert lo_pct <= 100 * r["ties"] <= hi_pct, (
            f"the panel prints {lo_pct}-{hi_pct}% exact ties, which excludes {r['name']} at "
            f"{100 * r['ties']:.2f}%")
    return rows, half, (lo_pct, hi_pct)


def _ecdf(v, left, right):
    """Step coordinates for the empirical CDF of ``v``, drawn with drawstyle 'steps-post'.

    Ties are kept as a single vertical rise at their shared value, which is the whole point of
    this panel: the jump at zero must be one step of its true height, not a stack of hairlines.
    """
    xs, counts = np.unique(v, return_counts=True)
    ys = np.cumsum(counts) / v.size
    x = np.concatenate([[left], xs, [right]])
    y = np.concatenate([[0.0], ys, [ys[-1]]])
    return x, y


def draw_3b(ax):
    """Per-cell-line ECDF of the population-minus-mean MoA-nDCG gain, against zero."""
    rows, half, (lo_pct, hi_pct) = _numbers()

    # The sign lives in the background, never in the curves: mean-signature retrieval is
    # favoured left of zero, population-level retrieval right of it.
    mean_half, pop_half = sign_field(ax, vertical=True, at=0.0, pop_side="right", zorder=0)
    # sign_field spans +/- 1e9 in data units and relies on axes clipping, so no ink escapes; but
    # an unclipped window extent that wide is reported as ink outside the panel box by the
    # per-panel QA harness. The two patches are trimmed to the view set below, which changes
    # nothing that is drawn and makes the reported extent the truth. Their y is in axes
    # fraction (axvspan uses get_xaxis_transform), so the height is 0 to 1.
    mean_half.set_bounds(-half, 0.0, half, 1.0)
    pop_half.set_bounds(0.0, 0.0, half, 1.0)
    zero_rule(ax, at=0.0, vertical=True, color=FAINT, lw=0.8, zorder=1)
    # The level at which an ECDF reads out the median.
    ax.axhline(0.5, color=FAINT, lw=LW_HAIR, zorder=1)

    for r in rows:
        x, y = _ecdf(r["v"], -half, half)
        ax.plot(x, y, drawstyle="steps-post", color=SHARED, lw=LW_LINE, ls=r["dash"],
                solid_capstyle="butt", dash_capstyle="butt", zorder=3)

    # The step at zero, named once, right beside it. It sits in the upper-left corner, which
    # _numbers has already proved empty: no curve reaches ANN_FLOOR anywhere left of zero.
    ax.text(ANN_X, ANN_TOP, f"step at zero:\n{lo_pct}-{hi_pct}% exact ties",
            transform=ax.transAxes, ha="right", va="top", fontsize=PT_ANNOT, color=TEXT,
            linespacing=1.22, zorder=5)

    # The key IS the median statement: each cell line, its dash, and its own median, one place,
    # one size. Same guarantee mirrored: _numbers has proved every curve is above KEY_TOP by the
    # time it reaches KEY_X0, so the lower-right corner is empty ink too.
    ax.text(KEY_NUM_X, KEY_HEAD_Y, "median", transform=ax.transAxes, ha="left", va="center",
            fontsize=PT_SMALL, color=SUBTLE, zorder=5)
    for i, r in enumerate(rows):
        y = KEY_Y0 - KEY_DY * i
        ax.add_line(Line2D([KEY_X0, KEY_X1], [y, y], transform=ax.transAxes, color=SHARED,
                           lw=LW_LINE, ls=r["dash"], solid_capstyle="butt",
                           dash_capstyle="butt", zorder=5))
        ax.text(KEY_NAME_X, y, r["name"], transform=ax.transAxes, ha="left", va="center",
                fontsize=PT_ANNOT, color=TEXT, zorder=5)
        ax.text(KEY_NUM_X, y, f"{r['med']:.3f}", transform=ax.transAxes, ha="left", va="center",
                fontsize=PT_ANNOT, color=TEXT, zorder=5)

    bare_axes(ax)
    ax.set_xlim(-half, half)
    ax.set_ylim(0.0, 1.0)
    ax.set_xticks(list(X_TICKS))
    ax.set_xticklabels(["\u22120.5", "0", "0.5"], fontsize=PT_TICK)
    ax.set_xticks(list(X_TICKS_MINOR), minor=True)
    ax.tick_params(axis="x", which="minor", length=1.3, width=0.6, color=FAINT)
    ax.set_yticks([0.0, 0.5, 1.0])
    ax.set_yticklabels(["0", "0.5", "1"], fontsize=PT_TICK)
    ax.set_xlabel("MoA-nDCG gain\npopulation \u2212 mean", fontsize=PT_ANNOT, color=TEXT,
                  linespacing=1.20, labelpad=1.5)
    ax.set_ylabel("cumulative\nfraction", fontsize=PT_ANNOT, color=TEXT, linespacing=1.20,
                  labelpad=1.5)
    title(ax, "Median exactly zero in every cell line")
    return ax


if __name__ == "__main__":
    # Reproduce the printed geometry exactly: panel box 2.90 x 1.26 in, axes 2.10 x 0.82 in at
    # the pads fig3_assemble gives panel b, so the preview is what the composite prints.
    BOX_W, BOX_H, LEFT, BOTTOM, AX_W, AX_H = 2.90, 1.26, 0.70, 0.44, 2.10, 0.82
    fig = plt.figure(figsize=(BOX_W, BOX_H))
    ax = fig.add_axes([LEFT / BOX_W, BOTTOM / BOX_H, AX_W / BOX_W, AX_H / BOX_H])
    draw_3b(ax)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "3b.png")
    fig.savefig(out, dpi=300)
    print(f"wrote {out}")
