"""EvalShift Figure 2 panel 2c: energy distance meets the mean-distance floor as lambda -> 0.

Source data: results/exp06_theory_limits/degenerate_limit_synthetic.csv (rows prop1_spread);
mirrored for release in figures/source_data/fig2c_energy_collapse.csv. The dashed floor is the
two_dmu column (mean-to-mean distance), which is constant by construction.

Run standalone: python fig2c.py  (writes 2c.png)
"""
import os, numpy as np, pandas as pd, matplotlib.pyplot as plt
import sys; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FOCAL, COMP, GREY = "#5185C0", "#E99D4E", "#7A7A7A"
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def draw_2c(ax):
    """Energy score converges to the mean-to-mean distance floor as the residual vanishes."""
    d = pd.read_csv(f"{REPO}/results/exp06_theory_limits/degenerate_limit_synthetic.csv")
    sp = (d[d["prop"] == "prop1_spread"].dropna(subset=["t_spread"])
          .sort_values("t_spread"))
    floor = float(sp["two_dmu"].iloc[0])
    lam = sp["t_spread"].to_numpy()
    energy = sp["energy"].to_numpy()

    ax.axhline(floor, ls="--", lw=1.0, color=COMP, zorder=1)
    ax.plot(lam, energy, "-", color=FOCAL, lw=1.5, zorder=3)
    ax.plot(lam[1:], energy[1:], "o", color=FOCAL, ms=3.8, zorder=3)
    # the lambda = 0 endpoint carries the claim, so it is drawn as the emphasised point
    ax.plot([lam[0]], [energy[0]], "o", color=FOCAL, ms=6.0, mec="white", mew=0.8, zorder=5)

    ax.text(1.02, floor + 1.6, f"mean-distance floor  {floor:.2f}", ha="right", va="bottom",
            fontsize=6, color=COMP)
    # annotation parked in the empty upper-right wedge so its leader never crosses the curve
    ax.annotate(f"$\\lambda=0$:  {energy[0]:.2f}\n(the floor, reached)",
                xy=(lam[0], energy[0]), xytext=(0.33, energy[0] - 7.5),
                fontsize=6, color=FOCAL, ha="left", va="center",
                arrowprops=dict(arrowstyle="-", lw=0.6, color=FOCAL,
                                shrinkA=2, shrinkB=4))

    ax.set_xlabel(r"residual scale $\lambda$")
    ax.set_ylabel("energy distance")
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(28, 108)
    ax.set_yticks([40, 60, 80, 100])
    ax.set_title(r"Energy distance meets the mean-distance floor", loc="left")


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(3.45, 1.9))
    draw_2c(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "2c.png"), dpi=200, bbox_inches="tight")
    print("wrote 2c.png")
