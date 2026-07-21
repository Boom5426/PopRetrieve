#!/usr/bin/env python
"""Experiment 4 — CD34+ honest negative control (plan §8-Exp4, reproduces FINDINGS §7).

Distribution-aware retrieval is NOT a universal booster. On real primary CD34+ HSPCs
with natural progenitor lineages (nothing constructed):
  * self-retrieval of 36 real drugs -> mean-cosine WINS (a low-variance statistic on a
    real source), distributional scores pay a sampling-variance penalty;
  * matched-budget within-vs-between test -> natural lineages do NOT rank drugs
    differently beyond the noise floor (between-lineage agreement ~ within-lineage
    reliability). Predicted by the §8 gate: lineages respond ALIKE (cross_cos ~1),
    sitting BELOW the divergence gate.

    python src/experiments/exp04_cd34_negative.py --n-seeds 8 --K 4
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from experiments.common import FINDINGS, verdict, ordering_verdict   # noqa: E402
from data.load_cd34 import load_cd34                                  # noqa: E402
from retrieval.tasks import NaturalSubpops, _cos                     # noqa: E402
from retrieval.metrics import _energy_dist                           # noqa: E402
from utils.io import results_path, write_csv                         # noqa: E402
from utils.logging import log, section                               # noqa: E402

OUT = "exp04_cd34_negative"
SC = ["mean_cosine", "global_energy", "coverage_mean", "coverage_worst"]


def _edist(a, b, cap, seed):
    return _energy_dist(a, b, max_cells=cap, seed=seed, min_cells=3)


def self_retrieval(X, is_ctrl, pert, K=4, n_seeds=8, cap=160):
    Xc = X[is_ctrl]
    mu_c = Xc.mean(0)
    drugs = sorted(set(pert[~is_ctrl]))
    D = len(drugs)
    subpops = NaturalSubpops(Xc, K=K)
    log(f"[cd34] control={len(Xc)} drugs={D} K={K} "
        f"fractions={np.round(subpops.fractions, 3)} minority={subpops.fractions.min():.3f}")
    pool = {d: X[pert == d] for d in drugs}
    passign = {d: subpops.assign(pool[d]) for d in drugs}

    def split_idx(n, seed):
        r = np.random.default_rng(seed)
        idx = r.permutation(n)
        h = n // 2
        return idx[:h], idx[h:]

    rows = []
    for seed in range(n_seeds):
        A, B, Aa, Ba = {}, {}, {}, {}
        for d in drugs:
            ia, ib = split_idx(len(pool[d]), 7000 + seed)
            A[d], B[d] = pool[d][ia], pool[d][ib]
            Aa[d], Ba[d] = passign[d][ia], passign[d][ib]
        cand_sig = {d: B[d].mean(0) - mu_c for d in drugs}
        for qi, dq in enumerate(drugs):
            target, tat = A[dq], Aa[dq]
            tgt_sig = target.mean(0) - mu_c
            sc = {s: np.zeros(D) for s in SC}
            for ci, dc in enumerate(drugs):
                es_seed = 1000 + seed
                sc["mean_cosine"][ci] = _cos(tgt_sig, cand_sig[dc])
                sc["global_energy"][ci] = -_edist(B[dc], target, cap, es_seed)
                es = []
                for k in range(K):
                    tk = target[tat == k]
                    pk = B[dc][Ba[dc] == k]
                    if len(tk) >= 3 and len(pk) >= 3:
                        es.append(_edist(pk, tk, cap, es_seed))
                sc["coverage_mean"][ci] = -np.mean(es) if es else -1e6
                sc["coverage_worst"][ci] = -np.max(es) if es else -1e6
            for s in SC:
                order = np.argsort(-sc[s])
                rank = int(np.where(order == qi)[0][0]) + 1
                rows.append({"seed": seed, "query": dq, "scorer": s,
                             "hit@1": float(rank == 1), "hit@3": float(rank <= 3),
                             "mrr": 1.0 / rank, "rank": rank})
        log(f"  seed {seed} done")
    return pd.DataFrame(rows), drugs, subpops, pool, passign, mu_c


def lineage_response_cosine(drugs, pool, passign, subpops, Xc):
    """Per-drug median pairwise lineage response-direction cosine. At ~60-270
    cells/subpop/drug this is NOISE-dominated (each per-lineage signature is mostly
    sampling noise, so two lineages look ~orthogonal -> low cos). It is therefore a
    NOISE-FLOOR estimate, NOT evidence of genuine divergence; the honest 'respond
    alike' evidence is the drug-RANKING agreement (lineage_mean_agreement) plus the
    matched within-vs-between control."""
    K = subpops.K
    ctrl_mu = {k: Xc[subpops.control_labels == k].mean(0) for k in range(K)}
    rows = []
    for d in drugs:
        P, a = pool[d], passign[d]
        sigs = {}
        for k in range(K):
            pk = P[a == k]
            if len(pk) >= 5:
                sigs[k] = pk.mean(0) - ctrl_mu[k]
        ks = sorted(sigs)
        coss = [_cos(sigs[i], sigs[j]) for ii, i in enumerate(ks) for j in ks[ii + 1:]]
        if coss:
            rows.append({"drug": d, "n_pairs": len(coss),
                         "median_lineage_cos": float(np.median(coss))})
    return pd.DataFrame(rows)


def lineage_mean_agreement(drugs, pool, passign, subpops, Xc, min_cells=20):
    """Per-lineage Spearman agreement of the drug-RANKING structure with the whole-mean
    ranking (ports the cd34_robust 'agree-with-mean' number). Majorities ~0.68-0.73
    (they effectively rank drugs like the mean => respond ALIKE for the ranking task);
    the tiny minority is lower AND unreliable. This is the honest 'CD34 sits below the
    gate' evidence (FINDINGS §7/§8: lineage/mean agreement 0.68-0.73)."""
    def unit(M):
        return M / (np.linalg.norm(M, axis=1, keepdims=True) + 1e-9)

    def od(M):
        return M[np.triu_indices(M.shape[0], 1)]

    K = subpops.K
    mu_c = Xc.mean(0)
    ctrl_mu = {k: Xc[subpops.control_labels == k].mean(0) for k in range(K)}
    D, G = len(drugs), pool[drugs[0]].shape[1]
    Sall = unit(np.stack([pool[d].mean(0) - mu_c for d in drugs]))
    Mall = Sall @ Sall.T
    rows = []
    for k in range(K):
        S = np.full((D, G), np.nan)
        ok = np.zeros(D, bool)
        for di, d in enumerate(drugs):
            idx = np.where(passign[d] == k)[0]
            if len(idx) >= min_cells:
                S[di] = pool[d][idx].mean(0) - ctrl_mu[k]
                ok[di] = True
        if ok.sum() < 4:
            continue
        Uk, Ua = unit(np.nan_to_num(S))[ok], Sall[ok]
        agree = spearmanr(od(Uk @ Uk.T), od(Ua @ Ua.T)).correlation
        rows.append({"lineage": f"c{k}", "frac": float(subpops.fractions[k]),
                     "n_drugs": int(ok.sum()), "agree_with_mean": float(agree),
                     "is_minority": bool(k == int(np.argmin(subpops.fractions)))})
    return pd.DataFrame(rows)


def within_between(X, is_ctrl, pert, n=80, seeds=12, thr=0.2):
    def unit(M):
        return M / (np.linalg.norm(M, axis=1, keepdims=True) + 1e-9)

    def od(M):
        return M[np.triu_indices(M.shape[0], 1)]

    Xc = X[is_ctrl]
    mu_c = Xc.mean(0)
    drugs = sorted(set(pert[~is_ctrl]))
    rows = []
    for K in (2, 3):
        subpops = NaturalSubpops(Xc, K=K)
        asg = {d: subpops.assign(X[pert == d]) for d in drugs}
        ctrl_mu = {k: Xc[subpops.control_labels == k].mean(0) for k in range(K)}
        frac = subpops.fractions
        big = [k for k in range(K) if frac[k] > thr]
        usable = [d for d in drugs if all((asg[d] == k).sum() >= 2 * n for k in big)]
        if len(usable) < 8:
            log(f"  [within/between] K={K}: too few usable drugs ({len(usable)}); skip")
            continue
        within = {k: [] for k in big}
        between = {}
        for s in range(seeds):
            r = np.random.default_rng(300 + s)
            samp = {}
            for k in big:
                Amat = np.zeros((len(usable), X.shape[1]))
                Bmat = np.zeros((len(usable), X.shape[1]))
                for di, d in enumerate(usable):
                    idx = np.where(asg[d] == k)[0]
                    r.shuffle(idx)
                    Amat[di] = X[pert == d][idx[:n]].mean(0) - ctrl_mu[k]
                    Bmat[di] = X[pert == d][idx[n:2 * n]].mean(0) - ctrl_mu[k]
                samp[(k, 0)], samp[(k, 1)] = unit(Amat), unit(Bmat)
            for k in big:
                within[k].append(spearmanr(od(samp[(k, 0)] @ samp[(k, 0)].T),
                                           od(samp[(k, 1)] @ samp[(k, 1)].T)).correlation)
            for i, k in enumerate(big):
                for l in big[i + 1:]:
                    between.setdefault((k, l), []).append(
                        spearmanr(od(samp[(k, 0)] @ samp[(k, 0)].T),
                                  od(samp[(l, 0)] @ samp[(l, 0)].T)).correlation)
        for k in big:
            rows.append({"K": K, "type": "within", "subpops": f"c{k}",
                         "agreement": float(np.mean(within[k])), "std": float(np.std(within[k]))})
        for (k, l), v in between.items():
            wk, wl = np.mean(within[k]), np.mean(within[l])
            verdict_str = "DISAGREE(real)" if np.mean(v) < min(wk, wl) - 2 * np.std(v) else "agree~noise"
            rows.append({"K": K, "type": "between", "subpops": f"c{k}-c{l}",
                         "agreement": float(np.mean(v)), "std": float(np.std(v)),
                         "verdict": verdict_str})
            log(f"  [within/between] K={K} c{k}vc{l}: between={np.mean(v):.2f} "
                f"(within {wk:.2f}/{wl:.2f}) -> {verdict_str}")
    return pd.DataFrame(rows)


def run(n_seeds=8, K=4, cap=160, processed=None):
    data = load_cd34(processed)
    log(data.summary())
    X, is_ctrl, pert = data.X, data.is_control, data.pert

    section("EXP04a self-retrieval (36 real drugs)")
    retr, drugs, subpops, pool, passign, mu_c = self_retrieval(X, is_ctrl, pert, K=K,
                                                               n_seeds=n_seeds, cap=cap)
    write_csv(retr, results_path(OUT, "cd34_retrieval.csv"))
    agg = {s: float(retr[retr.scorer == s]["hit@1"].mean()) for s in SC}
    log("  Hit@1: " + "  ".join(f"{s}={agg[s]:.3f}" for s in SC) +
        f"   (random={1/len(drugs):.3f})")

    section("EXP04b lineage drug-ranking agreement + raw response-cos noise floor")
    linc = lineage_response_cosine(drugs, pool, passign, subpops, X[is_ctrl])
    write_csv(linc, results_path(OUT, "cd34_lineage_response_cosine.csv"))
    med_lin = float(linc["median_lineage_cos"].median())
    agree = lineage_mean_agreement(drugs, pool, passign, subpops, X[is_ctrl])
    write_csv(agree, results_path(OUT, "cd34_lineage_mean_agreement.csv"))
    maj_agree = float(agree[~agree["is_minority"]]["agree_with_mean"].median())
    log(f"  raw per-drug cross-lineage response cos = {med_lin:.2f} (NOISE FLOOR at "
        f"this depth — not divergence)")
    log(f"  majority lineage vs whole-mean drug-ranking agreement = {maj_agree:.2f} "
        f"(FINDINGS ~0.68-0.73 => lineages rank drugs ALIKE => below gate)")

    section("EXP04c matched-budget within-vs-between noise control")
    wb = within_between(X, is_ctrl, pert)
    write_csv(wb, results_path(OUT, "cd34_noise_controls.csv"))

    no_disagree = (len(wb) == 0) or bool(
        (~wb["verdict"].fillna("").str.startswith("DISAGREE")).all())
    write_csv(pd.DataFrame([{
        "dataset": "CD34+", "majority_lineage_mean_agreement": maj_agree,
        "raw_response_cos_noise_floor": med_lin, "gate": 0.9,
        "robust_lineage_divergence": (not no_disagree),
        "regime": "below gate (no distributional advantage): lineages rank drugs like "
                  "the mean; matched within~=between at the noise floor"}]),
        results_path(OUT, "cd34_gate_position.csv"))

    section("EXP04 VERDICTS vs FINDINGS §7")
    checks = [verdict(f"cd34/{s}", agg[s], FINDINGS["exp04_cd34"][s]) for s in SC]
    checks.append(ordering_verdict(
        "mean_cosine WINS self-retrieval (mean > energy) on real primary source",
        agg["mean_cosine"] > agg["global_energy"],
        f"mean={agg['mean_cosine']:.2f} > energy={agg['global_energy']:.2f}"))
    if len(wb):
        no_disagree = bool((~wb["verdict"].fillna("").str.startswith("DISAGREE")).all())
        checks.append(ordering_verdict(
            "no robust lineage disagreement (between ~ within noise floor)",
            no_disagree, "all pairs agree at noise floor" if no_disagree else "some DISAGREE"))
    checks.append(ordering_verdict(
        "majority lineages rank drugs ~like the mean (agreement > 0.5 => below gate)",
        maj_agree > 0.5, f"majority lineage/mean agreement = {maj_agree:.2f}"))
    return {"headline": agg, "checks": checks}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-seeds", type=int, default=8)
    ap.add_argument("--K", type=int, default=4)
    ap.add_argument("--cap", type=int, default=160)
    ap.add_argument("--processed", default=None)
    args = ap.parse_args()
    run(n_seeds=args.n_seeds, K=args.K, cap=args.cap, processed=args.processed)


if __name__ == "__main__":
    main()
