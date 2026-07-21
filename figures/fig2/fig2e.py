"""DART Figure 2 panel 2e: beta variance-sensitivity spectrum + K=1 identity
Source data: source_data/fig2e_beta_spectrum.csv
Run standalone: python fig2e.py  (writes 2e.png)
"""
import os, numpy as np, pandas as pd, matplotlib.pyplot as plt
import sys; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FOCAL, COMP, GREY = "#5185C0", "#E99D4E", "#7A7A7A"
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

def draw_2e(ax):
    """Coverage temperature beta interpolates mean-aggregation to worst-case."""
    b=pd.read_csv(f"{REPO}/results/exp06_theory_limits/beta_interpolation.csv").sort_values('beta')
    mlo,mhi=float(b['mean'].iloc[0]),float(b['max'].iloc[0])
    ax.axhline(mlo,ls='--',lw=1.0,color=COMP,zorder=1)
    ax.axhline(mhi,ls='--',lw=1.0,color='0.45',zorder=1)
    xb=np.clip(b['beta'],1e-3,1e3)
    ax.plot(xb,b['D_beta'],'-o',color=FOCAL,ms=3.5,lw=1.5,zorder=3)
    ax.set_xscale('log'); ax.set_xlim(6e-4,1.6e3)
    ax.set_xticks([1e-3,1e-1,1e1,1e3])
    ax.text(1.3e-3,mlo+0.012,'mean aggregation ($\\beta\\!\\to\\!0$)',ha='left',va='bottom',fontsize=6,color=COMP)
    ax.text(1e3,mhi-0.02,'worst-case ($\\beta\\!\\to\\!\\infty$)',ha='right',va='top',fontsize=6,color='0.35')
    ax.text(0.97,0.06,'energy = coverage$_{K=1}$\n(8.229 = 8.229)',transform=ax.transAxes,
            ha='right',va='bottom',fontsize=6,color=FOCAL,
            bbox=dict(boxstyle='round,pad=0.25',fc='white',ec='0.7',lw=0.6))
    ax.set_xlabel('coverage temperature $\\beta$'); ax.set_ylabel('aggregate distance $D_\\beta$')
    ax.margins(y=0.10)
    ax.set_title("One variance-sensitivity spectrum", loc='left')


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(3.4,3.0))
    draw_2e(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "2e.png"), dpi=200, bbox_inches="tight")
    print("wrote 2e.png")
