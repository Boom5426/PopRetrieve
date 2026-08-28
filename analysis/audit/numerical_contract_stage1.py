"""Numerical-contract audit, stage 1: pandas side.

Recovers the manuscript's MoA-defined query set from the ONLY documented rule in the
repository (src/experiments/exp16_common.mask_undefined), recomputes every R3-R5 headline
value, and dumps paired-difference vectors for stage 2 (scipy) to test.
"""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path
import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))
from experiments.exp16_common import mask_undefined, SENTINEL  # noqa: E402

OUT = REPO / "results" / "audit"
OUT.mkdir(parents=True, exist_ok=True)
KEY = ["split_type", "cell_line", "heldout_drug", "observed_library_fraction",
       "information_condition_mode", "seed"]
VARIANTS = ["DART_energy", "DART_mmd", "DART_sliced_wasserstein",
            "DART_coverage_mean", "DART_coverage_worst"]
BASE = "mean_cosine"
report: dict = {}

# ---------------------------------------------------------------- load + mask
raw = pd.read_csv(REPO / "results/exp12_partial_observed_retrieval/per_query_scores.csv")
masked = mask_undefined(raw)                       # exp12's -1 sentinel -> NaN

qid = raw.groupby(KEY, sort=True).size().index
report["n_queries_total"] = len(qid)
report["rows"] = len(raw)
report["methods"] = sorted(raw.method.unique())

# ------------------------------------------------- the denominator tree
by_split = raw.groupby("split_type").size() // raw.method.nunique()
sent_q = masked.groupby(KEY)["moa_ndcg"].apply(lambda s: s.isna().all())
report["split_type_counts"] = by_split.to_dict()
report["n_all_moa_sentinel"] = int(sent_q.sum())
report["sentinel_by_split"] = (
    raw[raw.moa_ndcg <= SENTINEL + 1e-9].groupby("split_type").size() // raw.method.nunique()
).to_dict()

moa_defined = sent_q[~sent_q].index                # the MoA-defined set
report["n_moa_defined"] = len(moa_defined)
mdf = pd.DataFrame(list(moa_defined), columns=KEY)
report["moa_defined_split_types"] = mdf.split_type.value_counts().to_dict()

# alternative (rejected) rule, for the record
nmoa = raw.groupby(KEY)["n_gt_moa"].max()
report["n_under_rejected_rule_n_gt_moa_gt_0"] = int((nmoa > 0).sum())

# stable hash of the ordered identifiers
def qhash(idx) -> str:
    lines = ["|".join(str(x) for x in t) for t in sorted(idx)]
    return hashlib.sha256("\n".join(lines).encode()).hexdigest()

report["hash_all765"] = qhash(qid)
report["hash_moa600"] = qhash(moa_defined)
pd.DataFrame(sorted(moa_defined), columns=KEY).to_csv(OUT / "moa_defined_query_set.csv", index=False)

rec = raw.groupby(KEY)["recommendation_mode"].first()
report["recommendation_counts"] = rec.value_counts().to_dict()

# ------------------------------------------------- pivots
regret = raw.pivot_table(index=KEY, columns="method", values="decision_regret")
ndcg = masked.pivot_table(index=KEY, columns="method", values="moa_ndcg")

SUBSETS = {
    "all765":        regret.index,
    "moa600":        moa_defined,
    "recommended621": rec[rec == "DART_recommended"].index,
    "nonrecommended133": rec[rec == "mean_or_no_call"].index,
    "meansufficient11": rec[rec == "mean_sufficient"].index,
}

def stats_block(idx, pivot, direction):
    """direction='regret' -> base-variant (reduction). direction='gain' -> variant-base."""
    ii = pivot.index.intersection(idx)
    out = {}
    for v in VARIANTS:
        d = (pivot.loc[ii, BASE] - pivot.loc[ii, v]) if direction == "regret" \
            else (pivot.loc[ii, v] - pivot.loc[ii, BASE])
        d = d.dropna()
        out[v] = dict(n=int(len(d)), median=float(d.median()), mean=float(d.mean()),
                      frac_improved=float((d > 0).mean()), frac_worsened=float((d < 0).mean()),
                      frac_tied=float((d == 0).mean()), sd=float(d.std(ddof=1)))
    return out

report["classA"] = {k: stats_block(i, regret, "regret") for k, i in SUBSETS.items()}
report["classB"] = {k: stats_block(i, ndcg, "gain") for k, i in SUBSETS.items()}

# identical-query-set confirmation for the ranges
ii = regret.index.intersection(moa_defined)
setA = {v: set(map(tuple, (regret.loc[ii, BASE] - regret.loc[ii, v]).dropna().index)) for v in VARIANTS}
setB = {v: set(map(tuple, (ndcg.loc[ii, v] - ndcg.loc[ii, BASE]).dropna().index)) for v in VARIANTS}
allsets = list(setA.values()) + list(setB.values())
report["identical_query_set_across_all_10_ranges"] = all(s == allsets[0] for s in allsets)
report["identical_query_set_n"] = len(allsets[0])

# ------------------------------------------------- dump paired diffs for scipy
dumps = {}
for v in VARIANTS:
    dumps[f"A_moa600_{v}"] = (regret.loc[ii, BASE] - regret.loc[ii, v]).dropna().to_numpy()
    dumps[f"B_moa600_{v}"] = (ndcg.loc[ii, v] - ndcg.loc[ii, BASE]).dropna().to_numpy()
jj = regret.index
for v in ["DART_coverage_worst"]:
    dumps[f"A_all765_{v}"] = (regret.loc[jj, BASE] - regret.loc[jj, v]).dropna().to_numpy()
np.savez(OUT / "paired_diffs.npz", **dumps)

# ------------------------------------------------- R3: Hit@1 macro-means
hit_src = REPO / "results/exp08_signature_baselines/summary.csv"
if hit_src.exists():
    h = pd.read_csv(hit_src)
    report["hit_columns"] = list(h.columns)
    report["hit_head"] = h.head(20).to_dict("records")
else:
    report["hit_src_missing"] = str(hit_src)

# ------------------------------------------------- R4/R5: JSON oracles
for name, p in [("class_c", "results/upgrade/class_c_functional_oracle.json"),
                ("oracle_shape", "results/upgrade/oracle_shape_test.json"),
                ("magctrl_v2", "results/upgrade/class_c_magnitude_control_v2.json")]:
    report[name] = json.loads((REPO / p).read_text())

cc = pd.read_csv(REPO / "results/upgrade/class_c_functional_oracle.csv")
unc = {c: float(cc[c].median()) for c in cc.columns if c.endswith("_uncentered")}
unc["energy_rho_partial_magmatch_median"] = float(cc["energy_rho_partial_magmatch"].median())
unc["n_rows"] = len(cc)
report["class_c_uncentered_medians"] = unc

# ------------------------------------------------- R4: exp13 real-data projection
proj = REPO / "results/exp13_real_data_projection/projection.csv"
if proj.exists():
    pj = pd.read_csv(proj)
    report["proj_columns"] = list(pj.columns)
    report["proj_shape"] = list(pj.shape)

(OUT / "audit_stage1.json").write_text(json.dumps(report, indent=1, default=str))
print("n_total", report["n_queries_total"], "| moa_defined", report["n_moa_defined"],
      "| rejected-rule", report["n_under_rejected_rule_n_gt_moa_gt_0"])
print("splits", report["split_type_counts"], "| sentinel", report["sentinel_by_split"])
print("identical set across 10 ranges:", report["identical_query_set_across_all_10_ranges"],
      report["identical_query_set_n"])
