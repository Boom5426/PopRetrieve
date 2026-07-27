> **SUPERSEDED IN PART, audited 2026-07-27.** This is a working document. It predates the July
> 2026 audit, which retracted or revised numbers this file may still quote, among them the
> "5.1x structure collapse" (R1), the MoA-nDCG statistics computed over 165 undefined sentinel
> values (R2), the Class A/B contrast that compared two different scorers (R4), the HIR-Bench
> predictability AUC of 0.640 (R11), the claim that no Class C metric was available (R14), and
> the "0 of 37 real-data tasks" count (R13). **Read [CORRECTIONS.md](../../CORRECTIONS.md) before quoting any
> number below**, and treat `manuscript/latex/EvalShift_manuscript.tex` as the authority for
> anything that reaches the paper. Where this file and CORRECTIONS.md disagree, CORRECTIONS.md
> is right.

# class_c/, semi-real viability oracle (and its confound)

- `match_drugs_v2.py`, matches SciPlex3 drugs to GDSC dose-response (exact + substring).
- `class_c_experiment.py`, ranks candidates by EvalShift energy vs mean cosine, scored
  against GDSC viability (AUC/IC50) as an external oracle.
- `class_c_functional_oracle.py`, **the one the paper uses.** The Class-C oracle is drug-drug
  *functional similarity*: the rank correlation between two compounds' GDSC2 dose-response AUC
  profiles across the 966 cell lines left after the three SciPlex3 lines are excluded, mean-centred
  per cell line so a drug's overall potency level cannot drive it. It is query-dependent, so a
  query-independent scalar cannot game it by construction. Both the centred and uncentred
  constructions are reported, because the ordering reverses between them (CORRECTIONS.md R23).
- `class_c_protein_oracle.py`, the pair of oracles built from the same proteins in the same cells
  and differing only in whether each is computed as a mean or as a distribution.
- `oracle_shape_test.py`, the oracle-shape result those two support.

- `class_c_magnitude_control_v2.py`: **SEMANTICALLY MISMATCHED ORACLE, do not quote its
  conclusion** (CORRECTIONS.md R15). Its numbers are arithmetically right and its interpretation is
  not: it scores a *similarity* retriever against *absolute* potency, so a correctly working
  retriever handed a weak query returns other weak drugs and is counted as failing. Both the
  negative correlation and the scalar's sweep below were close to preordained by that choice.
  Energy retrieval is
  **anti-correlated** with true potency (rho = **-0.520**, same sign in all three cell
  lines): the candidates most similar to the query are the *less potent* ones. A
  query-independent scalar that ranks by candidate response magnitude and performs no
  retrieval at all reaches **+0.692** and outranks energy on **103 of 103** queries.
  Energy *distance* tracks candidate magnitude (rho = +0.79), and magnitude predicts
  potency, so ranking nearest-first returns the weakest drugs.

- `class_c_experiment.py`, `class_c_magnitude_control.py`: **SUPERSEDED, do not quote.**
  They rank `score_energy` ascending, but it returns MINUS the energy distance (a
  similarity), so EvalShift's top pick was the population *farthest* from the query while the
  mean baseline was ranked correctly. That inversion manufactured an apparent +0.52. They
  also pooled all four doses and pooled GDSC1 with GDSC2. See CORRECTIONS.md R14.
