# class_c/, semi-real viability oracle (and its confound)

- `match_drugs_v2.py`, matches SciPlex3 drugs to GDSC dose-response (exact + substring).
- `class_c_experiment.py`, ranks candidates by DART energy vs mean cosine, scored
  against GDSC viability (AUC/IC50) as an external oracle.
- `class_c_magnitude_control_v2.py`, **the one to use**. Energy retrieval is
  **anti-correlated** with true potency (rho = **-0.520**, same sign in all three cell
  lines): the candidates most similar to the query are the *less potent* ones. A
  query-independent scalar that ranks by candidate response magnitude and performs no
  retrieval at all reaches **+0.692** and outranks energy on **103 of 103** queries.
  Energy *distance* tracks candidate magnitude (rho = +0.79), and magnitude predicts
  potency, so ranking nearest-first returns the weakest drugs.

- `class_c_experiment.py`, `class_c_magnitude_control.py`: **SUPERSEDED, do not quote.**
  They rank `score_energy` ascending, but it returns MINUS the energy distance (a
  similarity), so DART's top pick was the population *farthest* from the query while the
  mean baseline was ranked correctly. That inversion manufactured an apparent +0.52. They
  also pooled all four doses and pooled GDSC1 with GDSC2. See CORRECTIONS.md R14.
