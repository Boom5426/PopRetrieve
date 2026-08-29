"""PopRetrieve Extended Data Fig. 6 panel d: information condition regret
Source data: results/exp11_hir_benchmark/method_dominance.csv
Run standalone: python ed6_panel_d.py
"""
import os, numpy as np, pandas as pd, matplotlib as mpl, matplotlib.pyplot as plt
# Palette comes from the house-style module; do NOT re-declare the hex values here. Every
# panel file used to carry its own copy, which made figstyle's "one edit here recolours the
# whole deck" untrue: a recolour meant editing 43 files and missing one was silent.
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
from figstyle import FOCAL_SOFT, COMP_SOFT, GREY, INK  # noqa: E402
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
H = os.path.join(REPO, "results", "exp11_hir_benchmark")
S = os.path.join(REPO, "results", "exp11_synthetic_phase_diagram")

def draw_ed6c(ax):
    """Information condition: decision regret balloons under predicted_mean (structure destroyed)."""
    md=pd.read_csv(f"{H}/method_dominance.csv")
    reg=md[md.metric=='decision_regret']
    # observed vs predicted_mean, for worst welfare (the minority-sensitive one)
    rows=[]
    for wt in ['mean','worst']:
        for ic in ['observed','predicted_mean']:
            v=reg[(reg.welfare_type==wt)&(reg.information_condition==ic)]['best_value']
            if len(v): rows.append((f'{wt}\nwelfare',ic,v.iloc[0]))
    dfp=pd.DataFrame(rows,columns=['welfare','ic','regret'])
    piv=dfp.pivot(index='welfare',columns='ic',values='regret')
    x=np.arange(len(piv)); w=0.36
    ax.bar(x-w/2,piv['observed'],w,color=FOCAL_SOFT,alpha=0.8,label='observed')
    ax.bar(x+w/2,piv['predicted_mean'],w,color=COMP_SOFT,alpha=0.8,label='predicted-mean')
    for xi,(o,p) in enumerate(zip(piv['observed'],piv['predicted_mean'])):
        ax.text(xi-w/2,o+0.02,f'{o:.2f}',ha='center',fontsize=5.6,color=INK)
        ax.text(xi+w/2,p+0.02,f'{p:.2f}',ha='center',fontsize=5.6,color=INK)
    ax.set_xticks(x); ax.set_xticklabels(piv.index,fontsize=6)
    ax.set_ylabel('best decision regret'); ax.set_ylim(0,1.1)
    ax.legend(fontsize=5.6,loc='upper left',frameon=False)
    ax.set_title("Losing structure inflates regret", loc='left')


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(3.5,3.0))
    draw_ed6c(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "ed6c.png"), dpi=200, bbox_inches="tight")
    print("wrote ed6c.png")
