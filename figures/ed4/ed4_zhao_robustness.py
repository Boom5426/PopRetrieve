"""Extended Data Fig. 4: validation and threshold robustness of the compartment
assignments in patient-derived glioblastoma (ZhaoSims2021).

Replaces the retired resistance-exploratory panel, whose figure body no longer matched
its caption. The four panels are exactly the four the caption names:

  a  marker-expression validation of the three retained compartments
  b  cells retained against cells left unassigned, over the joint threshold sweep
  c  malignant-versus-myeloid differential-response cosine over the same sweep
  d  supervised ceiling and best unsupervised recovery over the same sweep

Source data: results/zhao_gbm/compartment_validation.csv   (panel a)
             results/zhao_gbm/zhao_threshold_sensitivity.csv (panels b-d)
Run standalone: python ed4_zhao_robustness.py
"""
from __future__ import annotations

import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "figures"))
from figstyle import (FOCAL_SOFT, COMP_SOFT, GREY, INK, META, PURPLE_SOFT, apply_style,
                      panel_letter, save, soften_axes, strip_titles)  # noqa: E402

P = os.path.join(REPO, "results", "zhao_gbm")
STEM = "ed4_zhao_robustness"
FIG_W, FIG_H = 6.90, 2.45

BOXES = {
    "a": (0.52, 0.52, 1.30, 1.20),
    "b": (2.28, 0.52, 1.24, 1.20),
    "c": (4.02, 0.52, 1.18, 1.20),
    "d": (5.72, 0.52, 1.06, 1.20),
}
TITLES = {"a": "Compartment calls match\ntheir own markers",
          "b": "Cells retained across\nthe threshold sweep",
          "c": "Differential response\nis threshold-stable",
          "d": "Recoverability gap\npersists throughout"}

COMPART = ["malignant", "myeloid", "oligo"]
SHORT = {"malignant": "malig.", "myeloid": "myeloid", "oligo": "oligo"}


def _val():
    return pd.read_csv(os.path.join(P, "compartment_validation.csv"))


def _sweep():
    df = pd.read_csv(os.path.join(P, "zhao_threshold_sensitivity.csv"))
    return df.sort_values("floor").reset_index(drop=True)


def draw_a(ax):
    """Called compartment against marker-set mean expression: the diagonal must win."""
    v = _val().set_index("compartment")
    M = np.array([[float(v.loc[c, f"expr_{m}"]) for m in COMPART] for c in COMPART])
    x = np.arange(len(COMPART))
    w = 0.26
    for j, m in enumerate(COMPART):
        ax.bar(x + (j - 1) * w, M[:, j], width=w,
               color=[FOCAL_SOFT, COMP_SOFT, PURPLE_SOFT][j], alpha=0.9, label=f"{SHORT[m]} markers")
    ax.set_xticks(x)
    ax.set_xticklabels([SHORT[c] for c in COMPART], fontsize=6.2)
    ax.set_xlabel("called compartment", fontsize=6.2, labelpad=1.5)
    ax.set_ylabel("mean marker-set\nexpression", fontsize=6.2)
    ax.legend(fontsize=5.0, frameon=False, loc="upper center", ncol=1,
              handlelength=0.9, borderpad=0.1, labelspacing=0.2)
    ax.set_ylim(0, M.max() * 1.42)


def draw_b(ax):
    """How much of the tissue survives assignment as the two thresholds move together."""
    d = _sweep()
    t = d["floor"].values
    un = d["frac_unassigned"].values
    ax.plot(t, 1 - un, "o-", color=FOCAL_SOFT, ms=4, lw=1.3, label="retained")
    ax.plot(t, un, "s--", color=COMP_SOFT, ms=3.6, lw=1.2, label="unassigned")
    pap = d[d["is_paper_setting"]]
    if len(pap):
        ax.axvline(float(pap["floor"].iloc[0]), ls=":", lw=0.9, color=GREY)
        ax.text(float(pap["floor"].iloc[0]) + 0.012, 0.92, "primary",
                fontsize=5.2, color=META, rotation=90, va="top")
    ax.set_ylim(0, 1)
    ax.set_xlabel("marker floor = margin", fontsize=6.2, labelpad=1.5)
    ax.set_ylabel("fraction of cells", fontsize=6.2)
    ax.legend(fontsize=5.2, frameon=False, loc="lower left",
              handlelength=1.1, borderpad=0.1, labelspacing=0.25)


def draw_c(ax):
    """Malignant vs myeloid induced-response cosine; low = compartments diverge."""
    d = _sweep()
    ax.plot(d["floor"], d["gate1_cos"], "o-", color=FOCAL_SOFT, ms=4, lw=1.3)
    lo, hi = float(d["gate1_cos"].min()), float(d["gate1_cos"].max())
    ax.axhspan(lo, hi, color=FOCAL_SOFT, alpha=0.10, lw=0)
    ax.text(0.98, 0.04, f"range {lo:.2f}-{hi:.2f}", fontsize=5.2, color=INK,
            ha="right", va="bottom", transform=ax.transAxes)
    ax.set_ylim(0, 1)
    ax.set_xlabel("marker floor = margin", fontsize=6.2, labelpad=1.5)
    ax.set_ylabel("differential response\ncosine (median)", fontsize=6.2)


def draw_d(ax):
    """Supervised ceiling against best unsupervised recovery, and the gap between them."""
    d = _sweep()
    t = d["floor"].values
    ax.fill_between(t, d["gate2_unsup"], d["gate2_ceiling"], color=GREY, alpha=0.16, lw=0)
    ax.plot(t, d["gate2_ceiling"], "o-", color=FOCAL_SOFT, ms=4, lw=1.3, label="supervised")
    ax.plot(t, d["gate2_unsup"], "s-", color=COMP_SOFT, ms=3.6, lw=1.2, label="unsupervised")
    ax.set_ylim(0.5, 1.0)
    ax.set_xlabel("marker floor = margin", fontsize=6.2, labelpad=1.5)
    ax.set_ylabel("drug-response\nrecovery accuracy", fontsize=6.2)
    ax.legend(fontsize=5.2, frameon=False, loc="lower left",
              handlelength=1.1, borderpad=0.1, labelspacing=0.25)


def build(apply_style_fn, panel_letter_fn):
    apply_style_fn(sizes=(7, 6.2, 5.6))
    fig = plt.figure(figsize=(FIG_W, FIG_H))
    fns = {"a": draw_a, "b": draw_b, "c": draw_c, "d": draw_d}
    for k, (x0, y0, w, h) in BOXES.items():
        ax = fig.add_axes([x0 / FIG_W, y0 / FIG_H, w / FIG_W, h / FIG_H])
        fns[k](ax)
        ax.set_title(TITLES[k], loc="left", fontsize=7)
        panel_letter_fn(ax, k, case="lower", dx=-0.40 / w, dy=1.20)
    # Same rule as the rest of the deck: the caption carries the four per-panel entries, so the
    # drawn titles go and TITLES stays as the declaration each panel is checked against.
    return strip_titles(soften_axes(fig))


if __name__ == "__main__":
    f = build(apply_style, panel_letter)
    save(f, os.path.join(HERE, STEM))
    print(f"wrote {STEM}.{{pdf,svg,png}}")
