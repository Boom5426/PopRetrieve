"""PopRetrieve Figure 1 panel d: means tie, distributions separate.

Panel d answers exactly one question: if the mean score cannot tell two candidates apart, how
does the population score change which one is preferred? It is the CONSEQUENCE of b (averaging
can hide what a population is doing) and of c (which statistic enters the score), so it reuses
c's vocabulary rather than inventing one: populations are drawn with fig1_style.cells, the
collapse of a population onto one vector is stated where c states it, and the two routes keep the
colours they were given there (MEAN orange for the collapsed signature, POP blue for the
population, SHARED grey for what both routes see).

fig1_style.centroid is deliberately NOT drawn on the shared mean, although panel d is one of the
panels its docstring names. In this construction the shared mean falls inside candidate B, so the
orange diamond would sit on top of, and be read as a marker of, the orange population; the dashed
rule carries the shared mean instead. The diamond is kept for the verdict, where it is what the
mean route compares, against the cell cluster the population route compares. Those two marks are
c's two rows, which is what makes the verdict a consequence rather than a new assertion.

THE CONSTRUCTION
----------------
Three populations, drawn once and shown twice: as the marginal along the axis they differ on, and
as the cells themselves. All three are rigidly translated so that their sample means coincide
EXACTLY, which is what lets one dashed rule stand for all three. Without that translation the
rule would sit at a point none of the three clouds actually has, and the panel's whole claim is
an equality of means.

    target Q     SHARED   bimodal
    candidate A  POP      bimodal at the target's two modes: distribution-matched
    candidate B  MEAN     unimodal, peaking in the target's valley: mean-matched only

The one number the mean route sees is the same for all three, so it returns a tie. The
populations are not the same, so the population route does not. That verdict is set at the
bottom, at PT_EQ, because a reader must not have to infer the outcome of the panel that exists
to show the outcome.

Nothing here is measured. The populations are drawn from a seeded generator, no file in results/
is read, and the caption says the panel is a constructed illustration.

Run standalone: python3 fig1d.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fig1_style import (FAINT, LW_HAIR, LW_LINE, MEAN, POP, PT_ANNOT,  # noqa: E402
                        PT_EQ, SHARED, TEXT, blank, cells, centroid, title)

# ------------------------------------------------------------------ the axis the halves share
# The axes the composite gives panel d (fig1_assemble: FIGW * ROW1_SHARE["d"] less the letter
# gutter and the right margin, by ROW1_H). It cannot be imported from there, because
# fig1_assemble imports this module, so it is restated here and the preview block builds at
# exactly it. Everything below is in axes fractions, and these two numbers are what turn a radius
# or a mark width into the same number of inches horizontally as vertically.
PANEL_W_IN, PANEL_H_IN = 1.652, 3.000
ASPECT = PANEL_W_IN / PANEL_H_IN

X0, X1 = 0.015, 0.985      # the shared x axis runs the full panel width; panel d has no y axis
D_LO, D_HI = -2.0, 2.0     # arbitrary units: this panel measures nothing
SX = (X1 - X0) / (D_HI - D_LO)
SY = SX * ASPECT

# ------------------------------------------------------------------ vertical stack, axes fraction
# Read top to bottom: what the panel claims, who the three populations are, the two views of them,
# and what the two retrieval routes therefore return.
Y_KEY = (0.893, 0.853, 0.813)
Y_LAB_1D = 0.768
Y_MEAN = 0.728            # the rule is named once, above the half the reader meets first
Y_BAND_TOP, Y_BASE = 0.700, 0.512
Y_LAB_2D = 0.486
Y_SC_TOP, Y_FLOOR = 0.464, 0.268
Y_XLABEL = 0.244
Y_VERDICT = (0.135, 0.045)   # the verdict is set off by white space, not by a box or a rule

X_SWATCH = (0.000, 0.045)  # flush left with the panel letter and the title, which title() sets at 0
X_TAG, X_TEXT = 0.058, 0.115
MARK_PT = 5.4              # width of a verdict row's mark, a little under the 7.2 pt beside it, so
                           # the two routes are marked at the weight of a key and not of a figure

# ------------------------------------------------------------------ the three populations
# In data units. The two candidates are separated by SHAPE, not by a fifth colour: A repeats the
# target's two modes, B fills the valley between them. Both integrate to the same mean, which is
# the only statistic the mean route keeps.
LOBE, R_Q, R_A = 1.25, 0.44, 0.42
R_B = (0.70, 0.45)         # wide enough to span the target's valley, narrow enough not to reach
                           # into its modes: the clouds must not touch in the 2D view
N_CELLS = 96               # equal population sizes, so a difference in the marginals is shape;
                           # large enough that three clouds of it read as tissue, not as dots
KDE_H = 0.19               # about half a mode radius: smooths the sampling, keeps the two modes
Y_SC = (Y_FLOOR + Y_SC_TOP) / 2.0
MX = X0 + (0.0 - D_LO) * SX


def _ax_x(v):
    return X0 + (v - D_LO) * SX


def _blobs(spec):
    """Data-unit (cx, cy, rx, ry) blobs into axes coordinates."""
    return [(_ax_x(cx), Y_SC + cy * SY, rx * SX, ry * SY) for cx, cy, rx, ry in spec]


def _population(ax, spec, colour, seed, s, alpha, zorder):
    """Draw one population as one or two cell blobs, centred exactly on the shared mean.

    A finite sample of a mean-zero population does not have a mean of zero, and at this panel's
    scale that sampling error is a visible fraction of a mode radius. The whole population is
    therefore translated onto the shared mean after sampling, so the rule the panel draws through
    all three is the mean all three actually have. cells() draws them, so the glyph is the one
    used everywhere else in the figure; only the offsets of what it drew are corrected.
    """
    rng = np.random.default_rng(seed)
    parts, colls = [], []
    for cx, cy, rx, ry in _blobs(spec):
        x, y = cells(ax, cx, cy, N_CELLS // len(spec), rx, ry, color=colour, rng=rng,
                     s=s, alpha=alpha, zorder=zorder)
        parts.append((x, y))
        colls.append(ax.collections[-1])
    dx = np.concatenate([p[0] for p in parts]).mean() - MX
    dy = np.concatenate([p[1] for p in parts]).mean() - Y_SC
    for coll, (x, y) in zip(colls, parts):
        coll.set_offsets(np.column_stack([x - dx, y - dy]))
    xs = np.concatenate([p[0] for p in parts]) - dx
    ys = np.concatenate([p[1] for p in parts]) - dy
    # the equality of means is the panel's claim, so it is asserted rather than assumed
    assert abs(xs.mean() - MX) < 1e-12 and abs(ys.mean() - Y_SC) < 1e-12
    return xs


def _marginal(x, grid, h):
    """Gaussian kernel density of the cells that were actually drawn, so the two halves of the
    panel are two views of one sample rather than two independent illustrations."""
    z = (grid[None, :] - x[:, None]) / h
    return np.exp(-0.5 * z ** 2).sum(0) / (len(x) * h * np.sqrt(2 * np.pi))


def _stub(ax, y, colour):
    """The key mark: one stroke of the curve this row names. Colour is carried by the mark."""
    ax.plot(X_SWATCH, [y, y], color=colour, lw=1.9, solid_capstyle="butt", zorder=5)


def _route_mark(ax, y, colour):
    """What each retrieval route actually compares, at the size of a key mark.

    Not a colour stub. The verdict rows are the two rows of panel c, and drawing c's glyphs here,
    the collapsed one-vector diamond against a cell population, is what says the verdict follows
    from the operator rather than from a new claim. It also keeps the verdict block from reading
    as a second copy of the population key above it.
    """
    x = sum(X_SWATCH) / 2.0
    if colour == MEAN:
        # scatter sizes are areas, so a mark MARK_PT across is MARK_PT squared
        centroid(ax, x, y, color=MEAN, size=MARK_PT ** 2)
    else:
        r_pt = MARK_PT / 2.0
        cells(ax, x, y, 11, r_pt / (PANEL_W_IN * 72.0), r_pt / (PANEL_H_IN * 72.0),
              color=POP, rng=np.random.default_rng(5), s=2.6, alpha=0.95, zorder=5)


def draw_1d(ax):
    blank(ax)
    title(ax, "Means tie,\ndistributions separate", x=0.0, y=1.0, va="top", linespacing=1.15)

    # ---- who the three populations are, before either view of them ----
    key = ((SHARED, "Q", "target population"),
           (POP, "A", "distribution-matched"),
           (MEAN, "B", "mean-matched only"))
    for y, (colour, tag, gloss) in zip(Y_KEY, key):
        _stub(ax, y, colour)
        ax.text(X_TAG, y, tag, fontsize=PT_ANNOT, color=TEXT, fontweight="bold",
                ha="left", va="center")
        ax.text(X_TEXT, y, gloss, fontsize=PT_ANNOT, color=TEXT, ha="left", va="center")

    # ---- the cells, drawn first because both views are views of them ----
    tgt = _population(ax, [(-LOBE, 0.0, R_Q, R_Q), (LOBE, 0.0, R_Q, R_Q)],
                      SHARED, seed=11, s=3.6, alpha=0.55, zorder=3)
    cand_a = _population(ax, [(-LOBE, 0.0, R_A, R_A), (LOBE, 0.0, R_A, R_A)],
                         POP, seed=23, s=3.4, alpha=0.85, zorder=4)
    cand_b = _population(ax, [(0.0, 0.0, R_B[0], R_B[1])],
                         MEAN, seed=37, s=3.4, alpha=0.85, zorder=4)

    # ---- upper half: the marginal along the axis they differ on ----
    ax.text(0.0, Y_LAB_1D, "1D marginal view", fontsize=PT_ANNOT, color=TEXT,
            style="italic", ha="left", va="center")
    grid = np.linspace(X0, X1, 400)
    h = KDE_H * SX
    dens = [_marginal(x, grid, h) for x in (tgt, cand_a, cand_b)]
    scale = (Y_BAND_TOP - Y_BASE) / max(d.max() for d in dens)
    ax.plot([X0, X1], [Y_BASE, Y_BASE], color=FAINT, lw=LW_HAIR, zorder=1)
    # the target is the reference, so it is the only filled one: the candidates are read against it
    ax.fill_between(grid, Y_BASE, Y_BASE + dens[0] * scale, color=SHARED, alpha=0.16,
                    lw=0, zorder=2)
    for d, colour, z in ((dens[0], SHARED, 3), (dens[2], MEAN, 4), (dens[1], POP, 5)):
        ax.plot(grid, Y_BASE + d * scale, color=colour, lw=LW_LINE, zorder=z,
                solid_capstyle="round")

    # ---- lower half: the same cells, as cells ----
    ax.text(0.0, Y_LAB_2D, "2D cellular population", fontsize=PT_ANNOT, color=TEXT,
            style="italic", ha="left", va="center")
    ax.plot([X0, X1], [Y_FLOOR, Y_FLOOR], color=FAINT, lw=LW_HAIR, zorder=1)
    ax.text(0.5, Y_XLABEL, "latent dimension 1", fontsize=PT_ANNOT, color=TEXT,
            ha="center", va="top")

    # ---- the one rule both halves are hung on ----
    # Two segments rather than one: the label of the lower half crosses the rule's x, and a rule
    # printed through a word costs more than the interruption does.
    for lo, hi in ((Y_BASE, Y_MEAN - 0.016), (Y_FLOOR, Y_SC_TOP)):
        ax.plot([MX, MX], [lo, hi], color=SHARED, lw=LW_HAIR, ls=(0, (2.6, 2.0)), zorder=2)
    ax.text(MX, Y_MEAN, "Shared mean", fontsize=PT_ANNOT, color=TEXT,
            ha="center", va="center")

    # ---- the verdict, which is why the panel is in the figure ----
    for y, colour, route, relation in ((Y_VERDICT[0], MEAN, "Mean retrieval", "A = B"),
                                       (Y_VERDICT[1], POP, "Population retrieval", "A > B")):
        _route_mark(ax, y, colour)
        ax.text(X_TAG, y, route, fontsize=PT_ANNOT, color=TEXT, ha="left", va="center")
        ax.text(1.0, y, relation, fontsize=PT_EQ, color=TEXT, fontweight="bold",
                ha="right", va="center")


# --------------------------------------------------------------------------------- preview
def _min_effective_pt(fig):
    """Smallest size any Text on the panel actually prints at, mathtext sub/superscripts at the
    0.7x matplotlib renders them at. fig1_assemble asserts the same floor over the whole figure."""
    import re

    import matplotlib.text as mtext
    subsup = re.compile(r"\$[^$]*[\^_][^$]*\$")
    sizes = []
    for t in fig.findobj(mtext.Text):
        s = str(t.get_text())
        if not s.strip() or not t.get_visible():
            continue
        sizes.append((t.get_fontsize() * (0.7 if subsup.search(s) else 1.0), s.replace("\n", "/")))
    return sorted(sizes)


def _collisions(fig, ax, tol_pt=0.4):
    """Pairs of labels whose tight bboxes overlap. The floor keeps type legible one label at a
    time; on a panel this dense the other way to lose a word is to print it under another one."""
    import matplotlib.text as mtext
    r = fig.canvas.get_renderer()
    boxes = [(str(t.get_text()).replace("\n", "/")[:22], t.get_window_extent(r))
             for t in ax.findobj(mtext.Text) if str(t.get_text()).strip() and t.get_visible()]
    pad = tol_pt * fig.dpi / 72.0
    hits = []
    for i, (li, bi) in enumerate(boxes):
        for lj, bj in boxes[i + 1:]:
            if (bi.x0 < bj.x1 - pad and bj.x0 < bi.x1 - pad
                    and bi.y0 < bj.y1 - pad and bj.y0 < bi.y1 - pad):
                hits.append((li, lj))
    return hits


def _overhangs(fig, ax, tol_pt=0.25):
    """Every artist that leaves the axes, and by how much. Text and clip_on=False artists do not
    clip, so anything hanging out here would widen the composite page (figstyle.pin_canvas)."""
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    box, out = ax.bbox, []
    # blank() has switched the axis furniture off, so XAxis/YAxis render no ink; their reported
    # extent is a phantom of tick machinery that is never drawn. Everything else is measured.
    skip = set(ax.spines.values()) | {ax.patch, ax.xaxis, ax.yaxis}
    assert not ax.axison, "panel d draws no axis furniture; if that changes, measure it here"
    for a in ax.get_children():
        if not a.get_visible() or a in skip:
            continue
        bb = a.get_tightbbox(r)
        if bb is None:
            continue
        over = [(box.x0 - bb.x0), (bb.x1 - box.x1), (box.y0 - bb.y0), (bb.y1 - box.y1)]
        over = [o * 72.0 / fig.dpi for o in over]
        if max(over) > tol_pt:
            label = getattr(a, "get_text", lambda: type(a).__name__)() or type(a).__name__
            out.append((str(label).replace("\n", "/")[:34],
                        [round(o, 2) for o in over]))
    return out


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from figstyle import apply_style  # noqa: E402
    from fig1_style import PT_FLOOR, PT_TICK, PT_TITLE  # noqa: E402

    # Exactly the axes the composite gives panel d, so a position tuned here is the one that ships.
    apply_style(sizes=(PT_TITLE, PT_ANNOT, PT_TICK))
    fig = plt.figure(figsize=(1.652, 3.000))
    ax = fig.add_axes([0.0, 0.0, 1.0, 1.0])
    draw_1d(ax)

    sizes = _min_effective_pt(fig)
    assert sizes[0][0] >= PT_FLOOR - 1e-6, f"below the {PT_FLOOR} pt floor: {sizes[:4]}"
    print(f"smallest effective size: {sizes[0][0]:.2f} pt  ({sizes[0][1]})")

    hang = _overhangs(fig, ax)
    for label, over in hang:
        print(f"  hangs out [left, right, bottom, top] pt: {over}  {label}")
    assert not hang, "artists leave the axes; see above"

    hits = _collisions(fig, ax)
    for a, b in hits:
        print(f"  labels overlap: {a!r} / {b!r}")
    assert not hits, "labels overlap; see above"
    print("every artist inside the axes, and no two labels overlap")

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "1d.png")
    fig.savefig(out, dpi=400)
    print(f"wrote {out}")
