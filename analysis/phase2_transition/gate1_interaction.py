#!/usr/bin/env python
"""Gate 1, rebuilt: cross-fitted drug-by-state interaction on Tahoe-100M plate 3.

Replaces the ``D = 1 - cos(r_G1, r_G2M)`` statistic audited in
docs/phase2/05_DIFFERENTIAL_RESPONSE_AUDIT.md, which turned out to be largely a signal-to-noise
measure: it correlated -0.584 with the response norm and -0.529 with the number of treated cells,
so the weakest drugs scored as the most "differentially responding". The replacement is defined in
src/retrieval/interaction.py; this script measures it on the same 3,992 queries, side by side with
the old one, and runs the two sanity checks that need real material.

    S_int = <I_A, I_B> / p      cross-fitted interaction strength, zero under the additive null
    R_int = cos(I_A, I_B)       is the interaction reproducible across disjoint halves?

Splits are library-preparation-disjoint wherever a condition spans at least two sublibraries, which
is the same partition Phase A uses, so a half never shares a library prep with its counterpart.

THE TWO CHECKS THAT NEED REAL DATA
----------------------------------
Check 3, positive control. Tahoe has no constructed mixture, so one is built from the plate itself:
a synthetic condition whose G1 cells come from drug A and whose G2M cells come from drug B. Its
interaction is real and large by construction, and it is made from the same cells, the same states
and the same arm sizes as the queries it is compared against, so a failure to detect it cannot be
blamed on the material.

Check 5, effect-size audit. The old statistic's fatal property was a mechanical negative
correlation with response magnitude. The new one is allowed to correlate with magnitude, because a
stronger drug may genuinely interact more, but it must not reproduce the inversion.

OUTPUTS (--out)
---------------
    interaction_per_query.csv   S_int, R_int, the old D, response norms and arm sizes per query
    positive_control.csv        the synthetic interacting conditions of check 3
    checks.json                 check 5's correlations and the summary of check 3
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.sparse as sp
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from audit_eligibility import read_obs, sha256                       # noqa: E402
import phase2_common as pc                                           # noqa: E402
from retrieval.interaction import cross_fitted_interaction, permutation_null   # noqa: E402

STATES = ("G1", "G2M")
MIN_ARM_CELLS = 50           # per arm, matching phase_c_gates.py so the two are comparable
MAX_ARM_CELLS = 400          # cap, for cost; drawn without replacement, seeded
N_REPEATS = 10               # A/B splits averaged per query
N_PERM = 20                  # permutation replicates, on the queries selected for the null
PERM_EVERY = 10              # run the permutation null on every Nth query, for cost
N_POSITIVE_CONTROL = 200     # synthetic interacting conditions
SEED = 0


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def _cos(a, b) -> float:
    na, nb = float(np.linalg.norm(a)), float(np.linalg.norm(b))
    return float("nan") if na < 1e-12 or nb < 1e-12 else float(a @ b / (na * nb))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--h5ad", required=True)
    ap.add_argument("--freeze-dir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--limit-contexts", type=int, default=0)
    ap.add_argument("--no-hash", action="store_true")
    a = ap.parse_args()

    h5ad, freeze_dir, out = Path(a.h5ad).resolve(), Path(a.freeze_dir), Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    freeze = json.loads((freeze_dir / "task_freeze.json").read_text())
    if freeze["input_sha256"] and not a.no_hash and sha256(h5ad) != freeze["input_sha256"]:
        raise ValueError("input file does not match the freeze")
    elig = pd.read_csv(freeze_dir / "query_eligibility.csv")
    ctx_tab = pd.read_csv(freeze_dir / "context_summary.csv")
    contexts = ctx_tab.loc[ctx_tab.context_usable, "cell_name"].tolist()
    if a.limit_contexts:
        contexts = contexts[:a.limit_contexts]
    queries_by_ctx = {c: g.loc[g.eligible, "drug"].tolist() for c, g in elig.groupby("cell_name")}

    import anndata as ad
    log(f"reading {h5ad}")
    adata = ad.read_h5ad(h5ad)
    X = adata.X
    if not sp.isspmatrix_csr(X):
        X = sp.csr_matrix(X)
    X = X.astype(np.float32)
    obs = read_obs(h5ad, ["cell_name", "drug", "phase", "sublibrary"])
    del adata
    cell_name = obs.cell_name.to_numpy()
    drug = obs.drug.to_numpy()
    phase = obs.phase.to_numpy()
    sublib = obs.sublibrary.to_numpy()
    log(f"X {X.shape}")

    def dense(rows):
        return np.asarray(X[rows].todense(), dtype=np.float32)

    rows, pos_rows = [], []
    for ci, c in enumerate(contexts):
        in_ctx = cell_name == c
        rng = np.random.default_rng([SEED, ci])
        ctrl = np.flatnonzero(in_ctx & (drug == pc.CONTROL_DRUG))
        ctrl_state, ctrl_cells, ctrl_sub = {}, {}, {}
        ok_ctrl = True
        for s in STATES:
            r = ctrl[phase[ctrl] == s]
            if len(r) < MIN_ARM_CELLS:
                ok_ctrl = False
                break
            if len(r) > MAX_ARM_CELLS:
                r = rng.choice(r, MAX_ARM_CELLS, replace=False)
            ctrl_state[s] = r
            ctrl_cells[s] = dense(r)
            ctrl_sub[s] = sublib[r]
        if not ok_ctrl:
            log(f"context {c}: vehicle arm too small in one state; skipped")
            continue

        treated_cache = {}
        for q in queries_by_ctx[c]:
            r = np.flatnonzero(in_ctx & (drug == q))
            arms, subs, sizes = {}, {}, {}
            small = False
            for s in STATES:
                rs = r[phase[r] == s]
                if len(rs) < MIN_ARM_CELLS:
                    small = True
                    break
                sizes[s] = len(rs)
                if len(rs) > MAX_ARM_CELLS:
                    rs = rng.choice(rs, MAX_ARM_CELLS, replace=False)
                arms[s] = dense(rs)
                subs[s] = sublib[rs]
            rec = {"cell_line": c, "drug": q,
                   "n_treated_G1": int(sizes.get("G1", 0)), "n_treated_G2M": int(sizes.get("G2M", 0)),
                   "n_vehicle_G1": len(ctrl_state["G1"]), "n_vehicle_G2M": len(ctrl_state["G2M"])}
            if small:
                rec.update({k: np.nan for k in
                            ("S_int", "S_int_se", "R_int", "R_int_se", "half_norm_mean",
                             "D_old", "induced_cosine", "norm_r_G1", "norm_r_G2M", "z_perm",
                             "p_perm")})
                rows.append(rec)
                continue

            res = cross_fitted_interaction(
                arms["G1"], arms["G2M"], ctrl_cells["G1"], ctrl_cells["G2M"],
                n_repeats=N_REPEATS, seed=SEED + ci,
                groups=(subs["G1"], subs["G2M"], ctrl_sub["G1"], ctrl_sub["G2M"]))
            r1 = arms["G1"].mean(0) - ctrl_cells["G1"].mean(0)
            r2 = arms["G2M"].mean(0) - ctrl_cells["G2M"].mean(0)
            cs = _cos(r1, r2)
            rec.update(res)
            rec.update({"D_old": 1.0 - cs, "induced_cosine": cs,
                        "norm_r_G1": float(np.linalg.norm(r1)),
                        "norm_r_G2M": float(np.linalg.norm(r2))})
            if len(rows) % PERM_EVERY == 0:
                pn = permutation_null(arms["G1"], arms["G2M"], ctrl_cells["G1"], ctrl_cells["G2M"],
                                      n_perm=N_PERM, n_repeats=4, seed=SEED + ci)
                rec.update({"z_perm": pn["z"], "p_perm": pn["p_two_sided"],
                            "null_sd": pn["null_sd"]})
            else:
                rec.update({"z_perm": np.nan, "p_perm": np.nan})
            rows.append(rec)
            treated_cache[q] = (arms, subs)

        # ---- check 3: synthetic positive controls, built from this context's own cells ----
        names = sorted(treated_cache)
        if len(names) >= 2:
            per_ctx = max(1, N_POSITIVE_CONTROL // max(len(contexts), 1))
            for j in range(per_ctx):
                ia, ib = rng.choice(len(names), 2, replace=False)
                da, db = names[ia], names[ib]
                ga = treated_cache[da][0]["G1"]
                gb = treated_cache[db][0]["G2M"]
                sa = treated_cache[da][1]["G1"]
                sb = treated_cache[db][1]["G2M"]
                res = cross_fitted_interaction(
                    ga, gb, ctrl_cells["G1"], ctrl_cells["G2M"], n_repeats=N_REPEATS,
                    seed=SEED + 991 + j,
                    groups=(sa, sb, ctrl_sub["G1"], ctrl_sub["G2M"]))
                r1 = ga.mean(0) - ctrl_cells["G1"].mean(0)
                r2 = gb.mean(0) - ctrl_cells["G2M"].mean(0)
                pos_rows.append({"cell_line": c, "drug_G1": da, "drug_G2M": db,
                                 **res, "D_old": 1.0 - _cos(r1, r2)})
        log(f"context {ci + 1}/{len(contexts)} {c} done ({time.time() - t0:.0f}s)")

    per_query = pd.DataFrame(rows)
    per_query.to_csv(out / "interaction_per_query.csv", index=False)
    pos = pd.DataFrame(pos_rows)
    pos.to_csv(out / "positive_control.csv", index=False)

    d = per_query.dropna(subset=["S_int"])
    d = d.assign(norm_mean=(d.norm_r_G1 + d.norm_r_G2M) / 2,
                 n_treated=d.n_treated_G1 + d.n_treated_G2M)
    checks = {
        "n_scored": int(len(d)), "n_queries": int(len(per_query)),
        "check5_effect_size_audit": {
            "spearman_S_int_vs_response_norm": float(spearmanr(d.S_int, d.norm_mean).statistic),
            "spearman_S_int_vs_n_treated": float(spearmanr(d.S_int, d.n_treated).statistic),
            "spearman_R_int_vs_response_norm": float(spearmanr(d.R_int, d.norm_mean).statistic),
            "spearman_D_old_vs_response_norm": float(spearmanr(d.D_old, d.norm_mean).statistic),
            "spearman_D_old_vs_n_treated": float(spearmanr(d.D_old, d.n_treated).statistic),
            "spearman_S_int_vs_D_old": float(spearmanr(d.S_int, d.D_old).statistic),
        },
        "observed": {
            "S_int_median": float(d.S_int.median()), "S_int_mean": float(d.S_int.mean()),
            "S_int_q05": float(d.S_int.quantile(0.05)), "S_int_q95": float(d.S_int.quantile(0.95)),
            "frac_S_int_positive": float((d.S_int > 0).mean()),
            "R_int_median": float(d.R_int.median()),
            "D_old_median": float(d.D_old.median()),
        },
        "check3_positive_control": ({
            "n": int(len(pos)),
            "S_int_median": float(pos.S_int.median()),
            "R_int_median": float(pos.R_int.median()),
            "D_old_median": float(pos.D_old.median()),
            "ratio_to_real_median": (float(pos.S_int.median() / d.S_int.median())
                                     if d.S_int.median() else float("nan")),
        } if len(pos) else {}),
    }
    perm = per_query.dropna(subset=["z_perm"])
    if len(perm):
        checks["permutation_null"] = {
            "n": int(len(perm)),
            "median_z": float(perm.z_perm.median()),
            "frac_p_below_0.1": float((perm.p_perm < 0.1).mean()),
            "frac_z_above_2": float((perm.z_perm > 2).mean()),
        }
    (out / "checks.json").write_text(json.dumps(checks, indent=2) + "\n")
    log(json.dumps(checks, indent=2))
    log(f"wrote {out} ({time.time() - t0:.0f}s)")


if __name__ == "__main__":
    sys.exit(main())
