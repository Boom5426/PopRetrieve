# PopRetrieve Package 1: control-reference sensitivity

## Status

Completed. This analysis tests the only retrieval settings in which the query and
candidate populations carry different matched-control means: the three SciPlex3
cross-line mixtures and the Frangieh within-gene contrasts. It does not rerun
controlled-mixture, partial-observation, GDSC2, or same-context RNA rankings.
Those paths use one common control translation for the compared populations, so
energy, RBF-MMD, sliced Wasserstein and fixed-label coverage are unchanged by
subtracting that common control.

The population arm is compared with the existing control-referenced mean-cosine
baseline. `population_minus_mean` is the population score's retrieval metric
minus the mean-cosine metric on the same query.

## Frozen run

```text
dataset: processed SciPlex3 and Frangieh inputs used by the project
SciPlex3: K562+A549, A549+MCF7, K562+MCF7
SciPlex3: 15 divergent drugs, alpha = 0.5, 0.6, 0.7, 0.8, 0.9, 10 seeds
Frangieh: IFNGR1, Control+IFNγ, Control+Co-culture, IFNγ+Co-culture, 10 seeds
candidate library: 43 candidates (one correct covers-both candidate)
cells: 200 per query/candidate population
population estimator: U for energy, RBF-MMD and coverage energy components
SW: 128 projections, fixed kernel projection seed as in the scorer
```

The exact run command was:

```bash
DIDR_DATA_ROOT=/absolute/path/to/data \
  python \
  analysis/audit/control_reference_sensitivity.py \
  --out results/audit/package1_raw_vs_control.csv \
  --sciplex3 /absolute/path/to/data/processed/sciplex3_all.pt \
  --frangieh /absolute/path/to/data/processed/frangieh_hvg.npz \
  --dataset both --n-seeds 10 --n-drugs 15 --n-total 200 \
  --n-distractors 40 --frangieh-perturbation IFNGR1
```

The batched audit implementation was checked against the scalar scorer on one
query for all five population methods in both arms. Candidate order was identical;
the largest absolute score difference was (1.5\times10^{-4}) for energy and
(1.2\times10^{-8}) for sliced Wasserstein.

## Results

Values are means over the listed queries. Each cell reports raw / referenced.
`ΔH1` and `ΔMRR` are population minus mean-cosine effects.

### SciPlex3 cross-line mixtures

| setting (n queries) | scorer | Hit@1 raw / ref | MRR raw / ref | ΔH1 raw / ref | ΔMRR raw / ref |
|---|---|---:|---:|---:|---:|
| K562+A549 (750) | energy | 0.9107 / 0.9080 | 0.9356 / 0.9342 | +0.4040 / +0.4013 | +0.2147 / +0.2134 |
| K562+A549 (750) | RBF-MMD | 0.9160 / 0.9160 | 0.9379 / 0.9379 | +0.4093 / +0.4093 | +0.2170 / +0.2170 |
| K562+A549 (750) | sliced Wasserstein | 0.7440 / 0.7387 | 0.8232 / 0.8201 | +0.2373 / +0.2320 | +0.1024 / +0.0993 |
| K562+A549 (750) | coverage-mean | 0.8413 / 0.8413 | 0.8863 / 0.8863 | +0.3347 / +0.3347 | +0.1655 / +0.1655 |
| K562+A549 (750) | coverage-worst | 0.8547 / 0.8547 | 0.8872 / 0.8872 | +0.3480 / +0.3480 | +0.1664 / +0.1664 |
| A549+MCF7 (750) | energy | 0.9533 / 0.9480 | 0.9743 / 0.9717 | +0.4240 / +0.4187 | +0.2188 / +0.2162 |
| A549+MCF7 (750) | RBF-MMD | 0.9573 / 0.9573 | 0.9766 / 0.9766 | +0.4280 / +0.4280 | +0.2211 / +0.2211 |
| A549+MCF7 (750) | sliced Wasserstein | 0.8640 / 0.8573 | 0.9130 / 0.9094 | +0.3347 / +0.3280 | +0.1575 / +0.1539 |
| A549+MCF7 (750) | coverage-mean | 0.8613 / 0.8613 | 0.9118 / 0.9118 | +0.3320 / +0.3320 | +0.1563 / +0.1563 |
| A549+MCF7 (750) | coverage-worst | 0.8960 / 0.8960 | 0.9296 / 0.9296 | +0.3667 / +0.3667 | +0.1742 / +0.1742 |
| K562+MCF7 (750) | energy | 0.8973 / 0.8960 | 0.9357 / 0.9347 | +0.5987 / +0.5973 | +0.3379 / +0.3369 |
| K562+MCF7 (750) | RBF-MMD | 0.9000 / 0.9000 | 0.9364 / 0.9364 | +0.6013 / +0.6013 | +0.3386 / +0.3386 |
| K562+MCF7 (750) | sliced Wasserstein | 0.8347 / 0.8320 | 0.8963 / 0.8949 | +0.5360 / +0.5333 | +0.2985 / +0.2971 |
| K562+MCF7 (750) | coverage-mean | 0.8480 / 0.8480 | 0.8981 / 0.8981 | +0.5493 / +0.5493 | +0.3003 / +0.3003 |
| K562+MCF7 (750) | coverage-worst | 0.8573 / 0.8573 | 0.9009 / 0.9009 | +0.5587 / +0.5587 | +0.3031 / +0.3031 |

Across all 2,250 cross-line queries, the primary energy result was Hit@1
0.9189 raw versus 0.9158 referenced, MRR 0.9478 versus 0.9462, and
population-minus-mean effects +0.4746 versus +0.4715 for Hit@1 and +0.2571
versus +0.2554 for MRR. RBF-MMD and both coverage limits were unchanged to the
reported precision. Sliced Wasserstein was Hit@1 0.8123 versus 0.8075 and MRR
0.8768 versus 0.8741; its effect remained positive in every setting.

### Frangieh IFNGR1 contrasts

| setting (n queries) | scorer | Hit@1 raw / ref | MRR raw / ref | ΔH1 raw / ref | ΔMRR raw / ref |
|---|---|---:|---:|---:|---:|
| Control+IFNγ (10) | energy | 0.8000 / 0.8000 | 0.9000 / 0.9000 | +0.6000 / +0.6000 | +0.3833 / +0.3833 |
| Control+IFNγ (10) | RBF-MMD | 0.5000 / 0.5000 | 0.7333 / 0.7333 | +0.3000 / +0.3000 | +0.2167 / +0.2167 |
| Control+IFNγ (10) | sliced Wasserstein | 0.4000 / 0.4000 | 0.7000 / 0.7000 | +0.2000 / +0.2000 | +0.1833 / +0.1833 |
| Control+IFNγ (10) | coverage-mean | 0.6000 / 0.6000 | 0.7833 / 0.7833 | +0.4000 / +0.4000 | +0.2667 / +0.2667 |
| Control+IFNγ (10) | coverage-worst | 0.3000 / 0.3000 | 0.6167 / 0.6167 | +0.1000 / +0.1000 | +0.1000 / +0.1000 |
| Control+Co-culture (10) | energy | 0.6000 / 0.6000 | 0.7833 / 0.7833 | +0.6000 / +0.6000 | +0.3667 / +0.3667 |
| Control+Co-culture (10) | RBF-MMD | 0.4000 / 0.4000 | 0.6417 / 0.6417 | +0.4000 / +0.4000 | +0.2250 / +0.2250 |
| Control+Co-culture (10) | sliced Wasserstein | 0.7000 / 0.7000 | 0.8167 / 0.8167 | +0.7000 / +0.7000 | +0.4000 / +0.4000 |
| Control+Co-culture (10) | coverage-mean | 0.7000 / 0.7000 | 0.8333 / 0.8333 | +0.7000 / +0.7000 | +0.4167 / +0.4167 |
| Control+Co-culture (10) | coverage-worst | 0.6000 / 0.6000 | 0.7667 / 0.7667 | +0.6000 / +0.6000 | +0.3500 / +0.3500 |
| IFNγ+Co-culture (10) | energy | 1.0000 / 1.0000 | 1.0000 / 1.0000 | +0.0000 / +0.0000 | +0.0000 / +0.0000 |
| IFNγ+Co-culture (10) | RBF-MMD | 1.0000 / 1.0000 | 1.0000 / 1.0000 | +0.0000 / +0.0000 | +0.0000 / +0.0000 |
| IFNγ+Co-culture (10) | sliced Wasserstein | 0.9000 / 0.9000 | 0.9500 / 0.9500 | -0.1000 / -0.1000 | -0.0500 / -0.0500 |
| IFNγ+Co-culture (10) | coverage-mean | 1.0000 / 1.0000 | 1.0000 / 1.0000 | +0.0000 / +0.0000 | +0.0000 / +0.0000 |
| IFNγ+Co-culture (10) | coverage-worst | 1.0000 / 1.0000 | 1.0000 / 1.0000 | +0.0000 / +0.0000 | +0.0000 / +0.0000 |

## Interpretation

No qualitative manuscript conclusion changes. Population methods remain above the
control-referenced mean-cosine baseline in the cross-line response-matching tasks,
and the differing-control sensitivity does not create or remove a population gain.
The small raw-versus-referenced differences are confined to settings in which the
single-context candidates enter the cross-context library; they do not support
attributing the observed gain to a different overall conclusion.

The following manuscript paths were not rerun because the relevant control shift is
common to query and candidate populations within the task: controlled SciPlex3
mixtures, partial-observation SciPlex3 rankings, the GDSC2 global energy rankings,
and the Frangieh RNA rankings evaluated against protein. Their raw and
control-referenced population distances are the same under the implemented
translation-invariant kernels (with labels held fixed for coverage).

## Machine-readable outputs

* `results/audit/package1_raw_vs_control.csv`: one row per setting, seed, scorer
  and reference arm.
* `results/audit/package1_raw_vs_control_summary.csv`: aggregate retrieval metrics.
* `results/audit/package1_raw_vs_control_qualitative.csv`: sign comparison for the
  population-minus-mean effects.
