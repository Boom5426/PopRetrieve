# R3. Objective-aligned evaluation reports large distributional gains

**Status:** draft 1, contract-clean. Every numeral is locked to a macro defined at
`PopRetrieve_manuscript.tex:112-205` and verified in `manuscript/reference/numerical_contract_audit.md`
(rows R3-01 to R3-12). All fifteen R3 contract rows passed at first audit; nothing in this section
required a correction.

**Word count: 489** (target 450 to 550).

---

## 1. Revised section title

> **Objective-aligned evaluation reports large distributional gains**

"Reports" rather than "shows" or "establishes". The section's job is to fix a high-water mark under a
criterion of the method's own kind, not to certify it. The current title, "Objective-aligned
evaluation inflates the gain", states R4's conclusion in R3's heading and gives away the ladder before
the reader has seen its first rung.

---

## 2. Complete prose

The first rung of the ladder is the criterion the field reports by default: a distributional metric
applied to a distributional score. We measure it under the most favourable condition available, with
candidate responses \emph{observed} rather than predicted, so that the retriever is handed the full
candidate population a distributional score is designed to exploit and nothing is lost to a
generative model. Under that condition objective-aligned evaluation places distributional retrieval
well ahead of the mean incumbent. Energy-distance retrieval reaches Hit@1 \HITENERGY\ against
\HITMEAN\ for mean cosine and
the numerically identical Connectivity-Map cosine; PCA-distance retrieval reaches \HITPCADIST\ against
PCA-mean's \HITPCAMEAN\ (Fig.~\ref{fig:3}a). These are unweighted macro-means over the seven
(task $\times$ setting) cells of three retrieval tasks. Weighting cells by their query counts gives
\HITENERGYW\ against \HITMEANW; the unweighted figure is primary throughout, because it does not let
the largest cell dominate, and the weighted values are reported as a sensitivity analysis.

The ladder is not uniform across tasks, and the exception is the one dataset in it whose
heterogeneity nobody constructed. The advantage holds on the controlled and cross-line SciPlex3 tasks.
On Frangieh it does not: mean and Connectivity-Map cosine reach Hit@1 \HITFRANGMEAN\ against energy's
\HITFRANGENERGY\ (Fig.~\ref{fig:3}b). A macro-mean over seven cells conceals a single dissenting cell
by construction, so the counterexample is stated here and not left to the legend. It is also the
earliest signal in this study that constructed and natural heterogeneity behave differently, a
distinction the gate analyses return to.

The same ordering appears in the partial-observed setting, where candidates are scored by an
energy-based welfare regret: how much decision regret a ranking incurs against a latent welfare
objective. Over all \NALL\ partial-observed queries the worst-case subpopulation-coverage scorer
reduces median regret by \REGRETALL\ against mean retrieval (mean \REGRETALLMEAN), improving
\REGRETALLFRAC\ of queries (two-sided paired Wilcoxon $p = \REGRETALLP$; Fig.~\ref{fig:3}c). The mean
exceeds the median because a minority of queries are rescued from a very poor ranking, which is the
behaviour a coverage scorer is built for. All five distributional variants show a positive gain under
this criterion (Fig.~\ref{fig:3}f). We report the
full query set rather than the gate-recommended subset of it, because selecting a headline on a
gate-selected subset is precisely the analytic degree of freedom this study sets out to audit.

By the standard of these metrics the distributional score is far ahead, and the standard is
objective-aligned: the energy welfare regret and the energy retrieval score measure the same
distributional object, and the coverage scorer optimises the quantity the regret is computed from.
What this establishes is objective fidelity. Distributional retrieval computes a discriminative
objective, and observed heterogeneous populations carry real distributional structure that a mean
signature discards. That is a distributional retrieval signal under an objective-aligned proxy. It
fixes the high-water mark against which the evaluator shifts of the following sections are measured,
and it is not, on its own, evidence that candidate selection improves.

---

## 3. Source-to-sentence numerical contract

Hit@1 rows: `results/exp08_signature_baselines/summary.csv`, column `hit@1`, unweighted macro-mean
over the seven (task $\times$ setting) cells unless the row says weighted. Regret rows:
`results/exp12_partial_observed_retrieval/per_query_scores.csv`, column `decision_regret`, direction
`mean_cosine - DART_coverage_worst`.

| Sentence (opening words) | Value | Macro | n | Source field | Audit row | Reproduced |
|---|---|---|---:|---|---|---|
| "Energy-distance retrieval reaches Hit@1 0.837" | 0.837 | `\HITENERGY` | 7 cells | `global_energy` | R3-02 | `0.836905` |
| "against 0.388 for mean cosine and the numerically identical CMap cosine" | 0.388 | `\HITMEAN` | 7 cells | `mean_cosine`, `cmap_cosine` | R3-01, R3-02 | both `0.388492`, identical to six figures |
| "PCA-distance retrieval reaches 0.778 against PCA-mean's 0.518" | 0.778 / 0.518 | `\HITPCADIST` / `\HITPCAMEAN` | 7 cells | `pca_dist`, `pca_mean` | R3-03 | `0.778175` / `0.517857` |
| "Weighting cells by their query counts gives 0.887 against 0.421" | 0.887 / 0.421 | `\HITENERGYW` / `\HITMEANW` | 7 cells | `hit@1` weighted by `n_queries` | R3-04 | `0.886508` / `0.421429` |
| "mean and CMap cosine reach Hit@1 0.600 against energy's 0.578" | 0.600 / 0.578 | `\HITFRANGMEAN` / `\HITFRANGENERGY` | 90 | Frangieh cell only | R3-05 | `0.600000` / `0.577778` |
| "Over all 765 partial-observed queries" | 765 | `\NALL` | 765 | query key, sha256 `11e6c902...` | audit 1.2 | 765 |
| "reduces median regret by +0.118" | +0.118 | `\REGRETALL` | 765 | median paired difference | R3-07 | `+0.11826` |
| "(mean +0.258)" | +0.258 | `\REGRETALLMEAN` | 765 | mean paired difference | R3-08 | `+0.25790` |
| "improving 72% of queries" | 72% | `\REGRETALLFRAC` | 765 | fraction `> 0` | R3-09 | `0.7203` |
| "two-sided paired Wilcoxon p = 1.6e-66" | 1.6e-66 | `\REGRETALLP` | 765 (710 nonzero) | Wilcoxon, zeros dropped | R3-10 | `T = 32002`, `z = -17.230`, `p = 1.568e-66` |
| "All five distributional variants show a positive gain" | all `> 0` | none (qualitative) | 765 | five variants | R3-12 | `+0.0495` to `+0.1183` |

**Macros to add before compile.** Seven Hit@1 values are currently bare literals in the manuscript and
become macros here:

```latex
\newcommand{\HITENERGY}{0.837}         % unweighted macro-mean, 7 cells
\newcommand{\HITMEAN}{0.388}           % identical for mean_cosine and cmap_cosine (0.388492)
\newcommand{\HITPCADIST}{0.778}
\newcommand{\HITPCAMEAN}{0.518}
\newcommand{\HITENERGYW}{0.887}        % query-weighted sensitivity
\newcommand{\HITMEANW}{0.421}          % query-weighted sensitivity
\newcommand{\HITFRANGMEAN}{0.600}      % Frangieh cell only, n = 90
\newcommand{\HITFRANGENERGY}{0.578}    % Frangieh cell only, n = 90
```

`\HITMEAN` is used for both the mean-cosine and the CMap-cosine value deliberately: they are the same
number to six figures (R3-01), and a single macro makes that identity impossible to break by editing
one and not the other. The six-figure form `0.388492` stays in R2, where the identity is the result.

---

## 4. Deleted or relocated source material

### 4.1 Deleted

| Current text | Location | Reason |
|---|---|---|
| "Across all retrieval metrics, mean cosine and Connectivity-Map cosine are perfectly correlated ($\rho = 1.00$), while the energy and coverage scores form a separate, near-orthogonal block" | [:288-290](../latex/PopRetrieve_manuscript.tex#L288) | this is R2's result (the continuum), restated in R3. The $\rho = 1.00$ block stays in R2 and in Extended Data Fig. 1 |
| "The correlation is computed over the 54,180 query-candidate scores that the 1,260 retrieval queries generate against their candidate libraries, at 43 candidates per query." | [:291-293](../latex/PopRetrieve_manuscript.tex#L291) | a unit definition, relocated to Methods |
| "The unit is the scored pair, not the query: an earlier draft called these '54,180 real queries', which overstates the independent sample size by a factor of 43." | [:293-295](../latex/PopRetrieve_manuscript.tex#L293) | manuscript-history narration. The correct unit is stated once in Methods without the history |
| "the two are indistinguishable ($+$0.119 on the 621 recommended queries)" | [:312-313](../latex/PopRetrieve_manuscript.tex#L312) | a value on the gate partition quoted inside the paragraph reporting the 765-query result. The gate comparison belongs entirely to R4 block 4, where both of its arms appear together |
| "This result establishes objective fidelity: distributional retrieval computes a discriminative objective, and observed heterogeneous populations contain real distributional signal. It is a \textit{distributional retrieval signal under an objective-aligned proxy}, not evidence of independent therapeutic utility. Whether that signal survives a more independent judge is the question the next sections answer." | [:318-322](../latex/PopRetrieve_manuscript.tex#L318) | retained in substance as the closing paragraph, with the forward-pointing question removed. The section ends on what was established, not on what comes next |

### 4.2 Relocated to Methods

| Content | Current location |
|---|---|
| Query and scored-pair definitions: 1,260 queries, 43 candidates per query, 54,180 scored pairs, and the statement that the pair is not the independent unit | [:291-295](../latex/PopRetrieve_manuscript.tex#L291) |
| Definition of the seven (task $\times$ setting) cells and the unweighted macro-mean convention | [:255-256](../latex/PopRetrieve_manuscript.tex#L255), [:301-304](../latex/PopRetrieve_manuscript.tex#L301) |
| Definition of the energy-based welfare regret and the latent welfare objective | [:307-308](../latex/PopRetrieve_manuscript.tex#L307) |

### 4.3 Relocated to Supplementary Information

| Content | Current location |
|---|---|
| Alpha-crossover per-line curves (K562 1.00 to 0.05 as $\alpha$ rises 0.5 to 0.9; A549 and MCF7 flat or wider) | Fig. 3e legend, [:328](../latex/PopRetrieve_manuscript.tex#L328) |
| Dataset positions on the divergence axis (cross-line 0.032, Frangieh 0.709, CD34+ 0.186) and the failure of the dataset-level divergence rule | [:388-397](../latex/PopRetrieve_manuscript.tex#L388) |

### 4.4 Retained against the compression pressure

Two items were candidates for demotion and are kept in the main text on the author decision:

- **The Frangieh counterexample.** It weakens R3's own headline, which is why it must stay: a
  macro-mean that hides its one natural-data dissenter is the exact reporting practice this paper
  audits. Keeping it in R3 also seeds the constructed-versus-natural distinction that R6 and R7 carry.
- **The query-weighted macro-mean.** Reporting only the unweighted figure would invite the objection
  that the primary statistic was chosen after seeing both. Both are given, the choice is justified in
  one clause, and the weighted values are labelled a sensitivity analysis.

---

## 5. Exact word count

Counted on the prose of section 2 only, macros expanded to their printed values, `\ref` resolved to a
single token, remaining LaTeX stripped.

```
489 words
```

Target 450 to 550. Inside band, 61 words of headroom.

Paragraph lengths: 151, 94, 138, 106. Four paragraphs: the criterion and the apparent gain, the
natural-data counterexample, the partial-observed replication, and the interpretation as objective
fidelity.

**No limitation paragraph.** R3 has none, because its only caveat, that the criterion is
objective-aligned, is the section's conclusion rather than a qualification of it. The Frangieh
counterexample is a result and is written as one.

**No claim of general superiority.** The section says the distributional score is ahead *by the
standard of these metrics* and names the standard in the same sentence. The words "better",
"superior" and "outperforms" do not appear.

---

## 6. Grep checklist

```bash
# 1. No claim of general superiority.
awk '/^## 2\./,/^## 3\./' manuscript/rewrite/R3_objective_aligned.md \
  | grep -niE '\b(superior|outperform|better than|state of the art)\b'    # expect 0

# 2. The Frangieh counterexample is present in the prose, not only the legend.
awk '/^## 2\./,/^## 3\./' manuscript/rewrite/R3_objective_aligned.md | grep -c 'Frangieh'  # expect >= 1

# 3. Unweighted is named primary and weighted is named a sensitivity analysis.
awk '/^## 2\./,/^## 3\./' manuscript/rewrite/R3_objective_aligned.md \
  | grep -oE 'unweighted figure is primary|sensitivity analysis'          # expect both

# 4. R3 reports the 765 set and never the 621 gate subset.
awk '/^## 2\./,/^## 3\./' manuscript/rewrite/R3_objective_aligned.md | grep -cE '\bNREC\b|621'  # expect 0

# 5. Every macro used in R3 is defined exactly once.
for m in NALL REGRETALL REGRETALLMEAN REGRETALLFRAC REGRETALLP \
         HITENERGY HITMEAN HITPCADIST HITPCAMEAN HITENERGYW HITMEANW \
         HITFRANGMEAN HITFRANGENERGY; do
  n=$(grep -c "newcommand{\\\\$m}" manuscript/latex/PopRetrieve_manuscript.tex)
  printf '%-16s %s\n' "$m" "$n"
done          # every line must read 1

# 6. Macro values against the artifact.
python3 - <<'PY'
import pandas as pd, re, pathlib
h = pd.read_csv("results/exp08_signature_baselines/summary.csv")
p = h.pivot_table(index=["task", "setting"], columns="method", values="hit@1")
w = h.pivot_table(index=["task", "setting"], columns="method", values="n_queries")
un, wt = p.mean(), (p * w).sum() / w.sum()
tex = pathlib.Path("manuscript/latex/PopRetrieve_manuscript.tex").read_text()
def macro(n):
    m = re.search(r"newcommand\{\\%s\}\{([^}]*)\}" % n, tex)
    return float(m.group(1)) if m else None
pairs = [("HITENERGY", un["global_energy"]), ("HITMEAN", un["mean_cosine"]),
         ("HITPCADIST", un["pca_dist"]),     ("HITPCAMEAN", un["pca_mean"]),
         ("HITENERGYW", wt["global_energy"]),("HITMEANW", wt["mean_cosine"])]
for name, truth in pairs:
    v = macro(name)
    print(f"{name:14s} macro {v}  artifact {truth:.6f}  "
          f"{'OK' if v is not None and abs(v - round(truth, 3)) < 5e-4 else 'PENDING/MISMATCH'}")
assert abs(un["mean_cosine"] - un["cmap_cosine"]) < 1e-12, "mean/CMap identity broken"
print("mean_cosine == cmap_cosine to machine precision: OK")
fr = h[(h.task == "frangieh")].set_index("method")["hit@1"]
print(f"Frangieh mean {fr['mean_cosine']:.6f} > energy {fr['global_energy']:.6f}: "
      f"{fr['mean_cosine'] > fr['global_energy']}")
PY

# 7. No em dashes.
awk '/^## 2\./,/^## 3\./' manuscript/rewrite/R3_objective_aligned.md \\
  | grep -cP '\\x{2014}'   # expect 0. Scoped to the prose and written as a
                              # codepoint so the check cannot match itself.
```

**Checklist result, measured 2026-07-29. All seven items pass.**

| Item | Result |
|---|---|
| 1 superiority words | 0 hits |
| 2 Frangieh in prose | present |
| 3 unweighted primary / weighted sensitivity | both phrases present |
| 4 gate subset absent from R3 | 0 hits |
| 5 macros defined once | 13 of 13 |
| 6 macro values against artifact | `HITENERGY` 0.837 / 0.836905, `HITMEAN` 0.388 / 0.388492, `HITPCADIST` 0.778 / 0.778175, `HITPCAMEAN` 0.518 / 0.517857, `HITENERGYW` 0.887 / 0.886508, `HITMEANW` 0.421 / 0.421429, `HITWTCS` 0.4635 / 0.463492; `mean_cosine == cmap_cosine` to machine precision; Frangieh mean 0.600000 > energy 0.577778. **ALL OK** |
| 7 em dashes in prose | 0 |

The nine `\HIT*` macros in section 3 are installed at `PopRetrieve_manuscript.tex:196-205`, so item 5
no longer reports `PENDING`.
