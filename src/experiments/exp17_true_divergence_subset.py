"""exp17 — True-divergence-stratified non-circular audit (Phase 3: Q2 + Q3).

Decouples the gate entirely. Instead of asking "does the gate pick good queries?",
it asks the direct question: on genuinely high-divergence tasks (measured by TRUE
subpopulation response divergence, not the gate), does EvalShift beat mean retrieval on the
two NON-CIRCULAR metrics?

Q2 (stratified advantage):
  - Stratify all real per-query rows into quartiles of true_divergence.
  - In each stratum, paired EvalShift-vs-mean gap on minority_state_coverage and moa_ndcg,
    with paired Wilcoxon signed-rank + Benjamini-Hochberg across strata.
  - Core question: in the HIGHEST-divergence stratum, is EvalShift significantly > mean on a
    non-circular metric?

Q3 (power analysis):
  - For the highest-divergence stratum, compute achieved power at the current n and the
    n required for 80% power, per non-circular metric. Report whether the data suffice.

Outcome mapping (drives the final verdict A/B/C):
  - highest stratum significantly positive on a non-circular metric  -> A (conditional advantage holds)
  - positive but not significant + power analysis shows underpowered -> B (trend, sample-limited)
  - highest stratum ~0 or negative                                   -> C (chain broken in expression data)

ABSOLUTE RULES: non-circular metrics only as primary judges; FULL for verdicts;
BH correction; never write "trend" as "advantage"; null is a valid, reported result.

Outputs:
  results/exp17_true_divergence_subset/divergence_stratified.csv
  results/exp17_true_divergence_subset/power_analysis.csv
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from experiments.exp16_common import (                                                 # noqa: E402
    benjamini_hochberg, mask_undefined, n_for_power, power_two_sided,
)
from utils.io import results_path, write_csv                                            # noqa: E402
from utils.logging import log, section                                                  # noqa: E402

OUT = "exp17_true_divergence_subset"
DART_METHOD = "DART_coverage_worst"
MEAN_METHOD = "mean_cosine"
NONCIRCULAR = ["minority_state_coverage", "moa_ndcg"]
N_STRATA = 4


def _per_query_gaps():
    """One row per query: true_divergence + paired EvalShift-mean gap on each non-circular metric.

    Undefined metrics are masked to NaN BEFORE differencing (see exp16_common.mask_undefined).
    Without this, exp12's -1 sentinel differences to an exact 0 and 165 of the 765 queries
    (21.6%) enter every statistic as a structural zero.
    """
    perf = pd.read_csv(results_path("exp12_partial_observed_retrieval", "per_query_scores.csv"))
    if "true_divergence" not in perf.columns:
        raise RuntimeError("per_query_scores.csv lacks 'true_divergence' — run patched exp12 FULL first.")
    perf = mask_undefined(perf)
    keys = ["split_type", "cell_line", "heldout_drug", "heldout_MoA",
            "observed_library_fraction", "seed"]
    dart = perf[perf.method == DART_METHOD].set_index(keys)
    mean = perf[perf.method == MEAN_METHOD].set_index(keys)
    common = dart.index.intersection(mean.index)
    dart, mean = dart.loc[common], mean.loc[common]
    out = pd.DataFrame(index=common)
    out["true_divergence"] = dart["true_divergence"]
    for m in NONCIRCULAR:
        out[f"{m}_dart"] = dart[m]
        out[f"{m}_mean"] = mean[m]
        out[f"{m}_gap"] = dart[m] - mean[m]      # NaN wherever either side is undefined
    out = out.reset_index()
    return out.dropna(subset=["true_divergence"])


def _paired_test(gaps):
    """Paired Wilcoxon on the EvalShift-mean differences (gaps). Returns stat dict."""
    g = np.asarray(gaps, dtype=float)
    g = g[np.isfinite(g)]
    n = len(g)
    res = {"n": n, "mean_gap": float(np.mean(g)) if n else float("nan"),
           "median_gap": float(np.median(g)) if n else float("nan"),
           "sd_gap": float(np.std(g, ddof=1)) if n > 1 else float("nan"),
           "frac_positive": float(np.mean(g > 0)) if n else float("nan")}
    nonzero = g[g != 0]
    if len(nonzero) >= 6:
        try:
            _, p = wilcoxon(nonzero, alternative="two-sided")
            _, p_greater = wilcoxon(nonzero, alternative="greater")
        except ValueError:
            p = p_greater = float("nan")
    else:
        p = p_greater = float("nan")
    res["wilcoxon_p_two_sided"] = float(p)
    res["wilcoxon_p_greater"] = float(p_greater)
    return res


def stratified(df):
    section("EXP17 Q2 — true-divergence-stratified EvalShift-vs-mean on non-circular metrics")
    # Quartile edges on true_divergence (rank-based; robust to skew).
    df = df.copy()
    try:
        df["stratum"] = pd.qcut(df["true_divergence"], N_STRATA,
                                labels=[f"Q{i+1}" for i in range(N_STRATA)], duplicates="drop")
    except ValueError:
        df["stratum"] = pd.cut(df["true_divergence"], N_STRATA,
                               labels=[f"Q{i+1}" for i in range(N_STRATA)])
    rows = []
    strata = [s for s in df["stratum"].cat.categories if (df["stratum"] == s).any()]
    for metric in NONCIRCULAR:
        for s in strata:
            sub = df[df["stratum"] == s]
            st = _paired_test(sub[f"{metric}_gap"].values)
            lo, hi = sub["true_divergence"].min(), sub["true_divergence"].max()
            rows.append({"metric": metric, "stratum": s,
                         "divergence_lo": float(lo), "divergence_hi": float(hi),
                         "divergence_median": float(sub["true_divergence"].median()),
                         **st})
        # whole-population reference row
        st_all = _paired_test(df[f"{metric}_gap"].values)
        rows.append({"metric": metric, "stratum": "ALL",
                     "divergence_lo": float(df["true_divergence"].min()),
                     "divergence_hi": float(df["true_divergence"].max()),
                     "divergence_median": float(df["true_divergence"].median()), **st_all})
    res = pd.DataFrame(rows)
    # BH across the per-stratum (non-ALL) two-sided tests, within each metric family
    mask = res["stratum"] != "ALL"
    res["bh_qvalue"] = np.nan
    for metric in NONCIRCULAR:
        mm = mask & (res["metric"] == metric)
        res.loc[mm, "bh_qvalue"] = benjamini_hochberg(res.loc[mm, "wilcoxon_p_two_sided"].values)
    for _, r in res[res.stratum != "ALL"].iterrows():
        log(f"  [{r['metric']}] {r['stratum']} (div~{r['divergence_median']:.2f}, n={r['n']}): "
            f"median_gap={r['median_gap']:+.4f} frac+={r['frac_positive']:.2f} "
            f"p={r['wilcoxon_p_two_sided']:.3f} q={r['bh_qvalue']:.3f}")
    return res, df, strata


def power_analysis(df, strata):
    section("EXP17 Q3 — power analysis on the highest-divergence stratum")
    highest = strata[-1] if strata else None
    rows = []
    for metric in NONCIRCULAR:
        for s in ([highest] if highest else []):
            sub = df[df["stratum"] == s]
            g = sub[f"{metric}_gap"].values
            g = g[np.isfinite(g)]
            n = len(g)
            eff = float(np.mean(g)) if n else float("nan")
            sd = float(np.std(g, ddof=1)) if n > 1 else float("nan")
            achieved = power_two_sided(eff, sd, n)
            need = n_for_power(eff, sd, power=0.8)
            rows.append({"metric": metric, "stratum": s, "n": n,
                         "observed_mean_gap": eff, "sd_gap": sd,
                         "achieved_power": achieved,
                         "n_for_80pct_power": need,
                         "data_sufficient": bool(np.isfinite(need) and n >= need)})
    res = pd.DataFrame(rows)
    for _, r in res.iterrows():
        need = r["n_for_80pct_power"]
        need_s = f"{need:.0f}" if np.isfinite(need) else "inf"
        log(f"  [{r['metric']}] {r['stratum']}: n={r['n']} eff={r['observed_mean_gap']:+.4f} "
            f"power={r['achieved_power']:.2f} n@80%={need_s} sufficient={r['data_sufficient']}")
    return res


def run(quick=False):
    section(f"EXP17 TRUE-DIVERGENCE SUBSET ({'QUICK' if quick else 'FULL'})")
    df = _per_query_gaps()
    log(f"  loaded {len(df)} queries with paired EvalShift/mean non-circular outcomes")
    log(f"  true_divergence range [{df.true_divergence.min():.3f}, {df.true_divergence.max():.3f}]")

    strat, df_s, strata = stratified(df)
    write_csv(strat, results_path(OUT, "divergence_stratified.csv"))
    power = power_analysis(df_s, strata)
    write_csv(power, results_path(OUT, "power_analysis.csv"))
    return strat, power


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    args = ap.parse_args()
    run(quick=args.quick)


if __name__ == "__main__":
    main()
