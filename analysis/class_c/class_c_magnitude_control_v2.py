#!/usr/bin/env python3
"""Class C: does a retrieval ranking surface therapeutically potent drugs?

Rewritten. The v1 script (class_c_magnitude_control.py, class_c_experiment.py) had a sign
error that inverted the entire result, plus two configuration faults. All three are fixed
here and the v1 numbers must not be used.

  1. THE SIGN. `retrieval.metrics.score_energy` returns MINUS the energy distance, i.e. a
     SIMILARITY (higher = more similar). v1 ranked it ascending (`rankdata(e_scores)`,
     `argmin(dart_scores)`) under the comment "lowest energy = top pick", so DART's rank-1
     candidate was the population FARTHEST from the query. The mean-cosine baseline in the
     same scripts was ranked correctly (`argmax`). DART was therefore ranked backwards and
     its incumbent was not.

     This is not a cosmetic bug. Candidates with large response magnitude sit far from the
     query (rank corr between energy distance and candidate magnitude = +0.83), and large
     response magnitude predicts potency. Ranking "farthest first" therefore selects potent
     drugs, which is where v1's apparent +0.52 DART-vs-potency correlation came from. It
     was an artifact of the inversion.

  2. THE DOSE. v1 pooled all four SciPlex3 doses (10 nM to 10 uM) into each drug's
     population. Every other retrieval experiment in the paper runs at 10 uM. A four-dose
     pool is multimodal along the dose axis by construction, so it is not the same task.
     Fixed to 10 uM.

  3. THE ASSAY. v1 pooled GDSC1 and GDSC2 AUCs into one potency ranking. They are different
     platforms and their AUCs are not on a common scale. Fixed to GDSC2 only.

RANKINGS COMPARED (all scored against external GDSC potency, which no scorer can see):
  energy            distributional retrieval, ranked correctly (most similar first)
  mean_cosine_ctrl  the correct incumbent: cosine of CONTROL-SUBTRACTED mean signatures
  mean_cosine_raw   the incumbent as commonly run, without control subtraction
  magnitude_only    rank candidates by the norm of their own response. QUERY-INDEPENDENT:
                    it produces one ordering for every query and performs no retrieval.
                    This is the control that matters, because response magnitude predicts
                    potency on its own and any retrieval score must be shown to beat it.

    PYTHONPATH=src python analysis/class_c/class_c_magnitude_control_v2.py
"""
from pathlib import Path as _P
REPO = _P(__file__).resolve().parents[2]
import sys
sys.path.insert(0, str(REPO / "src"))

import json
import numpy as np
import pandas as pd
from scipy import stats

from data.load_sciplex3 import load_sciplex3
from retrieval.metrics import score_energy, score_mean_cosine

SEED = 42
DOSE = 10000.0          # 10 uM, the dose every other retrieval experiment in the paper uses
GDSC_SOURCE = "GDSC2"   # one platform only; GDSC1 and GDSC2 AUCs are not on a common scale
OUT = REPO / "results" / "upgrade"

np.random.seed(SEED)


def dense(a):
    return a.toarray() if hasattr(a, "toarray") else np.asarray(a)


def main() -> None:
    match = pd.read_csv(OUT / "drug_match_table.csv")
    n_all = len(match)
    match = match[match.gdsc_source == GDSC_SOURCE].copy()
    match = match[match.sp_drug != "S-Ruxolitinib (INCB018424)"].copy()
    print(f"match table: {n_all} rows -> {len(match)} after restricting to {GDSC_SOURCE} "
          f"and dropping the duplicate mapping")

    ds = load_sciplex3()
    obs = ds.obs
    dose_v = obs["dose_value"].values if "dose_value" in obs.columns else None
    if dose_v is None:
        raise RuntimeError("no dose_value column: cannot restrict to 10 uM, and pooling "
                           "doses is what this rewrite exists to stop.")

    rows, direct = [], {}
    for line in ["A549", "K562", "MCF7"]:
        lm = match[match.cell_line == line]
        via = dict(zip(lm.sp_drug, lm.AUC))
        in_line = (obs["cell_line"] == line).values
        at_dose = in_line & (dose_v == DOSE)
        ctrl = dense(ds.X[in_line & obs["is_control"].values]).mean(0).astype(np.float64)

        cells, dmean, mag = {}, {}, {}
        for d in sorted(lm.sp_drug.unique()):
            m = at_dose & (obs["perturbation"] == d).values & (~obs["is_control"].values)
            if m.sum() >= 10:
                C = dense(ds.X[m]).astype(np.float64)
                cells[d] = C
                dmean[d] = C.mean(0) - ctrl
                mag[d] = float(np.linalg.norm(dmean[d]))
        valid = sorted(cells)
        if len(valid) < 8:
            print(f"  {line}: only {len(valid)} drugs at {DOSE:.0f} nM, skipped")
            continue

        r, p = stats.spearmanr([mag[d] for d in valid], [via[d] for d in valid])
        direct[line] = {"rho_magnitude_vs_AUC": float(r), "p": float(p), "n_drugs": len(valid)}
        print(f"  {line}: {len(valid)} drugs at 10 uM; magnitude vs potency rho={r:+.3f} p={p:.1e}")

        for q in valid:
            cand = [d for d in valid if d != q]
            qc, qd = cells[q], dmean[q]
            e_sim, cos_ctrl, cos_raw, magonly, auc = [], [], [], [], []
            for c in cand:
                # score_energy returns MINUS the distance: HIGHER = MORE SIMILAR.
                e_sim.append(score_energy(qc, cells[c], max_cells=500, seed=SEED))
                cos_ctrl.append(score_mean_cosine(cells[c], qc, control_P=ctrl, control_Q=ctrl))
                cos_raw.append(score_mean_cosine(cells[c], qc))
                magonly.append(mag[c])
                auc.append(via[c])
            e_sim, magonly, auc = map(np.asarray, (e_sim, magonly, auc))
            cos_ctrl, cos_raw = np.asarray(cos_ctrl), np.asarray(cos_raw)

            # rank 1 = the candidate the method puts FIRST. Every score here is a
            # similarity (higher = better), so every ranking negates before rankdata.
            pot = stats.rankdata(auc)                 # rank 1 = lowest AUC = most potent
            def rho(sim):
                return float(stats.spearmanr(stats.rankdata(-np.asarray(sim)), pot)[0])

            rows.append({
                "cell_line": line, "query_drug": q, "n_cand": len(cand),
                "query_magnitude": mag[q], "query_auc": via[q],
                "energy_rho": rho(e_sim),
                "mean_cosine_ctrl_rho": rho(cos_ctrl),
                "mean_cosine_raw_rho": rho(cos_raw),
                "magnitude_only_rho": rho(magonly),
                # is the energy ranking a magnitude ranking? use the DISTANCE, not the score.
                "energydist_vs_candmag_rho": float(stats.spearmanr(-e_sim, magonly)[0]),
            })

    df = pd.DataFrame(rows)
    df.to_csv(OUT / "class_c_magnitude_control_v2.csv", index=False)

    cols = ["energy_rho", "mean_cosine_ctrl_rho", "mean_cosine_raw_rho",
            "magnitude_only_rho", "energydist_vs_candmag_rho"]
    res = {"n_queries": len(df), "dose_nM": DOSE, "gdsc_source": GDSC_SOURCE,
           "direct_magnitude_vs_AUC": direct}
    print(f"\n{'ranking':32s} {'median rho':>11s} {'mean rho':>10s}")
    print("-" * 56)
    for c in cols:
        res[c + "_median"] = float(df[c].median())
        res[c + "_mean"] = float(df[c].mean())
        print(f"  {c:30s} {df[c].median():+11.4f} {df[c].mean():+10.4f}")

    # paired: magnitude-only vs energy. Report per cell line too: the magnitude-only ranking
    # is query-independent, so its per-query rho is nearly constant within a line and the
    # 152 "paired queries" are NOT independent. The per-line medians are the honest summary.
    print("\nPER CELL LINE (the honest unit: the query-independent control is constant within a line)")
    res["per_line"] = {}
    for line, s in df.groupby("cell_line"):
        d = {c: float(s[c].median()) for c in cols}
        d["n_queries"] = int(len(s))
        d["magonly_beats_energy"] = int((s.magnitude_only_rho > s.energy_rho).sum())
        res["per_line"][line] = d
        print(f"  {line}: energy {d['energy_rho']:+.3f} | mean(ctrl) {d['mean_cosine_ctrl_rho']:+.3f} | "
              f"mean(raw) {d['mean_cosine_raw_rho']:+.3f} | magnitude-only {d['magnitude_only_rho']:+.3f} "
              f"| magonly>energy {d['magonly_beats_energy']}/{d['n_queries']}")

    w = stats.wilcoxon(df.magnitude_only_rho, df.energy_rho)
    res["wilcoxon_magonly_vs_energy"] = {"stat": float(w.statistic), "p": float(w.pvalue),
                                         "n": int(len(df)),
                                         "note": "queries within a cell line share a candidate "
                                                 "pool and the magnitude-only ranking is "
                                                 "query-independent, so this p-value is "
                                                 "anticonservative. Use the per-line medians."}
    res["magonly_beats_energy_overall"] = int((df.magnitude_only_rho > df.energy_rho).sum())
    print(f"\nmagnitude-only beats energy in {res['magonly_beats_energy_overall']}/{len(df)} queries")
    print(f"  (Wilcoxon p={w.pvalue:.2e}, but see the note: this is anticonservative.)")

    json.dump(res, open(OUT / "class_c_magnitude_control_v2.json", "w"), indent=2)
    print(f"\nwrote {OUT/'class_c_magnitude_control_v2.csv'} and .json")


if __name__ == "__main__":
    main()
