"""DART Figure 1 panel 1b: inverse-retrieval task schematic
Synthetic/schematic (no external data).
Run standalone: python fig1b.py
"""
import os, numpy as np, pandas as pd, matplotlib as mpl, matplotlib.pyplot as plt
FOCAL, COMP, GREY = "#5185C0", "#E99D4E", "#7A7A7A"

def draw_1b(ax):
    """Inverse-retrieval task schematic: Q -> {P_d} -> score -> ranking."""
    ax.axis('off'); ax.set_xlim(0,1); ax.set_ylim(0,1)
    def box(x,y,w,h,txt,col,fc,fs=6.2):
        ax.add_patch(mpl.patches.FancyBboxPatch((x-w/2,y-h/2),w,h,boxstyle='round,pad=0.006',fc=fc,ec=col,lw=1.0))
        ax.text(x,y,txt,ha='center',va='center',fontsize=fs,color=col)
    box(0.15,0.5,0.22,0.20,'query\nphenotype\nQ',GREY,'white')
    box(0.45,0.72,0.26,0.16,'candidate\npopulations\n{$P_d$}',GREY,'white',6.0)
    box(0.45,0.28,0.26,0.14,'mean\nsignature',COMP,'#fbeceb',6.0)
    box(0.45,0.50,0.26,0.10,'distribution\n$s(P_d,Q)$',FOCAL,'#eaf1f8',6.0)
    box(0.82,0.5,0.20,0.30,'drug\nranking',GREY,'white')
    ax.annotate('',xy=(0.31,0.55),xytext=(0.26,0.52),arrowprops=dict(arrowstyle='->',lw=0.9,color=GREY))
    for yy,cc in [(0.72,GREY),(0.50,FOCAL),(0.28,COMP)]:
        ax.annotate('',xy=(0.72,0.5),xytext=(0.58,yy),arrowprops=dict(arrowstyle='->',lw=0.9,color=cc))
    ax.text(0.45,0.90,'inverse retrieval',ha='center',fontsize=6.4,color='k')
    ax.set_title("The drug-retrieval task", loc='left')


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(3.4,3.0))
    draw_1b(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "1b.png"), dpi=200, bbox_inches="tight")
    print("wrote 1b.png")
