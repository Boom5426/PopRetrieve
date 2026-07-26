"""JUDGE Figure 4 panel 4c: minority coverage gain by divergence quartile
Source data: source_data/fig4ef_gate_divergence.csv
Run standalone: python fig4c.py
"""
import os, numpy as np, pandas as pd, matplotlib as mpl, matplotlib.pyplot as plt
FOCAL, COMP, GREY, INK = "#5185C0", "#E99D4E", "#7A7A7A", "#1A1A1A"
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
key=["split_type","cell_line","heldout_drug","observed_library_fraction","seed"]

def draw_4c(ax):
    """Minority-coverage effect size by divergence quartile (significant but negligible).

    Presentation note (2026-07-26). The bars are the QUARTILE MEAN with its s.e.m., and used to
    carry a caption reading "significant but negligible (<0.002)". That bound is true of the
    quartile MEDIANS (+0.0009 to +0.0018, the numbers the manuscript quotes) and false of the
    means plotted here (+0.0042 to +0.0062), which are pulled up by a heavy tail. The statistic
    on the axis is unchanged; the median is now drawn on each bar as well, and the note states
    what is actually true of both: the effect is a fraction of a metric that operates on
    [0.89, 0.99].
    """
    mg=pd.read_csv(f"{REPO}/results/exp16_gate_diagnosis/_merged_query_divergence.csv")
    mg=mg.dropna(subset=['true_divergence','minority_state_coverage_gap'])
    mg['divq']=pd.qcut(mg['true_divergence'],4,labels=['Q1','Q2','Q3','Q4'])
    g=mg.groupby('divq',observed=True)['minority_state_coverage_gap'].agg(['mean','sem','median'])
    xs=np.arange(len(g))
    ax.bar(xs,g['mean'],yerr=g['sem'],width=0.62,color=FOCAL,alpha=0.80,
           error_kw=dict(lw=0.8,capsize=1.8,ecolor=INK))
    ax.plot(xs,g['median'],ls='',marker='_',ms=9,mew=1.2,color=INK,zorder=4)
    ax.axhline(0,color=INK,lw=0.8)
    ax.set_xticks(xs); ax.set_xticklabels(g.index,fontsize=6.2)
    ax.set_xlabel('true divergence quartile',fontsize=6.2)
    ax.set_ylabel('minority-coverage gain,\ndistributional $-$ mean',fontsize=6.2)
    # 1:1 re-cut: the head-room above the bars is opened from 0.0098 to 0.0135 so the four-line
    # key sits clear of the tallest error bar in a panel that is now 1.1 in wide. Same statistic,
    # same bars; only the view and the line breaks changed.
    ax.set_ylim(0,0.0135)
    ax.set_yticks([0,0.004,0.008,0.012])
    ax.tick_params(labelsize=5.8)
    ax.text(0.03,0.99,'bar, mean $\\pm$ s.e.m.\ndash, median\n'
                      'significant, all $\\leq$0.006\non a 0.89$-$0.99 metric',
            transform=ax.transAxes,ha='left',va='top',fontsize=5.6,color=GREY,linespacing=1.30)
    for sp in ['right','top']: ax.spines[sp].set_visible(False)
    ax.set_title("Minority-coverage gain is negligible", loc='left')


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(3.5,3.0))
    draw_4c(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "4c.png"), dpi=200, bbox_inches="tight")
    print("wrote 4c.png")
