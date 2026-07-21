# diagnostics/, the four-probe protocol

`dart_diagnostic.py` is a dependency-light module (numpy, scipy, scikit-learn)
that distinguishes a REAL method null from an IMPLEMENTATION ARTIFACT. Four
probes, each returning a verdict dict:

1. `translation_invariance_probe`, is a raw-vs-delta comparison unfair? For a
   translation-invariant distance (energy) it is not: E(P,Q) == E(P-c, Q-c).
2. `subsampling_power_probe`, is the null caused by an estimator too noisy at
   the cell budget used? Reports CV under subsampling.
3. `metric_blindspot_probe`, does a mean/scalar metric actually measure what it
   claims, or is it structurally blind to cell-level structure?
4. `magnitude_confound_probe`, is an apparent positive just the near-tautology
   that larger perturbations track the readout?

`protocol_validation.py` re-runs all four probes on the DART audit data and
checks they reproduce the reported audit verdicts.

```bash
PYTHONPATH=src python analysis/diagnostics/protocol_validation.py
```
