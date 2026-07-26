"""The premise correlation, recomputed on DISJOINT compartments.

WHY
---
The manuscript reports that in a patient's tumour the similarity of two drugs' MEAN signatures
ranks the similarity of their MALIGNANT-compartment responses at Spearman +0.878 (Fig. 5f), and
reads that as the mean already ranking most of what the subpopulation does.

That statistic has a mechanical component. The mean signature is taken over ALL called cells, and
malignant glioma is 41,314 of the 96,225 called cells, i.e. 43% of them (Supplementary Table 3).
The two quantities being correlated therefore share nearly half their cells, so part of the
correlation is arithmetic rather than biology. The same structure was found and corrected in the
Tahoe pilot, where the mean signature contained 26% of the compartment being predicted and the
overlap was worth +0.064 of rho.

The clean version uses compartments that share no cells at all: does the MYELOID compartment's
response similarity rank the MALIGNANT compartment's? Each compartment's response is already
referred to its own compartment-matched control in the upstream analysis, so the baseline
identity of each compartment cancels and what is compared is response.

This script recomputes from the per-pair table the upstream analysis already writes. It adds no
new data and fits nothing.

Run: python zhao_premise_disjoint.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
from scipy.stats import spearmanr

REPO = Path(__file__).resolve().parents[2]
SRC = REPO / "results" / "zhao_gbm" / "premise_mean_vs_compartment.csv"


def main() -> int:
    if not SRC.exists():
        raise FileNotFoundError(
            f"{SRC} is missing. It is written by analysis/natural/zhao_two_gates.py; run that "
            f"first. This script deliberately does not recompute the compartment responses, so "
            f"that the disjoint statistic is derived from exactly the same per-pair values as "
            f"the published one and the two cannot drift apart.")
    d = pd.read_csv(SRC)
    need = {"cos_mean_signature", "cos_malignant_response", "cos_myeloid_response"}
    missing = need - set(d.columns)
    if missing:
        raise KeyError(f"{SRC} lacks {sorted(missing)}; cannot compute the disjoint statistic")

    print(f"pairs {len(d)} | patients {d.patient.nunique()} | "
          f"per patient {d.patient.value_counts().to_dict()}")
    print("NOTE: 15 of the 18 pairs come from PW030, so neither statistic below is quoted with a "
          "p-value; they are a strong association in one patient, consistent in sign with three "
          "single-pair observations elsewhere.")

    rows = []
    for name, x, y in [
        ("published  (mean signature -> malignant, SHARES 43% of its cells)",
         "cos_mean_signature", "cos_malignant_response"),
        ("disjoint   (myeloid -> malignant, shares no cells)",
         "cos_myeloid_response", "cos_malignant_response"),
    ]:
        rho, _ = spearmanr(d[x], d[y])
        rows.append((name, rho))
        print(f"  {name:62s} rho = {rho:+.3f}")
    print(f"\n  effect of removing the mechanical overlap: {rows[1][1] - rows[0][1]:+.3f}")

    pw = d[d.patient == "PW030"]
    print(f"\nPW030 alone (n={len(pw)}):")
    print(f"  published {spearmanr(pw.cos_mean_signature, pw.cos_malignant_response)[0]:+.3f} | "
          f"disjoint {spearmanr(pw.cos_myeloid_response, pw.cos_malignant_response)[0]:+.3f}")

    out = REPO / "results" / "zhao_gbm" / "premise_disjoint.csv"
    pd.DataFrame(rows, columns=["statistic", "spearman_rho"]).to_csv(out, index=False)
    print(f"\nwrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
