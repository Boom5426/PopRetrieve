# audit/, Phase 1-3 objection tests

Each script tests one candidate objection to EvalShift's oracle-independent null. All
seven objections were falsified or the confirmed weakness was shown to *over*-credit
EvalShift:

- `diag_delta_vs_raw.py`, delta-vs-raw asymmetry (energy is translation-invariant, rho=1.0).
- `diag_subsample_power.py`, power loss at the cell budget (energy CV at n=120 is 6.3%).
- `audit_minority_coverage.py`, the mean-based minority-coverage metric is structurally blind (rho=-0.19 vs cell-level).
- `audit_circularity.py`, gate circularity (boot_stability weight 0.40 is the real anti-correlation driver, rho=-0.421).
- `diag_welfare_circularity.py`, welfare-proxy circularity (63.5% of the gain is non-circular).
- `fix_validation_e2e.py`, end-to-end validation that the cell-level coverage fix does not rescue EvalShift (wins only 36.7%, p=0.99).
