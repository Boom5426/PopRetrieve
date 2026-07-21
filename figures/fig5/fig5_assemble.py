"""DART Figure 5: The benchmark decides the answer.

WHY THESE TWO THINGS ARE NOW ONE FIGURE
---------------------------------------
This used to be HIR-Bench alone (six panels), with the natural-heterogeneity test as a separate
Figure 7 (three panels). They are the same argument approached from opposite ends, and splitting
them hid that:

  ROW 1, FROM THE INSIDE. In a synthetic benchmark the latent utility oracle is known, so
  circularity stops being something one argues about and becomes something one measures: every
  feature can be labelled oracle-derived or observable and the inflation read off a dial.

  ROW 2, FROM THE OUTSIDE. Take a benchmark we constructed (cell-line mixtures) and check it
  against tissue nobody assembled (patient glioblastoma). It misled us in BOTH directions at once,
  and both distortions happened to flatter our own premise.

HIR-Bench is also cut from six panels to two, which is the right size for it. Its phase boundary is
designed in and its transfer to real data fails, so it earns main-text space only for the analytic
condition and for the circularity measurement, which is the one place in this paper where
circularity is quantified rather than asserted. The generative schematic (old 6a), the Hit@1 grid
(6c), the regret decomposition (6d) and the sanity checks (6e) move to Extended Data.

Earlier titles for 6c/6d/6f described panels other than the ones drawn; a title that contradicts
its own axes is the same class of error this paper is about, and they were fixed on 2026-07-12.
"""
import os
import sys

import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..")))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "fig7")))

from fig5b import draw_5b                        # analytic flip boundary
from fig5f import draw_5f                        # 2x2: observable vs oracle-derived x CV unit
from fig5_shape import draw_shape                # the oracle's SHAPE picks the winner (real data)
from fig5_gate2 import draw_gate2                # Gate 2, same construct in both settings
from fig7_natural import draw_b as draw_nat_gate1
from fig7_natural import draw_c as draw_nat_premise

TITLES = {
    "a": "Analytic condition for structure to matter",
    "b": "Circularity, measured rather than argued",
    "c": "The oracle's shape picks the winner",
    "d": "Gate 2, asked the same question twice",
    "e": "Gate 1: we overstated divergence",
    "f": "The mean already ranks most of it",
}
ROW_LABELS = [
    "The criterion decides: analytically, inside a synthetic benchmark, and between two real "
    "external oracles",
    "From the outside: our constructed benchmark, checked against tissue nobody assembled",
]


def build(apply_style, panel_letter):
    apply_style(sizes=(8, 7, 6))
    fig = plt.figure(figsize=(11.6, 6.6))
    gs = fig.add_gridspec(2, 6, height_ratios=[0.90, 1.0], hspace=0.70, wspace=1.15,
                          left=0.062, right=0.958, top=0.868, bottom=0.095)
    spans = {"a": (0, 0, 2), "b": (0, 2, 4), "c": (0, 4, 6),
             "d": (1, 0, 2), "e": (1, 2, 4), "f": (1, 4, 6)}
    fns = {"a": draw_5b, "b": draw_5f, "c": draw_shape,
           "d": draw_gate2, "e": draw_nat_gate1, "f": draw_nat_premise}

    row_first = {}
    for k, (rr, c0, c1) in spans.items():
        ax = fig.add_subplot(gs[rr, c0:c1])
        fns[k](ax)
        ax.set_title(TITLES[k], loc="left", fontsize=7.6)
        panel_letter(ax, k, case="lower")
        row_first.setdefault(rr, ax)

    for rr, txt in enumerate(ROW_LABELS):
        y = row_first[rr].get_position().y1 + 0.048
        fig.text(0.055, y, txt, fontsize=7.2, fontweight="bold", color="#1A1A1A")

    fig.savefig(os.path.join(HERE, "fig5_benchmarks.png"), dpi=300, bbox_inches="tight")
    fig.savefig(os.path.join(HERE, "fig5_benchmarks.pdf"), bbox_inches="tight")
    print("wrote fig5_benchmarks.png / .pdf")
    return fig


if __name__ == "__main__":
    from figstyle import apply_style, panel_letter
    build(apply_style, panel_letter)
