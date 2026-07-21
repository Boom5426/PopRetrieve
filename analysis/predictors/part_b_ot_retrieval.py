#!/usr/bin/env python3
"""Part B, the framework's falsification test: does OPENING Gate 1 buy any RETRIEVAL gain?

THE TEST
--------
Gate 1 is necessary for a distributional decision layer to help: the candidate populations a
scorer ranks must actually respond differently across their subpopulations. We now have a predictor
that opens Gate 1 (the latent OT map: true induced divergence 0.903 against the additive ceiling of
1.000; CORRECTIONS.md R33) and additive predictors that do not (cosine exactly 1). The two-gate
account predicts that distributional retrieval should beat mean retrieval MORE when candidates come
from the Gate-1-opening predictor than when they come from an additive one. If it does not, Gate 1
is not the operative condition and the account is wrong.

We reuse exp09's cross-line predict-then-rank protocol and scorers unchanged; only the predictor
pool is restricted to the additive baseline and the OT map, so no VAE is fitted and the test is
fast. For each predictor we report distributional-minus-mean retrieval, per metric:

    delta = (dart_energy or dart_coverage retrieval) - (mean_cosine retrieval)

If opening Gate 1 helps, delta should be systematically larger for ot_map than for average_effect.

    PYTHONPATH=src python analysis/predictors/part_b_ot_retrieval.py --n-seeds 8 --n-drugs 10
"""
from pathlib import Path as _P
REPO = _P(__file__).resolve().parents[2]
import sys
sys.path.insert(0, str(REPO / "src"))

import argparse
import json

import numpy as np
import pandas as pd

from data.load_sciplex3 import load_sciplex3
from baselines.average_effect_predictor import AverageEffectPredictor
from baselines.nonadditive_predictors import OTMapPredictor
from experiments.exp09_predict_then_rank import (
    _crossline_queries, _run_task, RETRIEVALS, REF_RETRIEVAL, DART_RETRIEVALS,
)

OUT = REPO / "results" / "exp14_nonadditive_predictors"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-seeds", type=int, default=8)
    ap.add_argument("--n-drugs", type=int, default=10)
    args = ap.parse_args()

    data = load_sciplex3()
    print(data.summary(), flush=True)

    # ONLY the additive baseline and the Gate-1-opening OT map. No VAE, so this is fast and the
    # contrast is clean: same queries, same libraries, same four scorers, one additive candidate
    # source and one non-additive one.
    pool = [AverageEffectPredictor(), OTMapPredictor()]
    for p in pool:
        p.fit(data)
        print(f"fitted {p.name}", flush=True)

    qs = _crossline_queries(data, args.n_seeds, args.n_drugs, alphas=(0.5, 0.7, 0.9))
    print(f"built {len(qs)} cross-line queries", flush=True)

    metric_rows, perq_rows, rt = [], [], {}
    # loco is irrelevant here (neither predictor is nearest-neighbour); the OT leakage guard is
    # mandatory inside _run_task and uses each query's own contexts.
    _run_task("crossline", qs, pool, rt, perq_rows, metric_rows, synth="cells", loco=False)
    df = pd.DataFrame(metric_rows)
    df.to_csv(OUT / "part_b_ot_retrieval.csv", index=False)

    print(f"\n{'='*92}")
    print("PART B: distributional retrieval minus mean retrieval, by candidate-response source.")
    print("If opening Gate 1 helps, the DART-minus-mean delta is larger for ot_map than additive.")
    print(f"\n{'predictor':16s} {'metric':10s} {'mean_cosine':>12s} {'dart_energy':>12s} "
          f"{'dart_coverage':>14s} {'E - mean':>9s} {'C - mean':>9s}")
    print("-" * 92)

    res = {}
    for pname in ["average_effect", "ot_map"]:
        sp = df[df.predictor == pname]
        if sp.empty:
            continue
        res[pname] = {}
        for metric in ["hit@1", "ndcg@10"]:
            piv = sp.groupby("retrieval")[metric].mean()
            base = float(piv.get(REF_RETRIEVAL, float("nan")))
            en = float(piv.get("dart_energy", float("nan")))
            cov = float(piv.get("dart_coverage", float("nan")))
            res[pname][metric] = {"mean_cosine": base, "dart_energy": en, "dart_coverage": cov,
                                  "energy_minus_mean": en - base, "coverage_minus_mean": cov - base}
            print(f"  {pname:14s} {metric:10s} {base:>12.3f} {en:>12.3f} {cov:>14.3f} "
                  f"{en - base:>+9.3f} {cov - base:>+9.3f}")
    print("-" * 92)

    # the decisive contrast: is the DART advantage LARGER for the Gate-1-opening predictor?
    if "ot_map" in res and "average_effect" in res:
        print("\nDOES OPENING GATE 1 HELP? DART-minus-mean advantage, ot_map versus additive:")
        res["contrast"] = {}
        for metric in ["hit@1", "ndcg@10"]:
            for ch, key in [("energy", "energy_minus_mean"), ("coverage", "coverage_minus_mean")]:
                ot = res["ot_map"][metric][key]
                ad = res["average_effect"][metric][key]
                res["contrast"][f"{metric}_{ch}"] = {"ot_map": ot, "additive": ad,
                                                     "ot_minus_additive": ot - ad}
                print(f"  {metric:8s} {ch:9s}: ot_map {ot:+.3f}  vs additive {ad:+.3f}  "
                      f"->  difference {ot - ad:+.3f}")
        print("\nA positive 'difference' means opening Gate 1 buys distributional retrieval gain.")
        print("Near-zero or negative means Gate 1 is open but the advantage does not follow, which")
        print("would be evidence against the two-gate account. No verdict is hard-coded; the")
        print("numbers are reported and interpreted in the text.")

    json.dump(res, open(OUT / "part_b_ot_retrieval.json", "w"), indent=2)
    print(f"\nwrote {OUT/'part_b_ot_retrieval.csv'} and .json")


if __name__ == "__main__":
    main()
