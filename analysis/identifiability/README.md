# identifiability/, Group I: can subpopulations be recovered?

- `subpop_identifiability_landscape.py`, 9 unsupervised clustering methods across
  529 real drugs. None reaches ARI > 0.15 (best median 0.106); silhouettes near zero.
- `identifiability_phase_diagram.py`, controlled bimodal mixture swept over source
  separation x cell budget. Only separation, not budget, lifts ARI; the real regime
  (separation ~1) stays unidentifiable at any budget.
- `signal_decode_run.py`, decodes what JUDGE's real (non-circular) signal encodes by
  comparing JUDGE-vs-mean drug picks against structural/target/MoA properties. The
  signal does not align with any measured drug property.
