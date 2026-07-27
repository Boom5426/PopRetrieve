> **SUPERSEDED IN PART, audited 2026-07-27.** This is a working document. It predates the July
> 2026 audit, which retracted or revised numbers this file may still quote, among them the
> "5.1x structure collapse" (R1), the MoA-nDCG statistics computed over 165 undefined sentinel
> values (R2), the Class A/B contrast that compared two different scorers (R4), the HIR-Bench
> predictability AUC of 0.640 (R11), the claim that no Class C metric was available (R14), and
> the "0 of 37 real-data tasks" count (R13). **Read [CORRECTIONS.md](../../CORRECTIONS.md) before quoting any
> number below**, and treat `manuscript/latex/EvalShift_manuscript.tex` as the authority for
> anything that reaches the paper. Where this file and CORRECTIONS.md disagree, CORRECTIONS.md
> is right.

# identifiability/, Group I: can subpopulations be recovered?

- `subpop_identifiability_landscape.py`, nine clustering *columns* over 529 **(cell line, drug)
  pairs** drawn from the study's 188-drug SciPlex3 panel. The nine columns are only **6-7 distinct
  algorithms** (`response_kmeans_k2` is bit-identical to `raw_kmeans_k2`; `bestk3/4/5` are one
  best-k method under three names), all centroid- or Gaussian-based, with no density or graph
  method tested. The "best median ARI 0.106" is a median over the **4 of 20 seeds** in which k=4
  won; the dense columns sit at 0.037-0.078 and the global maximum is 0.149. Silhouettes near
  zero. See CORRECTIONS.md R10 and R29 for both corrections.
- `identifiability_phase_diagram.py`, controlled bimodal mixture swept over source
  separation x cell budget. Only separation, not budget, lifts ARI; the real regime
  (separation ~1) stays unidentifiable at any budget.
- `signal_decode_run.py`, decodes what EvalShift's real (non-circular) signal encodes by
  comparing EvalShift-vs-mean drug picks against structural/target/MoA properties. The
  signal does not align with any measured drug property.
