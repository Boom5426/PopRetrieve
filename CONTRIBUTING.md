# Contributing to DART

Thanks for your interest. DART is a research codebase accompanying a methods
manuscript, so contributions that improve **reproducibility, correctness, and
clarity** are especially welcome.

## Ground rules

- **The `src/` package is self-contained.** It must not import from `oracle/`
  (the provenance snapshot) or from any external research project. New code in
  `src/` may depend only on the packages in `requirements.txt`.
- **Every reported number must stay reproducible.** If you touch a scorer,
  ranker, or experiment, re-run the relevant script and confirm
  `results/all_existing_results_recomputed.csv` still passes (35/35 within
  tolerance).
- **Be honest about negatives.** DART is framed as a *probe*, not a universally
  better method. Do not add framing that overstates where the distributional
  signal helps; keep the null / negative results (CD34+, MoA-nDCG) in view.

## Development setup

```bash
pip install -r requirements.txt
python tests/run_tests.py        # offline runner; `pytest tests/` also works
```

Place processed data under `data/processed/` as described in [DATA.md](DATA.md).
CUDA is optional (it accelerates the energy distance).

## Before opening a pull request

1. **Run the test suite** — `python tests/run_tests.py` must report all passing.
2. **Add a test** for any bug fix or new behavior (see `tests/` for the style;
   tests are plain `test_*` functions, no pytest fixtures required).
3. **Keep diffs focused.** One logical change per PR. Do not commit large data
   files, model weights, or `results/**/per_query_scores.csv` (all git-ignored).
4. **Explain the *why*** in the PR description, and note whether any reported
   number changed (it usually should not).

## Reporting issues

Please include: the command you ran, the expected vs. observed result, and your
environment (`python --version`, key package versions). A minimal reproducer is
worth a thousand words.
