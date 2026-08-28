> **SUPERSEDED IN PART, audited 2026-07-27.** This is a working document. It predates the July
> 2026 audit, which retracted or revised numbers this file may still quote, among them the
> "5.1x structure collapse" (R1), the MoA-nDCG statistics computed over 165 undefined sentinel
> values (R2), the Class A/B contrast that compared two different scorers (R4), the HIR-Bench
> predictability AUC of 0.640 (R11), the claim that no Class C metric was available (R14), and
> the "0 of 37 real-data tasks" count (R13). **Read [CORRECTIONS.md](../../CORRECTIONS.md) before quoting any
> number below**, and treat `manuscript/latex/PopRetrieve_manuscript.tex` as the authority for
> anything that reaches the paper. Where this file and CORRECTIONS.md disagree, CORRECTIONS.md
> is right.

# Non-additive predictors: the falsification test for Gate 1

## Why this directory exists

The paper's Gate-1 claim has two halves, and only one of them was ever supported.

**The algebra** is not in question: a predictor that adds a *single* delta vector to *every* cell
gives its two subpopulations identical responses, so their induced cosine is exactly 1 and the
divergence a distributional score could exploit is exactly zero. That is a property of a model
class and no amount of training removes it.

**The empirical claim** was circular. The three predictors originally tested were:

| predictor | structure |
|---|---|
| `average_effect` | one delta added in gene space |
| `nearest_neighbor` | a transferred delta, added to every cell |
| `scgen` (`backend=cpa_linear`) | **an in-repo PCA + additive latent delta + LINEAR decoder** |

All three are additive *by construction*. Finding that they induce no divergence demonstrated the
algebra and surveyed nothing. Worse, the third was labelled "scGen" while being neither scGen nor
CPA, and the manuscript concluded from it that *current perturbation predictors are additive*.
**We built an additive model, called it scGen, and then concluded that scGen is additive.** That is
the self-fulfilling structure the paper indicts in others. See `CORRECTIONS.md`, R17.

This directory runs the models that could actually falsify Gate 1.

## The ladder

Each rung escapes additivity by a *different* mechanism. That is the point: the ladder isolates
**which property matters**, rather than just showing that "we ran some modern models".

| predictor | escapes additivity by | Gate-1 prediction |
|---|---|---|
| `average_effect` | (nothing: control) | cos = 1 exactly |
| `linear_latent` | (nothing: control) | cos = 1 exactly |
| `scgen_real` | a **nonlinear decoder** (published `scgen` 2.1.1) | does decoder curvature alone open it? |
| `cpa_real` | **drug/dose/covariate conditioning** (published `cpa-tools` 0.8.1) | does explicit conditioning open it? |
| `ot_map` | a **per-cell displacement** from an optimal-transport coupling | maximally non-additive |

`scgen_real` reproduces `scgen.SCGEN.predict`'s arithmetic verbatim (`_scgen.py:155-164`):
`delta = mean(latent of treated) - mean(latent of control)`, then `z_pred = z_ctrl + delta`, then a
**nonlinear** decode. It is latent-additive like `linear_latent`, so the only thing that changes is
decoder curvature. That isolation is what makes the comparison informative.

## Two safeguards, both of which changed the answer

**1. The Gate-1 metric is measured twice.** Assigning subpopulations by nearest mode, as a scorer
must, an *additive* predictor scores about 0.43, not the 1.000 the algebra demands. The gap is not
divergence, it is **assignment error**, which means Gate-1 divergence and Gate-2 assignment error
are confounded in that number. So we also run each predictor *separately on each context's control
cells*, giving a partition that is true by construction:

* `cos_ORACLE` isolates **Gate 1 alone**. An additive predictor *must* land at ~1.000 here, and the
  script asserts it. If it does not, the measurement is broken and no conclusion may be drawn.
* `cos_ESTIMATED` is what a retrieval layer actually gets: **Gate 1 and Gate 2 compounded**.

**2. Every predictor must prove it learned anything.** An undertrained generative model emits a
near-constant population, which has no differential response and scores *exactly like a perfectly
trained additive model*. We would then report "even CPA cannot induce differential response" when
the truth was "we did not train CPA". Given that CPA runs at ~28 min/epoch on all 276k SciPlex3
cells even on an RTX 4090, that failure mode is not hypothetical. Before any Gate-1 number is read,
each predictor must reproduce the *direction* of the observed mean response:

    cos(predicted mean delta, TRUE mean delta)

A model near 0 is reported as **VOID**, not as a finding. CPA is fitted on a stratified subsample
(`--cpa-max-cells`, default 300 cells per drug x context) so that it can actually be trained.

**No silent fallbacks.** If `scgen` or `cpa-tools` is missing, `nonadditive_predictors.py` raises.
It does not substitute a linear model. A silent fallback is what produced the error this directory
exists to correct.

## Environment

`scgen` and `cpa-tools` pin an older `scvi-tools` and cannot coexist with the main analysis
environment, so they live in their own. The main `Agent` environment is left untouched: it produced
every other number in the paper and must stay reproducible.

```bash
conda create -y -n dartcpa python=3.10
conda activate dartcpa
export PYTHONNOUSERSITE=1                 # a user site-packages dir will shadow and break this

pip install cpa-tools pot
pip install "pyarrow==14.0.2"             # ray (a cpa dep) breaks on pyarrow >= 15
pip install --no-deps "git+https://github.com/theislab/scgen.git"
                                          # PyPI scgen 2.1.0 imports scvi._compat.Literal, which
                                          # scvi-tools 0.20.3 turned into a shim that RAISES.
                                          # The git version (2.1.1) works on the modern stack.
python -c "import scgen, cpa, ot; print(scgen.__version__, cpa.CPA, ot.__version__)"
```

## Run

```bash
conda activate dartcpa
export PYTHONNOUSERSITE=1

# Gate 1: does any non-additive predictor induce differential response?
PYTHONPATH=src python analysis/predictors/exp_nonadditive_gate1.py \
    --n-drugs 10 --n-seeds 5 --epochs 100

# Part B: does that divergence buy a retrieval advantage? Same harness, same queries,
# same scorers as the incumbent predictors; only the predictor list changes.
# NOTE: exp09_predict_then_rank.py has NO --nonadditive flag. `nonadditive` is a keyword
# argument of run(), not a CLI option (see its argparse block), so the command below is the
# only way to reach that code path from a shell. Audited 2026-07-27.
PYTHONPATH=src python analysis/predictors/exp_nonadditive_gate1.py
```

## What decides the framework

Gate 1 alone decides nothing. The two-gate account predicts that **divergence should buy retrieval
gain**. If a predictor that genuinely induces differential response *still* yields no distributional
advantage, the account is wrong at Gate 1 and we say so. Both outcomes are publishable and neither
was predetermined.

Outputs: `results/exp14_nonadditive_predictors/gate1_nonadditive.{csv,json}`.
