"""Figure 4 panel a: the control that makes panel b's reversal mean anything.

WHAT THIS PANEL SHOWS
---------------------
Panel b reports that two RNA rankings swap places when the external protein evaluator is rebuilt
from a mean into a distribution. That is only interesting if nothing else swapped with it, and
"nothing else" is a claim about the experiment rather than about the numbers, so it is drawn
rather than asserted in a caption a reader has to take on trust.

Three things are held fixed across the two columns of panel b and the schematic says so by
construction:

  * the CELLS. One Perturb-CITE-seq experiment, RNA and 20 surface proteins measured in the same
    cells, joined on the barcode. Neither column sees a cell the other does not.
  * the RANKINGS. The same two RNA scorers, an energy distance between response clouds and a
    cosine between mean response vectors, producing the same two orderings in both columns.
  * the PROTEIN MEASUREMENTS. The same control-centred protein responses feed both evaluator
    forms.

What changes is one thing: whether the protein readout is collapsed to a mean before the two
candidates are compared, or compared as cell clouds. The panel is drawn so that the single
branching point is the only place the two paths differ.

WHY THIS IS ITS OWN PANEL
-------------------------
It was inside panel b's caption, as the clause "same cells, same proteins, same rankings". A
caption clause is where a reader least expects to find the control that licenses the result, and
this figure's whole argument is that an external evaluator is not automatically a neutral judge.
The design IS the argument, so it gets the space to be seen.

NO NUMBER IS DRAWN HERE. The schematic carries structure; every value is in panels b and c and in
docs/phase2/FINAL_FIGURE_NUMBER_LEDGER.md. The two cell counts it does name, the protein panel
size and the joined cell count, are read from the provenance block that
analysis/class_c/oracle_shape_test.py writes into its own result file, so they cannot drift from
the run that produced the panels beside this one.

Run standalone: python3 fig4_design.py
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle  # noqa: E402

from fig4_style import MEAN, POP, PT_ANNOT, PT_SMALL, REPO, SHARED, SUBTLE, TEXT  # noqa: E402

# The axes fig4_assemble.RECTS gives panel a, in inches. Every length below is authored on
# the printed page and converted here, because a swatch is a physical mark and a fraction
# of a box is not.
AX_W_IN, AX_H_IN = 3.28, 1.75
STUB_W_IN = 0.085           # the key's mark: shorter than the 6.5 pt name beside it
STUB_GAP_IN = 0.030         # mark -> its name, so the pair reads as one token
STUB_H_IN = 0.026           # a little under the x-height it sits against

SRC = f"{REPO}/results/upgrade/oracle_shape_test.json"
# The join provenance is a SEPARATE file the same script writes; the two counts this
# panel names live there rather than in the result file.
PROV = f"{REPO}/results/upgrade/oracle_shape_join_provenance.json"

# The boxes, in axes fractions: (x0, y0, w, h).
SRC_BOX = (0.135, 0.845, 0.730, 0.150)
RNA_BOX = (0.010, 0.455, 0.375, 0.230)
PRO_BOX = (0.520, 0.520, 0.470, 0.165)
EVAL_L = (0.395, 0.115, 0.275, 0.190)
EVAL_R = (0.710, 0.115, 0.280, 0.190)


def _box(ax, rect, colour, fc="white"):
    x, y, w, h = rect
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.004,rounding_size=0.02",
                                lw=0.8, ec=colour, fc=fc, zorder=2))
    return (x + w / 2.0, y + h / 2.0)


def _arrow(ax, p0, p1, colour=SHARED, lw=0.8, rad=0.0):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="-|>", lw=lw, color=colour,
                                 mutation_scale=6, shrinkA=1.5, shrinkB=1.5, zorder=1,
                                 connectionstyle=f"arc3,rad={rad}"))


def provenance():
    """The three counts this panel names, read from the run that produced panels b and c."""
    for path in (SRC, PROV):
        if not os.path.exists(path):
            raise FileNotFoundError(f"{path} missing. Run analysis/class_c/oracle_shape_test.py.")
    n = int(json.load(open(SRC))["n_queries"])
    prov = json.load(open(PROV))
    # The panel says "in the same cells", so the barcode join has to be what makes that true.
    assert (prov["n_cells_joined_by_barcode"] == prov["n_cells_protein_file"]
            == prov["n_cells_rna_file"]), (
        f"the RNA and protein files no longer cover the same cells "
        f"({prov['n_cells_rna_file']} and {prov['n_cells_protein_file']} joining to "
        f"{prov['n_cells_joined_by_barcode']}); the schematic's central claim is that they do.")
    return n, int(prov["n_markers_used"]), int(prov["n_cells_joined_by_barcode"])


def _text_w_frac(ax, text, pt):
    """Printed width of ``text`` as a fraction of this panel's width, so a key can be centred
    as one unit instead of at a typed offset that a rename silently invalidates."""
    fig = ax.figure
    fig.canvas.draw()
    t = ax.text(0.0, -1.0, text, fontsize=pt)
    w = t.get_window_extent(renderer=fig.canvas.get_renderer()).width
    t.remove()
    return float(w) / fig.dpi / AX_W_IN


def draw_design(ax):
    """One experiment, two rankings, one protein readout, two evaluator forms."""
    n_q, markers, cells = provenance()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # ---- the one experiment both columns are built from --------------------------------------
    cx, cy = _box(ax, SRC_BOX, SHARED, fc="#F7F7F7")
    head = "one Perturb-CITE-seq experiment"
    sub = f"RNA and {markers} surface proteins in the same {cells:,} cells"
    ax.text(cx, cy + 0.030, head, ha="center", va="center", fontsize=PT_ANNOT, color=TEXT)
    ax.text(cx, cy - 0.042, sub, ha="center", va="center", fontsize=PT_SMALL, color=SUBTLE)

    # ---- what is ranked, and what judges it --------------------------------------------------
    rx, ry = _box(ax, RNA_BOX, TEXT)
    ax.text(rx, ry + 0.062, "two RNA rankings", ha="center", va="center", fontsize=PT_ANNOT,
            color=TEXT)
    # A SWATCH AND INK, not coloured letters. These two names are the key that binds panel b's
    # blue and orange bars, and they were the key in the only channel the deck forbids for text:
    # figstyle states that a label is INK or META and that colour reaches the reader through
    # marks. It is not a style preference. Measured against white, COMP_SOFT sits at 2.23:1 and
    # FOCAL_SOFT at 3.84:1, both under the 4.5:1 small text is normally held to, and these were
    # set at 6.5 pt. Two rows further down this same panel already does it correctly: "evaluator
    # as a mean" and "as a distribution" are INK inside a coloured box.
    #
    # The stub plus its name is centred as one unit, so the pair stays centred in the box however
    # the names are edited, and the panel asserts the unit fits before it draws.
    stub_w, stub_gap, stub_h = STUB_W_IN / AX_W_IN, STUB_GAP_IN / AX_W_IN, STUB_H_IN / AX_H_IN
    for i, (name, colour) in enumerate((("energy distance", POP), ("mean cosine", MEAN))):
        y = ry - 0.008 - i * 0.070
        tw = _text_w_frac(ax, name, PT_SMALL)
        total = stub_w + stub_gap + tw
        assert total < RNA_BOX[2] - 0.04, (
            f"{name!r} plus its swatch sets {total * AX_W_IN:.2f} in and the rankings box is "
            f"{RNA_BOX[2] * AX_W_IN:.2f} in wide; the key no longer fits the box it names.")
        x0 = rx - total / 2.0
        ax.add_patch(Rectangle((x0, y - stub_h / 2.0), stub_w, stub_h,
                               fc=colour, ec="none", zorder=5, clip_on=False))
        ax.text(x0 + stub_w + stub_gap, y, name, ha="left", va="center", fontsize=PT_SMALL,
                color=TEXT)
    ax.text(rx, RNA_BOX[1] - 0.050, "identical in both columns", ha="center",
            va="top", fontsize=PT_SMALL, color=SUBTLE)

    px, py = _box(ax, PRO_BOX, TEXT)
    ax.text(px, py + 0.030, "protein response", ha="center", va="center", fontsize=PT_ANNOT,
            color=TEXT)
    # The branch is stated on the box it branches from, not as a free-floating phrase. A phrase
    # placed in the band below this box has nowhere to go: four arrows leave that band, and every
    # position that clears them puts the words over a neighbour.
    ax.text(px, py - 0.040, "of those same cells, read two ways", ha="center", va="center",
            fontsize=PT_SMALL, color=SUBTLE)

    _arrow(ax, (0.32, SRC_BOX[1]), (rx, RNA_BOX[1] + RNA_BOX[3]))
    _arrow(ax, (0.68, SRC_BOX[1]), (px, PRO_BOX[1] + PRO_BOX[3]))

    # ---- the one thing that changes ----------------------------------------------------------
    lx, ly = _box(ax, EVAL_L, MEAN, fc="#FDF8F2")
    ax.text(lx, ly + 0.048, "evaluator as a mean", ha="center", va="center", fontsize=PT_SMALL,
            color=TEXT)
    ax.text(lx, ly - 0.032, "cosine between\nmean protein deltas", ha="center", va="center",
            fontsize=PT_SMALL, color=SUBTLE, linespacing=1.15)

    ex, ey = _box(ax, EVAL_R, POP, fc="#F2F7FC")
    ax.text(ex, ey + 0.048, "as a distribution", ha="center", va="center", fontsize=PT_SMALL,
            color=TEXT)
    ax.text(ex, ey - 0.032, "energy between\nprotein cell clouds", ha="center", va="center",
            fontsize=PT_SMALL, color=SUBTLE, linespacing=1.15)

    # The protein readout branches; the rankings do not. Two arrows leave the protein box and two
    # leave the ranking box, and the pair from the ranking box is what says the rankings are the
    # same on both sides rather than re-derived per column.
    for target_x, target in ((lx, EVAL_L), (ex, EVAL_R)):
        _arrow(ax, (px, PRO_BOX[1]), (target_x, target[1] + target[3]), colour=SHARED)
        _arrow(ax, (RNA_BOX[0] + RNA_BOX[2] * 0.62, RNA_BOX[1]),
               (target[0] + 0.02, target[1] + target[3] * 0.72), colour=SUBTLE, lw=0.7,
               rad=-0.18)

    ax.text(0.005, 0.030, f"n = {n_q} queries", ha="left", va="bottom",
            fontsize=PT_SMALL, color=SUBTLE)

    # ---- what the schematic may not do -------------------------------------------------------
    drawn = [str(t.get_text()) for t in ax.texts]
    assert not any(ch.isdigit() for t in drawn for ch in t
                   if t not in (f"n = {n_q} queries", sub)), (
        "this panel names structure, not results. The only digits it may draw are the two counts "
        f"read from {SRC}; every other value belongs to panels b and c.")
    return {"n_queries": n_q, "n_markers": markers, "n_cells": cells}


if __name__ == "__main__":
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    sys.path.insert(0, os.path.join(REPO, "figures"))
    from figstyle import apply_style
    from fig4_style import PT_TICK, PT_TITLE

    apply_style(sizes=(PT_TITLE, PT_ANNOT, PT_TICK))
    plt.rcParams["savefig.bbox"] = None
    BOX_W, BOX_H, AX_W, AX_H = 3.30, 1.55, 3.16, 1.40
    fig = plt.figure(figsize=(BOX_W, BOX_H))
    ax = fig.add_axes([0.10 / BOX_W, 0.10 / BOX_H, AX_W / BOX_W, AX_H / BOX_H])
    print(draw_design(ax))
    fig.savefig(os.path.join(os.path.dirname(os.path.abspath(__file__)), "4a.png"), dpi=300)
    print("wrote 4a.png")
