# Retracted outputs

Files here are kept for provenance only. **Nothing may cite a number from them**, and no figure,
table or manuscript sentence reads them. They live in this directory rather than being deleted so
that the ledger entries which retract them still point at something.

## `class_c_viability.csv`

Written by `analysis/class_c/class_c_experiment.py`, which carries a SUPERSEDED banner. Retracted
by `CORRECTIONS.md` R14a.

The script ranks `retrieval.metrics.score_energy` ascending. That function returns MINUS the energy
distance, i.e. a similarity, so the population scorer's rank-1 candidate in this file is the
population **farthest** from the query, while the mean-cosine baseline in the same script is ranked
correctly. The signature is visible in the file itself: `dart_top1_drug` is effectively
query-independent, naming Panobinostat (LBH589) in 142 of its 152 rows, against 27 to 32 distinct
picks for `mean_top1_drug`.

The file also pools all four doses (the rest of the study uses 10 uM) and pools GDSC1 with GDSC2,
which are different platforms with no common AUC scale.

It is easy to mistake this for a finished decision-level analysis, because its schema is exactly
the one such an analysis would have (`dart_top1_drug`, `dart_top1_auc`, `mean_top1_drug`,
`mean_top1_auc`, `most_potent_drug`). The apparent effect it contains is the sign error.

Use `analysis/class_c/class_c_magnitude_control_v2.py` and
`results/upgrade/class_c_functional_oracle.csv` instead.
