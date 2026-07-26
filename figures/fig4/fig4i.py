"""JUDGE Figure 4 panel 4i: Class C per query, distributional score against the scalar it must beat.

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

# Panel title. Kept next to the data it describes so a standalone run and the composite cannot
# disagree. The old title ("a scalar that ignores the query wins every query") belonged to the
# withdrawn absolute-potency oracle and is false of these points: energy leads on most queries,
# and the scalar plotted here is query-DEPENDENT.
#
# The win count now lives in the title rather than as an in-axes label, because at the printed
# panel width (1.3 in) a two-line corner label sat on the point cloud. It is COMPUTED from the
# source table, not typed, so the title cannot drift from the panel it sits over.
def title_4i():
    """Panel-i title, with the win count read from the source table."""
    d = pd.read_csv(SRC)
    wins = int((d.energy_rho > d.magnitude_match_rho).sum())
    return f"Energy leads on {wins} of {len(d)}\nqueries, not reliably"


TITLE_4I = title_4i()


def draw_4i(ax):
    if not os.path.exists(SRC):
        raise FileNotFoundError(
            f"{SRC} does not exist. Run analysis/class_c/class_c_functional_oracle.py first.")
    d = pd.read_csv(SRC)
    x, y = d.energy_rho.values, d.magnitude_match_rho.values
    energy_wins = int((x > y).sum())
    p = float(stats.wilcoxon(x, y).pvalue)

    # Limits are identical on both axes and leave a data-free strip at the top (no query has
    # magnitude-match rho above +0.68), which is where the cell-line key sits: nothing overlaps.
    # Equal scales on both axes (so the identity line is a true 45 degrees), but the x range runs
    # further right than the y range: that band is data-free and carries the win-count label,
    # which otherwise sat on top of a point in the lower-right corner.
    lo, hi, xhi = -0.78, 0.98, 1.30
    ax.plot([lo, hi], [lo, hi], ls="--", lw=0.8, color=INK, zorder=2)
    ax.fill_between([lo, hi, xhi], [lo, lo, lo], [lo, hi, hi],
                    color=FOCAL, alpha=0.06, zorder=0, lw=0)

    for ln, mk in zip(LINES, MARKS):
        s = d[d.cell_line == ln]
        ax.plot(s.energy_rho, s.magnitude_match_rho, ls="", marker=mk, ms=3.2,
                mfc=FOCAL, mec="white", mew=0.35, alpha=0.80, label=ln, zorder=3)

    ax.axvline(0, ls=":", lw=0.6, color=GREY, zorder=1)
    ax.axhline(0, ls=":", lw=0.6, color=GREY, zorder=1)

    # One direct label, naming the shaded half-plane, set in the data-free strip beyond the
    # largest energy rho (+0.70) so it crosses no point. Its companion ("the scalar is better
    # here") is gone: at the printed panel width it lay across the upper-left cloud, and the
    # shading plus the diagonal already say which side is which. The win count moved into the
    # title, where it costs no plot area.
    ax.text(0.98, 0.03, "energy\nbetter", transform=ax.transAxes, ha="right", va="bottom",
            fontsize=5.8, fontweight="bold", color=FOCAL, linespacing=1.25)

    # The oracle is named in full on panel h and in the row-3 banner, one panel to the left, so
    # these axis labels name only the score. Spelled out ("energy retrieval: rho with functional
    # similarity") the x label was 1.4 in on a 1.2 in axes and ran off the canvas edge.
    ax.set_xlabel(r"energy retrieval, $\rho$", fontsize=6.0)
    ax.set_ylabel("response-magnitude match\n(a scalar), " r"$\rho$", fontsize=6.0)
    ax.set_xlim(lo, xhi)
    ax.set_ylim(lo, hi)
    ax.set_aspect("equal", adjustable="box")
    ax.set_anchor("S")
    ax.set_xticks([-0.5, 0.0, 0.5])
    ax.set_yticks([-0.5, 0.0, 0.5])
    ax.tick_params(labelsize=5.8)
    for sp in ("right", "top"):
        ax.spines[sp].set_visible(False)
    ax.legend(loc="upper left", bbox_to_anchor=(-0.02, 1.02), fontsize=5.8, handletextpad=0.1,
              borderaxespad=0.0, labelspacing=0.22, frameon=False, ncol=3, columnspacing=0.5,
              handlelength=0.8)   # the default 2.0 handle spread the key across the diagonal

    # The Wilcoxon p and its anticonservativeness caveat used to be set under this axis at 4.7 pt,
    # below the 5 pt Nature floor. The caveat is load-bearing, so it is not lost: it is stated in
    # the Fig. 4 caption. The statistic is still computed here and printed on a standalone run so
    # the caption number remains regenerable from this script.
    return {"energy_wins": energy_wins, "n_queries": int(len(d)), "wilcoxon_p": p}


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(3.1, 3.1))
    st = draw_4i(ax)
    ax.set_title(TITLE_4I, loc="left", fontsize=8)
    fig.savefig(os.path.join(os.path.dirname(__file__), "4i.png"), dpi=200, bbox_inches="tight")
    print("wrote 4i.png")
    print(f"energy better on {st['energy_wins']} / {st['n_queries']} queries; "
          f"Wilcoxon p = {st['wilcoxon_p']:.3f} (anticonservative; see caption)")
