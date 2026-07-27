"""EvalShift Figure 2 panel 2a: the mean signature is the lambda -> 0 limit (schematic).

Source data: none. Seeded gaussian schematic (seed=0) illustrating the algebra
    X = mu + lambda * eps,  E[eps] = 0
and its retrieval consequence: as lambda -> 0 each population collapses onto its mean
signature and the population-to-population score becomes the mean-to-mean score. That
mean-to-mean value is exactly the floor measured from data in panel c.

Run standalone: python fig2a.py  (writes 2a.png)
"""
import os, numpy as np, matplotlib.pyplot as plt
import sys; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FOCAL, COMP, GREY = "#5185C0", "#E99D4E", "#7A7A7A"
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Schematic geometry in axes fraction. The panel is wide and short, so the residual
# clouds get an anisotropic sigma in order to render visually round.
_ASPECT = 2.15
_SD_X = 0.030
_Y0 = 0.545          # cloud centre / mean-marker baseline
_Y_LINK = 0.760      # mean-to-mean connector
_N = 70


def _cloud(ax, cx, color, rng, alpha=0.5):
    pts = rng.normal([cx, _Y0], [_SD_X, _SD_X * _ASPECT], size=(_N, 2))
    pts = pts - pts.mean(0) + np.array([cx, _Y0])       # sample mean is exactly mu
    ax.scatter(pts[:, 0], pts[:, 1], s=3.4, color=color, alpha=alpha,
               edgecolors="none", zorder=2)


def _mean_marker(ax, cx):
    ax.scatter([cx], [_Y0], marker="x", s=22, color=COMP, lw=1.3, zorder=5)


def _link(ax, x0, x1, label):
    ax.annotate("", xy=(x1, _Y_LINK), xytext=(x0, _Y_LINK),
                arrowprops=dict(arrowstyle="<|-|>", lw=0.7, color=COMP,
                                mutation_scale=6, shrinkA=0, shrinkB=0))
    for x in (x0, x1):
        ax.plot([x, x], [_Y0 + 0.06, _Y_LINK], lw=0.5, color=COMP, alpha=0.5, zorder=1)
    ax.text((x0 + x1) / 2, _Y_LINK + 0.03, label, ha="center", va="bottom",
            fontsize=6, color=COMP)


def draw_2a(ax):
    """X = mu + lambda*eps: at lambda -> 0 two populations become two mean signatures."""
    ax.axis("off"); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    rng = np.random.RandomState(0)

    ax.text(0.0, 0.965, r"$X=\mu+\lambda\,\epsilon,\qquad \mathbb{E}[\epsilon]=0$",
            ha="left", va="center", fontsize=7.5)

    # left: observed populations, lambda = 1
    xP, xQ = 0.095, 0.305
    _cloud(ax, xP, FOCAL, rng); _cloud(ax, xQ, GREY, rng, alpha=0.58)
    _mean_marker(ax, xP); _mean_marker(ax, xQ)
    ax.text(xP, 0.345, r"$P_d$", ha="center", va="top", fontsize=6.5, color=FOCAL)
    ax.text(xQ, 0.345, r"$Q$", ha="center", va="top", fontsize=6.5, color="0.35")
    _link(ax, xP, xQ, r"$d(\mu_P,\mu_Q)$")
    ax.text((xP + xQ) / 2, 0.215, r"observed populations ($\lambda=1$)",
            ha="center", va="top", fontsize=6.5, color="0.25")

    # collapse
    ax.annotate("", xy=(0.585, _Y0), xytext=(0.430, _Y0),
                arrowprops=dict(arrowstyle="-|>", lw=1.0, color="0.45", mutation_scale=8))
    ax.text(0.507, _Y0 + 0.055, r"$\lambda\to0$", ha="center", va="bottom",
            fontsize=6.5, color="0.25")

    # right: mean signatures, lambda = 0
    xP2, xQ2 = 0.695, 0.900
    _mean_marker(ax, xP2); _mean_marker(ax, xQ2)
    ax.text(xP2, 0.345, r"$\mu_P$", ha="center", va="top", fontsize=6.5, color=COMP)
    ax.text(xQ2, 0.345, r"$\mu_Q$", ha="center", va="top", fontsize=6.5, color=COMP)
    _link(ax, xP2, xQ2, "unchanged")
    ax.text((xP2 + xQ2) / 2, 0.215, r"mean signatures ($\lambda=0$)",
            ha="center", va="top", fontsize=6.5, color="0.25")

    ax.text(0.5, 0.055,
            r"the population score $s_{\mathrm{dist}}(P_d,Q)$ becomes the mean-to-mean "
            r"score $s_{\mathrm{mean}}(\mu_P,\mu_Q)$",
            ha="center", va="center", fontsize=6, color="0.3")

    ax.set_title(r"The mean signature is the $\lambda\to0$ limit", loc="left")


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(3.45, 1.65))
    draw_2a(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "2a.png"), dpi=200, bbox_inches="tight")
    print("wrote 2a.png")
