#!/usr/bin/env python
"""Experiment 5 — Frangieh natural evidence (plan §8-Exp5, reproduces FINDINGS §11).

Melanoma Perturb-CITE-seq with THREE natural immune microenvironments (Control / IFNγ
/ Co-culture) as the subpopulation axis and 248 CRISPR KOs as the library. Natural
context-divergence is real but concentrated in immune genes; the clean, honest
deliverable is per-KO and the within-gene IFNGR1 case:
  * per-KO gate: the distributional advantage scales with context-divergence (§8 gate
    holds on natural data);
  * IFNGR1 = within-gene controlled natural instance: the SAME KO triggers mean-out
    ONLY when its two mixed immune contexts diverge (Control+IFNγ: mean~0.2 vs
    energy~0.8), not when both contexts are immune-active (~0.95 / 0.95).

    python src/experiments/exp05_frangieh_natural.py --n-seeds 20
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from experiments.common import ordering_verdict            # noqa: E402
from data.load_frangieh import load_frangieh               # noqa: E402
from retrieval.tasks import ContextMixtureTask, context_divergence_probe  # noqa: E402
from retrieval.rankers import score_labeled, SCORERS        # noqa: E402
from retrieval.evaluation import hit_at_1                   # noqa: E402
from retrieval.bootstrap import bootstrap_stat              # noqa: E402
from utils.io import results_path, write_csv                # noqa: E402
from utils.logging import log, section                     # noqa: E402

OUT = "exp05_frangieh_natural"
IFN = "IFNγ"                                            # 'IFNγ' as stored in the data
CONTRASTS = [("Control", IFN), ("Control", "Co-culture"), (IFN, "Co-culture")]


def per_ko_gate(data, div, cond_maj, cond_min, n_seeds=20, alpha=0.7, n_total=200,
                n_distractors=40):
    task = ContextMixtureTask(data, cond_maj, cond_min, min_cells=60)
    div_i = div.set_index("ko")
    kos = [g for g in task.shared
           if g in div_i.index and bool(div_i.loc[g, "reliable"])
           and min(len(task.pool[cond_maj][g][0]),
                   len(task.pool[cond_min][g][0])) >= n_total // 2]
    log(f"[gate] {cond_maj}+{cond_min}: {len(kos)} reliable well-powered KOs")
    rows = []
    for g in kos:
        hit = {"mean_cosine": [], "global_energy": []}
        for s in range(n_seeds):
            q = task.build(g, alpha, n_total, n_distractors, 2000 + s)
            sc = score_labeled(q)
            names = list(q["cands"])
            gt = names.index("covers-both")
            for scorer in hit:
                hit[scorer].append(hit_at_1(np.array([sc[scorer][n] for n in names]), gt))
        rows.append({"ko": g, "cross_cos": float(div_i.loc[g, "cross_cos"]),
                     "eff_min": float(div_i.loc[g, "eff_b"]),
                     "mean_cosine": float(np.mean(hit["mean_cosine"])),
                     "global_energy": float(np.mean(hit["global_energy"])),
                     "advantage": float(np.mean(hit["global_energy"]) - np.mean(hit["mean_cosine"]))})
    return pd.DataFrame(rows).sort_values("cross_cos").reset_index(drop=True)


def ifngr1_within_gene(data, ko="IFNGR1", n_seeds=20, alpha=0.7, n_total=200,
                       n_distractors=40):
    rows = []
    for maj, minor in CONTRASTS:
        div = context_divergence_probe(data, maj, minor, min_cells=40, id_col="ko")
        cross_cos = float(div.set_index("ko").loc[ko, "cross_cos"]) if ko in set(div["ko"]) else np.nan
        task = ContextMixtureTask(data, maj, minor, min_cells=60)
        if ko not in task.shared:
            log(f"  [ifngr1] {maj}+{minor}: {ko} not well-powered in both; skip")
            continue
        hit = {"mean_cosine": [], "global_energy": []}
        for s in range(n_seeds):
            q = task.build(ko, alpha, n_total, n_distractors, 2000 + s)
            sc = score_labeled(q)
            names = list(q["cands"])
            gt = names.index("covers-both")
            for scorer in hit:
                hit[scorer].append(hit_at_1(np.array([sc[scorer][n] for n in names]), gt))
        mc = bootstrap_stat(hit["mean_cosine"])
        en = bootstrap_stat(hit["global_energy"])
        rows.append({"ko": ko, "contrast": f"{maj}+{minor}", "cross_cos": cross_cos,
                     "mean_cosine": mc[0], "mean_cosine_lo": mc[1], "mean_cosine_hi": mc[2],
                     "global_energy": en[0], "global_energy_lo": en[1], "global_energy_hi": en[2]})
        log(f"  [ifngr1] {maj}+{minor}: cross_cos={cross_cos:.2f} "
            f"mean={mc[0]:.2f}[{mc[1]:.2f},{mc[2]:.2f}] energy={en[0]:.2f}[{en[1]:.2f},{en[2]:.2f}]")
    return pd.DataFrame(rows)


def run(n_seeds=20, processed=None):
    data = load_frangieh(processed)
    log(data.summary())

    section("EXP05a context-divergence probes (3 immune contrasts)")
    divs = []
    for maj, minor in CONTRASTS:
        d = context_divergence_probe(data, maj, minor, min_cells=40, gate=0.9,
                                     rel_floor=0.5, seed=0, id_col="ko")
        d = d.copy()
        d["contrast"] = f"{maj}+{minor}"
        divs.append(d)
        rel = d[d["reliable"]]
        log(f"  {maj}+{minor}: reliable KOs={len(rel)} "
            f"median cross_cos={rel['cross_cos'].median():.2f}")
    div_all = pd.concat(divs, ignore_index=True)
    write_csv(div_all, results_path(OUT, "frangieh_divergence.csv"))

    section("EXP05b per-KO gate (Control vs IFNγ)")
    div_ctrl_ifn = divs[0]
    gate = per_ko_gate(data, div_ctrl_ifn, "Control", IFN, n_seeds=n_seeds)
    write_csv(gate, results_path(OUT, "frangieh_retrieval_by_gene.csv"))
    if len(gate) >= 3:
        rho, p = spearmanr(gate["cross_cos"], gate["advantage"])
        log(f"  Spearman(cross_cos, advantage) = {rho:+.2f} (p={p:.3f}) "
            f"[gate predicts NEGATIVE]")
        lo = gate[gate.cross_cos < 0.5]
        hi = gate[gate.cross_cos >= 0.5]
        if len(lo):
            log(f"  strongly divergent (cos<0.5, n={len(lo)}): "
                f"mean={lo.mean_cosine.mean():.2f} energy={lo.global_energy.mean():.2f} "
                f"adv={lo.advantage.mean():+.2f}")
        if len(hi):
            log(f"  moderate (cos>=0.5, n={len(hi)}): "
                f"mean={hi.mean_cosine.mean():.2f} energy={hi.global_energy.mean():.2f} "
                f"adv={hi.advantage.mean():+.2f}")

    section("EXP05c IFNGR1 within-gene controlled natural experiment (+ bootstrap CI)")
    ifn = ifngr1_within_gene(data, "IFNGR1", n_seeds=n_seeds)
    write_csv(ifn, results_path(OUT, "frangieh_ifngr1_case.csv"))
    write_csv(gate.assign(bootstrap="see frangieh_ifngr1_case.csv"),
              results_path(OUT, "frangieh_bootstrap_ci.csv"))

    section("EXP05 VERDICTS vs FINDINGS §11")
    checks = []
    if len(ifn):
        ifn_i = ifn.set_index("contrast")
        # divergent contrast: mean << energy ; both-immune-active: mean ~ energy (both high)
        div_key = f"Control+{IFN}"
        if div_key in ifn_i.index:
            r = ifn_i.loc[div_key]
            checks.append(ordering_verdict(
                f"IFNGR1 {div_key}: mean-out FAILS, energy rescues (energy > mean)",
                r["global_energy"] > r["mean_cosine"] + 0.2,
                f"mean={r['mean_cosine']:.2f} energy={r['global_energy']:.2f}"))
        both_key = f"{IFN}+Co-culture"
        if both_key in ifn_i.index:
            r = ifn_i.loc[both_key]
            checks.append(ordering_verdict(
                f"IFNGR1 {both_key} (both immune-active): no failure (mean ~ energy, both high)",
                (r["mean_cosine"] > 0.6) and (abs(r["global_energy"] - r["mean_cosine"]) < 0.25),
                f"mean={r['mean_cosine']:.2f} energy={r['global_energy']:.2f}"))
    if len(gate) >= 3:
        rho, _ = spearmanr(gate["cross_cos"], gate["advantage"])
        checks.append(ordering_verdict(
            "per-KO gate direction: advantage rises as cross_cos falls (Spearman<0)",
            rho < 0, f"Spearman={rho:+.2f}"))
    return {"checks": checks}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-seeds", type=int, default=20)
    ap.add_argument("--processed", default=None)
    args = ap.parse_args()
    run(n_seeds=args.n_seeds, processed=args.processed)


if __name__ == "__main__":
    main()
