"""PopRetrieve Extended Data, consolidated: seven figures become three.

WHY THIS FILE EXISTS
--------------------
The deck carried seven Extended Data figures for 26 panels, drawn at roughly 5.9 in2 per panel
against the main deck's 3.7 in2. Reading them back panel by panel against the manuscript, the SI
tables and the Supplementary Notes established three things:

  * Five panels were carried in full somewhere else and are deleted, not merged. They are listed
    in DELETED below with the thing that already carries them. No measured value is lost.
  * Four are load-bearing for a main-text claim with no main-figure support: the lambda -> 0
    collapse (ED1b here), the beta interpolation (ED1c), and the two Tahoe-100M measurements
    (ED3e and ED3g). Promoting them into the main deck was measured and rejected: every main
    figure page already runs 86 to 99 per cent full, and none has the 1.4 in a new row costs
    plus the caption words the new panels need. They therefore lead the Extended Data instead.
  * The remaining seventeen are robustness, quality-control and audit panels. A Nature reader
    who meets a power analysis or a threshold sweep in a MAIN figure reads it as a sign that the
    headline result is thin, so Extended Data is where they belong anyway.

All twenty-one are drawn here, in three figures instead of seven, at panel sizes the old split
could not give them: ED1 and ED3 gained 0.6 in of axes height per row.

DELETED, WITH WHAT ALREADY CARRIES THEM
---------------------------------------
  old ED1a  dataset-scale bars      -> Supplementary Table 1, which is strictly richer: it adds
                                       ZhaoSims2021, Tahoe-100M and GDSC2, and prints every count.
  old ED1b  score-family key        -> Supplementary Table 2(a) defines all five scores; Fig. 2a
                                       already carries the family colour key inline. The panel was
                                       ax.axis("off") and five hard-coded strings, no data.
  old ED2c  MoA gain by quartile    -> main Fig. 5g. Same file
                                       (results/exp17_true_divergence_subset/), same four-row
                                       filter, same Benjamini-Hochberg star rule. Fig. 5g is a
                                       strict superset: it also draws s.e.m. bars.
  old ED3c  variance ratio vs cos   -> main Fig. 5c. fig5c._pick and ed_panels.draw_ed3c are the
                                       same function over the same two CSVs and the same four
                                       predictors in the same order; Fig. 5c adds +/- s.d.
  old ED6a  HIR-Bench schematic     -> main Fig. 4a and Supplementary Note 1. The panel was
                                       ax.axis("off"); it declared two result paths and read
                                       neither.

LAYOUT
------
Geometry is in inches on the printed page, the idiom fig3_assemble.py uses, because at 1:1 the
room a y-axis apparatus or a panel letter needs is a fixed physical quantity and does not scale
with the panel it belongs to. Expressing it as a share of a gridspec column is what produced the
uneven gutters in the figures this file replaces.

Both figures are authored 6.90 in wide, the width they are printed at, so nominal point size IS
printed point size and the 5 pt floor is enforced on the real thing.

Rebuild: python ed_consolidated.py
"""
import os
import sys

import matplotlib.pyplot as plt
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
FIGROOT = os.path.dirname(HERE)
for _p in (HERE, FIGROOT, os.path.join(FIGROOT, "ed4"), os.path.join(FIGROOT, "ed5"),
           os.path.join(FIGROOT, "ed6"), os.path.join(FIGROOT, "ed7")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from figstyle import (apply_style, panel_letter, pin_canvas, soften_axes,  # noqa: E402
                      strip_titles, save)

import ed_panels                       # noqa: E402  draw_edNx(ax, D)
import ed4_zhao_robustness as _ed4     # noqa: E402  draw_a..draw_d(ax)
import ed5 as _ed5                     # noqa: E402  draw_a/draw_b(ax, dataframe)
import ed7_tahoe as _ed7               # noqa: E402  draw_a..draw_d(ax)
from ed6_panel_c import draw_ed6b      # noqa: E402  (ax)
from ed6_panel_d import draw_ed6c      # noqa: E402  (ax)
from ed6_panel_e import draw_ed6d      # noqa: E402  (ax)

FIGW = 6.90                 # the width these figures are printed at; the text block is 6.95 in

# Vertical ledger, in inches. A row costs axh + below + TITLE_BLOCK, plus ROW_GAP between rows.
# The budget each figure has to fit inside is the SI text block, 9.461 in, minus its caption and
# the float-to-caption gap; _report() below prints the arithmetic every time the file is run so a
# row height can never drift past the page silently.
PAD_TOP = 0.02
PAD_BOT = 0.06
TITLE_BLOCK = 0.14          # the panel letter sits here, above the axes; panels carry no titles
ROW_GAP = 0.11
GUTTER_LEAD = 0.16          # previous panel's right edge -> letter's left edge

SI_TEXTHEIGHT = 9.461       # \textheight, both documents
CAPTION_PT_PER_WORD = 0.869  # calibrated on two measured captions in this submission
# Non-panel vertical overhead per float, in points: the SI's \captionsetup{skip=4pt} plus the
# \textfloatsep LaTeX puts between a top float and the text below it. Calibrated by bisection
# against pdflatex's own "Float too large for page" warning rather than assumed: at 4 pt this
# check passed a figure LaTeX rejected by 1.70 pt, and at 40 pt (a value measured on a MANUSCRIPT
# page, where the caption skip differs) it rejected figures LaTeX sets happily.
FLOAT_GAP_IN = 16 / 72

# Words in the caption each figure actually carries in PopRetrieve_SI.tex. Keep in step with the
# .tex: these are what the page-fit check below is measured against.
CAPTION_WORDS = {
    "ed1_scores_and_limits": 270,
    "ed2_identifiability_and_benchmark": 306,
    "ed3_tissue_and_scale": 317,
}


def _adapt(fn, arg):
    """Wrap a draw function that wants a second argument so every panel is callable as fn(ax)."""
    return lambda ax: fn(ax, arg)


def _build_specs():
    """Resolve the per-panel draw callables. Data is loaded once, here, not once per panel."""
    D = ed_panels.load()
    ed5_df = pd.read_csv(_ed5.SRC)

    # ED1: how the scores relate to each other, the two analytic limits that connect mean to
    # population retrieval, and the power the task-proximal comparison actually has.
    ed1 = dict(
        stem="ed1_scores_and_limits",
        rows=[
            dict(axh=2.24, below=0.46, panels=[
                ("a", 0.85, 2.30, _adapt(ed_panels.draw_ed1c, D)),
                ("b", 1.00, 2.55, _adapt(ed_panels.draw_ed1d, D), 0.55),
            ]),
            dict(axh=2.19, below=0.44, panels=[
                ("c", 0.62, 1.85, _adapt(ed_panels.draw_ed1e, D)),
                ("d", 0.55, 1.75, _adapt(ed_panels.draw_ed2a, D)),
                ("e", 0.58, 1.55, _adapt(ed_panels.draw_ed2b, D)),
            ]),
        ],
    )

    # ED2: whether the machinery holds up. Can the states be recovered at all, does the synthetic
    # benchmark behave as specified, and what happens under an endpoint that answers a different
    # question from the one the retriever was given.
    ed2 = dict(
        stem="ed2_identifiability_and_benchmark",
        rows=[
            dict(axh=1.18, below=0.42, panels=[
                ("a", 1.28, 1.72, _adapt(ed_panels.draw_ed3a, D)),
                ("b", 0.50, 1.45, _adapt(ed_panels.draw_ed3b, D)),
                # 0.35 in of the row is left unclaimed after c: its colorbar lives OUTSIDE
                # its axes, and at full width the "ARI" label and the 1.2 tick ran 0.32 in
                # past the canvas, which bbox_inches="tight" turns into a wider page.
                ("c", 0.50, 1.10, _adapt(ed_panels.draw_ed3d, D)),
            ]),
            dict(axh=1.14, below=0.42, panels=[
                ("d", 0.52, 1.52, draw_ed6b),
                ("e", 0.92, 1.58, draw_ed6c, 0.60),
                ("f", 0.83, 1.53, draw_ed6d),
            ]),
            dict(axh=1.14, below=0.38, panels=[
                ("g", 1.35, 2.45, _adapt(_ed5.draw_a, ed5_df)),
                ("h", 0.55, 2.55, _adapt(_ed5.draw_b, ed5_df)),
            ]),
        ],
    )

    # ED3: the same questions on material nobody constructed, at two scales. Row 1 is the
    # glioblastoma compartment calls and their threshold sweep; row 2 is Tahoe-100M.
    ed3 = dict(
        stem="ed3_tissue_and_scale",
        rows=[
            dict(axh=1.95, below=0.44, panels=[
                ("a", 0.52, 1.30, _ed4.draw_a),
                ("b", 0.50, 1.25, _ed4.draw_b),
                ("c", 0.50, 1.20, _ed4.draw_c),
                ("d", 0.55, 1.08, _ed4.draw_d),
            ]),
            dict(axh=1.95, below=0.46, panels=[
                ("e", 0.55, 1.22, _ed7.draw_a),
                ("f", 0.50, 1.16, _ed7.draw_b),
                ("g", 0.68, 1.16, _ed7.draw_c),
                ("h", 0.52, 1.08, _ed7.draw_d),
            ]),
        ],
    )
    return [ed1, ed2, ed3]


def _layout(rows):
    """Resolve the inch ledger into (figure height, rects, letter x), all in inches.

    rects[key] is (axes left, axes top measured from the figure top, width, height). Letters sit
    on the gutter one GUTTER_LEAD in from where the panel to their left ends, not at a fixed
    axes-fraction offset, so a wide panel and a narrow one in the same row still line their
    letters up on one column.
    """
    rects, letters = {}, {}
    y = PAD_TOP
    for row in rows:
        ax_top = y + TITLE_BLOCK
        x = 0.0
        for key, pad, w, _fn, *rest in row["panels"]:
            letters[key] = x + GUTTER_LEAD + (rest[0] if rest else 0.0)
            x += pad
            rects[key] = (x, ax_top, w, row["axh"])
            x += w
        assert x <= FIGW + 1e-9, f"row overruns the canvas: {x:.3f} in of {FIGW} in"
        y = ax_top + row["axh"] + row["below"] + ROW_GAP
    return y - ROW_GAP + PAD_BOT, rects, letters


def _report(stem, figh, n_panels):
    """Print the page-fit arithmetic. A figure that cannot fit its page must say so at build time.

    The old deck grew panel by panel with no check that graphic plus caption still fit the text
    block; this is that check, and it runs on every build rather than on a reviewer's screen.
    """
    printed_h = figh * 6.951 / FIGW           # \includegraphics[width=\textwidth]
    words = CAPTION_WORDS[stem]
    cap_in = words * CAPTION_PT_PER_WORD / 72
    total = printed_h + cap_in + FLOAT_GAP_IN
    slack = SI_TEXTHEIGHT - total
    verdict = "FITS" if slack >= 0 else "OVERFLOWS"
    print(f"  {stem}: graphic {printed_h:.2f} in + caption {cap_in:.2f} in "
          f"({n_panels} panels, {words} words) + gap {FLOAT_GAP_IN:.2f} in "
          f"= {total:.2f} of {SI_TEXTHEIGHT:.2f} in -> {verdict}, slack {slack:+.2f} in")
    return slack


def build_one(spec):
    figh, rects, letter_x = _layout(spec["rows"])
    fig = plt.figure(figsize=(FIGW, figh))
    n = 0
    for row in spec["rows"]:
        for key, _pad, _w, fn, *_rest in row["panels"]:
            x, top, w, h = rects[key]
            ax = fig.add_axes([x / FIGW, 1.0 - (top + h) / figh, w / FIGW, h / figh])
            fn(ax)
            panel_letter(ax, key, dx=(letter_x[key] - x) / w,
                         dy=1.0 + TITLE_BLOCK / h, case="lower")
            n += 1
    _report(spec["stem"], figh, n)
    pin_canvas(fig)
    return strip_titles(soften_axes(fig)), n


def main():
    apply_style(sizes=(8, 7, 6))
    print("Extended Data, consolidated:")
    for spec in _build_specs():
        fig, _n = build_one(spec)
        save(fig, os.path.join(HERE, spec["stem"]))
        plt.close(fig)


if __name__ == "__main__":
    main()
