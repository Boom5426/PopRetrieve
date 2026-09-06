# Phase II: transition-to-intervention retrieval

Execution of
[`docs/PopRetrieve_PhaseII_Transition_to_Intervention_Retrieval_Frozen_Plan.md`](../PopRetrieve_PhaseII_Transition_to_Intervention_Retrieval_Frozen_Plan.md)
on Tahoe-100M plate 3. Read [10](10_FINAL_VERDICT.md) first if you read only one.

The task: given a held-out cell line's vehicle cells and a desired treated population, rank all 92
plate-3 compounds by how well each is predicted to carry one to the other. Leave-one-cell-line-out,
44 contexts, 3,992 queries, 5 seeds.

| Document | What it settles |
|---|---|
| [01 Task freeze](01_TRANSITION_TASK_FREEZE.md) | the frozen task, pools, split, thresholds and metrics |
| [02 Eligibility audit](02_DATA_ELIGIBILITY_AUDIT.md) | which contexts and queries are in, and why 6 lines are out |
| [03 Phase A, oracle ceiling](03_ORACLE_RETRIEVAL_RESULTS.md) | with perfect candidate outcomes, population information gains +0.030 MRR, two thirds of it magnitude |
| [04 Phase B, LOCO prediction](04_LOCO_PREDICTED_RETRIEVAL.md) | after prediction the gain reverses; the best system is the average effect scored by mean cosine, MRR 0.888 |
| [05 Gate 1](05_DIFFERENTIAL_RESPONSE_AUDIT.md) | observed differential response, and why `1 - cos` is confounded with effect size |
| [06 Gate 2](06_RECOVERABILITY_AUDIT.md) | supervised 0.80 against unsupervised 0.555: an algorithm-limited regime |
| [07 Gate 3](07_DECISION_RELEVANCE_AUDIT.md) | decision relevance as flips, not correlations |
| [08 Three gates together](08_THREE_GATE_ANALYSIS.md) | the framework's predicted regime holds 5 queries and gains nothing; headroom explains the gain |
| [09 Oracle to prediction](09_ORACLE_TO_PREDICTION_DECOMPOSITION.md) | where the population information goes |
| [10 Final verdict](10_FINAL_VERDICT.md) | the four questions, answered |

## Post-Phase-II repair track

Phase-II left two measurement problems that had to be fixed before anything else moved. These
documents carry the repairs and the reanalysis they forced; where they contradict 01 to 10, they
win, and the contradicted paragraph carries a dated correction.

| Document | What it settles |
|---|---|
| [P0 Claim dependency matrix](P0_CLAIM_DEPENDENCY_MATRIX.md) | which panel moves when a scorer or a statistic changes; 19 of 40 panels are estimator-sensitive |
| [P1 Estimator audit](P1_ESTIMATOR_AUDIT.md) | the V-statistic's bias is worth a 0.184 sd mean shift at 50 cells; U-statistic energy and MMD implemented and tested |
| [P2 Legacy re-run](P2_LEGACY_RERUN.md) | every affected published number, recomputed under both estimators |
| [P3 Interaction statistic](P3_INTERACTION_STATISTIC.md) | `1 - cos` retired; a cross-fitted drug-by-state interaction that passes five pre-specified checks |
| [P4 Bottleneck decomposition](P4_BOTTLENECK_DECOMPOSITION.md) | the headroom result was a ceiling artefact; the repaired interaction still does not locate population gain |
| [P5 State-conditioned predictor](P5_STATE_CONDITIONED_PREDICTOR.md) | the one permitted non-additive predictor: passes both entry gates, does not close the gap |
| **[Post-Phase-II verdict](POP_RETRIEVE_POST_PHASEII_VERDICT.md)** | **the five questions, answered; read this one** |

## Reissue track

The manuscript is edited from these two, not from memory of which run produced what.

| Document | What it settles |
|---|---|
| **[Post-repair master results](POST_REPAIR_MASTER_RESULTS.md)** | **every reissued number, in four categories; the single source of truth** |
| [P6 Retiring `1 - cos`](P6_COS_RETIREMENT.md) | every use classified; the two load-bearing numbers recomputed against a matched null |
| **[Fig. 2 magnitude control](FIG2_MAGNITUDE_CONTROL_VERDICT.md)** | **the family assertion fails; 89% of the panel's population advantage is magnitude, and rho with the energy distance goes 0.06 to 0.80** |

## Reproducing

Code in [`analysis/phase2_transition/`](../../analysis/phase2_transition/), results in
`results/phase2_transition/`. The plate is not redistributable; see [`DATA.md`](../../DATA.md).
Each phase reads the frozen pools rather than recomputing them, so the pools cannot drift.

```bash
H=/path/to/plate3_filt_Vevo_Tahoe100M_WServicesFrom_ParseGigalab_preprocessed_cpu.h5ad
R=results/phase2_transition
python analysis/phase2_transition/audit_eligibility.py --h5ad $H --out $R/eligibility
python analysis/phase2_transition/phase_a_oracle.py   --h5ad $H --freeze-dir $R/eligibility --out $R/phase_a
python analysis/phase2_transition/phase_b_loco.py     --h5ad $H --freeze-dir $R/eligibility --out $R/phase_b
python analysis/phase2_transition/phase_c_gates.py    --h5ad $H --freeze-dir $R/eligibility --out $R/phase_c
python analysis/phase2_transition/phase_d_synthesis.py --phase-a $R/phase_a --phase-b $R/phase_b \
                                                       --phase-c $R/phase_c --out $R/synthesis
# the repair track
python analysis/estimator_audit/estimator_bias_table.py --out results/estimator_audit
POPRETRIEVE_ESTIMATOR=v bash analysis/estimator_audit/run_legacy_suite.sh   # in one checkout
POPRETRIEVE_ESTIMATOR=u bash analysis/estimator_audit/run_legacy_suite.sh   # in another
python analysis/phase2_transition/gate1_interaction.py --h5ad $H --freeze-dir $R/eligibility \
                                                       --out $R/gate1_interaction
python analysis/phase2_transition/phase_e_bottleneck.py --phase-a $R/phase_a --phase-b $R/phase_b \
       --phase-c $R/phase_c --gate1 $R/gate1_interaction --out $R/bottleneck
```

Runtimes on one RTX 4090 with 124 GB of RAM: 30 s, 183 s, 688 s, 1,055 s, 4 s. Phase A and Phase B
draw every random quantity from generators keyed by purpose rather than by call order, so they are
paired cell for cell and the decomposition in [09](09_ORACLE_TO_PREDICTION_DECOMPOSITION.md) is a
per-query comparison rather than an average-to-average one.

The two large per-ranking dumps are stored gzipped (`per_query.csv.gz`); pandas reads them directly.
