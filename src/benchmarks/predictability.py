"""HIR-Bench predictability layer.

Extract observable (non-oracle) features from a benchmark cell and predict
whether a EvalShift-style distributional method would improve over mean retrieval.

The predictability module must NOT import oracle_utility — it uses only
information available to a retrieval method at query time: the candidate
response populations and the query population.

Two feature families:
  1. Population-diversity features — within-candidate heterogeneity
  2. Score-disagreement features  — gap between mean and distributional scores
"""
from __future__ import annotations

import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import roc_auc_score

from .heterogeneous_retrieval_benchmark import HIRCell


# ── observable features ──────────────────────────────────────────────────────

def subpop_variance_ratio(X: np.ndarray, n_clusters: int = 2) -> float:
    """Between-cluster / total variance.  Higher = more subpopulation structure."""
    if X.shape[0] < n_clusters + 1:
        return 0.0
    mu = X.mean(axis=0)
    sst = float(np.sum((X - mu) ** 2))
    if sst < 1e-12:
        return 0.0
    km = KMeans(n_clusters=n_clusters, n_init=3, random_state=0, max_iter=50).fit(X)
    ssw = sum(float(np.sum((X[km.labels_ == c] - X[km.labels_ == c].mean(0)) ** 2))
              for c in range(n_clusters))
    return float((sst - ssw) / sst)


def isotropy_index(X: np.ndarray) -> float:
    """Ratio of smallest to largest eigenvalue of the covariance.  1.0 = isotropic."""
    if X.shape[0] < 3 or X.shape[1] < 2:
        return 1.0
    # Use top-2 eigenvalues only (fast)
    mu = X.mean(axis=0)
    Xc = X - mu
    if Xc.shape[0] > 500:
        rng = np.random.default_rng(0)
        idx = rng.choice(Xc.shape[0], 500, replace=False)
        Xc = Xc[idx]
    cov = Xc.T @ Xc / (Xc.shape[0] - 1)
    evals = np.linalg.eigvalsh(cov)
    evals = evals[evals > 0]
    if len(evals) < 2:
        return 1.0
    return float(evals.min() / evals.max())


def response_diversity(X: np.ndarray, n_samples: int = 200) -> float:
    """Average pairwise cosine distance among cells. Higher = more diverse."""
    if X.shape[0] < 2:
        return 0.0
    rng = np.random.default_rng(0)
    if X.shape[0] > n_samples:
        idx = rng.choice(X.shape[0], n_samples, replace=False)
        X = X[idx]
    norms = np.linalg.norm(X, axis=1, keepdims=True)
    norms = np.maximum(norms, 1e-12)
    Xn = X / norms
    sims = Xn @ Xn.T
    np.fill_diagonal(sims, 0)
    n = sims.shape[0]
    return float(1.0 - sims.sum() / (n * (n - 1)))


def score_disagreement(mean_scores: np.ndarray, dist_scores: np.ndarray) -> float:
    """Kendall tau distance between mean-based and distributional rankings.

    Higher = the two scoring paradigms disagree more = EvalShift may help.
    """
    from scipy.stats import kendalltau
    tau, _ = kendalltau(mean_scores, dist_scores)
    if not np.isfinite(tau):
        # kendalltau is NaN when either ranking is constant (no variance to
        # disagree on) -> treat as zero disagreement rather than propagating NaN.
        return 0.0
    return float(1 - tau) / 2  # convert to distance in [0, 1]


# ── cell-level feature extraction ────────────────────────────────────────────

def extract_features(cell: HIRCell, max_candidates: int = 20, seed: int = 0) -> dict:
    """Extract observable (non-oracle) features from a benchmark cell.

    These features use only the candidate populations and the query, nothing from the latent
    targets or the utility matrix. They are the feature set the predictability claim needs.

    The candidate-level features are MEANS over candidates, so they are estimated from a
    deterministic subsample of at most ``max_candidates`` candidates (each one costs a
    k-means fit, an eigendecomposition and a pairwise-cosine pass, and the FULL grid has
    13,440 cells with libraries of up to 100). ``n_candidates_sampled`` is returned so the
    cap is visible in the output rather than silently applied.
    """
    ids = list(cell.drug_ids)
    if len(ids) > max_candidates:
        rng = np.random.default_rng(seed)
        ids = [ids[i] for i in sorted(rng.choice(len(ids), max_candidates, replace=False))]

    vr_vals, iso_vals, div_vals = [], [], []
    for d_id in ids:
        X = cell.candidate_populations[d_id]
        vr_vals.append(subpop_variance_ratio(X))
        iso_vals.append(isotropy_index(X))
        div_vals.append(response_diversity(X))

    return {
        "mean_subpop_variance_ratio": float(np.mean(vr_vals)),
        "mean_isotropy_index": float(np.mean(iso_vals)),
        "mean_response_diversity": float(np.mean(div_vals)),
        "query_subpop_variance_ratio": subpop_variance_ratio(cell.query_X),
        "query_isotropy_index": isotropy_index(cell.query_X),
        "query_response_diversity": response_diversity(cell.query_X),
        "n_candidates_sampled": int(len(ids)),
        "n_candidates_total": int(len(cell.drug_ids)),
    }


# ── leakage-safe predictability scoring ──────────────────────────────────────

# The two feature sets, kept explicitly apart because the distinction is the whole point.
#
# ORACLE_FEATURES are computed from cell.utility_matrix (preference_conflict.py). So is the
# label, oracle_flip_risk (oracle_utility.py). A model that predicts the label from these is
# predicting one function of the utility matrix from another function of the SAME utility
# matrix. That is exactly the evaluation circularity this project exists to audit, so an AUC
# obtained this way must never be described as "failure is predictable from observable
# features". It is reported here only as an upper bound, and it is labelled oracle-derived.
#
# OBSERVABLE_FEATURES come from extract_features(), which touches only the candidate
# populations and the query, i.e. what a retrieval method can actually see at query time.
# This is the feature set the claim requires. It was implemented and then never called.
ORACLE_FEATURES = ["topk_disagreement", "weighted_kendall_conflict",
                   "standard_kendall_conflict", "response_cosine"]
OBSERVABLE_FEATURES = ["mean_subpop_variance_ratio", "mean_isotropy_index",
                       "mean_response_diversity", "query_subpop_variance_ratio",
                       "query_isotropy_index", "query_response_diversity"]

# The label is a deterministic function of the parameters that shape the utility matrix.
# grid_id ALSO encodes information_condition, cells_per_subpop and noise_sigma, none of
# which change the utility matrix, so leave-one-grid_id-out leaves near-identical copies of
# the held-out row in the training set. Group on the axes that actually determine the label.
LABEL_DETERMINING_GROUP = ["alpha", "conflict_level"]


def predictability_auc(method_independent_df, method_performance_df=None,
                       target_col: str = "oracle_flip_risk",
                       feature_cols: list | None = None,
                       group_cols: list | None = None) -> dict:
    """Cross-validated AUC for predicting retrieval failure.

    ``feature_cols`` defaults to OBSERVABLE_FEATURES: the claim under test is that failure
    is predictable from what a method can SEE, not from the oracle that defines failure.
    Pass ORACLE_FEATURES explicitly to measure the circular upper bound.

    ``group_cols`` defaults to LABEL_DETERMINING_GROUP so that every replicate sharing a
    label-determining parameter cell is held out TOGETHER. Grouping on grid_id instead
    leaves ~12 near-duplicate rows of each held-out cell in the training set, which inflates
    the AUC and makes any n-based confidence interval invalid.

    Returns the pooled AUC, the per-fold AUC distribution (mean and 95% interval), the
    majority-class baseline, and the feature coefficients.
    """
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler

    df = method_independent_df.copy()
    feature_cols = list(feature_cols) if feature_cols is not None else list(OBSERVABLE_FEATURES)
    group_cols = list(group_cols) if group_cols is not None else list(LABEL_DETERMINING_GROUP)

    missing = [c for c in feature_cols if c not in df.columns]
    if missing:
        raise KeyError(
            f"feature column(s) {missing} not in the benchmark table. If you asked for the "
            f"observable feature set, exp11 must call benchmarks.predictability."
            f"extract_features(cell) and log those columns. Refusing to silently fall back "
            f"to the oracle features.")

    # Only keep conflict-varying cells (drop distractors, keep worst welfare)
    df = df[df.welfare_type == "worst"].copy()

    y = df[target_col].values.astype(int)
    base = {"feature_set": feature_cols, "group_cols": group_cols,
            "n_positive": int(y.sum()), "n_negative": int(len(y) - y.sum()),
            "majority_baseline": float(max(y.mean(), 1 - y.mean())) if len(y) else float("nan")}
    if len(set(y)) < 2:
        return {**base, "auc": float("nan"), "auc_fold_mean": float("nan"),
                "auc_fold_lo": float("nan"), "auc_fold_hi": float("nan"), "n_folds": 0,
                "feature_importances": {f: 0.0 for f in feature_cols}}

    X = df[feature_cols].values
    groups = df[group_cols].astype(str).agg("|".join, axis=1).values
    unique_groups = np.unique(groups)
    base["n_effective_units"] = int(len(unique_groups))

    y_pred = np.zeros(len(y), dtype=float)
    coefs = np.zeros(len(feature_cols))
    fold_aucs, n_fit = [], 0

    for g in unique_groups:
        mask = groups == g
        X_train, y_train = X[~mask], y[~mask]
        if len(set(y_train)) < 2:
            y_pred[mask] = y_train.mean() if len(y_train) else 0.5
            continue
        scaler = StandardScaler().fit(X_train)
        lr = LogisticRegression(max_iter=1000, random_state=0)
        lr.fit(scaler.transform(X_train), y_train)
        p = lr.predict_proba(scaler.transform(X[mask]))[:, 1]
        y_pred[mask] = p
        coefs += lr.coef_[0]
        n_fit += 1
        # a per-fold AUC only exists if the held-out fold has both classes; with a
        # deterministic label these folds are often single-class, which is itself the
        # finding and is reported via n_folds rather than hidden.
        if len(set(y[mask])) == 2:
            fold_aucs.append(float(roc_auc_score(y[mask], p)))

    if n_fit:
        coefs /= n_fit
    pooled = float(roc_auc_score(y, y_pred)) if len(set(y)) == 2 else float("nan")
    fa = np.asarray(fold_aucs, dtype=float)

    return {
        **base,
        "auc": pooled,                                   # pooled over out-of-fold predictions
        "auc_fold_mean": float(fa.mean()) if len(fa) else float("nan"),
        "auc_fold_lo": float(np.percentile(fa, 2.5)) if len(fa) > 1 else float("nan"),
        "auc_fold_hi": float(np.percentile(fa, 97.5)) if len(fa) > 1 else float("nan"),
        "n_folds": int(len(fa)),
        "feature_importances": dict(zip(feature_cols, coefs.tolist())),
    }
