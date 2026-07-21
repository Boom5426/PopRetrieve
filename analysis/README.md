# analysis/, post-hoc audit and upgrade experiments

This directory holds the analyses developed during the DART audit and upgrade
cycle (2026-07). They are organized by the question each one answers, and every
script resolves the repository root from its own location, so they run from a
checkout without editing paths:

```bash
PYTHONPATH=src python analysis/<category>/<script>.py
```

Outputs are written to `results/upgrade/`. Large inputs (GDSC dose-response
tables, the SciPlex3 tensor) are obtained separately, see `DATA.md`.

## Layout

| directory | question it answers | key outputs |
|-----------|--------------------|-------------|
| `diagnostics/` | Is a distributional method's null a REAL null or an implementation artifact? | `dart_diagnostic.py` (four-probe module), `protocol_validation.py` |
| `audit/` | Do the seven candidate objections to the null survive scrutiny? | delta-vs-raw, subsample power, minority-coverage blindspot, gate circularity, welfare proxy, end-to-end fix |
| `identifiability/` | Can subpopulation structure be recovered at all, and what does the real signal encode? | subpopulation-identifiability landscape, phase diagram, DART-vs-mean signal decode |
| `class_c/` | Does DART's ranking track a real viability oracle, or a response-magnitude confound? | GDSC drug matching, viability experiment, magnitude control |
| `hir_bench/` | Is retrieval failure predictable from observable features? | HIR-Bench predictability ROC |

## The headline finding

The audit confirmed that DART's oracle-independent null is a **real null**, not
an artifact: seven candidate objections were falsified, and the four confirmed
weaknesses all pointed the same direction (they had been *over*-crediting DART,
not under-crediting it). The `diagnostics/` four-probe protocol packages the
reusable core of that audit so the same test can be run on any distributional
retrieval method.

See the manuscript (kept local, not in this repo) for the full narrative; each
subdirectory has its own README with the specific numbers.
