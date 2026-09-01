"""PopRetrieve Figure 1 panel f: the evidence ladder, and how far each body of work climbs it.

The panel makes two statements, in this order.

1. Evaluation of a retrieval method is not one measurement but a hierarchy, ordered by how far the
   judge sits from the score being judged: response matching restates the retrieval objective,
   mechanism recovery moves to task-proximal biology on the same upstream data, and external
   function is measured by an evaluator the method never saw. That ordering is the only axis the
   panel draws, and it is deliberately NOT an axis of claim strength: a headline response-matching
   result is the right test of objective fidelity, it is simply not a test of independent utility.
2. Published families report at the bottom step; this study reports at all three. The right-hand
   pair of columns is drawn small on purpose. It is the panel's second sentence, not its subject.

WHY IT IS A STAIRCASE AND NOT A STACK OF LABELS
-----------------------------------------------
The previous version expressed the hierarchy through text POSITION: three rules with three blocks
of type above them, ordered because they happened to be drawn at increasing height. A reader with
the labels covered saw three rows, not three levels. This version draws the ordering as geometry:
each level is a filled platform, each platform sits one full height above the one below it and one
step to the right, so the silhouette is a staircase and the rise survives having every word masked.
The step run (X_STEP) is what carries "independence increases upward"; the wording only names what
the rise already shows.

The 2026-08-31 layout change is what made this possible. The panel is now 3.15 x 2.03 in, roughly
2:1 landscape, where the old box was 1.38 x 3.70 in portrait. A staircase needs run as well as
rise; the portrait box had no run to give, which is why the old cut had to fall back on text.

COLOUR: ONE NEUTRAL, since 2026-09-01. The three platforms used to take three of the figure's four
role colours, and the argument for it was that each role happened to fit: POP because response
matching is the population score's own ground truth, SHARED because mechanism recovery runs on data
both routes share, EXT because the top level is a judge the method never saw.

That argument does not survive being read from the reader's side. fig1_style teaches four colours
over panels a to e, and blue there means "population-level / distributional" while grey means
"everything both routes have in common". An evidence CLASS is neither. So a reader who had learned
the vocabulary arrived at the last panel and found two of its colours attached to something else,
and the reasoning above is the sound of a panel talking itself into that.

The ordinal axis this panel exists to draw is already carried twice, by the staircase offset and by
the labelled arrow beside it, so hue was carrying nothing except the false signal. All three
platforms are now one neutral. The status marks stay ink in both columns, because filled-versus-open
already carries "reports here" and tinting one of them would have given a role a second meaning.

WHAT AN OPEN MARK MEANS, AND WHAT IT MUST NOT BE READ AS
--------------------------------------------------------
The audit records each family's metrics as a class string whose FIRST letter is the class of its
HEADLINE metric. All six published families are headline A, and four of them (single-cell
signature retrieval, perturbation predictors, foundation models, PDGrapher-style graph methods)
also carry a B through DEG overlap or target-family recovery. An open mark therefore means "not
this family's headline metric", never "never reported", and the legend over the two columns says
"filled = headline metric" for exactly that reason. Nothing in the panel may be strengthened into
an absence claim.

PROVENANCE
----------
The survey size and the step each published family reports at are read from the field audit table
(``manuscript/components/related_work_metric_audit_table.csv``), not typed in: the panel's whole
point is that the audit found one headline class, so the audit file is what should be able to
change it. This study reporting at all three steps is the manuscript's own claim (Fig. 1 caption,
and the Class C GDSC2 evaluation in Results), and the evaluator at the top step is imported from
GDSC2 dose-response data rather than measured here, which the provenance line qualifies in a word.

The arrow label says "of the retrieval objective" in full because the panel sits beside e, which
is where that objective is defined; the caption carries the rest.

Schematic. No measured value is plotted.

Run standalone: python3 fig1f.py
"""
from __future__ import annotations

import csv
import os
import re
import sys

import matplotlib.pyplot as plt
from matplotlib.colors import to_rgba
from matplotlib.patches import Rectangle

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fig1_style import (LW_ARROW, LW_HAIR, MS_ARROW, PT_ANNOT,  # noqa: E402
                        PT_SMALL, PT_TICK, SHARED, SUBTLE, TEXT, arrow, blank)

# ---------------------------------------------------------------------------- the field audit
_REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
AUDIT_CSV = os.path.join(_REPO, "manuscript", "components", "related_work_metric_audit_table.csv")
THIS_WORK = "PopRetrieve / distributional retrieval"   # the one row that is not a published family

# The first letter of metric_class is the class of the family's HEADLINE metric, and that is the
# only thing the filled marks assert. A "B" later in the string ("A (with some B via DEG
# overlap)") is a secondary metric and must NOT fill the middle step; see the module docstring.
CLASS_STEP = {"A": 0, "B": 1, "C": 2}


def _audit():
    """(number of published families, set of steps any of them reports at) from the audit table."""
    with open(AUDIT_CSV, newline="", encoding="utf-8") as fh:
        rows = [r for r in csv.DictReader(fh) if r["method_family"].strip() != THIS_WORK]
    if not rows:
        raise RuntimeError(f"no published method families in {AUDIT_CSV}; panel f has no survey "
                           f"to report and must not invent one")
    heads = [r["metric_class"].strip()[:1] for r in rows]
    unknown = sorted(set(heads) - set(CLASS_STEP))
    if unknown:
        raise RuntimeError(f"{AUDIT_CSV} carries headline metric class(es) {unknown}, which the "
                           f"ladder has no step for; the panel must not silently drop a family")
    return len(rows), {CLASS_STEP[h] for h in heads}


# ---------------------------------------------------------------------------- the three levels
# Bottom to top. Each level shows its two example metrics on their own lines rather than joined by
# a comma: "GDSC2 dose response, protein response" is 1.71 in as one line and the platform is
# 1.22 in wide, and one metric per line keeps the three platforms identical in shape.
LEVELS = (
    dict(name="Response matching", gloss="objective-aligned",
         metrics=("energy regret", "connectivity")),
    dict(name="Mechanism recovery", gloss="task-proximal biology",
         metrics=("MoA-nDCG", "minority coverage")),
    dict(name="External function", gloss="external measurement",
         metrics=("GDSC2 dose response", "protein response")),
)
OURS_STEPS = (0, 1, 2)      # manuscript: "We report PopRetrieve under all three classes"

# ---------------------------------------------------------------------------- geometry, inches
# The axes is 3.15 x 2.03 in in the composite. Positions are held in inches and converted, rather
# than written as axes fractions, because every constraint here is a collision between a point size
# and a width, and points are inches. Every width below was measured in the deck font at the size
# it is set in, not estimated.
AX_W, AX_H = 3.15, 2.03

X_SLAB0 = 0.37              # left edge of the bottom platform
X_STEP = 0.28               # the run of one step: what makes the silhouette a staircase
W_SLAB = 1.22               # widest line inside a platform is the bold name at 1.03 in, plus pad
PAD_TEXT = 0.075            # platform edge -> text, left

Y_LADDER_B, Y_LADDER_T = 0.30, 1.76
GAP_SLAB = 0.02             # a hairline of white between platforms, so the three do not merge
H_SLAB = (Y_LADDER_T - Y_LADDER_B - 2 * GAP_SLAB) / 3.0

# Baselines inside a platform, measured DOWN from its top edge. The four lines (name, gloss, two
# metrics) plus the last descender come to 0.432 in, which leaves 0.04 in of padding at each edge.
DY_NAME, DY_GLOSS, DY_M1, DY_M2 = 0.115, 0.220, 0.320, 0.412

X_ARROW = 0.22              # the independence axis, in the clear column left of the bottom step
X_LABEL = 0.015             # its label sits UNDER it, where the full panel width is free: the two
                            # lines are 0.85 and 1.10 in, and no column beside the ladder is that
                            # wide at any height
Y_FOOT = (0.155, 0.035)     # the footer band, shared by the arrow label and the provenance

X_PUB, X_OURS = 2.32, 2.80  # 0.48 in pitch: the headers are 0.40 and 0.44 in wide, so their two
                            # half-widths plus a 0.06 in gap are what set the columns apart
X_PROV_R = 3.10             # provenance is right-aligned into the corner, away from the ladder
Y_HEADER = 1.80             # column names, in the band between the ladder and the title
Y_LEGEND = 1.93             # what a filled mark means, directly over the marks it explains
X_LEGEND = (X_PUB + X_OURS) / 2.0       # centred on the pair, so it reads as their heading

LW_TREAD = 2.0              # the platform's top edge. At LW_LINE the platform reads as a tinted
                            # text box; at twice that the top edge reads as a surface it stands on.
# ONE NEUTRAL, NOT THREE HUES, since 2026-09-01. Each platform used to be washed and outlined in
# its own colour: POP blue for response matching, SHARED grey for mechanism recovery, EXT green for
# external function. Only the last was right. fig1_style gives blue the meaning "population-level /
# distributional" and grey the meaning "everything both routes have in common", and neither is what
# an evidence class is, so a reader who had learned the figure's four colours by panel e arrived
# here and found two of them attached to something else. The module's own rule covers this case:
# "if a panel needs to separate two things and has run out, it separates them by shape, fill, or
# position, not by inventing a hue". This panel had never run out; it had three hues it did not
# need, because the ORDINAL axis is already carried twice, by the staircase offset and by the
# labelled arrow beside it. The platforms are now one neutral container and the ordering is
# position alone.
TINT = 0.16                 # the wash inside a platform
SLAB = SHARED               # the one neutral every platform is drawn in
MS_STATUS = 16              # marker area in pt^2 -> 4.5 pt across, legible and still secondary


def _fx(x_in):
    return x_in / AX_W


def _fy(y_in):
    return y_in / AX_H


def _step(i):
    """(left, bottom) of platform i, in inches: one height up and X_STEP right, each time."""
    return X_SLAB0 + i * X_STEP, Y_LADDER_B + i * (H_SLAB + GAP_SLAB)


def _mid(i):
    """The y a level is read at: its platform centre, which is where its status marks sit."""
    return _step(i)[1] + H_SLAB / 2.0


def _platform(ax, i, level):
    """One step: a neutral block with a solid top edge, carrying its own four lines of text."""
    left, bottom = _step(i)
    ax.add_patch(Rectangle((_fx(left), _fy(bottom)), _fx(W_SLAB), _fy(H_SLAB),
                           fc=to_rgba(SLAB, TINT), ec=SLAB, lw=LW_HAIR,
                           zorder=2))
    ax.plot([_fx(left), _fx(left + W_SLAB)], [_fy(bottom + H_SLAB)] * 2, lw=LW_TREAD,
            color=SLAB, solid_capstyle="butt", zorder=3)

    x = _fx(left + PAD_TEXT)
    top = bottom + H_SLAB
    ax.text(x, _fy(top - DY_NAME), level["name"], ha="left", va="baseline", fontsize=PT_ANNOT,
            fontweight="bold", color=TEXT, zorder=5)
    ax.text(x, _fy(top - DY_GLOSS), level["gloss"], ha="left", va="baseline", fontsize=PT_SMALL,
            style="italic", color=TEXT, zorder=5)
    # The example metrics are the level's provenance, not its claim, so they are SUBTLE: at full
    # ink the platform becomes four equal lines of type and the level name stops being the label.
    for metric, dy in zip(level["metrics"], (DY_M1, DY_M2)):
        ax.text(x, _fy(top - dy), metric, ha="left", va="baseline", fontsize=PT_SMALL,
                color=SUBTLE, zorder=5)


def _status(ax, x_in, y_in, filled):
    """Reports here / does not. Round, ink, sized in points so it stays round at any aspect."""
    ax.scatter([_fx(x_in)], [_fy(y_in)], s=MS_STATUS, marker="o", zorder=6, linewidths=0.7,
               facecolors=TEXT if filled else "white", edgecolors=TEXT)


def draw_1f(ax):
    blank(ax)
    n_published, published_steps = _audit()

    # Hung inside the top edge rather than on the helper's default baseline above it: everything
    # this panel draws has to stay within the rect, or it widens the row it is assembled into.
    # No panel title. "Evidence ladder" was set here at PT_TITLE and is the caption's own
    # opening clause for this panel; the axis below already names what the staircase orders.

    # ---- the axis the steps are ordered on: independence, not strength ----
    # It spans exactly the ladder, tail on the bottom platform and head on the top one, so the
    # arrow and the rise are the same measurement drawn twice.
    arrow(ax, (_fx(X_ARROW), _fy(Y_LADDER_B)), (_fx(X_ARROW), _fy(Y_LADDER_T)), color=TEXT,
          lw=LW_ARROW, ms=MS_ARROW, zorder=4)
    for line, y_in in zip(("more independent", "of the retrieval objective"), Y_FOOT):
        ax.text(_fx(X_LABEL), _fy(y_in), line, ha="left", va="baseline", fontsize=PT_ANNOT,
                color=TEXT, zorder=5)

    # ---- the ladder ----
    for i, level in enumerate(LEVELS):
        _platform(ax, i, level)

    # ---- who reports where, kept deliberately small ----
    # One line through this study's three marks, drawn under them: the column is read as a single
    # traverse of the ladder rather than as three unrelated ticks.
    # LW_HAIR, not LW_LINE: the line is a guide that joins three marks, and the reader has to stop
    # on the marks. At a plotted-series weight it became the boldest stroke in the panel and the
    # comparison stopped being the panel's second sentence.
    ax.plot([_fx(X_OURS)] * 2, [_fy(_mid(0)), _fy(_mid(len(LEVELS) - 1))], lw=LW_HAIR, color=TEXT,
            solid_capstyle="butt", zorder=5)
    for i in range(len(LEVELS)):
        _status(ax, X_PUB, _mid(i), i in published_steps)
        _status(ax, X_OURS, _mid(i), i in OURS_STEPS)
    for x_in, label in ((X_PUB, "Published"), (X_OURS, "This study")):
        ax.text(_fx(x_in), _fy(Y_HEADER), label, ha="center", va="baseline", fontsize=PT_TICK,
                color=TEXT, zorder=5)
    # Open means "not the headline metric": four of the six families do report a Class B metric,
    # just not as their headline. The legend is placed over the columns rather than in the corner
    # because it is the one thing a reader needs before the marks mean anything.
    ax.text(_fx(X_LEGEND), _fy(Y_LEGEND), "filled = headline metric", ha="center", va="baseline",
            fontsize=PT_SMALL, color=SUBTLE, zorder=5)

    # ---- provenance, in the corner the ladder leaves empty ----
    # The audit size comes from the table; "imported" is the one word the top step needs, because
    # its evaluator is read out of GDSC2 dose-response data rather than measured in this study.
    provenance = (f"{n_published} families surveyed", "GDSC2 evaluator imported")
    for line, y_in in zip(provenance, Y_FOOT):
        ax.text(_fx(X_PROV_R), _fy(y_in), line, ha="right", va="baseline", fontsize=PT_SMALL,
                color=SUBTLE, zorder=5)


# ------------------------------------------------------------------------------------ preview
_SUBSUP = re.compile(r"\$[^$]*[\^_][^$]*\$")


def _check(fig, ax):
    """The two gates the composite applies, run here so a failure is found at panel scale."""
    fig.canvas.draw()
    rend = fig.canvas.get_renderer()

    sizes = []
    for t in fig.findobj(plt.Text):
        s = str(t.get_text())
        if not s.strip() or not t.get_visible():
            continue
        sizes.append((t.get_fontsize() * (0.7 if _SUBSUP.search(s) else 1.0), s))
    smallest = min(sizes)
    assert smallest[0] >= 6.5 - 1e-9, f"below the 6.5 pt floor: {smallest}"

    # Only the artists this panel draws. blank() has already switched the spines and the two
    # Axis objects off, and an invisible Axis still reports the extent it would have had.
    panel = ax.get_window_extent(renderer=rend)
    out = []
    for art in [*ax.texts, *ax.lines, *ax.collections, *ax.patches]:
        if not art.get_visible():
            continue
        bb = art.get_tightbbox(rend)
        if bb is None or (bb.width == 0 and bb.height == 0):
            continue
        over = (max(0.0, panel.x0 - bb.x0), max(0.0, bb.x1 - panel.x1),
                max(0.0, panel.y0 - bb.y0), max(0.0, bb.y1 - panel.y1))
        if max(over) > 0.5:      # half a display pixel, i.e. below the resolution of the export
            label = getattr(art, "get_text", lambda: type(art).__name__)()
            out.append((tuple(round(o / fig.dpi, 4) for o in over), str(label)[:44]))
    for over, label in out:
        print(f"  OUTSIDE axes by (l, r, b, t) = {over} in: {label}")
    assert not out, f"{len(out)} artist(s) hang outside the axes; see above"
    return smallest[0]


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import matplotlib as mpl
    from figstyle import apply_style
    from fig1_style import PT_TITLE

    # The composite's own type ladder, so a size tuned here is the size that prints.
    apply_style(sizes=(PT_TITLE, PT_ANNOT, PT_TICK))
    fig, ax = plt.subplots(figsize=(AX_W, AX_H))
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)   # the axes IS the composite's rect
    draw_1f(ax)
    fig.canvas.draw()
    got = ax.get_window_extent(renderer=fig.canvas.get_renderer())
    assert (round(got.width / fig.dpi, 3), round(got.height / fig.dpi, 3)) == (AX_W, AX_H), (
        f"previewed at {got.width / fig.dpi:.3f} x {got.height / fig.dpi:.3f} in, but the "
        f"composite gives panel f {AX_W} x {AX_H} in; a panel tuned at another size is wrong")
    print(f"axes {AX_W} x {AX_H} in")

    print(f"smallest effective size: {_check(fig, ax):.2f} pt")
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "1f.png")
    # savefig.bbox is "tight" deck-wide; here it would crop the panel to its ink and the preview
    # would no longer be the 3.15 x 2.03 in rect the composite hands this panel.
    with mpl.rc_context({"savefig.bbox": None, "savefig.pad_inches": 0.0}):
        fig.savefig(out, dpi=400)
    print(f"wrote {out}")
