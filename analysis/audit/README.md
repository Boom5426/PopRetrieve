> **SUPERSEDED IN PART, audited 2026-07-27.** This is a working document. It predates the July
> 2026 audit, which retracted or revised numbers this file may still quote, among them the
> "5.1x structure collapse" (R1), the MoA-nDCG statistics computed over 165 undefined sentinel
> values (R2), the Class A/B contrast that compared two different scorers (R4), the HIR-Bench
> predictability AUC of 0.640 (R11), the claim that no Class C metric was available (R14), and
> the "0 of 37 real-data tasks" count (R13). **Read [CORRECTIONS.md](../../CORRECTIONS.md) before quoting any
> number below**, and treat `manuscript/latex/PopRetrieve_manuscript.tex` as the authority for
> anything that reaches the paper. Where this file and CORRECTIONS.md disagree, CORRECTIONS.md
> is right.

# audit/, Phase 1-3 objection tests

Each script tests one candidate objection to PopRetrieve's oracle-independent null. All
seven objections were falsified or the confirmed weakness was shown to *over*-credit
PopRetrieve:

- `diag_delta_vs_raw.py`, delta-vs-raw asymmetry (energy is translation-invariant, rho=1.0).
- `diag_subsample_power.py`, power loss at the cell budget (energy CV at n=120 is 3.8%; the 6.3%
  this line used to quote is the CV of the same-drug self-distance, a different quantity in a
  different CSV, CORRECTIONS.md R12).
- `audit_minority_coverage.py`, the mean-based minority-coverage metric is structurally blind (rho=-0.19 vs cell-level).
- `audit_circularity.py`, gate circularity (boot_stability weight 0.40 is the real anti-correlation driver, rho=-0.421).
- `diag_welfare_circularity.py`, welfare-proxy circularity (63.5% of the gain is non-circular).
- `fix_validation_e2e.py`, end-to-end validation that the cell-level coverage fix does not rescue PopRetrieve (wins only 36.7%, p=0.99).
