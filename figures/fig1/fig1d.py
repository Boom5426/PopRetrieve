"""DART Figure 1 panel 1d: evaluation coupling schematic
Synthetic/schematic (no external data).
Run standalone: python fig1d.py
"""
import os, numpy as np, pandas as pd, matplotlib as mpl, matplotlib.pyplot as plt
FOCAL, COMP, GREY = "#5185C0", "#E99D4E", "#7A7A7A"

def draw_1d(ax):
    """Evaluation coupling: objective / metric / outcome, coupled vs independent."""
    ax.axis('off'); ax.set_xlim(0,1); ax.set_ylim(0,1)
    def node(x,y,txt,col,fc):
        ax.add_patch(mpl.patches.Circle((x,y),0.085,fc=fc,ec=col,lw=1.2))
        ax.text(x,y,txt,ha='center',va='center',fontsize=5.6,color=col)
    node(0.20,0.72,'retrieval\nobjective',FOCAL,'#eaf1f8')
    node(0.20,0.30,'evaluation\nmetric',FOCAL,'#eaf1f8')
    node(0.72,0.72,'energy\nregret',COMP,'#fbeceb')
    node(0.72,0.30,'MoA /\nviability',GREY,'white')
    ax.annotate('',xy=(0.20,0.39),xytext=(0.20,0.63),arrowprops=dict(arrowstyle='->',lw=1.0,color=FOCAL))
    ax.annotate('',xy=(0.635,0.68),xytext=(0.285,0.34),arrowprops=dict(arrowstyle='->',lw=1.2,color=COMP))
    ax.text(0.47,0.58,'coupled\n(Class A)',fontsize=5.8,color=COMP,ha='center')
    ax.annotate('',xy=(0.635,0.32),xytext=(0.285,0.30),arrowprops=dict(arrowstyle='->',lw=1.2,color=GREY,ls='--'))
    ax.text(0.47,0.20,'independent\n(Class B/C)',fontsize=5.8,color=GREY,ha='center')
    ax.set_title("When is the evaluator independent?", loc='left')


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(3.4,3.0))
    draw_1d(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "1d.png"), dpi=200, bbox_inches="tight")
    print("wrote 1d.png")
