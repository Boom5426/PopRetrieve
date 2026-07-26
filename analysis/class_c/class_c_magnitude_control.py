#!/usr/bin/env python3

# =============================================================================
# SUPERSEDED. DO NOT USE THE NUMBERS THIS SCRIPT PRODUCES.
#
# `retrieval.metrics.score_energy` returns MINUS the energy distance, i.e. a
# SIMILARITY (higher = more similar). This script ranks it ASCENDING
# (rankdata(e_scores) / argmin(dart_scores)) under the comment "lowest energy =
# top pick", so JUDGE's rank-1 candidate is the population FARTHEST from the
# query. The mean-cosine baseline in the same script is ranked correctly
# (argmax). JUDGE is ranked backwards and its incumbent is not.
#
# The inversion selects large-response candidates (energy distance tracks
# candidate magnitude at rho = +0.79), and large response predicts potency, so
# it manufactures an apparent +0.52 JUDGE-vs-potency correlation. The true value
# is -0.52.
#
# This script also pools all four doses (the rest of the paper uses 10 uM) and
# pools GDSC1 with GDSC2 (different platforms, not a common AUC scale).
#
# Use analysis/class_c/class_c_magnitude_control_v2.py. See CORRECTIONS.md R14.
# =============================================================================


"""Class C magnitude-confound control.
Tests whether JUDGE energy's potency correlation is a response-magnitude artifact.
For each matched drug: response magnitude m = ||mean_treated - mean_control||.
Compares 4 rankings' Spearman correlation with true GDSC potency (AUC):
  1. energy (reproduce child)
  2. mean_delta_cosine (PROPER control-subtracted mean baseline)
  3. magnitude_similarity: -|m_query - m_cand|  (similar-magnitude candidates)
  4. magnitude_only: rank candidates by their own m_cand (query-independent)
Also: direct Spearman(m_cand, AUC) across drugs per line = can a scalar predict potency?
"""

# --- repo-root path resolution (added for public release; replaces hardcoded /data/boom/JUDGE) ---
from pathlib import Path as _P
REPO = _P(__file__).resolve().parents[2]
SRC = str(REPO / "src")
RESULTS_AUDIT = str(REPO / "results" / "upgrade")
DATA_PROC = str(REPO / "data" / "processed")
DATA_ANNO = str(REPO / "data" / "annotation")
# ------------------------------------------------------------------------------------------------
import sys, json, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, SRC)
import numpy as np, pandas as pd
from scipy import stats
from data.load_sciplex3 import load_sciplex3
from retrieval.metrics import score_energy

SEED = 42
np.random.seed(SEED)
ADIR = RESULTS_AUDIT

match_df = pd.read_csv(f"{ADIR}/drug_match_table.csv")
match_df = match_df[match_df["sp_drug"] != "S-Ruxolitinib (INCB018424)"].copy()

ds = load_sciplex3()
X = ds.X
obs = ds.obs

def dense(a):
    return a.toarray() if hasattr(a, "toarray") else np.asarray(a)

rows = []
direct_corr = {}
for cell_line in ["A549", "K562", "MCF7"]:
    lm = match_df[match_df["cell_line"] == cell_line]
    via = dict(zip(lm["sp_drug"], lm["AUC"]))
    line_mask = (obs["cell_line"] == cell_line).values
    ctrl_mask = line_mask & obs["is_control"].values
    ctrl_mean = dense(X[ctrl_mask]).mean(0).astype(np.float64)

    drug_cells, drug_dmean, drug_mag = {}, {}, {}
    for drug in sorted(lm["sp_drug"].unique()):
        dm = line_mask & (obs["perturbation"] == drug).values & (~obs["is_control"].values)
        if dm.sum() >= 10:
            cells = dense(X[dm]).astype(np.float64)
            drug_cells[drug] = cells
            dmean = cells.mean(0) - ctrl_mean          # delta mean (response vector)
            drug_dmean[drug] = dmean
            drug_mag[drug] = float(np.linalg.norm(dmean))  # response magnitude

    valid = sorted(drug_cells.keys())
    if len(valid) < 8:
        continue

    # Direct: does response magnitude alone predict potency (AUC)?
    mags = np.array([drug_mag[d] for d in valid])
    aucs = np.array([via[d] for d in valid])
    rho_mag_auc, p_mag_auc = stats.spearmanr(mags, aucs)
    direct_corr[cell_line] = {"rho_magnitude_vs_AUC": float(rho_mag_auc), "p": float(p_mag_auc), "n_drugs": len(valid)}

    # Leave-one-out: 4 rankings vs potency
    for q in valid:
        cands = [d for d in valid if d != q]
        qcells = drug_cells[q]; qdmean = drug_dmean[q]; qmag = drug_mag[q]
        e_scores, cos_scores, magsim, magonly, cand_auc = [], [], [], [], []
        for cd in cands:
            ccells = drug_cells[cd]
            e_scores.append(score_energy(qcells, ccells, max_cells=500, seed=SEED))
            cdm = drug_dmean[cd]
            denom = (np.linalg.norm(qdmean) * np.linalg.norm(cdm)) + 1e-12
            cos_scores.append(float(np.dot(qdmean, cdm) / denom))     # delta-mean cosine
            magsim.append(-abs(qmag - drug_mag[cd]))                  # similar magnitude
            magonly.append(drug_mag[cd])                              # candidate's own magnitude
            cand_auc.append(via[cd])
        e_scores=np.array(e_scores); cos_scores=np.array(cos_scores)
        magsim=np.array(magsim); magonly=np.array(magonly); cand_auc=np.array(cand_auc)
        pot_rank = stats.rankdata(cand_auc)                # 1 = most potent (low AUC)
        # energy: low = similar -> rank
        er = stats.rankdata(e_scores)
        # delta-cosine: high = similar -> rank by -cos
        cr = stats.rankdata(-cos_scores)
        # magnitude-similarity: high magsim = similar -> rank by -magsim
        mr = stats.rankdata(-magsim)
        # magnitude-only: higher magnitude candidate first -> rank by -magonly
        mor = stats.rankdata(-magonly)
        def rho(a): return stats.spearmanr(a, pot_rank)[0]
        rows.append({
            "cell_line": cell_line, "query_drug": q, "n_cand": len(cands),
            "query_magnitude": qmag, "query_auc": via[q],
            "energy_rho": rho(er), "delta_cosine_rho": rho(cr),
            "magsim_rho": rho(mr), "magonly_rho": rho(mor),
            # also: correlation of energy score with candidate magnitude (is energy ~ magnitude?)
            "energy_vs_candmag_rho": stats.spearmanr(e_scores, magonly)[0],
        })

df = pd.DataFrame(rows)
df.to_csv(f"{ADIR}/class_c_magnitude_control.csv", index=False)

out = {"direct_magnitude_vs_AUC": direct_corr, "n_queries": len(df)}
for col in ["energy_rho","delta_cosine_rho","magsim_rho","magonly_rho","energy_vs_candmag_rho"]:
    out[col+"_median"] = float(df[col].median())
    out[col+"_mean"] = float(df[col].mean())
# per line energy vs magonly
out["per_line"] = {}
for ln in df.cell_line.unique():
    s = df[df.cell_line==ln]
    out["per_line"][ln] = {"energy_rho_med": float(s.energy_rho.median()),
                            "magonly_rho_med": float(s.magonly_rho.median()),
                            "delta_cosine_rho_med": float(s.delta_cosine_rho.median()),
                            "energy_vs_candmag_med": float(s.energy_vs_candmag_rho.median())}
json.dump(out, open(f"{ADIR}/class_c_magnitude_control.json","w"), indent=2)
print(json.dumps(out, indent=2))
