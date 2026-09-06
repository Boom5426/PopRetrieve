# 09. Where population information is lost

From `results/phase2_transition/synthesis/oracle_to_prediction.csv`. Phase A and Phase B are paired
query by query: the same source cells, the same sublibrary split and the same target cells, so for
every query both `dMRR_oracle` and `dMRR_predicted` exist and the plan's four cases can be counted
rather than argued.

`dMRR` throughout is `energy` minus `mean_cosine`, averaged over the five seeds of each query.

## The four cases, per predictor, over 3,992 queries

| Predictor | Mean `dMRR` oracle | Mean `dMRR` predicted | I: neither | II: oracle only | III: both | IV: predicted only | Retained fraction |
|---|---:|---:|---:|---:|---:|---:|---:|
| `average_effect` | +0.0303 | -0.0356 | 2,894 | 546 | 209 | 343 | **-1.17** |
| `linear_latent` | +0.0303 | -0.0341 | 2,849 | 527 | 228 | 388 | -1.13 |
| `nearest_context` | +0.0303 | -0.3159 | 2,917 | 523 | 232 | 320 | -10.41 |
| `nearest_context_cells` | +0.0303 | -0.3399 | 2,979 | 576 | 179 | 258 | -11.20 |
| **`ot_map`** | +0.0303 | **+0.0027** | 2,072 | 305 | 450 | 1,165 | **+0.09** |

## Reading it

**Case I dominates.** For 71% to 75% of queries neither the oracle nor the predictor shows a
population gain, for every predictor except `ot_map`, where the share is 52%. That is not a failure of prediction: taken on its own, the oracle
gains nothing on 81% of queries (77% tie exactly), because the mean route already ranks the true
drug first. Any account of this project that describes population information as broadly useful has
to survive the fact that on four fifths of a 3,992-query benchmark it is not usable even with
perfect knowledge.

**Case II is the plan's forward-predictor bottleneck, and it is real but not the main story.** For
`average_effect`, 546 queries have an oracle gain that prediction does not deliver. Against 209 in
case III, that is a 2.6 to 1 loss.

**The retained fraction is negative for every additive predictor.** The oracle gain is not merely
lost, it reverses: `average_effect` turns +0.0303 into -0.0356. Plan section 14 anticipated a
retained fraction between zero and one. A negative one means the correct description is not "the
predictor loses the population signal" but "the predictor manufactures a population signal that is
wrong, and the distributional scorer believes it". The mechanism is in
[04](04_LOCO_PREDICTED_RETRIEVAL.md): an additive predictor's candidate population is the vehicle
population translated by an average-over-43-lines signature, so both its shape and its magnitude are
wrong in ways the energy distance is sensitive to and the cosine is not.

**`ot_map` retains 9% of the oracle gain**, the only predictor with a positive retained fraction,
and has by far the largest case III count (450). It also has 1,165 case IV queries, gains where the
oracle had none, which plan section 14 marks as suspect. They are not noise: `ot_map`'s absolute MRR
is 0.665 on the mean route against the oracle's 0.945, so it has enormous headroom, and by the
headroom result in [08](08_THREE_GATE_ANALYSIS.md) a poor ranker leaves room for a distributional
score to help on queries where the oracle's excellent mean ranker left none. Case IV here is a
symptom of a weak baseline, not of a discovery.

## The answer to the question this decomposition was built to ask

> Where is the population information lost?

Not in one place. In order of size:

1. **It mostly was not there.** Three quarters of queries have no oracle-level population gain,
   because magnitude-aware mean matching already ranks the true drug first. This is a decision-
   relevance limit, and it is the largest term.
2. **What is there is two thirds magnitude.** Of the +0.0303 oracle gain, +0.0201 is recovered by
   `mean_l2`, a mean-only scorer ([03](03_ORACLE_RETRIEVAL_RESULTS.md)). Only +0.0102 is genuinely
   distributional.
3. **The forward predictor destroys the remainder and then some.** Every additive predictor turns
   the residual gain into a loss, because its predicted population has a shape it never modelled and
   a magnitude borrowed from other cell lines.

Plan section 15's cases do not map cleanly onto this. It is not Case A, since the oracle gain exists.
It is not Case B either, since prediction does not merely fail to deliver the gain, it reverses it.
The verdict in [10](10_FINAL_VERDICT.md) says what follows.
