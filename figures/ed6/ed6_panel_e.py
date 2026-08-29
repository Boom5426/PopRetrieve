"""PopRetrieve Extended Data Fig. 6 panel e: benchmark QC
Source data: results/exp11_hir_benchmark/sanity_checks.csv
Run standalone: python ed6_panel_e.py
"""
import os, numpy as np, pandas as pd, matplotlib as mpl, matplotlib.pyplot as plt
# Palette comes from the house-style module; do NOT re-declare the hex values here. Every
# panel file used to carry its own copy, which made figstyle's "one edit here recolours the
# whole deck" untrue: a recolour meant editing 43 files and missing one was silent.
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
from figstyle import FOCAL_SOFT, COMP_SOFT, GREY, INK, TRACK  # noqa: E402
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
H = os.path.join(REPO, "results", "exp11_hir_benchmark")
S = os.path.join(REPO, "results", "exp11_synthetic_phase_diagram")

def draw_ed6d(ax):
    """QC sanity checks panel."""
    sc=pd.read_csv(f"{H}/sanity_checks.csv")
    labs={'no_conflict_flip_rate':'no-conflict\nflip rate','median_boundary_margin':'median\nboundary margin',
          'predicted_mean_dart_eq_mean':'pred-mean:\ndistributional=mean'}
    # Every check is scored on the same 0-1 scale, so the track states it once and each bar
    # reads as a fraction of it. Without the track the three bars were three unrelated lengths
    # against a distant axis, and the threshold ticks had nothing to sit against.
    TRACK_MAX = 1.0
    ys=np.arange(len(sc))
    for y,(_,row) in zip(ys,sc.iterrows()):
        passed=row['pass']==1
        ax.barh(y,TRACK_MAX,color=TRACK,height=0.5,lw=0,zorder=1)
        ax.barh(y,row['value'],color=FOCAL_SOFT if passed else COMP_SOFT,height=0.5,zorder=2)
        ax.plot(row['threshold'],y,'|',ms=10,color=INK,mew=1.0,zorder=3)
        # Set just past the bar end, and past the threshold tick ONLY when that tick would fall
        # inside the label. Anchored to the bar alone the label printed on top of the tick for the
        # two checks whose threshold sits just beyond a short bar; anchored to max(bar, threshold)
        # unconditionally it flew to x = 1.03 for the boundary-margin row, 0.7 of the axis away
        # from the bar it belongs to. LAB_W is the label's own width in data units at 5.8 pt.
        LAB_W = 0.22
        x_lab = row['value'] + 0.03
        if x_lab <= row['threshold'] <= x_lab + LAB_W:
            x_lab = row['threshold'] + 0.03
        # PASS/FAIL is already a word, so it does not also need a hue; the bar beside it is the
        # coloured mark. A failing check would be the exception worth weighting, and there is
        # none in this table, so weight is left alone rather than being spent on the pass case.
        ax.text(x_lab,y,f"{row['value']:.3f} {'PASS' if passed else 'FAIL'}",va='center',fontsize=5.8,
                color=INK)
    ax.set_yticks(ys); ax.set_yticklabels([labs.get(c,c) for c in sc['check']],fontsize=5.8)
    ax.set_xlabel('value (| = threshold)'); ax.set_xlim(0,1.42)
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.spines['bottom'].set_bounds(0, TRACK_MAX)   # the axis is the track
    for sp in ['right','top']: ax.spines[sp].set_visible(False)
    ax.set_title("Benchmark quality control", loc='left')


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(3.5,3.0))
    draw_ed6d(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "ed6d.png"), dpi=200, bbox_inches="tight")
    print("wrote ed6d.png")
