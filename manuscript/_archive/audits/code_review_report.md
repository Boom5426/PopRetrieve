# DART — Code Review Report

**Date:** 2026-07-06
**Scope:** Full codebase correctness review + GitHub-standard polish, ahead of the
first substantive commit (only the scaffold commit `ddc5306` existed; the entire
Phase 2/3 body of work — exp08–17, new `src/` modules, `paper/` docs — was
uncommitted).
**Environment:** server `ssh:139.180.131.202`, repo `/data/boom/DART`, conda env
`Agent` (Python 3.11, torch 2.10, numpy 1.26, scipy 1.14, sklearn 1.7).
**Test status:** `python tests/run_tests.py` → **95 passed, 0 failed** (91 before
this review; +4 regression tests added here).

---

## 1. Headline

**Zero result-changing bugs** were found across the whole codebase (~10,800 LOC,
60 files). This review combined three passes:

1. a prior grounded review of the 14 core Phase-1/2 files (0 result-changing bugs,
   documented separately);
2. the exp16/17 gate-diagnosis work (which patched exp12 additively and re-ran it
   FULL, EXIT_0);
3. **this pass** — a grounded, parallel LLM correctness review (reasoning model,
   real numbered source spans) over the 16 previously-unreviewed core-logic
   modules, followed by line-by-line hand-adjudication of every flag.

All numerical results the manuscript relies on are therefore unaffected by this
review; the changes made are hardening, defensive guards, documentation, and repo
presentation.

---

## 2. Pass-2 correctness review (this session)

**Modules reviewed:** 16 core-logic modules
(retrieval: evaluation, tasks, rankers, bootstrap; data: population + 3 loaders;
benchmarks: oracle_utility, heterogeneous_retrieval_benchmark; baselines:
average_effect, nearest_neighbor, pca_latent; exp09_structure_diagnostics; utils).
**Clean:** 13 / 16.
**Findings:** 3, all MEDIUM-or-below, all in the
predict-then-rank baselines. Each was hand-verified against the real source and
against how `exp09` actually calls it.

| ID | File:Line | Reviewer sev. | Verdict | Result-changing? |
|---|---|---|---|---|
| P2-1 | `nearest_neighbor_predictor.py:75` | MEDIUM | **HARDENING (LOW)** | no |
| P2-2 | `nearest_neighbor_predictor.py:91` | MEDIUM | **FIX (LOW-impact, correctness)** | no |
| P2-3 | `average_effect_predictor.py:79` | MEDIUM | **FALSE POSITIVE** | no |

### Adjudication detail

**P2-1 — `src/baselines/nearest_neighbor_predictor.py:75` (_nearest_context)** — *HARDENING (LOW)*
- **Claim:** fallback `self._contexts[0]` ignores `exclude` when all contexts excluded
- **Adjudication:** Only fires if a SINGLE-context dataset is used with exclude=that context. exp09 carrier = 3-context SciPlex3; empirically all 188 drugs present in all 3 contexts, so best is never None. Real defensive gap, cannot fire in tested config. Cheap fix: return None + let caller handle.

**P2-2 — `src/baselines/nearest_neighbor_predictor.py:91` (predict)** — *FIX (LOW-impact, correctness)*
- **Claim:** fallback average over contexts does not exclude exclude_context -> can leak query's own context in leave-one-context-out
- **Adjudication:** Real: contradicts docstring 'force genuine cross-context transfer'. But fallback only runs when nearest context lacks the drug; empirically 0 SciPlex3 drugs are missing from any context, so it never fires in exp09 -> reported numbers unchanged. Worth fixing to make the LOCO guarantee airtight for future datasets with coverage gaps.

**P2-3 — `src/baselines/average_effect_predictor.py:79` (predict_population)** — *FALSE POSITIVE*
- **Claim:** reseeds identical noise per call -> synthetic populations share noise, artificially correlated
- **Adjudication:** exp09 passes seed=<per-query seed>, identical across candidates within a query. This is common-random-numbers: every candidate sees the SAME noise realization, so candidate differences come purely from delta (signal), not noise-draw luck. This REDUCES comparison variance and is the conservative/fairest design for exp09's mean-vs-DART contrast. Not a bug; independent reseeding would ADD irrelevant variance.

### Empirical guard on the exp09 invariant

Both `nearest_neighbor` findings (P2-1, P2-2) touch fallback paths that only fire
when a drug is missing from a context. This was checked against the data: **all
188 SciPlex3 drugs are present in all 3 contexts (A549 / K562 / MCF7)**, so the
fallback never fires in exp09. After applying the fixes, 120 `(excluded-context,
drug)` predictions were re-checked: **0 hit the changed fallback path**, i.e. the
fix is provably a no-op for exp09's configuration — **exp09's reported numbers are
unchanged.** The corrected behavior only activates for future datasets that have
genuine coverage gaps.

---

## 3. Fixes applied (all non-result-changing)

| # | File | Change | Why |
|---|---|---|---|
| 1 | `src/baselines/nearest_neighbor_predictor.py` | `_nearest_context` now returns `Optional[str]` (None when all contexts excluded) instead of silently returning `contexts[0]` | Degenerate single-context case could return the excluded context, violating the docstring's cross-context-transfer guarantee |
| 2 | `src/baselines/nearest_neighbor_predictor.py` | `predict` fallback average now filters out `exclude_context` | Airtight leave-one-context-out: fallback can no longer leak the held-out context's signature |
| 3 | `src/benchmarks/predictability.py` | `score_disagreement` NaN guard on constant ranking | `kendalltau` returns NaN when a ranking is constant; guard returns 0.0 instead of propagating NaN into gate features |
| 4 | `src/benchmarks/preference_conflict.py` | `standard_kendall_conflict` NaN guard | Same constant-column NaN, same guard |

**Regression tests added (+4, suite 91 → 95):**
- `test_nn_nearest_context_returns_none_when_all_excluded`
- `test_nn_predict_fallback_excludes_held_out_context`
- `test_standard_kendall_conflict_constant_column_is_finite`
- `test_score_disagreement_constant_ranking_is_finite`

---

## 4. Repo hygiene audit

- **Largest stageable file:** 476 KB (`results/exp11_hir_benchmark/phase_grid_method_performance.csv`) — far under GitHub's 50 MB warning. No `.pt` / `.npz` / `.h5ad` / `per_query_scores.csv` would be staged; `.gitignore` verified working (0 `__pycache__` staged).
- **Secrets scan:** CLEAN - no api keys/tokens/passwords in src/scripts/configs.
- **Hardcoded paths:** CLEAN - no /data/boom or /home/* absolute paths in src/*.py.

**Actions taken:**
- Added results/_*_backup/, results/_runlogs/, .venv_pred/ to .gitignore (excludes session scratch: _exp12_full_backup + runlogs)
- Added CONTRIBUTING.md (self-contained-package rule, reproducibility rule, honest-negatives rule, PR checklist)
- Added CITATION.cff (entity-style author, MIT, repo link)

**Flagged, deliberately not changed** (already public in `ddc5306`; not deleting published content in a hygiene pass):
- oracle/ (58 files) - already tracked/public in ddc5306; deliberate provenance snapshot w/ own README defending its role; NOT deleting already-published content in a hygiene pass
- docs/ (3 files: project_plan_v3.md, report_v1_zh.md, report_v2_zh.md) - already tracked/public; internal planning + zh reports; left as-is
- _merged_query_divergence.csv - IS written by exp16_gate_diagnosis.py, legitimate cached output, kept

---

## 5. README rewrite

The previous README (4960 B) covered only Phase 1 (exp01–07) and framed DART as
"global energy beats mean" — inconsistent with the current honest positioning.
The rewrite (9227 B):

- adopts the **probe** framing: DART exposes when objective-aligned proxy metrics
  create apparent gains that do not transfer to oracle-independent criteria;
- reports **both sides** with numbers pulled directly from the result CSVs — the
  objective-aligned positive (energy Hit@1 **0.837** vs mean-cosine = cmap-cosine
  **0.389**, an algebraic identity) **and** the oracle-independent null
  (minority-coverage gap tiny but divergence-monotone; MoA-nDCG null at every
  divergence stratum);
- adds popular-repo scaffolding: badges, table of contents, tested Quickstart,
  reproduce commands, repository map, an "how the evaluation avoids fooling
  itself" section, and citation.

Every path and command referenced in the README was verified to exist / run; the
Quickstart snippet was executed against the real `metrics.py` API.

---

## 6. Overall assessment

The codebase is **correct, tested, and reproducible**. It is honest about its
negative results by design (the audit machinery is built to resist circular
evaluation), and the presentation now matches that honesty. It is ready to
commit.

**Recommended follow-ups (optional, not blocking):**
- Consider whether `oracle/` (58-file provenance snapshot) and the internal
  `docs/*_zh.md` planning notes should remain in the public repo long-term.
- The two `nearest_neighbor` fallbacks are now correct but still untested on a
  real coverage-gap dataset (none exists in the current data); worth a note if
  such a dataset is added.
