"""PopRetrieve Figure 2 panel 2e: the beta-interpolation spectrum, plus the K = 1 identity.

Source data:
  results/exp06_theory_limits/beta_interpolation.csv  (controlled benchmark; D_beta rises
      monotonically from 0.7125 at beta -> 0, the mean-aggregated value, to 1.300 at
      beta -> inf, the worst-case value; mirrored in figures/source_data/fig2e_beta_spectrum.csv)
  results/exp06_theory_limits/degenerate_limit_synthetic.csv rows prop2_K1 (global energy equals
      the single-partition coverage aggregate exactly, 8.229259 at every beta).

Note on provenance: the K = 1 identity annotation is the SYNTHETIC check. The manuscript quotes
the real-data instance of the same identity (Panobinostat, 0.1099 vs 0.1099, difference 0), which
lives in degenerate_limit_real.csv. The panel therefore labels its number as synthetic so the two
cannot be confused.

Run standalone: python fig2e.py  (writes 2e.png)
"""
import os, numpy as np, pandas as pd, matplotlib.pyplot as plt
import sys; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FOCAL, COMP, GREY = "#5185C0", "#E99D4E", "#7A7A7A"
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def draw_2e(ax):
    """Coverage temperature beta interpolates mean aggregation to worst case."""
    b = (pd.read_csv(f"{REPO}/results/exp06_theory_limits/beta_interpolation.csv")
         .sort_values("beta"))
    mlo, mhi = float(b["mean"].iloc[0]), float(b["max"].iloc[0])

    k1 = pd.read_csv(f"{REPO}/results/exp06_theory_limits/degenerate_limit_synthetic.csv")
    k1 = k1[k1["prop"] == "prop2_K1"]
    e_glob = float(k1["global_energy"].iloc[0])
    e_cov = float(k1["coverage_K1"].iloc[0])

    ax.axhline(mlo, ls="--", lw=0.9, color=COMP, zorder=1)
    ax.axhline(mhi, ls="--", lw=0.9, color="0.45", zorder=1)
    xb = np.clip(b["beta"], 1e-3, 1e3)
    ax.plot(xb, b["D_beta"], "-o", color=FOCAL, ms=3.2, lw=1.4, zorder=3)

    ax.text(1.1e-3, mhi + 0.012, f"worst case, $\\beta\\to\\infty$   {mhi:.3f}",
            ha="left", va="bottom", fontsize=6, color="0.35")
    ax.text(1.1e-3, mlo - 0.032, f"mean aggregation, $\\beta\\to0$   {mlo:.4f}",
            ha="left", va="top", fontsize=6, color=COMP)
    ax.text(0.985, 0.20,
            f"energy $=$ coverage$_{{K=1}}$ exactly\n"
            f"(synthetic check, {e_glob:.3f} vs {e_cov:.3f})",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=6, color=FOCAL)

    ax.set_xscale("log")
    ax.set_xlim(8e-4, 2.2e3)
    ax.set_xticks([1e-3, 1e-1, 1e1, 1e3])
    ax.set_ylim(mlo - 0.105, mhi + 0.062)
    ax.set_yticks([0.7, 0.9, 1.1, 1.3])
    ax.set_xlabel(r"coverage temperature $\beta$")
    ax.set_ylabel(r"aggregate distance $D_\beta$")
    ax.set_title(r"$\beta$ interpolates mean aggregation to worst case", loc="left")


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(3.45, 1.9))
    draw_2e(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "2e.png"), dpi=200, bbox_inches="tight")
    print("wrote 2e.png")
