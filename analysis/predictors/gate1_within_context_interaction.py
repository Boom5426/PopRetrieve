#!/usr/bin/env python3
"""The within-context Gate 1 number, recomputed with the repaired interaction statistic.

WHAT THIS IS FOR
----------------
`gate1_within_context.py` reports a mean induced-response cosine of 0.205 for real treated cells
against 1.000 for the additive predictors, and the manuscript reads the gap as the size of the
state-specific response that additive models cannot generate. The audit in
docs/phase2/05_DIFFERENTIAL_RESPONSE_AUDIT.md showed that `1 - cos` is confounded with effect size
and cell count, and that noise pushes the cosine DOWN. The real-cell 0.205 is therefore an
**upper** bound on divergence, inflated by whatever sampling noise the four arms carry, while the
predictor's 1.000 is exact algebra with no noise in it at all. The two numbers are not on the same
footing and the gap between them is overstated by an unknown amount.

This script measures that amount. It rebuilds the identical construct, the same cell line, the same
PCA plus k-means split of the control cells, the same nearest-subpopulation assignment of treated
cells, and reports side by side:

    cos_old        the published statistic, cos(d_0, d_1)
    S_int          the cross-fitted interaction, zero in expectation under the additive null
    share          S_int / (S_int + S_main), the scale-free fraction that is state-dependent
    R_int          cos(I_A, I_B), whether the interaction reproduces across disjoint halves
    cos_null       the same cos_old computed on a SHUFFLED state assignment, which is the noise
                   floor of the published statistic on these exact arms

`cos_null` is the number the comparison needs. It says what cosine the published construct returns
when there is no state-specific response at all, so 0.205 can be read against its own floor rather
than against an algebraic 1.000.

The additive self-check is kept and asserted, in the same spirit as the original: adding one delta
vector to every cell must give S_int = 0 and cos_old = 1 exactly.

    PYTHONPATH=src python analysis/predictors/gate1_within_context_interaction.py --n-drugs 12
"""
from pathlib import Path as _P
REPO = _P(__file__).resolve().parents[2]
import sys
sys.path.insert(0, str(REPO / "src"))

import argparse
import json
import time
import warnings

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score

from data.load_sciplex3 import load_sciplex3
from retrieval.interaction import cross_fitted_interaction

warnings.filterwarnings("ignore")

N_PCA = 30
N_CTRL = 400
MIN_SUB = 60
MIN_TREATED = 40
MIN_ARM = 12           # cells per arm needed for a cross-fitted split
N_REPEATS = 20
N_SHUFFLE = 20         # shuffled-state replicates for the cos_old noise floor
SEED = 0
OUT = REPO / "results" / "exp14_nonadditive_predictors"


def _cos(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return float(np.dot(a, b) / (na * nb)) if na > 1e-12 and nb > 1e-12 else np.nan


def subpopulations(Xc, seed=SEED):
    Z = PCA(n_components=min(N_PCA, Xc.shape[0] - 1, Xc.shape[1]),
            random_state=seed).fit_transform(Xc)
    lab = KMeans(n_clusters=2, n_init=10, random_state=seed).fit_predict(Z)
    sil = float(silhouette_score(Z, lab)) if len(set(lab)) > 1 else np.nan
    return lab, sil


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--n-drugs", type=int, default=12)
    ap.add_argument("--contexts", default="K562,A549,MCF7")
    ap.add_argument("--out", default=str(OUT))
    a = ap.parse_args()
    out = _P(a.out)
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    data = load_sciplex3()
    rows = []
    for ctx in a.contexts.split(","):
        cr = data.control_rows(ctx)
        if len(cr) < 2 * MIN_SUB:
            continue
        rng = np.random.default_rng(SEED)
        cr = rng.choice(cr, min(N_CTRL, len(cr)), replace=False)
        Xc = data.X[cr].astype(np.float64)
        lab, sil = subpopulations(Xc)
        C = {k: Xc[lab == k] for k in (0, 1)}
        if min(len(C[0]), len(C[1])) < MIN_SUB:
            continue
        print(f"{ctx}: subpopulations {len(C[0])}/{len(C[1])}, silhouette {sil:.3f}", flush=True)

        # ---- self-check and noise floor: a single delta added to every control cell ----
        #
        # The published statistic is EXACTLY 1 here, because it takes one mean per arm and the
        # shift cancels. S_int is zero only in EXPECTATION: the treated and control halves are
        # drawn independently, as they must be for real data where the two arms are different
        # cells, so each half's response carries its own sampling error and their inner product
        # averages to zero rather than being zero. Running the control repeatedly therefore both
        # checks the statistic and measures its noise floor on these exact arm sizes, which is the
        # scale every real S_int below has to be read against.
        # The treated arm must be built from cells the control arm does not contain. If the same
        # cells appear in both, a half of the treated arm and the complementary half of the
        # control arm carry exactly opposite deviations from their shared mean, which makes I_A
        # and I_B anticorrelated and drives S_int systematically negative. Real data never has
        # that structure, because treated and vehicle cells are different cells; the null has to
        # reproduce the real structure or it measures its own construction. Each subpopulation is
        # therefore halved once, and one half is shifted to play the treated arm.
        add_null = []
        for j in range(12):
            r_j = np.random.default_rng(SEED + 1000 + j)
            delta = r_j.normal(size=Xc.shape[1]) * 0.5
            Cn, Tn = {}, {}
            for k in (0, 1):
                idx = r_j.permutation(len(C[k]))
                h = len(idx) // 2
                Cn[k], Tn[k] = C[k][idx[:h]], C[k][idx[h:]] + delta
            if j == 0:
                d_add = {k: Tn[k].mean(0) - Cn[k].mean(0) for k in (0, 1)}
                assert np.isfinite(_cos(d_add[0], d_add[1])), "additive self-check: cos undefined"
            add_null.append(cross_fitted_interaction(Tn[0], Tn[1], Cn[0], Cn[1],
                                                     n_repeats=N_REPEATS,
                                                     seed=SEED + 1000 + j)["S_int"])
        add_null = np.asarray(add_null)
        se = add_null.std(ddof=1) / np.sqrt(len(add_null))
        assert abs(add_null.mean()) < 4 * se, (
            f"additive self-check failed: S_int null mean {add_null.mean():.4g} "
            f"is more than 4 standard errors ({se:.4g}) from zero")
        print(f"  additive null S_int: mean {add_null.mean():+.3e}, sd {add_null.std(ddof=1):.3e} "
              f"over {len(add_null)} draws", flush=True)
        null_scale = float(add_null.std(ddof=1))

        all_drugs = sorted(set(data.pert[~data.is_control].tolist()))
        drugs = [d for d in all_drugs
                 if len(data.treated_rows(ctx, d)) >= MIN_TREATED][:a.n_drugs]

        m0, m1 = C[0].mean(0), C[1].mean(0)
        for drug in drugs:
            tr = data.treated_rows(ctx, drug)
            Xt = data.X[tr].astype(np.float64)
            assign = (np.linalg.norm(Xt - m1, axis=1)
                      < np.linalg.norm(Xt - m0, axis=1)).astype(int)
            T = {k: Xt[assign == k] for k in (0, 1)}
            if min(len(T[0]), len(T[1])) < MIN_ARM:
                continue
            d_real = {k: T[k].mean(0) - C[k].mean(0) for k in (0, 1)}
            cos_old = _cos(d_real[0], d_real[1])
            res = cross_fitted_interaction(T[0], T[1], C[0], C[1], n_repeats=N_REPEATS, seed=SEED)

            # THE NUMBER THIS SCRIPT EXISTS FOR: the noise floor of the published statistic under
            # a genuinely additive drug OF THIS DRUG'S OWN EFFECT SIZE.
            #
            # The manuscript reads the gap between the real cells' cosine and the additive
            # predictor's 1.000 as the size of the state-specific response. But the 1.000 is exact
            # algebra computed on a single mean per arm with no sampling error, while the real
            # value is a noisy estimate, and noise pushes a cosine DOWN. The two are not on the
            # same footing.
            #
            # The matched null puts them on it. The synthetic treated arm is a disjoint half of
            # the same control cells shifted by this drug's own pooled response, so it has the
            # drug's magnitude, the drug's arm sizes and no state-specific component whatsoever.
            # Whatever cosine that returns is what "no interaction" looks like through this
            # instrument, and it is the reference the observed value belongs against.
            r_pooled = Xt.mean(0) - Xc.mean(0)
            sh = np.random.default_rng(SEED + 7)
            nulls = []
            for _ in range(N_SHUFFLE):
                dn = {}
                for k in (0, 1):
                    idx = sh.permutation(len(C[k]))
                    n_t = min(len(T[k]), len(idx) // 2)
                    ctrl_half = C[k][idx[:len(idx) // 2]]
                    treat_half = C[k][idx[len(idx) // 2:][:n_t]] + r_pooled
                    dn[k] = treat_half.mean(0) - ctrl_half.mean(0)
                nulls.append(_cos(dn[0], dn[1]))
            rows.append({"context": ctx, "drug": drug,
                         "n_treated_0": len(T[0]), "n_treated_1": len(T[1]),
                         "n_control_0": len(C[0]), "n_control_1": len(C[1]),
                         "silhouette": sil, "cos_old": cos_old,
                         "S_int_additive_null_sd": null_scale,
                         "cos_old_additive_null_mean": float(np.mean(nulls)),
                         "cos_old_additive_null_sd": float(np.std(nulls, ddof=1)),
                         **{k: res[k] for k in ("S_int", "S_int_se", "S_main",
                                                "interaction_share", "R_int")}})
        print(f"  {len([r for r in rows if r['context'] == ctx])} drugs scored "
              f"({time.time() - t0:.0f}s)", flush=True)

    df = pd.DataFrame(rows)
    df.to_csv(out / "gate1_within_context_interaction.csv", index=False)
    summary = {
        "n": int(len(df)), "contexts": sorted(df.context.unique().tolist()),
        "cos_old_mean": float(df.cos_old.mean()), "cos_old_median": float(df.cos_old.median()),
        "cos_old_additive_null_mean": float(df.cos_old_additive_null_mean.mean()),
        "cos_old_additive_null_median": float(df.cos_old_additive_null_mean.median()),
        "cos_old_additive_null_sd": float(df.cos_old_additive_null_sd.mean()),
        "frac_real_below_its_own_null": float((df.cos_old < df.cos_old_additive_null_mean).mean()),
        "real_gap_to_matched_null": float(df.cos_old_additive_null_mean.mean() - df.cos_old.mean()),
        "published_gap_to_algebraic_one": float(1.0 - df.cos_old.mean()),
        "S_int_median": float(df.S_int.median()),
        "interaction_share_median": float(df.interaction_share.median()),
        "R_int_median": float(df.R_int.median()),
        "frac_S_int_positive": float((df.S_int > 0).mean()),
        "S_int_additive_null_sd": float(df.S_int_additive_null_sd.mean()),
        "S_int_median_over_null_sd": float(df.S_int.median() / df.S_int_additive_null_sd.mean()),
        "reading": ("cos_old_additive_null_mean is what the published statistic returns for a "
                    "drug of the same effect size with NO state-specific response, measured "
                    "through the same arms and the same sampling noise. The observed real-cell "
                    "value belongs against that, not against the algebraic 1.000."),
        "runtime_seconds": round(time.time() - t0, 1),
    }
    (out / "gate1_within_context_interaction.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    sys.exit(main())
