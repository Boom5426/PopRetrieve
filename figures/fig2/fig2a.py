"""DART Figure 2 panel 2a: mean is the zero-variance limit (schematic)
Source data: (schematic, seed=0)
Run standalone: python fig2a.py  (writes 2a.png)
"""
import os, numpy as np, pandas as pd, matplotlib.pyplot as plt
import sys; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FOCAL, COMP, GREY = "#5185C0", "#E99D4E", "#7A7A7A"
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

def draw_2a(ax):
    """Unified model X = mu + lambda*eps: mean-collapsed to observed."""
    ax.axis('off'); ax.set_xlim(0,1); ax.set_ylim(0,1)
    ax.text(0.5,0.90, r"$X=\mu+\lambda\,\epsilon,\ \ \mathbb{E}[\epsilon]=0$",
            ha='center', va='center', fontsize=8)
    rng=np.random.RandomState(0)
    centers=[0.20,0.50,0.80]; stds=[0.0,0.045,0.11]; lams=['0','0.5','1']
    for cx,sd,lam in zip(centers,stds,lams):
        pts=rng.normal([cx,0.50],[sd,sd*1.6],size=(60,2)) if sd>0 else np.array([[cx,0.50]])
        col = COMP if sd==0 else FOCAL
        ax.scatter(pts[:,0],pts[:,1],s=5,color=col,alpha=0.45,edgecolors='none',zorder=1)
        ax.scatter([cx],[0.50],marker='x',s=34,color='k',lw=1.4,zorder=3)
        ax.text(cx,0.30,rf"$\lambda={lam}$",ha='center',va='center',fontsize=6)
    ax.annotate('',xy=(0.86,0.16),xytext=(0.14,0.16),
                arrowprops=dict(arrowstyle='->',lw=1.0,color='0.4'))
    ax.text(0.14,0.085,'mean-collapsed',ha='left',va='center',fontsize=6,color='0.35')
    ax.text(0.86,0.085,'observed',ha='right',va='center',fontsize=6,color='0.35')
    ax.text(0.5,0.665, r"$s_{\mathrm{dist}}\!\to\!s_{\mathrm{mean}}$ as $\lambda\!\to\!0$",
            ha='center',va='center',fontsize=6,color='0.2')
    ax.set_title("Mean is the zero-variance limit of one model", loc='left')


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(3.4,3.0))
    draw_2a(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "2a.png"), dpi=200, bbox_inches="tight")
    print("wrote 2a.png")
