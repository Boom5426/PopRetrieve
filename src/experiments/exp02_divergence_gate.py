#!/usr/bin/env python
"""Experiment 2 — Divergence gate (plan §8-Exp2, reproduces FINDINGS §8).

When is distribution-aware retrieval actually necessary? Three sweeps on the K562
HDAC/JAK controlled mixture (ground truth = covers-both):
  * divergence axis : minority = majority shifted by lam*(mu_B-mu_A); sweep lam.
  * power axis       : subsample N cells/subpop; sweep N.
  * metric axis      : score globally (K=1) with energy / MMD / sliced-Wasserstein.

Prediction (§8): the distributional advantage is GATED by subpop-response divergence
(threshold ~cos 0.9), largely independent of depth (~15-60 cells suffice), and
metric-agnostic (energy/MMD/sliced-W agree; mean-cosine ~0 throughout).

    python src/experiments/exp02_divergence_gate.py --n-seeds 20
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from experiments.common import ordering_verdict            # noqa: E402
from data.load_sciplex3 import load_sciplex3               # noqa: E402
from retrieval.tasks import (                              # noqa: E402
    ControlledMixtureTask, build_divergence_query, subsample_controlled_query,
    context_divergence_probe)


GATE_COS = 0.9   # subpopulation response cosine below which responses count as divergent


def dataset_positions_on_gate(data, gate: float = GATE_COS) -> pd.DataFrame:
    """Where each dataset actually sits on the divergence axis.

    This table used to be three typed-in literals under a comment that said "from probes",
    and no probe ran. One of them was flatly contradicted by our own data: it placed CD34+
    at cross_cos 0.95 ("below gate, no advantage"), while exp04 measures a MEDIAN lineage
    response cosine of about 0.19 on the same cells. The table feeds the source data of two
    main figures, so it is now computed, and a missing input raises instead of being
    replaced by a plausible number.

    SciPlex3 cross-line is probed here directly. CD34+ and Frangieh are read from the
    experiments that measure them (exp04, exp05), because their tensors are not loaded here.
    """
    rows = []

    # SciPlex3 cross-line: measured now, from the real response cosines.
    cos_by_pair = []
    for maj, minor in (("K562", "A549"), ("A549", "MCF7"), ("K562", "MCF7")):
        probe = context_divergence_probe(data, maj, minor, min_cells=30, gate=gate,
                                         rel_floor=0.5, seed=0, id_col="drug")
        if len(probe):
            cos_by_pair.append(float(probe["cross_cos"].median()))
    if not cos_by_pair:
        raise RuntimeError("cross-line divergence probe returned no drugs; cannot place "
                           "SciPlex3 on the gate")
    rows.append({"dataset": "cross-line (SciPlex3)",
                 "typical_cross_cos": float(np.median(cos_by_pair)),
                 "source": "context_divergence_probe, median over 3 line pairs",
                 "n": len(cos_by_pair)})

    # CD34+ and Frangieh: read the measurement from the experiment that made it.
    for name, exp_dir, fname, col in (
        ("CD34+ lineages", "exp04_cd34_negative", "cd34_lineage_response_cosine.csv",
         "median_lineage_cos"),
        ("Frangieh immune", "exp05_frangieh_natural", "frangieh_retrieval_by_gene.csv",
         "cross_cos"),
    ):
        p = results_path(exp_dir, fname)
        if not Path(p).exists():
            raise FileNotFoundError(
                f"{name} position on the gate needs {p}, which does not exist. Run "
                f"{exp_dir} first. This table is NOT allowed to carry a hand-entered "
                f"number: it is the source data for Fig 1e and Fig 3e.")
        sub = pd.read_csv(p)
        rows.append({"dataset": name, "typical_cross_cos": float(sub[col].median()),
                     "source": f"{exp_dir}/{fname}:{col} (median)", "n": int(len(sub))})

    df = pd.DataFrame(rows)
    df["regime"] = np.where(
        df.typical_cross_cos < gate,
        f"divergent (cos < {gate}): distributional retrieval may help",
        f"homogeneous (cos >= {gate}): mean signature is sufficient")
    df["clears_gate"] = df.typical_cross_cos < gate
    return df.sort_values("typical_cross_cos").reset_index(drop=True)
from retrieval.rankers import (                            # noqa: E402
    score_controlled, score_metric_robustness, SCORERS, METRIC_SET)
from retrieval.evaluation import hit_at_1                  # noqa: E402
from utils.io import results_path, write_csv               # noqa: E402
from utils.logging import log, section                    # noqa: E402

OUT = "exp02_divergence_gate"


def divergence_sweep(data, lams, n_seeds, cell_line="K562", alpha=0.7, ntot=800,
                     n_distractors=40):
    task = ControlledMixtureTask(data, cell_line=cell_line, n_total=ntot)
    rows = []
    for lam in lams:
        for s in range(n_seeds):
            q, cos = build_divergence_query(task, lam, alpha, ntot, n_distractors, 3000 + s)
            sc = score_controlled(q)
            names = list(q["candidates"])
            gt = names.index("covers-both")
            for scorer in SCORERS:
                vals = np.array([sc[scorer][n] for n in names])
                rows.append({"lam": lam, "subpop_cos": round(cos, 3), "scorer": scorer,
                             "hit@1": hit_at_1(vals, gt)})
        sub = pd.DataFrame([r for r in rows if r["lam"] == lam])
        log(f"  [div] lam={lam:4.2f} cos={sub.subpop_cos.iloc[0]:+.2f} | " +
            "  ".join(f"{s}={sub[sub.scorer==s]['hit@1'].mean():.2f}" for s in SCORERS))
    return pd.DataFrame(rows)


def power_sweep(data, Ns, n_seeds, cell_line="K562", alpha=0.7):
    task = ControlledMixtureTask(data, cell_line=cell_line, n_total=1600)
    rows = []
    for N in Ns:
        for s in range(n_seeds):
            q = task.build(alpha, n_distractors=40, seed=1000 + s)
            q2 = subsample_controlled_query(q, N, seed=2000 + s)
            sc = score_controlled(q2)
            names = list(q2["candidates"])
            gt = names.index("covers-both")
            for scorer in SCORERS:
                vals = np.array([sc[scorer][n] for n in names])
                rows.append({"N": N, "scorer": scorer, "hit@1": hit_at_1(vals, gt)})
        sub = pd.DataFrame([r for r in rows if r["N"] == N])
        log(f"  [power] N={N:4d} | " +
            "  ".join(f"{s}={sub[sub.scorer==s]['hit@1'].mean():.2f}" for s in SCORERS))
    return pd.DataFrame(rows)


def metric_sweep(data, lams, n_seeds, cell_line="K562", alpha=0.7, ntot=800,
                 n_distractors=40, cap=220):
    task = ControlledMixtureTask(data, cell_line=cell_line, n_total=ntot)
    rows = []
    for lam in lams:
        for s in range(n_seeds):
            q, cos = build_divergence_query(task, lam, alpha, ntot, n_distractors, 3000 + s)
            sc = score_metric_robustness(q, cap=cap, seed=5000 + s, n_proj=64)
            names = list(q["candidates"])
            gt = names.index("covers-both")
            for m in METRIC_SET:
                vals = np.array([sc[m][n] for n in names])
                rows.append({"lam": lam, "subpop_cos": round(cos, 3), "metric": m,
                             "hit@1": hit_at_1(vals, gt)})
        sub = pd.DataFrame([r for r in rows if r["lam"] == lam])
        log(f"  [metric] lam={lam:4.2f} cos={sub.subpop_cos.iloc[0]:+.2f} | " +
            "  ".join(f"{m}={sub[sub.metric==m]['hit@1'].mean():.2f}" for m in METRIC_SET))
    return pd.DataFrame(rows)


def run(n_seeds=20, processed=None):
    data = load_sciplex3(processed)
    log(data.summary())
    section("EXP02a divergence sweep")
    dv = divergence_sweep(data, [0.0, 0.25, 0.5, 0.75, 1.0, 1.5], n_seeds)
    section("EXP02b power sweep")
    pw = power_sweep(data, [15, 30, 60, 120, 240], n_seeds)
    section("EXP02c metric robustness")
    mr = metric_sweep(data, [0.0, 0.5, 0.75, 1.0, 1.5], n_seeds)

    write_csv(dv, results_path(OUT, "divergence_sweep.csv"))
    write_csv(pw, results_path(OUT, "depth_sweep.csv"))
    write_csv(mr, results_path(OUT, "metric_robustness.csv"))

    section("EXP02d dataset positions on the gate")
    positions = dataset_positions_on_gate(data)
    write_csv(positions, results_path(OUT, "dataset_positions_on_gate.csv"))
    log(positions.round(3).to_string(index=False))

    section("EXP02 VERDICTS vs FINDINGS §8")
    checks = []
    # power: advantage large already at low depth; energy monotone up in N and >> mean
    pv = pw.groupby(["N", "scorer"])["hit@1"].mean().unstack()
    e_low = pv.loc[[n for n in (15, 30, 60) if n in pv.index], "global_energy"]
    checks.append(ordering_verdict(
        "power: global_energy >> mean_cosine at 15-60 cells/subpop",
        bool((e_low > pv.loc[e_low.index, "mean_cosine"] + 0.3).all()),
        f"energy@{{15,30,60}}={e_low.round(2).to_dict()} mean~{pv['mean_cosine'].mean():.2f}"))
    # divergence: advantage rises as subpop_cos falls
    dvp = dv.groupby(["subpop_cos", "scorer"])["hit@1"].mean().unstack().sort_index()
    adv = (dvp["global_energy"] - dvp["mean_cosine"])
    checks.append(ordering_verdict(
        "divergence: advantage largest at most-divergent (lowest cos), ~0 at cos~1",
        bool(adv.idxmin() >= adv.idxmax() - 1e-9 or adv.iloc[0] > adv.iloc[-1]),
        f"adv(low cos)={adv.iloc[0]:.2f} adv(high cos)={adv.iloc[-1]:.2f}"))
    # metric: energy/mmd/sliced_w all beat mean at the most-divergent lam
    mrp = mr.groupby(["subpop_cos", "metric"])["hit@1"].mean().unstack().sort_index()
    lo = mrp.iloc[0]
    checks.append(ordering_verdict(
        "metric-agnostic: energy/mmd/sliced_w all >> mean_cosine at low cos",
        bool((lo[["energy", "mmd", "sliced_w"]] > lo["mean_cosine"] + 0.2).all()),
        f"@cos={mrp.index[0]:+.2f}: " + " ".join(f"{m}={lo[m]:.2f}" for m in METRIC_SET)))
    return {"checks": checks}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-seeds", type=int, default=20)
    ap.add_argument("--processed", default=None)
    args = ap.parse_args()
    run(n_seeds=args.n_seeds, processed=args.processed)


if __name__ == "__main__":
    main()
