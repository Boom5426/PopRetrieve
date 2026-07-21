"""DART Figure 4 panel 4d: recommended vs non-recommended
Source data: source_data/fig4d_recommendation_vs_outcome.csv
Run standalone: python fig4d.py
"""
import os, numpy as np, pandas as pd, matplotlib as mpl, matplotlib.pyplot as plt
FOCAL, COMP, GREY = "#5185C0", "#E99D4E", "#7A7A7A"
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
key=["split_type","cell_line","heldout_drug","observed_library_fraction","seed"]

def draw_4d(ax):
    """Recommended vs non-recommended full distributions (both ~+0.12)."""
    rvo=pd.read_csv(f"{REPO}/results/exp12_partial_observed_retrieval/recommendation_vs_outcome.csv")
    cw=rvo[rvo.dart_method=='DART_coverage_worst']
    modes=[('DART_recommended','recommended',FOCAL),('mean_or_no_call','non-recommended',GREY)]
    xs=[];meds=[];ns=[];cols=[];labs=[]
    for i,(m,lab,col) in enumerate(modes):
        row=cw[cw.recommendation_mode==m]
        if len(row):
            xs.append(i);meds.append(row['median_regret_reduction'].iloc[0]);ns.append(int(row['n_queries'].iloc[0]));cols.append(col);labs.append(lab)
    ax.bar(xs,meds,width=0.55,color=cols,alpha=0.8)
    for x,m,n in zip(xs,meds,ns): ax.text(x,m+0.003,f'+{m:.3f}\nn={n}',ha='center',fontsize=6)
    ax.set_xticks(xs); ax.set_xticklabels(labs,fontsize=6.5)
    ax.set_ylabel('median regret reduction'); ax.set_ylim(0,0.16); ax.axhline(0,color='k',lw=0.8)
    for sp in ['right','top']: ax.spines[sp].set_visible(False)
    ax.set_title("Non-recommended queries gain as much", loc='left')


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(3.5,3.0))
    draw_4d(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "4d.png"), dpi=200, bbox_inches="tight")
    print("wrote 4d.png")
