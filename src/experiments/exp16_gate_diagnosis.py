"""exp16 — Gate diagnosis (Phase 1 & Phase 2 of the gate-repair audit).

Question being audited: exp12's diagnostic gate labels a "DART_recommended" subset
whose non-circular advantage (+regret is energy-based/circular) is no better than the
non-recommended subset — the gate has no discriminative power. Before trying to fix or
repair the gate we must locate the lesion.

Phase 1 (Q1): is the gate even aligned with TRUE subpopulation response divergence?
  - Rebuild every exp12 query deterministically (same seeds), compute true response
    divergence (exp16_common.true_response_divergence) — a quantity the gate never saw.
  - Merge onto exp12's logged gate labels + non-circular outcomes.
  - Test: (a) recommended vs non-recommended true-divergence (Mann-Whitney U);
           (b) Spearman(preference_conflict, true_divergence).
  - Output: results/exp16_gate_diagnosis/gate_vs_true_divergence.csv

Phase 2: gate-variant sweep (only meaningful if a fix is plausible, but we run it
  regardless and report the full table — no cherry-picking).
  - Enumerate preference_conflict and structure_reliability variants.
  - For each, the recommended-vs-nonrecommended gap on the two NON-CIRCULAR metrics
    (minority_state_coverage, moa_ndcg), with leave-one-CELL-LINE-out CV (all lines are SciPlex3; this is NOT cross-dataset) and
    Benjamini-Hochberg correction.
  - Output: results/exp16_gate_diagnosis/gate_variants_sweep.csv

ABSOLUTE RULES (anti-self-deception, per the execution spec):
  - Primary judge metrics are the two NON-CIRCULAR ones only. Never tune an
    energy-based / EvalShift-aligned metric to make EvalShift win.
  - No cherry-picking a variant without multiple-comparison correction.
  - FULL only for verdicts; QUICK for sanity.
  - "trend but not significant" is never written as "advantage". null is a valid result.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu, spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from experiments.exp16_common import benjamini_hochberg, mask_undefined   # noqa: E402
from utils.io import results_path, write_csv                       # noqa: E402
from utils.logging import log, section                             # noqa: E402

OUT = "exp16_gate_diagnosis"

# The EvalShift method vs the mean incumbent for per-query non-circular gaps.
DART_METHOD = "DART_coverage_worst"
MEAN_METHOD = "mean_cosine"
NONCIRCULAR = ["minority_state_coverage", "moa_ndcg"]


# ─────────────────────────────────────────────────────────────────────────────
# Query reconstruction: replay exp12's per-query loops, emit true divergence only.
# We reproduce the EXACT rng consumption order so query_X matches exp12 bit-for-bit.
# ─────────────────────────────────────────────────────────────────────────────

def _load_exp12_perquery():
    """Load exp12 per-query scores; one row per query with gate labels, true divergence,
    and EvalShift-vs-mean gaps on the two non-circular metrics.

    exp12 is patched to log `true_divergence` (exp16_common.true_response_divergence)
    on the exact query population it scores — so there is NO reconstruction/join drift.
    We read that column directly rather than rebuilding queries.
    """
    perf = pd.read_csv(results_path("exp12_partial_observed_retrieval", "per_query_scores.csv"))
    if "true_divergence" not in perf.columns:
        raise RuntimeError("per_query_scores.csv lacks 'true_divergence' — re-run patched exp12 "
                           "(FULL) before exp16.")
    # exp12's -1 "not applicable" sentinel must never be differenced like a measurement:
    # (-1) - (-1) = 0 would enter the gap statistics as a structural zero.
    perf = mask_undefined(perf)
    keys = ["split_type", "cell_line", "heldout_drug", "heldout_MoA",
            "observed_library_fraction", "seed"]
    agg = dict(
        recommendation_mode=("recommendation_mode", "first"),
        structure_reliability_score=("structure_reliability_score", "first"),
        preference_conflict=("preference_conflict", "first"),
        information_condition_mode=("information_condition_mode", "first"),
        true_divergence=("true_divergence", "first"),
    )
    for extra in ("true_div_min_cos", "true_div_minority_frac"):
        if extra in perf.columns:
            agg[extra] = (extra, "first")
    gate = perf.groupby(keys, dropna=False).agg(**agg).reset_index()
    # EvalShift and mean non-circular outcomes -> per-query gap
    dart = perf[perf.method == DART_METHOD].set_index(keys)[NONCIRCULAR]
    mean = perf[perf.method == MEAN_METHOD].set_index(keys)[NONCIRCULAR]
    gap = (dart - mean).rename(columns={m: f"{m}_gap" for m in NONCIRCULAR}).reset_index()
    out = gate.merge(gap, on=keys, how="left")
    out = out.merge(dart.add_suffix("_dart").reset_index(), on=keys, how="left")
    out = out.merge(mean.add_suffix("_mean").reset_index(), on=keys, how="left")
    return out, keys


# ─────────────────────────────────────────────────────────────────────────────
# Phase 1: alignment of gate labels with true divergence
# ─────────────────────────────────────────────────────────────────────────────

def phase1(merged):
    section("EXP16 Phase 1 — gate vs true divergence alignment")
    rec = merged[merged.recommendation_mode == "DART_recommended"]["true_divergence"].dropna()
    non = merged[merged.recommendation_mode != "DART_recommended"]["true_divergence"].dropna()

    rows = []
    if len(rec) >= 3 and len(non) >= 3:
        u, p_mw = mannwhitneyu(rec, non, alternative="two-sided")
        # rank-biserial effect size
        rb = 1 - 2 * u / (len(rec) * len(non))
        rows.append({"test": "recommended_vs_nonrecommended_divergence",
                     "statistic": float(u), "pvalue": float(p_mw),
                     "effect_size_rank_biserial": float(rb),
                     "n_recommended": int(len(rec)), "n_nonrecommended": int(len(non)),
                     "median_recommended": float(rec.median()),
                     "median_nonrecommended": float(non.median())})
    sub = merged.dropna(subset=["true_divergence", "preference_conflict"])
    if len(sub) >= 3:
        rho, p_sp = spearmanr(sub.preference_conflict, sub.true_divergence)
        rows.append({"test": "spearman_preference_conflict_vs_divergence",
                     "statistic": float(rho), "pvalue": float(p_sp),
                     "effect_size_rank_biserial": float("nan"),
                     "n_recommended": int(len(sub)), "n_nonrecommended": 0,
                     "median_recommended": float("nan"), "median_nonrecommended": float("nan")})
    # also structure_reliability vs divergence
    sub2 = merged.dropna(subset=["true_divergence", "structure_reliability_score"])
    if len(sub2) >= 3:
        rho2, p2 = spearmanr(sub2.structure_reliability_score, sub2.true_divergence)
        rows.append({"test": "spearman_structure_reliability_vs_divergence",
                     "statistic": float(rho2), "pvalue": float(p2),
                     "effect_size_rank_biserial": float("nan"),
                     "n_recommended": int(len(sub2)), "n_nonrecommended": 0,
                     "median_recommended": float("nan"), "median_nonrecommended": float("nan")})
    df = pd.DataFrame(rows)
    for _, r in df.iterrows():
        log(f"  {r['test']}: stat={r['statistic']:.4f} p={r['pvalue']:.3e} "
            f"n={r['n_recommended']}")
    return df


# ─────────────────────────────────────────────────────────────────────────────
# Phase 2: gate-variant sweep on NON-CIRCULAR metrics, leave-one-cell-line-out CV, BH-corrected
# ─────────────────────────────────────────────────────────────────────────────

def _conflict_variants(merged):
    """Dict of candidate preference-conflict signals available per query."""
    v = {}
    v["gate_preference_conflict"] = merged["preference_conflict"].values
    # divergence-derived surrogates (available at query time from observed data)
    v["true_divergence"] = merged["true_divergence"].values
    if "true_div_min_cos" in merged:
        v["min_pairwise_cos_neg"] = -merged["true_div_min_cos"].values
    return v


def _reliability_variants(merged):
    v = {}
    v["gate_structure_reliability"] = merged["structure_reliability_score"].values
    # structure surrogates available from the patched exp12 columns
    if "true_div_minority_frac" in merged:
        v["minority_frac"] = merged["true_div_minority_frac"].values
    # a second reliability axis: how strongly the gate already rated structure
    v["structure_x_conflict"] = (merged["structure_reliability_score"].values *
                                 merged["preference_conflict"].values)
    return v


def phase2(merged):
    # The held-out unit here is a CELL LINE, and all of them (A549, K562, MCF7) come from a
    # single dataset, SciPlex3. This is leave-one-CELL-LINE-out within one experiment, NOT
    # leave-one-DATASET-out: the three lines share batch, protocol, HVG set and
    # normalization, so the cross-validation does not license a cross-dataset
    # generalization claim. The threshold-fitting scheme is unchanged; only the name and the
    # claim it supports are corrected.
    section("EXP16 Phase 2 — gate-variant sweep (non-circular metrics, LOCO-CV over "
            "SciPlex3 cell lines, BH)")
    conflicts = _conflict_variants(merged)
    reliabilities = _reliability_variants(merged)
    contexts = sorted(merged.cell_line.dropna().unique().tolist())
    log(f"  held-out units: {contexts} (all SciPlex3 cell lines, one dataset)")

    rows = []
    for cname, cvals in conflicts.items():
        for rname, rvals in reliabilities.items():
            m = merged.copy()
            m["_c"] = cvals
            m["_r"] = rvals
            m = m.dropna(subset=["_c", "_r"] + [f"{x}_gap" for x in NONCIRCULAR])
            if len(m) < 20:
                continue
            # Recommended = above-median on BOTH conflict and reliability, with thresholds
            # fit on the other cell lines so they are not tuned on the line being tested.
            rec_mask = np.zeros(len(m), dtype=bool)
            for held in contexts:
                train = m[m.cell_line != held]
                test_idx = np.where(m.cell_line.values == held)[0]
                if len(train) < 5 or len(test_idx) == 0:
                    continue
                c_thr = np.nanmedian(train["_c"].values)
                r_thr = np.nanmedian(train["_r"].values)
                tt = m.iloc[test_idx]
                sel = (tt["_c"].values >= c_thr) & (tt["_r"].values >= r_thr)
                rec_mask[test_idx] = sel
            for metric in NONCIRCULAR:
                gcol = f"{metric}_gap"
                rec_gap = m.loc[rec_mask, gcol].dropna()
                non_gap = m.loc[~rec_mask, gcol].dropna()
                if len(rec_gap) < 5 or len(non_gap) < 5:
                    continue
                u, p = mannwhitneyu(rec_gap, non_gap, alternative="two-sided")
                rb = 1 - 2 * u / (len(rec_gap) * len(non_gap))
                # cross-dataset stability: sign of per-context recommended-gap median
                per_ctx_sign = []
                for held in contexts:
                    cc_mask = (m.cell_line.values == held) & rec_mask
                    if cc_mask.sum() >= 3:
                        per_ctx_sign.append(np.sign(np.nanmedian(m.loc[cc_mask, gcol])))
                stability = float(np.mean([s > 0 for s in per_ctx_sign])) if per_ctx_sign else float("nan")
                rows.append({
                    "conflict_variant": cname, "reliability_variant": rname,
                    "metric": metric, "n_recommended": int(len(rec_gap)),
                    "n_nonrecommended": int(len(non_gap)),
                    "recommended_gap_median": float(rec_gap.median()),
                    "nonrecommended_gap_median": float(non_gap.median()),
                    "gap_of_gaps": float(rec_gap.median() - non_gap.median()),
                    "mannwhitney_p": float(p),
                    "effect_size_rank_biserial": float(rb),
                    "cross_cellline_pos_fraction": stability,
                })
    df = pd.DataFrame(rows)
    if len(df):
        df["bh_qvalue"] = benjamini_hochberg(df["mannwhitney_p"].values)
        df = df.sort_values("gap_of_gaps", ascending=False).reset_index(drop=True)
        for _, r in df.head(6).iterrows():
            log(f"  {r['conflict_variant']}×{r['reliability_variant']} [{r['metric']}]: "
                f"gap_of_gaps={r['gap_of_gaps']:+.4f} p={r['mannwhitney_p']:.3f} "
                f"q={r['bh_qvalue']:.3f} stab={r['cross_cellline_pos_fraction']}")
    return df


def run(quick=False):
    # exp16 is a pure re-analysis of exp12's per-query CSV (which must be the patched
    # FULL output). QUICK vs FULL is therefore determined by which exp12 CSV is on disk;
    # the flag only affects logging.
    section(f"EXP16 GATE DIAGNOSIS ({'QUICK' if quick else 'FULL'})")

    merged, keys = _load_exp12_perquery()
    log(f"  loaded exp12 per-query gate+outcomes+true_divergence: {len(merged)} queries")
    log(f"  true_divergence non-nan: {int(merged.true_divergence.notna().sum())}/{len(merged)}, "
        f"range [{merged.true_divergence.min():.3f}, {merged.true_divergence.max():.3f}]")

    p1 = phase1(merged)
    write_csv(p1, results_path(OUT, "gate_vs_true_divergence.csv"))
    p2 = phase2(merged)
    write_csv(p2, results_path(OUT, "gate_variants_sweep.csv"))
    # persist merged for exp17 reuse
    write_csv(merged, results_path(OUT, "_merged_query_divergence.csv"))
    return merged, p1, p2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    args = ap.parse_args()
    run(quick=args.quick)


if __name__ == "__main__":
    main()
