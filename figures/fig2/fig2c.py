"""PopRetrieve Figure 2 panel 2c: per-query regret reduction, ECDF over ALL 765 queries.

Source data: results/exp12_partial_observed_retrieval/per_query_scores.csv, paired per query
(mean_cosine decision_regret minus DART_coverage_worst decision_regret).

Scope note, and the reason this panel now reads the raw per-query file: it previously plotted
figures/source_data/fig2c_regret_reduction.csv, which holds only the 621 gate-recommended queries
(annotated "n=621, p=4e-56"). The manuscript caption and Results text both report panel c on ALL
765 partial-observed queries (median +0.118, 72% improved, Wilcoxon p = 1.6e-66), precisely so the
headline is not taken on a gate-selected subset. The panel was stale against the text; it now
computes the full 765-query set from the authoritative results file, and asserts n == 765 so a
subset cannot silently return. figures/source_data/fig2c_regret_reduction.csv has been regenerated
from the same computation.

Run standalone: python fig2c.py
"""
import os, sys, numpy as np, pandas as pd, matplotlib as mpl, matplotlib.pyplot as plt
from scipy.stats import wilcoxon
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from figstyle import PT_MATH
# Palette comes from the house-style module; do NOT re-declare the hex values here. Every
# panel file used to carry its own copy, which made figstyle's "one edit here recolours the
# whole deck" untrue: a recolour meant editing 43 files and missing one was silent.
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
from figstyle import FOCAL_SOFT, RULE, META, INK  # noqa: E402
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

QUERY_KEY = ['split_type', 'cell_line', 'heldout_drug', 'observed_library_fraction', 'seed']
N_QUERIES = 765          # all partial-observed queries; see module docstring


def regret_reduction():
    """Paired per-query regret reduction, mean-cosine minus PopRetrieve coverage-worst, all queries."""
    d = pd.read_csv(f"{REPO}/results/exp12_partial_observed_retrieval/per_query_scores.csv")
    base = d[d.method == 'mean_cosine'].set_index(QUERY_KEY)['decision_regret']
    dart = d[d.method == 'DART_coverage_worst'].set_index(QUERY_KEY)['decision_regret']
    j = pd.concat([base.rename('mean'), dart.rename('dart')], axis=1).dropna()
    assert len(j) == N_QUERIES, f"expected {N_QUERIES} paired queries, got {len(j)}"
    return (j['mean'] - j['dart']).values


def draw_2c(ax):
    """ECDF of the Class-A per-query regret reduction over all 765 partial-observed queries."""
    rr = regret_reduction()
    xs = np.sort(rr)
    ys = np.arange(1, len(xs) + 1) / len(xs)
    med = float(np.median(rr))
    frac_up = float((rr > 0).mean())
    frac_dn = float((rr < 0).mean())
    p = wilcoxon(rr).pvalue

    ax.plot(xs, ys, color=FOCAL_SOFT, lw=1.2, zorder=4, solid_joinstyle='round')
    ax.axvline(0, ls='-', lw=0.7, color=RULE, zorder=1)
    ax.axvline(med, ls=':', lw=0.8, color=FOCAL_SOFT, zorder=2)

    # the two readings that matter, marked on the curve itself; the text is ink and grey, the
    # colour is left to the markers
    ax.scatter([med], [0.5], s=14, color=FOCAL_SOFT, zorder=5, linewidths=0)
    ax.scatter([0], [frac_dn], s=14, color=META, zorder=5, linewidths=0)
    ax.text(med + 0.14, 0.50, f'median  +{med:.3f}', fontsize=6, color=INK,
            va='center', ha='left')
    ax.text(-0.10, frac_dn, f'{frac_dn:.0%} worse', fontsize=6, color=META,
            va='center', ha='right')

    # Wrapped to three short lines for the 1.77 in printed panel. The interpretive half-sentence
    # that used to trail the mean ("pulled up by the right tail") is visible in the ECDF itself and
    # is stated in the text, so it is cut rather than shrunk below the 5 pt floor.
    # THE TEST AND THE MEAN ARE IN THE CAPTION. A Nature figure legend has to define the test,
    # its n and its statistic anyway, so a three-line stats block on the panel is the same words
    # twice. The two direct labels that remain mark points on the curve and are not restatements
    # of the caption.
    _ = p  # p is quoted in the caption; kept here so the source of that number is this file

    ax.set_xlabel('regret reduction\n(mean cosine $-$ coverage-worst)', linespacing=1.2)
    ax.set_ylabel('cumulative fraction of queries')
    ax.set_xlim(-1.2, 2.9)
    ax.set_ylim(-0.02, 1.04)
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.tick_params(axis='both', length=2.2, color=RULE, labelcolor=INK)
    for sp in ['right', 'top']:
        ax.spines[sp].set_visible(False)
    for sp in ['left', 'bottom']:
        ax.spines[sp].set_color(RULE)
    # title built from the plotted values, never hand-typed, so it cannot drift from the data
    ax.set_title(f"{frac_up:.0%} of all {len(rr)} queries\nimprove, median $+${med:.3f}",
                 loc='left', linespacing=1.15)


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(3.6, 3.0))
    draw_2c(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "2c.png"), dpi=200, bbox_inches="tight")
    print("wrote 2c.png")
