"""Figure 4 panel d: what the two natural-tissue panels are asking of one tumour.

WHAT THIS PANEL SHOWS
---------------------
Panels e and f both come from the same cohort and ask different questions of it, and neither
question is legible from its own axes without knowing how the tissue was cut. This schematic is
that cut.

Each patient tumour is split into two compartments by cell identity, malignant and myeloid. The
split is DISJOINT: no cell is in both, which is the property that makes panel f a comparison
between two populations rather than a correlation of one population with itself. Every drug is
applied to the whole tumour, so both compartments see the same treatment and the same matched
control, and the two panels then ask:

  * e, RECOVERABILITY. Given the cells of a treated tumour with two drugs mixed in, can the true
    drug partition be recovered without labels, and how far short of a supervised probe does the
    best unsupervised attempt fall?
  * f, ORDERING. Do the two disjoint compartments rank the same drug pairs by response
    similarity, or does compartment structure reorder them?

The counts are read from the result files rather than typed, so a cohort that changes size cannot
leave this panel describing the old one.

NO RESULT IS DRAWN HERE, and one is deliberately absent. A third natural-tissue panel used to sit
beside these two, an induced-response cosine between the malignant and myeloid response directions
on 17 patient-drug pairs, read as evidence that compartment pharmacology differs. It is no longer
in the main figure: a cosine between two response directions is confounded with effect size and
signal-to-noise, so it cannot carry a quantitative claim about how strongly the two compartments
differ. It is described in the Supplementary Information as a descriptive alignment, and this
schematic does not gesture at it.

Run standalone: python3 fig4_tissue.py
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
import pandas as pd
from matplotlib.backends.backend_agg import RendererAgg

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

from fig4_style import (MEAN, POP, PT_ANNOT, PT_SMALL, REPO, SHARED,  # noqa: E402
                        SUBTLE, TEXT)

GATE2 = f"{REPO}/results/zhao_gbm/gate2_drug_response.json"
PREMISE = f"{REPO}/results/zhao_gbm/premise_mean_vs_compartment.csv"

TUMOUR_BOX = (0.055, 0.660, 0.890, 0.300)
COMP_L = (0.075, 0.375, 0.390, 0.215)
COMP_R = (0.535, 0.375, 0.390, 0.215)
Q_L = (0.030, 0.045, 0.440, 0.230)
Q_R = (0.530, 0.045, 0.440, 0.230)


def _box(ax, rect, colour, fc="white"):
    x, y, w, h = rect
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.004,rounding_size=0.03",
                                lw=0.8, ec=colour, fc=fc, zorder=2))
    return (x + w / 2.0, y + h / 2.0)


def _arrow(ax, p0, p1, colour=SHARED, lw=0.8):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="-|>", lw=lw, color=colour,
                                 mutation_scale=6, shrinkA=1.5, shrinkB=1.5, zorder=1))


def _cloud(ax, cx, cy, n, rx, ry, colour, seed):
    rng = np.random.default_rng(seed)
    t = rng.uniform(0, 2 * np.pi, n)
    r = np.sqrt(rng.uniform(0, 1, n))
    ax.scatter(cx + rx * r * np.cos(t), cy + ry * r * np.sin(t), s=1.1, color=colour, lw=0,
               alpha=0.75, zorder=3)


def cohort():
    """The counts this panel names, from the two files panels e and f draw."""
    for path in (GATE2, PREMISE):
        if not os.path.exists(path):
            raise FileNotFoundError(f"{path} missing; panels d, e and f share this cohort.")
    g = json.load(open(GATE2))
    p = pd.read_csv(PREMISE)
    n_patients = int(g["n_patients"])
    assert int(p["patient"].nunique()) == n_patients, (
        f"{GATE2} reports {n_patients} patients and {PREMISE} carries "
        f"{int(p['patient'].nunique())}; the schematic describes one cohort for both panels.")
    # Panel f's claim is that the two compartments share no cells, which is why its columns are
    # two different cosines of the same drug pair. If the file ever stopped carrying both, the
    # word "disjoint" on this panel would have nothing behind it.
    for col in ("cos_malignant_response", "cos_myeloid_response"):
        assert col in p.columns, f"{PREMISE} lacks {col}; panel f compares two compartments"
    return n_patients, int(g["n_drug_pairs"]), int(len(p))


def draw_tissue(ax):
    """One tumour, two disjoint compartments, and the two questions panels e and f ask of them."""
    n_patients, n_gate2_pairs, n_premise_pairs = cohort()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    tx, ty = _box(ax, TUMOUR_BOX, SHARED, fc="#F3F6F9")
    ax.text(tx, ty + 0.058, "glioblastoma tissue", ha="center", va="center", fontsize=PT_ANNOT,
            color=TEXT)
    ax.text(tx, ty - 0.062, f"{n_patients} patients\ndrug and matched control", ha="center",
            va="center", fontsize=PT_SMALL, color=SUBTLE, linespacing=1.15)

    # THE TWO COMPARTMENTS ARE NEUTRAL, and that is a correction made on 2026-09-04. They were
    # drawn in POP blue and MEAN orange, which fig4_style defines as "population-level, and the
    # observable / honest arm" and "mean-signature, and the evaluator-derived / circular arm".
    # Malignant and myeloid are neither. Inside one figure the same two hues then carried the
    # scoring families in a, b and g and two cell types here, and the collision was not idle:
    # panel f plots cos(malignant) against cos(myeloid) with every point in POP blue, so a reader
    # carrying this key one panel forward reads those points as the malignant compartment.
    #
    # Nothing is lost by dropping the hues. The two boxes are named in words, they sit side by
    # side, and they are the only boxes in the panel holding a cell cloud, so three channels
    # already separate them from each other and from the four process boxes. This is the deck's
    # standing rule: a panel that has run out of colours separates by shape, fill or position
    # rather than by spending a hue that means something else.
    for rect, name, seed in ((COMP_L, "malignant", 11), (COMP_R, "myeloid", 12)):
        cx, cy = _box(ax, rect, SHARED)
        _cloud(ax, cx, cy + 0.028, 70, 0.115, 0.048, SHARED, seed)
        ax.text(cx, rect[1] + 0.030, name, ha="center", va="center", fontsize=PT_SMALL,
                color=TEXT)
        _arrow(ax, (cx, TUMOUR_BOX[1]), (cx, rect[1] + rect[3]))

    # Between the two down-arrows rather than across them: at 1.42 in the panel has no width to
    # spare, and this is the one word the reader must not miss.
    ax.text(0.5, (COMP_L[1] + COMP_L[3] + TUMOUR_BOX[1]) / 2.0, "disjoint cells",
            ha="center", va="center", fontsize=PT_SMALL, color=TEXT)

    # No colour column: these two boxes are drawn in SHARED whatever is passed, and the POP and
    # MEAN that used to sit here were read by nothing. A dead argument naming a family is how a
    # later editor concludes the left question is the blue one.
    for rect, head, tail in (
            (Q_L, "recover the\ndrug partition", f"e: {n_gate2_pairs} pairs"),
            (Q_R, "compare their\ndrug orderings", f"f: {n_premise_pairs} pairs")):
        qx, qy = _box(ax, rect, SHARED, fc="white")
        ax.text(qx, qy + 0.048, head, ha="center", va="center", fontsize=PT_SMALL, color=TEXT,
                linespacing=1.15)
        ax.text(qx, rect[1] + 0.032, tail, ha="center", va="center", fontsize=PT_SMALL,
                color=SUBTLE)
    _arrow(ax, ((COMP_L[0] + COMP_L[2] / 2), COMP_L[1]), (Q_L[0] + Q_L[2] / 2, Q_L[1] + Q_L[3]))
    _arrow(ax, ((COMP_R[0] + COMP_R[2] / 2), COMP_R[1]), (Q_R[0] + Q_R[2] / 2, Q_R[1] + Q_R[3]))
    # Panel f needs BOTH compartments, so it gets a second arrow; panel e is asked of the tumour
    # as a whole and is drawn from the malignant side only to keep the two paths readable.
    _arrow(ax, ((COMP_L[0] + COMP_L[2] / 2) + 0.06, COMP_L[1]),
           (Q_R[0] + 0.05, Q_R[1] + Q_R[3]), colour=SUBTLE, lw=0.7)

    # A SCHEMATIC HAS NO AXIS TO CLIP AGAINST, so nothing but this stops a label from printing
    # over its neighbour's panel. Every drawn string is measured against the axes rectangle: at
    # 1.42 in of width three of them overflowed on the first draw and the composite would have
    # carried all three.
    fig = ax.figure
    r = RendererAgg(int(fig.get_figwidth() * fig.dpi), int(fig.get_figheight() * fig.dpi), fig.dpi)
    box = ax.get_window_extent(renderer=r)
    over = []
    for t in ax.texts:
        bb = t.get_window_extent(renderer=r)
        if bb.x0 < box.x0 - 0.5 or bb.x1 > box.x1 + 0.5:
            out = max(box.x0 - bb.x0, bb.x1 - box.x1) / fig.dpi * 72.0
            over.append((str(t.get_text()).replace("\n", "/")[:34], round(out, 1)))
    assert not over, (
        f"these labels overflow the panel box by the printed points shown: {over}. Shorten or "
        f"re-break them; the panel is 1.42 in wide and a schematic cannot clip.")

    return {"n_patients": n_patients, "n_gate2_pairs": n_gate2_pairs,
            "n_premise_pairs": n_premise_pairs}


if __name__ == "__main__":
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    sys.path.insert(0, os.path.join(REPO, "figures"))
    from figstyle import apply_style
    from fig4_style import PT_TICK, PT_TITLE

    apply_style(sizes=(PT_TITLE, PT_ANNOT, PT_TICK))
    plt.rcParams["savefig.bbox"] = None
    BOX_W, BOX_H = 1.42, 1.75
    fig = plt.figure(figsize=(BOX_W, BOX_H))
    ax = fig.add_axes([0.0, 0.0, 1.0, 1.0])
    print(draw_tissue(ax))
    fig.savefig(os.path.join(os.path.dirname(os.path.abspath(__file__)), "4d.png"), dpi=300)
    print("wrote 4d.png")
