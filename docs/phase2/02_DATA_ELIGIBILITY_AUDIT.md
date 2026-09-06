# 02. Data eligibility audit: Tahoe-100M plate 3

Produced by [`analysis/phase2_transition/audit_eligibility.py`](../../analysis/phase2_transition/audit_eligibility.py),
run 2026-09-02. Tables in `results/phase2_transition/eligibility/`. No model was fitted and no
expression value was read: every number here is a count taken from `obs`, so nothing in this
audit can have been steered by a downstream result.

## Input

| | |
|---|---|
| File | `plate3_filt_Vevo_Tahoe100M_WServicesFrom_ParseGigalab_preprocessed_cpu.h5ad` |
| Size | 5,858,821,682 bytes |
| sha256 | `dfca387b6d7e35e49a841ac708be8ad151227317d98302cf91a44dc69daff6bb` |
| Shape | 4,158,278 cells x 2,304 genes, log1p |
| Plate | `plate3` (single plate, verified) |
| Vehicle | `DMSO_TF` |

## The grid

50 cell lines x 92 candidate compounds = 4,600 conditions. **All 4,600 are present.** The grid is
complete; nothing is missing, and every exclusion below is a cell-count exclusion, not an absence.

`obs['drug']` has 93 categories. The 93rd is the vehicle. No compound maps to more than one
`drugname_drugconc`, so plate 3 is one dose per compound and no dose pooling occurs anywhere.

## Eligibility outcome

| Quantity | Count |
|---|---:|
| Grid conditions | 4,600 |
| Conditions present | 4,600 |
| **Eligible queries** | **3,992** |
| Eligible with at least 200 treated cells (full-size query) | 3,791 (95.0%) |
| Eligible with at least 400 treated cells (full-size query and oracle bank) | 3,143 (78.7%) |
| Eligible admitting a sublibrary-disjoint split | 3,992 (100%) |
| Eligible admitting a sample-disjoint split | 88 (2.2%) |
| **Usable contexts** | **44 of 50** |

Eligible queries per usable context: minimum 80, median 91, maximum 92.
Eligible queries per candidate compound: minimum 23, median 44, maximum 44.

Treated cells per eligible condition: minimum 101, first quartile 445, median 754, third quartile
1,295, maximum 7,701.

Vehicle cells per usable context: minimum 342, median 1,611, maximum 3,386.

## Exclusions, each counted once

Reasons are evaluated in a fixed order and only the first is recorded, so the two counts partition
the 608 excluded conditions exactly.

| Reason | Conditions | Meaning |
|---|---:|---|
| `context_control_too_few` | 552 | the cell line's vehicle arm has fewer than 200 cells, so the whole context is dropped |
| `treated_too_few` | 56 | the condition has fewer than 100 treated cells |
| `condition_absent` | 0 | none: the grid is complete |

**Six contexts dropped on the vehicle arm**, with their vehicle cell counts:

| Cell line | Vehicle cells |
|---|---:|
| NCI-H596 | 27 |
| NCI-H2122 | 37 |
| SW 1271 | 102 |
| CHP-212 | 150 |
| SW 1088 | 156 |
| NCI-H661 | 161 |

Each drops all 92 of its conditions, which is where 552 of the 608 exclusions come from. Note that
these six are dropped for a property of their vehicle arm alone, decided before any response was
computed, so this is not a selection on response.

**Fifty-six conditions dropped on the treated arm**, spread over 25 contexts and 16 compounds,
with 9 to 99 cells (median 73.5). No compound is dropped from the library because of this; only the
affected queries are dropped, as the plan requires.

### Sensitivity of the one threshold the plan left open

| Vehicle floor | Usable contexts | Eligible queries |
|---:|---:|---:|
| 100 cells | 48 | 4,139 |
| **200 cells (frozen)** | **44** | **3,992** |

The 200-cell floor costs 4 contexts and 147 queries and buys a source population of identical size
in every context. The 100-cell variant is pre-registered as a sensitivity analysis in
[01](01_TRANSITION_TASK_FREEZE.md) section 6, not as a fallback to be chosen later.

## Replicate-label structure, and why the oracle split uses sublibraries

The plan prefers a batch-disjoint oracle split where a replicate label exists. Plate 3 has two
candidate labels and the audit measured both rather than assuming either.

| Label | Values | Structure | Usable as a within-condition split? |
|---|---:|---|---|
| `sample` | 96 | exactly 1 drug per sample, up to 50 cell lines per sample | **No.** It is nested inside the drug axis, so it separates drugs, not two halves of one condition. |
| `sublibrary` | 105 | median 105 per condition, median 7 cells per (condition, sublibrary) | **Yes**, for all 3,992 eligible queries. |

`sample` being nested in drug is a fact about the assay design, not a defect: Tahoe pools cell
lines and demultiplexes them, so one well is one drug across many lines. It does mean that any
claim of a "batch-disjoint" oracle split based on `sample` would be false, which is why the audit
checked it.

The frozen choice is therefore a seeded sublibrary-disjoint split-half, which is cell-disjoint and
additionally shares no library preparation between the two halves.

## What this audit does not establish

It fixes pools and sizes. It says nothing about whether any of these queries carries recoverable
population information, which is the question Phase A exists to answer. It also does not resolve
the MoA annotation gap recorded in [01](01_TRANSITION_TASK_FREEZE.md) section 12: plate 3's `obs`
carries no MoA or target column, so `MoA-nDCG@10` cannot be computed from the released file alone.
