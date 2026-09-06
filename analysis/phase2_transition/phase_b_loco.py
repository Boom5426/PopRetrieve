#!/usr/bin/env python
"""Phase B: leave-one-cell-line-out predict-then-retrieve.

WHAT QUESTION THIS ANSWERS
--------------------------
    After leakage-safe forward prediction, how much of Phase A's population advantage survives?

Phase A gave every candidate its observed response in the held-out context. Phase B deletes all
of them. For a held-out context c, a predictor is fitted on the other 43 usable contexts only,
then asked to imagine each of the 92 candidates' response in c from c's vehicle cells alone. The
retrieval rules are exactly Phase A's, and the query cells, the source cells and the sublibrary
split are exactly Phase A's, because both phases draw them from generators keyed by purpose
rather than by call order (phase2_common.rng_for). The two phases are therefore paired query by
query, which is what the oracle-to-prediction decomposition needs.

THE LEAKAGE RULE, WHICH IS THE POINT OF THIS PHASE
--------------------------------------------------
No treated cell of the held-out context may reach a predictor, a representation fit or the
ranker. The held-out context contributes exactly two things, both of which are task inputs: its
vehicle cells (X_source) and the current query's own target population. Concretely, every PCA
below is refitted per held-out context on training contexts only, and no per-drug quantity is
ever estimated from the held-out context.

PREDICTORS
----------
The frozen set from plan section 10, plus one diagnostic variant that the section's own logic
requires. Three of the four named predictors are additive: they emit one signature per drug and
apply it to every source cell identically. An additive predictor produces a candidate population
that is the source population rigidly translated, so its within-population structure is the
vehicle's, not the drug's, and no distributional scorer can recover state-specific response from
it. Running only additive predictors would therefore answer the Phase B question by construction
rather than by measurement, so `nearest_context_cells` is included: it transfers the neighbour
context's treated population itself, and is the cheapest predictor in this family that can carry
a non-additive response shape.

    average_effect            delta_d = mean over training contexts of (mu_{d,c'} - mu_{0,c'}).
                              Additive. The plan's additive lower baseline.
    state_conditioned_average_effect
                              the same average effect estimated separately per cell-cycle state,
                              delta_{d,s} = mean over training contexts of
                              (mu_{d,c',s} - mu_{0,c',s}), applied to each source cell according
                              to its own state. The cheapest possible non-additive predictor: it
                              costs one extra grouping and nothing else, and it is the first
                              predictor in this set that can produce a non-zero differential
                              response at all. A source cell whose state has no training estimate
                              falls back to the pooled delta_d, which is recorded rather than
                              silently applied.
    nearest_context           delta_d taken from the single training context whose vehicle mean
                              is closest in cosine to the held-out vehicle mean. Additive.
    linear_latent             the average effect truncated to the principal components of the
                              training cells that reach LATENT_VAR_TARGET of their variance.
                              Additive by construction: for an orthonormal basis P,
                              decode(encode(x) + dz) = x + P dz.
    ot_map                    a Gaussian (Bures) optimal-transport map in the training PCA
                              basis, from the pooled within-context vehicle covariance to drug
                              d's pooled within-condition treated covariance, with the mean
                              shifted by the average latent effect. Each cloud is centred on its
                              own condition mean before pooling, so the treated covariance is
                              within-condition cell scatter and does not absorb between-context
                              variation in the effect itself. The map is applied to the held-out
                              vehicle cells as a latent EDIT, x_hat = x + P((A - I)z + b), so the
                              prediction keeps the part of each cell outside the latent subspace
                              instead of collapsing the population into 50 dimensions. It reduces
                              exactly to linear_latent when A is the identity. Cell-dependent, and
                              the plan's non-additive reference.
    nearest_context_cells     diagnostic: the neighbour context's actual treated cells for drug
                              d, shifted by the difference of the two vehicle means. Non-additive.

OUTPUTS (--out)
---------------
    per_query.csv.gz        one row per (context, query drug, seed, predictor, scorer)
    summary.csv             per (predictor, scorer), with a context-clustered bootstrap
    delta_vs_reference.csv  paired differences against the mean route, within each predictor
    predictor_fit.csv       per (context, predictor) fit diagnostics
    provenance.json

Run:
    python analysis/phase2_transition/phase_b_loco.py \
        --h5ad <plate3 .h5ad> \
        --freeze-dir results/phase2_transition/eligibility \
        --out results/phase2_transition/phase_b
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.sparse as sp

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_eligibility import read_obs, sha256                       # noqa: E402
import phase2_common as pc                                           # noqa: E402

# ---- frozen constants of this phase ----
# The two latent models are truncated for different reasons, so they are truncated differently.
# linear_latent has no covariance to estimate, so the only reason to truncate it at all is that
# it is a latent model; its dimension is set by a variance target, computed on training cells and
# therefore not an outcome-driven choice. ot_map must estimate a latent covariance per drug from
# roughly 8,600 pooled training cells, which is what bounds its dimension at 50.
LATENT_VAR_TARGET = 0.80     # linear_latent keeps the fewest components reaching this share
LATENT_DIM_MAX = 512         # cap on that count
LATENT_DIM_OT = 50           # ot_map: bounded by covariance estimability, not by variance
N_PCA_CELLS = 50_000         # cells sampled from the training contexts to fit each PCA
N_FIT_CELLS = 200            # cells per (context, drug) used to fit the OT map and to transfer
MIN_STATE_CELLS = 20         # a (line, drug, state) mean below this is not estimated at all
OT_SHRINKAGE = 1e-3          # ridge on the latent covariances, as a fraction of their trace
PREDICTORS = ("average_effect", "nearest_context", "linear_latent", "ot_map",
              "nearest_context_cells", "state_conditioned_average_effect")
STATES = ("G1", "S", "G2M")   # the cell-cycle calls that ship with the plate


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def _sqrtm_psd(M, torch, eps: float = 1e-10):
    """Symmetric PSD square root by eigendecomposition."""
    w, V = torch.linalg.eigh((M + M.transpose(-1, -2)) / 2)
    w = w.clamp_min(eps)
    return (V * w.sqrt()) @ V.transpose(-1, -2)


def _bures_map(S0, S1, torch):
    """Linear part of the Gaussian optimal-transport map from N(., S0) to N(., S1).

        A = S0^{-1/2} ( S0^{1/2} S1 S0^{1/2} )^{1/2} S0^{-1/2}

    This is the unique optimal map between two Gaussians; it reduces to the identity when the two
    covariances agree, so a drug with no effect on the covariance yields a purely additive map and
    the predictor degrades gracefully to the additive family rather than to noise.
    """
    r = _sqrtm_psd(S0, torch)
    ri = torch.linalg.inv(r)
    return ri @ _sqrtm_psd(r @ S1 @ r, torch) @ ri


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--h5ad", required=True)
    ap.add_argument("--freeze-dir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--predictors", default=",".join(PREDICTORS))
    ap.add_argument("--limit-contexts", type=int, default=0,
                    help="debug only: first N contexts. Never use for a reported result.")
    ap.add_argument("--no-hash", action="store_true")
    a = ap.parse_args()

    import torch

    h5ad = Path(a.h5ad).resolve()
    freeze_dir, out = Path(a.freeze_dir), Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    dev = torch.device(a.device if (torch.cuda.is_available() or a.device == "cpu") else "cpu")
    predictors = [p for p in a.predictors.split(",") if p]
    unknown = set(predictors) - set(PREDICTORS)
    if unknown:
        raise ValueError(f"unknown predictors {sorted(unknown)}")
    t0 = time.time()

    freeze = json.loads((freeze_dir / "task_freeze.json").read_text())
    if freeze["input_sha256"] and not a.no_hash:
        got = sha256(h5ad)
        if got != freeze["input_sha256"]:
            raise ValueError(f"input does not match the freeze: {got} != {freeze['input_sha256']}")
    elig = pd.read_csv(freeze_dir / "query_eligibility.csv")
    ctx_tab = pd.read_csv(freeze_dir / "context_summary.csv")
    candidates = pd.read_csv(freeze_dir / "candidate_library.csv")["drug"].tolist()
    contexts = ctx_tab.loc[ctx_tab.context_usable, "cell_name"].tolist()
    run_contexts = contexts[:a.limit_contexts] if a.limit_contexts else contexts
    queries_by_ctx = {c: g.loc[g.eligible, "drug"].tolist() for c, g in elig.groupby("cell_name")}
    gt_index = {d: i for i, d in enumerate(candidates)}
    log(f"{len(run_contexts)} held-out contexts of {len(contexts)} usable, "
        f"{len(candidates)} candidates, predictors={predictors}, device={dev}")

    import anndata as ad
    log(f"reading {h5ad}")
    adata = ad.read_h5ad(h5ad)
    X = adata.X
    if not sp.isspmatrix_csr(X):
        X = sp.csr_matrix(X)
    X = X.astype(np.float32)
    obs = read_obs(h5ad, ["cell_name", "drug", "sublibrary", "phase"])
    del adata
    n_genes = X.shape[1]
    log(f"X {X.shape} nnz={X.nnz:,}")

    sublibs = np.sort(pd.unique(obs.sublibrary))
    sub_code = pd.Categorical(obs.sublibrary, categories=sublibs).codes
    cell_name, drug = obs.cell_name.to_numpy(), obs.drug.to_numpy()
    phase = obs.phase.to_numpy()

    # ---- condition means over the usable contexts, computed once ----
    log("computing (cell line, drug) means")
    keep = np.isin(cell_name, contexts)
    kidx = np.flatnonzero(keep)
    cats, means, counts = pc.group_means(X[kidx], pd.Series(cell_name[kidx]) + "||"
                                         + pd.Series(drug[kidx]))
    mpos = {k: i for i, k in enumerate(cats)}
    mu_cond = means.astype(np.float32)

    def cond_mean(c, d):
        return mu_cond[mpos[f"{c}||{d}"]]

    ctrl_mean = {c: cond_mean(c, pc.CONTROL_DRUG) for c in contexts}

    # (cell line, drug, state) means, for the state-conditioned predictor. Groups below
    # MIN_STATE_CELLS are dropped rather than estimated from a handful of cells; the predictor
    # falls back to the pooled signature there and the count is reported.
    mu_state, spos = None, {}
    if "state_conditioned_average_effect" in predictors:
        log("computing (cell line, drug, state) means")
        keep_s = keep & np.isin(phase, STATES)
        ks = np.flatnonzero(keep_s)
        cats_s, means_s, counts_s = pc.group_means(
            X[ks], pd.Series(cell_name[ks]) + "||" + pd.Series(drug[ks]) + "||"
            + pd.Series(phase[ks]))
        good = counts_s >= MIN_STATE_CELLS
        mu_state = means_s.astype(np.float32)
        spos = {k: i for i, k in enumerate(cats_s) if good[i]}
        log(f"{len(spos)} of {len(cats_s)} (line, drug, state) groups clear "
            f"{MIN_STATE_CELLS} cells")

    # ---- a fixed cell subsample per condition, used for every fit and every transfer ----
    log(f"sampling up to {N_FIT_CELLS} cells per condition for the fits")
    fit_rows: dict[tuple, np.ndarray] = {}
    r_fit = pc.rng_for(pc.RNG_FIT, 0, 0)
    for c in contexts:
        in_ctx = cell_name == c
        for d in [pc.CONTROL_DRUG] + candidates:
            r = np.flatnonzero(in_ctx & (drug == d))
            fit_rows[(c, d)] = (r if len(r) <= N_FIT_CELLS
                                else r_fit.choice(r, N_FIT_CELLS, replace=False))
    fit_index = np.concatenate([fit_rows[k] for k in fit_rows])
    fit_lookup = {}
    off = 0
    for k in fit_rows:
        fit_lookup[k] = (off, off + len(fit_rows[k]))
        off += len(fit_rows[k])
    log(f"gathering {len(fit_index):,} fit cells")
    FIT = np.asarray(X[fit_index].todense(), dtype=np.float32)
    log(f"fit matrix {FIT.shape} ({FIT.nbytes / 1e9:.1f} GB)")

    def fit_cells(c, d):
        s, e = fit_lookup[(c, d)]
        return FIT[s:e]

    rows: list[dict] = []
    fit_diag: list[dict] = []
    g1_pred: list[dict] = []      # Gate 1 on the PREDICTED populations (plan section 12)

    def _cos(a, b):
        na, nb = float(np.linalg.norm(a)), float(np.linalg.norm(b))
        return float("nan") if na < 1e-12 or nb < 1e-12 else float(a @ b / (na * nb))

    for ci, c in enumerate(run_contexts):
        train = [t for t in contexts if t != c]
        in_ctx = cell_name == c
        ctrl_rows = np.flatnonzero(in_ctx & (drug == pc.CONTROL_DRUG))
        qrows = {d: np.flatnonzero(in_ctx & (drug == d)) for d in queries_by_ctx[c]}
        tfit = time.time()

        # -- additive signatures, from training-context condition means only --
        deltas_per_ctx = np.stack([np.stack([cond_mean(t, d) - ctrl_mean[t] for t in train])
                                   for d in candidates])            # n_drug x n_train x genes
        sig_avg = deltas_per_ctx.mean(1)                            # n_drug x genes

        # -- per-state signatures, from training-context (line, drug, state) means only --
        sig_state, state_fallbacks = None, 0
        if "state_conditioned_average_effect" in predictors:
            sig_state = {}
            for st in STATES:
                acc = []
                for di, d in enumerate(candidates):
                    per_ctx = []
                    for t in train:
                        kt, kc = f"{t}||{d}||{st}", f"{t}||{pc.CONTROL_DRUG}||{st}"
                        if kt in spos and kc in spos:
                            per_ctx.append(mu_state[spos[kt]] - mu_state[spos[kc]])
                    # A drug with no usable state-specific training estimate keeps its pooled
                    # signature for that state, which makes it locally additive there. Counted.
                    acc.append(np.mean(per_ctx, axis=0) if per_ctx else sig_avg[di])
                    if not per_ctx:
                        state_fallbacks += 1
                sig_state[st] = np.stack(acc).astype(np.float32)

        cm = np.stack([ctrl_mean[t] for t in train])
        qc = ctrl_mean[c]
        cos = (cm @ qc) / (np.linalg.norm(cm, axis=1) * np.linalg.norm(qc) + 1e-12)
        nn_i = int(np.argmax(cos))
        nn_ctx = train[nn_i]
        sig_nn = deltas_per_ctx[:, nn_i, :]

        # -- training PCA, refitted for this held-out context --
        need_latent = {"linear_latent", "ot_map"} & set(predictors)
        if need_latent:
            r_pca = pc.rng_for(pc.RNG_FIT, 1, ci)
            pool = np.concatenate([np.arange(*fit_lookup[(t, d)])
                                   for t in train for d in [pc.CONTROL_DRUG] + candidates])
            take = pool if len(pool) <= N_PCA_CELLS else r_pca.choice(pool, N_PCA_CELLS,
                                                                      replace=False)
            Z = torch.as_tensor(FIT[take], device=dev)
            Zc = Z - Z.mean(0)
            cov = (Zc.T @ Zc).double() / (len(Zc) - 1)
            w, V = torch.linalg.eigh(cov)
            w = w.flip(0)
            V = V.flip(1)                                            # descending eigenvalues
            frac = torch.cumsum(w, 0) / w.sum()
            k_lin = int(min(int((frac < LATENT_VAR_TARGET).sum().item()) + 1, LATENT_DIM_MAX))
            P_lin = V[:, :k_lin].float()
            P = V[:, :LATENT_DIM_OT].float()                         # genes x LATENT_DIM_OT
            evr_lin = float(frac[k_lin - 1].item())
            evr_ot = float(frac[LATENT_DIM_OT - 1].item())
            del Z, Zc, cov, V

            sig_lat = ((torch.as_tensor(sig_avg, device=dev) @ P_lin) @ P_lin.T).cpu().numpy()
        else:
            P, P_lin, k_lin, evr_lin, evr_ot, sig_lat = None, None, 0, float("nan"), float("nan"), None

        # -- Gaussian OT maps in the training latent space --
        if "ot_map" in predictors:
            # Every cloud is centred on its OWN condition mean before pooling, so a covariance
            # here is within-condition cell scatter. The effect itself is carried separately, as
            # the average latent shift, and never enters a covariance.
            ctrl_c, drug_c = [], {d: [] for d in candidates}
            drug_eff = {d: [] for d in candidates}
            for t in train:
                base = torch.as_tensor(fit_cells(t, pc.CONTROL_DRUG), device=dev) @ P
                bm = base.mean(0)
                ctrl_c.append(base - bm)
                for d in candidates:
                    td = torch.as_tensor(fit_cells(t, d), device=dev) @ P
                    tm = td.mean(0)
                    drug_c[d].append(td - tm)
                    drug_eff[d].append(tm - bm)
            eye = torch.eye(LATENT_DIM_OT, device=dev, dtype=torch.float64)

            def _cov(M):
                Md = M.double()
                S = (Md.T @ Md) / (len(Md) - 1)
                return S + eye * (OT_SHRINKAGE * torch.diagonal(S).mean())

            S0 = _cov(torch.cat(ctrl_c))
            ot_A, ot_b = [], []
            for d in candidates:
                ot_A.append(_bures_map(S0, _cov(torch.cat(drug_c[d])), torch).float())
                ot_b.append(torch.stack(drug_eff[d]).mean(0))
            ot_A = torch.stack(ot_A)                                 # n_drug x L x L
            ot_b = torch.stack(ot_b)
            ot_dev = float((ot_A - eye.float()).norm(dim=(1, 2)).mean())
            del ctrl_c, drug_c, drug_eff
        else:
            ot_A = ot_b = None
            ot_dev = float("nan")

        fit_diag.append({"cell_line": c, "n_train_contexts": len(train),
                         "state_signature_fallbacks": state_fallbacks,
                         "nearest_context": nn_ctx, "nearest_context_cosine": float(cos[nn_i]),
                         "linear_latent_dim": k_lin,
                         "linear_latent_explained_variance": evr_lin,
                         "ot_latent_explained_variance": evr_ot,
                         "ot_mean_deviation_from_identity": ot_dev,
                         "fit_seconds": round(time.time() - tfit, 1)})

        # -- rank, per seed --
        for seed in pc.SEEDS:
            h1 = pc.sublibrary_halves(len(sublibs), seed, ci)
            r_src = pc.rng_for(pc.RNG_SOURCE, seed, ci)
            src = r_src.choice(ctrl_rows, min(pc.N_SOURCE, len(ctrl_rows)), replace=False)
            S = np.asarray(X[src].todense(), dtype=np.float32)
            mu = S.mean(0)
            S_dev = torch.as_tensor(S - mu, device=dev)              # source cells, centred
            # Gate 1 needs the predicted response of each pre-defined cellular state. The states
            # are the cell-cycle calls that ship with the plate, taken on the SOURCE cells, which
            # are a task input. A state's predicted response is the mean predicted cell of that
            # state minus the mean source cell of that state, so an additive predictor gives the
            # same vector for both states and a differential response of exactly zero. That is
            # not asserted here, it is computed and written out.
            sph = phase[src]
            st_mask = {p: sph == p for p in ("G1", "G2M")}
            st_ok = all(m.sum() >= 20 for m in st_mask.values())
            src_state_mean = {p: S[st_mask[p]].mean(0) for p in st_mask} if st_ok else None

            caches = {}
            for name in predictors:
                if name == "state_conditioned_average_effect":
                    # Each source cell is shifted by its OWN state's signature, so two states
                    # receive different vectors and the predicted differential response is not
                    # zero by construction. Cells in a state with no signature (S is present in
                    # the data but the states used downstream are G1 and G2M) take the pooled one.
                    sg = torch.as_tensor(sig_avg, device=dev)
                    per_state = {st: torch.as_tensor(sig_state[st], device=dev) for st in STATES}
                    idx = {st: torch.as_tensor(np.flatnonzero(sph == st), device=dev)
                           for st in STATES}
                    other = torch.as_tensor(np.flatnonzero(~np.isin(sph, STATES)), device=dev)
                    blocks = []
                    for k in range(len(candidates)):
                        Bk = S_dev.clone()
                        for st in STATES:
                            if len(idx[st]):
                                Bk[idx[st]] += per_state[st][k][None]
                        if len(other):
                            Bk[other] += sg[k][None]
                        blocks.append(Bk)
                    B = torch.cat(blocks)
                    sizes = [len(S)] * len(candidates)
                    sig = None
                elif name == "average_effect":
                    sig = sig_avg
                elif name == "nearest_context":
                    sig = sig_nn
                elif name == "linear_latent":
                    sig = sig_lat
                else:
                    sig = None
                if sig is not None:
                    # x_hat = x_source + delta_d, then referred to mu_source: the source scatter
                    # translated by the signature.
                    sg = torch.as_tensor(sig, device=dev)
                    B = torch.cat([S_dev + sg[k][None] for k in range(len(candidates))])
                    sizes = [len(S)] * len(candidates)
                elif name == "ot_map":
                    # A latent EDIT rather than a latent reconstruction: the part of each source
                    # cell outside the 50-dimensional subspace is carried through untouched, so
                    # the predicted population keeps the dimensionality of a real one.
                    Zq = S_dev @ P                                    # latent, already centred
                    B = torch.cat([S_dev + (Zq @ (ot_A[k] - torch.eye(LATENT_DIM_OT, device=dev)).T
                                            + ot_b[k][None]) @ P.T
                                   for k in range(len(candidates))])
                    sizes = [len(S)] * len(candidates)
                elif name == "nearest_context_cells":
                    shift = qc - ctrl_mean[nn_ctx]
                    B = torch.as_tensor(
                        np.concatenate([fit_cells(nn_ctx, d) + shift - mu for d in candidates]),
                        device=dev)
                    sizes = [len(fit_cells(nn_ctx, d)) for d in candidates]
                caches[name] = pc.make_cache(B, sizes, ci, seed, torch, dev)

                if st_ok:
                    Bc = B.cpu().numpy() + mu          # predicted cells, back in expression space
                    offs = np.concatenate([[0], np.cumsum(sizes)])
                    if name == "nearest_context_cells":
                        cell_state = np.concatenate(
                            [phase[fit_rows[(nn_ctx, d)]] for d in candidates])
                        ref = {p: src_state_mean[p] for p in st_mask}
                    else:
                        cell_state = np.tile(sph, len(candidates))
                        ref = src_state_mean
                    for k, d in enumerate(candidates):
                        seg = slice(offs[k], offs[k + 1])
                        cs = cell_state[seg]
                        r = {}
                        for pstate in ("G1", "G2M"):
                            msk = cs == pstate
                            r[pstate] = (Bc[seg][msk].mean(0) - ref[pstate]
                                         if msk.sum() >= 20 else None)
                        both = r["G1"] is not None and r["G2M"] is not None
                        # The predicted analogue of the observed cross-fitted interaction
                        # strength: ||r_1 - r_2||^2 / p. A prediction carries no sampling noise,
                        # so it needs no cross-fitting, and this is on the same scale as the
                        # observed S_int. The cosine below is kept only for continuity with the
                        # retired statistic; comparing a predicted cosine against an observed
                        # magnitude is the confound that statistic was retired for.
                        g1_pred.append({
                            "cell_line": c, "seed": seed, "predictor": name, "drug": d,
                            "predicted_S_int": (float(((r["G1"] - r["G2M"]) ** 2).mean())
                                                if both else np.nan),
                            "predicted_main_norm2": (float((((r["G1"] + r["G2M"]) / 2) ** 2).mean())
                                                     if both else np.nan),
                            "predicted_induced_cosine": (_cos(r["G1"], r["G2M"])
                                                         if both else np.nan),
                            "n_pred_G1": int((cs == "G1").sum()),
                            "n_pred_G2M": int((cs == "G2M").sum()),
                        })

            for q in queries_by_ctx[c]:
                r = qrows[q]
                r1 = r[h1[sub_code[r]]]
                take = min(pc.N_TARGET, len(r1))
                if take < 2:
                    continue
                r_t = pc.rng_for(pc.RNG_TARGET, seed, ci, gt_index[q])
                tidx = r_t.choice(r1, take, replace=False)
                T = torch.as_tensor(np.asarray(X[tidx].todense(), dtype=np.float32) - mu,
                                    device=dev)
                gi = gt_index[q]
                for name in predictors:
                    for scorer, s in pc.score_all(T, caches[name], torch).items():
                        rk, tied = pc.rank_of(s, gi)
                        # Top-1 identity is needed for Flip@1 in plan section 12. argmax resolves
                        # a tie to the first candidate in library order; ties at the top are
                        # counted separately in n_ties so such a case is visible rather than
                        # silently decided.
                        rows.append({
                            "cell_line": c, "drug": q, "seed": seed,
                            "predictor": name, "scorer": scorer,
                            "rank": rk, "reciprocal_rank": 1.0 / rk,
                            "hit@1": float(rk <= 1), "hit@5": float(rk <= 5),
                            "hit@10": float(rk <= 10), "n_ties": tied,
                            "top1_drug": candidates[int(np.argmax(s))],
                            "n_target_cells": take, "n_source_cells": len(src),
                            "n_candidates": len(candidates),
                        })
            del caches
        log(f"context {ci + 1}/{len(run_contexts)} {c} done ({time.time() - t0:.0f}s)")

    per_query = pd.DataFrame(rows)
    per_query.to_csv(out / "per_query.csv.gz", index=False)   # 58 MB raw, 3.5 MB gzipped
    pc.summarize(per_query, ["predictor", "scorer"]).to_csv(out / "summary.csv", index=False)
    deltas = pd.concat([pc.paired_deltas(g, []).assign(predictor=p)
                        for p, g in per_query.groupby("predictor")], ignore_index=True)
    deltas.to_csv(out / "delta_vs_reference.csv", index=False)
    pd.DataFrame(fit_diag).to_csv(out / "predictor_fit.csv", index=False)
    pd.DataFrame(g1_pred).to_csv(out / "gate1_predicted.csv.gz", index=False)

    prov = {
        "input_h5ad": str(h5ad), "input_sha256": freeze["input_sha256"],
        "freeze_dir": str(freeze_dir), "device": str(dev),
        "n_held_out_contexts": len(run_contexts), "n_usable_contexts": len(contexts),
        "n_candidates": len(candidates), "predictors": predictors,
        "constants": {"N_SOURCE": pc.N_SOURCE, "N_TARGET": pc.N_TARGET,
                      "LATENT_VAR_TARGET": LATENT_VAR_TARGET, "LATENT_DIM_MAX": LATENT_DIM_MAX,
                      "LATENT_DIM_OT": LATENT_DIM_OT, "N_PCA_CELLS": N_PCA_CELLS,
                      "N_FIT_CELLS": N_FIT_CELLS, "OT_SHRINKAGE": OT_SHRINKAGE,
                      "SW_N_PROJ": pc.SW_N_PROJ, "N_BOOTSTRAP": pc.N_BOOTSTRAP},
        "seeds": list(pc.SEEDS),
        "leakage_rule": "no treated cell of the held-out context enters any fit or any ranker",
        "runtime_seconds": round(time.time() - t0, 1),
    }
    (out / "provenance.json").write_text(json.dumps(prov, indent=2) + "\n")
    log(f"wrote {out}  ({time.time() - t0:.0f}s)")


if __name__ == "__main__":
    sys.exit(main())
