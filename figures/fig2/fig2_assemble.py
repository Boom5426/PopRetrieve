"""PopRetrieve Figure 2: cell populations carry retrievable information beyond mean signatures.

ARCHETYPE: quantitative grid with one hero panel (a, at 30 per cent of panel area). Seven panels,
read in one order:

    HOW BIG IS IT?
      a  The Hit@1 ladder          every population-level scorer above every mean-level one

    HOW GENERAL IS IT?
      b  Per task                  large on both constructed tasks, reversed on Frangieh
      c  Per query                 it survives partial observation on most of 765 queries

    CAN WE SAY WHERE IT WILL BE?
      d  The pre-specified gate    does not enrich for the gain
      e  Minority-state fraction   starving the minority state does not universally erase it

    IS IT A PROPERTY OF ONE SCORE, OR OF A FAMILY?
      f  Five population scorers   all five gain, and the coverage pair gains most
      g  Score-to-score agreement  the two families are internally coherent and near orthogonal

Everything here is objective-aligned (Class A): the criteria reward correspondence between
response populations, which is the information population-level retrieval uses. That is the
figure's whole scope and the reason it stops where it does. What happens under criteria that do
NOT share the retrieval objective is Figure 3.

THE 2026-08-31 REBUILD, AND WHAT IT WAS FIXING
----------------------------------------------
The science was already here. What was missing is that six of the seven panels were standard
statistical charts that stated their result instead of showing it, and the layout was the reason.
Three panels across a 6.90 in canvas leaves each one about 1.7 in wide, which is a size at which
the only way to fit an annotation is to shrink it, so the figure had drifted down to 5.6 pt in six
places. Two per row, and one full-width headline, buys the 6.5 pt floor this file now enforces.

Four things changed that are about the argument rather than about the drawing:

  * a is grouped by REPRESENTATION FAMILY and no longer by performance alone. That is free,
    because the two orderings coincide: 0.589 is the weakest population-level scorer and 0.518
    the strongest mean-level one, so the ladder is sorted and grouped at the same time. It was
    previously drawn in three colours with pca_dist coloured as "other", which put a latent
    ENERGY DISTANCE outside the population family and weakened the claim the panel exists to
    make. fig2a asserts the separation at draw time.
  * d was two bars whose near-equality the reader had to notice. It now carries the measurement:
    a bootstrap interval on each median, the difference, and a rank test. The gate's two groups
    differ by -0.003 in median regret reduction, 95% CI [-0.065, +0.059], Mann-Whitney p = 0.97.
  * e plotted six curves, three of them the mean baseline, and asserted only that energy Hit@1
    falls with alpha. The quantity the manuscript's own caption discusses is the ADVANTAGE, so
    the panel now plots it directly: three curves instead of six, and the claim ("not a universal
    monotonic collapse") is a property of the drawn lines rather than of the caption.

    Rebuilding it also caught an error in the manuscript, which the panel's author and its
    auditor found independently. Both the Results text and the old caption described alpha as a
    SIMILARITY knob, "progressively merging the two constructed subpopulations". It is not.
    ControlledMixtureTask.build draws n_maj = round(alpha * 400) cells from the HDAC response
    pool and the remaining 400 - n_maj from the JAK pool, so the two states stay orthogonal and
    what alpha moves is their PROPORTION: the minority state falls from 200 cells to 40. A real
    merging sweep does exist in this repository, build_divergence_query's lam ("lam = 0 gives
    identical subpops, lam >= 1 orthogonal"), but it belongs to exp02 and exp11 and is not what
    this panel plots. The conclusion survived; the mechanism named did not. Both sentences are
    corrected, and CORRECTIONS.md records it.
  * e and f moved off hand-copied mirrors in figures/source_data/ onto the results/ files those
    mirrors were copied from, which is what panel c was already fixed to do. The mirrors had no
    generator, and both were verified to agree with their parent before the switch.

    g did NOT move, because it cannot. It reads figures/source_data/ed1_metric_correlation.csv,
    which source_data/README.md classifies PRIMARY, meaning nothing regenerates it. No file under
    results/ holds the 54,180 query-candidate scores, and exp08_signature_baselines.py exports
    none, so the matrix behind g and behind the manuscript's "rho = 1.000 over 54,180 scores"
    cannot be recomputed from the released code. That was tolerable while the panel was Extended
    Data; it is a main-text reproducibility gap now, and the fix is a generator, not an edit
    here.

GEOMETRY, IN INCHES ON THE PRINTED PAGE
---------------------------------------
The manuscript text block is 6.951 in and the figure enters with
``\\includegraphics[width=\\textwidth]``. Authored at 6.90 in, so the scale factor is 1.00 and
nominal point size IS printed point size; the 6.5 pt floor asserted below is 6.5 pt on paper.
The float has to clear a 9.461 in text block less about 16/72 in of float overhead, so the
canvas is 9.20 in and exports at 9.22 with savefig's 0.01 in pad.

Row heights differ because the rows do. a is the headline and is the only full-width panel; d and
e get the deepest row because d carries per-query distributions behind its two intervals and e
carries a schematic strip above its curves.

Rebuild: python fig2_assemble.py
"""
import os
import re
import sys

import matplotlib.pyplot as plt
import matplotlib.text as mtext

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# ONE canonical output stem per figure; build_all.STEMS holds the same string and refuses to
# build if the two drift apart. This is the name that syncs to manuscript/latex/figures/fig2.pdf.
STEM = "fig2_temptation"

from figstyle import pin_canvas, strip_titles  # noqa: E402
from fig2_style import PT_ANNOT, PT_FLOOR, PT_LETTER, PT_TICK, PT_TITLE, TEXT  # noqa: E402

from fig2a import draw_2a  # noqa: E402
from fig2b import draw_2b  # noqa: E402
from fig2c import draw_2c  # noqa: E402
from fig2d import draw_2d  # noqa: E402
from fig2e import draw_2e  # noqa: E402
from fig2f import draw_2f  # noqa: E402
from fig2g import draw_2g  # noqa: E402

# ------------------------------------------------------------------------------------------
# The inch ledger
# ------------------------------------------------------------------------------------------
FIGW = 6.90

PAD_TOP, PAD_BOT = 0.05, 0.08
# The panel letter alone. It was 0.26 in while every panel also stated a bold conclusion phrase;
# removing those (see fig2_style) returns 0.36 in to the four rows, and the row gap tightens with
# them. The height a figure spends on sentences is height it does not spend on evidence.
LETTER_BLOCK = 0.17
ROW_GAP = 0.22

# (panel keys in the row, row height in inches). A one-key row is full width.
# HIERARCHY, MEASURED 2026-08-31. Panel a is a proper hero at 30 per cent of panel area, but below
# it the page was flat and in one place inverted: panel d, a diagnostic, was the SECOND LARGEST
# panel in the figure at 14.1 per cent, larger than c, which is one of the figure's two main
# results, and larger than every robustness panel. Row 3 was also the tallest row on the page and
# it holds the two diagnostics. d is now the smallest panel at 8.7 per cent, which is what it
# should be, and the tier averages run 18.6 / 11.3 / 10.8 instead of 20.2 / 12.0 / 11.8.
#
# The third tier is only just below the second, and that is honest rather than fixable: with seven
# panels and a 30 per cent hero the remaining six share 70 per cent, so they land between 9 and 13
# per cent whatever is done. Panel e sits at the top of that band because of its composition strip,
# which exists because alpha was being described as the wrong quantity until CORRECTIONS.md R45,
# and shrinking it away would undo that fix.
ROWS = [(("a",), 1.66),
        (("b", "c"), 1.58),
        (("d", "e"), 1.50),
        (("f", "g"), 1.54)]

# Box widths per row, in inches, summing to FIGW. A row of one is full width; a row of two is
# split evenly unless named here. Row 3 is deliberately uneven: d is two point estimates and does
# not need half the page, while e carries five alpha points under a composition strip.
ROW_WIDTHS = {("d", "e"): (2.85, 4.05)}

# (left, right, bottom) pad in inches inside the panel BOX. Top is always zero: the panel phrase
# is drawn at transAxes y = 1.0 and lives in the LETTER_BLOCK band above the axes. Left pads are
# sized by what each panel's y furniture actually needs at 6.8 pt, which is why they differ:
# "coverage-worst" as a y tick label is 0.62 in, a rotated y axis label plus numeric ticks is
# 0.46 in, and every panel reserves 0.24 in of that for the letter.
PADS = {"a": (0.94, 0.08, 0.46),
        "b": (0.72, 0.10, 0.50),
        "c": (0.72, 0.10, 0.50),
        "d": (0.72, 0.10, 0.52),
        "e": (0.72, 0.10, 0.50),
        "f": (0.90, 0.10, 0.48),
        "g": (0.86, 0.10, 0.50)}

# e is a curve under a schematic strip that says what its x axis physically means, the same
# construction figure 1 uses for its two continuum panels.
E_STRIP_H, E_STRIP_GAP = 0.34, 0.08


def _boxes():
    """Resolve the rows into per-panel axes rects, in inches, measured from the FIGURE TOP."""
    rects, letters = {}, {}
    y = PAD_TOP
    for keys, row_h in ROWS:
        y += LETTER_BLOCK
        widths = ROW_WIDTHS.get(keys, tuple(FIGW / len(keys) for _ in keys))
        assert abs(sum(widths) - FIGW) < 1e-9, (keys, widths)
        for i, k in enumerate(keys):
            box_w = widths[i]
            x0 = sum(widths[:i])
            letters[k] = (x0, y)
            left, right, bottom = PADS[k]
            ax_x, ax_w = x0 + left, box_w - left - right
            if k == "e":
                rects["e_top"] = (ax_x, y, ax_w, E_STRIP_H)
                rects["e"] = (ax_x, y + E_STRIP_H + E_STRIP_GAP, ax_w,
                              row_h - E_STRIP_H - E_STRIP_GAP - bottom)
            else:
                rects[k] = (ax_x, y, ax_w, row_h - bottom)
        y += row_h + ROW_GAP
    return y - ROW_GAP + PAD_BOT, rects, letters


FIGH, RECTS, LETTER_XY = _boxes()


def _letter(fig, key):
    """Panel letters in the gutter, on one baseline per row, at this figure's own 9.5 pt.

    Placed in FIGURE coordinates rather than as an axes-fraction offset, so that the two columns
    line up: a fixed transAxes dx puts the letter a different distance out on every panel width,
    and this figure has five distinct axes widths.
    """
    x0, row_top = LETTER_XY[key]
    fig.text(x0 / FIGW, 1.0 - (row_top - 0.04) / FIGH, key,
             fontsize=PT_LETTER, fontweight="bold", va="bottom", ha="left", color=TEXT)


_SUBSUP = re.compile(r"\$[^$]*[\^_][^$]*\$")


def _assert_floor(fig, floor=PT_FLOOR):
    """Refuse to return a figure carrying text below THIS figure's floor.

    figstyle.save() already enforces the deck's 5 pt production limit. This is stricter and runs
    earlier, because the point of the rebuild was legibility rather than compliance: 5 pt is what
    production rejects, 6.5 pt is what a reader can take in at 183 mm. Mathtext is measured at its
    effective size, since a sub/superscript prints at 0.7x nominal.

    The fix when this fires is to CUT the annotation and move the sentence into the caption, which
    is where dense explanation belongs and costs no space. It is not to lower the size.
    """
    bad = []
    for t in fig.findobj(mtext.Text):
        s = str(t.get_text())
        if not s.strip() or not t.get_visible():
            continue
        eff = t.get_fontsize() * (0.7 if _SUBSUP.search(s) else 1.0)
        if eff < floor - 1e-6:
            bad.append((round(eff, 2), s.replace("\n", "/")[:40]))
    assert not bad, (
        f"Figure 2 sets its own {floor} pt floor and these are under it: {sorted(bad)[:8]}. "
        f"Cut the annotation into the caption; do not lower the size.")
    return fig



def _assert_no_titles(fig, cap=PT_ANNOT):
    """Refuse to return a figure in which any PANEL draws text above ``cap``.

    The mechanical form of the rule in fig2_style: the panels carry evidence and the caption
    carries the argument. A conclusion sentence set over a panel is always the largest text on it,
    so capping panel text at the annotation size is what stops one coming back. The panel letters
    are exempt because fig2_assemble draws them, not the panels, and they are navigation rather
    than claims.

    It is deliberately a size gate and not a wording gate. Nothing here can tell a claim from a
    label, but a claim that has to fit at 7.2 pt beside the marks it describes is a caption
    sentence that has already lost the argument for being on the panel.
    """
    letters = set(fig.texts)
    bad = []
    for t in fig.findobj(mtext.Text):
        if t in letters or not str(t.get_text()).strip() or not t.get_visible():
            continue
        if t.get_fontsize() > cap + 1e-6:
            bad.append((round(t.get_fontsize(), 2), str(t.get_text()).replace("\n", "/")[:44]))
    assert not bad, (
        f"Figure 2 caps panel text at {cap} pt and these are above it: {sorted(bad)[:8]}. "
        f"A panel states no conclusion; move the sentence to the caption.")
    return fig


def build(apply_style, panel_letter):
    # This figure's ladder sits one step above the deck's (8, 7, 6); see fig2_style. panel_letter
    # is accepted to keep build_all's contract and deliberately not used: its size is fixed at
    # 8 pt, below this figure's own title size.
    apply_style(sizes=(PT_TITLE, PT_ANNOT, PT_TICK))
    fig = plt.figure(figsize=(FIGW, FIGH))
    pin_canvas(fig)

    def _ax(key):
        x, top, w, h = RECTS[key]
        return fig.add_axes([x / FIGW, 1.0 - (top + h) / FIGH, w / FIGW, h / FIGH])

    for key, fn in (("a", draw_2a), ("b", draw_2b), ("c", draw_2c),
                    ("d", draw_2d), ("f", draw_2f), ("g", draw_2g)):
        fn(_ax(key))
    draw_2e(_ax("e"), _ax("e_top"))

    for key in "abcdefg":
        _letter(fig, key)

    # strip_titles clears rc titles so a panel's standalone preview can label itself without the
    # composite inheriting it. The one phrase each panel states over itself here is drawn ink via
    # fig2_style.title and survives on purpose.
    return _assert_no_titles(_assert_floor(strip_titles(fig)))


if __name__ == "__main__":
    # build() must NOT export. Every export goes through figstyle.save(), which applies the
    # deck-wide 5 pt floor first; a savefig here would ship a figure that never met the gate.
    from figstyle import apply_style, panel_letter, save
    save(build(apply_style, panel_letter),
         os.path.join(os.path.dirname(os.path.abspath(__file__)), STEM))
    print(f"wrote {STEM}.pdf / .svg / .png  ({FIGW} x {FIGH:.2f} in)")
