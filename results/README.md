# Results

Selected experiment snapshots are grouped by task:

| Directory | Contents |
| --- | --- |
| `exp08_signature_baselines/` | Signature-baseline summaries |
| `exp09_predict_then_rank/` | Prediction and retrieval summaries |
| `exp11_hir_benchmark/` | Synthetic benchmark summaries |
| `exp12_partial_observed_retrieval/` | Partial-observation summaries and per-query scores |
| `exp13_real_data_projection/` | Exploratory transfer results |
| `exp18_dose_mismatch/` | SciPlex3 re-identification across matched and mismatched doses: per-query ranks, dose-pair summaries, primary contrasts with drug-cluster bootstrap intervals and run provenance |
| `exp20_decision_level/` | Top-ranked candidate in GDSC2 and mechanism-of-action retrieval: per-query tables, summaries with query-drug cluster bootstrap intervals, changed top-1 counts, reproduction checks, run provenance and, in `inputs/`, the GDSC2 candidate scores |
| `phase2_transition/` | Observed-to-predicted intervention-retrieval summaries; `bottleneck/` holds the per-query table and the regression below the mean-cosine ceiling. `eligibility/` holds the task definition (held-out cell lines, candidate library, query eligibility). `covariance_control/` holds the four Gaussian optimal-transport arms with reproduction checks, steps, contrasts and provenance. `phase_b_p5/delta_vs_reference.csv` is the reference run that `exp21_covariance_control.py` checks the `ot_map` arm against |

The root [`README.md`](../README.md) lists commands for the released package experiments. Snapshots include earlier experimental settings; the accompanying manuscript and its Supplementary material specify the final protocols and reported values. The release covers selected experiments and results. For Tahoe-100M it includes the eligibility audit and the leave-one-cell-line-out prediction driver in `src/experiments/phase2_transition/`. Complete figure source data and the ZhaoSims2021 and GDSC2 analysis drivers are not included. The GDSC2 candidate scores used by the decision-level evaluation are in `exp20_decision_level/inputs/`.
