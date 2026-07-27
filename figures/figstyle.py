"""EvalShift Nature-Methods house style, shared across all figure panels.

Mirrors the AllelePerturb manuscript config: sans-serif 6-7 pt, thin INK axes,
no top/right spines, soft Okabe-Ito palette, true print geometry (183 mm double
column), editable-text vector PDF + high-dpi PNG.

Palette (one edit here recolours the whole deck):
  FOCAL  = #5185C0  distributional / EvalShift / structure-preserved   (blue)
  COMP   = #E99D4E  mean-signature / collapse / structure-lost     (orange)
  GREY   = #7A7A7A  context / neutral
"""
import os
import matplotlib.pyplot as plt
import re

import matplotlib as mpl
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Rectangle

MM = 1.0 / 25.4
COL1_MM, COL2_MM = 89.0, 183.0

FOCAL = "#5185C0"      # distributional / EvalShift
COMP = "#E99D4E"       # mean / collapse
GREY = "#7A7A7A"       # context
LIGHT_GREY = "#D9D9D9"
PURPLE = "#8281B9"
GREEN = "#55966B"
INK = "#1A1A1A"
# signed EvalShift-minus-mean advantage: orange (mean) <- white -> blue (EvalShift)
DIVMAP = LinearSegmentedColormap.from_list("dart_div", [COMP, "#f7f7f7", FOCAL])


def apply_style(sizes=(8, 7, 6)):
    """Set the house rcParams. ``sizes`` = (title, label, tick) point sizes.

    This is the entry point every ``figN_assemble.py`` calls. It used to live only in an
    external authoring skill and was never vendored into the repo, so ``build(apply_style,
    panel_letter)`` could not run from a checkout and none of the six main composites were
    regenerable from committed code. It is defined here now so the deck rebuilds from the
    repository alone.
    """
    title, label, tick = sizes
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "Liberation Sans", "Nimbus Sans", "DejaVu Sans"],
        "font.size": label, "axes.titlesize": title, "axes.labelsize": label,
        "xtick.labelsize": tick, "ytick.labelsize": tick, "legend.fontsize": tick,
        "figure.titlesize": title,
        "axes.linewidth": 0.5, "lines.linewidth": 0.75, "patch.linewidth": 0.5,
        "xtick.major.width": 0.5, "ytick.major.width": 0.5,
        "xtick.major.size": 2.2, "ytick.major.size": 2.2,
        "axes.labelcolor": INK, "axes.edgecolor": INK, "xtick.color": INK, "ytick.color": INK,
        "text.color": INK, "axes.titlecolor": INK,
        "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False,
        "figure.facecolor": "white", "savefig.facecolor": "white",
        "savefig.bbox": "tight", "savefig.pad_inches": 0.01,
        "pdf.fonttype": 42, "ps.fonttype": 42, "svg.fonttype": "none",
    })


def apply_rcparams():
    """Backwards-compatible alias for the panel scripts that call it with no arguments."""
    apply_style(sizes=(7, 7, 6))


def pin_canvas(fig):
    """Pin ``bbox_inches="tight"`` to the AUTHORED canvas, so the exported width is deterministic.

    Every main figure is authored at the final printed width (~6.90 in, a hair under the 6.93 in
    manuscript text block) so that nominal point size equals printed point size. ``savefig`` then
    writes with ``bbox_inches="tight"``, which crops the page back to the ink and hands LaTeX a
    figure NARROWER than the authored canvas; ``\\includegraphics[width=\\textwidth]`` magnifies it
    again and the printed sizes are no longer the authored ones. Worse, the crop makes the exported
    width an emergent property of whatever text happens to sit furthest out, so a later annotation
    can move the page width, and past 6.93 in it silently reintroduces DOWN-scaling and the deck
    drops back under the 5 pt production floor.

    This appends a transparent, unstroked, full-canvas rectangle. It contributes extent and no ink,
    so the tight bbox is the canvas: the exported media box is the authored size plus
    ``savefig.pad_inches`` on each side, whatever the panels later grow into.

    Two obligations come with it. The canvas is now the page, so (1) nothing may hang OUTSIDE the
    canvas, since the bbox is the union of the patch and the ink and an overhang still enlarges the
    page, and (2) empty canvas margin is no longer cropped away, so the margins are authored.
    """
    fig.patches.append(Rectangle((0, 0), 1, 1, transform=fig.transFigure,
                                 fill=False, ec="none", lw=0, zorder=-10))
    return fig


def panel_letter(ax, letter, dx=-0.11, dy=1.06, case="lower"):
    s = letter.lower() if case == "lower" else letter.upper()
    ax.text(dx, dy, s, transform=ax.transAxes, fontsize=8, fontweight="bold",
            va="top", ha="left", color=INK)


# --------------------------------------------------------------------------------------------
# Typography floor, enforced at build time
# --------------------------------------------------------------------------------------------
# Nature Portfolio production rejects text below 5 pt at final printed size, and 5 pt is a floor
# rather than a target: 6-7 pt is what is actually legible in a 183 mm double-column figure. Panel
# scripts drift below it silently, because the natural response to a crowded panel is to shrink the
# annotation rather than to cut it, and nothing complains until the proofs come back.
#
# So nothing complains until here. `save()` walks every Text artist in the rendered figure and
# refuses to write the file if any of them is under the floor. The correct fix when this fires is
# almost never "set it to 5.0": it is to DELETE the annotation and move that sentence into the
# caption, which is where dense explanation belongs and where it costs no space.
MIN_PT = 5.0


def _text_sizes(fig):
    """Every Text artist actually drawn, with its effective point size."""
    out = []
    for t in fig.findobj(mpl.text.Text):
        s = t.get_text()
        if not s or not str(s).strip():
            continue
        out.append((t, float(t.get_fontsize()), str(s).replace("\n", " ")[:44]))
    return out


# Matplotlib renders a mathtext sub/superscript at this fraction of the surrounding size. It is
# not configurable through rcParams, and get_fontsize() reports the NOMINAL size of the whole
# string, so a 5.6 pt label containing $P_{1}$ prints its subscript at 3.9 pt while the gate below
# sees only 5.6. Audited 2026-07-27.
MATHTEXT_SUBSUP_SCALE = 0.7
_MATH_SUBSUP = re.compile(r"\$[^$]*[\^_][^$]*\$")


def mathtext_offenders(fig, floor=MIN_PT):
    """Text whose mathtext sub/superscript prints below `floor`, with its effective size.

    Reported separately from assert_min_fontsize rather than folded into it: raising these to
    compliance means raising the NOMINAL size to floor / 0.7 (about 7.2 pt for a 5 pt floor),
    which is a re-authoring decision about the panel, not a one-line fix.
    """
    out = []
    for t, sz, txt in _text_sizes(fig):
        if _MATH_SUBSUP.search(str(t.get_text())):
            eff = sz * MATHTEXT_SUBSUP_SCALE
            if eff < floor - 1e-6:
                out.append((round(eff, 2), sz, txt))
    return sorted(out)


def assert_min_fontsize(fig, floor=MIN_PT, strict=True):
    """Raise if any rendered text is below the production floor. Returns the offenders.

    NOTE what this does NOT catch, and why the caller must also look at mathtext_offenders():
    it compares NOMINAL point sizes, so it is blind to mathtext sub/superscript shrinkage, and it
    knows nothing about the document's text width, so a figure authored wider than the text block
    is scaled down by includegraphics and can print below the floor with this returning clean.
    """
    bad = [(sz, txt) for _t, sz, txt in _text_sizes(fig) if sz < floor - 1e-6]
    if bad and strict:
        lines = "\n".join(f"    {sz:.1f} pt  {txt!r}" for sz, txt in sorted(bad)[:12])
        raise ValueError(
            f"{len(bad)} text element(s) below the {floor} pt production floor:\n{lines}\n"
            f"  Do not simply raise them to {floor}. A panel that needs 4 pt text is a panel with "
            f"too much text: cut the annotation and put the sentence in the caption.")
    return bad


def save(fig, stem, dpi=600, check=True):
    """Export to the formats Nature accepts, after enforcing the typography floor."""
    if check:
        assert_min_fontsize(fig)
    stem = str(stem)
    fig.savefig(stem + ".pdf", dpi=dpi)          # vector, editable text (pdf.fonttype 42)
    fig.savefig(stem + ".svg")                   # vector, editable text (svg.fonttype none)
    fig.savefig(stem + ".png", dpi=dpi)          # review copy
    return stem
