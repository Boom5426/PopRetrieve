"""JUDGE Figure 4 panel 4f: recommendation cannot sort divergence
Source data: source_data/fig4ef_gate_divergence.csv
Run standalone: python fig4f.py
"""
import os, numpy as np, pandas as pd, matplotlib as mpl, matplotlib.pyplot as plt
from scipy import stats
FOCAL, COMP, GREY, INK = "#5185C0", "#E99D4E", "#7A7A7A", "#1A1A1A"
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
key=["split_type","cell_line","heldout_drug","observed_library_fraction","seed"]

def draw_4f(ax):
    """Binary recommendation does not separate divergence (Mann-Whitney p=0.09)."""
    mg=pd.read_csv(f"{REPO}/results/exp16_gate_diagnosis/_merged_query_divergence.csv")
    u=mg.dropna(subset=['true_divergence']).drop_duplicates(subset=key)
    rec=u[u.recommendation_mode=='DART_recommended']['true_divergence']
    nonrec=u[u.recommendation_mode!='DART_recommended']['true_divergence']
    bp=ax.boxplot([rec,nonrec],positions=[0,1],widths=0.5,patch_artist=True,showfliers=False)
    for patch,col in zip(bp['boxes'],[FOCAL,GREY]):
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
    ax.set_xticklabels([f'recommended\nn={len(rec)}',f'not recommended\nn={len(nonrec)}'],fontsize=6.0)
    ax.set_xlabel('information-condition gate verdict',fontsize=6.2)
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
    draw_4f(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "4f.png"), dpi=200, bbox_inches="tight")
    print("wrote 4f.png")
