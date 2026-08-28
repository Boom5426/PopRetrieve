"""PopRetrieve Figure 2 panel 2b: scaling lambda moves the residual only, never the mean.

Source data: none. Seeded gaussian schematic (seed=1). The residual draw is explicitly
re-centred, so the plotted sample mean is identical at every lambda: that identity is the
point of the panel and it is a construction, not a measurement.

Run standalone: python fig2b.py  (writes 2b.png)
"""
import os, numpy as np, matplotlib.pyplot as plt
import sys; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FOCAL, COMP, GREY = "#5185C0", "#E99D4E", "#7A7A7A"
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

LAMBDAS = (0.0, 0.25, 0.5, 1.0)
MU0, SIGMA0, NCELL = 1.0, 0.30, 60


def draw_2b(ax):
    """Same mean at every lambda; only the residual spread changes."""
    rng = np.random.RandomState(1)
    z = rng.normal(size=NCELL)
    z = z - z.mean()                                    # exactly zero-mean residual
    jit = rng.uniform(-0.15, 0.15, size=NCELL)

    ax.axhline(MU0, ls="--", lw=0.9, color=COMP, zorder=1)
    for i, lam in enumerate(LAMBDAS):
        ax.scatter(np.full(NCELL, i) + jit, MU0 + lam * SIGMA0 * z, s=3.0,
                   color=FOCAL, alpha=0.45, edgecolors="none", zorder=2)
        ax.scatter([i], [MU0], marker="x", s=24, color=COMP, lw=1.4, zorder=5)

    # sits ABOVE the dashed mean line, not centred on it: at 1:1 print size a va="center"
    # label is straddled by the line, which runs through the gap between its two rows.
    ax.text(3.24, MU0 + 0.05, "mean $\\mu$\nfixed", ha="left", va="bottom",
            fontsize=6, color=COMP)
    ax.annotate("", xy=(0.0, 1.70), xytext=(3.0, 1.70),
                arrowprops=dict(arrowstyle="-|>", lw=0.8, color="0.45", mutation_scale=7))
    ax.text(1.5, 1.74, "residual shrinks", ha="center", va="bottom",
            fontsize=6, color="0.3")

    ax.set_xticks(range(len(LAMBDAS)))
    ax.set_xticklabels([f"{v:g}" for v in LAMBDAS])
    ax.set_xlim(-0.45, 4.15)
    ax.set_ylim(0.22, 1.92)
    ax.set_yticks([0.5, 1.0, 1.5])
    ax.set_xlabel(r"residual scale $\lambda$")
    ax.set_ylabel("simulated response (a.u.)")
    ax.set_title(r"Scaling $\lambda$ changes only the residual", loc="left")


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(2.4, 1.65))
    draw_2b(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "2b.png"), dpi=200, bbox_inches="tight")
    print("wrote 2b.png")
