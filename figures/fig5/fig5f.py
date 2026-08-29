"""PopRetrieve Figure 5 panel 5f: the separation ladder, and the positive control Gate 2 needs.

Source data: results/upgrade/gate2_supervised_upper_bound.csv

Panel 6e reports that on this CONSTRUCTED mixture the supervised ceiling (0.692) and the best
unsupervised method (0.674) are 0.018 apart, so within that benchmark the limit is informational
rather than algorithmic. (Posed as the same drug-versus-drug question in a patient's tumour the
ceiling is 0.923 against 0.777 unsupervised: the information limit was a property of the benchmark,
not of biology. See main-text Fig. 4d and CORRECTIONS.md R21.) That conclusion is only safe if the
probe is capable of pulling away from clustering WHEN THERE IS SOMETHING TO PULL AWAY WITH.
Otherwise "no gap" could simply mean the probe is insensitive, and the whole argument collapses.

This panel is that control. Artificially raise the separation between the two source populations
and the gap opens exactly as it should: +0.114 at 1.5x, +0.162 at 2.0x, before both saturate at
perfect recovery. The probe detects exploitable structure whenever exploitable structure exists.
Its failure to detect any on real data (leftmost point, separation = 1.0) is therefore a
measurement, not a null result.

The panel replaces an ARI phase diagram over (separation x cell budget). The cell-budget axis was
flat and is reported in Extended Data; the separation axis is the one that carries the argument,
and it now carries the ceiling with it.

Run standalone: python fig5f.py
"""
import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Palette comes from the house-style module; do NOT re-declare the hex values here. Every
# panel file used to carry its own copy, which made figstyle's "one edit here recolours the
# whole deck" untrue: a recolour meant editing 43 files and missing one was silent.
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
from figstyle import FOCAL_SOFT, COMP_SOFT, GREY, INK  # noqa: E402
GREEN_SOFT = "#55966B"
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC = f"{REPO}/results/upgrade/gate2_supervised_upper_bound.csv"

UNSUP = ["acc_kmeans_k2", "acc_gmm_k2", "acc_leiden", "acc_hdbscan"]


def draw_5f(ax):
    if not os.path.exists(SRC):
        raise FileNotFoundError(
            f"{SRC} does not exist. Run analysis/identifiability/gate2_supervised_upper_bound.py.")
    d = pd.read_csv(SRC)

    g = d.groupby("separation_scale")
    seps = np.array(sorted(d.separation_scale.unique()))
    ceil = np.array([float(g.get_group(s).probe_acc.median()) for s in seps])
    best = np.array([max(float(g.get_group(s)[c].median()) for c in UNSUP) for s in seps])

    ax.fill_between(seps, best, ceil, color=COMP_SOFT, alpha=0.18, zorder=1)
    ax.plot(seps, ceil, "-o", color=GREEN_SOFT, ms=4, lw=1.5, zorder=3)
    ax.plot(seps, best, "-s", color=FOCAL_SOFT, ms=4, lw=1.5, zorder=3)
    ax.axhline(0.5, ls="--", lw=0.8, color=GREY, zorder=1)
    ax.text(7.9, 0.508, "chance", ha="right", va="bottom", fontsize=5.5, color=GREY)

    # Direct labels on the two curves, in their own colours, instead of a boxed legend: the
    # widest part of the wedge is the only place in this panel with room, and it is also the
    # place a reader is looking when the panel's point lands.
    ax.text(2.0, 0.948, "supervised ceiling", ha="right", va="bottom", fontsize=5.8,
            color=INK)
    ax.text(2.2, 0.700, "best unsupervised", ha="left", va="center", fontsize=5.8,
            color=INK)
    ax.text(2.02, 0.843, "gap", ha="center", va="center", fontsize=6.2,
            color=INK)
    # THE SHADING KEY IS IN THE CAPTION. Defining an encoding is what a figure legend is for,
    # and the wedge is already bounded by the two curves it lies between and labelled "gap".
    _UNUSED_SHADING_KEY = (lambda *a, **k: None)(2.35, 0.615, "", ha="left", va="top",
            fontsize=5.5, color=COMP_SOFT, linespacing=1.25)

    # the real-data regime: the gap is closed, and that is what panel e measures
    ax.axvline(1.0, ls=":", lw=1.0, color=INK, zorder=2)
    ax.annotate(f"real separation:\ngap {ceil[0] - best[0]:+.3f}",
                xy=(1.0, (ceil[0] + best[0]) / 2), xytext=(1.30, 0.545),
                fontsize=5.8, color=INK, linespacing=1.25,
                arrowprops=dict(arrowstyle="->", lw=0.8, color=INK))

    ax.set_xlabel(r"source separation ($\times$ real)", fontsize=6)
    ax.set_ylabel("accuracy recovering the true partition", fontsize=6)
    ax.set_xscale("log")
    ax.set_xticks(seps)
    ax.set_xticklabels([f"{s:g}" for s in seps], fontsize=5.6)
    ax.set_xlim(0.93, 8.7)
    ax.set_ylim(0.45, 1.06)
    ax.tick_params(axis="y", labelsize=5.6)
    ax.minorticks_off()
    for sp in ("right", "top"):
        ax.spines[sp].set_visible(False)


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(3.6, 3.0))
    draw_5f(ax)
    # Must stay identical to fig5_assemble.TITLES["f"], which overrides whatever this file sets
    # when the panel is composited.
    ax.set_title("The probe pulls away when structure is there", loc="left", fontsize=8)
    fig.savefig(os.path.join(os.path.dirname(__file__), "5f.png"), dpi=200, bbox_inches="tight")
    print("wrote 5f.png")
