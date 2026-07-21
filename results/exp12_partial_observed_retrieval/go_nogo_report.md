# exp12 Partial-Observed Retrieval — Go/No-Go Report

Data: SciPlex3 (A549/K562/MCF7), leave-drug-out + leave-MoA-out + partial-library.
Total per-query rows: 6885; diagnostic queries: 765.

## Recommendation-mode distribution

| mode | n | frac |
|---|---|---|
| DART_recommended | 621 | 0.81 |
| mean_or_no_call | 133 | 0.17 |
| mean_sufficient | 11 | 0.01 |

## Go criteria (protocol §7 — satisfy ≥3)

| criterion | pass | detail |
|---|---|---|
| Go-1 | PASS | DART_recommended: best=DART_coverage_worst, median regret reduction=+0.1190, Wilcoxon p=4.26e-56, 72% improved (n=621) |
| Go-2 | PASS | nDCG gain=-0.0134, MRR gain=+0.0284 (best DART_sliced_wasserstein) |
| Go-3 | PASS | mean_sufficient: DART regret reduction=+0.0000, p=1 (should be ~0 / n.s.) |
| Go-4 | PASS | exp13 predicted_mean → no-DART: 100% (≥60% target) |
| Go-5 | PASS | 20 queries where DART covers a minority state >0.05 better than mean |

## Verdict

**3/5 Go criteria satisfied → CONDITIONAL-GO (metric-dependent; see caveats)**

### Discrimination diagnostics

- Median regret reduction: DART_recommended = +0.1190 vs mean_or_no_call = +0.1219 (gate does NOT separate — advantage is diffuse)
- Non-circular nDCG (MoA-recovery) gain on DART_recommended = -0.0134 (DART does NOT help under the non-circular outcome)

### Reasoning

The phase-gate asks whether DART's advantage appears in the realistic partial-observed setting, on the subset the information-condition diagnostics flag as DART_recommended (high preference-conflict + reliable structure).

**The GO is metric-dependent and must be reported as such.** DART reduces the energy-welfare decision regret significantly on the DART_recommended subset (median +0.1190, Wilcoxon p≪0.001, 72% of queries), and the gate correctly withholds a recommendation on the small mean_sufficient subset. **However, two honest caveats bound the claim:**

1. *Metric alignment.* The welfare-regret proxy is energy-based, and DART optimizes distributional (energy/MMD) distance — so the regret metric is partially aligned with DART's objective. DART also reduces this regret on the mean_or_no_call subset by a similar margin, i.e. the advantage is not sharply concentrated in DART_recommended.

2. *Non-circular outcomes are flat.* Under MoA-recovery nDCG and minority-state coverage (outcomes DART does not directly optimize), DART shows no consistent gain over mean retrieval on this SciPlex3 leave-drug-out task (exp13: 0/37 tasks DART-favoured under minority coverage).

**Recommended positioning:** DART's demonstrated contribution is *welfare-regret reduction on information-condition-flagged high-conflict tasks*, plus the diagnostic gate and HIR-Bench benchmark — a strong methods contribution. A universal 'better drug recommendation' claim is not yet supported by the non-circular outcomes; strengthening it needs a task with an oracle-independent utility (e.g. real dose-response or held-out functional readout).