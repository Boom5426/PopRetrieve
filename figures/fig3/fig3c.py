"""DART Figure 3 panel 3c: per-query regret reduction, ECDF over ALL 765 queries.

Source data: results/exp12_partial_observed_retrieval/per_query_scores.csv, paired per query
(mean_cosine decision_regret minus DART_coverage_worst decision_regret).

Scope note, and the reason this panel now reads the raw per-query file: it previously plotted
figures/source_data/fig3c_regret_reduction.csv, which holds only the 621 gate-recommended queries
(annotated "n=621, p=4e-56"). The manuscript caption and Results text both report panel c on ALL
765 partial-observed queries (median +0.118, 72% improved, Wilcoxon p = 1.6e-66), precisely so the
headline is not taken on a gate-selected subset. The panel was stale against the text; it now
computes the full 765-query set from the authoritative results file, and asserts n == 765 so a
subset cannot silently return. figures/source_data/fig3c_regret_reduction.csv has been regenerated
from the same computation.

Run standalone: python fig3c.py
"""
import os, numpy as np, pandas as pd, matplotlib as mpl, matplotlib.pyplot as plt
from scipy.stats import wilcoxon
FOCAL, COMP, GREY, INK = "#5185C0", "#E99D4E", "#7A7A7A", "#1A1A1A"
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

QUERY_KEY = ['split_type', 'cell_line', 'heldout_drug', 'observed_library_fraction', 'seed']
N_QUERIES = 765          # all partial-observed queries; see module docstring


def regret_reduction():
    """Paired per-query regret reduction, mean-cosine minus DART coverage-worst, all queries."""
    d = pd.read_csv(f"{REPO}/results/exp12_partial_observed_retrieval/per_query_scores.csv")
    base = d[d.method == 'mean_cosine'].set_index(QUERY_KEY)['decision_regret']
    dart = d[d.method == 'DART_coverage_worst'].set_index(QUERY_KEY)['decision_regret']
    j = pd.concat([base.rename('mean'), dart.rename('dart')], axis=1).dropna()
    assert len(j) == N_QUERIES, f"expected {N_QUERIES} paired queries, got {len(j)}"
    return (j['mean'] - j['dart']).values


def draw_3c(ax):
    """ECDF of the Class-A per-query regret reduction over all 765 partial-observed queries."""
    rr = regret_reduction()
    xs = np.sort(rr)
    ys = np.arange(1, len(xs) + 1) / len(xs)
    med = float(np.median(rr))
    frac_up = float((rr > 0).mean())
    frac_dn = float((rr < 0).mean())
    p = wilcoxon(rr).pvalue

    ax.plot(xs, ys, color=FOCAL, lw=1.8, zorder=4, solid_joinstyle='round')
    ax.axvline(0, ls='--', lw=0.9, color=GREY, zorder=1)
    ax.axvline(med, ls=':', lw=1.0, color=FOCAL, zorder=2)

    # the two readings that matter, marked on the curve itself
    ax.scatter([med], [0.5], s=16, color=FOCAL, zorder=5, linewidths=0)
    ax.scatter([0], [frac_dn], s=16, color=GREY, zorder=5, linewidths=0)
    ax.text(med + 0.12, 0.50, f'median\n+{med:.3f}', fontsize=6, color=FOCAL,
            va='center', ha='left', linespacing=1.15)
    ax.text(-0.06, frac_dn, f'{frac_dn:.0%}\nworse', fontsize=6, color=GREY,
            va='center', ha='right', linespacing=1.15)

    # Wrapped to three short lines for the 1.77 in printed panel. The interpretive half-sentence
    # that used to trail the mean ("pulled up by the right tail") is visible in the ECDF itself and
    # is stated in the text, so it is cut rather than shrunk below the 5 pt floor.
    exp = int(np.floor(np.log10(p)))
    mant = p / 10 ** exp
    ax.text(0.97, 0.05,
            f'paired Wilcoxon\n$p = {mant:.1f}\\times10^{{{exp}}}$\n'
            f'mean $+${np.mean(rr):.3f}',
            transform=ax.transAxes, ha='right', va='bottom', fontsize=6,
            color=INK, linespacing=1.3)

    ax.set_xlabel('regret reduction\n(mean cosine $-$ coverage-worst)', linespacing=1.2)
    ax.set_ylabel('cumulative fraction of queries')
    ax.set_xlim(-1.2, 2.9)
    ax.set_ylim(-0.02, 1.04)
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    for sp in ['right', 'top']:
        ax.spines[sp].set_visible(False)
    # title built from the plotted values, never hand-typed, so it cannot drift from the data
    ax.set_title(f"{frac_up:.0%} of all {len(rr)} queries\nimprove, median $+${med:.3f}",
                 loc='left', linespacing=1.15)


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(3.6, 3.0))
    draw_3c(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "3c.png"), dpi=200, bbox_inches="tight")
    print("wrote 3c.png")
