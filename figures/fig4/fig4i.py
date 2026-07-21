"""DART Figure 4 panel 4i: Class C per query, distributional score against the scalar it must beat.

Source data: source_data/fig4hi_class_c_functional.csv

Each point is one leave-one-drug-out query, scored against the semantically matched oracle
(drug-drug functional similarity from GDSC2 dose-response profiles; see fig4h.py).
  x = energy retrieval, which compares whole populations
  y = response-magnitude matching, a QUERY-DEPENDENT SCALAR that compares no distributions at all
      and merely prefers candidates whose response is about as large as the query's

Energy sits above this scalar on 62 of 103 queries. That is the honest headline, and it is a far
weaker claim than the panel it replaces, which reported "103 of 103" against ABSOLUTE POTENCY: an
oracle no similarity retriever was ever asked to optimize, and one on which a magnitude scalar is
near-guaranteed to win because potency is largely magnitude. Reporting a 103/103 sweep over
queries that share a candidate pool within each cell line also treated pseudo-replicates as
independent evidence, which this study elsewhere refuses to do.

The cloud straddles the diagonal. Distributional retrieval is better on most queries but not
reliably so, and the paired test that would nominally support it (p = 0.073) is itself
anticonservative for the same pseudo-replication reason. The honest unit is the three cell lines.

Run standalone: python fig4i.py
"""
import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

FOCAL, COMP, GREY, INK = "#5185C0", "#E99D4E", "#7A7A7A", "#1A1A1A"
GREEN = "#55966B"
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC = f"{REPO}/figures/source_data/fig4hi_class_c_functional.csv"

LINES = ["A549", "K562", "MCF7"]
MARKS = ["o", "s", "^"]


def draw_4i(ax):
    if not os.path.exists(SRC):
        raise FileNotFoundError(
            f"{SRC} does not exist. Run analysis/class_c/class_c_functional_oracle.py first.")
    d = pd.read_csv(SRC)
    x, y = d.energy_rho.values, d.magnitude_match_rho.values
    energy_wins = int((x > y).sum())
    p = float(stats.wilcoxon(x, y).pvalue)

    lo, hi = -0.72, 0.92
    ax.plot([lo, hi], [lo, hi], ls="--", lw=0.8, color=INK, zorder=2)
    ax.fill_between([lo, hi], [lo, lo], [lo, hi], color=FOCAL, alpha=0.055, zorder=0, lw=0)

    for ln, mk in zip(LINES, MARKS):
        s = d[d.cell_line == ln]
        ax.plot(s.energy_rho, s.magnitude_match_rho, ls="", marker=mk, ms=3.0,
                mfc=FOCAL, mec="white", mew=0.35, alpha=0.80, label=ln, zorder=3)

    ax.axvline(0, ls=":", lw=0.6, color=GREY, zorder=1)
    ax.axhline(0, ls=":", lw=0.6, color=GREY, zorder=1)

    ax.text(0.97, 0.05, f"energy better:\n{energy_wins} / {len(d)} queries",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=6.0,
            fontweight="bold", color=FOCAL)
    ax.text(0.04, 0.96, "the scalar\nis better here", transform=ax.transAxes,
            ha="left", va="top", fontsize=5.3, color=GREY, style="italic")

    ax.set_xlabel(r"energy retrieval:  $\rho$ with functional similarity", fontsize=6)
    ax.set_ylabel("magnitude matching (a scalar):" "\n" r"$\rho$ with functional similarity",
                  fontsize=6)
    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)
    ax.set_aspect("equal", adjustable="box")
    ax.tick_params(labelsize=5.6)
    for sp in ("right", "top"):
        ax.spines[sp].set_visible(False)
    ax.legend(loc="lower left", fontsize=5.2, handletextpad=0.2, borderaxespad=0.3,
              labelspacing=0.2, frameon=False)

    # The Wilcoxon p and its anticonservativeness caveat used to be set under this axis at 4.7 pt,
    # below the 5 pt Nature floor. The caveat is load-bearing, so it is not lost: it is stated in
    # the Fig. 4 caption. The statistic is still computed here and printed on a standalone run so
    # the caption number remains regenerable from this script.
    return {"energy_wins": energy_wins, "n_queries": int(len(d)), "wilcoxon_p": p}


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(3.1, 3.1))
    st = draw_4i(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "4i.png"), dpi=200, bbox_inches="tight")
    print("wrote 4i.png")
    print(f"energy better on {st['energy_wins']} / {st['n_queries']} queries; "
          f"Wilcoxon p = {st['wilcoxon_p']:.3f} (anticonservative; see caption)")
