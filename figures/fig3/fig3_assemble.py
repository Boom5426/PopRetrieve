"""PopRetrieve Figure 3: the apparent gains do not survive independent evaluation.

Thirteen panels, one argument, read row by row. This is the metric-class ladder and the
paper's central figure.

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
  Row 3 (h-i)  Class C, an independent functional oracle: drug-drug functional similarity from
               GDSC2 dose-response AUC profiles, with the three SciPlex3 lines held out. Energy
               retrieval BEATS the correctly specified mean incumbent here (+0.276 vs +0.083),
               the one such win in the study, but a query-dependent scalar that compares no
               distributions reaches +0.232 and partialling it out leaves energy +0.097.
  Row 4 (j-k)  The Class-B null is not a power artifact. Inside the highest response-divergence
               quartile, the stratum the gate itself nominates, the task-proximal comparison
               reached power 1.00 while mechanism recovery reached 0.06; 80% power on MoA-nDCG
               would have taken 20,844 queries against the 143 that exist.
  Row 5 (l-m)  What the Class-C endpoint has to be. Score the same four rankings against
               ABSOLUTE GDSC2 potency instead of drug-drug functional similarity and the two
               that carry candidate magnitude change sign (energy +0.276 to -0.52, raw mean
               cosine +0.241 to -0.53) while a scalar that does no retrieval at all wins at
               +0.69. The reason is on panel m: the query-candidate energy distance is itself
               largely a ranking of the candidate's own response magnitude, median rho +0.791.

TITLES ARE CLAIMS, AND THEY WERE WRONG HERE
-------------------------------------------
Until 2026-07-26 this file still carried the row-3 titles of the WITHDRAWN potency framing:
"Class C: an external functional oracle (measured drug potency)", "similarity is anti-aligned
with potency", "a scalar that ignores the query wins every query". The panels below them had
already been rebuilt on the functional-similarity oracle and showed the opposite: energy leads
(+0.276) and wins 62 of 103 queries against a scalar that is itself query-DEPENDENT. A title that
contradicts its own axes is the exact failure this paper is about, so all three now state what
the plotted numbers show, and match Fig. 3's caption in the manuscript.

THE EXTENDED DATA DECK IS RETIRED, AND j-m ARRIVE FROM IT (2026-08-30)
----------------------------------------------------------------------
Captions now set on the page FOLLOWING the figure rather than under it, so the graphic is no
longer capped near 5 in and this figure has room for two more rows. Four Extended Data panels
come here rather than to any other main figure, because each answers an objection a reader forms
while looking at a panel that is already on this page. Nothing is re-plotted and nothing is
copied: the draw functions are imported from the modules that already own them, which is what
stops the panel on this page and the analysis it came from drifting apart.

  j  edfigs/ed_panels.draw_ed2a, was Extended Data Fig. 1d. Achieved power in the highest
     response-divergence quartile: 1.00 for minority-state coverage against 0.06 for MoA-nDCG.
  k  edfigs/ed_panels.draw_ed2b, was Extended Data Fig. 1e. Queries needed for 80% power: 45
     against an observed n=191 for minority coverage, 20,844 against an observed n=143 for
     MoA-nDCG.
  l  ed5/ed5.draw_a, was Extended Data Fig. 2g. The four rankings scored against ABSOLUTE GDSC2
     potency: energy -0.52, raw mean cosine -0.53, control-subtracted mean cosine +0.10,
     response magnitude alone +0.69. Note what is and is not claimed. The two rankings that
     inherit candidate magnitude invert; the control-subtracted one, which does not, collapses
     to near zero rather than inverting.
  m  ed5/ed5.draw_b, was Extended Data Fig. 2h. The Spearman correlation between the
     query-candidate energy distance and the candidate's own response magnitude, median +0.791.

Why beside these panels and not in some other figure:

  j,k next to a-d.  Panel b puts a MoA-nDCG gain whose median is exactly 0.000 in front of the
     reader, and the first thing anyone does with a null is ask whether the comparison could have
     seen the effect at all. Row 4 answers in the same highest-divergence quartile that panel c's
     rightmost bar reports, which is the stratum where the gate itself says the advantage should
     be largest and therefore the only stratum where the objection has any force. Left in
     Extended Data the answer arrived pages after the objection, and a reader who has to go
     looking for a power analysis has already decided the null is thin.
  l,m next to h-i.  Row 3 is the study's one external win, and it is a win only because the
     endpoint was chosen to ask the retriever's own question. Row 5 is the control that shows
     what a different endpoint does: scored against absolute potency the rankings that carry
     candidate magnitude change sign, which is not retrieval failing but the endpoint asking
     something else.
     Panel m then names the channel, response magnitude, that panel h ALREADY partials out; the
     +0.097 residual in h and the +0.791 median in m are two readings of one mechanism, and a
     reader cannot check the first without the second.

AUTHORED AT PRINT SIZE (2026-07-26 re-cut, height re-cut 2026-08-30)
--------------------------------------------------------------------
The manuscript's text block is 6.93 in wide and every figure enters with
\\includegraphics[width=\\textwidth]. This figure used to be authored 11.4 in wide, so LaTeX
shrank it by 0.605x on the page and its 5.6-8 pt source text printed at 3.4-4.8 pt: below the
5 pt floor Nature Portfolio enforces at FINAL PRINTED SIZE. The build-time gate in figstyle.py
measures NOMINAL size, so it reported the figure clean while the printed page failed.

The canvas is therefore 6.90 in wide, the width it is printed at, and the scale factor is 1.0:
nominal point size IS printed point size. Panel geometry is set in INCHES here rather than
through gridspec ratios, because at 1:1 the space a y-axis label or a panel letter needs is a
fixed physical quantity (about 0.5 in and 0.34 in) and does not scale with the panel it belongs
to; expressing it as a fraction of a 12-column grid is what produced the uneven gutters and the
collisions in the 11.4 in version.

The canvas is 0.605x its old width, so annotation that used to be shrunk by LaTeX now competes
with the panels for real space. Every panel and every panel letter is kept. What was cut is
on-panel prose that the Fig. 3 caption already carries verbatim: panel g's second x-label line,
panel h's two-line gloss on the dotted remainder, and panel i's "the scalar is better here".
Nothing was rescued by shrinking type below the floor.

HEIGHT CEILING, AND WHY THE CANVAS IS NOW PINNED
------------------------------------------------
Height used to be capped near 5 in because the caption shared the page with the graphic. It no
longer does, so the ceiling is 9.30 in and the two new rows take this figure from 4.83 to 8.59 in.
The WIDTH is untouched at 6.90 in, because width is the only number that governs printed point
size: \\includegraphics[width=\\textwidth] scales by 6.93/6.92 whatever the height is.

pin_canvas() is called now and was not before. figstyle sets savefig.bbox to "tight", so the
exported page used to be whatever the ink happened to span, 6.878 in, which LaTeX then magnified
by 1.008x to fill the text block. That is a small factor, but it is the same silent re-scaling the
11.4 in version was rebuilt to end, and every row added is another chance for one annotation to
move the page width. Pinning makes the media box the authored canvas plus savefig.pad_inches,
6.92 in, whatever the panels later grow into. Its price is that nothing may hang outside the
canvas any more, which is why _layout() now asserts that no row overruns FIGW.

Rebuild: python fig3_assemble.py
"""
import os
import sys

import matplotlib.pyplot as plt
import pandas as pd

_HERE = os.path.dirname(os.path.abspath(__file__))
_FIGROOT = os.path.abspath(os.path.join(_HERE, ".."))
sys.path.insert(0, _HERE)
sys.path.insert(0, _FIGROOT)
# Panels j-m are drawn by modules that live in sibling figure directories, so those directories
# join the path the same way this one and figures/ do. edfigs/ed_consolidated.py reaches its
# panels this way too; both files import the same functions, which is the point.
for _p in (os.path.join(_FIGROOT, "edfigs"), os.path.join(_FIGROOT, "ed5")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# The one canonical output stem for this figure; must equal build_all.STEMS[4], which build_all
# asserts, because that is the name copied to manuscript/latex/figures/fig3.pdf.
STEM = "fig3_collapse"

from fig3a import draw_3a
from fig3b import draw_3b
from fig3c import draw_3c
from fig3d import draw_3d
from fig3e import draw_3e
from fig3f import draw_3f
from fig3g import draw_3g
from fig3h import draw_3h, TITLE_4H
from fig3i import draw_3i, TITLE_4I

# The adopted panels, imported rather than re-implemented. Both take a second argument holding
# already-loaded data, which _adopted_panels() binds once per build; see _adapt below.
import ed_panels                    # noqa: E402  draw_ed2a/draw_ed2b(ax, D)
import ed5 as _ed5                  # noqa: E402  draw_a/draw_b(ax, dataframe)

TITLES = {
    "a": "Same queries,\nopposite verdicts",
    "b": "MoA-nDCG gain\ncenters on zero",
    "c": "Minority-coverage\ngain is negligible",
    "d": "Non-recommended\nqueries gain as much",
    "e": "The diagnostic axis points\nthe wrong way",
    "f": "Recommendation cannot\nsort by divergence",
    "g": "Real, negligible, confined to mixtures",
    "h": TITLE_4H,
    "i": TITLE_4I,
    "j": "Power is 1.00 for coverage,\n0.06 for mechanism recovery",
    "k": "MoA-nDCG would have needed\n20,844 queries, not 143",
    "l": "Under absolute potency\nthe retrieval rankings invert",
    "m": "Energy distance is largely\na magnitude ranking",
}

ROW_LABELS = [
    "Response matching $\\rightarrow$ mechanism recovery: the same rankings, judged by a metric "
    "that does not share their objective",
    "Why the diagnostic cannot rescue it, and what 239 real-data tasks show",
    "External functional evaluation: an independent readout (drug$-$drug functional similarity, "
    "GDSC2 dose-response)",
    "The Class-B null is not a power artifact: what the task-proximal comparison could and could "
    "not have detected",
    "Choosing the external endpoint: what happens when the readout answers a different question "
    "from the retrieval task",
]

# ------------------------------------------------------------------------------------------
# Geometry, in inches on the printed page
# ------------------------------------------------------------------------------------------
from figstyle import pin_canvas, soften_axes, strip_titles  # noqa: E402

FIGW = 6.90                 # the width the figure is printed at; text block is 6.93 in

# Since build() pins the canvas these two are AUTHORED margins, not slack the tight bbox trims
# away: they are the white above the first panel letter and below the last x label on the exported
# page. savefig.pad_inches then adds 0.01 in outside them on every side.
PAD_TOP = 0.02
PAD_BOT = 0.06
# THE ROW BANNERS AND THE PANEL TITLES ARE BOTH GONE. Both were text on the figure that a
# Nature-family figure puts in its legend instead: the banners were three sentences organising the
# rows, and every panel carried a claim over itself. The caption now opens each row's first entry
# with what its banner said, and every panel entry with what its title said. The three constants
# survive so the ledger below still reads as a ledger, with BANNER_H and BANNER_GAP at zero and
# TITLE_BLOCK reduced to the height of the panel letter alone, which still sits above the axes.
BANNER_H = 0.0              # was 0.072 in, one line of 6.8 pt row-banner text
BANNER_GAP = 0.0            # was 0.055 in, banner baseline -> top of the row's panel title
TITLE_BLOCK = 0.14          # was 0.293 in (4 pt pad + two 8 pt title lines); now the letter only
ROW_GAP = 0.09              # bottom of one row's x-label -> top of the next row's banner

# Per panel: (key, left pad, axes width). The left pad is the physical room the panel's y-axis
# apparatus and its bold letter need, which is why it is a constant and not a share of the row.
# ``below`` is the room the row's x tick labels and x label need under the deepest axes in it.
#
# RESIDUAL PASS (2026-07-26). Three numbers here changed, all of them clearances measured on the
# rendered page rather than judged by eye. Row widths are unchanged panel by panel where they
# matter, so the exported PDF is the same width as before and LaTeX still prints it at 1:1.
#   * row 1 axh 0.78 -> 1.05. Panel a's two summary blocks sat on the Class-A violin's real
#     kernel tail. The fix needs a data-free band above the plotted view (see fig3a.py), and
#     0.27 in more height is what buys that band WITHOUT flattening the violins.
#   * panel c pad 0.50 -> 0.59, width 1.08 -> 0.99. Panel b's three-line note cleared panel c's
#     rotated y label by 1.2 pt, the tightest text-to-text gap in the deck. The two changes
#     cancel, so panel c's right edge, panel d and the row's right edge do not move; panel c's
#     y-axis apparatus moves 0.09 in right, for a measured 7.7 pt gap. Note the direction: the
#     first attempt narrowed panel b instead, which does open the same gap, but panel b's note
#     is anchored at 0.97 of ITS axes and there is only 0.575 in of free zone right of that
#     panel's dashed zero line, so moving the note left put it 0.8 pt off the zero line. The
#     free space has to come from panel c, which has it.
#   * panel h pad 1.05 -> 1.51, width 4.03 -> 3.57. Its five category labels are one line each
#     now instead of two (see fig3h.py) and the longest is 1.38 in, so the label column has to
#     be 1.51 in wide to hold them without reaching further left than the labels already did.
#     The 0.46 in comes out of the axes, whose right 40% is data-free.
#
# LEFT-EDGE PASS (2026-08-30), forced by pinning the canvas. Two of the pads above were 0.01 to
# 0.02 in short of the apparatus they hold, so panel a's rotated y label reached x = -0.008 in and
# panel h's longest category label reached x = -0.018 in. The old tight crop absorbed that
# silently; a pinned canvas turns it into a page 0.018 in wider than authored, and 6.92 in of
# authored canvas exported at 6.94. Both pads grow, both axes give back the same amount, so every
# panel to the right of them and both row right edges stay exactly where they were. Note the
# measurement: 1.51 in was set against the Agg renderer's 1.38 in for "response-magnitude match
# (no retrieval)", and the PDF renderer's own font metrics make that string 1.449 in.
ROWS = [
    dict(banner=0, axh=1.05, below=0.39,
         panels=[("a", 0.52, 1.42), ("b", 0.46, 1.24), ("c", 0.59, 0.99), ("d", 0.50, 1.12)]),
    dict(banner=1, axh=1.05, below=0.38,
         panels=[("e", 0.50, 1.55), ("f", 0.50, 1.48), ("g", 0.38, 2.43)]),
    dict(banner=2, axh=1.00, below=0.28,
         panels=[("h", 1.54, 3.54), ("i", 0.46, 1.30)]),
    # ROWS 4 AND 5, ADOPTED 2026-08-30. Two rows rather than one, and the arithmetic settles it
    # rather than taste. Measured on the rendered page, m's single x label is 2.32 in of set text
    # and l's is 1.81 in, so their axes cannot be narrower than that; l also needs 1.35 in of pad
    # for its categorical labels. Those four numbers already come to 6.03 in of a 6.90 in row and
    # leave 0.87 in for j, k and two more pads, which is not a row.
    #   * row 5 is therefore the geometry ed_consolidated.py already ships for this pair, taken
    #     over unchanged: 1.35 in of pad holds l's four two-line categorical labels (the longest,
    #     "response magnitude alone", measures 0.92 in) and the row lands exactly on 6.90. That is
    #     the full canvas with nothing to spare, which is safe only because m's x label is centred
    #     and ends 0.12 in inside its own right spine; it was measured, not assumed.
    #   * row 4 stops at 6.20 in and leaves 0.70 in unclaimed on the right. The gap is deliberate.
    #     j and k are two-category bar panels whose pads are fixed by their y-axis apparatus
    #     (0.58 in for "achieved power (Q4)", 0.74 in for "n for 80% power (log)" plus its
    #     mathtext decade labels), so the only way to reach the right edge is to widen the AXES to
    #     about 2.8 in each, and a bar drawn at 30% of its axes then prints 0.84 in wide. A margin
    #     reads better than a bar chart that looks like a poster.
    #   * j at 2.42 in and k at 2.46 in, against the 1.75 and 1.55 they had in Extended Data. The
    #     floor is j's pair of two-line x tick labels, 0.59 and 0.74 in wide and centred on the
    #     quarter points, which touch below 1.34 in of axes; the rest of the width is spent to
    #     keep the row from looking like two small panels adrift in it.
    #   * axh 1.32 and 1.30 against row 3's 1.00. These four panels came from a deck drawn at
    #     2.2 in of axes height; below about 1.3 in, l's four categorical rows and m's 18 bins
    #     stop being separable, and height is the one budget this figure now has to spend.
    #   * KNOWN TIGHT, and 1.32 is a deliberate stopping point, not the best number available.
    #     Panel k stacks "observed n=191" (drawn at 0.62x the observed line) over "45" (drawn at
    #     1.5x the bar), both at fixed DATA positions 0.239 log decades apart, over an axis
    #     spanning 3.778 decades. Their clearance is therefore set by the row height alone:
    #     0.53 pt here, 1.6 pt at axh 1.55, 3.8 pt at 2.03, and 4.4 pt at the 2.19 the Extended
    #     Data version had. Buying back that 4 pt costs the entire remaining height budget and
    #     makes two two-bar panels the largest thing on a page whose argument is rows 1 to 3, so
    #     it was not bought. Rendered at 600 dpi the pair reads as two lines: the bboxes nearly
    #     touch, the glyphs do not, because "observed n=191" has no descender under it and "45"
    #     no ascender over it. Do not shrink this row further; there is no clearance left.
    dict(banner=3, axh=1.32, below=0.32,
         panels=[("j", 0.58, 2.42), ("k", 0.74, 2.46)]),
    dict(banner=4, axh=1.30, below=0.36,
         panels=[("l", 1.35, 2.45), ("m", 0.55, 2.55)]),
]

# a-i take (ax) and need nothing else. j-m take (ax, data) and are bound in _adopted_panels(),
# which build() calls once, so FNS stays a plain literal and importing this module still reads no
# CSV. check_overlaps.py imports it to call build(), and an import that touches results/ would
# make a missing table a syntax-error-shaped failure in an unrelated tool.
FNS = {"a": draw_3a, "b": draw_3b, "c": draw_3c, "d": draw_3d, "e": draw_3e,
       "f": draw_3f, "g": draw_3g, "h": draw_3h, "i": draw_3i}


def _adapt(fn, arg):
    """Wrap a two-argument draw function so every panel is callable as fn(ax)."""
    return lambda ax: fn(ax, arg)


def _adopted_panels():
    """Bind j-m to their tables. Each table is read ONCE per build, not once per panel.

    ed_panels.load() reads fourteen tables and j and k use one of them, power_analysis.csv;
    calling it per panel would read all fourteen twice and, worse, would let j's bars and k's bars
    come from two different reads of a file a rerun of exp17 can change underneath them.
    """
    D = ed_panels.load()
    ed5_df = pd.read_csv(_ed5.SRC)
    return {"j": _adapt(ed_panels.draw_ed2a, D), "k": _adapt(ed_panels.draw_ed2b, D),
            "l": _adapt(_ed5.draw_a, ed5_df), "m": _adapt(_ed5.draw_b, ed5_df)}

GUTTER_LEAD = 0.16          # inches from the previous panel's right edge to the letter's left edge


def _layout():
    """Resolve the inch geometry into (figure height, per-panel rect, per-panel letter x, banner y).

    ``rects[key]`` is (axes left, axes top from the figure top, width, height) in inches and
    ``letters[key]`` is the letter's left edge, one GUTTER_LEAD in from where the panel to its
    left ends. Aligning the letters on the gutter rather than on a fixed offset from their own
    axes is what puts a, e and h in one column: panel h reserves 1.51 in for its categorical y
    labels and a fixed -0.34 in offset left its letter floating over them.
    """
    rects, letters, banners = {}, {}, []
    y = PAD_TOP
    for row in ROWS:
        y += BANNER_H
        banners.append(y)                                   # banner baseline, from the top
        ax_top = y + BANNER_GAP + TITLE_BLOCK
        x = 0.0
        for key, pad, w in row["panels"]:
            letters[key] = x + GUTTER_LEAD
            x += pad
            rects[key] = (x, ax_top, w, row["axh"])
            x += w
        # The canvas is pinned (see build), so the exported page is the authored width only while
        # every row fits inside it. Fail here, where the offending number is, rather than in a
        # media box that silently came out wide.
        assert x <= FIGW + 1e-9, f"row {row['banner']} overruns the canvas: {x:.3f} of {FIGW} in"
        y = ax_top + row["axh"] + row["below"] + ROW_GAP
    figh = y - ROW_GAP + PAD_BOT
    return figh, rects, letters, banners


FIGH, RECTS, LETTER_X, BANNER_Y = _layout()
# The graphic's own ceiling, now that the caption sets on the following page: the manuscript text
# block is 9.30 in tall and a figure taller than that is a float LaTeX cannot place. Asserted here
# rather than left to a reviewer's page proof, because every row added moves this number.
assert FIGH <= 9.30 + 1e-9, f"graphic is {FIGH:.2f} in tall, past the 9.30 in text block"
FIGSIZE = (FIGW, FIGH)


def build(apply_style, panel_letter):
    apply_style(sizes=(8, 7, 6))
    fig = plt.figure(figsize=FIGSIZE)

    fns = dict(FNS, **_adopted_panels())
    missing = [k for row in ROWS for k, _p, _w in row["panels"] if k not in fns]
    assert not missing, f"ROWS names panels with no draw function: {missing}"

    axes = {}
    for key, (x, top, w, h) in RECTS.items():
        ax = fig.add_axes([x / FIGW, 1.0 - (top + h) / FIGH, w / FIGW, h / FIGH])
        fns[key](ax)
        axes[key] = ax

    # Panel letters in the gutter to the left of each panel, on one baseline per row. A fixed
    # axes-fraction offset (the old dx=-0.11) placed the letter twice as far out on a double-width
    # panel as on a narrow one, so the row never lined up.
    for key, ax in axes.items():
        x_in, _top, w_in, h_in = RECTS[key]
        panel_letter(ax, key, dx=(LETTER_X[key] - x_in) / w_in,
                     dy=1.0 + TITLE_BLOCK / h_in, case="lower")

    # Nature panels carry no titles and Nature figures carry no row banners; both are in the
    # caption. ROW_LABELS is kept as the statement of what each row argues, because the caption
    # has to be checkable against it.
    # Pin the tight bbox to the authored canvas. Without this the exported page was the ink's
    # own bounding box, 6.878 in, and LaTeX magnified it back to the text block; with it the page
    # is 6.90 in plus savefig.pad_inches however far a later annotation reaches.
    pin_canvas(fig)
    return strip_titles(soften_axes(fig))


if __name__ == "__main__":
    # build() must NOT export. It used to call fig.savefig() here, which meant two things:
    # `python figures/build_all.py` without --write, documented as a report-only dry run,
    # silently overwrote four tracked composites; and it wrote them BEFORE
    # assert_min_fontsize ran, so a figure that then FAILED the gate had already been
    # deployed to disk. Every export now goes through figstyle.save(), which applies the
    # 5 pt floor first. (Audited 2026-07-27; fig1 and fig4 already worked this way.)
    from figstyle import apply_style, panel_letter, save
    save(build(apply_style, panel_letter),
         os.path.join(os.path.dirname(os.path.abspath(__file__)), STEM))
    print(f"wrote fig3 composite (13 panels, 5 rows) at {FIGW:.2f} x {FIGH:.2f} in")
