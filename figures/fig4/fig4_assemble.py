"""DART Figure 4: the apparent gains do not survive independent evaluation.

Nine panels, one argument, read row by row. This is the metric-class ladder and the paper's
central figure.

  Row 1 (a-d)  Class A -> Class B. One scorer, one query set: the only thing that changes is
               the class of metric doing the judging. A Class-A gain of +0.129 becomes a
               Class-B loss of -0.037, and the gate meant to concentrate the advantage does
               not concentrate it.
  Row 2 (e-g)  Why the gate cannot rescue it, and what the real data actually show. The
               gate's own reliability axis is anti-correlated with true response divergence,
               and across 239 real-data tasks the coverage advantage is statistically real,
               practically negligible, and confined to the mixtures we constructed. Panel g
               plots the DISTRIBUTION, not a count of "dominant" tasks: the threshold sits
               inside the noise band and the seed is not a replicate.
  Row 3 (h-i)  Class C, an external functional oracle (measured drug potency). Retrieval
               similarity is ANTI-correlated with potency, and a scalar that never looks at
               the query outranks distributional retrieval on every single query.

Rebuild: python fig4_assemble.py
"""
import os
import sys

import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fig4a import draw_4a
from fig4b import draw_4b
from fig4c import draw_4c
from fig4d import draw_4d
from fig4e import draw_4e
from fig4f import draw_4f
from fig4g import draw_4g
from fig4h import draw_4h
from fig4i import draw_4i

TITLES = {
    "a": "Same queries, opposite verdicts",
    "b": "MoA-nDCG gain centers on zero",
    "c": "Minority-coverage gain is negligible",
    "d": "Non-recommended queries gain as much",
    "e": "The gate axis points the wrong way",
    "f": "Recommendation cannot sort by divergence",
    "g": "Real but negligible, only in mixtures",
    "h": "Class C: similarity is anti-aligned with potency",
    "i": "A scalar that ignores the query wins every query",
}

ROW_LABELS = [
    "Class A $\\rightarrow$ Class B: the same rankings, judged by a metric that does not share "
    "their objective",
    "Why the gate cannot rescue it, and what 239 real-data tasks show",
    "Class C: an external functional oracle (measured drug potency)",
]


def build(apply_style, panel_letter):
    apply_style(sizes=(8, 7, 6))
    fig = plt.figure(figsize=(11.4, 9.2))
    gs = fig.add_gridspec(3, 12, hspace=0.62, wspace=2.9,
                          left=0.055, right=0.96, top=0.915, bottom=0.055)

    spans = {
        "a": (0, 0, 3), "b": (0, 3, 6), "c": (0, 6, 9), "d": (0, 9, 12),
        "e": (1, 0, 4), "f": (1, 4, 8), "g": (1, 8, 12),
        "h": (2, 0, 6), "i": (2, 6, 12),
    }
    fns = {"a": draw_4a, "b": draw_4b, "c": draw_4c, "d": draw_4d, "e": draw_4e,
           "f": draw_4f, "g": draw_4g, "h": draw_4h, "i": draw_4i}

    row_first = {}
    for k, (rr, c0, c1) in spans.items():
        ax = fig.add_subplot(gs[rr, c0:c1])
        fns[k](ax)
        ax.set_title(TITLES[k], loc="left")
        panel_letter(ax, k, case="lower")
        row_first.setdefault(rr, ax)

    # anchor each row banner to the actual top of that row, not to a guessed figure fraction
    for rr, txt in enumerate(ROW_LABELS):
        y = row_first[rr].get_position().y1 + 0.038
        fig.text(0.055, y, txt, fontsize=7.4, fontweight="bold", color="#1A1A1A",
                 ha="left", va="bottom")

    out = os.path.dirname(os.path.abspath(__file__))
    fig.savefig(os.path.join(out, "fig4_collapse.png"), dpi=300, bbox_inches="tight")
    fig.savefig(os.path.join(out, "fig4_collapse.pdf"), bbox_inches="tight")
    return fig


if __name__ == "__main__":
    from figstyle import apply_style, panel_letter

    build(apply_style, panel_letter)
    print("wrote fig4 composite (9 panels, 3 rows)")
