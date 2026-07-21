#!/usr/bin/env python3
"""Does a NON-ADDITIVE, state-conditional predictor open Gate 1? The falsification test.

THE CLAIM UNDER TEST
--------------------
Gate 1: a distributional decision layer can add nothing on top of a candidate-response source
that supplies no *differential* response. Its load-bearing half is algebraic and is not in
question: a predictor that adds ONE delta vector to EVERY cell gives its two subpopulations
identical responses, so their induced cosine is exactly 1 and the exploitable divergence is
exactly zero.

Its empirical half was, until now, unsupported and quietly circular. The three predictors
previously tested (average-effect, nearest-neighbour, and an in-repo linear-latent model
labelled "scGen") are ALL additive by construction. Finding that they induce no divergence
demonstrated the algebra and surveyed nothing; concluding from it that current perturbation
predictors are additive was inferring a property of the field from a property of our own code.

This script runs the models that could falsify the framework, on the SAME harness, changing
only the predictor:

    average_effect   gene-space delta                          cos = 1 EXACTLY (algebra)
    linear_latent    latent delta, LINEAR decoder              cos = 1 EXACTLY (algebra)
    scgen_real       latent delta, NONLINEAR decoder           <- published scgen 2.1.1
    cpa_real         drug/dose/covariate embeddings, nonlinear <- published cpa-tools 0.8.1
    ot_map           per-cell displacement from an OT coupling <- maximally non-additive

TWO-GATE PREDICTION, stated before the run: induced divergence should RISE across that ladder,
and if the framework is right, retrieval gain should rise with it. If divergence rises and gain
does not, the framework is WRONG at Gate 1 and this script is how we find out.

WHAT IS MEASURED, AND WHY IT IS MEASURED TWICE
---------------------------------------------
induced_response_cosine = cos(d_maj, d_min), where d_k is the mean response of subpopulation k of
the PREDICTED candidate population, each referred to its own matched control. Lower cosine = more
divergence = more for a distributional score to exploit.

The subtlety that decides this experiment is HOW the two subpopulations are identified, and the
first version of this script got it wrong. Assigning them by nearest mode of the real candidate,
as a scorer must, an ADDITIVE predictor scores about 0.43 rather than the 1.000 the algebra
demands. The gap is not divergence. It is ASSIGNMENT ERROR: the estimated partition is not the
true one, so d_maj and d_min differ even when every cell received an identical delta. Measured
that way, Gate-1 divergence and Gate-2 assignment error are confounded, and a low cosine for a
non-additive model could not be distinguished from noise.

Both quantities are therefore reported.

  cos_ORACLE     the predictor is run SEPARATELY on the majority context's control cells and on
                 the minority context's control cells, and d_k is taken from its own run. The
                 partition is then true by construction, and the number isolates GATE 1 alone:
                 does this model class produce a state-specific response at all? An additive
                 predictor must score ~1.000 here, and if it does not, this script is broken.

  cos_ESTIMATED  the blended population, partitioned by nearest mode, which is what a retrieval
                 layer actually has to work with. It is GATE 1 AND GATE 2 COMPOUNDED, and it is
                 the number a distributional score actually gets to exploit.

The difference between them is the cost of Gate 2, measured directly.

LEAKAGE. The generative predictors (scGen, CPA) are fitted on all contexts, exactly as the
incumbent predictors are in exp09. That is leakage IN THEIR FAVOUR: they may see the query
context's treated cells for the candidate drug. We keep it because it makes a null result
airtight (a predictor that cannot induce divergence even when shown the answer certainly cannot
induce it fairly), and we flag it wherever a positive result would depend on it. The OT map,
which is the one predictor whose mechanism could trivially memorize, is held out strictly:
its coupling never sees the query context.

    conda activate dartcpa    # scgen 2.1.1 + cpa-tools 0.8.1 + POT; see README
    PYTHONPATH=src python analysis/predictors/exp_nonadditive_gate1.py
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

from data.load_sciplex3 import load_sciplex3
from retrieval.tasks import ContextMixtureTask
from baselines.average_effect_predictor import AverageEffectPredictor
from baselines.scgen_predictor import ScGenPredictor
from baselines.nonadditive_predictors import (
    RealScGenPredictor, RealCPAPredictor, OTMapPredictor,
)
from retrieval.metrics import score_energy, score_mean_cosine

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

PAIRS = [("A549", "K562"), ("A549", "MCF7"), ("K562", "MCF7")]
ALPHA = 0.7
N_CELLS = 200
OUT = REPO / "results" / "exp14_nonadditive_predictors"


def _cos(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return float(np.dot(a, b) / (na * nb)) if na > 1e-12 and nb > 1e-12 else float("nan")


def _blend(data, ctx_a, ctx_b, rows_a, rows_b, n, alpha, rng):
    na = int(round(n * alpha))
    nb = n - na
    if len(rows_a) < 5 or len(rows_b) < 5:
        return None, None
    ia = rng.choice(rows_a, na, replace=len(rows_a) < na)
    ib = rng.choice(rows_b, nb, replace=len(rows_b) < nb)
    X = np.vstack([data.X[ia], data.X[ib]]).astype(np.float64)
    lab = np.array([ctx_a] * na + [ctx_b] * nb)
    return X, lab


def _assign_to_modes(X, mu_a, mu_b, lab_a, lab_b):
    da = ((X - mu_a) ** 2).sum(1)
    db = ((X - mu_b) ** 2).sum(1)
    return np.where(da <= db, lab_a, lab_b)


def _induced_response_cosine(X, labels, ctrl_by_label):
    uniq = [u for u in np.unique(labels) if u in ctrl_by_label]
    if len(uniq) < 2:
        return float("nan")
    deltas = []
    for u in uniq[:2]:
        rows = X[labels == u]
        if len(rows) < 2:
            return float("nan")
        deltas.append(rows.mean(0) - np.asarray(ctrl_by_label[u], dtype=np.float64))
    return _cos(deltas[0], deltas[1])


def learned_check(pred, data, drugs, contexts, n_cells=200, seed=0):
    """DID THIS MODEL LEARN THE RESPONSE AT ALL? Nothing downstream means anything if not.

    The hazard this guards against is specific and severe. An undertrained generative model emits
    a near-constant population, which has NO differential response between subpopulations, and the
    Gate-1 metric would score it exactly like a perfectly-trained additive model. We would then
    report "even CPA cannot induce differential response" when the truth was "we did not train
    CPA". Given how slow CPA is to fit, that failure mode is not hypothetical.

    So before any Gate-1 number is read, each predictor must show it can reproduce the direction
    of the observed mean response: cosine between its predicted mean delta and the TRUE mean delta,
    for each drug, in a real context. A model at cosine ~0 has learned nothing and its Gate-1
    number is reported as void rather than as a finding.
    """
    rng = np.random.default_rng(seed)
    out = []
    for ctx in contexts:
        cr = data.control_rows(ctx)
        ctrl_mean = data.control_mean(ctx)
        cc = data.X[rng.choice(cr, min(len(cr), n_cells), replace=False)]
        for d in drugs:
            tr = data.treated_rows(ctx, d)
            if len(tr) < 10:
                continue
            true_delta = data.X[tr].mean(0) - ctrl_mean
            try:
                kw = dict(n_cells=n_cells, seed=seed, synth="cells",
                          control_mean=ctrl_mean, control_cells=cc)
                if pred.name == "ot_map":
                    kw["exclude_context"] = None      # generous: may use every context
                if pred.name == "cpa_real":
                    kw["context"] = ctx
                pp = pred.predict_population(d, **kw)
            except Exception:
                continue
            out.append(_cos(pp.mean(0) - ctrl_mean, true_delta))
    return float(np.nanmedian(out)) if out else float("nan")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-drugs", type=int, default=10)
    ap.add_argument("--n-seeds", type=int, default=5)
    ap.add_argument("--epochs", type=int, default=100)
    ap.add_argument("--cpa-max-cells", type=int, default=300)
    args = ap.parse_args()

    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    data = load_sciplex3()
    print(f"SciPlex3: {data.X.shape}, contexts {list(data.contexts)}", flush=True)

    print("\nfitting predictors (the two additive controls, then the three that could "
          "falsify Gate 1)", flush=True)
    preds = {}
    preds["average_effect"] = AverageEffectPredictor(seed=0).fit(data)
    print(f"  average_effect  fitted   [{time.time()-t0:.0f}s]", flush=True)

    ll = ScGenPredictor(force_fallback=True, seed=0).fit(data)     # the LINEAR-latent control
    assert ll.backend == "cpa_linear", f"expected the linear-latent control, got {ll.backend}"
    preds["linear_latent"] = ll
    print(f"  linear_latent   fitted (backend={ll.backend})   [{time.time()-t0:.0f}s]", flush=True)

    sg = RealScGenPredictor(n_epochs=args.epochs, seed=0).fit(data)
    preds["scgen_real"] = sg
    print(f"  scgen_real      fitted (PUBLISHED scgen VAE)   [{time.time()-t0:.0f}s]", flush=True)

    try:
        cp = RealCPAPredictor(n_epochs=args.epochs, seed=0,
                              max_cells_per_group=args.cpa_max_cells).fit(data)
        preds["cpa_real"] = cp
        print(f"  cpa_real        fitted (PUBLISHED cpa-tools, {cp.n_train_cells} cells)   "
              f"[{time.time()-t0:.0f}s]", flush=True)
    except Exception as exc:
        # Do NOT silently substitute a linear model. Record the failure and continue.
        print(f"  cpa_real        FAILED TO FIT: {type(exc).__name__}: {exc}", flush=True)
        print("                  (recorded as a gap, not replaced by a fallback)", flush=True)

    preds["ot_map"] = OTMapPredictor(seed=0).fit(data)
    print(f"  ot_map          ready (no training; coupling solved per query)   "
          f"[{time.time()-t0:.0f}s]", flush=True)

    # ---- DID THEY LEARN? Nothing below is interpretable for a model that did not. ----
    print("\nSANITY: cosine between each predictor's mean delta and the TRUE mean delta.")
    print("A model near 0 has learned nothing, and its Gate-1 number is VOID, not a finding.",
          flush=True)
    chk_drugs = sorted({d for p in PAIRS
                        for d in list(ContextMixtureTask(data, ctx_maj=p[0],
                                                         ctx_min=p[1]).shared)[:args.n_drugs]})[:8]
    learned = {}
    for pname, pred in preds.items():
        learned[pname] = learned_check(pred, data, chk_drugs, ["A549", "K562", "MCF7"])
        flag = "OK" if learned[pname] > 0.2 else "*** VOID: did not learn ***"
        print(f"  {pname:16s} cos(predicted delta, true delta) = {learned[pname]:+.3f}   {flag}",
              flush=True)

    rows = []
    for ctx_maj, ctx_min in PAIRS:
        pair = f"{ctx_maj}+{ctx_min}"
        ctrl_by_ctx = {ctx_maj: data.control_mean(ctx_maj), ctx_min: data.control_mean(ctx_min)}
        cr_maj, cr_min = data.control_rows(ctx_maj), data.control_rows(ctx_min)
        ctrl_blend = ALPHA * ctrl_by_ctx[ctx_maj] + (1 - ALPHA) * ctrl_by_ctx[ctx_min]

        task = ContextMixtureTask(data, ctx_maj=ctx_maj, ctx_min=ctx_min)
        drugs = [d for d in sorted(task.shared)
                 if len(data.treated_rows(ctx_maj, d)) >= 10
                 and len(data.treated_rows(ctx_min, d)) >= 10][:args.n_drugs]
        print(f"\npair {pair}: {len(drugs)} drugs", flush=True)

        for drug in drugs:
            for seed in range(args.n_seeds):
                rng = np.random.default_rng(10_000 + seed)
                ctrl_cells, _ = _blend(data, ctx_maj, ctx_min, cr_maj, cr_min,
                                       N_CELLS, ALPHA, rng)
                real_blend, real_lab = _blend(
                    data, ctx_maj, ctx_min,
                    data.treated_rows(ctx_maj, drug), data.treated_rows(ctx_min, drug),
                    N_CELLS, ALPHA, rng)
                if ctrl_cells is None or real_blend is None:
                    continue

                # per-context control cells, so the ORACLE partition needs no estimation
                n_maj = int(round(N_CELLS * ALPHA))
                n_min = N_CELLS - n_maj
                cc_maj = data.X[rng.choice(cr_maj, n_maj, replace=len(cr_maj) < n_maj)]
                cc_min = data.X[rng.choice(cr_min, n_min, replace=len(cr_min) < n_min)]

                base = {"pair": pair, "drug": drug, "seed": seed}
                rows.append({**base, "predictor": "real_blend",
                             "cos_estimated": _induced_response_cosine(
                                 real_blend, real_lab, ctrl_by_ctx),
                             "cos_oracle": _induced_response_cosine(
                                 real_blend, real_lab, ctrl_by_ctx)})

                mu_a = real_blend[real_lab == ctx_maj].mean(0)
                mu_b = real_blend[real_lab == ctx_min].mean(0)

                for pname, pred in preds.items():
                    kw = dict(seed=seed, synth="cells", control_mean=ctrl_blend)
                    if pname == "ot_map":
                        kw["exclude_context"] = ctx_min     # strict: never sees the query context
                    if pname == "cpa_real":
                        kw["context"] = ctx_maj
                    try:
                        # ESTIMATED: the blended population a scorer actually receives
                        pp = pred.predict_population(drug, n_cells=N_CELLS,
                                                     control_cells=ctrl_cells, **kw)
                        plab = _assign_to_modes(pp, mu_a, mu_b, ctx_maj, ctx_min)
                        c_est = _induced_response_cosine(pp, plab, ctrl_by_ctx)

                        # ORACLE: run the predictor separately per context, so d_maj and d_min
                        # come from a partition that is true by construction. This isolates
                        # Gate 1: an additive predictor MUST land at ~1.000 here.
                        kw_min = dict(kw)
                        if pname == "cpa_real":
                            kw_min["context"] = ctx_min
                        p_maj = pred.predict_population(drug, n_cells=n_maj,
                                                        control_cells=cc_maj, **kw)
                        p_min = pred.predict_population(drug, n_cells=n_min,
                                                        control_cells=cc_min, **kw_min)
                        d_maj = p_maj.mean(0) - ctrl_by_ctx[ctx_maj]
                        d_min = p_min.mean(0) - ctrl_by_ctx[ctx_min]
                        c_orc = _cos(d_maj, d_min)
                    except Exception as exc:
                        print(f"    {pname} failed on {drug}/{seed}: "
                              f"{type(exc).__name__}: {exc}", flush=True)
                        continue
                    rows.append({**base, "predictor": pname,
                                 "cos_estimated": c_est, "cos_oracle": c_orc})
        print(f"  done  [{time.time()-t0:.0f}s]", flush=True)

    df = pd.DataFrame(rows)
    df.to_csv(OUT / "gate1_nonadditive.csv", index=False)

    ORDER = ["real_blend", "average_effect", "linear_latent", "scgen_real", "cpa_real", "ot_map"]
    KIND = {"real_blend": "REAL candidate population",
            "average_effect": "additive (gene space)",
            "linear_latent": "additive (latent) + LINEAR decoder",
            "scgen_real": "additive (latent) + NONLINEAR decoder [published scGen]",
            "cpa_real": "drug/covariate conditioned, nonlinear [published CPA]",
            "ot_map": "per-cell OT displacement (non-additive)"}

    print(f"\n{'='*104}")
    print("GATE 1: induced response cosine  cos(d_maj, d_min) of the PREDICTED population")
    print("  1.000 = the two subpopulations respond IDENTICALLY -> zero divergence to exploit")
    print("  0.000 = they respond ORTHOGONALLY -> maximal divergence")
    print("\n  cos_ORACLE    true partition (predictor run per context). ISOLATES GATE 1.")
    print("  cos_ESTIMATED nearest-mode partition, as a scorer must. GATE 1 + GATE 2 compounded.")
    print(f"\n{'predictor':16s} {'cos_ORACLE':>18s} {'cos_ESTIMATED':>18s} {'learned?':>9s}  "
          f"model class")
    print("-" * 116)
    res = {"n_drugs": args.n_drugs, "n_seeds": args.n_seeds, "epochs": args.epochs,
           "learned_check": learned, "predictors": {}}
    for p in ORDER:
        s = df[df.predictor == p]
        o = s["cos_oracle"].dropna()
        e = s["cos_estimated"].dropna()
        if o.empty and e.empty:
            print(f"  {p:14s} {'--- did not run ---':>38s}  {KIND[p]}")
            res["predictors"][p] = {"status": "did not run"}
            continue
        lc = learned.get(p, float("nan"))
        void = (p not in ("real_blend",)) and not (lc > 0.2)
        res["predictors"][p] = {
            "cos_oracle_mean": float(o.mean()), "cos_oracle_sd": float(o.std()),
            "cos_estimated_mean": float(e.mean()), "cos_estimated_sd": float(e.std()),
            "learned_cos": float(lc), "void_did_not_learn": bool(void),
            "n": int(len(s)), "class": KIND[p]}
        mark = "VOID" if void else f"{lc:+.3f}"
        print(f"  {p:14s} {o.mean():>10.3f} +- {o.std():<5.3f} {e.mean():>10.3f} +- {e.std():<5.3f}"
              f" {mark:>9s}  {KIND[p]}")
    print("-" * 116)
    print("  'learned?' = cos(predicted mean delta, TRUE mean delta). VOID means the model did")
    print("  not learn the response, so its Gate-1 number says nothing about its model class.")

    # SELF-CHECK. Additivity implies cos_oracle == 1 exactly. If the additive controls do not
    # land there, the measurement is broken and no conclusion may be drawn from it.
    ok = True
    for p in ("average_effect", "linear_latent"):
        m = res["predictors"].get(p, {}).get("cos_oracle_mean")
        if m is None or m < 0.97:
            print(f"\n*** SELF-CHECK FAILED: {p} is additive by construction and must give "
                  f"cos_oracle ~ 1.000; got {m}. The measurement is wrong, not the model. ***")
            ok = False
    res["self_check_additive_controls_at_one"] = ok
    if ok:
        print("\nSELF-CHECK PASSED: both additive controls sit at cos_oracle ~ 1.000, as the "
              "algebra requires.")

    real_o = res["predictors"]["real_blend"]["cos_oracle_mean"]
    print(f"\nREAL candidate populations sit at cos = {real_o:.3f} (near-orthogonal). A predictor "
          f"is useful to a\ndistributional scorer only insofar as it moves DOWN toward that value.")

    # a model that did not learn cannot be counted either way
    NONADD = [p for p in ("scgen_real", "cpa_real", "ot_map")
              if "cos_oracle_mean" in res["predictors"].get(p, {})
              and not res["predictors"][p]["void_did_not_learn"]]
    opened = [p for p in NONADD if res["predictors"][p]["cos_oracle_mean"] < 0.90]
    res["gate1_opened_by"] = opened
    res["verdict"] = (
        "NON-ADDITIVE PREDICTORS DO INDUCE DIVERGENCE (" + ", ".join(
            f"{p} cos={res['predictors'][p]['cos_oracle_mean']:.3f}" for p in opened) +
        "). Gate 1 is NOT a property of all predictors, only of the additive class. Whether that "
        "divergence buys a retrieval advantage is the next test, and it is what decides the "
        "framework."
        if opened else
        "NO PREDICTOR OPENS GATE 1. Even explicitly state-conditional models fail to induce "
        "differential response between the query's subpopulations, so Gate 1 is a property of "
        "the predictor class and not of our implementation.")
    print(f"\nVERDICT: {res['verdict']}")

    json.dump(res, open(OUT / "gate1_nonadditive.json", "w"), indent=2)
    print(f"\nwrote {OUT/'gate1_nonadditive.csv'} and .json   [{time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
