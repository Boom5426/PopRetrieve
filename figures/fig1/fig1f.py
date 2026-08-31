"""PopRetrieve Figure 1 panel f: the evidence ladder, and how far each body of work climbs it.

The panel makes two statements, in this order.

1. Evaluation of a retrieval method is not one measurement but a hierarchy, ordered by how far the
   judge sits from the score being judged: response matching restates the retrieval objective,
   mechanism recovery moves to task-proximal biology on the same upstream data, and external
   function is measured by an evaluator the method never saw. That ordering is the only axis the
   panel draws, and it is deliberately NOT an axis of claim strength: a Class A result is the
   right test of objective fidelity, it is simply not a test of independent utility.
2. Published families report at the bottom rung; this study reports at all three. The right-hand
   pair of columns is drawn small on purpose. It is the panel's second sentence, not its subject.

WHY IT IS A LADDER AND NOT A MATRIX
-----------------------------------
The previous version was a status matrix with the rungs as rows, and a matrix asks the reader to
compare cells. The claim here is ordinal, so the drawing is ordinal: three treads at increasing
height, each one a step the level's text stands on, with one arrow running the full height of the
stack. The reader gets the ordering from geometry before reading a word, which is what lets the
right-hand columns stay small enough to be secondary.

Colour follows the figure's four roles and adds nothing. The bottom tread is POP because response
matching IS the population score's own ground truth; the middle tread is SHARED because mechanism
recovery still runs on the data both routes share; the top tread is EXT, the figure's mark for a
judge the method never saw, and panel f is one of the two panels allowed to use it. The status
marks are ink in both columns, because filled-versus-open already carries "reports here" and
tinting one of them would have given one of the four roles a second, unrelated meaning.

PROVENANCE
----------
The survey size and the rung each published family reports at are read from the field audit table
(``manuscript/components/related_work_metric_audit_table.csv``), not typed in: the panel's whole
point is that the audit found one class, so the audit file is what should be able to change it.
This study reporting at all three rungs is the manuscript's own claim (Fig. 1 caption, and the
Class C GDSC2 evaluation in Results), and the evaluator at the top rung is imported from GDSC2
dose-response data rather than measured here, which the provenance line qualifies in one word.

Schematic. No measured value is plotted.

Run standalone: python fig1f.py
"""
from __future__ import annotations

import csv
import os
import re
import sys

import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fig1_style import (EXT, LW_ARROW, LW_LINE, MS_ARROW,  # noqa: E402
                        POP, PT_ANNOT, PT_SMALL, PT_TICK, SHARED, SUBTLE, TEXT,
                        arrow, blank, title)

# ---------------------------------------------------------------------------- the field audit
_REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
AUDIT_CSV = os.path.join(_REPO, "manuscript", "components", "related_work_metric_audit_table.csv")
THIS_WORK = "PopRetrieve / distributional retrieval"   # the one row that is not a published family

# The audit records each family's metrics as a class string whose FIRST letter is the class of the
# headline metric ("A", "A (with some B via DEG overlap)", "A + B"). That first letter is what the
# panel's filled markers mean: the class a body of work reports as its primary evidence.
CLASS_RUNG = {"A": 0, "B": 1, "C": 2}


def _audit():
    """(number of published families, set of rungs any of them reports at) from the audit table."""
    with open(AUDIT_CSV, newline="", encoding="utf-8") as fh:
        rows = [r for r in csv.DictReader(fh) if r["method_family"].strip() != THIS_WORK]
    if not rows:
        raise RuntimeError(f"no published method families in {AUDIT_CSV}; panel f has no survey "
                           f"to report and must not invent one")
    rungs = {CLASS_RUNG[r["metric_class"].strip()[0]] for r in rows}
    return len(rows), rungs


# ---------------------------------------------------------------------------- the three rungs
# Bottom to top. `gloss` and `examples` are pre-wrapped rather than auto-wrapped: the column is
# 0.96 in wide, every break here is at a word or at an existing hyphen, and a wrapper would break
# "Evaluator-independent" somewhere else on a machine with a different metric font.
LEVELS = (
    dict(name=("Response", "matching"), gloss=("Objective-aligned",),
         examples=("energy regret", "connectivity"), tread=POP),
    dict(name=("Mechanism", "recovery"), gloss=("Task-proximal biology",),
         examples=("MoA-nDCG", "minority coverage"), tread=SHARED),
    dict(name=("External", "function"), gloss=("Evaluator-independent", "measurement"),
         examples=("GDSC2 dose response", "protein response"), tread=EXT),
)
OURS_RUNGS = (0, 1, 2)      # manuscript: "We report PopRetrieve under all three classes"

# ---------------------------------------------------------------------------- geometry, inches
# The axes is 1.376 x 3.70 in in the composite. Positions are held in inches and converted, rather
# than written as axes fractions, because every constraint in a panel this narrow is a collision
# between a point size and a width, and points are inches.
AX_W, AX_H = 1.376, 3.70

X_RAIL = 0.145              # the independence arrow doubles as the ladder's rail: the treads
                            # start on it, so three coloured rungs hang off one vertical
X_ARROW_LABEL = 0.070       # its rotated label, one line high, clears the axes edge by 0.02 in
X_TEXT = 0.185              # the text stands on the rung, inset from the rail
X_TREAD_R = 1.135           # "GDSC2 dose response" is the widest line at 0.96 in; this is its end
X_PUB, X_OURS = 1.196, 1.316    # 0.12 in pitch: one rotated 6.8 pt line is 0.09 in wide

Y_RUNG = (0.32, 1.49, 2.66)     # even pitch; the ladder is the one thing that must be regular
Y_ARROW = (0.26, 2.78)          # over-runs the end rungs, so the head is not drawn on the top one
Y_HEADER = 2.72                 # rotated column headers start just above the top rung
Y_PROV = (0.150, 0.035)         # two provenance lines, below the bottom rung

DY_EX = 0.100               # first example line, above its tread
DY_LINE = (0.120, 0.115, 0.125)     # examples, gloss, name: leading within each group
DY_GROUP = 0.050            # extra air between groups, so the three tiers are scannable

MS_STATUS = 16              # marker area in pt^2 -> 4.0 pt across, legible and still secondary


def _fx(x_in):
    return x_in / AX_W


def _fy(y_in):
    return y_in / AX_H


def _status(ax, x_in, y_in, filled):
    """Reports here / does not. Round, ink, sized in points so it stays round at any aspect."""
    ax.scatter([_fx(x_in)], [_fy(y_in)], s=MS_STATUS, marker="o", zorder=6, linewidths=0.7,
               facecolors=TEXT if filled else "white", edgecolors=TEXT)


def _rung_text(ax, level, y_rung):
    """One rung's three tiers: name, italic gloss, examples, stacked upward from its tread.

    Built from the bottom up so the examples always sit the same distance above their tread. The
    top rung's gloss needs a second line and therefore pushes its own name up by one line; that
    happens above the reader's anchor rather than below it, and the rungs stay evenly spaced.
    """
    tiers = ((level["examples"], PT_SMALL, "normal", "normal", DY_LINE[0]),
             (level["gloss"], PT_SMALL, "italic", "normal", DY_LINE[1]),
             (level["name"], PT_ANNOT, "normal", "bold", DY_LINE[2]))
    y = y_rung + DY_EX
    for tier, (group, size, style, weight, lead) in enumerate(tiers):
        y += DY_GROUP if tier else 0.0      # air between tiers, but not under the bottom one
        for line in reversed(group):
            ax.text(_fx(X_TEXT), _fy(y), line, ha="left", va="baseline", fontsize=size,
                    style=style, fontweight=weight, color=TEXT, zorder=5)
            y += lead


def draw_1f(ax):
    blank(ax)
    n_published, published_rungs = _audit()

    # Hung inside the top edge rather than on the helper's default baseline above it: everything
    # this panel draws has to stay within the rect, or it widens the row it is assembled into.
    title(ax, "Evidence ladder", y=0.998, va="top")

    # ---- the axis the rungs are ordered on: independence, not strength ----
    arrow(ax, (_fx(X_RAIL), _fy(Y_ARROW[0])), (_fx(X_RAIL), _fy(Y_ARROW[1])), color=TEXT,
          lw=LW_ARROW, ms=MS_ARROW, zorder=4)
    ax.text(_fx(X_ARROW_LABEL), _fy(sum(Y_ARROW) / 2),
            "Increasing independence from retrieval objective", rotation=90, ha="center",
            va="center", fontsize=PT_ANNOT, color=TEXT, zorder=5)

    # ---- the ladder ----
    for i, (level, y_rung) in enumerate(zip(LEVELS, Y_RUNG)):
        # The tread is the step the level stands on, and the only place colour appears. No leader
        # runs from it out to the status marks: three rungs this far apart are already unambiguous
        # rows, and a rule reaching the far column closed a rectangle around the whole panel.
        # 2.0 pt, twice a plotted series: at 0.6 or 1.0 the rung reads as a rule dividing two
        # blocks of text rather than as a surface the block stands on, and the ladder goes with it.
        ax.plot([_fx(X_RAIL), _fx(X_TREAD_R)], [_fy(y_rung)] * 2, lw=2.0, color=level["tread"],
                solid_capstyle="butt", zorder=2)
        _rung_text(ax, level, y_rung)
        _status(ax, X_PUB, y_rung, i in published_rungs)
        _status(ax, X_OURS, y_rung, i in OURS_RUNGS)

    # One line through this study's three marks: the column is read as a single traverse of the
    # ladder rather than as three unrelated ticks. That contrast is the panel's second sentence.
    ax.plot([_fx(X_OURS)] * 2, [_fy(Y_RUNG[0]), _fy(Y_RUNG[-1])], lw=LW_LINE, color=TEXT,
            solid_capstyle="butt", zorder=5)

    # ---- who reports, kept deliberately small ----
    for x_in, label in ((X_PUB, "Published families"), (X_OURS, "This study")):
        ax.text(_fx(x_in), _fy(Y_HEADER), label, rotation=90, ha="center", va="bottom",
                fontsize=PT_TICK, color=TEXT, zorder=5)

    # ---- provenance ----
    # The audit size comes from the table; "imported" is the one word the top rung needs, because
    # its evaluator is read out of GDSC2 dose-response data rather than measured in this study.
    provenance = (f"{n_published} families surveyed", "GDSC2 evaluator imported")
    for line, y_in in zip(provenance, Y_PROV):
        ax.text(_fx(X_TEXT), _fy(y_in), line, ha="left", va="baseline", fontsize=PT_SMALL,
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
    # would no longer be the 1.376 x 3.70 in rect the composite hands this panel.
    with mpl.rc_context({"savefig.bbox": None, "savefig.pad_inches": 0.0}):
        fig.savefig(out, dpi=400)
    print(f"wrote {out}")
