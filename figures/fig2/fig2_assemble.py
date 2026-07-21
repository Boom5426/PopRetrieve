"""DART Figure 2: Mean retrieval is the variance-collapsed limit of distribution-aware retrieval.
Assembles panels a-f into fig2_unification.{png,pdf}. Reproducible entry point.
Requires figure-style apply_figure_style/panel_letter in the kernel, or run via the build harness.
"""
import os, sys, matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fig2a import draw_2a
from fig2b import draw_2b
from fig2c import draw_2c
from fig2d import draw_2d
from fig2e import draw_2e
from fig2f import draw_2f

def build(apply_style, panel_letter):
    apply_style(sizes=(8,7,6))
    fig = plt.figure(figsize=(7.09,7.4))
    gs = fig.add_gridspec(3,2,hspace=0.55,wspace=0.34,left=0.10,right=0.975,top=0.945,bottom=0.06)
    for r,c,k,fn in [(0,0,"a",draw_2a),(0,1,"b",draw_2b),(1,0,"c",draw_2c),
                     (1,1,"d",draw_2d),(2,0,"e",draw_2e),(2,1,"f",draw_2f)]:
        ax = fig.add_subplot(gs[r,c]); fn(ax); panel_letter(ax,k,case="lower")
    out = os.path.dirname(os.path.abspath(__file__))
    fig.savefig(os.path.join(out,"fig2_unification.png"), dpi=300, bbox_inches="tight")
    fig.savefig(os.path.join(out,"fig2_unification.pdf"), bbox_inches="tight")
    return fig


if __name__ == "__main__":
    from figstyle import apply_style, panel_letter
    build(apply_style, panel_letter)
    print("wrote fig2 composite")
