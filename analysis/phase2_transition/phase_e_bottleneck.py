#!/usr/bin/env python
"""Phase 4: population-to-decision bottleneck decomposition.

This replaces the three-gate confirmation analysis. The old framework predicted that population
benefit concentrates where differential response is strong and recoverability is high; on this
benchmark that cell of the grid held 5 of 3,620 queries and gained nothing, while the strongest
correlate of gain was the headroom the mean route left (Spearman +0.783,
docs/phase2/08_THREE_GATE_ANALYSIS.md). So the question is no longer whether the three gates line
up. It is:

    after controlling for how much room the mean route leaves, does a repaired, reproducible
    drug-by-state interaction still explain population-specific decision gain?

Four quantities per query, each measured rather than assumed:

    H       headroom, 1 - RR_mean_cosine under the oracle. A property of the incumbent scorer.
    S_int   cross-fitted drug-by-state interaction (src/retrieval/interaction.py), with its
            scale-free companion `interaction_share`. Replaces the discredited 1 - cos.
    A_sup   supervised recoverability, treated against vehicle (phase_c_gates.py).
    G       decision gain, RR_population - RR_reference, for both references.

The reference matters and both are reported. Against `mean_cosine`, G is the headline gain and
mixes magnitude with distribution. Against `mean_l2`, G is what is left after a mean-only scorer
has already taken the magnitude, which is the only version that can be called
population-specific.

The regression is ordinary least squares with cluster-robust standard errors at the cell line,
because queries inside one context share a source population and an entire candidate library.
Predictors are standardised so the coefficients are directly comparable, and a nested comparison
against a headroom-only model reports what the interaction term adds beyond it.

OUTPUTS (--out)
---------------
    bottleneck_per_query.csv    one row per query with all four quantities and both gains
    regression.csv              standardised coefficients, cluster-robust CIs, nested R^2
    strata.csv                  the non-parametric companion: headroom x interaction-share grid
    summary.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parent))
import phase2_common as pc                                           # noqa: E402

POP, MEANC, MEANL2 = "energy", "mean_cosine", "mean_l2"


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def per_query_gain(pq: pd.DataFrame, pop: str, ref: str, tag: str) -> pd.DataFrame:
    """Per-query mean gain of ``pop`` over ``ref``, plus the flip counts."""
    key = ["cell_line", "drug", "seed"]
    a = pq[pq.scorer == pop].set_index(key)
    b = pq[pq.scorer == ref].set_index(key)
    j = a.join(b, rsuffix="_ref", how="inner").reset_index()
    j["gain"] = j.reciprocal_rank - j.reciprocal_rank_ref
    j["corrected_flip"] = ((j["rank"] == 1) & (j["rank_ref"] > 1)).astype(float)
    j["reverse_flip"] = ((j["rank_ref"] == 1) & (j["rank"] > 1)).astype(float)
    g = j.groupby(["cell_line", "drug"], as_index=False).agg(
        **{f"G_{tag}": ("gain", "mean"),
           f"corrected_flip_{tag}": ("corrected_flip", "mean"),
           f"reverse_flip_{tag}": ("reverse_flip", "mean"),
           f"RR_ref_{tag}": ("reciprocal_rank_ref", "mean"),
           f"RR_pop_{tag}": ("reciprocal_rank", "mean")})
    return g


def fit(df: pd.DataFrame, y: str, terms: list[str], cluster: str):
    """OLS with cluster-robust covariance; standardised predictors."""
    import statsmodels.api as sm
    d = df.dropna(subset=[y] + terms).copy()
    Z = d[terms].copy()
    for c in terms:
        sd = Z[c].std()
        Z[c] = (Z[c] - Z[c].mean()) / (sd if sd > 0 else 1.0)
    Z = sm.add_constant(Z, has_constant="add")
    m = sm.OLS(d[y], Z).fit(cov_type="cluster", cov_kwds={"groups": d[cluster]})
    return m, d


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--phase-a", required=True)
    ap.add_argument("--phase-b", required=True)
    ap.add_argument("--phase-c", required=True)
    ap.add_argument("--gate1", required=True, help="output dir of gate1_interaction.py")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    pa, pb, pcd, g1, out = (Path(a.phase_a), Path(a.phase_b), Path(a.phase_c),
                            Path(a.gate1), Path(a.out))
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    A = pd.read_csv(pa / "per_query.csv.gz")
    B = pd.read_csv(pb / "per_query.csv.gz")
    g2 = pd.read_csv(pcd / "gate2_observed.csv")[["cell_line", "drug", "A_sup", "A_unsup", "G"]]
    g2 = g2.rename(columns={"G": "G_gap"})
    inter = pd.read_csv(g1 / "interaction_per_query.csv")
    log(f"phase A {A.shape}, phase B {B.shape}, gate2 {g2.shape}, interaction {inter.shape}")

    d = (per_query_gain(A, POP, MEANC, "oracle_vs_cos")
         .merge(per_query_gain(A, POP, MEANL2, "oracle_vs_l2"), on=["cell_line", "drug"])
         .merge(g2, on=["cell_line", "drug"], how="left")
         .merge(inter[["cell_line", "drug", "S_int", "S_main", "interaction_share", "R_int",
                       "D_old", "norm_r_G1", "norm_r_G2M", "n_treated_G1", "n_treated_G2M"]],
                on=["cell_line", "drug"], how="left"))
    for p, gb in B.groupby("predictor"):
        d = d.merge(per_query_gain(gb, POP, MEANC, f"pred_{p}")[
            ["cell_line", "drug", f"G_pred_{p}"]], on=["cell_line", "drug"], how="left")

    # H and G share the term RR_mean with opposite signs, and RR is capped at 1, so a positive gain
    # is impossible where the mean route is already perfect. Any correlation between them is
    # therefore part mechanical, and the size of the mechanical part is measured below rather than
    # assumed small. The tautology-free specification regresses RR_pop on RR_ref plus the
    # candidate explanatory variables: its coefficients say what predicts how well the population
    # route does GIVEN how well the mean route did, which is the question that was meant.
    d["H"] = 1.0 - d["RR_ref_oracle_vs_cos"]
    d["H_l2"] = 1.0 - d["RR_ref_oracle_vs_l2"]
    d["log_S_int"] = np.log10(d.S_int.clip(lower=1e-8))
    d.to_csv(out / "bottleneck_per_query.csv", index=False)

    # ---- regressions ----
    rows = []
    specs = [
        ("G_oracle_vs_cos", ["H"], "headroom only"),
        ("G_oracle_vs_cos", ["H", "interaction_share"], "headroom + interaction share"),
        ("G_oracle_vs_cos", ["H", "interaction_share", "A_sup"], "plus recoverability"),
        ("G_oracle_vs_cos", ["H", "interaction_share", "A_sup", "H_x_share"], "plus interaction term"),
        ("G_oracle_vs_l2", ["H_l2"], "headroom only, magnitude-controlled"),
        ("G_oracle_vs_l2", ["H_l2", "interaction_share"], "plus interaction share"),
        ("G_oracle_vs_l2", ["H_l2", "interaction_share", "A_sup"], "plus recoverability"),
        ("G_oracle_vs_l2", ["H_l2", "interaction_share", "A_sup", "H_x_share"], "plus interaction term"),
        ("G_oracle_vs_cos", ["H", "log_S_int", "A_sup"], "absolute interaction instead of share"),
        ("G_oracle_vs_cos", ["H", "D_old", "A_sup"], "the old statistic, for contrast"),
        # Tautology-free: outcome is the population route's own performance, with the mean route's
        # performance as a covariate instead of subtracted from it.
        ("RR_pop_oracle_vs_cos", ["RR_ref_oracle_vs_cos"], "conditional: mean route only"),
        ("RR_pop_oracle_vs_cos", ["RR_ref_oracle_vs_cos", "interaction_share"],
         "conditional: plus interaction share"),
        ("RR_pop_oracle_vs_cos", ["RR_ref_oracle_vs_cos", "interaction_share", "A_sup"],
         "conditional: plus recoverability"),
        ("RR_pop_oracle_vs_cos", ["RR_ref_oracle_vs_cos", "interaction_share", "A_sup", "R_int"],
         "conditional: plus interaction reproducibility"),
        ("RR_pop_oracle_vs_cos", ["RR_ref_oracle_vs_cos", "D_old", "A_sup"],
         "conditional: the old statistic"),
        ("RR_pop_oracle_vs_l2", ["RR_ref_oracle_vs_l2", "interaction_share", "A_sup"],
         "conditional, magnitude-controlled"),
    ]
    d["H_x_share"] = d["H"] * d["interaction_share"]
    for y, terms, label in specs:
        t = ["H_x_share" if c == "H_x_share" else c for c in terms]
        if y == "G_oracle_vs_l2" and "H_x_share" in t:
            d["H_x_share"] = d["H_l2"] * d["interaction_share"]
        try:
            m, sub = fit(d, y, t, "cell_line")
        except Exception as exc:                       # noqa: BLE001
            rows.append({"outcome": y, "model": label, "error": str(exc)[:160]})
            continue
        ci = m.conf_int()
        for name in m.params.index:
            rows.append({"outcome": y, "model": label, "term": name,
                         "beta": float(m.params[name]),
                         "ci_lo": float(ci.loc[name, 0]), "ci_hi": float(ci.loc[name, 1]),
                         "p": float(m.pvalues[name]),
                         "r2": float(m.rsquared), "n": int(m.nobs),
                         "n_clusters": int(sub.cell_line.nunique())})
    reg = pd.DataFrame(rows)
    reg.to_csv(out / "regression.csv", index=False)

    # ---- non-parametric companion: headroom x interaction-share quartiles ----
    q = d.dropna(subset=["H", "interaction_share", "G_oracle_vs_cos"]).copy()
    q["H_q"] = pd.qcut(q.H.rank(method="first"), 4, labels=["Q1", "Q2", "Q3", "Q4"])
    q["share_q"] = pd.qcut(q.interaction_share, 4, labels=["Q1", "Q2", "Q3", "Q4"])
    strata = (q.groupby(["H_q", "share_q"], observed=True)
                .agg(n=("H", "size"), median_H=("H", "median"),
                     median_share=("interaction_share", "median"),
                     G_oracle_vs_cos=("G_oracle_vs_cos", "mean"),
                     G_oracle_vs_l2=("G_oracle_vs_l2", "mean"),
                     corrected_flip=("corrected_flip_oracle_vs_cos", "mean"))
                .reset_index())
    strata.to_csv(out / "strata.csv", index=False)

    # ---- how much of the headroom-gain correlation is mechanical? ----
    #
    # Reshuffling the population route's reciprocal ranks WITHIN each context destroys any real
    # link between the two scorers while preserving both marginal distributions, the ceiling at
    # RR = 1, and the clustering. Whatever correlation survives that is definitional.
    rng = np.random.default_rng(0)
    null_rho = []
    for _ in range(200):
        perm = d.groupby("cell_line").RR_pop_oracle_vs_cos.transform(
            lambda x: rng.permutation(x.to_numpy()))
        null_rho.append(float(spearmanr(d.H, perm - d.RR_ref_oracle_vs_cos).statistic))
    obs_rho = float(spearmanr(d.H, d.G_oracle_vs_cos).statistic)

    ok = d.dropna(subset=["interaction_share", "G_oracle_vs_cos", "A_sup", "D_old"])
    summary = {
        "n_queries": int(len(d)), "n_complete": int(len(ok)),
        "spearman_with_oracle_gain": {
            "headroom": float(spearmanr(ok.H, ok.G_oracle_vs_cos).statistic),
            "interaction_share": float(spearmanr(ok.interaction_share, ok.G_oracle_vs_cos).statistic),
            "S_int": float(spearmanr(ok.S_int, ok.G_oracle_vs_cos).statistic),
            "R_int": float(spearmanr(ok.R_int, ok.G_oracle_vs_cos).statistic),
            "A_sup": float(spearmanr(ok.A_sup, ok.G_oracle_vs_cos).statistic),
            "D_old": float(spearmanr(ok.D_old, ok.G_oracle_vs_cos).statistic),
        },
        "spearman_with_magnitude_controlled_gain": {
            "headroom": float(spearmanr(ok.H_l2, ok.G_oracle_vs_l2).statistic),
            "interaction_share": float(spearmanr(ok.interaction_share, ok.G_oracle_vs_l2).statistic),
            "A_sup": float(spearmanr(ok.A_sup, ok.G_oracle_vs_l2).statistic),
            "D_old": float(spearmanr(ok.D_old, ok.G_oracle_vs_l2).statistic),
        },
        "headroom_correlation_is_mechanical": {
            "observed_spearman_H_vs_G": obs_rho,
            "null_mean": float(np.mean(null_rho)),
            "null_ci": [float(np.percentile(null_rho, 2.5)), float(np.percentile(null_rho, 97.5))],
            "observed_inside_null": bool(np.percentile(null_rho, 2.5) <= obs_rho
                                         <= np.percentile(null_rho, 97.5)),
            "n_shuffles": len(null_rho),
            "note": ("the null keeps both marginals, the RR<=1 ceiling and the clustering, and "
                     "destroys only the pairing between the two scorers"),
        },
        "queries_with_zero_headroom": int((d.H <= 1e-12).sum()),
        "nested_r2": {r["model"]: r["r2"] for _, r in
                      reg[reg.outcome == "G_oracle_vs_cos"].drop_duplicates("model").iterrows()
                      if "r2" in r and r["r2"] == r["r2"]},
        "runtime_seconds": round(time.time() - t0, 1),
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    log(json.dumps(summary["spearman_with_oracle_gain"], indent=2))
    log(f"wrote {out} ({time.time() - t0:.0f}s)")


if __name__ == "__main__":
    sys.exit(main())
