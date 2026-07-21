"""DART Figure 6 panel 6a: predict-then-rank schematic
Source data: (schematic)
Run standalone: python fig6a.py
"""
import os, numpy as np, pandas as pd, matplotlib as mpl, matplotlib.pyplot as plt
from scipy import stats
FOCAL, COMP, GREY = "#5185C0", "#E99D4E", "#7A7A7A"
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

def draw_6a(ax):
    ax.axis('off'); ax.set_xlim(0,1); ax.set_ylim(0,1)
    def box(x,y,w,h,txt,col,fc):
        ax.add_patch(mpl.patches.FancyBboxPatch((x-w/2,y-h/2),w,h,
            boxstyle='round,pad=0.006',fc=fc,ec=col,lw=1.0))
        ax.text(x,y,txt,ha='center',va='center',fontsize=6.0,color=col)
    box(0.15,0.72,0.24,0.15,'held-out\nquery',GREY,'white')
    box(0.15,0.28,0.24,0.15,'predictor',COMP,'#fbeceb')
    box(0.50,0.28,0.24,0.15,'predicted\npopulation',COMP,'#fbeceb')
    box(0.50,0.72,0.24,0.15,'observed\npopulation',FOCAL,'#eaf1f8')
    box(0.83,0.50,0.20,0.24,'DART /\nmean\nrank',GREY,'white')
    for (x0,y0,x1,y1,cc) in [(0.27,0.72,0.38,0.72,FOCAL),(0.27,0.28,0.38,0.28,COMP),
                             (0.62,0.72,0.74,0.58,FOCAL),(0.62,0.28,0.74,0.42,COMP),
                             (0.15,0.645,0.15,0.355,GREY)]:
        ax.annotate('',xy=(x1,y1),xytext=(x0,y0),arrowprops=dict(arrowstyle='->',lw=0.9,color=cc))
    ax.text(0.50,0.90,'divergent response',ha='center',fontsize=5.8,color=FOCAL)
    ax.text(0.50,0.09,'structure kept, divergence lost',ha='center',fontsize=5.8,color=COMP)


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(3.4,3.0))
    draw_6a(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "6a.png"), dpi=200, bbox_inches="tight")
    print("wrote 6a.png")
