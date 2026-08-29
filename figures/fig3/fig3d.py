"""PopRetrieve Figure 3 panel 3d: recommended vs non-recommended
Source data: results/exp12_partial_observed_retrieval/recommendation_vs_outcome.csv
             (source_data/fig3d_recommendation_vs_outcome.csv is a mirror of it, not read here)
Run standalone: python fig3d.py
"""
import os, numpy as np, pandas as pd, matplotlib as mpl, matplotlib.pyplot as plt
# Palette comes from the house-style module; do NOT re-declare the hex values here. Every
# panel file used to carry its own copy, which made figstyle's "one edit here recolours the
# whole deck" untrue: a recolour meant editing 43 files and missing one was silent.
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
from figstyle import FOCAL_SOFT, COMP_SOFT, GREY, INK, META  # noqa: E402
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
key=["split_type","cell_line","heldout_drug","observed_library_fraction","seed"]

def draw_3d(ax):
    """Recommended vs non-recommended full distributions (both ~+0.12)."""
    rvo=pd.read_csv(f"{REPO}/results/exp12_partial_observed_retrieval/recommendation_vs_outcome.csv")
    cw=rvo[rvo.dart_method=='DART_coverage_worst']
    modes=[('DART_recommended','recommended',FOCAL_SOFT),('mean_or_no_call','not\nrecommended',GREY)]
    xs=[];meds=[];ns=[];cols=[];labs=[]
    for i,(m,lab,col) in enumerate(modes):
        row=cw[cw.recommendation_mode==m]
        if len(row):
            xs.append(i);meds.append(row['median_regret_reduction'].iloc[0]);ns.append(int(row['n_queries'].iloc[0]));cols.append(col);labs.append(lab)
    ax.bar(xs,meds,width=0.52,color=cols,alpha=0.85)
    for x,m,n in zip(xs,meds,ns):
        ax.text(x,m+0.004,f'$+${m:.3f}',ha='center',va='bottom',fontsize=6,color=INK)
        # n below the tick label in META grey, not stacked on top of the value: secondary
        # information is secondary everywhere in this deck.
        # Offset measured against the TALLER tick label ("not\nrecommended", two lines); a
        # single offset for both keeps the two n on one line, and the x label is padded to clear
        # them rather than being allowed to collide.
        ax.text(x,-0.285,f'n = {n}',transform=ax.get_xaxis_transform(),ha='center',va='top',
                fontsize=5.6,color=META)
    ax.set_xticks(xs); ax.set_xticklabels(labs,fontsize=6.2)
    # Two lines, not three. The criterion is stated in the caption; the third line put this
    # label's outer edge 0.03 in from panel c's axes, the tightest gap in the row.
    ax.set_ylabel('median regret\nreduction', fontsize=6.2)
    ax.set_ylim(0,0.185); ax.set_xlim(-0.45,1.45)
    ax.set_yticks([0,0.05,0.10,0.15])
    ax.tick_params(labelsize=5.8)
    ax.axhline(0,color=INK,lw=0.8)
    ax.set_xlabel('pre-specified diagnostic',fontsize=6.2,labelpad=11.0)
    for sp in ['right','top']: ax.spines[sp].set_visible(False)
    ax.set_title("Non-recommended queries gain as much", loc='left')


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(3.5,3.0))
    draw_3d(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "3d.png"), dpi=200, bbox_inches="tight")
    print("wrote 3d.png")
