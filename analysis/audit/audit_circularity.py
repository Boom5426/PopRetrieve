#!/usr/bin/env python

"""Audit: structure_reliability circularity from energy_disagreement component.
Fixed version: includes component columns in query_sr selection.
"""

# --- repo-root path resolution (added for public release; replaces hardcoded /data/boom/JUDGE) ---
from pathlib import Path as _P
REPO = _P(__file__).resolve().parents[2]
SRC = str(REPO / "src")
RESULTS_AUDIT = str(REPO / "results" / "upgrade")
DATA_PROC = str(REPO / "data" / "processed")
DATA_ANNO = str(REPO / "data" / "annotation")
# ------------------------------------------------------------------------------------------------
import os, json, sys
import numpy as np
import pandas as pd
from scipy.stats import spearmanr, mannwhitneyu

RESULTS_DIR = str(REPO / "results" / "exp12_partial_observed_retrieval")
OUT_DIR = RESULTS_AUDIT
os.makedirs(OUT_DIR, exist_ok=True)

info = pd.read_csv(os.path.join(RESULTS_DIR, "information_condition_summary.csv"))
pq   = pd.read_csv(os.path.join(RESULTS_DIR, "per_query_scores.csv"))

merge_keys = ["split_type", "cell_line", "heldout_drug", "heldout_MoA",
              "observed_library_fraction", "information_condition_mode", "seed"]
component_cols = ["subpopulation_variance_ratio", "isotropy_index",
                  "response_diversity", "mean_energy_disagreement",
                  "bootstrap_rank_stability", "preference_conflict_topk"]

info_slim = info[merge_keys + component_cols].drop_duplicates()
df = pq.merge(info_slim, on=merge_keys, how="inner")
has_td = df[df["true_divergence"].notna()].copy()

def sr_original(row):
    svr   = np.clip(row["subpopulation_variance_ratio"] / 0.05, 0, 1)
    div   = np.clip(row["response_diversity"], 0, 1)
    boot  = np.clip(row["bootstrap_rank_stability"], 0, 1)
    edis  = np.clip(abs(row["mean_energy_disagreement"]), 0, 1)
    return 0.15 * svr + 0.10 * div + 0.40 * boot + 0.35 * edis

def sr_v2(row):
    svr   = np.clip(row["subpopulation_variance_ratio"] / 0.05, 0, 1)
    div   = np.clip(row["response_diversity"], 0, 1)
    boot  = np.clip(row["bootstrap_rank_stability"], 0, 1)
    w_svr  = 0.15 / 0.65
    w_div  = 0.10 / 0.65
    w_boot = 0.40 / 0.65
    return w_svr * svr + w_div * div + w_boot * boot

def recommendation_mode(struct_rel, pref_conflict,
                        struct_thresh=0.4, conflict_thresh=0.4):
    if struct_rel < struct_thresh:
        return "mean_or_no_call"
    if pref_conflict < conflict_thresh:
        return "mean_sufficient"
    if pref_conflict >= conflict_thresh and struct_rel >= struct_thresh:
        return "DART_recommended"
    return "uncertain"

has_td["sr_original_recomputed"] = has_td.apply(sr_original, axis=1)
has_td["sr_v2"] = has_td.apply(sr_v2, axis=1)

edis_clip = has_td["mean_energy_disagreement"].abs().clip(0, 1)
edis_contribution = 0.35 * edis_clip

has_td["rmode_original"] = has_td.apply(
    lambda r: recommendation_mode(r["sr_original_recomputed"], r["preference_conflict_topk"]), axis=1)
has_td["rmode_v2"] = has_td.apply(
    lambda r: recommendation_mode(r["sr_v2"], r["preference_conflict_topk"]), axis=1)

# Query-level: one sr per query-seed, include ALL component columns
query_keys = ["cell_line", "heldout_drug", "observed_library_fraction", "information_condition_mode"]
query_sr = has_td.drop_duplicates(subset=query_keys + ["seed"])[
    query_keys + ["seed", "sr_original_recomputed", "sr_v2",
     "true_divergence", "rmode_original", "rmode_v2",
     "mean_energy_disagreement", "preference_conflict_topk",
     "subpopulation_variance_ratio", "response_diversity",
     "bootstrap_rank_stability"]
].copy()
print(f"Unique query-seed pairs: {len(query_sr)}")

# Correlations
rho_orig, p_orig = spearmanr(query_sr["sr_original_recomputed"], query_sr["true_divergence"])
rho_v2, p_v2     = spearmanr(query_sr["sr_v2"], query_sr["true_divergence"])
print(f"Spearman(sr_original, true_div): rho={rho_orig:.4f}, p={p_orig:.4e}")
print(f"Spearman(sr_v2, true_div):       rho={rho_v2:.4f}, p={p_v2:.4e}")

# Component correlations
comp_corrs = {}
for comp, label in [("subpopulation_variance_ratio", "svr"),
                    ("response_diversity", "diversity"),
                    ("bootstrap_rank_stability", "boot_stability"),
                    ("mean_energy_disagreement", "energy_disagree_abs")]:
    vals = query_sr[comp].abs() if "disagreement" in comp else query_sr[comp]
    rr, pp = spearmanr(vals, query_sr["true_divergence"])
    comp_corrs[label] = {"rho": round(float(rr), 4), "p": float(pp)}
    print(f"  Spearman({label}, true_div): rho={rr:.4f}, p={pp:.4e}")

# Mann-Whitney U
def gate_mw(rmode_col, label):
    rec = query_sr[query_sr[rmode_col] == "DART_recommended"]["true_divergence"]
    nrec = query_sr[query_sr[rmode_col] != "DART_recommended"]["true_divergence"]
    print(f"\n{label}: n_rec={len(rec)}, n_nrec={len(nrec)}")
    print(f"  rec mean={rec.mean():.4f}, nrec mean={nrec.mean():.4f}")
    if len(rec) >= 2 and len(nrec) >= 2:
        U, p = mannwhitneyu(rec, nrec, alternative="two-sided")
        print(f"  Mann-Whitney U={U:.1f}, p={p:.4e}")
        return float(p)
    return None

p_mw_orig = gate_mw("rmode_original", "Original gate")
p_mw_v2   = gate_mw("rmode_v2", "V2 gate")

# Fractions
frac_orig = float((query_sr["rmode_original"] == "DART_recommended").mean())
frac_v2   = float((query_sr["rmode_v2"] == "DART_recommended").mean())
print(f"\nFrac recommended original: {frac_orig:.4f}")
print(f"Frac recommended v2: {frac_v2:.4f}")

# Gate distribution detail
print("\n=== Original gate ===")
print(query_sr["rmode_original"].value_counts().to_string())
print("\n=== V2 gate ===")
print(query_sr["rmode_v2"].value_counts().to_string())

improved = rho_v2 > rho_orig
print(f"\n=== VERDICT ===")
print(f"Removing energy_disagreement: rho {rho_orig:.4f} -> {rho_v2:.4f}")
print(f"Improved (less negative)? {improved}")
print(f"Circularity confirmed (v2 better aligned with true_div)? {improved}")

results = {
    "rho_original_vs_true_div": round(float(rho_orig), 4),
    "rho_v2_vs_true_div": round(float(rho_v2), 4),
    "p_original_mannwhitney": p_mw_orig,
    "p_v2_mannwhitney": p_mw_v2,
    "frac_recommended_original": round(frac_orig, 4),
    "frac_recommended_v2": round(frac_v2, 4),
    "energy_disagreement_contribution": round(float(edis_contribution.mean()), 4),
    "confirmed_circularity": bool(improved),
    "component_correlations": comp_corrs,
    "gate_distribution_original": query_sr["rmode_original"].value_counts().to_dict(),
    "gate_distribution_v2": query_sr["rmode_v2"].value_counts().to_dict(),
}

with open(os.path.join(OUT_DIR, "structure_reliability_circularity.json"), "w") as f:
    json.dump(results, f, indent=2)
print(f"\nSaved to {OUT_DIR}/structure_reliability_circularity.json")
print(json.dumps(results, indent=2))

