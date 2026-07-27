"""Extended Data Fig. 6: HIR-Bench, the panels demoted from the main text.

Main-text Fig. 6 keeps only the two HIR-Bench panels that carry argument: the analytic condition
under which subpopulation structure can change a decision at all, and the 2x2 that MEASURES
circularity (oracle-derived features versus observable ones, crossed with an honest versus a
pseudo-replicated cross-validation unit).

The four panels here were in the main text and should not have been. HIR-Bench's phase boundary is
designed into its generator, so recovering it is a check that the benchmark works rather than a
finding about biology; and its transfer to real data fails (Supplementary Note 1). A synthetic
benchmark whose boundary is expected by construction does not earn four main-text panels, and a
reader could reasonably read them as biological evidence. They are kept here because they document
that the benchmark behaves as specified, which is a precondition for trusting the two panels that
did stay.

  a  generative model: a query is a majority plus a minority subpopulation with welfares A and B
  b  energy-minus-mean Hit@1 across the (minority fraction, conflict) grid
  c  best decision regret by information condition; collapsing candidates to their means inflates
     regret most against the worst-welfare objective, which is the one that depends on the minority
  d  benchmark sanity checks: no-conflict flip rate 0.000, median boundary margin 0.27

Run standalone: python ed6.py
"""
import os
import sys

import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..")))

# BROKEN UNTIL 2026-07-27, and it would have produced a figure that silently disagreed with its own
# caption. This file used to do `from fig6a import draw_6a` etc., which was correct only while
# Figure 6 WAS the HIR-Bench figure. Figure 6 was later re-cut into the two-gate figure, so those
# four names now draw the predict-then-rank schematic, Gate 1, the structure diagnostics and the
# Gate 2 mixture: four panels with nothing to do with the four this figure's caption describes.
# The real panels had been parked in figures/fig5/_stale/, whose own README already said they
# "moved to Extended Data"; parking them one directory deeper also broke their
# REPO = dirname/../.. path resolution, so they could not have run from there either. They now live
# beside this file, at the directory depth they were authored for.
from ed6_panel_a import draw_5a
from ed6_panel_c import draw_5c
from ed6_panel_d import draw_5d
from ed6_panel_e import draw_5e

TITLES = {
    "a": "Generative model",
    "b": "Energy $-$ mean Hit@1 across the grid",
    "c": "Best decision regret by information condition",
    "d": "Benchmark sanity checks",
}


def build():
    fig, axes = plt.subplots(2, 2, figsize=(9.4, 6.6))
    fns = [draw_5a, draw_5c, draw_5d, draw_5e]
    for ax, fn, k in zip(axes.ravel(), fns, "abcd"):
        fn(ax)
        ax.set_title(TITLES[k], loc="left", fontsize=8)
        ax.text(-0.14, 1.10, k, transform=ax.transAxes, fontsize=10, fontweight="bold")
    fig.subplots_adjust(hspace=0.55, wspace=0.42)
    fig.savefig(os.path.join(HERE, "edfig6.pdf"), bbox_inches="tight")
    fig.savefig(os.path.join(HERE, "edfig6.png"), dpi=300, bbox_inches="tight")
    print("wrote edfig6.pdf / .png")


if __name__ == "__main__":
    build()
