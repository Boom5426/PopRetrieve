#!/usr/bin/env python3
"""Does the ORACLE'S OWN STATISTICAL SHAPE decide which retrieval method wins?

THE OBSERVATION THAT FORCED THIS TEST
-------------------------------------
Two independent external oracles disagree about whether distributional retrieval beats the mean:

  GDSC functional similarity (class_c_functional_oracle.py)
      energy +0.276  >  mean +0.083     distributional retrieval WINS
  Surface-protein response (class_c_protein_oracle.py)
      energy +0.142  <  mean +0.241     the MEAN wins, in all three immune conditions

Both are external, neither is visible to any scorer, and they point opposite ways. Before writing
either up, notice what the protein oracle actually is:

    oracle_mean(q, c) = cos( MEAN protein delta of q , MEAN protein delta of c )

It collapses the protein readout to a mean. The RNA mean-cosine scorer computes the same statistic
in a different modality. A mean-shaped oracle is structurally matched to a mean-shaped scorer, and
energy, which compares distributions, is being graded on a criterion that threw its distribution
away. That is the mirror image of the Class-A circularity this paper is about, and if it explains
the protein result then the protein result is not evidence that the mean is biologically better.

THE TEST
--------
Build the oracle from the SAME cells, the SAME proteins, twice, changing ONLY its statistical form:

    oracle_MEAN(q,c) = cos( mean protein delta_q , mean protein delta_c )
    oracle_DIST(q,c) = -energy_distance( protein cells of q , protein cells of c )
                       (both centred on that condition's control protein cells, so it is a
                        response distance and not a baseline-identity distance)

Then score the SAME two RNA rankings against both.

  If the mean scorer wins under oracle_MEAN and the energy scorer wins under oracle_DIST, the
  winner is decided by the oracle's SHAPE, not by which method is biologically right. That is the
  strongest form of this paper's thesis: even among independent, external, oracle-blind criteria,
  objective alignment silently picks the victor.

  If the mean wins under BOTH, the mean is genuinely better on this readout and we say so, and the
  protein result stands as evidence against distributional retrieval.

Both outcomes are reportable and we do not know which we will get.

    PYTHONPATH=src python analysis/class_c/oracle_shape_test.py
"""
from pathlib import Path as _P
REPO = _P(__file__).resolve().parents[2]
import sys
sys.path.insert(0, str(REPO / "src"))

import json
import warnings

import numpy as np
import pandas as pd
from scipy import stats

from retrieval.metrics import score_energy, score_mean_cosine

warnings.filterwarnings("ignore")

SEED = 42
MIN_CELLS = 60
MAX_CELLS = 250
ISOTYPES = ["Rat_IgG2a", "Mouse_IgG1", "Mouse_IgG2a", "Mouse_IgG2b"]

RAW = REPO / "data" / "raw" / "frangieh2021"
OUT = REPO / "results" / "upgrade"


def _cos(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return float(np.dot(a, b) / (na * nb)) if na > 1e-12 and nb > 1e-12 else np.nan


def clr(X):
    L = np.log1p(X)
    return (L - L.mean(1, keepdims=True)).astype(np.float32)


def main():
    import anndata as ad
    import scanpy as sc

    p = ad.read_h5ad(RAW / "FrangiehIzar2021_protein.h5ad")
    r = ad.read_h5ad(RAW / "FrangiehIzar2021_RNA.h5ad")
    # Hoist the lookup set out of the comprehension. Inline, the condition rebuilds a
    # 218k-element set on every one of 218k iterations, which is quadratic and does not finish.
    rna_barcodes = set(r.obs_names)
    shared = [b for b in p.obs_names if b in rna_barcodes]
    p, r = p[shared].copy(), r[shared].copy()
    assert list(p.obs_names) == list(r.obs_names)
    print(f"joined by barcode: {len(shared)} cells", flush=True)

    keep = [i for i, v in enumerate(p.var_names) if str(v) not in ISOTYPES]
    P = clr(p.X.toarray() if hasattr(p.X, "toarray") else np.asarray(p.X))[:, keep]

    sc.pp.normalize_total(r, target_sum=1e4)
    sc.pp.log1p(r)
    sc.pp.highly_variable_genes(r, n_top_genes=2000, flavor="seurat")
    r = r[:, r.var.highly_variable].copy()
    R = (r.X.toarray() if hasattr(r.X, "toarray") else np.asarray(r.X)).astype(np.float32)
    pert = r.obs["perturbation"].astype(str).values
    is_ctrl = pert == "control"
    cond = r.obs["perturbation_2"].astype(str).values
    print(f"RNA {R.shape} | protein {P.shape} | conditions {sorted(set(cond.tolist()))}\n",
          flush=True)

    rows = []
    for cnd in sorted(set(cond.tolist())):
        m = cond == cnd
        ci = np.where(m & is_ctrl)[0]
        if len(ci) < MIN_CELLS:
            continue
        rng = np.random.default_rng(SEED)
        rna_ctrl, prot_ctrl = R[ci].mean(0), P[ci].mean(0)
        # control protein cells, used to centre the DISTRIBUTIONAL protein oracle so that it
        # measures a RESPONSE distance rather than a baseline-identity distance
        pc = P[rng.choice(ci, min(len(ci), MAX_CELLS), replace=False)] - prot_ctrl

        kos, rna_cells, prot_resp, rna_d, prot_d = [], {}, {}, {}, {}
        for k in sorted(set(pert[m & ~is_ctrl].tolist())):
            idx = np.where(m & (pert == k) & ~is_ctrl)[0]
            if len(idx) < MIN_CELLS:
                continue
            sub = rng.choice(idx, min(len(idx), MAX_CELLS), replace=False)
            kos.append(k)
            rna_cells[k] = R[sub].astype(np.float64)
            prot_resp[k] = (P[sub] - prot_ctrl).astype(np.float64)   # per-cell protein RESPONSE
            rna_d[k] = R[idx].mean(0) - rna_ctrl
            prot_d[k] = P[idx].mean(0) - prot_ctrl
        if len(kos) < 10:
            continue
        print(f"{cnd}: {len(kos)} knockouts", flush=True)

        for qi, q in enumerate(kos):
            if qi % 50 == 0:
                print(f"  {cnd} {qi}/{len(kos)}", flush=True)
            cand = [c for c in kos if c != q]
            e_rna, m_rna, g_rna, o_mean, o_dist = [], [], [], [], []
            qmag = float(np.linalg.norm(rna_d[q]))
            for c in cand:
                # the two RNA rankings under test (identical in both columns)
                e_rna.append(score_energy(rna_cells[q], rna_cells[c],
                                          max_cells=MAX_CELLS, seed=SEED))
                m_rna.append(score_mean_cosine(rna_cells[c], rna_cells[q],
                                               control_P=rna_ctrl, control_Q=rna_ctrl))
                # THE CONTROL THAT DECIDES WHAT THE SHAPE EFFECT ACTUALLY IS.
                # Both "distributional" objects here are energy distances, and an energy distance
                # is known to track a candidate's own response magnitude (rho = +0.791). So a
                # magnitude-to-magnitude channel would reproduce the swap without any distribution
                # being compared. Rank by how closely the candidate's RNA response magnitude
                # matches the query's: query-dependent, and it compares no distributions at all.
                g_rna.append(-abs(float(np.linalg.norm(rna_d[c])) - qmag))
                # THE SAME PROTEIN DATA, TWO ORACLE SHAPES
                o_mean.append(_cos(prot_d[q], prot_d[c]))
                o_dist.append(score_energy(prot_resp[q], prot_resp[c],
                                           max_cells=MAX_CELLS, seed=SEED))
            e_rna, m_rna, g_rna = np.asarray(e_rna), np.asarray(m_rna), np.asarray(g_rna)
            o_mean, o_dist = np.asarray(o_mean), np.asarray(o_dist)
            rows.append({
                "condition": cnd, "query": q, "n_cand": len(cand),
                "energy_vs_oracleMEAN": float(stats.spearmanr(e_rna, o_mean)[0]),
                "mean_vs_oracleMEAN": float(stats.spearmanr(m_rna, o_mean)[0]),
                "magmatch_vs_oracleMEAN": float(stats.spearmanr(g_rna, o_mean)[0]),
                "energy_vs_oracleDIST": float(stats.spearmanr(e_rna, o_dist)[0]),
                "mean_vs_oracleDIST": float(stats.spearmanr(m_rna, o_dist)[0]),
                "magmatch_vs_oracleDIST": float(stats.spearmanr(g_rna, o_dist)[0]),
            })

    df = pd.DataFrame(rows)
    df.to_csv(OUT / "oracle_shape_test.csv", index=False)

    print(f"\n{'='*84}")
    print("SAME CELLS. SAME PROTEINS. SAME TWO RNA RANKINGS. ONLY THE ORACLE'S SHAPE CHANGES.")
    print(f"\n{'':22s} {'oracle = MEAN protein':>24s} {'oracle = protein DIST':>24s}")
    print("-" * 84)
    res = {"n_queries": int(len(df))}
    LAB = {"energy": "energy (distributional)", "mean": "mean cosine (incumbent)",
           "magmatch": "magnitude scalar [CTRL]"}
    for scorer in ["energy", "mean", "magmatch"]:
        a = float(df[f"{scorer}_vs_oracleMEAN"].median())
        b = float(df[f"{scorer}_vs_oracleDIST"].median())
        res[f"{scorer}_vs_oracleMEAN"] = a
        res[f"{scorer}_vs_oracleDIST"] = b
        print(f"  {LAB[scorer]:22s} {a:>+22.4f} {b:>+22.4f}")
    print("-" * 84)

    # Does the magnitude scalar reproduce the swap? If it tracks the DIST oracle about as well as
    # energy does, then the "shape effect" is a magnitude channel shared by two energy distances,
    # not a distribution-to-distribution effect, and it must be reported as such.
    e_d, g_d = res["energy_vs_oracleDIST"], res["magmatch_vs_oracleDIST"]
    e_m, g_m = res["energy_vs_oracleMEAN"], res["magmatch_vs_oracleMEAN"]
    res["magnitude_confound"] = {
        "energy_minus_magmatch_under_DIST": e_d - g_d,
        "energy_minus_magmatch_under_MEAN": e_m - g_m,
        "reading": ("If energy barely exceeds the magnitude scalar under the DIST oracle, the "
                    "swap is a magnitude channel shared by two energy distances rather than a "
                    "distributional effect. The scalar compares no distributions at all."),
    }
    print(f"\n  MAGNITUDE CONTROL. Under the DIST-shaped oracle, energy {e_d:+.4f} against the "
          f"scalar {g_d:+.4f} (difference {e_d - g_d:+.4f}).")
    print(f"  Under the MEAN-shaped oracle, energy {e_m:+.4f} against the scalar {g_m:+.4f} "
          f"(difference {e_m - g_m:+.4f}).")

    win_mean_oracle = "energy" if res["energy_vs_oracleMEAN"] > res["mean_vs_oracleMEAN"] else "mean"
    win_dist_oracle = "energy" if res["energy_vs_oracleDIST"] > res["mean_vs_oracleDIST"] else "mean"
    res["winner_under_mean_oracle"] = win_mean_oracle
    res["winner_under_dist_oracle"] = win_dist_oracle
    print(f"\n  winner under the MEAN-shaped oracle        : {win_mean_oracle}")
    print(f"  winner under the DISTRIBUTION-shaped oracle: {win_dist_oracle}")

    res["verdict"] = (
        "THE ORACLE'S SHAPE PICKS THE WINNER. The same two rankings, scored on the same cells and "
        "the same proteins, swap places when the oracle is rebuilt from a mean to a distribution. "
        "Neither method is 'better' on this readout; the criterion decides. Objective alignment "
        "operates even among external, oracle-blind criteria, which is the strongest form of this "
        "paper's claim."
        if win_mean_oracle != win_dist_oracle else
        f"NO SHAPE EFFECT: {win_mean_oracle} wins under BOTH oracle shapes. The advantage is a "
        f"property of the method, not of the criterion, and on this readout it belongs to "
        f"{win_mean_oracle}.")
    print(f"\nVERDICT: {res['verdict']}")

    print("\nPER CONDITION (the honest unit)")
    res["per_condition"] = {}
    for cnd, s in df.groupby("condition"):
        d = {c: float(s[c].median()) for c in
             ["energy_vs_oracleMEAN", "mean_vs_oracleMEAN", "magmatch_vs_oracleMEAN",
              "energy_vs_oracleDIST", "mean_vs_oracleDIST", "magmatch_vs_oracleDIST"]}
        d["n"] = int(len(s))
        d["flips"] = bool((d["energy_vs_oracleMEAN"] > d["mean_vs_oracleMEAN"]) !=
                          (d["energy_vs_oracleDIST"] > d["mean_vs_oracleDIST"]))
        res["per_condition"][cnd] = d
        print(f"  {cnd:12s} (n={d['n']:>3d}) MEAN-oracle: energy {d['energy_vs_oracleMEAN']:+.3f} "
              f"vs mean {d['mean_vs_oracleMEAN']:+.3f} | DIST-oracle: energy "
              f"{d['energy_vs_oracleDIST']:+.3f} vs mean {d['mean_vs_oracleDIST']:+.3f} | "
              f"flips: {d['flips']}")

    json.dump(res, open(OUT / "oracle_shape_test.json", "w"), indent=2)
    print(f"\nwrote {OUT/'oracle_shape_test.csv'} and .json")


if __name__ == "__main__":
    main()
