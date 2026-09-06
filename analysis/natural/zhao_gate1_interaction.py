#!/usr/bin/env python3
"""The patient-glioblastoma Gate 1 number, recomputed with the repaired interaction statistic.

`zhao_two_gates.py` reports a median induced-response cosine of 0.566 between the malignant and
myeloid compartments and reads the distance from 1 as the size of the compartment-specific
response. The audit in docs/phase2/05_DIFFERENTIAL_RESPONSE_AUDIT.md showed that `1 - cos` is
confounded with effect size and cell count, and that sampling noise pushes the cosine down, so a
value below 1 is not by itself evidence of a compartment-specific response.

This recomputes the same construct, the same patients, the same compartments, the same
compartment-matched controls, and adds the two references the published number lacks:

    cos_old                     the published statistic
    cos_old_additive_null       what it returns for a drug of the SAME effect size with no
                                compartment-specific response at all, built from a disjoint half
                                of the same control cells shifted by the drug's own pooled
                                response. Same arms, same sizes, same noise, no interaction.
    S_int, share, R_int         the cross-fitted interaction (src/retrieval/interaction.py)

The published value belongs against `cos_old_additive_null`, not against 1.

    PYTHONPATH=src python analysis/natural/zhao_gate1_interaction.py
"""
from pathlib import Path as _P
REPO = _P(__file__).resolve().parents[2]
import sys
sys.path.insert(0, str(REPO / "src"))

import argparse
import json
import time

import numpy as np
import pandas as pd

from data.load_zhao_gbm import ZhaoGBM
from retrieval.interaction import cross_fitted_interaction

PAIR = ("malignant", "myeloid")
MIN_CELLS = 30
MIN_ARM = 12
N_REPEATS = 20
N_NULL = 20
SEED = 0
OUT = REPO / "results" / "zhao_gbm"


def _cos(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return float(np.dot(a, b) / (na * nb)) if na > 1e-12 and nb > 1e-12 else np.nan


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=str(OUT))
    a = ap.parse_args()
    out = _P(a.out)
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    d = ZhaoGBM()
    rows = []
    for p in d.patients:
        drugs = sorted({x for x in d.pert[d.patient == p] if x != "control"})
        ctrl_rows = {}
        for c in PAIR:
            r = d.rows(patient=p, compartment=c, control=True)
            if len(r) >= MIN_CELLS:
                ctrl_rows[c] = r
        if len(ctrl_rows) < 2:
            continue
        C = {c: d.X[ctrl_rows[c]].astype(np.float64) for c in PAIR}

        for drug in drugs:
            tr = {c: d.rows(patient=p, drug=drug, compartment=c) for c in PAIR}
            if any(len(tr[c]) < MIN_CELLS for c in PAIR):
                continue
            T = {c: d.X[tr[c]].astype(np.float64) for c in PAIR}
            dk = {c: T[c].mean(0) - C[c].mean(0) for c in PAIR}
            cos_old = _cos(dk[PAIR[0]], dk[PAIR[1]])
            if min(len(T[c]) for c in PAIR) < MIN_ARM or min(len(C[c]) for c in PAIR) < 2 * MIN_ARM:
                res = {k: np.nan for k in ("S_int", "S_int_se", "S_main",
                                           "interaction_share", "R_int")}
            else:
                res = cross_fitted_interaction(T[PAIR[0]], T[PAIR[1]], C[PAIR[0]], C[PAIR[1]],
                                               n_repeats=N_REPEATS, seed=SEED)
                res = {k: res[k] for k in ("S_int", "S_int_se", "S_main",
                                           "interaction_share", "R_int")}

            # effect-size-matched additive null, exactly as in the SciPlex3 version
            Xt = np.concatenate([T[c] for c in PAIR])
            Xc = np.concatenate([C[c] for c in PAIR])
            r_pooled = Xt.mean(0) - Xc.mean(0)
            sh = np.random.default_rng(SEED + 7)
            nulls = []
            for _ in range(N_NULL):
                dn = {}
                for c in PAIR:
                    idx = sh.permutation(len(C[c]))
                    half = len(idx) // 2
                    n_t = min(len(T[c]), len(idx) - half)
                    dn[c] = (C[c][idx[half:][:n_t]] + r_pooled).mean(0) - C[c][idx[:half]].mean(0)
                nulls.append(_cos(dn[PAIR[0]], dn[PAIR[1]]))

            rows.append({"patient": p, "drug": drug,
                         "n_malignant": len(tr[PAIR[0]]), "n_myeloid": len(tr[PAIR[1]]),
                         "n_ctrl_malignant": len(ctrl_rows[PAIR[0]]),
                         "n_ctrl_myeloid": len(ctrl_rows[PAIR[1]]),
                         "cos_old": cos_old,
                         "cos_old_additive_null_mean": float(np.mean(nulls)),
                         "cos_old_additive_null_sd": float(np.std(nulls, ddof=1)),
                         **res})

    df = pd.DataFrame(rows)
    df.to_csv(out / "zhao_gate1_interaction.csv", index=False)
    ok = df.dropna(subset=["S_int"])
    summary = {
        "n_pairs": int(len(df)), "n_with_interaction": int(len(ok)),
        "patients": sorted(df.patient.unique().tolist()),
        "cos_old_median": float(df.cos_old.median()),
        "cos_old_additive_null_median": float(df.cos_old_additive_null_mean.median()),
        "frac_below_own_null": float((df.cos_old < df.cos_old_additive_null_mean).mean()),
        "published_gap_to_one": float(1.0 - df.cos_old.median()),
        "honest_gap_to_matched_null": float(df.cos_old_additive_null_mean.median()
                                            - df.cos_old.median()),
        "S_int_median": float(ok.S_int.median()) if len(ok) else None,
        "interaction_share_median": float(ok.interaction_share.median()) if len(ok) else None,
        "R_int_median": float(ok.R_int.median()) if len(ok) else None,
        "frac_S_int_positive": float((ok.S_int > 0).mean()) if len(ok) else None,
        "runtime_seconds": round(time.time() - t0, 1),
    }
    (out / "zhao_gate1_interaction.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    sys.exit(main())
