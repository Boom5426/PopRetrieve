"""DART Figure 2 panel 2b: variance scaling with mean fixed (schematic)
Source data: (schematic, seed=1)
Run standalone: python fig2b.py  (writes 2b.png)
"""
import os, numpy as np, pandas as pd, matplotlib.pyplot as plt
import sys; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FOCAL, COMP, GREY = "#5185C0", "#E99D4E", "#7A7A7A"
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

def draw_2b(ax):
    """Variance-scaling: same mean, residual variance scaled lambda in {0,.25,.5,1}."""
    ax.axis('off'); ax.set_xlim(0,1); ax.set_ylim(0,1)
    rng=np.random.RandomState(1)
    centers=[0.14,0.38,0.62,0.86]; lams=[0.0,0.25,0.5,1.0]; base=0.16
    for cx,lam in zip(centers,lams):
        sd=lam*base
        if sd>0:
            pts=rng.normal([cx,0.55],[sd*0.7,sd],size=(80,2))
            ax.scatter(pts[:,0],pts[:,1],s=4,color=FOCAL,alpha=0.4,edgecolors='none',zorder=1)
        ax.scatter([cx],[0.55],marker='x',s=30,color=COMP,lw=1.4,zorder=3)
        ax.text(cx,0.20,rf"$\lambda={lam:g}$",ha='center',va='center',fontsize=6)
    ax.text(0.5,0.045,'mean fixed (orange x); only heterogeneity changes',
            ha='center',va='center',fontsize=6,color='0.35')
    ax.set_title("Scaling variance, not changing the data", loc='left')


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(3.4,3.0))
    draw_2b(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "2b.png"), dpi=200, bbox_inches="tight")
    print("wrote 2b.png")
