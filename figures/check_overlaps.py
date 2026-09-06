"""Pairwise text-overlap check across a whole composite.

Three sources of false positives are filtered, each for a stated reason:
  * annotate() extents include their arrow, so an annotation whose LEADER passes near a label
    reads as a 100% overlap. Only the text box is wanted.
  * matplotlib keeps a Text artist for every tick LOCATOR position, including ticks outside the
    current view limits. Those are never drawn but still report an extent, parked at the axes
    edge, where they collide with whatever is really there.
  * a twinned axes exposes the shared axis's tick labels a second time, at the same coordinates.
  * a COMPOSED EXPRESSION is several Text artists that are one piece of notation. Figure 1 sets
    its subscripts as their own artists rather than as mathtext, because mathtext renders a
    subscript at 0.7x nominal and that falls under that figure's 6.5 pt floor. The subscript is
    then tucked against its base exactly where mathtext would have put it, and pairwise bbox
    comparison reads the tuck as a 30% collision. Fragments of one expression share a gid, so
    they are compared with everything except each other.
"""
import sys, importlib
sys.path.insert(0, "figures")
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from figstyle import apply_style, panel_letter


def visible_ticklabels(ax):
    out = []
    for axis, lim in ((ax.xaxis, ax.get_xlim()), (ax.yaxis, ax.get_ylim())):
        lo, hi = min(lim), max(lim)
        for tick, loc in zip(axis.get_major_ticks(), axis.get_majorticklocs()):
            if lo - 1e-9 <= loc <= hi + 1e-9:
                out.append(tick.label1)
    return out


total = 0
for n in [int(a) for a in sys.argv[1:]] or [1, 2, 3, 4, 5, 6]:
    sys.path.insert(0, f"figures/fig{n}")
    mod = importlib.import_module(f"fig{n}.fig{n}_assemble")
    plt.close("all")
    fig = mod.build(apply_style, panel_letter); fig.canvas.draw()
    r = fig.canvas.get_renderer()
    items, seen = [], set()
    for ax in fig.axes:
        arts = list(ax.texts) + visible_ticklabels(ax) + [ax.xaxis.label, ax.yaxis.label]
        lg = ax.get_legend()
        if lg:
            arts += list(lg.get_texts())
        for t in arts:
            if not t.get_text().strip() or not t.get_visible():
                continue
            if getattr(t, "arrow_patch", None) is not None:
                continue
            try:
                bb = t.get_window_extent(renderer=r)
            except Exception:
                continue
            key = (t.get_text(), int(bb.x0), int(bb.y0))
            if key in seen:
                continue
            seen.add(key)
            items.append((t.get_text().replace("\n", "/")[:30], bb, t.get_gid()))
    hits = 0
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            gi, gj = items[i][2], items[j][2]
            if gi is not None and gi == gj:      # two fragments of one composed expression
                continue
            a, b = items[i][1], items[j][1]
            ox = min(a.x1, b.x1) - max(a.x0, b.x0)
            oy = min(a.y1, b.y1) - max(a.y0, b.y0)
            if ox > 1 and oy > 1:
                frac = (ox * oy) / min(a.width * a.height, b.width * b.height)
                if frac > 0.06:
                    hits += 1
                    print(f"  fig{n}  {frac:4.0%}  {items[i][0]!r}  x  {items[j][0]!r}")
    total += hits
    print(f"figure {n}: {hits} collisions")
    plt.close("all")
print(f"\nTOTAL {total}")
