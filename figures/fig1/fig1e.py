"""DART Figure 1 panel 1e: metric evidence ladder schematic
Synthetic/schematic (no external data).
Run standalone: python fig1e.py
"""
import os, numpy as np, pandas as pd, matplotlib as mpl, matplotlib.pyplot as plt
FOCAL, COMP, GREY = "#5185C0", "#E99D4E", "#7A7A7A"

def draw_1e(ax):
    ax.axis('off'); ax.set_xlim(0,1); ax.set_ylim(0,1)
    tiers=[('Class C','externally grounded','viability, survival','none',COMP,0.20),
           ('Class B','task-proximal','MoA-nDCG, coverage','partial',GREY,0.50),
           ('Class A','objective-aligned','energy regret','full',FOCAL,0.80)]
    for name,desc,ex,cov,col,y in tiers:
        ax.add_patch(mpl.patches.FancyBboxPatch((0.10,y-0.12),0.86,0.215,boxstyle='round,pad=0.006',fc=col,ec=col,alpha=0.14,lw=1.0))
        ax.text(0.13,y+0.045,name,fontsize=6.6,color=col,fontweight='bold',va='center')
        ax.text(0.13,y-0.035,desc,fontsize=5.2,color='k',va='center',style='italic')
        ax.text(0.13,y-0.093,ex,fontsize=5.0,color='0.35',va='center')
        cc={'full':FOCAL,'partial':GREY,'none':COMP}[cov]
        ax.text(0.92,y,f'this study\n{cov}',fontsize=5.6,color=cc,ha='right',va='center',fontweight='bold')
    ax.annotate('',xy=(0.06,0.87),xytext=(0.06,0.11),arrowprops=dict(arrowstyle='->',lw=1.3,color='k'))
    ax.text(0.038,0.5,'evidence strength',rotation=90,fontsize=5.6,va='center')
    ax.set_xlim(0,1); ax.set_ylim(0.02,0.98)


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(3.4,3.0))
    draw_1e(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "1e.png"), dpi=200, bbox_inches="tight")
    print("wrote 1e.png")
