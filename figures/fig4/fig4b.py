"""PopRetrieve Figure 4 panel a: analytic boundary alpha* = B/(A+B)
Source data: results/exp11_hir_benchmark/theoretical_boundary.csv
             (source_data/fig4a_theoretical_boundary.csv is a mirror of it, not read here)
Run standalone: python fig4b.py

2026-08-31 TYPOGRAPHY PASS: to Figure 4's 6.5 pt floor, on the new 1.55 x 1.75 in rect.
------------------------------------------------------------------------------------
RAISED. Eleven artists were under the floor and none is now.
  * The expression, the worst of them. "$\\alpha^*=B/(A{+}B)$" is mathtext with a superscript,
    which matplotlib prints at 0.7x nominal, so at 7.2 pt its star landed at 5.04 pt. PT_EQ = 9.3
    would clear the floor but is above the 7.2 pt cap fig4_assemble._assert_no_titles enforces, so
    the expression cannot be drawn as one mathtext string here at all. It is composed by hand
    instead: three Text artists at PT_SMALL on a measured baseline, the star raised rather than
    superscripted, sharing one gid so the overlap checker reads them as one expression. The model
    is figures/fig1/fig1a.py.
  * Both region labels, 6.2 -> PT_SMALL.
  * Both axis labels, 6.2 -> PT_ANNOT. Neither carries a sub/superscript, so plain mathtext is
    safe for them.
  * The six tick labels, 6.0 -> PT_TICK, by deleting the panel's tick_params(labelsize=...) so
    the rcParams value set by apply_style applies.

CUT INTO THE CAPTION. Nothing, and the measurement is why rather than a preference. The candidate
was the x axis label, which repeats the right-hand side of the expression drawn at the centre of
the panel; at PT_ANNOT "welfare ratio B/(A+B)" measures 0.930 in under a 1.550 in axes, so it fits
with room to spare and shortening it would have been a cut this pass did not have to make. The
region labels and the expression fit at PT_SMALL as well. Every string this panel carried before
the pass, it still carries.

RE-TUNED FOR THE NEW BOX, which is 1.55 x 1.75 in rather than 1.46 x 1.46.
  * The labelpad of 2.0 was measured against the old axes, which sat 0.30 in above the row-2
    banner. The row now ends 0.67 in above it, and the panel's furniture reaches 0.335 in below
    the axes and 0.375 in left of it, inside the 0.55 in of left slack the row allows. So both
    pads go back to the house default instead of staying pinched against a banner that moved.
  * The region labels moved outward, to (0.26, 0.84) and (0.75, 0.15): the taller box lets each
    sit clear of both the boundary line and the expression's plate at the larger size.
  * The plate is now measured from the composed run's ink box rather than set by a Text bbox pad,
    because the run is three artists and no one of them has a bbox that covers the expression.

2026-08-31 AUDIT FIX, on top of that pass: the limits are now set BEFORE the expression is
composed. The run is placed in data coordinates and spaced from ink measured in pixels, so the
measurement was being taken while the fills' autoscale (-0.05, 1.05) was still in force and the
drawing was done after set_xlim(0, 1) had rescaled it. Every measured offset printed 1.1x: the run
sat 1.4 pt left of centre, its plate was padded 1.8 pt on the left and 4.6 pt on the right, and the
-0.10 em kern reached the page as -0.03 em. No number the panel plots was affected; the boundary,
the fills, the limits and the ticks are vertex-identical to the pre-pass panel.
"""
import os
import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# Palette and type ladder come from the house-style module; do NOT re-declare a hex value or a
# point size here. Every panel file used to carry its own copy, which made figstyle's "one edit
# here recolours the whole deck" untrue: a recolour meant editing 43 files and missing one was
# silent. fig4_style is the Figure 4 layer of that: POP blue is the distributional arm, MEAN
# orange the arm for which the mean is a sufficient statistic.
from fig4_style import MEAN, POP, PT_ANNOT, PT_SMALL, TEXT  # noqa: E402

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
H = os.path.join(REPO, "results", "exp11_hir_benchmark")

FILL_ALPHA = 0.14           # both regions, so neither reads as the stronger claim
BOUNDARY_LW = 1.4           # heavier than fig4_style.LW_LINE on purpose: the boundary is this
                            # panel's subject, not one series among several
SUP_RISE_EM = 0.05          # the star's baseline shift, in ems of PT_SMALL. Small on purpose:
                            # the asterisk's own ink already sits at cap height, so a full
                            # superscript shift lifts it clear off the expression.
# ink-to-ink kerns in the composed run, in ems of PT_SMALL, set by measuring the rendered ink.
# What they print, measured off the 1200 dpi render of the composite: the star's ink starts 0.65 pt
# inside the alpha's, so the two just touch as a superscript should, and the "=" carries 1.4 pt of
# air on its left and 1.6 pt on its right, which is the thick space mathtext would have set anyway.
KERN_EM = {"star": -0.10, "rhs": 0.00}
CAP_EM = 0.35               # half a cap height, to hang the run's optical centre on the boundary
PLATE_PAD_EM = 0.28         # white plate around the expression, in ems of PT_SMALL


def _pt_to_axes(ax, pt, vertical):
    """``pt`` points as a fraction of the axes box. Read from the figure, so the panel is
    correct at whatever size it is drawn."""
    w_in, h_in = ax.get_position().size * ax.figure.get_size_inches()
    return pt / 72.0 / float(h_in if vertical else w_in)


def _expression(ax, x, y, parts, gid, zorder=4):
    """Set ``parts`` left to right on one baseline, centred on ``x``, spaced by MEASURED ink.

    ``parts`` is ((text, is_raised, kern_em), ...). Every fragment is drawn at PT_SMALL: that is
    the whole point of composing by hand, because a real mathtext superscript would print at 0.7x
    PT_SMALL, and the only nominal size that survives that, PT_EQ, is above this figure's 7.2 pt
    cap. The fragments share ``gid`` so the QA overlap check treats them as one expression rather
    than as three artists sitting on top of each other.

    Spacing is measured ink edge to ink edge, not anchor to anchor: a mathtext fragment carries
    its own leading space (matplotlib sets a thick space before a relation such as "="), so
    stacking raw advances leaves a gap this panel cannot see and cannot control.

    Returns the run's ink box in axes units, as (x0, y0, x1, y1), so the caller can size the
    white plate from what was actually set rather than from a nominal em.
    """
    fig = ax.figure
    fig.canvas.draw()
    rend = fig.canvas.get_renderer()
    rise = _pt_to_axes(ax, PT_SMALL * SUP_RISE_EM, vertical=True)
    inv = ax.transData.inverted()

    def _x(px):
        return float(inv.transform((px, 0.0))[0])

    arts, cur = [], 0.0
    for txt, raised, kern_em in parts:
        t = ax.text(0.0, y + (rise if raised else 0.0), txt, ha="left", va="baseline",
                    fontsize=PT_SMALL, color=TEXT, zorder=zorder, gid=gid)
        bb = t.get_window_extent(renderer=rend)
        ink_off = _x(bb.x0)                    # ink start relative to the anchor, which is at data x = 0
        ink_w = _x(bb.x1) - _x(bb.x0)
        cur += _pt_to_axes(ax, PT_SMALL * kern_em, vertical=False)
        t.set_x(cur - ink_off)
        cur += ink_w
        arts.append(t)
    for t in arts:
        t.set_x(t.get_position()[0] + x - cur / 2.0)
    boxes = [t.get_window_extent(renderer=rend) for t in arts]
    inv_pt = [(inv.transform((b.x0, b.y0)), inv.transform((b.x1, b.y1))) for b in boxes]
    return (min(p0[0] for p0, _ in inv_pt), min(p0[1] for p0, _ in inv_pt),
            max(p1[0] for _, p1 in inv_pt), max(p1[1] for _, p1 in inv_pt))


def draw_4b(ax):
    """Analytic boundary alpha* = B/(A+B) with decision regions.

    Colour semantics follow fig4_style: the regime in which subpopulation structure can change the
    decision is POP blue (distributional), the regime in which the mean is a sufficient statistic
    is MEAN orange. Those two fills were swapped until 2026-07-26, so this panel read against the
    palette used by every other panel in the paper.
    """
    tb = pd.read_csv(f"{H}/theoretical_boundary.csv")
    if tb.empty:                      # provenance check: the boundary is analytic, but the grid
        raise ValueError(             # it was verified on must exist for this panel to be honest
            f"{H}/theoretical_boundary.csv is empty; the analytic boundary panel is not drawn "
            f"without the grid it was checked against.")
    # boundary curve: alpha_star vs ratio (perfect identity) -> decision line in (ratio, alpha) space
    xx = np.linspace(0, 1, 200)
    ax.fill_between(xx, xx, 1, color=POP, alpha=FILL_ALPHA, lw=0)    # alpha>alpha*: structure matters
    ax.fill_between(xx, 0, xx, color=MEAN, alpha=FILL_ALPHA, lw=0)   # alpha<alpha*: mean sufficient
    ax.plot(xx, xx, color=TEXT, lw=BOUNDARY_LW, zorder=3)
    # 2026-07-26: the region labels used to read "minority optimal / structure matters" and
    # "majority optimal / mean is sufficient". Which side is the minority-optimal one is already
    # given by the y axis (majority fraction alpha) and stated in the caption; what the reader
    # needs on the panel is which regime each fill means. 2026-08-31: raised to PT_SMALL and moved
    # outward into the corners the taller box opened up.
    ax.text(0.26, 0.84, 'structure\nmatters', fontsize=PT_SMALL, color=TEXT,
            ha='center', va='center')
    ax.text(0.75, 0.15, 'mean is\nsufficient', fontsize=PT_SMALL, color=TEXT,
            ha='center', va='center')
    # The limits are fixed HERE, before the expression is composed, and that order is load-bearing
    # rather than cosmetic. The run and its plate are placed in DATA coordinates and spaced from ink
    # measured in pixels, so the data-to-pixel scale has to be final at the moment of measurement.
    # Left where it was, below, the fills' autoscale (-0.05, 1.05) was the scale in force while the
    # kerns were measured and (0, 1) was the scale they were drawn at: every measured offset came
    # out 1.1x, which pushed the run 1.4 pt off centre, left the plate padded 1.8 pt on one side and
    # 4.6 pt on the other, and turned the -0.10 em kern below into -0.03 em on the page.
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    # The expression sits ON the boundary it names, so it needs a plate to be legible. The plate is
    # measured from the composed run instead of coming from a Text bbox, because a per-fragment
    # bbox would inflate each fragment's measured advance and break the spacing.
    gid = "alpha-star-expression"
    y_base = 0.5 - _pt_to_axes(ax, PT_SMALL * CAP_EM, vertical=True)   # centre the run ON the line
    ex0, ey0, ex1, ey1 = _expression(ax, 0.5, y_base, (
        (r'$\alpha$', False, 0.0),      # mathtext, no sub/superscript, so it prints at nominal
        ('*', True, KERN_EM["star"]),   # the star, raised rather than superscripted
        # the leading \! cancels the thick space matplotlib sets before a relation: the star
        # already separates the two sides, and the kern above is what sets that gap
        (r'$\!=B/(A{+}B)$', False, KERN_EM["rhs"]),
    ), gid=gid)
    pad_x = _pt_to_axes(ax, PT_SMALL * PLATE_PAD_EM, vertical=False)
    pad_y = _pt_to_axes(ax, PT_SMALL * PLATE_PAD_EM, vertical=True)
    ax.add_patch(Rectangle((ex0 - pad_x, ey0 - pad_y),
                           (ex1 - ex0) + 2.0 * pad_x, (ey1 - ey0) + 2.0 * pad_y,
                           fc='white', ec='none', zorder=3.5))
    # the full form is kept: at PT_ANNOT it measures 0.930 in under a 1.550 in axes, so raising it
    # from 6.2 pt costs the panel nothing and the reader still gets the ratio's definition without
    # going to the caption
    ax.set_xlabel(r'welfare ratio $B/(A{+}B)$', fontsize=PT_ANNOT)
    # 2026-09-06: MAJORITY, not minority. HIR-Bench's alpha is the weight of the FIRST
    # subpopulation: heterogeneous_retrieval_benchmark.generate_hir_cell sets
    # weights[0] = majority_fraction, exp11_hir_benchmark.py passes majority_fraction=params
    # ['alpha'], and the grid holds 0.85 and 0.95, values no minority fraction can take. The
    # fills above are already right under that reading and the data agree: of the 12,768 rows of
    # theoretical_boundary.csv, 8,640 of the 10,644 with alpha > alpha_star flip and none of the
    # 2,124 below it does. Only this label was inverted.
    ax.set_ylabel(r'majority fraction $\alpha$', fontsize=PT_ANNOT)
    ax.set_xticks([0, 0.5, 1.0]); ax.set_yticks([0, 0.5, 1.0])
    # no tick_params(labelsize=...) here: the panel used to pin 6 pt, under the floor. The tick
    # size is rcParams["xtick.labelsize"], which apply_style sets to fig4_style.PT_TICK.
    for sp in ['right', 'top']: ax.spines[sp].set_visible(False)
    # no ax.set_title: fig4_assemble._assert_no_titles keeps this panel free of a conclusion


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(1.55, 1.75))
    draw_4b(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "4b.png"), dpi=300, bbox_inches="tight")
    print("wrote 4b.png")
