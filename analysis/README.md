> **SUPERSEDED IN PART, audited 2026-07-27.** This is a working document. It predates the July
> 2026 audit, which retracted or revised numbers this file may still quote, among them the
> "5.1x structure collapse" (R1), the MoA-nDCG statistics computed over 165 undefined sentinel
> values (R2), the Class A/B contrast that compared two different scorers (R4), the HIR-Bench
> predictability AUC of 0.640 (R11), the claim that no Class C metric was available (R14), and
> the "0 of 37 real-data tasks" count (R13). **Read [CORRECTIONS.md](../CORRECTIONS.md) before quoting any
> number below**, and treat `manuscript/latex/EvalShift_manuscript.tex` as the authority for
> anything that reaches the paper. Where this file and CORRECTIONS.md disagree, CORRECTIONS.md
> is right.

# analysis/, post-hoc audit and upgrade experiments

This directory holds the analyses developed during the EvalShift audit and upgrade
cycle (2026-07). They are organized by the question each one answers, and every
script resolves the repository root from its own location, so they run from a
checkout without editing paths:

```bash
PYTHONPATH=src python analysis/<category>/<script>.py
```

Outputs go to `results/`, mostly but **not only** `results/upgrade/`: the natural-tissue scripts
write `results/zhao_gbm/` and the Tahoe pilot writes `results/tahoe_pilot/`. Large inputs (the GDSC2
dose-response workbook, the SciPlex3 tensor, the ZhaoSims2021 h5ad, the Tahoe plate) are obtained
separately, see `DATA.md`.

## Layout

| directory | question it answers | key outputs |
|-----------|--------------------|-------------|
| `diagnostics/` | Is a distributional method's null a REAL null or an implementation artifact? | `dart_diagnostic.py` (four-probe module), `protocol_validation.py` |
| `audit/` | Do the seven candidate objections to the null survive scrutiny? | delta-vs-raw, subsample power, minority-coverage blindspot, gate circularity, welfare proxy, end-to-end fix |
| `identifiability/` | Can subpopulation structure be recovered at all, and what does the real signal encode? | subpopulation-identifiability landscape, phase diagram, EvalShift-vs-mean signal decode |
| `class_c/` | Does EvalShift's ranking track a real viability oracle, or a response-magnitude confound? | GDSC drug matching, viability experiment, magnitude control |
| `hir_bench/` | Is retrieval failure predictable from observable features? | HIR-Bench predictability ROC and the 2x2 that separates feature circularity from pseudo-replication |
| `natural/` | Do the two gates open in patient tissue nobody constructed? | `zhao_two_gates.py`, `zhao_threshold_sensitivity.py`, `zhao_premise_disjoint.py` -> `results/zhao_gbm/` |
| `predictors/` | Does a non-additive predictor open Gate 1, and does that help? | OT map, CellFlow and CPA as Part-B instruments |
| `tahoe_pilot/` | Do the gates hold at scale on unconstructed material? | Tahoe-100M plate 3 -> `results/tahoe_pilot/` |

## The headline finding

The audit confirmed that EvalShift's oracle-independent null is a **real null**, not
an artifact: seven candidate objections were falsified, and the four confirmed
weaknesses all pointed the same direction (they had been *over*-crediting EvalShift,
not under-crediting it). The `diagnostics/` four-probe protocol packages the
reusable core of that audit so the same test can be run on any distributional
retrieval method.

See `manuscript/latex/EvalShift_manuscript.tex` for the full narrative (the sources are in this
repository); each subdirectory has its own README with the specific numbers, and
`CORRECTIONS.md` outranks every one of them where they disagree.
