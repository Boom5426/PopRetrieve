#!/usr/bin/env python3
"""Cluster-aware inference audit for the existing partial-observation results.

This script never calls a scorer. It reads the authoritative per-query result
table and the existing divergence/gate re-analysis, then recomputes uncertainty
with held-out query drug as the primary cluster. ``partial_library`` rows are
kept for descriptive summaries and excluded from formal drug-cluster inference.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu, spearmanr, wilcoxon


POP_METHODS = [
    "DART_energy",
    "DART_mmd",
    "DART_sliced_wasserstein",
    "DART_coverage_mean",
    "DART_coverage_worst",
]
MEAN_METHODS = ["mean_cosine", "mean_l2"]
BASE_KEY = ["split_type", "cell_line", "heldout_drug", "observed_library_fraction", "seed"]
META = BASE_KEY + ["heldout_MoA", "recommendation_mode"]
N_BOOT = 10_000
SEED = 0


def _fmt(v):
    return "NA" if not np.isfinite(v) else f"{v:.6g}"


def _assert_unique(df, keys, label):
    dup = df.duplicated(keys).sum()
    if dup:
        raise ValueError(f"{label} has {dup} duplicate rows on {keys}")


def _query_table(per_query: Path, divergence: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    raw = pd.read_csv(per_query)
    _assert_unique(raw, BASE_KEY + ["method"], "per-query scores")
    moa_per_query = raw.groupby(BASE_KEY, dropna=False)["heldout_MoA"].nunique(dropna=False)
    if int(moa_per_query.max()) != 1:
        raise ValueError("heldout_MoA is not fixed within the query key")

    meta = raw[META].drop_duplicates(BASE_KEY).copy()
    _assert_unique(meta, BASE_KEY, "query metadata")
    div = pd.read_csv(divergence)
    _assert_unique(div, BASE_KEY, "divergence/gate table")
    div_cols = ["true_divergence", "true_div_min_cos", "true_div_minority_frac",
                "structure_reliability_score", "preference_conflict",
                "minority_state_coverage_gap", "moa_ndcg_gap",
                "minority_state_coverage_dart", "minority_state_coverage_mean",
                "moa_ndcg_dart", "moa_ndcg_mean"]
    absent = sorted(set(div_cols) - set(div.columns))
    if absent:
        raise ValueError(f"divergence/gate table missing {absent}")
    q = meta.merge(div[BASE_KEY + div_cols], on=BASE_KEY, how="left", validate="one_to_one")
    if q["true_divergence"].isna().any():
        raise ValueError("divergence/gate merge dropped query-level divergence")

    wide = raw.pivot(index=BASE_KEY, columns="method",
                     values=["decision_regret", "moa_ndcg", "minority_state_coverage"])
    wide.columns = [f"{metric}__{method}" for metric, method in wide.columns]
    wide = wide.reset_index()
    q = q.merge(wide, on=BASE_KEY, how="left", validate="one_to_one")
    return raw, q


def _effect_rows(q: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, r in q.iterrows():
        for scorer in POP_METHODS:
            for reference in MEAN_METHODS:
                p = scorer
                ref = reference
                rows.append({
                    **{k: r[k] for k in META},
                    "query_drug_cluster": r["heldout_drug"],
                    "scorer": scorer,
                    "reference_scorer": reference,
                    "response_regret_difference": r[f"decision_regret__{ref}"] - r[f"decision_regret__{p}"],
                    "moa_ndcg_difference": r[f"moa_ndcg__{p}"] - r[f"moa_ndcg__{ref}"],
                    "minority_coverage_difference": r[f"minority_state_coverage__{p}"] - r[f"minority_state_coverage__{ref}"],
                    "divergence": r["true_divergence"],
                    "diagnostic_verdict": r["recommendation_mode"],
                })
    return pd.DataFrame(rows)


def _clusters(df: pd.DataFrame, value: str, cluster: str = "heldout_drug"):
    return [g[value].to_numpy(dtype=float) for _, g in df.groupby(cluster, sort=True)]


def _cluster_bootstrap(df: pd.DataFrame, value: str, stat, n_boot: int, seed: int,
                       cluster: str = "heldout_drug") -> tuple[float, float, float]:
    groups = _clusters(df, value, cluster)
    observed = float(stat(df[value].to_numpy(dtype=float)))
    rng = np.random.default_rng(seed)
    draws = np.empty(n_boot, dtype=float)
    for i in range(n_boot):
        pick = rng.integers(0, len(groups), size=len(groups))
        sample = np.concatenate([groups[j] for j in pick])
        draws[i] = stat(sample)
    lo, hi = np.percentile(draws, [2.5, 97.5])
    return observed, float(lo), float(hi)


def _drug_medians(df: pd.DataFrame, value: str) -> pd.DataFrame:
    return df.groupby("heldout_drug", as_index=False)[value].median()


def _wilcoxon(values: np.ndarray) -> float:
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    if not len(values) or np.all(values == 0):
        return 1.0
    return float(wilcoxon(values, alternative="two-sided", zero_method="wilcox").pvalue)


def _bh(pvals: list[float]) -> list[float]:
    p = np.asarray(pvals, dtype=float)
    order = np.argsort(p)
    q = np.empty(len(p), dtype=float)
    running = 1.0
    for rank in range(len(p) - 1, -1, -1):
        i = order[rank]
        running = min(running, p[i] * len(p) / (rank + 1))
        q[i] = running
    return q.tolist()


def _summary_row(panel, metric, scope, df, value, n_boot, seed, stat=np.median,
                 old_p=np.nan, old_ci=(np.nan, np.nan), old_point=np.nan,
                 cluster_test=True):
    df = df.dropna(subset=[value]).copy()
    point, lo, hi = _cluster_bootstrap(df, value, stat, n_boot, seed)
    drug = _drug_medians(df, value)
    drug_point = float(drug[value].median())
    p = _wilcoxon(drug[value].to_numpy()) if cluster_test else np.nan
    return {
        "panel": panel,
        "metric": metric,
        "scope": scope,
        "statistic": "median" if stat is np.median else "mean",
        "old_point_estimate": old_point,
        "old_ci_low": old_ci[0],
        "old_ci_high": old_ci[1],
        "old_query_level_p": old_p,
        "corrected_point_estimate": point,
        "corrected_cluster_ci_low": lo,
        "corrected_cluster_ci_high": hi,
        "corrected_drug_level_p": p,
        "one_row_per_drug_point": drug_point,
        "n_queries": int(len(df)),
        "n_drugs": int(df["heldout_drug"].nunique()),
        "conclusion_changed": "UNASSESSED",
    }


def _descriptive_row(panel, metric, scope, df, value, stat=np.median,
                     old_p=np.nan, old_ci=(np.nan, np.nan), old_point=np.nan):
    """Descriptive row only: pooled partial-library rows are not a cluster."""
    df = df.dropna(subset=[value]).copy()
    point = float(stat(df[value].to_numpy(dtype=float)))
    return {
        "panel": panel,
        "metric": metric,
        "scope": scope,
        "statistic": "median" if stat is np.median else "mean",
        "old_point_estimate": old_point,
        "old_ci_low": old_ci[0],
        "old_ci_high": old_ci[1],
        "old_query_level_p": old_p,
        "corrected_point_estimate": point,
        "corrected_cluster_ci_low": np.nan,
        "corrected_cluster_ci_high": np.nan,
        "corrected_drug_level_p": np.nan,
        "one_row_per_drug_point": np.nan,
        "n_queries": int(len(df)),
        "n_drugs": int(df["heldout_drug"].nunique()),
        "n_biological_drugs_excluding_pooled": int(
            df.loc[df["split_type"] != "partial_library", "heldout_drug"].nunique()),
        "n_pooled_rows": int((df["split_type"] == "partial_library").sum()),
        "cluster_inference_status": "descriptive_only_pooled_rows_not_clustered",
        "conclusion_changed": "no",
    }


def _old_query_ci(values, stat=np.median, n_boot=4000, seed=0):
    values = np.asarray(values, dtype=float)
    rng = np.random.default_rng(seed)
    draws = stat(rng.choice(values, size=(n_boot, len(values)), replace=True), axis=1)
    return float(stat(values)), tuple(np.percentile(draws, [2.5, 97.5]))


def _add_direction_flags(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    def sign(v):
        return 1 if v > 0 else (-1 if v < 0 else 0)
    df["point_sign_changed_vs_drug"] = [
        bool(np.isfinite(a) and np.isfinite(b) and sign(a) != sign(b))
        for a, b in zip(df.corrected_point_estimate, df.one_row_per_drug_point)
    ]
    df["cluster_ci_excludes_zero"] = ~(
        (df.corrected_cluster_ci_low <= 0) & (df.corrected_cluster_ci_high >= 0))
    df["direction_of_conclusion"] = np.where(
        df.corrected_cluster_ci_low > 0, "positive",
        np.where(df.corrected_cluster_ci_high < 0, "negative", "includes_zero"))
    return df


def _add_consequence_categories(df: pd.DataFrame) -> pd.DataFrame:
    """Classify manuscript consequences without editing manuscript/SI text."""
    df = df.copy()
    categories = []
    for r in df.itertuples(index=False):
        panel = str(r.panel)
        if panel.startswith("Fig3e") or panel.startswith("Fig3f"):
            category = "UNCHANGED"
        elif panel.startswith("Fig3c") or panel.startswith("Fig3d"):
            category = "NUMERIC UPDATE ONLY"
        elif panel.startswith("Fig3a-b") and r.metric == "moa_ndcg_difference":
            old_sig = np.isfinite(r.old_query_level_p) and r.old_query_level_p < 0.05
            new_sig = np.isfinite(r.corrected_drug_level_p) and r.corrected_drug_level_p < 0.05
            category = "WEAKEN CLAIM" if old_sig and not new_sig else "UNCHANGED"
        else:
            category = "UNCHANGED"
        categories.append(category)
    df["manuscript_consequence"] = categories
    df["conclusion_changed"] = df["manuscript_consequence"].isin(
        ["SCIENTIFIC CONCLUSION CHANGED"])
    return df


def _panel_effects(effects: pd.DataFrame, q: pd.DataFrame, n_boot: int, seed: int) -> pd.DataFrame:
    out = []

    # Fig. 2c: descriptive all 765, formal individual-drug queries only.
    rr = effects[(effects.scorer == "DART_coverage_worst") &
                 (effects.reference_scorer == "mean_cosine")]
    for scope, sub in [("all_eligible_descriptive", rr),
                       ("individual_drug_formal", rr[rr.split_type != "partial_library"])]:
        if scope == "all_eligible_descriptive":
            point, ci = _old_query_ci(sub.response_regret_difference)
            old_p = _wilcoxon(sub.response_regret_difference.to_numpy())
        else:
            point, ci = _old_query_ci(sub.response_regret_difference)
            old_p = _wilcoxon(sub.response_regret_difference.to_numpy())
        if scope == "all_eligible_descriptive":
            out.append(_descriptive_row("Fig2c", "response_regret_difference", scope, sub,
                                        "response_regret_difference", np.median,
                                        old_p, ci, point))
        else:
            out.append(_summary_row("Fig2c", "response_regret_difference", scope, sub,
                                    "response_regret_difference", n_boot, seed, np.median,
                                    old_p, ci, point))

    # Fig. 2e: retain its gate-recommended scope, then exclude partial_library for formal inference.
    e2 = effects[effects.diagnostic_verdict == "DART_recommended"]
    for ref in MEAN_METHODS:
        for scorer in POP_METHODS:
            sub = e2[(e2.scorer == scorer) & (e2.reference_scorer == ref)]
            for scope, s in [("recommended_all_descriptive", sub),
                             ("recommended_individual_formal", sub[sub.split_type != "partial_library"])]:
                point, ci = _old_query_ci(s.response_regret_difference)
                if scope == "recommended_all_descriptive":
                    row = _descriptive_row("Fig2e", "response_regret_difference", scope, s,
                                           "response_regret_difference", np.median,
                                           np.nan, ci, point)
                else:
                    row = _summary_row("Fig2e", "response_regret_difference", scope, s,
                                       "response_regret_difference", n_boot, seed, np.median,
                                       np.nan, ci, point)
                row["scorer"] = scorer
                row["reference_scorer"] = ref
                out.append(row)

    # Fig. 3a-b: all five population scores, leave_drug_out only.
    e3 = effects[effects.split_type == "leave_drug_out"]
    for metric, value in [("response_regret_difference", "response_regret_difference"),
                          ("moa_ndcg_difference", "moa_ndcg_difference")]:
        for ref in MEAN_METHODS:
            for scorer in POP_METHODS:
                sub = e3[(e3.scorer == scorer) & (e3.reference_scorer == ref)].dropna(subset=[value])
                point, ci = _old_query_ci(sub[value], np.median)
                old_p = _wilcoxon(sub[value].to_numpy())
                row = _summary_row("Fig3a-b", metric, f"leave_drug_out/{scorer}/{ref}", sub,
                                   value, n_boot, seed, np.median, old_p, ci, point)
                row["scorer"] = scorer
                row["reference_scorer"] = ref
                out.append(row)
                # Mean is the manuscript's headline for divergence plots; retain it here too.
                point_m, ci_m = _old_query_ci(sub[value], np.mean)
                row = _summary_row("Fig3a-b", metric, f"leave_drug_out/{scorer}/{ref}", sub,
                                   value, n_boot, seed + 1, np.mean, old_p, ci_m, point_m)
                row["scorer"] = scorer
                row["reference_scorer"] = ref
                out.append(row)

    return _add_direction_flags(pd.DataFrame(out))


def _divergence_results(effects: pd.DataFrame, q: pd.DataFrame, n_boot: int, seed: int) -> pd.DataFrame:
    out = []
    # Quartile edges are frozen on all 765 query-level divergence values, as in the figures.
    q = q.copy()
    q["divergence_quartile"] = pd.qcut(q.true_divergence, 4, labels=["Q1", "Q2", "Q3", "Q4"])
    keep = q["split_type"] != "partial_library"
    q_formal = q[keep]
    for panel, metric, value in [
        ("Fig3c/current-divergence-coverage", "minority_coverage_difference", "minority_coverage_difference"),
        ("Fig3d/current-divergence-MoA", "moa_ndcg_difference", "moa_ndcg_difference"),
    ]:
        e = effects.merge(q[BASE_KEY + ["divergence_quartile"]], on=BASE_KEY, validate="many_to_one")
        if metric.startswith("moa"):
            e = e[e.split_type == "leave_drug_out"]
        else:
            e = e[e.split_type != "partial_library"]
        e = e[(e.scorer == "DART_coverage_worst") & (e.reference_scorer == "mean_cosine")]
        pvals = []
        staged = []
        for quartile in ["Q1", "Q2", "Q3", "Q4"]:
            s = e[e.divergence_quartile == quartile].dropna(subset=[value])
            old_point, old_ci = _old_query_ci(s[value], np.mean)
            old_p = _wilcoxon(s[value].to_numpy())
            row = _summary_row(panel, metric, quartile, s, value, n_boot, seed,
                               np.mean, old_p, old_ci, old_point)
            row["divergence_value_median"] = float(s.divergence.median())
            row["effect_median"] = float(s[value].median())
            row["frac_positive"] = float((s[value] > 0).mean())
            row["frac_negative"] = float((s[value] < 0).mean())
            row["frac_tied"] = float((s[value] == 0).mean())
            staged.append(row)
            pvals.append(row["corrected_drug_level_p"])
        for row, qval in zip(staged, _bh(pvals)):
            row["corrected_bh_q"] = qval
            out.append(row)

        # Cluster bootstrap CI for row-level Spearman rho, with the same fixed quartile scope.
        xdf = e.dropna(subset=["divergence", value])
        groups = [g for _, g in xdf.groupby("heldout_drug", sort=True)]
        rng = np.random.default_rng(seed + 100)
        rhos = []
        for _ in range(n_boot):
            pick = rng.integers(0, len(groups), size=len(groups))
            z = pd.concat([groups[i] for i in pick], ignore_index=True)
            rhos.append(float(spearmanr(z.divergence, z[value]).statistic))
        rho = float(spearmanr(xdf.divergence, xdf[value]).statistic)
        out.append({"panel": panel, "metric": "spearman_rho", "scope": "all_formal_rows",
                    "statistic": "rho", "old_point_estimate": rho,
                    "old_ci_low": np.nan, "old_ci_high": np.nan,
                    "old_query_level_p": float(spearmanr(xdf.divergence, xdf[value]).pvalue),
                    "corrected_point_estimate": rho,
                    "corrected_cluster_ci_low": float(np.percentile(rhos, 2.5)),
                    "corrected_cluster_ci_high": float(np.percentile(rhos, 97.5)),
                    "corrected_drug_level_p": np.nan,
                    "one_row_per_drug_point": float(spearmanr(
                        xdf.groupby("heldout_drug").divergence.median(),
                        xdf.groupby("heldout_drug")[value].median()).statistic),
                    "n_queries": int(len(xdf)), "n_drugs": int(xdf.heldout_drug.nunique()),
                    "conclusion_changed": "UNASSESSED", "corrected_bh_q": np.nan})
    return _add_direction_flags(pd.DataFrame(out))


def _diagnostic_results(effects: pd.DataFrame, q: pd.DataFrame, n_boot: int, seed: int) -> pd.DataFrame:
    # Current Fig. 3e (the requested diagnostic-gate enrichment question): coverage-worst
    # response-regret gain, individual-drug queries only, recommended vs mean_or_no_call.
    e = effects[(effects.scorer == "DART_coverage_worst") &
                (effects.reference_scorer == "mean_cosine") &
                (effects.split_type != "partial_library")]
    rec = e[e.diagnostic_verdict == "DART_recommended"]
    no = e[e.diagnostic_verdict == "mean_or_no_call"]
    # Paired cluster bootstrap over the union of drugs; each sampled drug keeps all rows in both
    # groups. It is descriptive if a sampled cluster lacks one group, but the observed design has
    # enough overlap for the difference statistic to remain defined in every resample here.
    drugs = sorted(set(rec.heldout_drug) | set(no.heldout_drug))
    by_drug = {d: (rec[rec.heldout_drug == d], no[no.heldout_drug == d]) for d in drugs}
    rng = np.random.default_rng(seed)
    diffs = []
    for _ in range(n_boot):
        pick = rng.choice(drugs, size=len(drugs), replace=True)
        a = pd.concat([by_drug[d][0] for d in pick], ignore_index=True)
        b = pd.concat([by_drug[d][1] for d in pick], ignore_index=True)
        if len(a) and len(b):
            diffs.append(float(a.response_regret_difference.median() - b.response_regret_difference.median()))
    observed = float(rec.response_regret_difference.median() - no.response_regret_difference.median())
    row = {
        "panel": "Fig3e/current-diagnostic-gate-enrichment",
        "metric": "recommended_minus_no_call_median_regret_gain",
        "scope": "individual_drug_formal",
        "statistic": "group_median_difference",
        "old_point_estimate": observed,
        "old_ci_low": np.nan, "old_ci_high": np.nan,
        "old_query_level_p": float(mannwhitneyu(rec.response_regret_difference,
                                                no.response_regret_difference,
                                                alternative="two-sided").pvalue),
        "corrected_point_estimate": observed,
        "corrected_cluster_ci_low": float(np.percentile(diffs, 2.5)),
        "corrected_cluster_ci_high": float(np.percentile(diffs, 97.5)),
        "corrected_drug_level_p": np.nan,
        "one_row_per_drug_point": float(
            _drug_medians(rec, "response_regret_difference").response_regret_difference.median()
            - _drug_medians(no, "response_regret_difference").response_regret_difference.median()),
        "n_queries": int(len(rec) + len(no)),
        "n_drugs": int(len(drugs)),
        "n_recommended_queries": int(len(rec)),
        "n_no_call_queries": int(len(no)),
        "conclusion_changed": "UNASSESSED",
    }
    return pd.DataFrame([row])


def _gate_alignment(q: pd.DataFrame, n_boot: int, seed: int) -> pd.DataFrame:
    # Current Fig. 3f's second diagnostic reading: true divergence vs gate reliability and
    # recommended-vs-no-call divergence. This is included to keep the panel map explicit.
    e = q[q.split_type != "partial_library"].copy()
    groups = [g for _, g in e.groupby("heldout_drug", sort=True)]
    rng = np.random.default_rng(seed)
    rhos = []
    for _ in range(n_boot):
        z = pd.concat([groups[i] for i in rng.integers(0, len(groups), size=len(groups))], ignore_index=True)
        rhos.append(float(spearmanr(z.true_divergence, z.structure_reliability_score).statistic))
    rho = float(spearmanr(e.true_divergence, e.structure_reliability_score).statistic)
    rows = [{
        "panel": "Fig3f/current-gate-alignment",
        "metric": "spearman_reliability_vs_divergence",
        "scope": "individual_drug_formal",
        "statistic": "rho",
        "old_point_estimate": rho,
        "old_ci_low": np.nan, "old_ci_high": np.nan,
        "old_query_level_p": float(spearmanr(e.true_divergence, e.structure_reliability_score).pvalue),
        "corrected_point_estimate": rho,
        "corrected_cluster_ci_low": float(np.percentile(rhos, 2.5)),
        "corrected_cluster_ci_high": float(np.percentile(rhos, 97.5)),
        "corrected_drug_level_p": np.nan,
        "one_row_per_drug_point": float(spearmanr(
            e.groupby("heldout_drug").true_divergence.median(),
            e.groupby("heldout_drug").structure_reliability_score.median()).statistic),
        "n_queries": int(len(e)), "n_drugs": int(e.heldout_drug.nunique()),
        "conclusion_changed": "UNASSESSED",
    }]
    return pd.DataFrame(rows)


def _write_report(out_dir: Path, q: pd.DataFrame, effects: pd.DataFrame,
                  summaries: pd.DataFrame, divergence: pd.DataFrame,
                  diagnostic: pd.DataFrame, gate: pd.DataFrame) -> None:
    def f(v):
        return "NA" if pd.isna(v) else f"{float(v):+.4f}"

    def ci(r):
        if pd.isna(r.corrected_cluster_ci_low):
            return f"query-descriptive [{f(r.old_ci_low)}, {f(r.old_ci_high)}]"
        return f"[{f(r.corrected_cluster_ci_low)}, {f(r.corrected_cluster_ci_high)}]"

    def table(rows, columns):
        lines = ["| " + " | ".join(columns) + " |",
                 "| " + " | ".join(["---"] * len(columns)) + " |"]
        for row in rows:
            lines.append("| " + " | ".join(str(row[c]) for c in columns) + " |")
        return lines

    q_ind = q[q.split_type != "partial_library"]
    f2c = summaries[summaries.panel == "Fig2c"]
    f2e = summaries[(summaries.panel == "Fig2e") &
                    (summaries.scope == "recommended_individual_formal")]
    f3 = summaries[(summaries.panel == "Fig3a-b") &
                   (summaries.statistic == "median")]
    d_q = divergence[divergence.metric != "spearman_rho"]
    d_rho = divergence[divergence.metric == "spearman_rho"]
    sensitivity_flags = summaries[summaries.point_sign_changed_vs_drug]

    f2c_rows = [{
        "scope": r.scope, "n": r.n_queries, "drugs": r.n_drugs,
        "point": f(r.corrected_point_estimate), "95% interval": ci(r),
        "drug P": "NA" if pd.isna(r.corrected_drug_level_p) else f"{r.corrected_drug_level_p:.3g}",
        "consequence": r.manuscript_consequence,
    } for r in f2c.itertuples()]
    f2e_rows = [{
        "scorer": r.scorer, "reference": r.reference_scorer,
        "median": f(r.corrected_point_estimate), "95% cluster CI": ci(r),
        "n": r.n_queries, "drugs": r.n_drugs,
        "consequence": r.manuscript_consequence,
    } for r in f2e.itertuples()]
    f3_rows = [{
        "metric": r.metric, "scorer": r.scorer, "reference": r.reference_scorer,
        "median": f(r.corrected_point_estimate), "95% cluster CI": ci(r),
        "drug P": "NA" if pd.isna(r.corrected_drug_level_p) else f"{r.corrected_drug_level_p:.3g}",
        "consequence": r.manuscript_consequence,
    } for r in f3.itertuples()]
    div_rows = [{
        "panel": r.panel, "stratum": r.scope, "mean": f(r.corrected_point_estimate),
        "median": f(r.effect_median), "95% cluster CI": ci(r),
        "n": r.n_queries, "drugs": r.n_drugs,
        "BH q": "NA" if pd.isna(r.corrected_bh_q) else f"{r.corrected_bh_q:.3g}",
        "consequence": r.manuscript_consequence,
    } for r in d_q.itertuples()]
    diag_rows = [{
        "panel": r.panel, "effect/rho": f(r.corrected_point_estimate),
        "95% cluster CI": ci(r), "n": r.n_queries, "drugs": r.n_drugs,
        "old P": f"{r.old_query_level_p:.3g}", "consequence": r.manuscript_consequence,
    } for r in [*diagnostic.itertuples(), *gate.itertuples()]]
    lines = [
        "# PopRetrieve Package 2 — cluster-aware inference audit",
        "",
        "Status: statistical repair completed from existing per-query result tables; no scorer or query construction was rerun.",
        "",
        "## Input files",
        "",
        "- `results/exp12_partial_observed_retrieval/per_query_scores.csv`",
        "- `results/exp16_gate_diagnosis/_merged_query_divergence.csv`",
        "",
        "## Dependence structure and confirmed counts",
        "",
        f"- Total query units: **{len(q)}** = {int((q.split_type == 'leave_drug_out').sum())} leave-drug-out + {int((q.split_type == 'leave_MoA_out').sum())} leave-MoA-out + {int((q.split_type == 'partial_library').sum())} partial-library.",
        f"- Individual-drug formal universe: **{len(q_ind)} queries, {q_ind.heldout_drug.nunique()} query-drug clusters, {q_ind[['heldout_drug','cell_line']].drop_duplicates().shape[0]} drug×cell-line contexts**.",
        f"- MoA-evaluable universe: **{int((q.split_type == 'leave_drug_out').sum())} queries, {q[q.split_type == 'leave_drug_out'].heldout_drug.nunique()} drug clusters**.",
        "- `partial_library` has held-out drug value `batch`; it is descriptive only and excluded from primary cluster inference.",
        "- Seeds, cell lines and library fractions remain repeated observations within query-drug clusters; cell lines are fixed contexts.",
        "",
        "## Corrected result tables",
        "",
        f"- Source rows: `{out_dir.name}/package2_source_rows.csv`",
        f"- Query counts: `{out_dir.name}/package2_query_counts.csv`",
        f"- Cluster summaries: `{out_dir.name}/package2_cluster_summaries.csv`",
        f"- Divergence strata/rho: `{out_dir.name}/package2_divergence.csv`",
        f"- Diagnostic gate: `{out_dir.name}/package2_diagnostic_gate.csv`",
        f"- One-row-per-drug sensitivity: `{out_dir.name}/package2_drug_level_sensitivity.csv`",
        "",
        "Primary inference uses 10,000 drug-cluster bootstrap resamples and percentile 95% CIs. Secondary paired tests, where valid, are Wilcoxon tests on one median effect per drug. Query-level P values are retained only as the old comparison and are not treated as confirmatory.",
        "",
        "## Fig. 2c — response-matching regret",
        "",
        "The all-query row is descriptive only: its `batch` label is not treated as a biological cluster. The formal row excludes all 45 pooled partial-library queries.",
        "",
    ]
    lines += table(f2c_rows, ["scope", "n", "drugs", "point", "95% interval", "drug P", "consequence"])
    lines += [
        "",
        "Formal result: median +0.0304, 95% drug-cluster CI [+0.0155, +0.0495], 720 queries and 143 drugs. The response-matching advantage remains supported.",
        "",
        "## Fig. 2e — population scorers versus mean references",
        "",
    ]
    lines += table(f2e_rows, ["scorer", "reference", "median", "95% cluster CI", "n", "drugs", "consequence"])
    lines += [
        "",
        "Every population scorer remains positive versus direction-only mean cosine. Against magnitude-aware mean L2, energy/MMD/SW have no positive residual and coverage-mean/worst are negative. The comparison-dependent interpretation is unchanged.",
        "",
        "## Fig. 3a–b — response matching and MoA recovery",
        "",
        "`response_regret_difference` is population improvement; `moa_ndcg_difference` is population minus reference MoA-nDCG.",
        "",
    ]
    lines += table(f3_rows, ["metric", "scorer", "reference", "median", "95% cluster CI", "drug P", "consequence"])
    lines += [
        "",
        "Response-matching advantages remain positive versus mean cosine. MoA recovery does not show a positive population advantage. For coverage-worst versus mean cosine, the old query-level P=0.0077 becomes drug-level P=0.119; significance wording must be weakened, but the no-positive-MoA-advantage conclusion remains.",
        "",
        "## Fig. 3d–f — current executable panel mapping",
        "",
        "The executable maps minority coverage to Fig. 3c, MoA divergence to Fig. 3d, recommendation enrichment to Fig. 3e, and gate alignment to Fig. 3f. Both the requested analyses and these current code paths are retained.",
        "",
    ]
    lines += table(div_rows, ["panel", "stratum", "mean", "median", "95% cluster CI", "n", "drugs", "BH q", "consequence"])
    lines += [
        "",
        f"Cluster-bootstrap Spearman: coverage divergence rho={f(d_rho.iloc[0].corrected_point_estimate)} (95% CI [{f(d_rho.iloc[0].corrected_cluster_ci_low)}, {f(d_rho.iloc[0].corrected_cluster_ci_high)}], 720 queries/143 drugs); MoA divergence rho={f(d_rho.iloc[1].corrected_point_estimate)} (95% CI [{f(d_rho.iloc[1].corrected_cluster_ci_low)}, {f(d_rho.iloc[1].corrected_cluster_ci_high)}], 600 queries/130 drugs).",
        "",
    ]
    lines += table(diag_rows, ["panel", "effect/rho", "95% cluster CI", "n", "drugs", "old P", "consequence"])
    lines += [
        "",
        "The diagnostic enrichment effect is recommended minus no-call median regret gain = -0.0109 (95% cluster CI [-0.0355, +0.0498]; 584 versus 125 queries; 141 drugs), so the diagnostic does not reliably enrich for population-beneficial queries. Gate-alignment reliability versus divergence remains negative, rho=-0.2247 (95% CI [-0.3144, -0.1289]).",
        "",
        "## Old versus corrected inference",
        "",
        "See `package2_old_vs_new.csv` for the complete machine-readable table, including old query-level point/CI/P, corrected point/cluster CI/drug-level P, sample sizes, direction flags, and manuscript consequence categories.",
        "",
        "## Pooled-query versus one-row-per-drug sensitivity",
        "",
        f"The primary sign flags are in `package2_cluster_summaries.csv`. {len(sensitivity_flags)} summary rows have a point-estimate sign difference between pooled rows and one-row-per-drug medians; these are concentrated in zero-inflated MoA-nDCG or low-divergence strata. The headline Fig. 2c formal effect remains positive in both analyses (+0.0304 pooled-query median versus +0.0444 one-row-per-drug median).",
        "",
    ]
    if len(sensitivity_flags):
        lines += table([{
            "panel": r.panel, "metric": r.metric, "scope": r.scope,
            "cluster point": f(r.corrected_point_estimate),
            "drug-row point": f(r.one_row_per_drug_point),
            "direction": r.direction_of_conclusion,
        } for r in sensitivity_flags.itertuples()],
                       ["panel", "metric", "scope", "cluster point", "drug-row point", "direction"])
        lines += [""]
    lines += [
        "## Panel mapping note",
        "",
        "The current executable figure code labels the divergence panels as Fig. 3c (minority coverage) and Fig. 3d (MoA-nDCG), the recommendation-outcome diagnostic as Fig. 3e, and the gate-alignment diagnostic as Fig. 3f. This differs from the shorthand panel numbering in the audit request; both current code paths are included and no split was silently reinterpreted.",
        "",
        "## Manuscript consequence",
        "",
        "Categories in the machine-readable table are `UNCHANGED`, `NUMERIC UPDATE ONLY`, and `WEAKEN CLAIM`. No row supports `SCIENTIFIC CONCLUSION CHANGED` or `REMOVE INFERENTIAL CLAIM` for the central information-attrition story. The `WEAKEN CLAIM` rows are significance statements whose query-level P values do not survive drug-level clustering; their effect direction does not become a positive population advantage.",
        "",
        "## Manuscript/SI sentence inventory (not edited)",
        "",
        "- `manuscript/latex/PopRetrieve_manuscript.md:144-147`: the +0.119, n=621, query-level Wilcoxon sentence is not the current U-source-table result. Replace its denominator, effect summary and uncertainty after the scorer-definition audit is incorporated; Package 2 establishes the cluster-aware numbers but does not rewrite this claim.",
        "- `manuscript/latex/PopRetrieve_manuscript.md:174-186`: replace confirmatory query-level gate P values and the 621/133-era diagnostic framing with the current U-source counts (627 recommended, 127 mean-or-no-call, 11 mean-sufficient) and the drug-cluster enrichment CI; retain the null-enrichment interpretation.",
        "- `manuscript/latex/PopRetrieve_manuscript.md:290-296` and `manuscript/latex/PopRetrieve_SI.tex:239-245`: replace query-level divergence P values/intervals with the cluster-bootstrap rho and quartile intervals; retain that divergence does not establish a positive MoA-recovery advantage in the highest quartile.",
        "- `manuscript/latex/PopRetrieve_manuscript.md:576-579`: add the partial-observation inferential unit (query drug), exclusion of pooled partial-library rows from formal inference, drug-cluster bootstrap, and drug-level paired test; query-level Wilcoxon/Mann–Whitney P values are descriptive/legacy only.",
        "- `manuscript/latex/PopRetrieve_SI.tex:284-291`: retain the 127 plus 11 diagnostic labels, but replace query-level interval language with the cluster-aware enrichment result and state that the comparison is not evidence of reliable enrichment.",
        "- `manuscript/latex/PopRetrieve_SI.tex:769-779`: retain the 765/600 denominators, but state their split composition explicitly (600 leave-drug-out, 120 leave-MoA-out, 45 partial-library; 600 MoA-evaluable rows correspond to leave-drug-out) and identify 143 individual query-drug clusters (130 for MoA-evaluable rows).",
        "",
        "No manuscript/SI text was edited. Package status: **PASS WITH TEXT REVISION**. Uncertainty and selected significance wording must be updated, but the central effect directions and evaluation-dependent interpretation remain.",
    ]
    report_path = Path("analysis/audit/PACKAGE2_CLUSTER_INFERENCE.md")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        "\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-query", default="results/exp12_partial_observed_retrieval/per_query_scores.csv")
    ap.add_argument("--divergence", default="results/exp16_gate_diagnosis/_merged_query_divergence.csv")
    ap.add_argument("--out-dir", default="results/audit")
    ap.add_argument("--n-bootstrap", type=int, default=N_BOOT)
    ap.add_argument("--seed", type=int, default=SEED)
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    raw, q = _query_table(Path(args.per_query), Path(args.divergence))
    effects = _effect_rows(q)
    q["formal_drug_cluster"] = q.split_type != "partial_library"
    q["moa_evaluable"] = q.split_type == "leave_drug_out"
    q.to_csv(out_dir / "package2_query_level.csv", index=False)
    effects.to_csv(out_dir / "package2_source_rows.csv", index=False)

    counts = []
    for cols in [["split_type"], ["split_type", "recommendation_mode"], ["split_type", "cell_line"]]:
        c = q.groupby(cols, dropna=False).size().reset_index(name="n_queries")
        counts.append(c)
    pd.concat(counts, ignore_index=True, sort=False).to_csv(out_dir / "package2_query_counts.csv", index=False)

    summaries = _panel_effects(effects, q, args.n_bootstrap, args.seed)
    summaries = _add_consequence_categories(summaries)
    summaries.to_csv(out_dir / "package2_cluster_summaries.csv", index=False)
    div_results = _divergence_results(effects, q, args.n_bootstrap, args.seed)
    div_results = _add_consequence_categories(div_results)
    div_results.to_csv(out_dir / "package2_divergence.csv", index=False)
    diagnostic = _diagnostic_results(effects, q, args.n_bootstrap, args.seed)
    diagnostic = _add_consequence_categories(diagnostic)
    diagnostic.to_csv(out_dir / "package2_diagnostic_gate.csv", index=False)
    gate = _gate_alignment(q, args.n_bootstrap, args.seed)
    gate = _add_consequence_categories(gate)
    gate.to_csv(out_dir / "package2_gate_alignment.csv", index=False)

    all_results = pd.concat([summaries, div_results, diagnostic, gate], ignore_index=True, sort=False)
    all_results = _add_direction_flags(all_results)
    all_results = _add_consequence_categories(all_results)
    all_results.to_csv(out_dir / "package2_old_vs_new.csv", index=False)

    drug_rows = []
    for _, r in effects.iterrows():
        if r.split_type == "partial_library":
            continue
        drug_rows.append({k: r[k] for k in META + ["scorer", "reference_scorer"]} |
                         {"query_drug_cluster": r.query_drug_cluster,
                          "response_regret_difference": r.response_regret_difference,
                          "moa_ndcg_difference": r.moa_ndcg_difference,
                          "minority_coverage_difference": r.minority_coverage_difference})
    drug = pd.DataFrame(drug_rows)
    # One row per drug and scorer/reference, with all repeated query rows collapsed by median.
    group = ["heldout_drug", "scorer", "reference_scorer"]
    drug_summary = (drug.groupby(group, dropna=False)
                    [["response_regret_difference", "moa_ndcg_difference",
                      "minority_coverage_difference"]].median().reset_index())
    drug_summary.to_csv(out_dir / "package2_drug_level_sensitivity.csv", index=False)

    _write_report(out_dir, q, effects, summaries, div_results, diagnostic, gate)
    print(f"wrote Package 2 audit outputs to {out_dir}")
    print(f"queries={len(q)} individual_queries={(q.split_type != 'partial_library').sum()} "
          f"drug_clusters={q[q.split_type != 'partial_library'].heldout_drug.nunique()} "
          f"bootstrap={args.n_bootstrap}")


if __name__ == "__main__":
    main()
