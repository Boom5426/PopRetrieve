#!/usr/bin/env python
"""Covariance control for the Gaussian optimal-transport predictor: gates, steps and contrasts.

Reads the output of src/experiments/phase2_transition/phase_b_loco.py run with the four OT arms,
checks that the ot_map arm reproduces the reference run and that the mean rules rank
identically under every arm, and then compares the energy ranking of ot_map with that of each
control arm, query by query.

outcome.json names the pattern the energy dMRR contrasts (ot_map minus each arm) follow:
O1, the shared and the deranged contrasts both lie above zero; O2, the shared contrast spans
zero and the identity contrast lies above zero; O3, the identity contrast spans zero.

    python -I src/experiments/exp21_covariance_control.py \
        --res results/phase2_transition/covariance_control
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src" / "experiments" / "phase2_transition"))
import phase2_common as pc  # noqa: E402

POSITIVE = "ot_map"
CONTROLS = ("ot_map_identity", "ot_map_shared", "ot_map_deranged")
KEY = ["cell_line", "drug", "seed"]
# Reference ot_map run (results/phase2_transition/phase_b_p5/delta_vs_reference.csv).
GATE = {("energy", "mean_l2"): 0.011041508425055902,
        ("mean_l2", "mean_cosine"): -0.008324192644609853}
GATE_TOL = 5e-4
N_PAIRED = 19_960
METRICS = (("reciprocal_rank", "dMRR"), ("hit@1", "dHit@1"))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--res", type=Path, required=True)
    args = ap.parse_args()
    pq = pd.read_csv(args.res / "per_query.csv.gz")
    dv = pd.read_csv(args.res / "delta_vs_reference.csv")
    arms = (POSITIVE, *CONTROLS)
    missing = set(arms) - set(pq.predictor)
    if missing:
        raise ValueError(f"missing arms {sorted(missing)}")

    gates = {}
    for (scorer, ref), target in GATE.items():
        r = dv[(dv.predictor == POSITIVE) & (dv.scorer == scorer) & (dv.reference == ref)].iloc[0]
        gates[f"{scorer}_minus_{ref}"] = {"target": target, "reproduced": float(r.dMRR),
                                          "n_paired": int(r.n_paired),
                                          "pass": abs(r.dMRR - target) <= GATE_TOL
                                          and int(r.n_paired) == N_PAIRED}
    for scorer in ("mean_l2", "mean_cosine"):
        ranks = pq[pq.scorer == scorer].pivot_table(index=KEY, columns="predictor", values="rank")
        same = all((ranks[a] == ranks[POSITIVE]).all() for a in CONTROLS)
        gates[f"{scorer}_ranks_identical_across_arms"] = {"n_rows": int(len(ranks)), "pass": same}
    (args.res / "gates.json").write_text(json.dumps(gates, indent=2))
    print(json.dumps(gates, indent=2))
    if not all(g["pass"] for g in gates.values()):
        print("gate failed: no arm is interpreted")
        return

    steps = dv[dv.predictor.isin(arms)
               & (((dv.scorer == "energy") & dv.reference.isin(["mean_l2", "mean_cosine"]))
                  | ((dv.scorer.isin(["mmd", "energy_v_statistic"])) & (dv.reference == "mean_l2")))]
    steps = steps[["predictor", "scorer", "reference", "n_paired", "dMRR", "dMRR_lo", "dMRR_hi",
                   "dHit@1", "dHit@1_lo", "dHit@1_hi"]]
    steps.to_csv(args.res / "steps_by_arm.csv", index=False)

    rows = []
    for scorer in ("energy", "mmd"):
        s = pq[pq.scorer == scorer].set_index(KEY)
        pos = s[s.predictor == POSITIVE]
        for arm in CONTROLS:
            j = pos.join(s[s.predictor == arm], rsuffix="_arm", how="inner").reset_index()
            rec = {"scorer": scorer, "contrast": f"{POSITIVE} minus {arm}", "n_paired": len(j)}
            for col, name in METRICS:
                j["_d"] = j[col] - j[f"{col}_arm"]
                rec[name] = float(j["_d"].mean())
                rec[f"{name}_lo"], rec[f"{name}_hi"] = pc.cluster_bootstrap(j, "_d", "cell_line")
            rows.append(rec)
    contrasts = pd.DataFrame(rows)
    contrasts.to_csv(args.res / "contrasts.csv", index=False)

    prim = contrasts[contrasts.scorer == "energy"].set_index("contrast")

    def above(arm: str) -> bool:
        return bool(prim.loc[f"{POSITIVE} minus {arm}", "dMRR_lo"] > 0)

    def spans(arm: str) -> bool:
        r = prim.loc[f"{POSITIVE} minus {arm}"]
        return bool(r.dMRR_lo <= 0 <= r.dMRR_hi)

    matched = [name for name, ok in (
        ("O1", above("ot_map_deranged") and above("ot_map_shared")),
        ("O2", spans("ot_map_shared") and above("ot_map_identity")),
        ("O3", spans("ot_map_identity"))) if ok]
    outcome = {"matched": matched,
               "outcome": matched[0] if len(matched) == 1 else "other: reported as it stands"}
    (args.res / "outcome.json").write_text(json.dumps(outcome, indent=2))
    print(steps.round(4).to_string(index=False))
    print(contrasts.round(4).to_string(index=False))
    print(json.dumps(outcome, indent=2))


if __name__ == "__main__":
    main()
