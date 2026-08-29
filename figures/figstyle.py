"""PopRetrieve Nature-Methods house style, shared across all figure panels.

Mirrors the AllelePerturb manuscript config: sans-serif 6-7 pt, thin INK axes,
no top/right spines, soft Okabe-Ito palette, true print geometry (183 mm double
column), editable-text vector PDF + high-dpi PNG.

Palette (one edit here recolours the whole deck; as of 2026-08-29 that is actually true, because
every panel file imports these names instead of re-declaring the hex values):

  FOCAL  = #0072B2  distributional / PopRetrieve / structure-preserved   (blue)
  COMP   = #D55E00  mean-signature / collapse / structure-lost     (vermillion)
  GREY   = #767676  context / neutral
  GREEN  = #009E73  handed information the retrieval method does not have (controls, ceilings)
  PURPLE = #CC79A7  a second experimental arm carrying no other semantics

These are the Okabe-Ito colourblind-safe hues. This docstring claimed "soft Okabe-Ito" for months
while the values were #5185C0 / #E99D4E / #55966B / #8281B9, which are not Okabe-Ito and are not
independently documented as colourblind-safe. They were also light: #E99D4E has a relative
luminance of 0.42, so 5.6 pt annotation text set in it sat at roughly 2:1 contrast on white, under
any legibility threshold worth naming. The Okabe-Ito pair is darker (0.16 and 0.19), which is why
the small coloured annotations this deck relies on are legible in it.

Colour is never the only channel: every panel that uses hue also separates its series by position,
shape or fill, as Nature requires.
"""
import os
import matplotlib.pyplot as plt
import re

import matplotlib as mpl
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Rectangle

MM = 1.0 / 25.4
COL1_MM, COL2_MM = 89.0, 183.0

FOCAL = "#0072B2"      # distributional / PopRetrieve
COMP = "#D55E00"       # mean / collapse
GREY = "#767676"       # context
LIGHT_GREY = "#D4D4D4"
PURPLE = "#CC79A7"     # second experimental arm, no other semantics
GREEN = "#009E73"      # given information the retrieval method does not have
INK = "#1A1A1A"
# Pale fills for the handful of places that need a wash rather than a stroke. Derived from the
# hues above at about 12% over white, so a recolour of FOCAL/COMP carries them along by intent
# even though they are written out: an alpha-composited fill inherits the hue automatically, but
# these are used where an explicit opaque colour is needed (behind text, under a marker).
FOCAL_TINT = "#DDEBF5"
COMP_TINT = "#FAE6D9"
# ---------------------------------------------------------------------------
# Presentation layer, adopted 2026-08-29 from the AllelePerturb figure 1 style.
#
# It is a RENDERING of the semantics above, not a second set of semantics: blue still means
# population-level, orange still means mean-level. What changes is where the ink goes.
#
#   * The marks carry the colour and the text does not. Every label is INK or META; a coloured
#     5.6 pt annotation is what forced the deck off #E99D4E in the first place (relative
#     luminance 0.66 against white is roughly 2:1, under any readability threshold), and the
#     rule below sidesteps that instead of trading the hue away for it.
#   * A value bar sits on a full-extent TRACK, and every value label is right-aligned past the
#     end of the track rather than chasing its own bar tip. One vertical reading line, not eight.
#   * Groups are separated by a RULE hairline, not by a box.
#   * Secondary information is META grey.
#
# NO MIDDLE-DOT TOKEN. The reference joins a name and its n on one line ("controlled  .  n = 90"),
# and that was tried here and removed: the form needs about 0.55 in per slot, and this deck's
# panels give three slots 0.53 in each, so all three labels overlapped by more than half their
# width. Where a slot is narrow the reference splits the pair over two lines too (its panel d),
# and that is what the panels here do. A convention no panel can follow is not a convention.
#
# ADOPTED BY the whole deck: main figures 1-5 and Extended Data 1-7. Nothing is left on the
# saturated FOCAL/COMP pair, and no figure colours its text. The two enforcement passes that
# hold this are in figures/build_all.py and figures/build_ed.py.
#
# Figure 1 needed one exception and got it as a mark rather than as a licence: its panel c row
# labels ("Mean", "Population") name whole rows and have no single adjacent mark to bind them to
# a family, so each carries a swatch. Every other label in the deck sits beside a coloured mark
# and is simply set in ink.
#
# These four ARE this project's original palette, which the reference figure also uses: the soft
# family was never invented, it was replaced deck-wide in an earlier pass and is now back under
# names that say what they are for. An earlier draft of this block reserved them for large
# filled areas and kept the saturated pair for thin strokes; that exception was tried and
# dropped, because the reference draws its own 1 pt lines and 2.6 pt dots in exactly these tones
# and they hold at print size. The contrast objection that motivated the exception applies to
# TEXT, and the first rule above already removes coloured text.
FOCAL_SOFT = "#5185C0"     # population-level, as a filled area
COMP_SOFT = "#E99D4E"      # mean-level, as a filled area
GREEN_SOFT = "#55966B"     # given information the retrieval method does not have
PURPLE_SOFT = "#8281B9"    # second experimental arm, no other semantics
SLATE = "#4F6D7A"          # a filled bar carrying no family semantics
TRACK = "#EDEDED"          # the full-extent track a value bar is drawn on
RULE = "#E6E6E6"           # hairline group separator
META = "#7A7A7A"           # secondary text: units, n, provenance
ACCENT = "#2A7F78"         # RESERVED, unused in the current deck: the emphasised element
ACCENT_TINT = "#E6F1EF"
FOCAL_SOFT_TINT = "#E4EDF6"
COMP_SOFT_TINT = "#FBF0E4"
# The signed advantage map, in the soft family. DIVMAP is kept as it is: it is still what the
# figures that have not adopted this layer use, and a colormap swapped underneath them would
# change their meaning silently.
DIVMAP_SOFT = LinearSegmentedColormap.from_list("dart_div_soft",
                                                [COMP_SOFT, "#f7f7f7", FOCAL_SOFT])


def soften_axes(fig, exclude=()):
    """Put every axes in the figure on hairline spines and short RULE-grey ticks.

    Centralised on purpose. The alternative is the same four lines pasted into twenty-two panel
    modules, which is how the palette itself came to be duplicated across forty-three files and
    silently drifted. Colorbar axes and any axes passed in ``exclude`` are left alone: a colorbar
    outline in RULE grey reads as a rendering artifact rather than as a frame.
    """
    for ax in fig.axes:
        if ax in exclude or getattr(ax, "_colorbar", None) is not None:
            continue
        for side, sp in ax.spines.items():
            if sp.get_visible():
                sp.set_color(RULE)
                sp.set_linewidth(0.6)
        ax.tick_params(which="both", length=2.2, width=0.6, color=RULE, labelcolor=INK)
    return fig


# signed PopRetrieve-minus-mean advantage: orange (mean) <- white -> blue (PopRetrieve)
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


def strip_titles(fig):
    """Remove every axes title from a composite. A Nature panel carries no title.

    The explanation belongs to the caption. A Nature-family panel carries axis labels, tick
    labels, direct labels on the marks themselves and a key, and nothing else; the figure legend
    is a bold one-sentence title for the whole figure followed by one entry per panel letter, and
    text on the panel that repeats the caption is what production asks authors to delete.

    This deck was authored the other way, with a claim sentence set over each of its 40 panels.
    Every one of those claims now lives in its figure's caption. Calling this at the end of a
    composite's ``build()`` is what guarantees a panel script cannot put a title back into the
    figure that ships: the panel scripts keep their own ``set_title`` calls, so a standalone
    ``python figNx.py`` still labels its preview, and the composite strips them.

    Titles set with ``loc="left"`` live in a different artist from centred ones, which is why all
    three locations are cleared rather than just ``ax.set_title("")``.
    """
    for ax in fig.axes:
        for loc in ("left", "center", "right"):
            ax.set_title("", loc=loc)
    return fig


def text_run(ax, x0, y, parts, fontsize, gap=0.008, va="center"):
    """Lay out a left-to-right run of differently styled text fragments by MEASURED width.

    ``parts`` is a sequence of ``(text, colour)`` or ``(text, colour, kwargs)`` tuples, where
    ``kwargs`` reaches ``ax.text`` (``fontweight``, ``style``, ...). Returns the x cursor after the
    last fragment, in data coordinates, so a following arrow or marker can be placed against it.

    Hard-coding the x of each fragment is only correct for one axes width and one font: schematic
    panels that did it overlapped their own labels as soon as the panel was resized, and clipped
    them when a fallback font measured wider than the one they were tuned on. Measuring in display
    space and converting back removes both failure modes.

    The panel must be drawn on a canvas with a renderer (Agg is what the build uses); this calls
    ``fig.canvas.draw()`` once per run.
    """
    fig = ax.figure
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    inv = ax.transData.inverted()
    x = x0
    for part in parts:
        txt, colour = part[0], part[1]
        kw = part[2] if len(part) > 2 else {}
        t = ax.text(x, y, txt, ha="left", va=va, fontsize=fontsize, color=colour, **kw)
        x = inv.transform((t.get_window_extent(renderer=renderer).x1, 0))[0] + gap
    return x


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
# The smallest NOMINAL size at which a label containing a mathtext sub/superscript still prints
# its subscript at or above MIN_PT: 5.0 / 0.7 = 7.15, rounded up. Any label carrying "$..._x$" or
# "$...^x$" is set at this size rather than at the 5.4-7.0 pt of the plain annotations around it,
# because get_fontsize() reports the nominal size and the gate in save() cannot see the shrunk
# glyph. Two tenths of a point is invisible next to a 7 pt axis label; a 4.2 pt subscript is not.
PT_MATH = 7.2

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
