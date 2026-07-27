"""EvalShift Extended Data Fig. 6 panel a: HIR-Bench generative model
Source data: (schematic)
Run standalone: python fig5a.py
"""
import os, numpy as np, pandas as pd, matplotlib as mpl, matplotlib.pyplot as plt
FOCAL, COMP, GREY = "#5185C0", "#E99D4E", "#7A7A7A"
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
H = os.path.join(REPO, "results", "exp11_hir_benchmark")
S = os.path.join(REPO, "results", "exp11_synthetic_phase_diagram")

def draw_5a(ax):
    """HIR-Bench generative model schematic."""
    ax.axis('off'); ax.set_xlim(0,1); ax.set_ylim(0,1)
    def box(x,y,w,h,txt,col,fc,fs=6.0):
        ax.add_patch(mpl.patches.FancyBboxPatch((x-w/2,y-h/2),w,h,boxstyle='round,pad=0.006',fc=fc,ec=col,lw=1.0))
        ax.text(x,y,txt,ha='center',va='center',fontsize=fs,color=col)
    box(0.5,0.90,0.5,0.12,'query response = majority + minority',GREY,'white',6.0)
    box(0.24,0.66,0.30,0.14,'majority\nsubpop (1$-\\alpha$)',FOCAL,'#eaf1f8')
    box(0.76,0.66,0.30,0.14,'minority\nsubpop ($\\alpha$)',COMP,'#fbeceb')
    box(0.24,0.40,0.30,0.13,'welfare A\n(majority)',FOCAL,'#eaf1f8')
    box(0.76,0.40,0.30,0.13,'welfare B\n(minority)',COMP,'#fbeceb')
    box(0.5,0.15,0.62,0.13,r'flip when $\alpha > \alpha^* = B/(A{+}B)$',GREY,'white',6.4)
    for x0,y0,x1,y1,cc in [(0.24,0.83,0.24,0.73,FOCAL),(0.76,0.83,0.76,0.73,COMP),
                           (0.24,0.59,0.24,0.47,FOCAL),(0.76,0.59,0.76,0.47,COMP),
                           (0.24,0.33,0.42,0.21,GREY),(0.76,0.33,0.58,0.21,GREY)]:
        ax.annotate('',xy=(x1,y1),xytext=(x0,y0),arrowprops=dict(arrowstyle='->',lw=0.8,color=cc))
    ax.set_title("HIR-Bench generative model", loc='left')


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(3.5,3.0))
    draw_5a(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "5a.png"), dpi=200, bbox_inches="tight")
    print("wrote 5a.png")
