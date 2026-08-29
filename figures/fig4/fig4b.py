"""PopRetrieve Figure 4 panel 4b: analytic boundary alpha*=B/(A+B)
Source data: results/exp11_hir_benchmark/theoretical_boundary.csv
             (source_data/fig4a_theoretical_boundary.csv is a mirror of it, not read here)
Run standalone: python fig4b.py
"""
import os, sys, numpy as np, pandas as pd, matplotlib as mpl, matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from figstyle import PT_MATH
# Palette comes from the house-style module; do NOT re-declare the hex values here. Every
# panel file used to carry its own copy, which made figstyle's "one edit here recolours the
# whole deck" untrue: a recolour meant editing 43 files and missing one was silent.
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
from figstyle import FOCAL_SOFT, COMP_SOFT, GREY, INK  # noqa: E402
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
H = os.path.join(REPO, "results", "exp11_hir_benchmark")
S = os.path.join(REPO, "results", "exp11_synthetic_phase_diagram")

def draw_4b(ax):
    """Analytic boundary alpha* = B/(A+B) with decision regions.

    Colour semantics follow the deck: the regime in which subpopulation structure can change the
    decision is FOCAL_SOFT blue (distributional), the regime in which the mean is a sufficient statistic
    is COMP_SOFT orange (mean / collapse). Those two fills were swapped until 2026-07-26, so this panel
    read against the palette used by every other panel in the paper.
    """
    tb = pd.read_csv(f"{H}/theoretical_boundary.csv")
    if tb.empty:                      # provenance check: the boundary is analytic, but the grid
        raise ValueError(             # it was verified on must exist for this panel to be honest
            f"{H}/theoretical_boundary.csv is empty; the analytic boundary panel is not drawn "
            f"without the grid it was checked against.")
    # boundary curve: alpha_star vs ratio (perfect identity) -> decision line in (ratio, alpha) space
    xx = np.linspace(0, 1, 200)
    ax.fill_between(xx, xx, 1, color=FOCAL_SOFT, alpha=0.14, lw=0)   # alpha>alpha*: structure matters
    ax.fill_between(xx, 0, xx, color=COMP_SOFT, alpha=0.14, lw=0)    # alpha<alpha*: mean sufficient
    ax.plot(xx, xx, color=INK, lw=1.4, zorder=3)
    # 2026-07-26: the region labels used to read "minority optimal / structure matters" and
    # "majority optimal / mean is sufficient". At the figure's print width this panel is 1.46 in
    # wide and those two lines were 0.73 in of text each, i.e. half the panel, overlapping the
    # boundary line and the alpha* box. Which side is the minority-optimal one is already given by
    # the y axis (minority fraction alpha) and stated in the caption; what the reader needs on the
    # panel is which regime each fill means.
    ax.text(0.28, 0.80, 'structure\nmatters', fontsize=6.2, color=INK,
            ha='center', va='center')
    ax.text(0.73, 0.17, 'mean is\nsufficient', fontsize=6.2, color=INK,
            ha='center', va='center')
    # PT_MATH, not 7: matplotlib prints a superscript at 0.7x nominal, so this label set at
    # 7 pt printed its star at 4.9 pt, under the 5 pt production floor.
    ax.text(0.5, 0.5, r'$\alpha^*=B/(A{+}B)$', fontsize=PT_MATH, color=INK, ha='center',
            va='center',
            zorder=4, bbox=dict(fc='white', ec='none', pad=1.6))
    # tight label pad: this axis label is the last line of row 1 and the row-2 banner is
    # 0.30 in below it on the 6.9 in canvas
    ax.set_xlabel(r'welfare ratio $B/(A{+}B)$', fontsize=6.2, labelpad=2.0)
    ax.set_ylabel(r'minority fraction $\alpha$', fontsize=6.2, labelpad=2.0)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.set_xticks([0, 0.5, 1.0]); ax.set_yticks([0, 0.5, 1.0])
    ax.tick_params(labelsize=6)
    for sp in ['right', 'top']: ax.spines[sp].set_visible(False)
    # the composite sets the title (fig4_assemble.TITLES); it is set here only so the panel can be
    # run standalone, and the composite overwrites it


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(3.5,3.0))
    draw_4b(ax)
    ax.set_title(r"The mean suffices below $\alpha^*$", loc='left', fontsize=8)
    fig.savefig(os.path.join(os.path.dirname(__file__), "4b.png"), dpi=200, bbox_inches="tight")
    print("wrote 4b.png")
