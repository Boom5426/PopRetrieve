"""Extended Data Fig. 6: HIR-Bench, the panels demoted from the main text.

Main-text Fig. 5 keeps only the two HIR-Bench panels that carry argument: the analytic condition
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
# caption. This file used to import its panels from the main-text figure directory that held the
# HIR-Bench panels at the time. That figure was later re-cut into the two-gate figure, so the
# imported names went on resolving but drew the predict-then-rank schematic, Gate 1, the structure
# diagnostics and the Gate 2 mixture: four panels with nothing to do with the four this figure's
# caption describes. The panel functions here are now named draw_ed6a..d after the figure they
# actually belong to, so no main-deck renumbering can silently re-point them again.
# The real panels had been parked in figures/fig4/_stale/, whose own README already said they
# "moved to Extended Data"; parking them one directory deeper also broke their
# REPO = dirname/../.. path resolution, so they could not have run from there either. They now live
# beside this file, at the directory depth they were authored for.
from figstyle import apply_style, panel_letter, soften_axes, strip_titles  # noqa: E402

from ed6_panel_a import draw_ed6a
from ed6_panel_c import draw_ed6b
from ed6_panel_d import draw_ed6c
from ed6_panel_e import draw_ed6d

TITLES = {
    "a": "Generative model",
    "b": "Energy $-$ mean Hit@1 across the grid",
    "c": "Best decision regret by information condition",
    "d": "Benchmark sanity checks",
}


def build():
    # THE HOUSE STYLE IS APPLIED HERE, and was not before. This figure drew on matplotlib's
    # defaults: 10 pt DejaVu Sans, 1.5 pt lines, framed legends, four spines. Against the 6.9 in
    # SI text block that is roughly twice the type size of every other figure in the submission,
    # which is why it read as a different document. apply_style() is the same call the main deck
    # makes, so this figure now shares its type ladder, palette and spine rules.
    apply_style(sizes=(8, 7, 6))
    # Authored at the printed width; see the note in ed5.py. The previous 9.4 in canvas
    # printed at 0.81x against the 6.93 in SI text block.
    fig, axes = plt.subplots(2, 2, figsize=(6.9, 5.4))
    fns = [draw_ed6a, draw_ed6b, draw_ed6c, draw_ed6d]
    for ax, fn, k in zip(axes.ravel(), fns, "abcd"):
        fn(ax)
        ax.set_title(TITLES[k], loc="left", fontsize=8)
        panel_letter(ax, k, dx=-0.14, dy=1.12, case="lower")
    # Extended Data panels carry no titles either. This figure's caption already has four
    # per-panel entries, so a drawn title is the same sentence printed twice; TITLES stays as
    # the declaration of what each panel must show, and a standalone preview still uses it.
    soften_axes(fig)
    strip_titles(fig)
    fig.subplots_adjust(hspace=0.42, wspace=0.42)
    fig.savefig(os.path.join(HERE, "edfig6.pdf"), bbox_inches="tight")
    fig.savefig(os.path.join(HERE, "edfig6.png"), dpi=300, bbox_inches="tight")
    print("wrote edfig6.pdf / .png")


if __name__ == "__main__":
    build()
