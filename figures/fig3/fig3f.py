"""PopRetrieve Figure 3 panel 3f: recommendation cannot sort divergence
Source data: results/exp16_gate_diagnosis/_merged_query_divergence.csv
             (source_data/fig3ef_gate_divergence.csv is a hand-built column view of it, not read here)
Run standalone: python fig3f.py
"""
import os, numpy as np, pandas as pd, matplotlib as mpl, matplotlib.pyplot as plt
from scipy import stats
# Palette comes from the house-style module; do NOT re-declare the hex values here. Every
# panel file used to carry its own copy, which made figstyle's "one edit here recolours the
# whole deck" untrue: a recolour meant editing 43 files and missing one was silent.
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
from figstyle import FOCAL_SOFT, COMP_SOFT, GREY, INK, META  # noqa: E402
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
key=["split_type","cell_line","heldout_drug","observed_library_fraction","seed"]

def draw_3f(ax):
    """Binary recommendation does not separate divergence (Mann-Whitney p=0.09)."""
    mg=pd.read_csv(f"{REPO}/results/exp16_gate_diagnosis/_merged_query_divergence.csv")
    u=mg.dropna(subset=['true_divergence']).drop_duplicates(subset=key)
    rec=u[u.recommendation_mode=='DART_recommended']['true_divergence']
    nonrec=u[u.recommendation_mode!='DART_recommended']['true_divergence']
    bp=ax.boxplot([rec,nonrec],positions=[0,1],widths=0.5,patch_artist=True,showfliers=False)
    for patch,col in zip(bp['boxes'],[FOCAL_SOFT,GREY]):
        patch.set_facecolor(col); patch.set_alpha(0.5); patch.set_edgecolor(INK)
    for part in ['whiskers','caps']:
        for art in bp[part]: art.set_color(INK)
    for med in bp['medians']: med.set_color(INK); med.set_linewidth(1.2)
    # Direct labels: the two medians ARE the claim. Set above each upper whisker, where nothing
    # else is drawn; beside the box they ran into the neighbouring box.
    for i,v in zip([0,1],[rec,nonrec]):
        q1,q3=np.percentile(v,[25,75])
        top=float(np.max(v[v<=q3+1.5*(q3-q1)]))
        ax.text(i,top+0.02,f'median {np.median(v):.2f}',fontsize=5.8,color=INK,
                ha='center',va='bottom')
    u_stat,pval=stats.mannwhitneyu(rec,nonrec)
    ax.set_xticks([0,1])
    ax.set_xticklabels(['recommended', 'not recommended'], fontsize=6.0)
    for x, nq in [(0, len(rec)), (1, len(nonrec))]:
        ax.text(x, -0.175, f'n = {nq}', transform=ax.get_xaxis_transform(), ha='center',
                va='top', fontsize=5.6, color=META)
    ax.set_xlabel('pre-specified diagnostic verdict',fontsize=6.2,labelpad=13.0)
    ax.set_ylabel('true response\ndivergence',fontsize=6.2)
    # 1:1 re-cut: the top of the view is opened from 2.02 to 2.22 so the test statistic sits above
    # the two median labels instead of on them once they are printed at full size.
    ax.set_xlim(-0.50,1.50); ax.set_ylim(1.14,2.22)
    ax.set_yticks([1.2,1.4,1.6,1.8,2.0]); ax.tick_params(labelsize=5.8)
    ax.spines['left'].set_bounds(1.14,2.02)
    ax.text(0.5,0.99,f'Mann$-$Whitney $p$ = {pval:.2f}',transform=ax.transAxes,ha='center',
            va='top',fontsize=6,color=GREY)
    for sp in ['right','top']: ax.spines[sp].set_visible(False)
    ax.set_title("Recommendation cannot sort by divergence", loc='left')


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(3.5,3.0))
    draw_3f(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "3f.png"), dpi=200, bbox_inches="tight")
    print("wrote 3f.png")
