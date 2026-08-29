"""PopRetrieve Extended Data Fig. 6 panel a: HIR-Bench generative model
Source data: (schematic)
Run standalone: python ed6_panel_a.py
"""
import os, sys, numpy as np, pandas as pd, matplotlib as mpl, matplotlib.pyplot as plt
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")))
from figstyle import PT_MATH
# Palette comes from the house-style module; do NOT re-declare the hex values here. Every
# panel file used to carry its own copy, which made figstyle's "one edit here recolours the
# whole deck" untrue: a recolour meant editing 43 files and missing one was silent.
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
from figstyle import FOCAL_SOFT, COMP_SOFT, GREY, INK  # noqa: E402
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
H = os.path.join(REPO, "results", "exp11_hir_benchmark")
S = os.path.join(REPO, "results", "exp11_synthetic_phase_diagram")

def draw_ed6a(ax):
    """HIR-Bench generative model schematic."""
    ax.axis('off'); ax.set_xlim(0,1); ax.set_ylim(0,1)
    def box(x,y,w,h,txt,col,fc,fs=6.0):
        # ``fc`` is accepted and ignored: white fill, hairline coloured edge. The filled pastel
        # chips this schematic used to draw are a slide idiom and made the boxes the heaviest
        # ink in a panel whose content is the flow between them. Same treatment as fig5a.
        ax.add_patch(mpl.patches.FancyBboxPatch(
            (x-w/2,y-h/2),w,h,boxstyle='round,pad=0.006,rounding_size=0.014',
            fc='white',ec=col,lw=0.7))
        # Ink, not the edge colour it used to inherit: the hairline edge is the coloured mark.
        ax.text(x,y,txt,ha='center',va='center',fontsize=fs,color=INK)
    # 0.70 wide, not 0.50: at this figure's authored width the panel axes is about 2.6 in,
    # so 0.50 is 1.30 in and this label is 1.35 in of 6 pt text. It overhung the box it
    # was supposed to sit inside on both flanks.
    box(0.5,0.90,0.70,0.12,'query response = majority + minority',GREY,'white',6.0)
    box(0.24,0.66,0.30,0.14,'majority\nsubpop (1$-\\alpha$)',FOCAL_SOFT,'#eaf1f8')
    box(0.76,0.66,0.30,0.14,'minority\nsubpop ($\\alpha$)',COMP_SOFT,'#fbeceb')
    box(0.24,0.40,0.30,0.13,'welfare A\n(majority)',FOCAL_SOFT,'#eaf1f8')
    box(0.76,0.40,0.30,0.13,'welfare B\n(minority)',COMP_SOFT,'#fbeceb')
    # PT_MATH: the star in $\alpha^*$ prints at 0.7x nominal, so 6.4 pt put it at 4.5 pt.
    box(0.5,0.15,0.72,0.13,r'flip when $\alpha > \alpha^* = B/(A{+}B)$',GREY,'white',PT_MATH)
    for x0,y0,x1,y1,cc in [(0.24,0.83,0.24,0.73,FOCAL_SOFT),(0.76,0.83,0.76,0.73,COMP_SOFT),
                           (0.24,0.59,0.24,0.47,FOCAL_SOFT),(0.76,0.59,0.76,0.47,COMP_SOFT),
                           (0.24,0.33,0.42,0.21,GREY),(0.76,0.33,0.58,0.21,GREY)]:
        ax.annotate('',xy=(x1,y1),xytext=(x0,y0),arrowprops=dict(arrowstyle='->',lw=0.8,color=cc))
    ax.set_title("HIR-Bench generative model", loc='left')


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(3.5,3.0))
    draw_ed6a(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "ed6a.png"), dpi=200, bbox_inches="tight")
    print("wrote ed6a.png")
