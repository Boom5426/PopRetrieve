"""PopRetrieve Figure 1 panel d: means tie, distributions separate.

Panel d answers exactly one question: if the mean score cannot tell two candidates apart, how
does the population score change which one is preferred? It is the CONSEQUENCE of b (averaging
can hide what a population is doing) and of c (which statistic enters the score), so it reuses
c's vocabulary rather than inventing one: populations are drawn with fig1_style.cells, the
collapse of a population onto one vector is marked where c marks it, and the two routes keep the
colours they were given there (MEAN orange for the collapsed signature, POP blue for the
population, SHARED grey for what both routes see).

fig1_style.centroid is deliberately NOT drawn on the shared mean, although panel d is one of the
panels its docstring names. In this construction the shared mean falls inside candidate B, so the
orange diamond would sit on top of, and be read as a marker of, the orange population; the dashed
guide carries the shared mean instead. The diamond is kept for the verdict, where it is what the
mean route compares, against the cell cluster the population route compares. Those two marks are
c's two rows, which is what makes the verdict a consequence rather than a new assertion.

THE CONSTRUCTION
----------------
Three populations, drawn once and shown twice: as the marginal along the axis they differ on, and
as the cells themselves. All three are rigidly translated so that their sample means coincide
EXACTLY, which is what lets one guide stand for all three. Without that translation the guide
would sit at a point none of the three clouds actually has, and the panel's whole claim is an
equality of means.

    target Q     SHARED   bimodal, drawn as a filled reference ribbon
    candidate A  POP      bimodal at the target's two modes: distribution-matched
    candidate B  MEAN     unimodal, peaking in the target's valley: mean-matched only

The one number the mean route sees is the same for all three, so it returns a tie. The
populations are not the same, so the population route does not. That verdict is set at the
bottom, because a reader must not have to infer the outcome of the panel that exists to show the
outcome.

THE 3.15 x 1.60 IN RE-LAYOUT, AND THE FOUR THINGS IT MOVED
-----------------------------------------------------------
The panel was authored for a 1.65 x 3.00 in portrait box and now gets a landscape one, roughly
twice as wide and half as tall. It shows the same three populations and returns the same verdict;
the arrangement is not the same, because a landscape box changes what the drawing can afford:

  * The title takes two lines at the top left and the three-population key sits beside it at the
    top right, so the whole width above the construction is one band instead of two stacked ones.
  * The construction keeps its stacking (marginal above cells), because the shared-mean guide can
    only run through both halves if one is above the other. It is the guide that makes the two
    halves one experiment rather than two illustrations, so it is now a SINGLE line from the top
    of the densities to the floor of the scatter, named once at its foot.
  * The clouds cannot grow with the width: their radius is capped by the height of the lower
    band, so the mode separation grows instead (LOBE below). Cells are still drawn on an
    isotropic scale, which is why the radius is converted through K in points rather than through
    two independent axes fractions.
  * The verdict rows carry their candidates' colours: the A and B of each relation are preceded
    by the key's own stub in POP blue and MEAN orange, so "A = B" and "A > B" tie back to the two
    curves above without a legend lookup. Colour travels through those marks, never through the
    colour of the letters.

TWO THINGS THAT CHANGED SIZE OR LEFT, AND WHY
---------------------------------------------
The relation is set at PT_ANNOT, where the portrait cut set it at PT_EQ. It carries no mathtext,
so PT_EQ is not owed to it, and the whole verdict row is now one 7.2 pt line whose emphasis comes
from the two colour marks rather than from a larger type size. That is also what the box allows:
two 9.3 pt rows fit between the axis labels and the bottom edge with about a tenth of a point to
spare, which is not a margin, it is a coincidence waiting to break on another font.

The two italic band labels, "1D marginal view" and "2D cellular population", are gone. They cost
about a fifth of the height this box has, and the caption already carries them word for word:
"shown as 1D marginals above the 2D cells the marginals are computed from". What names the two
halves now is the drawing, the curves above and the cells below, hung on one guide.

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
                        SHARED, TEXT, blank, cells, centroid)

# ------------------------------------------------------------------ the box this is tuned for
# The axes the composite gives panel d (fig1_assemble: half of FIGW less the letter gutter and the
# right margin, by the row height). It cannot be imported from there, because fig1_assemble
# imports this module, so it is restated here and the preview block builds at exactly it.
PANEL_W_IN, PANEL_H_IN = 3.15, 1.60
W_PT, H_PT = PANEL_W_IN * 72.0, PANEL_H_IN * 72.0

# Everything below is laid out in POINTS, x from the left edge and y DOWN from the top edge, and
# converted at the point of use. Axes fractions cannot express "this cloud is as tall as it is
# wide" on a panel whose aspect is about 2:1, and every earlier round of this panel that reasoned
# in fractions had to re-tune each constant when the box changed shape.


def _fx(pt):
    return pt / W_PT


def _fy(pt):
    return 1.0 - pt / H_PT


# ------------------------------------------------------------------ vertical bands, pt from top
# Read top to bottom: what the panel claims and who the three populations are, the two views of
# them hung on one guide, and what the two retrieval routes therefore return.
KEY_Y = (3.8, 12.3, 20.8)       # 8.5 pt leading: the tightest that keeps 7.2 pt rows apart, and
                                # the first row clears the top edge by its own half height
MARG_TOP, MARG_BASE = 27.0, 54.5
SC_CY = 71.5                    # centre of the cell band; its radius follows from R_Q and K
FLOOR_Y = 86.0
UNDER_Y = 91.5                  # the guide's name and the axis name share one line under the floor
VERDICT_Y = (102.0, 110.5)      # the verdict is set off by white space, not by a box or a rule

# ------------------------------------------------------------------ horizontal, pt from left
X0_PT, X1_PT = 3.4, 223.4       # the shared x axis runs the full panel width; panel d has no y axis
KEY_X = 100.0                   # clears the longest title line (90 pt set) by a 10 pt gutter
STUB_W = 9.0                    # key mark: one stroke of the curve the row names
TAG_DX, GLOSS_DX = 12.0, 21.0
MARK_CX, ROUTE_DX = 4.5, 12.0   # the verdict's route mark, and the route it names
# The relation is laid out glyph by glyph, because its two rows must align column for column and
# because the stub has to touch the letter it marks. Arial, Helvetica and Liberation Sans (the
# deck's stack, figstyle.apply_style) are metric compatible, so these advances hold for all three.
CAP_W = 5.04                    # a bold 7.2 pt capital
OP_W = 4.32                     # a bold 7.2 pt "=" or ">"; equal widths keep the rows aligned
REL_STUB_W = 8.0                # the key's stub, shortened to sit inside a relation
REL_MARK_GAP = 2.0              # stub -> its letter: tight, so the pair reads as one token
REL_OP_GAP = 4.0                # token -> operator: loose, so the relation reads as three parts
# The verdict ends where the axis above it ends, so the panel has one right edge, not two.
REL_X = X1_PT - (2 * (REL_STUB_W + REL_MARK_GAP + CAP_W) + 2 * REL_OP_GAP + OP_W)
MARK_PT = 5.4                   # width of a verdict row's mark, a little under the 7.2 pt beside
                                # it, so the two routes are marked at the weight of a key

# ------------------------------------------------------------------ the three populations
# In data units, on one isotropic scale: K points per data unit, horizontally AND vertically.
# The two candidates are separated by SHAPE, not by a fifth colour: A repeats the target's two
# modes, B fills the valley between them. Both integrate to the same mean, which is the only
# statistic the mean route keeps.
D_LO, D_HI = -3.8, 3.8
K = (X1_PT - X0_PT) / (D_HI - D_LO)      # points per data unit
# R_Q is what sets the cloud radius, and a cloud has to stand inside the 31.5 pt between
# MARG_BASE and FLOOR_Y; D_HI was chosen with R_Q so that 0.44 data units land at about 12.7 pt,
# which is the radius the portrait cut used as well. The width bought separation, not size.
LOBE, R_Q, R_A = 2.40, 0.44, 0.42
R_B = (1.00, 0.44)              # wide enough to reach into the target's valley and to leave the
                                # modes about 28 pt of clear space: the clouds must not touch in
                                # 2D, and B must stay dense enough to read as tissue at equal N
N_CELLS = 96                    # equal population sizes, so a difference in the marginals is
                                # shape; large enough that three clouds of it read as tissue
KDE_H = 0.26                    # about 0.6 of a mode radius: smooths the sampling, keeps the two
                                # modes, and lets B's flanks cross the modes' inner flanks


def _ax_x(v):
    """Data units to axes fraction, along the axis the three populations differ on."""
    return _fx(X0_PT + (v - D_LO) * K)


MX = _ax_x(0.0)                 # the shared mean, and the x of the guide both halves hang on
Y_SC = _fy(SC_CY)


def _blobs(spec):
    """Data-unit (cx, cy, rx, ry) blobs into axes coordinates, on one isotropic scale."""
    return [(_ax_x(cx), _fy(SC_CY - cy * K), rx * K / W_PT, ry * K / H_PT)
            for cx, cy, rx, ry in spec]


def _population(ax, spec, colour, seed, s, alpha, zorder):
    """Draw one population as one or two cell blobs, centred exactly on the shared mean.

    A finite sample of a mean-zero population does not have a mean of zero, and at this panel's
    scale that sampling error is a visible fraction of a mode radius. The whole population is
    therefore translated onto the shared mean after sampling, so the guide the panel draws through
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


def _stub(ax, x0_pt, y_pt, colour, w=STUB_W, lw=1.9, alpha=1.0, zorder=5):
    """One stroke of the curve a row names. Colour is carried by the mark, never by the letters."""
    ax.plot([_fx(x0_pt), _fx(x0_pt + w)], [_fy(y_pt)] * 2, color=colour, lw=lw, alpha=alpha,
            solid_capstyle="butt", zorder=zorder)


def _route_mark(ax, x_pt, y_pt, colour):
    """What each retrieval route actually compares, at the size of a key mark.

    Not a colour stub. The verdict rows are the two rows of panel c, and drawing c's glyphs here,
    the collapsed one-vector diamond against a cell population, is what says the verdict follows
    from the operator rather than from a new claim. It also keeps the verdict block from reading
    as a second copy of the population key above it.
    """
    x, y = _fx(x_pt), _fy(y_pt)
    if colour == MEAN:
        # scatter sizes are areas, so a mark MARK_PT across is MARK_PT squared
        centroid(ax, x, y, color=MEAN, size=MARK_PT ** 2)
    else:
        r_pt = MARK_PT / 2.0
        cells(ax, x, y, 11, r_pt / W_PT, r_pt / H_PT, color=POP,
              rng=np.random.default_rng(5), s=2.6, alpha=0.95, zorder=5)


def draw_1d(ax):
    blank(ax)
    # No phrase. The caption states it: "A mean score cannot separate them; a population score
    # prefers A." On the panel the shared-mean marker and the two marginal densities show it.

    # ---- who the three populations are, beside the title and above both views of them ----
    # The target is the reference the candidates are read against, so its key mark carries the
    # same pale block the density carries: the reader meets the filled curve already labelled.
    key = ((SHARED, "Q", "target population"),
           (POP, "A", "distribution-matched"),
           (MEAN, "B", "mean-matched only"))
    for y_pt, (colour, tag, gloss) in zip(KEY_Y, key):
        if colour == SHARED:
            _stub(ax, KEY_X, y_pt + 1.0, colour, lw=4.2, alpha=0.16, zorder=4)
            _stub(ax, KEY_X, y_pt - 0.9, colour, lw=1.9, alpha=0.55)
        else:
            _stub(ax, KEY_X, y_pt, colour)
        ax.text(_fx(KEY_X + TAG_DX), _fy(y_pt), tag, fontsize=PT_ANNOT, color=TEXT,
                fontweight="bold", ha="left", va="center")
        ax.text(_fx(KEY_X + GLOSS_DX), _fy(y_pt), gloss, fontsize=PT_ANNOT, color=TEXT,
                ha="left", va="center")

    # ---- the cells, drawn first because both views are views of them ----
    tgt = _population(ax, [(-LOBE, 0.0, R_Q, R_Q), (LOBE, 0.0, R_Q, R_Q)],
                      SHARED, seed=11, s=3.4, alpha=0.5, zorder=3)
    cand_a = _population(ax, [(-LOBE, 0.0, R_A, R_A), (LOBE, 0.0, R_A, R_A)],
                         POP, seed=23, s=3.2, alpha=0.85, zorder=4)
    cand_b = _population(ax, [(0.0, 0.0, R_B[0], R_B[1])],
                         MEAN, seed=37, s=3.2, alpha=0.85, zorder=4)

    # ---- upper half: the marginal along the axis they differ on ----
    grid = np.linspace(_fx(X0_PT), _fx(X1_PT), 500)
    h = KDE_H * K / W_PT
    dens = [_marginal(x, grid, h) for x in (tgt, cand_a, cand_b)]
    base, scale = _fy(MARG_BASE), (MARG_BASE - MARG_TOP) / H_PT / max(d.max() for d in dens)
    # No separate baseline rule under the densities. The three curves run out flat to both edges
    # and already draw one; a FAINT rule under them was a second horizontal line the eye stopped
    # on, and the panel only needs one, the floor the cells stand on.
    # The target is the reference, so it is the only filled one, and its outline is drawn as a
    # ribbon twice the width of a curve: A is then laid on that ribbon at ordinary curve width and
    # is SEEN to cover it, which is the whole meaning of "distribution-matched".
    ax.fill_between(grid, base, base + dens[0] * scale, color=SHARED, alpha=0.16, lw=0, zorder=2)
    ax.plot(grid, base + dens[0] * scale, color=SHARED, lw=LW_LINE * 2.0, alpha=0.5, zorder=3,
            solid_capstyle="round")
    for d, colour, z in ((dens[2], MEAN, 4), (dens[1], POP, 5)):
        ax.plot(grid, base + d * scale, color=colour, lw=LW_LINE, zorder=z,
                solid_capstyle="round")

    # ---- lower half: the same cells, as cells ----
    ax.plot([_fx(X0_PT), _fx(X1_PT)], [_fy(FLOOR_Y)] * 2, color=FAINT, lw=LW_HAIR, zorder=1)
    ax.text(_fx(X1_PT), _fy(UNDER_Y), "latent dimension 1", fontsize=PT_ANNOT, color=TEXT,
            ha="right", va="center")

    # ---- the one guide both halves are hung on ----
    # A SINGLE line, from the top of the densities to the floor of the scatter, drawn over the
    # cells rather than under them: it has to be followed through candidate B's cloud, which sits
    # on the shared mean, and a guide that disappeared there would leave two local rules again.
    ax.plot([MX, MX], [_fy(MARG_TOP), _fy(FLOOR_Y)], color=SHARED, alpha=0.45, lw=LW_HAIR,
            ls=(0, (2.6, 2.0)), zorder=6)
    ax.text(MX, _fy(UNDER_Y), "shared mean", fontsize=PT_ANNOT, color=TEXT,
            ha="center", va="center")

    # ---- the verdict, which is why the panel is in the figure ----
    # Each row: the mark of what the route compares, the route, then the relation with its two
    # candidates marked in their own colours. Same grammar as the key, so no lookup is needed.
    for y_pt, colour, route, op in ((VERDICT_Y[0], MEAN, "Mean retrieval", "="),
                                    (VERDICT_Y[1], POP, "Population retrieval", ">")):
        _route_mark(ax, MARK_CX, y_pt, colour)
        ax.text(_fx(ROUTE_DX), _fy(y_pt), route, fontsize=PT_ANNOT, color=TEXT,
                ha="left", va="center")
        x = REL_X
        for cand_colour, cand in ((POP, "A"), (MEAN, "B")):
            _stub(ax, x, y_pt, cand_colour, w=REL_STUB_W)
            x += REL_STUB_W + REL_MARK_GAP
            ax.text(_fx(x), _fy(y_pt), cand, fontsize=PT_ANNOT, color=TEXT, fontweight="bold",
                    ha="left", va="center")
            x += CAP_W
            if cand == "A":
                x += REL_OP_GAP
                ax.text(_fx(x), _fy(y_pt), op, fontsize=PT_ANNOT, color=TEXT, fontweight="bold",
                        ha="left", va="center")
                x += OP_W + REL_OP_GAP


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
    fig = plt.figure(figsize=(PANEL_W_IN, PANEL_H_IN))
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
