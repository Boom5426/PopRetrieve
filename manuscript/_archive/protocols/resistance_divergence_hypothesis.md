# Resistance-Divergence Hypothesis (exp15 — exploratory branch)

> **Status: exploratory side-branch.** This does **not** gate the Nature Methods
> main line. It asks whether DART's core quantity — perturbation-response
> *divergence* (population splitting rather than uniform shift) — carries
> biological signal about resistance/persistence-associated minority states.

## Hypothesis

When a perturbation drives a population to **diverge** into distinct response
subpopulations rather than shifting uniformly, the emergent **minority state** is
enriched for resistance/persistence-associated programs (drug-tolerant persister,
quiescence, immune-evasion). If so, response divergence — which DART's
distributional objective is uniquely sensitive to and mean retrieval is blind to —
is an early, *pre-treatment* marker of the subpopulation that will later dominate
under selective pressure.

```text
uniform response  →  no minority state       →  mean retrieval sufficient
divergent response →  distinct minority state →  minority may be a resistance precursor
                                                  →  DART-visible, mean-invisible
```

## Data and its limits

Only in-repo **Frangieh melanoma Perturb-CITE-seq** is used (CRISPR-KO × {Control,
IFNγ, Co-culture}, 2000 HVGs). This dataset supports the divergence-vs-program
question but has two hard limits:

1. **No drug timecourse / no post-treatment readout.** Frangieh is a single-snapshot
   CRISPR screen under immune pressure, not a drug-tolerance timecourse. Part B of
   the plan (divergence → post-treatment survival/expansion) therefore **cannot be
   tested** here — it is reported as a limitation, not a result. Testing it needs a
   drug-holiday / persister timecourse dataset (e.g. a PC9-osimertinib or
   melanoma-BRAFi timecourse), which is out of scope for this branch.
2. **Marker-panel coverage is IFN-biased.** The 2000 HVGs cover IFN-response (14/15)
   and antigen-presentation (7/12) well, but melanoma differentiation / EMT / stemness
   programs sparsely (1–2 genes each). Only adequately-covered programs are scored;
   the well-covered **quiescence** panel (MKI67/TOP2A/PCNA/CCNB1, inverted) is the
   most informative persister proxy available.

## What the experiment measures

- **Part A (data-supported):** per KO, response divergence = between-subpopulation
  variance ratio of the control-subtracted response; split into 2 subpopulations;
  score each marker program in the divergent minority vs the majority state using a
  common z-reference; correlate program enrichment with divergence, and compare
  high- vs low-divergence KOs (Mann–Whitney).
- **Part B (honest limit):** divergence → survival/expansion — **not evaluable** on
  Frangieh; documented above.
- **Part C (method-contrast):** for the highest-divergence KOs as queries, does the
  DART-energy-selected surrogate KO cover the resistance minority state better than
  the mean-cosine-selected surrogate?

## Results (FULL: IFNγ + Co-culture, 225→450 KO×context rows)

Divergent minority states are enriched (high- vs low-divergence, Mann–Whitney) for:

| program | corr(divergence, enrichment) | high−low Δ | p |
|---|---|---|---|
| **AXL_mesenchymal** | **+0.134** | +0.022 | 0.003 |
| IFN_response | +0.042 | +0.039 | 1.9e-6 |
| antigen_presentation | +0.037 | +0.015 | 0.044 |
| antigen_presentation_loss | −0.017 | −0.014 | 0.69 (n.s.) |
| quiescence | −0.127 | −0.071 | 7.7e-7 |

- **The AXL/mesenchymal program has the strongest monotonic link to response
  divergence** (correlation +0.134, p=0.003). AXL-high mesenchymal states are the
  canonical drug-tolerant / immunotherapy-resistant melanoma program, so this is the
  most biologically on-target positive: KOs that split the population most tend to
  produce an AXL-mesenchymal minority.
- **IFN-response and antigen-presentation** are also enriched in divergent minorities
  (p=1.9e-6, p=0.04), consistent with an immune-evasion-adjacent minority under IFNγ
  pressure.
- **Quiescence flips sign between the QUICK (IFNγ-only) and FULL (IFNγ+Co-culture)
  runs** — enriched in the IFNγ-only subset (p=2e-5) but *depleted* across both
  contexts (p=8e-7). This context-dependence is reported as-is and is **not** claimed
  as a robust persister signal; only the AXL/IFN/antigen-presentation direction is
  cross-context stable.
- **Part C (DART vs mean minority rescue) is weak/near-null**: DART-energy changes the
  selected surrogate KO in 14/16 high-divergence queries, but the minority-state
  coverage gain is marginal (mean ≈ +0.001; DART favoured in ~56% of queries). On a
  CRISPR-KO library where candidates are genetic perturbations (not drugs), DART's
  minority-rescue advantage is present in direction but not in magnitude.

## Interpretation and next step

The reproducible thread is **AXL-mesenchymal (and IFN/antigen-presentation)
enrichment in high-divergence minority states**: response divergence is not merely a
statistical property but tracks a biologically coherent, resistance-associated
minority program. That is a genuine, if modest, hypothesis-generating result. It does
**not** by itself justify a Nature Methods resistance claim, and Part C's near-null
means DART's *retrieval* advantage for resistance minorities is directional but not
demonstrated in magnitude on Frangieh.

To pursue this branch seriously would require a **drug-tolerance timecourse** with
pre/post readouts, so that divergence measured pre-treatment can be linked to the
subpopulation that expands post-treatment (Part B). Until then this remains an
exploratory hypothesis, kept deliberately separate from the main phase-gate.
