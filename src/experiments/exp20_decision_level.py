#!/usr/bin/env python
"""Decision-level evaluation of analogue retrieval: how good is the candidate each rule ranks first?

The analogue tasks report agreement of whole rankings. This script reads the existing
per-candidate (GDSC2) and per-query (mechanism of action) scores, checks that they reproduce the
reported ranking-level numbers, and then scores the top-ranked candidate of each rule under the
independent criterion.

    python src/experiments/exp20_decision_level.py \
        --gdsc2 results/exp20_decision_level/inputs/gdsc2_candidate_scores.csv \
        --moa results/exp12_partial_observed_retrieval/per_query_scores.csv \
        --out results/exp20_decision_level
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

N_BOOT = 10_000
BOOT_SEED = 0
TOP_B = 5

# Rule names as the manuscript uses them, mapped to each table's columns.
GDSC2_RULES = {"mean_cosine": "mean_cosine_ctrl", "mean_l2": "mean_l2_ctrl", "energy": "energy"}
MOA_RULES = {"mean_cosine": "mean_cosine", "mean_l2": "mean_l2", "energy": "DART_energy"}
RULE_NAMES = ("mean_cosine", "mean_l2", "energy")
CONTRASTS = (("structure", "energy", "mean_l2"), ("magnitude", "mean_l2", "mean_cosine"))
GDSC2_CRITERIA = {"centred": "functional_similarity",
                  "uncentred": "functional_similarity_uncentered"}

# Reproduction targets. GDSC2: per-query Spearman medians in Supplementary Table 3, taken at full
# precision from the run that produced the table. MoA: the manuscript's mean nDCG@10 differences.
GDSC2_TARGET = {"centred": {"energy": 0.2650401069518717, "mean_l2": 0.2847593582887701,
                            "mean_cosine": 0.08255347593582889},
                "uncentred": {"energy": 0.0902, "mean_l2": 0.0922, "mean_cosine": 0.138}}
GDSC2_TOL = {"centred": 1e-12, "uncentred": 5e-4}      # uncentred targets are printed values
MOA_TARGET = {"magnitude": -0.011, "structure": -0.002}
MOA_TOL = 5e-4


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def cluster_bootstrap(values: np.ndarray, clusters: np.ndarray) -> tuple[float, float]:
    """95% percentile interval of the mean, resampling whole clusters with replacement."""
    rng = np.random.default_rng(BOOT_SEED)
    keys = np.unique(clusters)
    groups = [values[clusters == k] for k in keys]
    sums = np.array([g.sum() for g in groups])
    sizes = np.array([len(g) for g in groups])
    draws = rng.integers(0, len(keys), size=(N_BOOT, len(keys)))
    stats = sums[draws].sum(1) / sizes[draws].sum(1)
    return float(np.percentile(stats, 2.5)), float(np.percentile(stats, 97.5))


def percentile_in_set(crit: np.ndarray) -> np.ndarray:
    """Each candidate's criterion percentile among the other candidates of the same query."""
    n = len(crit)
    lower = (crit[None, :] < crit[:, None]).sum(1)
    equal = (crit[None, :] == crit[:, None]).sum(1) - 1
    return (lower + 0.5 * equal) / (n - 1)


def top_set(score: np.ndarray) -> np.ndarray:
    return np.flatnonzero(score == score.max())


def top1_per_query(cand: pd.DataFrame, query_cols: list[str], candidate_col: str,
                   rules: dict, criteria: dict) -> tuple[pd.DataFrame, dict]:
    """Per query: each rule's ranking agreement, top-1 percentile, top-1 value and top-B percentile."""
    rows, ties = [], {r: 0 for r in rules}
    first_crit = next(iter(criteria))
    for keys, g in cand.groupby(query_cols, sort=True):
        rec = {**dict(zip(query_cols, keys)), "n_candidates": len(g)}
        for crit_name, crit_col in criteria.items():
            crit = g[crit_col].to_numpy()
            pct = percentile_in_set(crit)
            for rule, col in rules.items():
                s = g[col].to_numpy()
                top = top_set(s)
                if crit_name == first_crit and len(top) > 1:
                    ties[rule] += 1
                order = np.argsort(-s, kind="stable")
                rec[f"{rule}_rho_{crit_name}"] = float(spearmanr(s, crit).statistic)
                rec[f"{rule}_top1_pct_{crit_name}"] = float(pct[top].mean())
                rec[f"{rule}_top1_value_{crit_name}"] = float(crit[top].mean())
                rec[f"{rule}_top{TOP_B}_pct_{crit_name}"] = float(pct[order[:TOP_B]].mean())
                if crit_name == first_crit:
                    rec[f"{rule}_top1"] = "|".join(sorted(g[candidate_col].iloc[top]))
        rows.append(rec)
    return pd.DataFrame(rows), ties


def gdsc2_per_query(cand: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    return top1_per_query(cand, ["cell_line", "query_drug"], "candidate_drug", GDSC2_RULES,
                          GDSC2_CRITERIA)


def changed_top1(df: pd.DataFrame, a: str, b: str, value_a: str, value_b: str) -> dict:
    """Among queries where the two rules choose different top-1 candidates, which choice is better."""
    diff = df[f"{a}_top1"] != df[f"{b}_top1"]
    va, vb = df.loc[diff, value_a].to_numpy(), df.loc[diff, value_b].to_numpy()
    return {"n_queries": int(len(df)), "n_changed": int(diff.sum()),
            "first_better": int((va > vb).sum()), "first_worse": int((va < vb).sum()),
            "equal": int((va == vb).sum())}


def summarise(df: pd.DataFrame, cluster_col: str, dataset: str, outcomes: dict) -> list[dict]:
    out = []
    clusters = df[cluster_col].to_numpy()
    for label, fmt in outcomes.items():
        for rule in RULE_NAMES:
            v = df[fmt.format(rule=rule)].to_numpy(dtype=float)
            out.append({"dataset": dataset, "outcome": label, "quantity": rule,
                        "n_queries": len(v), "n_clusters": int(len(np.unique(clusters))),
                        "mean": float(v.mean()), "ci_lo": np.nan, "ci_hi": np.nan})
        for name, a, b in CONTRASTS:
            d = (df[fmt.format(rule=a)] - df[fmt.format(rule=b)]).to_numpy(dtype=float)
            lo, hi = cluster_bootstrap(d, clusters)
            out.append({"dataset": dataset, "outcome": label, "quantity": f"{name} ({a} - {b})",
                        "n_queries": len(d), "n_clusters": int(len(np.unique(clusters))),
                        "mean": float(d.mean()), "ci_lo": lo, "ci_hi": hi})
    return out


def run_gdsc2(path: Path) -> tuple[pd.DataFrame, list[dict], list[dict], dict]:
    cand = pd.read_csv(path)
    pq, ties = gdsc2_per_query(cand)
    repro = {}
    for crit_name, target in GDSC2_TARGET.items():
        for rule, t in target.items():
            got = float(pq[f"{rule}_rho_{crit_name}"].median())
            repro[f"gdsc2_{crit_name}_{rule}_median_rho"] = {
                "target": t, "reproduced": got, "pass": abs(got - t) <= GDSC2_TOL[crit_name]}
    repro["gdsc2_queries_with_tied_top1"] = ties
    if not all(v["pass"] for k, v in repro.items() if k.endswith("median_rho")):
        return pq, [], [], repro

    outcomes = {}
    for crit_name in GDSC2_CRITERIA:
        outcomes[f"top1 percentile, {crit_name}"] = "{rule}_top1_pct_" + crit_name
        outcomes[f"top1 criterion value, {crit_name}"] = "{rule}_top1_value_" + crit_name
        outcomes[f"top{TOP_B} mean percentile, {crit_name}"] = "{rule}_top%d_pct_%s" % (TOP_B, crit_name)
    summary = summarise(pq, "query_drug", "GDSC2", outcomes)
    changed = []
    for crit_name in GDSC2_CRITERIA:
        for name, a, b in CONTRASTS:
            rec = changed_top1(pq, a, b, f"{a}_top1_value_{crit_name}", f"{b}_top1_value_{crit_name}")
            changed.append({"dataset": "GDSC2", "criterion": crit_name,
                            "comparison": f"{name} ({a} vs {b})", **rec})
    return pq, summary, changed, repro


def run_moa(path: Path) -> tuple[pd.DataFrame, list[dict], list[dict], dict]:
    d = pd.read_csv(path)
    d = d[d.split_type == "leave_drug_out"]
    key = ["cell_line", "heldout_drug", "seed"]
    wide = None
    for rule, method in MOA_RULES.items():
        m = d[d.method == method].set_index(key)[["selected_top1_drug", "moa_hit@1", "moa_hit@5",
                                                   "moa_ndcg"]]
        m.columns = [f"{rule}_top1", f"{rule}_hit1", f"{rule}_hit5", f"{rule}_ndcg"]
        wide = m if wide is None else wide.join(m, how="inner")
    wide = wide.reset_index()
    repro = {"moa_n_queries": int(len(wide))}
    for name, a, b in CONTRASTS:
        got = float((wide[f"{a}_ndcg"] - wide[f"{b}_ndcg"]).mean())
        t = MOA_TARGET[name]
        repro[f"moa_{name}_mean_dndcg"] = {"target": t, "reproduced": got,
                                           "pass": abs(got - t) <= MOA_TOL}
    if not all(v["pass"] for k, v in repro.items() if k.endswith("dndcg")):
        return wide, [], [], repro

    outcomes = {"Hit@1": "{rule}_hit1", "Hit@5": "{rule}_hit5"}
    summary = summarise(wide, "heldout_drug", "MoA", outcomes)
    changed = []
    for name, a, b in CONTRASTS:
        rec = changed_top1(wide, a, b, f"{a}_hit1", f"{b}_hit1")
        changed.append({"dataset": "MoA", "criterion": "shares annotated mechanism",
                        "comparison": f"{name} ({a} vs {b})", **rec})
    return wide, summary, changed, repro


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gdsc2", type=Path, required=True)
    ap.add_argument("--moa", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    g_pq, g_sum, g_chg, g_rep = run_gdsc2(args.gdsc2)
    m_pq, m_sum, m_chg, m_rep = run_moa(args.moa)
    repro = {**g_rep, **m_rep}
    (args.out / "reproduction.json").write_text(json.dumps(repro, indent=2))
    g_pq.to_csv(args.out / "gdsc2_per_query.csv", index=False)
    m_pq.to_csv(args.out / "moa_per_query.csv", index=False)
    if g_sum or m_sum:
        pd.DataFrame(g_sum + m_sum).to_csv(args.out / "summary.csv", index=False)
        pd.DataFrame(g_chg + m_chg).to_csv(args.out / "changed_top1.csv", index=False)

    prov = {"argv": sys.argv, "inputs": {str(p): sha256(p) for p in (args.gdsc2, args.moa)},
            "n_boot": N_BOOT, "boot_seed": BOOT_SEED, "top_b": TOP_B,
            "python": sys.version.split()[0], "platform": platform.platform(),
            "versions": {"numpy": np.__version__, "pandas": pd.__version__},
            "gdsc2_gate_passed": bool(g_sum), "moa_gate_passed": bool(m_sum)}
    (args.out / "provenance.json").write_text(json.dumps(prov, indent=2))
    print(json.dumps(repro, indent=2))


if __name__ == "__main__":
    main()
