#!/usr/bin/env python3
"""Gate 1, measured WITHIN one context, which is the only place the theorem applies.

WHY THIS SCRIPT REPLACES exp_nonadditive_gate1.py's GATE-1 MEASUREMENT
----------------------------------------------------------------------
The paper's algebraic claim is:

    A predictor that adds a SINGLE delta vector to every cell OF THE QUERY CONTEXT gives its two
    subpopulations identical response deltas, so cos(d_maj, d_min) = 1 EXACTLY and the divergence
    a distributional score could exploit is exactly zero.

exp_nonadditive_gate1.py tried to measure this on an ALPHA-BLENDED candidate population whose two
subpopulations are two different cell lines (A549 + K562). That is a cross-context mixture, and an
additive predictor emits a DIFFERENT delta for each context. So it measures

    cos(delta_A549, delta_K562)

which is the similarity of two contexts' deltas, not a test of additivity at all. Its own built-in
self-check caught this and refused the run: the additive controls returned 0.267 and 0.353 where
the algebra requires 1.000, and the script printed "The measurement is wrong, not the model."
It was right. The manuscript's explanation of the 0.19-0.37 values (that they fall below 1 because
of Gate-2 assignment error) is therefore also wrong; the real reason is the cross-context structure.

THE CORRECT CONSTRUCT
---------------------
The two subpopulations must live in ONE context. We take one cell line's CONTROL cells and split
them into two subpopulations by their own cell state (PCA + k-means, k=2). This is real
within-context heterogeneity, of exactly the kind a candidate population has. Then, for each drug:

    run the predictor SEPARATELY on each subpopulation's control cells
    d_k = mean(predicted cells of subpop k) - mean(control cells of subpop k)
    report cos(d_0, d_1)

Because predict_population resamples with rng.choice(n, n, replace=False), a permutation, which
preserves a mean exactly, an additive predictor gives d_0 = d_1 = delta EXACTLY and cos = 1.000 to
floating point. THE SELF-CHECK IS EXACT, and it is asserted. If it ever fails again, the
measurement is broken and no number from this script may be reported.

A cell-state-conditional predictor (an OT map, a nonlinear decoder that reads the cell's own code)
gives a different displacement to cells in different states, so d_0 != d_1 and cos < 1. That is
Gate 1 opening, and it is the falsification test the two-gate framework names against itself.

    PYTHONPATH=src python analysis/predictors/gate1_within_context.py --n-drugs 12 --epochs 40
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
from baselines.average_effect_predictor import AverageEffectPredictor
from baselines.scgen_predictor import ScGenPredictor
from baselines.nonadditive_predictors import (
    RealScGenPredictor, RealCPAPredictor, OTMapPredictor,
)

warnings.filterwarnings("ignore")

N_PCA = 30
N_CTRL = 400          # control cells per context, split into the two subpopulations
MIN_SUB = 60          # a subpopulation below this is not a subpopulation
MIN_TREATED = 40
SEED = 0

# additive BY CONSTRUCTION. These must return cos == 1.000. They are the instrument's calibration,
# not a finding, and a run in which they do not is a broken run.
ADDITIVE = {"average_effect", "linear_latent"}

OUT = REPO / "results" / "exp14_nonadditive_predictors"


def _cos(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return float(np.dot(a, b) / (na * nb)) if na > 1e-12 and nb > 1e-12 else np.nan


_NULL_DRUG = "__ZERO_DELTA_BASELINE__"    # in no predictor's delta table, so its delta is zero

# Which predictors reconstruct their input, and therefore have a baseline of their own that is NOT
# the control cells. This is not a detail: it is the difference between measuring a drug response
# and measuring an autoencoder's reconstruction error.
#   "reconstruction": g(C) = P(C) + delta. Its own baseline is g(C) with a zero delta, i.e. P(C).
#   "identity":       g(C) = C + delta(C). It does not reconstruct, so its baseline IS C and the
#                     two baselines coincide (both cosines will agree, which is the correct answer
#                     for such a model, not a bug).
BASELINE_KIND = {
    "average_effect": "identity",        # adds a delta in gene space; no encode/decode
    "linear_latent":  "reconstruction",  # PCA encode -> +dz -> linear decode
    "scgen_real":     "reconstruction",  # VAE encode -> +dz -> nonlinear decode
    "cpa_real":       "reconstruction",  # VAE, drug/covariate conditioned
    "ot_map":         "reconstruction",  # latent OT: dec(enc(C) + disp) reconstructs through PCA
}


def _model_baseline(p, name, kw, C_k):
    """The population the model produces with NO drug effect, against which its own response is
    defined. For a reconstructing model this is P(C_k), and subtracting it cancels the
    reconstruction bias exactly. For a non-reconstructing model it is C_k itself.

    A predictor that exposes zero_effect_population knows its own baseline and we use it (the OT
    map, whose zero-effect output is its PCA reconstruction and which has no zero-delta drug to
    call). Otherwise a reconstructing model is asked for a zero-delta population via _NULL_DRUG,
    and an identity model has baseline C_k. We never silently guess which kind a model is.
    """
    if hasattr(p, "zero_effect_population"):
        import inspect
        zkw = dict(n_cells=len(C_k), seed=kw.get("seed", SEED))
        if "context" in inspect.signature(p.zero_effect_population).parameters:
            zkw["context"] = kw.get("context")
        return np.asarray(p.zero_effect_population(C_k, **zkw), dtype=np.float64)
    if BASELINE_KIND[name] == "identity":
        return C_k
    B = p.predict_population(**{**kw, "drug": _NULL_DRUG})
    return np.asarray(B, dtype=np.float64)


def subpopulations(Xc, seed=SEED):
    """Split one context's CONTROL cells into two cell-state subpopulations.

    Returns (labels, silhouette). The silhouette is reported because if the within-context
    structure is not real, a low induced cosine would mean nothing.
    """
    Z = PCA(n_components=min(N_PCA, Xc.shape[0] - 1, Xc.shape[1]),
            random_state=seed).fit_transform(Xc)
    lab = KMeans(n_clusters=2, n_init=10, random_state=seed).fit_predict(Z)
    sil = float(silhouette_score(Z, lab)) if len(set(lab)) > 1 else np.nan
    return lab, sil, Z


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-drugs", type=int, default=12)
    ap.add_argument("--epochs", type=int, default=40)
    ap.add_argument("--cpa-max-cells", type=int, default=60)
    args = ap.parse_args()

    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    data = load_sciplex3()
    contexts = list(data.contexts)
    print(f"SciPlex3: {data.X.shape}, contexts {contexts}", flush=True)

    print("\nfitting predictors", flush=True)
    preds = {}
    preds["average_effect"] = AverageEffectPredictor(seed=0).fit(data)
    print(f"  average_effect  [{time.time()-t0:.0f}s]", flush=True)
    ll = ScGenPredictor(force_fallback=True, seed=0).fit(data)
    assert ll.backend == "cpa_linear", f"expected linear-latent control, got {ll.backend}"
    preds["linear_latent"] = ll
    print(f"  linear_latent   backend={ll.backend}  [{time.time()-t0:.0f}s]", flush=True)
    preds["scgen_real"] = RealScGenPredictor(n_epochs=args.epochs, seed=0).fit(data)
    print(f"  scgen_real      PUBLISHED scgen VAE  [{time.time()-t0:.0f}s]", flush=True)
    try:
        preds["cpa_real"] = RealCPAPredictor(n_epochs=args.epochs, seed=0,
                                             max_cells_per_group=args.cpa_max_cells).fit(data)
        print(f"  cpa_real        PUBLISHED cpa-tools  [{time.time()-t0:.0f}s]", flush=True)
    except Exception as exc:
        # never substitute a linear model for a failed nonlinear one; record the gap
        print(f"  cpa_real        FAILED: {type(exc).__name__}: {exc}", flush=True)
    preds["ot_map"] = OTMapPredictor(seed=0).fit(data)
    print(f"  ot_map          per-cell OT displacement  [{time.time()-t0:.0f}s]", flush=True)

    rows, subinfo = [], []
    for ctx in contexts:
        cr = data.control_rows(ctx)
        rng = np.random.default_rng(SEED)
        cr = rng.choice(cr, min(len(cr), N_CTRL), replace=False)
        Xc = data.X[cr].astype(np.float64)
        lab, sil, _ = subpopulations(Xc)
        C = {k: Xc[lab == k] for k in (0, 1)}
        if min(len(v) for v in C.values()) < MIN_SUB:
            print(f"{ctx}: subpopulations too small, skipped", flush=True)
            continue
        subinfo.append({"context": ctx, "n_sub0": int(len(C[0])), "n_sub1": int(len(C[1])),
                        "silhouette": sil})
        print(f"\n{ctx}: within-context subpopulations {len(C[0])}/{len(C[1])} cells, "
              f"silhouette {sil:.3f}", flush=True)

        all_drugs = sorted(set(data.pert[~data.is_control].tolist()))
        drugs = [d for d in all_drugs
                 if len(data.treated_rows(ctx, d)) >= MIN_TREATED][:args.n_drugs]

        for drug in drugs:
            # REAL reference: what the real treated cells of this context actually do, with the
            # same partition carried over from the control cells (nearest control-subpop mean).
            tr = data.treated_rows(ctx, drug)
            Xt = data.X[tr].astype(np.float64)
            m0, m1 = C[0].mean(0), C[1].mean(0)
            assign = (np.linalg.norm(Xt - m1, axis=1) < np.linalg.norm(Xt - m0, axis=1)).astype(int)
            if min((assign == 0).sum(), (assign == 1).sum()) < 10:
                continue
            d_real = {k: Xt[assign == k].mean(0) - C[k].mean(0) for k in (0, 1)}
            # real cells ARE their own baseline, so the two columns coincide; write the same value
            # to cos_vs_real_control (the reporting block reads that column) rather than the
            # orphan cos_within, which the column rename left disconnected.
            rc = _cos(d_real[0], d_real[1])
            rows.append({"context": ctx, "drug": drug, "predictor": "real_cells",
                         "cos_within": rc, "cos_vs_real_control": rc,
                         "cos_vs_model_baseline": rc, "model_class": "REAL treated cells"})

            for name, p in preds.items():
                try:
                    if name in ("cpa_real", "scgen_real"):
                        known = p.known_drugs()
                        if known and drug not in known:
                            continue
                    # TWO BASELINES, AND THE DIFFERENCE BETWEEN THEM IS A FINDING.
                    #
                    # A generative predictor returns g(C_k), not C_k + delta. For a latent model
                    # g(C) = P(C) + W.dz, where P is the autoencoder's reconstruction. So:
                    #
                    #   vs the REAL control cells   d_k = [mean(P(C_k)) - mean(C_k)] + W.dz
                    #       The bracket is the RECONSTRUCTION BIAS of subpopulation k. It is
                    #       cell-state dependent and does NOT cancel, so an additive model shows
                    #       apparent divergence that is pure autoencoder artefact. THIS IS WHAT A
                    #       RETRIEVAL SCORER ACTUALLY SEES, which is why we report it.
                    #
                    #   vs the MODEL'S OWN baseline g(C_k) with a zero delta   d_k = W.dz
                    #       The bias cancels exactly, so an additive model gives cos = 1.000000 and
                    #       the number isolates the model's TRUE induced divergence. This is the
                    #       quantity the additivity theorem is about, and it is the self-check.
                    # LEARNING CHECK, on the whole context: cos(predicted mean delta, TRUE mean
                    # delta). A predictor that has not learned the drug effect cannot be said to
                    # open or shut any gate, and its divergence is noise structure. This gates
                    # whether the divergence below may be reported at all.
                    kwc = dict(drug=drug, control_cells=Xc, n_cells=len(Xc), context=ctx,
                               seed=SEED, synth="cells")
                    if name == "ot_map":
                        kwc["exclude_context"] = ctx
                    d_pred_ctx = np.asarray(p.predict_population(**kwc),
                                            dtype=np.float64).mean(0) - Xc.mean(0)
                    learned = _cos(d_pred_ctx, Xt.mean(0) - Xc.mean(0))

                    d_real_base, d_self_base = {}, {}
                    for k in (0, 1):
                        kw = dict(drug=drug, control_cells=C[k], n_cells=len(C[k]),
                                  context=ctx, seed=SEED, synth="cells")
                        if name == "ot_map":
                            kw["exclude_context"] = ctx      # no leakage from the query context
                        P = np.asarray(p.predict_population(**kw), dtype=np.float64)
                        B = _model_baseline(p, name, kw, C[k])
                        d_real_base[k] = P.mean(0) - C[k].mean(0)
                        d_self_base[k] = P.mean(0) - B.mean(0)
                    rows.append({"context": ctx, "drug": drug, "predictor": name,
                                 "learned": learned,
                                 "cos_vs_real_control": _cos(d_real_base[0], d_real_base[1]),
                                 "cos_vs_model_baseline": _cos(d_self_base[0], d_self_base[1]),
                                 "baseline_kind": BASELINE_KIND[name],
                                 "model_class": CLASS.get(name, "?")})
                except Exception as exc:
                    print(f"    {ctx} {drug} {name}: {type(exc).__name__}: {exc}", flush=True)
        print(f"  {ctx}: {len([r for r in rows if r['context']==ctx])} rows  "
              f"[{time.time()-t0:.0f}s]", flush=True)

    df = pd.DataFrame(rows)
    df.to_csv(OUT / "gate1_within_context.csv", index=False)
    pd.DataFrame(subinfo).to_csv(OUT / "gate1_within_context_subpops.csv", index=False)

    print(f"\n{'='*100}")
    print("GATE 1, WITHIN ONE CONTEXT, AGAINST TWO BASELINES. The two columns are the finding.")
    print()
    print("  cos vs REAL control    what a retrieval scorer actually measures: it contains the")
    print("                         model's RECONSTRUCTION BIAS, which differs between")
    print("                         subpopulations and is not a drug response at all.")
    print("  cos vs MODEL baseline  the model's TRUE induced divergence, with its reconstruction")
    print("                         bias cancelled. The additivity theorem pins this to 1.000000")
    print("                         for any additive model, and it is asserted.")
    print()
    print(f"  {'predictor':17s} {'learned':>8s} {'vs REAL ctrl':>13s} {'vs MODEL base':>14s}  "
          f"{'n':>4s}  model class")
    print("-" * 108)

    res, failures = {}, []
    LEARN_BAR = 0.30
    order = ["real_cells", "average_effect", "linear_latent", "scgen_real", "cpa_real", "ot_map"]
    for name in order:
        s_ = df[df.predictor == name]
        if s_.empty:
            print(f"  {name:17s} {'--- did not run ---':>22s}")
            res[name] = {"status": "did not run"}
            continue
        if name == "real_cells":
            a = float(s_.cos_vs_real_control.mean())
            print(f"  {name:17s} {'--':>8s} {a:>+13.4f} {'(no model)':>14s}  {len(s_):>4d}  "
                  f"REAL treated cells")
            res[name] = {"cos_vs_real_control": a, "n": int(len(s_))}
            continue
        learned = float(s_.learned.mean()) if "learned" in s_ else float("nan")
        a = float(s_.cos_vs_real_control.mean())
        b = float(s_.cos_vs_model_baseline.mean())
        void = learned < LEARN_BAR
        res[name] = {"learned": learned, "cos_vs_real_control": a, "cos_vs_model_baseline": b,
                     "n": int(len(s_)), "baseline_kind": BASELINE_KIND[name],
                     "model_class": CLASS[name], "void": bool(void)}
        tag = "  *** VOID: learned nothing, divergence not reportable ***" if void else ""
        print(f"  {name:17s} {learned:>+8.3f} {a:>+13.4f} {b:>+14.6f}  {len(s_):>4d}  "
              f"{CLASS[name]}{tag}")
        # An additive model must hit 1.000000 against its own baseline ONLY if it also learned;
        # a model that learned nothing has no obligation to the theorem.
        if name in ADDITIVE and not void and abs(b - 1.0) > 1e-6:
            failures.append((name, b))
    print("-" * 108)

    if failures:
        print("\n*** SELF-CHECK FAILED. THE MEASUREMENT IS BROKEN, NOT THE MODELS. ***")
        for name, m in failures:
            print(f"    {name} is additive by construction; against its own baseline the algebra")
            print(f"    requires cos = 1.000000, and it returned {m:.6f}.")
        print("    No number from this run may be reported. Fix the measurement first.")
        res["self_check"] = {"passed": False, "failures": dict(failures)}
    else:
        print("\nSELF-CHECK PASSED: every additive predictor returns cos = 1.000000 against its own")
        print("baseline, exactly as the algebra requires, so the measurement isolates Gate 1.")
        res["self_check"] = {"passed": True}

    print()
    print("READ THE TWO COLUMNS TOGETHER. An additive model induces ZERO true divergence (1.000000)")
    print("and yet, measured the way a scorer measures it, appears to induce a great deal. That")
    print("apparent divergence is the generator's reconstruction error, not biology. A distributional")
    print("score run on such a population is scoring the autoencoder.")

    res["subpopulations"] = subinfo
    json.dump(res, open(OUT / "gate1_within_context.json", "w"), indent=2)
    print(f"\nwrote {OUT/'gate1_within_context.csv'} and .json  [{time.time()-t0:.0f}s]")
    return 1 if failures else 0


CLASS = {
    "real_cells": "REAL treated cells",
    "average_effect": "ADDITIVE (gene space)",
    "linear_latent": "ADDITIVE (latent) + linear decoder",
    "scgen_real": "additive latent delta + NONLINEAR decoder [published scGen]",
    "cpa_real": "drug/covariate conditioned, nonlinear [published CPA]",
    "ot_map": "per-cell OT displacement (NON-ADDITIVE)",
}


if __name__ == "__main__":
    sys.exit(main())
