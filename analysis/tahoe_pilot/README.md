# Tahoe-100M: the three conditions, re-measured on unconstructed material

## Why this exists

Every gate statistic in the manuscript rests on one of two thin foundations:

| condition | evidence before this | weakness |
|---|---|---|
| Gate 1, differential response | mixtures we assembled (induced cosine 0.014-0.044) and 17 patient-drug pairs (median 0.566) | one is our own construction |
| Gate 2, recoverability | one constructed K562 mixture, and 36 glioblastoma splits | 30 of the 36 splits come from a single patient |
| Gate 3, decision relevance | 18 within-patient drug pairs, Spearman +0.878 | 15 of the 18 come from patient PW030; no p-value is quotable |

Tahoe-100M plate 3 is a **complete 50 cell line x 93 compound grid**, one dose per compound, a
`DMSO_TF` vehicle arm in every line, 4,158,278 cells, median 648 cells per condition, with a
cell-cycle call on every cell. Nobody pipetted two populations together: the within-line
heterogeneity is intrinsic cell state.

**It is not tissue, and it is not used to argue relevance.** It is used for sample size. The
manuscript's claims about what matters therapeutically continue to rest on the patient data.

## What is pre-specified, before any result was looked at

- **Representation.** The 2,304 highly variable genes in log1p space, exactly as the released
  preprocessed matrix ships them. Nothing refitted, rescaled or reselected.
- **Partition for Gates 1 and 3.** Cell-cycle phase (G1 vs G2M, S dropped as intermediate), and
  separately a `k`-means `k=2` partition fitted on each line's **control** cells only, with treated
  cells assigned to the nearest control centroid. The second is a property of untreated state and
  is fixed before any treated cell is seen, so it cannot be tuned to the response it measures.
  Both are reported everywhere; neither is selected after the fact.
- **Partition for Gate 2.** Drug identity, not phase. Phase is derived *from* expression by marker
  scoring, so asking a probe to recover it from expression is partly circular, which is the failure
  mode this project exists to criticise. Drug identity is external: it is which well the cell came
  from. This also makes the test the same construct as the manuscript's K562 benchmark and its
  tumour test, so the three numbers are comparable.
- **Baselines.** Each subpopulation's response is its mean minus the mean of the
  **same-subpopulation** control cells, so a baseline difference between subpopulations cannot
  enter the response (the error recorded as `CORRECTIONS.md` R28 and R30).
- **Minimum counts.** 50 cells in each of the four arms for Gates 1 and 3; 100 cells per arm for
  Gate 2. Every exclusion is counted and the resulting bias is measured rather than assumed away.
- **Direction predicted in advance.** If Gate 3 binds, the majority response should already rank
  the minority response in most contexts. Contexts where it does **not** are where a distributional
  score should pay off, which is a falsifiable positive prediction rather than another null.
- Seed 0 throughout.

## The scripts

| script | what it does |
|---|---|
| `tahoe_gate_pilot.py` | Gate 1 (induced response cosine), Gate 3 (first pass), Gate 2 (`k`-means arm) |
| `tahoe_gate3_disjoint.py` | Gate 3 on **disjoint** cell sets, under both partitions |
| `tahoe_gate2_clusterers.py` | Gate 2 re-scored across the manuscript's full clusterer panel |
| `tahoe_summary_numbers.py` | derives every Tahoe number quoted in the paper from the CSVs above |

```bash
H=<path>/plate3_filt_Vevo_Tahoe100M_WServicesFrom_ParseGigalab_preprocessed_cpu.h5ad
python tahoe_gate_pilot.py       --h5ad $H --out ../../results/tahoe_pilot
python tahoe_gate3_disjoint.py   --h5ad $H --out ../../results/tahoe_pilot/disjoint
python tahoe_gate2_clusterers.py --h5ad $H --pairs ../../results/tahoe_pilot/gate2_per_pair.csv \
                                 --out ../../results/tahoe_pilot/g2panel
python tahoe_summary_numbers.py                       # writes manuscript_numbers.json
```

`tahoe_gate2_clusterers.py` needs `scanpy`, `igraph` and `leidenalg` for the Leiden arm; the other
three need only numpy/scipy/pandas/scikit-learn/anndata.

## Two corrections this analysis produced

**The first-pass Gate 3 statistic shared cells between the two quantities it correlated.** The mean
signature contains the compartment whose response it is being asked to rank (26% here), so part of
the correlation is arithmetic. `tahoe_gate3_disjoint.py` is the fix, and it costs 0.064 of rho
(0.905 -> 0.841).

**The same flaw was then found in the manuscript's own premise correlation**, where the overlap is
larger (the malignant compartment is half of the tissue mean signature by construction): `CORRECTIONS.md` R42, and `analysis/natural/zhao_premise_disjoint.py`. The published
+0.878 becomes **+0.835** on disjoint compartments. Nothing is retracted; the number moves.

**The first Gate 2 pass was not like-for-like either.** It scored the unsupervised arm with
`k`-means alone and compared its gap against a tumour number whose unsupervised arm is the best of
four methods. Re-scored across the same panel the gap falls from 0.183 to 0.157, a small change,
because no method family rescues the partition here.

## Results

| | manuscript | Tahoe plate 3 |
|---|---|---|
| Gate 1, induced cosine | constructed 0.014-0.044; tissue 0.566 | median **0.739** over 3,630 conditions; only **0.11%** as divergent as the mixtures |
| Gate 2, ceiling / unsup / gap | 0.923 / 0.777 / **0.117** (36 splits) | 0.853 / 0.611 / **0.157** (960 pairs, 48 of 48 lines positive) |
| Gate 3, disjoint | **0.835** (18 pairs) | **0.841** (cell cycle) and **0.778** (cell state); **2 of 45** contexts below 0.5 |

Gate 1 and Gate 3 correlate across contexts at Spearman +0.620 within the cell-cycle partition
(`R^2` 0.385), so they share some variance and are not the same condition.

## Limits

1. **These are cell lines.** Their heterogeneity is unconstructed, which is the property the
   argument needs, but a cell line is not a tumour.
2. **One plate of fourteen**, 93 of the 380 compounds in the resource.
3. **Both partitions are coarse two-way splits of cell state**, not the persister or
   resistant-clone axis that motivates the work. What is measured is whether *a* real subpopulation
   structure behaves as the conditions predict, not whether *that* one does.
4. **Which contexts show an open Gate 3 depends on the partition.** The two agree at the extremes,
   and the same two cell lines are the most open under both, but their rankings agree only
   moderately (Spearman 0.466). Gate 3 can flag a handful of contexts; it cannot rank them finely
   until the partition is fixed in advance.
5. **The exclusion rule is mildly adverse.** Dropping conditions whose subpopulation arm falls
   below 50 cells preferentially removes cell-cycle-arresting compounds, which do respond more
   divergently. Measured: Spearman +0.077 between a compound's coverage and its cosine, and the
   median moves from 0.739 to 0.740 on well-covered compounds alone. Real, and negligible.

**No retrieval was run on this dataset.** There is no Hit@k, no regret and no Class-A, Class-B or
Class-C comparison derived from it. It enters the paper only as a larger measurement of the three
conditions.

## Data

Tahoe-100M is released under CC0 by Vevo Therapeutics and the Arc Institute, and is distributed
through the Arc Virtual Cell Atlas and Hugging Face (`tahoebio/Tahoe-100M`). Zhang *et al.* 2025,
[10.1101/2025.02.20.639398](https://doi.org/10.1101/2025.02.20.639398). See [`../../DATA.md`](../../DATA.md).
