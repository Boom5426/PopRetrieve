"""DART Figure 2 panel 2f: metric-family hierarchy (schematic)
Source data: (schematic)
Run standalone: python fig2f.py  (writes 2f.png)
"""
import os, numpy as np, pandas as pd, matplotlib.pyplot as plt
import sys; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FOCAL, COMP, GREY = "#5185C0", "#E99D4E", "#7A7A7A"
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

def draw_2f(ax):
    """Metric-family hierarchy: mean/energy/MMD/SW/coverage/worst on one axis."""
    ax.axis('off'); ax.set_xlim(0,1); ax.set_ylim(0,1)
    def box(x,y,txt,col='0.25',fc='white'):
        ax.text(x,y,txt,ha='center',va='center',fontsize=6.5,color=col,
                bbox=dict(boxstyle='round,pad=0.28',fc=fc,ec=col,lw=0.8))
    box(0.5,0.90,'distributional retrieval',col=FOCAL,fc='#eaf1f8')
    for x,t in [(0.20,'energy'),(0.40,'MMD'),(0.60,'sliced-W'),(0.80,'coverage')]:
        box(x,0.62,t,col=FOCAL)
        ax.annotate('',xy=(x,0.70),xytext=(0.5,0.83),arrowprops=dict(arrowstyle='-',lw=0.6,color='0.6'))
    box(0.80,0.34,'worst-case',col='0.35')
    ax.annotate('',xy=(0.80,0.42),xytext=(0.80,0.54),arrowprops=dict(arrowstyle='->',lw=0.7,color='0.5'))
    ax.text(0.905,0.48,r'$\beta\!\to\!\infty$',fontsize=5.5,color='0.4',va='center')
    box(0.5,0.10,'mean retrieval (CMap)',col=COMP,fc='#fbeceb')
    for x,tag in [(0.20,'$\\lambda\\!\\to\\!0$'),(0.40,'$\\lambda\\!\\to\\!0$'),(0.60,'$\\lambda\\!\\to\\!0$'),(0.80,'$\\beta\\!\\to\\!0$')]:
        ax.annotate('',xy=(0.5,0.17),xytext=(x,0.54),arrowprops=dict(arrowstyle='->',lw=0.6,color=COMP,alpha=0.5))
    ax.text(0.5,0.015,'all collapse to the mean',ha='center',fontsize=6,color=COMP)
    ax.set_title("The metric family and its limits", loc='left')


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(3.4,3.0))
    draw_2f(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "2f.png"), dpi=200, bbox_inches="tight")
    print("wrote 2f.png")
