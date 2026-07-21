"""DART Figure 3 panel 3d: recommended vs non-recommended
Source data: results exp12 recommendation_vs_outcome.csv
Run standalone: python fig3d.py
"""
import os, numpy as np, pandas as pd, matplotlib as mpl, matplotlib.pyplot as plt
FOCAL, COMP, GREY = "#5185C0", "#E99D4E", "#7A7A7A"
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

def draw_3d(ax):
    """Recommended vs non-recommended regret reduction (both positive; gate not concentrating)."""
    rvo=pd.read_csv(f"{REPO}/results/exp12_partial_observed_retrieval/recommendation_vs_outcome.csv")
    cw=rvo[rvo.dart_method=='DART_coverage_worst']
    modes={'DART_recommended':('recommended',FOCAL),'mean_or_no_call':('non-recommended',GREY)}
    xs=[];labels=[];meds=[];ns=[];cols=[]
    for i,(mode,(lab,col)) in enumerate(modes.items()):
        row=cw[cw.recommendation_mode==mode]
        if len(row):
            xs.append(i); labels.append(lab); meds.append(row['median_regret_reduction'].iloc[0])
            ns.append(int(row['n_queries'].iloc[0])); cols.append(col)
    ax.bar(xs,meds,width=0.55,color=cols,alpha=0.8)
    for x,m,n in zip(xs,meds,ns):
        ax.text(x,m+0.003,f'+{m:.3f}\nn={n}',ha='center',va='bottom',fontsize=6)
    ax.set_xticks(xs); ax.set_xticklabels(labels,fontsize=6.5)
    ax.set_ylabel('median regret reduction'); ax.set_ylim(0,0.16)
    ax.axhline(0,color='k',lw=0.8)
    for sp in ['right','top']: ax.spines[sp].set_visible(False)
    ax.set_title("Gate does not concentrate the gain", loc='left')


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(3.6,3.0))
    draw_3d(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "3d.png"), dpi=200, bbox_inches="tight")
    print("wrote 3d.png")
