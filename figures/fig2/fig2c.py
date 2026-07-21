"""DART Figure 2 panel 2c: energy collapses to mean-distance floor
Source data: source_data/fig2c_energy_collapse.csv
Run standalone: python fig2c.py  (writes 2c.png)
"""
import os, numpy as np, pandas as pd, matplotlib.pyplot as plt
import sys; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FOCAL, COMP, GREY = "#5185C0", "#E99D4E", "#7A7A7A"
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

def draw_2c(ax):
    """Energy score collapses to the mean-distance floor as spread -> 0."""
    d=pd.read_csv(f"{REPO}/results/exp06_theory_limits/degenerate_limit_synthetic.csv")
    sp=d[d['prop']=='prop1_spread'].dropna(subset=['t_spread']).sort_values('t_spread')
    floor=float(sp['two_dmu'].iloc[0])
    ax.axhline(floor,ls='--',lw=1.1,color=COMP,zorder=1)
    ax.plot(sp['t_spread'],sp['energy'],'-o',color=FOCAL,ms=4,lw=1.6,zorder=3)
    ax.text(0.97,floor-3.5,'mean-distance floor',ha='right',va='top',fontsize=6,color=COMP)
    ax.annotate(f'{sp["energy"].iloc[0]:.1f}',xy=(0,sp['energy'].iloc[0]),
                xytext=(0.08,sp['energy'].iloc[0]-9),fontsize=6,color=FOCAL,
                arrowprops=dict(arrowstyle='->',lw=0.7,color=FOCAL))
    ax.set_xlabel('residual spread $\\lambda$'); ax.set_ylabel('energy distance')
    ax.set_xlim(-0.04,1.04); ax.margins(y=0.08)
    ax.set_title("Energy retrieval collapses to mean at $\\lambda\\!\\to\\!0$", loc='left')


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(3.4,3.0))
    draw_2c(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "2c.png"), dpi=200, bbox_inches="tight")
    print("wrote 2c.png")
