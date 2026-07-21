#!/usr/bin/env python3

"""
subpop_identifiability_landscape.py (v2, optimized)
=====================================================
Gap statistic on PCA-50 (not raw 2000d), MiniBatchKMeans, B=5.
"""

# --- repo-root path resolution (added for public release; replaces hardcoded /data/boom/DART) ---
from pathlib import Path as _P
REPO = _P(__file__).resolve().parents[2]
SRC = str(REPO / "src")
RESULTS_AUDIT = str(REPO / "results" / "upgrade")
DATA_PROC = str(REPO / "data" / "processed")
DATA_ANNO = str(REPO / "data" / "annotation")
# ------------------------------------------------------------------------------------------------
import sys, os, json, time, warnings
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans, MiniBatchKMeans
from sklearn.mixture import GaussianMixture
from sklearn.metrics import silhouette_score, adjusted_rand_score
from sklearn.decomposition import PCA

warnings.filterwarnings("ignore")

sys.path.insert(0, SRC)
from data.load_sciplex3 import load_sciplex3
from retrieval.metrics import score_energy

OUT_DIR = RESULTS_AUDIT
os.makedirs(OUT_DIR, exist_ok=True)

SEED = 42
MAX_CELLS = 300
GAP_B = 5
CONTROLLED_SEEDS = 20
COVERAGE_SEEDS = 3

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def between_total_variance_ratio(X, labels):
    total_var = np.var(X, axis=0).sum()
    if total_var < 1e-12:
        return 0.0
    grand_mean = X.mean(axis=0)
    between_var = 0.0
    for k in np.unique(labels):
        mask = labels == k
        nk = mask.sum()
        ck = X[mask].mean(axis=0)
        between_var += nk * np.sum((ck - grand_mean) ** 2)
    between_var /= len(X)
    return float(between_var / total_var)


def gap_statistic(X_pca, k_range=(2, 3, 4, 5), B=5, seed=42):
    """Gap statistic on PCA-reduced data. Uses MiniBatchKMeans for speed."""
    rng = np.random.default_rng(seed)
    n, d = X_pca.shape

    def wk(data, k):
        km = MiniBatchKMeans(n_clusters=k, n_init=2, max_iter=50, 
                             batch_size=min(256, n), random_state=seed)
        lab = km.fit_predict(data)
        w = 0.0
        for c_idx in range(k):
            mask = lab == c_idx
            if mask.sum() > 1:
                w += np.sum(np.var(data[mask], axis=0)) * mask.sum()
        return w

    mins = X_pca.min(axis=0)
    maxs = X_pca.max(axis=0)
    spans = maxs - mins
    spans[spans < 1e-12] = 1.0

    gaps = {}
    gap_sds = {}
    for k in k_range:
        log_wk_val = np.log(max(wk(X_pca, k), 1e-300))
        ref_log_wks = []
        for b_idx in range(B):
            ref = rng.uniform(size=(n, d)) * spans + mins
            ref_log_wks.append(np.log(max(wk(ref, k), 1e-300)))
        ref_log_wks = np.array(ref_log_wks)
        gaps[k] = float(ref_log_wks.mean() - log_wk_val)
        gap_sds[k] = float(ref_log_wks.std() * np.sqrt(1 + 1.0 / B))

    ks = sorted(gaps.keys())
    best_k = ks[-1]
    for i in range(len(ks) - 1):
        k_cur = ks[i]
        k_next = ks[i + 1]
        if gaps[k_cur] >= gaps[k_next] - gap_sds[k_next]:
            best_k = k_cur
            break
    return best_k, gaps, gap_sds


def safe_sil(X, labels, seed=42):
    n = len(X)
    if len(set(labels)) < 2 or n < 3:
        return -1.0
    try:
        return float(silhouette_score(X, labels, 
                     sample_size=min(n, 2000), random_state=seed))
    except Exception:
        return -1.0


def run_clustering_methods(X, control_mean=None, seed=42):
    """Run all recovery methods. Returns dict of {method: (labels, silhouette)}."""
    n = X.shape[0]
    results = {}

    # 1. Raw KMeans k=2
    km = KMeans(n_clusters=2, n_init=5, max_iter=200, random_state=seed)
    lab = km.fit_predict(X)
    results["raw_kmeans_k2"] = (lab, safe_sil(X, lab, seed))

    # 2. PCA(10) -> KMeans k=2
    pca10 = PCA(n_components=min(10, X.shape[1]), random_state=seed).fit_transform(X)
    lab = KMeans(n_clusters=2, n_init=5, max_iter=200, random_state=seed).fit_predict(pca10)
    results["pca10_kmeans_k2"] = (lab, safe_sil(pca10, lab, seed))

    # 3. PCA(50) -> KMeans k=2
    nc50 = min(50, X.shape[1], n - 1)
    pca50 = PCA(n_components=nc50, random_state=seed).fit_transform(X)
    lab = KMeans(n_clusters=2, n_init=5, max_iter=200, random_state=seed).fit_predict(pca50)
    results["pca50_kmeans_k2"] = (lab, safe_sil(pca50, lab, seed))

    # 4. GMM(2) on raw (diag covariance for high-d)
    try:
        gmm = GaussianMixture(n_components=2, max_iter=100, random_state=seed, 
                               covariance_type="diag")
        lab = gmm.fit_predict(X)
        results["gmm2_raw"] = (lab, safe_sil(X, lab, seed))
    except Exception:
        results["gmm2_raw"] = (np.zeros(n, int), -1.0)

    # 5. GMM(2) on PCA-50
    try:
        gmm = GaussianMixture(n_components=2, max_iter=100, random_state=seed,
                               covariance_type="full")
        lab = gmm.fit_predict(pca50)
        results["gmm2_pca50"] = (lab, safe_sil(pca50, lab, seed))
    except Exception:
        results["gmm2_pca50"] = (np.zeros(n, int), -1.0)

    # 6. Higher k (3, 4, 5) on raw - take best silhouette
    best_higher_k = 3
    best_higher_sil = -2.0
    best_higher_lab = None
    for k in [3, 4, 5]:
        if n <= k:
            continue
        lab = KMeans(n_clusters=k, n_init=3, max_iter=200, random_state=seed).fit_predict(X)
        s = safe_sil(X, lab, seed)
        if s > best_higher_sil:
            best_higher_sil = s
            best_higher_k = k
            best_higher_lab = lab
    if best_higher_lab is not None:
        results[f"raw_kmeans_bestk{best_higher_k}"] = (best_higher_lab, best_higher_sil)

    # 7. Response-space: subtract control mean, then KMeans k=2
    if control_mean is not None:
        X_resp = X - control_mean
        lab = KMeans(n_clusters=2, n_init=5, max_iter=200, random_state=seed).fit_predict(X_resp)
        results["response_kmeans_k2"] = (lab, safe_sil(X_resp, lab, seed))

    return results


# ===========================================================================
# Step 1: Subpopulation identifiability landscape
# ===========================================================================

log("Loading SciPlex3...")
ds = load_sciplex3()
X_all = ds.X
obs = ds.obs.copy()
rng = np.random.default_rng(SEED)

rows_all = []

log("=== STEP 1: Subpop identifiability landscape (SciPlex3) ===")
for cell_line in ["K562", "A549", "MCF7"]:
    line_mask = (obs["cell_line"] == cell_line).values
    ctrl_mask = ds.is_control
    ctrl_rows = np.flatnonzero(line_mask & ctrl_mask)
    control_mean = X_all[ctrl_rows].mean(axis=0) if len(ctrl_rows) > 0 else X_all.mean(axis=0)

    treated_mask = line_mask & ~ctrl_mask & (obs["dose_value"].astype(float) == 10000.0).values
    drug_counts = obs.loc[treated_mask, "perturbation"].value_counts()
    eligible_drugs = drug_counts[drug_counts >= 100].index.tolist()
    log(f"  {cell_line}: {len(eligible_drugs)} drugs with >=100 cells at dose 10000")

    for i_drug, drug in enumerate(eligible_drugs):
        drug_rows = np.flatnonzero(treated_mask & (obs["perturbation"] == drug).values)
        if len(drug_rows) > MAX_CELLS:
            drug_rows = rng.choice(drug_rows, MAX_CELLS, replace=False)

        X_q = X_all[drug_rows].astype(np.float32)
        n_cells = len(X_q)
        moa = obs.iloc[drug_rows[0]]["target"]

        # Run ALL clustering methods
        methods = run_clustering_methods(X_q, control_mean=control_mean, seed=SEED)
        raw_sil = methods["raw_kmeans_k2"][1]
        raw_labels = methods["raw_kmeans_k2"][0]
        var_ratio = between_total_variance_ratio(X_q, raw_labels)

        # Gap statistic on PCA-50 (much faster than raw 2000d)
        nc = min(50, X_q.shape[1], n_cells - 1)
        X_pca = PCA(n_components=nc, random_state=SEED).fit_transform(X_q)
        best_k, gaps, gap_sds = gap_statistic(X_pca, seed=SEED)

        row = {
            "dataset": "SciPlex3",
            "cell_line": cell_line,
            "perturbation": drug,
            "moa": moa,
            "n_cells": n_cells,
            "sil_raw_k2": raw_sil,
            "var_ratio_k2": var_ratio,
            "gap_best_k": best_k,
            "gap_k2": gaps.get(2, np.nan),
            "gap_k3": gaps.get(3, np.nan),
            "gap_k4": gaps.get(4, np.nan),
            "gap_k5": gaps.get(5, np.nan),
        }
        for mname, (lab, sil) in methods.items():
            row[f"sil_{mname}"] = sil
        rows_all.append(row)

        if (i_drug + 1) % 20 == 0:
            log(f"    {cell_line}: {i_drug+1}/{len(eligible_drugs)} drugs done")

    log(f"  {cell_line}: done ({len(eligible_drugs)} drugs)")

# Frangieh
log("Loading Frangieh...")
from data.load_frangieh import load_frangieh
ds_f = load_frangieh()
X_f = ds_f.X
obs_f = ds_f.obs.copy()
ctrl_rows_f = np.flatnonzero(ds_f.is_control)
control_mean_f = X_f[ctrl_rows_f].mean(axis=0) if len(ctrl_rows_f) > 0 else X_f.mean(axis=0)

treated_mask_f = ~ds_f.is_control
pert_counts_f = obs_f.loc[treated_mask_f, "perturbation"].value_counts()
eligible_f = pert_counts_f[pert_counts_f >= 100].index.tolist()
log(f"  Frangieh: {len(eligible_f)} perturbations with >=100 cells")

for i_p, pert in enumerate(eligible_f):
    pert_rows = np.flatnonzero(treated_mask_f & (obs_f["perturbation"] == pert).values)
    if len(pert_rows) > MAX_CELLS:
        pert_rows = rng.choice(pert_rows, MAX_CELLS, replace=False)

    X_q = X_f[pert_rows].astype(np.float32)
    n_cells = len(X_q)

    methods = run_clustering_methods(X_q, control_mean=control_mean_f, seed=SEED)
    raw_sil = methods["raw_kmeans_k2"][1]
    raw_labels = methods["raw_kmeans_k2"][0]
    var_ratio = between_total_variance_ratio(X_q, raw_labels)

    nc = min(50, X_q.shape[1], n_cells - 1)
    X_pca = PCA(n_components=nc, random_state=SEED).fit_transform(X_q)
    best_k, gaps, gap_sds = gap_statistic(X_pca, seed=SEED)

    row = {
        "dataset": "Frangieh",
        "cell_line": "Jurkat",
        "perturbation": pert,
        "moa": "KO",
        "n_cells": n_cells,
        "sil_raw_k2": raw_sil,
        "var_ratio_k2": var_ratio,
        "gap_best_k": best_k,
        "gap_k2": gaps.get(2, np.nan),
        "gap_k3": gaps.get(3, np.nan),
        "gap_k4": gaps.get(4, np.nan),
        "gap_k5": gaps.get(5, np.nan),
    }
    for mname, (lab, sil) in methods.items():
        row[f"sil_{mname}"] = sil
    rows_all.append(row)

    if (i_p + 1) % 50 == 0:
        log(f"    Frangieh: {i_p+1}/{len(eligible_f)} perturbations done")

log(f"  Frangieh: done ({len(eligible_f)} perturbations)")
del ds_f, X_f, obs_f


# ===========================================================================
# Step 2: Controlled mixture recovery (KEY VERDICT)
# ===========================================================================

log("=== STEP 2: Controlled mixture recovery (HDAC+JAK, K562) ===")
from retrieval.tasks import ControlledMixtureTask

controlled_results = []
for s in range(CONTROLLED_SEEDS):
    task = ControlledMixtureTask(ds, cell_line="K562", class_a="HDAC", class_b="JAK",
                                 dose=10000.0, n_total=400, seed=s)
    mix = task.build(alpha=0.7, seed=s)
    X_mix = mix["target"]
    true_labels = mix["target_labels"]
    ctrl_mean = mix["pseudo_control"]

    methods = run_clustering_methods(X_mix, control_mean=ctrl_mean, seed=s)
    seed_row = {"seed": s, "n_cells": len(X_mix), "alpha": 0.7}
    for mname, (lab, sil) in methods.items():
        ari = adjusted_rand_score(true_labels, lab)
        seed_row[f"ari_{mname}"] = ari
        seed_row[f"sil_{mname}"] = sil
    controlled_results.append(seed_row)
    if (s + 1) % 5 == 0:
        log(f"  Controlled seed {s+1}/{CONTROLLED_SEEDS} done")

ctrl_df = pd.DataFrame(controlled_results)
log("Controlled mixture ARI summary (mean over 20 seeds):")
ari_cols = [c for c in ctrl_df.columns if c.startswith("ari_")]
for col_name in sorted(ari_cols):
    vals = ctrl_df[col_name]
    log(f"  {col_name}: mean={vals.mean():.4f}, std={vals.std():.4f}, "
        f"min={vals.min():.4f}, max={vals.max():.4f}")

ctrl_df.to_csv(os.path.join(OUT_DIR, "controlled_mixture_ari.csv"), index=False)
log("Saved controlled_mixture_ari.csv")


# ===========================================================================
# Step 3: Coverage-identifiability linkage (A549 leave-drug-out)
# ===========================================================================

log("=== STEP 3: Coverage-identifiability linkage (A549, leave-drug-out) ===")

cell_line = "A549"
line_mask = (obs["cell_line"] == cell_line).values
ctrl_rows_a549 = np.flatnonzero(line_mask & ds.is_control)
control_mean_a549 = X_all[ctrl_rows_a549].mean(axis=0)

treated_mask_a549 = line_mask & ~ds.is_control & (obs["dose_value"].astype(float) == 10000.0).values
drug_counts_a549 = obs.loc[treated_mask_a549, "perturbation"].value_counts()
eligible_a549 = drug_counts_a549[drug_counts_a549 >= 100].index.tolist()
log(f"  A549 eligible drugs (>=100 cells): {len(eligible_a549)}")

drug_info = {}
for drug in eligible_a549:
    d_rows = np.flatnonzero(treated_mask_a549 & (obs["perturbation"] == drug).values)
    moa = obs.iloc[d_rows[0]]["target"]
    drug_info[drug] = {"rows": d_rows, "moa": moa}

coverage_rows = []

for cov_seed in range(COVERAGE_SEEDS):
    rng_cov = np.random.default_rng(SEED + cov_seed * 1000)
    log(f"  Coverage seed {cov_seed}...")

    for i_q, query_drug in enumerate(eligible_a549):
        qi = drug_info[query_drug]
        q_rows = qi["rows"]
        if len(q_rows) > MAX_CELLS:
            q_rows = rng_cov.choice(q_rows, MAX_CELLS, replace=False)
        X_q = X_all[q_rows].astype(np.float32)

        # Query silhouette (raw KMeans k=2)
        if len(X_q) > 5:
            km = KMeans(n_clusters=2, n_init=5, max_iter=200, random_state=SEED)
            lab = km.fit_predict(X_q)
            q_sil = safe_sil(X_q, lab, SEED)
        else:
            q_sil = -1.0

        # Leave-drug-out retrieval
        scores = {}
        moas = {}
        for cand_drug in eligible_a549:
            if cand_drug == query_drug:
                continue
            ci = drug_info[cand_drug]
            c_rows = ci["rows"]
            if len(c_rows) > MAX_CELLS:
                c_rows = rng_cov.choice(c_rows, MAX_CELLS, replace=False)
            X_c = X_all[c_rows].astype(np.float32)
            e = score_energy(X_q, X_c, max_cells=300, seed=SEED + cov_seed)
            scores[cand_drug] = e
            moas[cand_drug] = ci["moa"]

        ranking = sorted(scores.keys(), key=lambda d: scores[d], reverse=True)
        query_moa = qi["moa"]
        relevances = {d: (1.0 if moas[d] == query_moa else 0.0) for d in ranking}

        hit1 = relevances.get(ranking[0], 0.0) if ranking else 0.0

        # nDCG
        dcg = 0.0
        for r_i, item in enumerate(ranking):
            dcg += relevances[item] / np.log2(r_i + 2)
        sorted_rels = sorted([relevances[d] for d in ranking], reverse=True)
        idcg = 0.0
        for r_i, rel in enumerate(sorted_rels):
            idcg += rel / np.log2(r_i + 2)
        ndcg_val = dcg / idcg if idcg > 0 else 0.0

        n_same_moa = sum(1 for d in ranking if relevances[d] == 1.0)

        coverage_rows.append({
            "seed": cov_seed,
            "query_drug": query_drug,
            "query_moa": query_moa,
            "n_query_cells": len(X_q),
            "n_candidates": len(ranking),
            "n_same_moa_candidates": n_same_moa,
            "query_silhouette": q_sil,
            "hit_at_1": hit1,
            "moa_ndcg": ndcg_val,
        })

        if (i_q + 1) % 20 == 0:
            log(f"    Seed {cov_seed}: query {i_q+1}/{len(eligible_a549)}")

    log(f"  Coverage seed {cov_seed}: done ({len(eligible_a549)} queries)")

cov_df = pd.DataFrame(coverage_rows)

# Stratify by silhouette tertile
cov_df["sil_tertile"] = pd.qcut(cov_df["query_silhouette"], 3, labels=["low", "mid", "high"])
strat = cov_df.groupby("sil_tertile", observed=True)[["moa_ndcg", "hit_at_1"]].agg(["mean", "std", "count"])
log("Coverage by silhouette tertile:")
log(str(strat))

from scipy.stats import spearmanr
rho, pval = spearmanr(cov_df["query_silhouette"], cov_df["moa_ndcg"])
log(f"  Spearman(silhouette, nDCG): rho={rho:.4f}, p={pval:.4g}")

rho_hit, pval_hit = spearmanr(cov_df["query_silhouette"], cov_df["hit_at_1"])
log(f"  Spearman(silhouette, Hit@1): rho={rho_hit:.4f}, p={pval_hit:.4g}")

# Tertile boundaries
sil_bounds = cov_df.groupby("sil_tertile", observed=True)["query_silhouette"].agg(["min", "max", "median"])
log(f"Silhouette tertile boundaries:\n{sil_bounds}")


# ===========================================================================
# Save everything
# ===========================================================================

log("=== SAVING RESULTS ===")

main_df = pd.DataFrame(rows_all)
main_df.to_csv(os.path.join(OUT_DIR, "subpop_identifiability.csv"), index=False)
log(f"Saved subpop_identifiability.csv ({len(main_df)} rows)")

cov_df.to_csv(os.path.join(OUT_DIR, "coverage_by_identifiability.csv"), index=False)
log(f"Saved coverage_by_identifiability.csv ({len(cov_df)} rows)")

sciplex_sils = main_df.loc[main_df["dataset"] == "SciPlex3", "sil_raw_k2"]
frangieh_sils = main_df.loc[main_df["dataset"] == "Frangieh", "sil_raw_k2"]

# Best recovery method
best_method = None
best_ari = -1
for col_name in ctrl_df.columns:
    if col_name.startswith("ari_"):
        m = ctrl_df[col_name].mean()
        if m > best_ari:
            best_ari = m
            best_method = col_name.replace("ari_", "")

cov_high = cov_df.loc[cov_df["sil_tertile"] == "high", "moa_ndcg"].mean()
cov_mid = cov_df.loc[cov_df["sil_tertile"] == "mid", "moa_ndcg"].mean()
cov_low = cov_df.loc[cov_df["sil_tertile"] == "low", "moa_ndcg"].mean()
cov_tracks = bool(cov_high > cov_low * 1.1)

hit1_high = cov_df.loc[cov_df["sil_tertile"] == "high", "hit_at_1"].mean()
hit1_mid = cov_df.loc[cov_df["sil_tertile"] == "mid", "hit_at_1"].mean()
hit1_low = cov_df.loc[cov_df["sil_tertile"] == "low", "hit_at_1"].mean()

summary = {
    "step1_landscape": {
        "sciplex3": {
            "n_drugs": int(len(sciplex_sils)),
            "median_silhouette": float(sciplex_sils.median()),
            "mean_silhouette": float(sciplex_sils.mean()),
            "iqr": [float(sciplex_sils.quantile(0.25)), float(sciplex_sils.quantile(0.75))],
            "frac_above_01": float((sciplex_sils > 0.1).mean()),
            "frac_above_025": float((sciplex_sils > 0.25).mean()),
            "per_line": {}
        },
        "frangieh": {
            "n_perturbations": int(len(frangieh_sils)),
            "median_silhouette": float(frangieh_sils.median()),
            "mean_silhouette": float(frangieh_sils.mean()),
            "frac_above_01": float((frangieh_sils > 0.1).mean()),
            "frac_above_025": float((frangieh_sils > 0.25).mean()),
        }
    },
    "step2_recovery": {
        "best_method": best_method,
        "best_ari_mean": float(best_ari),
        "best_ari_max": float(ctrl_df[f"ari_{best_method}"].max()),
        "any_method_ari_above_05": bool(any(ctrl_df[col].max() > 0.5
                                             for col in ctrl_df.columns if col.startswith("ari_"))),
        "all_method_means": {col.replace("ari_", ""): float(ctrl_df[col].mean())
                             for col in sorted(ctrl_df.columns) if col.startswith("ari_")},
        "all_method_maxes": {col.replace("ari_", ""): float(ctrl_df[col].max())
                             for col in sorted(ctrl_df.columns) if col.startswith("ari_")}
    },
    "step3_coverage_linkage": {
        "n_queries_per_seed": int(cov_df["query_drug"].nunique()),
        "n_seeds": COVERAGE_SEEDS,
        "spearman_rho": float(rho),
        "spearman_p": float(pval),
        "spearman_hit1_rho": float(rho_hit),
        "spearman_hit1_p": float(pval_hit),
        "coverage_by_tertile": {
            "high_ndcg": float(cov_high),
            "mid_ndcg": float(cov_mid),
            "low_ndcg": float(cov_low),
        },
        "hit1_by_tertile": {
            "high": float(hit1_high),
            "mid": float(hit1_mid),
            "low": float(hit1_low),
        },
        "coverage_tracks_identifiability": cov_tracks,
    }
}

for cl in ["K562", "A549", "MCF7"]:
    cl_sils = main_df.loc[(main_df["dataset"] == "SciPlex3") & (main_df["cell_line"] == cl), "sil_raw_k2"]
    summary["step1_landscape"]["sciplex3"]["per_line"][cl] = {
        "n_drugs": int(len(cl_sils)),
        "median_sil": float(cl_sils.median()) if len(cl_sils) > 0 else None,
        "frac_above_01": float((cl_sils > 0.1).mean()) if len(cl_sils) > 0 else None,
    }

# Recovery silhouettes on real drugs
sil_method_cols = [c for c in main_df.columns if c.startswith("sil_") and c != "sil_raw_k2"]
if sil_method_cols:
    sc_only = main_df.loc[main_df["dataset"] == "SciPlex3"]
    summary["step2_recovery"]["real_drug_best_sil_by_method"] = {}
    for mc in ["sil_raw_k2"] + sil_method_cols:
        if mc in sc_only.columns:
            vals = sc_only[mc].dropna()
            summary["step2_recovery"]["real_drug_best_sil_by_method"][mc.replace("sil_", "")] = {
                "median": float(vals.median()),
                "frac_above_01": float((vals > 0.1).mean()),
            }

with open(os.path.join(OUT_DIR, "subpop_identifiability_summary.json"), "w") as f:
    json.dump(summary, f, indent=2)
log("Saved subpop_identifiability_summary.json")

log("=== ALL DONE ===")
print("EXIT_OK")
