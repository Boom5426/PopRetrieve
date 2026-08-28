#!/usr/bin/env python
"""Diagnostic: decision_regret Class A circularity audit.

Tests whether exp12's +0.119 energy-welfare regret reduction is a tautology
by computing regret under an alternative welfare definition (mean-delta-cosine)
that is independent of the energy distance used by PopRetrieve for selection.

Two welfare functions:
  1. Energy welfare (original): per-state score_energy, aggregate worst-case
  2. Mean-delta-cosine welfare (alternative): per-state cosine(cand_delta, state_delta),
     aggregate worst-case. cand_delta = cand_mean - ctrl, state_delta = state_mean - ctrl

If PopRetrieve shows regret reduction only under (1) but not (2), then +0.119 is
purely circular: PopRetrieve selects the drug with best energy, welfare IS energy,
so PopRetrieve wins by definition.
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import numpy as np
import pandas as pd

from data.load_sciplex3 import load_sciplex3
from retrieval.metrics import score_energy, score_mean_cosine
from sklearn.cluster import KMeans

# ── helpers ──────────────────────────────────────────────────────────────────

def kmeans_states(X, k=2, seed=0):
    k = min(k, max(1, len(X) - 1))
    if k < 2:
        return np.zeros(len(X), dtype=int)
    km = KMeans(n_clusters=k, n_init=3, random_state=seed, max_iter=100).fit(X)
    return km.labels_


def cosine(a, b):
    na = np.linalg.norm(a)
    nb = np.linalg.norm(b)
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def welfare_energy(cand_pops, query_X, query_states, max_cells=200, seed=0):
    """Original: per-state score_energy, aggregate worst."""
    uniq = np.unique(query_states)
    state_Qs = {s: query_X[query_states == s] for s in uniq}
    vals = {}
    for name, P in cand_pops.items():
        per_state = []
        for s in uniq:
            Qs = state_Qs[s]
            if len(Qs) < 2:
                continue
            e = score_energy(P, Qs, max_cells=min(max_cells, len(P), len(Qs)), seed=seed)
            per_state.append(e)
        if not per_state:
            vals[name] = -1e9
        else:
            vals[name] = float(np.min(per_state))
    return vals


def welfare_delta_cosine(cand_pops, query_X, query_states, ctrl, max_cells=200):
    """Alternative: per-state cosine(cand_delta, state_delta), aggregate worst.
    cand_delta = mean(P) - ctrl, state_delta = mean(state_cells) - ctrl."""
    uniq = np.unique(query_states)
    state_Qs = {s: query_X[query_states == s] for s in uniq}
    vals = {}
    for name, P in cand_pops.items():
        cand_delta = P.mean(0) - ctrl
        per_state = []
        for s in uniq:
            Qs = state_Qs[s]
            if len(Qs) < 2:
                continue
            state_delta = Qs.mean(0) - ctrl
            per_state.append(cosine(cand_delta, state_delta))
        if not per_state:
            vals[name] = -1e9
        else:
            vals[name] = float(np.min(per_state))
    return vals


def decision_regret(welfare_vals, selected_drug):
    if not welfare_vals:
        return float("nan")
    opt = max(welfare_vals.values())
    sel = welfare_vals.get(selected_drug, min(welfare_vals.values()))
    return float(opt - sel)


def score_method(method, P, Q, ctrl, query_states, seed=0):
    mc = min(300, len(P), len(Q))
    if method == "mean_cosine":
        return score_mean_cosine(P, Q, control_P=ctrl, control_Q=ctrl)
    elif method == "DART_energy":
        return score_energy(P, Q, max_cells=mc, seed=seed)
    else:
        raise ValueError(method)


# ── main ─────────────────────────────────────────────────────────────────────

def main():
    print("Loading SciPlex3...")
    ds = load_sciplex3()
    print(ds.summary())

    ctx = "A549"
    all_drugs = sorted(set(
        np.asarray(ds.pert)[(ds.context == ctx) & (~ds.is_control)].tolist()
    ))
    ctrl = ds.control_mean(ctx)

    # Select drugs with enough cells (>= 20)
    viable = []
    for d in all_drugs:
        rows = ds.treated_rows(ctx, d)
        if len(rows) >= 20:
            viable.append(d)
    print(f"Viable drugs (>=20 cells): {len(viable)}")

    # Use first 15 drugs, 2 seeds as specified
    test_drugs = viable[:15]
    seeds = [0, 1]
    methods = ["mean_cosine", "DART_energy"]

    rows = []
    total = len(test_drugs) * len(seeds)
    done = 0

    for seed in seeds:
        rng = np.random.default_rng(seed)
        for hd in test_drugs:
            done += 1
            # Query = hidden drug's response
            hd_rows = ds.treated_rows(ctx, hd)
            if len(hd_rows) > 200:
                hd_rows = rng.choice(hd_rows, 200, replace=False)
            query_X = ds.X[hd_rows]
            query_states = kmeans_states(query_X, k=2, seed=seed)

            # Library = all viable drugs except hidden
            library = [d for d in viable if d != hd]
            cand_pops = {}
            for d in library:
                dr = ds.treated_rows(ctx, d)
                if len(dr) < 10:
                    continue
                if len(dr) > 150:
                    dr = rng.choice(dr, 150, replace=False)
                cand_pops[d] = ds.X[dr]

            if len(cand_pops) < 5:
                continue

            names = list(cand_pops.keys())

            # Score each method
            method_scores = {}
            for method in methods:
                sc = np.array([
                    score_method(method, cand_pops[n], query_X, ctrl, query_states, seed=seed)
                    for n in names
                ])
                method_scores[method] = sc

            # Compute both welfare definitions
            welf_energy = welfare_energy(cand_pops, query_X, query_states, seed=seed)
            welf_cosine = welfare_delta_cosine(cand_pops, query_X, query_states, ctrl)

            # For each method, find selected drug and compute regret under both welfares
            for method in methods:
                sc = method_scores[method]
                top1 = names[int(np.argmax(sc))]
                regret_energy = decision_regret(welf_energy, top1)
                regret_cosine = decision_regret(welf_cosine, top1)

                rows.append({
                    "seed": seed,
                    "heldout_drug": hd,
                    "method": method,
                    "selected_drug": top1,
                    "regret_energy_welfare": regret_energy,
                    "regret_cosine_welfare": regret_cosine,
                    "oracle_energy": max(welf_energy.values()),
                    "oracle_cosine": max(welf_cosine.values()),
                    "selected_energy_welfare": welf_energy.get(top1, float("nan")),
                    "selected_cosine_welfare": welf_cosine.get(top1, float("nan")),
                })

            if done % 5 == 0:
                print(f"  [{done}/{total}]")

    df = pd.DataFrame(rows)

    # ── Summary stats ────────────────────────────────────────────────────────
    print("\n=== Per-method mean regret ===")
    summary = df.groupby("method")[["regret_energy_welfare", "regret_cosine_welfare"]].mean()
    print(summary)

    # Regret reduction = mean_cosine_regret - DART_regret (positive = PopRetrieve better)
    mean_regret = df[df.method == "mean_cosine"].set_index(["seed", "heldout_drug"])
    dart_regret = df[df.method == "DART_energy"].set_index(["seed", "heldout_drug"])

    paired = mean_regret[["regret_energy_welfare", "regret_cosine_welfare"]].rename(
        columns=lambda c: c + "_mean"
    ).join(
        dart_regret[["regret_energy_welfare", "regret_cosine_welfare"]].rename(
            columns=lambda c: c + "_dart"
        )
    )

    paired["energy_reduction"] = paired["regret_energy_welfare_mean"] - paired["regret_energy_welfare_dart"]
    paired["cosine_reduction"] = paired["regret_cosine_welfare_mean"] - paired["regret_cosine_welfare_dart"]
    paired["dart_better_energy"] = (paired["energy_reduction"] > 0).astype(int)
    paired["dart_better_cosine"] = (paired["cosine_reduction"] > 0).astype(int)

    energy_reduction = paired["energy_reduction"].mean()
    cosine_reduction = paired["cosine_reduction"].mean()
    frac_better_energy = paired["dart_better_energy"].mean()
    frac_better_cosine = paired["dart_better_cosine"].mean()

    print(f"\n=== Regret Reduction (mean_cosine_regret - DART_regret) ===")
    print(f"  Energy welfare:       {energy_reduction:.6f}  (frac PopRetrieve better: {frac_better_energy:.3f})")
    print(f"  Delta-cosine welfare: {cosine_reduction:.6f}  (frac PopRetrieve better: {frac_better_cosine:.3f})")

    confirmed = (cosine_reduction <= 0)
    print(f"\n=== Circularity confirmed: {confirmed} ===")
    if confirmed:
        print("  +0.119 energy-welfare regret reduction is purely circular.")
        print("  PopRetrieve shows NO advantage under an oracle-independent welfare definition.")
    else:
        print("  PopRetrieve retains some advantage even under alternative welfare.")

    # Save results
    out_dir = Path(__file__).parent
    out_dir.mkdir(parents=True, exist_ok=True)

    df.to_csv(out_dir / "welfare_circularity_results.csv", index=False)
    print(f"\nSaved: {out_dir / 'welfare_circularity_results.csv'}")

    # Also save summary
    summary_data = {
        "energy_welfare_regret_reduction": [energy_reduction],
        "delta_cosine_welfare_regret_reduction": [cosine_reduction],
        "frac_dart_better_energy_welfare": [frac_better_energy],
        "frac_dart_better_cosine_welfare": [frac_better_cosine],
        "confirmed_circularity": [confirmed],
        "n_queries": [len(paired)],
    }
    pd.DataFrame(summary_data).to_csv(out_dir / "welfare_circularity_summary.csv", index=False)
    print(f"Saved: {out_dir / 'welfare_circularity_summary.csv'}")


if __name__ == "__main__":
    main()
