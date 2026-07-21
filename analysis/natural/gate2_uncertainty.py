#!/usr/bin/env python3
"""How much do we actually know about the +0.117 gap? Three attacks on our own headline number.

THE NUMBER UNDER TEST
---------------------
The paper's one CONSTRUCTIVE claim is that in a real tumour Gate 2 is an ALGORITHMIC bottleneck:
the supervised ceiling is 0.923, the best unsupervised method reaches 0.777, and the gap of +0.117
is far larger than the +0.007 on the like-for-like constructed split. That claim is now in the
abstract, the introduction, Fig. 6d and the discussion, and it is the least defended number in the
paper. It has three problems, and this script attacks all three.

PROBLEM 1: THE GAP IS A DIFFERENCE OF TWO MAXIMA (the winner's curse).
    gap = max(3 supervised probes) - max(4 unsupervised clusterers)
A maximum over methods is upward-biased: whichever method got lucky on this sample is the one
reported. Both terms are inflated, and the biases do NOT cancel, because 3 and 4 methods with
different variances are being maximised over. We therefore also report every FIXED (probe,
clusterer) pair, which involves no selection at all. If the gap only exists when both ends are
maximised, it is an artefact and we say so.

PROBLEM 2: THERE IS NO UNCERTAINTY ESTIMATE AT ALL. A single median over splits was reported.

PROBLEM 3: 30 OF THE 36 SPLITS COME FROM ONE PATIENT (PW030, the only one given more than two
compounds), and they reuse the same six drugs. Bootstrapping over SPLITS would treat those 30 as
independent and produce a confidence interval that is far too narrow: it would be the same
pseudo-replication this paper devotes a section to criticising. THE BOOTSTRAP IS THEREFORE OVER
PATIENTS (a cluster bootstrap), which is the honest unit and gives a much wider interval. With 4
patients that interval will be wide, and reporting it wide is the point.

We additionally do the sharpest robustness check available: DROP PW030 ENTIRELY and see what
survives on the remaining three patients.

    PYTHONPATH=src python analysis/natural/gate2_uncertainty.py
"""
from pathlib import Path as _P
REPO = _P(__file__).resolve().parents[2]
import sys
sys.path.insert(0, str(REPO / "src"))

import itertools
import json

import numpy as np
import pandas as pd

SRC = REPO / "results" / "zhao_gbm" / "gate2_drug_response.csv"
OUT = REPO / "results" / "zhao_gbm"
N_BOOT = 5000
SEED = 0

UNSUP = ["kmeans_k2", "gmm_k2", "leiden", "hdbscan"]
SUP = ["linear", "forest", "knn"]
SPLIT_KEY = ["patient", "compartment", "drug_a", "drug_b"]


def per_split(df):
    """Collapse seeds. One row per (patient, compartment, drug pair): the unit of analysis."""
    return df.groupby(["arm"] + SPLIT_KEY, as_index=False).median(numeric_only=True)


def cluster_bootstrap(g, value_col, n_boot=N_BOOT, seed=SEED):
    """Resample PATIENTS, not splits.

    The 36 natural splits are not 36 independent observations: 30 of them come from one patient and
    reuse the same six drugs. A split-level bootstrap would treat them as independent and return an
    interval several times too narrow. Resampling whole patients (with all their splits) respects
    the dependency. For the constructed arm every split shares the single pseudo-patient "-", so
    this correctly degenerates to a split-level bootstrap there, which is right: those splits ARE
    independent draws from one cell line.
    """
    rng = np.random.default_rng(seed)
    pats = g.patient.unique()
    v = g[value_col].to_numpy()
    if len(v) < 3:
        # A bootstrap over one or two observations returns a zero-width or two-point interval,
        # which LOOKS like precision and is nothing of the kind. Refuse rather than mislead.
        return np.full(n_boot, np.nan)
    if len(pats) == 1:                                  # constructed arm: no patient structure
        idx = rng.integers(0, len(v), size=(n_boot, len(v)))
        return np.median(v[idx], axis=1)
    by_pat = {p: g.loc[g.patient == p, value_col].to_numpy() for p in pats}
    out = np.empty(n_boot)
    for b in range(n_boot):
        draw = rng.choice(pats, size=len(pats), replace=True)
        out[b] = np.median(np.concatenate([by_pat[p] for p in draw]))
    return out


def ci(v, lo=2.5, hi=97.5):
    if np.all(np.isnan(v)):
        return float("nan"), float("nan")
    return float(np.nanpercentile(v, lo)), float(np.nanpercentile(v, hi))


def main():
    df = pd.read_csv(SRC)
    need = [f"sup_{m}" for m in SUP]
    missing = [c for c in need if c not in df.columns]
    if missing:
        raise SystemExit(
            f"{SRC} lacks the per-method supervised columns {missing}. Re-run "
            f"analysis/natural/gate2_drug_response.py, which now stores every probe rather than "
            f"only the winner. Without them the winner's-curse analysis cannot be done.")

    g = per_split(df)
    res = {"n_boot": N_BOOT, "bootstrap_unit": "patient (cluster bootstrap)"}

    print("=" * 100)
    print("THE +0.117 GAP, WITH ITS UNCERTAINTY. Bootstrap resamples PATIENTS, not splits.")
    print("=" * 100)

    # ---------------- 1. the headline gap, with a patient-level CI ----------------
    print(f"\n1. THE HEADLINE GAP  (both ends MAXIMISED, as reported)\n")
    print(f"   {'arm':20s} {'splits':>6s} {'patients':>8s} {'gap':>8s}  {'95% CI (patient bootstrap)':>28s}")
    print("   " + "-" * 78)
    for arm in ["constructed_class", "constructed_drug", "natural"]:
        s = g[g.arm == arm]
        if s.empty:
            continue
        boot = cluster_bootstrap(s, "gap_matched")
        lo, hi = ci(boot)
        med = float(s.gap_matched.median())
        npat = s.patient.nunique()
        res[arm] = {"gap_matched": med, "ci95": [lo, hi], "n_splits": int(len(s)),
                    "n_patients": int(npat)}
        print(f"   {arm:20s} {len(s):>6d} {npat:>8d} {med:>+8.3f}  [{lo:+.3f}, {hi:+.3f}]")

    # the comparison that carries the claim: is natural > constructed?
    if "natural" in res and "constructed_drug" in res:
        rng = np.random.default_rng(SEED)
        bn = cluster_bootstrap(g[g.arm == "natural"], "gap_matched", seed=SEED)
        bc = cluster_bootstrap(g[g.arm == "constructed_drug"], "gap_matched", seed=SEED + 1)
        diff = bn - bc
        dlo, dhi = ci(diff)
        p_le0 = float((diff <= 0).mean())
        res["natural_minus_constructed"] = {"point": res["natural"]["gap_matched"]
                                            - res["constructed_drug"]["gap_matched"],
                                            "ci95": [dlo, dhi], "frac_boot_le_0": p_le0}
        print(f"\n   natural gap MINUS constructed gap: "
              f"{res['natural_minus_constructed']['point']:+.3f}  "
              f"[{dlo:+.3f}, {dhi:+.3f}], {p_le0*100:.1f}% of bootstrap draws <= 0")

    # ---------------- 2. the winner's curse ----------------
    print(f"\n\n2. THE WINNER'S CURSE. Every FIXED (probe, clusterer) pair, no maximum taken.\n")
    fixed = {}
    for arm in ["constructed_drug", "natural"]:
        s = g[g.arm == arm]
        if s.empty:
            continue
        rows = []
        for sup, uns in itertools.product(SUP, UNSUP):
            gap = (s[f"sup_{sup}"] - s[f"acc_{uns}"]).median()
            rows.append({"sup": sup, "unsup": uns, "gap": float(gap)})
        fixed[arm] = rows
        vals = [r["gap"] for r in rows]
        # HDBSCAN is DEGENERATE here: it finds no density structure and assigns every cell to
        # noise, scoring exactly 0.500 (chance). Pairs involving it therefore show a huge "gap"
        # for a trivial reason (the clusterer did nothing), and including them inflates the
        # median. They are reported but excluded from the headline fixed-pair figure, and the
        # exclusion is stated rather than silent.
        live = [r["gap"] for r in rows if r["unsup"] != "hdbscan"]
        res[f"{arm}_fixed_pairs"] = {
            "median_over_pairs": float(np.median(vals)),
            "median_excluding_degenerate_hdbscan": float(np.median(live)),
            "min": float(min(vals)), "max": float(max(vals)), "pairs": rows,
            "note": "HDBSCAN assigns every cell to noise (acc = 0.500 = chance); pairs involving "
                    "it show a large gap because the clusterer did nothing, not because the "
                    "information is unreachable. The headline fixed-pair number excludes it."}
        print(f"   {arm}")
        print(f"      {'probe':10s} " + " ".join(f"{u:>10s}" for u in UNSUP))
        for sup in SUP:
            line = " ".join(f"{[r for r in rows if r['sup']==sup and r['unsup']==u][0]['gap']:>+10.3f}"
                            for u in UNSUP)
            print(f"      {sup:10s} {line}")
        print(f"      -> median over the 12 fixed pairs: {np.median(vals):+.3f} "
              f"(range {min(vals):+.3f} to {max(vals):+.3f})")
        print(f"      -> EXCLUDING degenerate HDBSCAN (it assigns every cell to noise, acc=0.500): "
              f"{np.median(live):+.3f}")
        print(f"      -> reported (both ends maximised): "
              f"{res[arm]['gap_matched']:+.3f}\n")

    if "natural" in fixed and "constructed_drug" in fixed:
        mn = np.median([r["gap"] for r in fixed["natural"] if r["unsup"] != "hdbscan"])
        mc = np.median([r["gap"] for r in fixed["constructed_drug"] if r["unsup"] != "hdbscan"])
        res["fixed_pair_contrast"] = {"natural": float(mn), "constructed_drug": float(mc),
                                      "difference": float(mn - mc)}
        print(f"   WITHOUT ANY SELECTION, the natural gap is {mn:+.3f} against {mc:+.3f} "
              f"constructed (difference {mn - mc:+.3f}).")
        print(f"   Selection inflates the reported gap by "
              f"{res['natural']['gap_matched'] - mn:+.3f} in the natural arm and "
              f"{res['constructed_drug']['gap_matched'] - mc:+.3f} in the constructed arm.")

    # ---------------- 3. drop the dominant patient ----------------
    print(f"\n\n3. DROP PW030, the patient contributing 30 of the 36 natural splits.\n")
    nat = g[g.arm == "natural"]
    dom = nat.patient.value_counts().idxmax()
    rest = nat[nat.patient != dom]
    only = nat[nat.patient == dom]
    for lab, s in [(f"only {dom}", only), (f"WITHOUT {dom}", rest)]:
        if s.empty:
            print(f"   {lab:18s} no splits")
            continue
        boot = cluster_bootstrap(s, "gap_matched")
        lo, hi = ci(boot)
        fx = np.median([(s[f"sup_{a}"] - s[f"acc_{b}"]).median()
                        for a, b in itertools.product(SUP, UNSUP)])
        res[f"natural_{lab.replace(' ', '_')}"] = {
            "gap_matched": float(s.gap_matched.median()), "ci95": [lo, hi],
            "fixed_pair_gap": float(fx), "n_splits": int(len(s)),
            "n_patients": int(s.patient.nunique())}
        print(f"   {lab:18s} splits={len(s):>2d}  patients={s.patient.nunique()}  "
              f"gap={s.gap_matched.median():+.3f} [{lo:+.3f}, {hi:+.3f}]  "
              f"fixed-pair gap={fx:+.3f}")

    json.dump(res, open(OUT / "gate2_uncertainty.json", "w"), indent=2)
    print(f"\nwrote {OUT/'gate2_uncertainty.json'}")
    print("\nNo verdict is emitted. The numbers are reported and interpreted in the text.")


if __name__ == "__main__":
    main()
