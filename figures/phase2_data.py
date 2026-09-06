"""Every number Figure 5 draws, loaded from results/. No panel hard-codes a value.

WHY THIS FILE EXISTS
--------------------
The rebuilt Figure 5 carries the post-Phase-II intervention-retrieval result, whose numbers live
in five different result trees written by four different runners. Before this file, a panel that
wanted the oracle MRR reached into one of them and wrote a float. That is how a figure and its
manuscript drift apart, and the audit that produced CORRECTIONS.md R65 found exactly that failure
in the previous deck: a dispersion quoted in the text with no file behind it.

Every accessor here raises on a missing file or a missing key rather than returning a default. A
panel that cannot find its number must fail the build, not draw a plausible one.

SOURCES
-------
    results/phase2_transition/phase_a/          oracle ceiling (summary, paired deltas)
    results/phase2_transition/phase_b/          leave-one-cell-line-out prediction
    results/phase2_transition/phase_b_p5/       the state-conditioned predictor and its Gate 1
    results/phase2_transition/gate1_interaction/ the repaired interaction statistic, observed
    results/phase2_transition/synthesis/        decision relevance (flips)
    results/phase2_transition/bottleneck/       the conditional regression
"""
from __future__ import annotations

import os
from functools import lru_cache

import numpy as np
import pandas as pd

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))   # figures/ -> repo root
P2 = os.path.join(REPO, "results", "phase2_transition")

POP_SCORER = "energy"          # the plan's primary population route
MEAN_SCORER = "mean_cosine"    # the plan's mean route
MAG_SCORER = "mean_l2"         # the magnitude-aware mean diagnostic


def _read(*parts: str) -> pd.DataFrame:
    path = os.path.join(P2, *parts)
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"{path} is missing. Figure 5 is drawn from the Phase-II result tree; regenerate it "
            f"with the commands in docs/phase2/README.md rather than editing this panel.")
    return pd.read_csv(path)


def _one(df: pd.DataFrame, where: dict, what: str) -> pd.Series:
    m = np.ones(len(df), dtype=bool)
    for k, v in where.items():
        m &= (df[k] == v).to_numpy()
    sub = df[m]
    if len(sub) != 1:
        raise KeyError(f"{what}: {where} matched {len(sub)} rows, expected exactly 1")
    return sub.iloc[0]


# ---------------------------------------------------------------------------
# b: the oracle decomposition, direction -> magnitude -> distribution
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def oracle_ladder() -> pd.DataFrame:
    """Three rows, in the order the argument builds them, with their bootstrap intervals."""
    s = _read("phase_a", "summary.csv").set_index("scorer")
    # Two-line labels are geometry, not taste: at the 2.24 in axes this panel gets, the one-line
    # forms overlap from the second category on.
    order = [(MEAN_SCORER, "direction\nonly"), (MAG_SCORER, "+\nmagnitude"),
             (POP_SCORER, "+\ndistribution")]
    return pd.DataFrame([{"scorer": k, "label": lab, "MRR": float(s.loc[k, "MRR"]),
                          "lo": float(s.loc[k, "MRR_lo"]), "hi": float(s.loc[k, "MRR_hi"])}
                         for k, lab in order])


# ---------------------------------------------------------------------------
# c: decision correction, corrected against reverse flips
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def oracle_flips() -> pd.DataFrame:
    """Corrected and reverse top-1 flips at the oracle, against both reference scorers."""
    g = _read("synthesis", "gate3_decision_relevance.csv")
    out = []
    for ref, lab in ((MEAN_SCORER, "direction\nonly"), (MAG_SCORER, "magnitude\naware")):
        r = _one(g, {"phase": "oracle", "predictor": "oracle", "reference": ref}, "oracle flips")
        out.append({"reference": ref, "label": lab,
                    "corrected": float(r["corrected_flip@1"]),
                    "corrected_lo": float(r["corrected_flip@1_lo"]),
                    "corrected_hi": float(r["corrected_flip@1_hi"]),
                    "reverse": float(r["reverse_flip@1"]),
                    "reverse_lo": float(r["reverse_flip@1_lo"]),
                    "reverse_hi": float(r["reverse_flip@1_hi"])})
    return pd.DataFrame(out)


# ---------------------------------------------------------------------------
# d: what prediction does to the gain
# ---------------------------------------------------------------------------

# One-line forms, for the panel that stacks all seven rows: at seven rows in a 1.16 in axes each
# row is 12 pt tall and a two-line 6.8 pt label needs 16, so the two-line forms collide.
PREDICTOR_LABEL_1L = {
    "average_effect": "average effect",
    "linear_latent": "linear latent",
    "nearest_context": "nearest context",
    "nearest_context_cells": "nearest context, cells",
    "ot_map": "OT map",
    "state_conditioned_average_effect": "state-cond. avg effect",
}

PREDICTOR_LABEL = {
    "average_effect": "average\neffect",
    "linear_latent": "linear\nlatent",
    "nearest_context": "nearest\ncontext",
    "nearest_context_cells": "nearest\ncontext, cells",
    "ot_map": "OT\nmap",
    "state_conditioned_average_effect": "state-cond.\naverage effect",
}


@lru_cache(maxsize=1)
def gain_ladder() -> pd.DataFrame:
    """dMRR of the population route over the mean route: the oracle, then each predictor.

    The state-conditioned predictor comes from the phase_b_p5 run, which is the same runner with
    that predictor added; the other five come from phase_b. Both are read rather than merged by
    hand so a change in either shows up here.
    """
    rows = []
    a = _read("phase_a", "delta_vs_reference.csv")
    r = _one(a, {"scorer": POP_SCORER, "reference": MEAN_SCORER}, "oracle gain")
    rows.append({"key": "oracle", "label": "oracle (observed)", "dMRR": float(r["dMRR"]),
                 "lo": float(r["dMRR_lo"]), "hi": float(r["dMRR_hi"]), "is_oracle": True})
    for tree in ("phase_b", "phase_b_p5"):
        d = _read(tree, "delta_vs_reference.csv")
        for pred in sorted(d.predictor.unique()):
            if pred in {x["key"] for x in rows}:
                continue
            r = _one(d, {"scorer": POP_SCORER, "reference": MEAN_SCORER, "predictor": pred},
                     f"{tree}/{pred}")
            rows.append({"key": pred, "label": PREDICTOR_LABEL_1L[pred], "dMRR": float(r["dMRR"]),
                         "lo": float(r["dMRR_lo"]), "hi": float(r["dMRR_hi"]), "is_oracle": False})
    order = ["oracle", "average_effect", "state_conditioned_average_effect", "linear_latent",
             "ot_map", "nearest_context", "nearest_context_cells"]
    df = pd.DataFrame(rows).set_index("key").reindex(order).reset_index()
    if df.dMRR.isna().any():
        raise KeyError(f"missing predictors: {list(df.key[df.dMRR.isna()])}")
    return df


# ---------------------------------------------------------------------------
# e: the interaction a predictor generates, against the one that is there
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def predicted_interaction() -> pd.DataFrame:
    """Median predicted drug-by-state interaction per predictor, and the observed value.

    Read as ||r_1 - r_2||^2 / p, the same quantity on both sides. A prediction carries no
    sampling noise, so it needs no cross-fitting; the observed column is the cross-fitted
    estimate, which is the only version of it that is unbiased.
    """
    g = pd.read_csv(os.path.join(P2, "phase_b_p5", "gate1_predicted.csv.gz"))
    med = (g.groupby("predictor").predicted_S_int.median().rename("S_int_pred").reset_index())
    obs = _read("gate1_interaction", "interaction_per_query.csv").S_int.dropna()
    med["label"] = med.predictor.map(PREDICTOR_LABEL)
    if med.label.isna().any():
        raise KeyError(f"unlabelled predictors: {list(med.predictor[med.label.isna()])}")
    med.attrs["observed_median"] = float(obs.median())
    med.attrs["observed_n"] = int(len(obs))
    return med


# ---------------------------------------------------------------------------
# f: the constructive test
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def state_conditioned_retrieval() -> pd.DataFrame:
    """Mean-route and population-route MRR for the baseline and the state-conditioned predictor."""
    s = _read("phase_b_p5", "summary.csv")
    out = []
    for pred in ("average_effect", "state_conditioned_average_effect"):
        for scorer, route in ((MEAN_SCORER, "mean"), (POP_SCORER, "population")):
            r = _one(s, {"predictor": pred, "scorer": scorer}, f"{pred}/{scorer}")
            out.append({"predictor": pred, "label": PREDICTOR_LABEL[pred], "route": route,
                        "MRR": float(r["MRR"]), "lo": float(r["MRR_lo"]),
                        "hi": float(r["MRR_hi"])})
    return pd.DataFrame(out)


# ---------------------------------------------------------------------------
# g: does anything locate the gain, once the mean route's own performance is known
# ---------------------------------------------------------------------------

CONDITIONAL_MODEL = "conditional: plus interaction reproducibility"
CONDITIONAL_OLD = "conditional: the old statistic"
# One line each. Four rows in a 1.06 in axes leave 19 pt per row, and a two-line 6.8 pt label
# needs 16 of them, so the two-line forms crowd into each other's rows.
TERM_LABEL = {
    "interaction_share": "interaction share",
    "A_sup": "response detectability",
    "R_int": "reproducibility",
    "D_old": "naive cosine",
}


@lru_cache(maxsize=1)
def conditional_terms() -> pd.DataFrame:
    """Standardised coefficients from the tautology-free specification.

    The outcome is the population route's own reciprocal rank with the mean route's reciprocal
    rank as a covariate, so a coefficient answers "given how well the mean route did, does this
    variable predict how well the population route does". The covariate itself is not drawn: it
    is the control, not a finding.
    """
    r = _read("bottleneck", "regression.csv")
    r = r[r.outcome == "RR_pop_oracle_vs_cos"]
    out = []
    for model, terms in ((CONDITIONAL_MODEL, ["interaction_share", "A_sup", "R_int"]),
                         (CONDITIONAL_OLD, ["D_old"])):
        for t in terms:
            row = _one(r, {"model": model, "term": t}, f"{model}/{t}")
            out.append({"term": t, "label": TERM_LABEL[t], "beta": float(row["beta"]),
                        "lo": float(row["ci_lo"]), "hi": float(row["ci_hi"]),
                        "p": float(row["p"]), "n": int(row["n"]),
                        "n_clusters": int(row["n_clusters"])})
    return pd.DataFrame(out)


# ---------------------------------------------------------------------------
# THE 2026-09-03 SPLIT: Figure 5 keeps the oracle, Figure 6 takes the predictor
# ---------------------------------------------------------------------------
# Everything above this line was written for the eight-panel Figure 5 and is unchanged. The
# accessors below were added when that page became two: an oracle figure that asks what
# population information is worth when candidate responses are OBSERVED, and a prediction figure
# that asks what survives when they are PREDICTED. No experiment was re-run for the split; every
# value below is read from the same Phase-II tree the eight panels already read.


@lru_cache(maxsize=1)
def ceiling() -> dict:
    """How much room the oracle mean route leaves the population route, per query.

    The single largest term in the whole analysis, and it is not biology: on most queries the mean
    route already ranks the true drug first at every seed, so its reciprocal rank is exactly 1 and
    no decision is available to improve. Returned as the per-query reciprocal ranks themselves,
    because the panel draws the distribution rather than the count, and the count is then read off
    the drawn array rather than typed beside it.
    """
    b = _read("bottleneck", "bottleneck_per_query.csv")
    rr = b["RR_ref_oracle_vs_cos"].to_numpy(dtype=float)
    gain = b["G_oracle_vs_cos"].to_numpy(dtype=float)
    if not np.isfinite(rr).all():
        raise ValueError("bottleneck_per_query.csv has a non-finite reference reciprocal rank")
    n_perfect = int((rr >= 1.0 - 1e-12).sum())
    return {"rr_mean_route": rr, "gain": gain, "n": int(len(rr)), "n_perfect": n_perfect,
            "frac_perfect": n_perfect / len(rr)}


@lru_cache(maxsize=1)
def headroom_null() -> dict:
    """The observed headroom-gain correlation against the ceiling null that reproduces it.

    Reported once as the strongest explanation of where population scoring pays. The null keeps
    both marginals, the RR <= 1 ceiling and the clustering, and destroys only the pairing between
    the two scorers; it reproduces the observed value. The accessor raises rather than defaulting
    if the key is missing, because a panel drawing this without the null would restate the
    retracted claim.
    """
    import json
    path = os.path.join(P2, "bottleneck", "summary.json")
    if not os.path.exists(path):
        raise FileNotFoundError(f"{path} is missing; Figure 5's ceiling panel has no null to draw")
    with open(path, encoding="utf-8") as fh:
        s = json.load(fh)
    m = s["headroom_correlation_is_mechanical"]
    return {"observed": float(m["observed_spearman_H_vs_G"]),
            "null_mean": float(m["null_mean"]),
            "null_lo": float(m["null_ci"][0]), "null_hi": float(m["null_ci"][1]),
            "n_shuffles": int(m["n_shuffles"]),
            "inside": bool(m["observed_inside_null"])}


# The two statistics the interaction gate can be built on, and the two ways either can be an
# artefact of effect size rather than a measurement of drug-by-state interaction.
STAT_LABEL = {"S_int": "cross-fitted\ninteraction", "D_old": "naive\ncosine"}
CONFOUND_LABEL = {"response_norm": "response\nmagnitude", "n_treated": "cells\nper arm"}


@lru_cache(maxsize=1)
def interaction_audit() -> dict:
    """Check 5 of the interaction gate: each statistic against the two things it must not measure.

    A statistic of drug-by-state interaction that runs NEGATIVE with response magnitude scores the
    weakest drugs as the most state-dependent, which is the failure that retired the old one. The
    positive control is the same statistic on a construction built from the plate's own cells,
    where interaction is present by design.
    """
    import json
    path = os.path.join(P2, "gate1_interaction", "checks.json")
    if not os.path.exists(path):
        raise FileNotFoundError(f"{path} is missing; the interaction audit panel has no source")
    with open(path, encoding="utf-8") as fh:
        c = json.load(fh)
    a = c["check5_effect_size_audit"]
    rows = []
    for stat in ("D_old", "S_int"):
        for conf in ("response_norm", "n_treated"):
            rows.append({"stat": stat, "confound": conf,
                         "rho": float(a[f"spearman_{stat}_vs_{conf}"])})
    return {"rows": pd.DataFrame(rows), "n_scored": int(c["n_scored"]),
            "control_ratio": float(c["check3_positive_control"]["ratio_to_real_median"]),
            "control_n": int(c["check3_positive_control"]["n"]),
            "frac_positive": float(c["observed"]["frac_S_int_positive"])}


@lru_cache(maxsize=1)
def route_loss(predictor: str = "average_effect") -> pd.DataFrame:
    """What deleting the observed candidate responses costs each route, oracle to predicted.

    Two rows, one per route, each with its oracle MRR, its predicted MRR and the loss. The loss is
    computed here rather than read, because no result file records it: the two MRRs live in two
    different summary files and subtracting them in a panel is how a number gets typed by hand.
    The column is named "loss" and not "drop": pandas resolves df.drop to DataFrame.drop, so a
    panel reading r.drop gets a bound method and a format error rather than a number.
    """
    a = _read("phase_a", "summary.csv").set_index("scorer")
    b = _read("phase_b", "summary.csv")
    out = []
    for scorer, route in ((MEAN_SCORER, "mean route"), (POP_SCORER, "population route")):
        r = _one(b, {"predictor": predictor, "scorer": scorer}, f"phase_b/{predictor}/{scorer}")
        out.append({"scorer": scorer, "route": route,
                    "oracle": float(a.loc[scorer, "MRR"]),
                    "predicted": float(r["MRR"]),
                    "predicted_lo": float(r["MRR_lo"]), "predicted_hi": float(r["MRR_hi"]),
                    "loss": float(a.loc[scorer, "MRR"]) - float(r["MRR"])})
    return pd.DataFrame(out)


@lru_cache(maxsize=1)
def predicted_reference_deltas(predictor: str = "average_effect") -> pd.DataFrame:
    """The population route's deficit under the predictor, against each of the two mean routes.

    Three paired deltas on one axis, all on the same predictions and the same queries:
    the population route against direction-only, the magnitude-aware mean against direction-only,
    and the population route against the magnitude-aware mean. The first is the published deficit;
    the second shows that the magnitude-aware mean carries almost all of it; the third is what is
    left once magnitude is controlled.
    """
    d = _read("phase_b", "delta_vs_reference.csv")
    spec = ((POP_SCORER, MEAN_SCORER, "population\nvs direction-only"),
            (MAG_SCORER, MEAN_SCORER, "magnitude-aware\nvs direction-only"),
            (POP_SCORER, MAG_SCORER, "population\nvs magnitude-aware"))
    out = []
    for scorer, ref, label in spec:
        r = _one(d, {"predictor": predictor, "scorer": scorer, "reference": ref},
                 f"phase_b/{predictor}/{scorer} vs {ref}")
        out.append({"scorer": scorer, "reference": ref, "label": label,
                    "dMRR": float(r["dMRR"]), "lo": float(r["dMRR_lo"]),
                    "hi": float(r["dMRR_hi"]), "n": int(r["n_paired"])})
    return pd.DataFrame(out)


# The four ways a query can fall out when the oracle gain meets the predictor, in the order the
# argument reads them: neither route gains, the oracle gain does not survive, it survives, and a
# gain appears that the oracle never had.
CASE_LABEL = (("case_I_neither", "neither"),
              ("case_II_oracle_only", "oracle only"),
              ("case_III_both", "both"),
              ("case_IV_predicted_only", "predicted only"))


@lru_cache(maxsize=1)
def case_decomposition() -> pd.DataFrame:
    """Per predictor, how the 3,992 queries split across those four cases, plus what is retained."""
    d = _read("synthesis", "oracle_to_prediction.csv")
    out = []
    for _, r in d.iterrows():
        row = {"predictor": r["predictor"], "label": PREDICTOR_LABEL_1L[r["predictor"]],
               "n_queries": int(r["n_queries"]),
               "retained": float(r["retained_fraction_of_oracle_gain"])}
        for key, lab in CASE_LABEL:
            row[key] = int(r[key])
        total = sum(row[k] for k, _ in CASE_LABEL)
        if total != row["n_queries"]:
            raise ValueError(f"{r['predictor']}: the four cases sum to {total}, not "
                             f"{row['n_queries']}; they are meant to partition the queries")
        out.append(row)
    order = ["average_effect", "linear_latent", "ot_map", "nearest_context",
             "nearest_context_cells"]
    return pd.DataFrame(out).set_index("predictor").reindex(order).reset_index()


@lru_cache(maxsize=1)
def recoverability() -> dict:
    """Gate 2: how well the state that carries the interaction can be recovered from the cells.

    Two accuracies per query, on the same cells. ``A_sup`` is recovered with the state labels
    given, which is a ceiling and not a method; ``A_unsup`` is recovered without them, which is
    what a deployed pipeline would have. Both are two-class balanced problems, so 0.5 is chance
    and the accessor asserts that neither column has left [0.5, 1], because a value below chance
    would mean the two arms were swapped rather than that recovery failed.
    """
    g = _read("phase_c", "gate2_observed.csv")
    for col in ("A_sup", "A_unsup"):
        lo, hi = float(g[col].min()), float(g[col].max())
        if not (0.5 - 1e-9 <= lo and hi <= 1.0 + 1e-9):
            raise ValueError(f"{col} runs {lo:.3f} to {hi:.3f}, outside [0.5, 1] for a balanced "
                             f"two-class accuracy; the arms may be swapped")
    return {"sup": g["A_sup"].to_numpy(dtype=float),
            "unsup": g["A_unsup"].to_numpy(dtype=float),
            "n": int(len(g)), "n_lines": int(g["cell_line"].nunique()),
            "n_drugs": int(g["drug"].nunique())}
