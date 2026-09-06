# Fig. 2 magnitude control: the verdict

Produced before any Figure 2 panel was touched, which is the point: the two numbers below decide
whether Figure 2 tells a three-tier gain story or a decomposition story, and the panels are drawn
after the decision rather than before it.

Source: `results/exp08_signature_baselines/` re-run 2026-09-03 with `POPRETRIEVE_ESTIMATOR=u` and
with `mean_l2` added to `retrieval.rankers.SCORERS`. Nine scorers, seven task-by-setting cells,
54,180 query-candidate pairs. Correlation matrix rebuilt by
[`figures/source_data/build_metric_correlation.py`](../../figures/source_data/build_metric_correlation.py),
which did not exist before today.

---

## Question 1: does the old family assertion still hold?

**No. It fails, and it fails by a wide margin.**

`fig2a._load` asserts that every population-family scorer sits above every mean-family scorer on
macro-average Hit@1. With a magnitude-aware mean scorer in the panel:

| Scorer | Family | Hit@1 | MRR | nDCG@10 |
|---|---|---:|---:|---:|
| `global_energy` | population | **0.8357** | 0.9009 | 0.9206 |
| **`mean_l2`** | **mean** | **0.7877** | 0.8748 | 0.9021 |
| `pca_dist` | population | 0.7782 | 0.8610 | 0.8919 |
| `coverage_mean` | population | 0.7488 | 0.8428 | 0.8748 |
| `coverage_worst` | population | 0.7468 | 0.8399 | 0.8712 |
| `pca_mean` | mean | 0.5179 | 0.7233 | 0.7875 |
| `cmap_wtcs` | mean | 0.4635 | 0.6901 | 0.7629 |
| `cmap_cosine` | mean | 0.3885 | 0.6686 | 0.7523 |
| `mean_cosine` | mean | 0.3885 | 0.6686 | 0.7523 |

Lowest population scorer 0.7468; highest mean scorer **0.7877**. `mean_l2` beats **three of the
four** population scorers. Only the energy distance stays above it.

The assertion is not repaired and the grouping is not restored. The separation it protected was a
property of which mean scorer was in the panel, not of the two representation families.

## The three-tier decomposition, which replaces it

| Level | Scorer | Hit@1 | Step |
|---|---|---:|---:|
| direction only | `mean_cosine` | 0.3885 | |
| + magnitude | `mean_l2` | 0.7877 | **+0.3992** |
| + distribution | `global_energy` | 0.8357 | **+0.0480** |

**89% of the apparent population advantage in this panel is response magnitude.** The distributional
residue is +0.0480 Hit@1, real but an eighth of the step below it.

This is a larger magnitude share than Phase A found on intervention retrieval, where it was 66% of
a +0.0303 MRR gain ([03](03_ORACLE_RETRIEVAL_RESULTS.md)). The two are not in conflict: they are
different tasks, different metrics and different candidate libraries. What is common to both is the
direction and the order of magnitude of the correction.

### Per task and setting, so the macro-mean is not doing the work

| Task | Setting | cosine | mean L2 | energy | L2 − cosine | energy − L2 |
|---|---|---:|---:|---:|---:|---:|
| controlled | A549 | 0.2667 | 0.9333 | 0.9333 | +0.6667 | **0.0000** |
| controlled | K562 | 0.1333 | 0.6333 | 0.7000 | +0.5000 | +0.0667 |
| controlled | MCF7 | 0.4667 | 0.8667 | 0.9000 | +0.4000 | +0.0333 |
| cross-line | A549+MCF7 | 0.5306 | 0.8389 | 0.9556 | +0.3083 | +0.1167 |
| cross-line | K562+A549 | 0.4417 | 0.8000 | 0.8861 | +0.3583 | +0.0861 |
| cross-line | K562+MCF7 | 0.2806 | 0.8306 | 0.8972 | +0.5500 | +0.0667 |
| Frangieh | Control+IFNγ | 0.6000 | 0.6111 | 0.5778 | +0.0111 | **−0.0333** |

The magnitude step is large in six of seven cells and near zero on Frangieh. The distributional
step is positive in five, exactly zero in one and **negative in one**, which is the same Frangieh
cell where mean cosine was already the best scorer in the published version.

---

## Question 2: how much of the cross-family separation was magnitude?

**Almost all of it.**

| Pair | Spearman over 54,180 query-candidate pairs |
|---|---:|
| ρ(`mean_cosine`, `global_energy`) | **0.0596** |
| ρ(`mean_l2`, `global_energy`) | **0.8007** |
| **Δρ** | **+0.7412** |

The 0.06 is the number behind the claim that the mean family and the population family rank
candidates by different information. Swap the mean scorer for one that keeps magnitude and the
correlation goes to 0.80.

It is systematic, not a property of the energy distance alone:

| Population scorer | ρ with `mean_cosine` | ρ with `mean_l2` |
|---|---:|---:|
| `global_energy` | 0.060 | **0.801** |
| `pca_dist` | 0.107 | **0.861** |
| `coverage_mean` | 0.010 | **0.682** |
| `coverage_worst` | 0.005 | **0.685** |

And the two mean scorers barely agree with each other: ρ(`mean_cosine`, `mean_l2`) = **0.198**.

### What the matrix actually splits into

Not "mean family" against "population family". Read by correlation, the nine scorers fall into:

- **direction-carrying**: `mean_cosine`, `cmap_cosine` (ρ = 1.000 with it, as before), `cmap_wtcs`
  (0.850), `pca_mean` (0.961)
- **magnitude-carrying**: `mean_l2`, `global_energy`, `pca_dist`, `coverage_mean`, `coverage_worst`,
  which correlate 0.68 to 0.97 with each other

`mean_l2` sits with the population scorers, not with the mean scorers it shares a representation
with. **The axis the matrix separates on is what the scorer keeps, not what it is computed from.**

---

## Consequences, stated before the panels are drawn

1. **`fig2a`'s family assertion must go, and the grouping with it.** The panel is rebuilt on the
   three-tier hierarchy with `mean_cosine`, `mean_l2` and `global_energy` as primary and the other
   six as lighter secondary markers. Restoring the old grouping by dropping `mean_l2` would be
   choosing the control that gives the desired picture.

2. **`fig2f`'s framing changes.** It is no longer evidence that two representation families use
   different information. It is evidence that **direction-only scoring is what is different**, and
   the panel's row order becomes direction, magnitude, population rather than family-blocked.

3. **The deck build is blocked until `fig2a` is rebuilt.** `build_all.py` will now fail on that
   assertion. That is the gate doing its job and it is left to fail rather than being disabled.

4. **The Figure 2 title survives the rule set for it, narrowly.** The rule was to keep "beyond
   direction alone" only if a principal population scorer retains a stable positive gain over
   `mean_l2`. It does: +0.0480 Hit@1 macro, positive in five of seven cells, and +0.0102 MRR
   [+0.0065, +0.0145] on the independent Phase A benchmark.

   It is still the weaker of the two candidate titles, because `mean_l2` is also "beyond direction
   alone" and it takes 89% of the step. The accurate options are:

   - *Response magnitude, not population structure, explains most information gained beyond
     directional signatures*: leads with the correction, which is what the data lead with;
   - *Perturbation information beyond directional signatures is mostly magnitude, with a smaller
     distributional residue*: states both terms in the order of their size.

   Recommended: the second. The decision is the author's.

---

## What was NOT done

No panel was drawn or edited. No figure was rebuilt. No number outside `exp08` was touched. The
Phase 6 predictor branch remains closed.
