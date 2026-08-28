# R5. The statistical form of an external criterion can reverse the preferred method

**Status:** draft 1, contract-clean. Every numeral below is locked to a macro defined at
`PopRetrieve_manuscript.tex:112-205` and verified in `manuscript/reference/numerical_contract_audit.md`
(rows R5-01 to R5-06). One value, the Frangieh cell count, is deliberately absent; see section 4.

**Word count: 544** (target 500 to 600).

---

## 1. Revised section title

> **The statistical form of an external criterion can reverse the preferred method**

Rejected alternatives and why: "Oracle shape not biology decides which method wins" (the current
title) asserts a dichotomy the gate analyses in R6 and R7 contradict, and "decides" overstates a
single controlled comparison. "An external oracle's shape selects the winner" reads as a claim about
oracles in general rather than about this experiment. The chosen title states what was demonstrated
and bounds it with "can".

---

## 2. Complete prose

A second external readout is available for this retrieval task, and taken at face value it
contradicts the first. Frangieh Perturb-CITE-seq measures \PROTMARKERS\ surface proteins, after four
isotype controls are excluded as background rather than phenotype, in the same cells whose RNA the
retrieval scores read. Protein and transcriptome are joined barcode by barcode, so this criterion
needs none of the cross-assay compound matching the GDSC readout requires, and no scorer sees it.
Scored against it, the mean signature beats energy retrieval, \SHAPEMEANORACLEMEAN\ against
\SHAPEMEANORACLEENERGY, in each of the three immune conditions.

The two criteria differ in construction as well as in verdict. The protein criterion is the cosine
between two knockouts' \emph{mean} protein deltas, so it collapses the protein readout to a mean, and
the mean-cosine RNA scorer computes that same statistic in the other modality. A criterion that
discards within-population variation is structurally matched to a scorer that discards it too, and
energy retrieval is being graded on a quantity from which the object it compares has been removed.
Whether that structural match, rather than the biology, produces the verdict is directly testable.

We therefore rebuilt the criterion from the same cells and the same proteins twice, changing only its
statistical form (Fig.~\ref{fig:5}; Methods). One version is the mean cosine above. The other is the
energy distance between the two knockouts' protein-response cell clouds, each referred to that
condition's control cells so that both versions measure response and not baseline identity. The two
RNA rankings under test are byte-identical across the two columns. Nothing about the scorers, the
cells, the proteins or the queries changes.

The preferred method swaps. Under the mean-shaped criterion the incumbent leads
(\SHAPEMEANORACLEMEAN\ against \SHAPEMEANORACLEENERGY); under the distribution-shaped criterion the
distributional score leads, and by a wider margin (\SHAPEDISTORACLEENERGY\ against
\SHAPEDISTORACLEMEAN). The reversal holds independently in each immune condition, Control, IFN$\gamma$
and Co-culture, at $n = \SHAPENCTRL$, \SHAPENIFN\ and \SHAPENCO\ of \SHAPEN\ queries.

A magnitude channel does not account for the swap on its own. An energy distance tracks a candidate's
own response magnitude ($\rho = \ENERGYCANDMAG$), and both distributional objects here are energy distances,
so a magnitude-to-magnitude coupling could in principle produce the reversal with no distribution
ever being compared. It reproduces part of it: the magnitude-matching scalar, which compares no
distributions, climbs from \SHAPEMAGMEAN\ to \SHAPEMAGDIST\ as the criterion turns distributional.
Energy nonetheless leads that scalar by \SHAPEEDGEDIST\ under the distributional criterion against
\SHAPEEDGEMEAN\ under the mean-shaped one, so a component of the swap survives the control.

What this establishes concerns the evaluator rather than therapeutic value. These protein
measurements carry both mean-level and distribution-level structure, and each is legible to the
criterion built in its own shape. The experiment shows that a criterion which is external,
independent and invisible to every scorer can still select the winner by its own statistical form. It
does not show which of the two representations is the more useful basis for a decision about a drug,
because no functional or survival endpoint enters it, and both criteria are molecular readouts one
layer removed from any outcome a patient experiences. Two criteria built from the same proteins in
the same cells reaching opposite conclusions bounds how far an external readout on its own can settle
the question.

---

## 3. Source-to-sentence numerical contract

| Sentence (opening words) | Value | Macro | Source file | Source field | Audit row | Reproduced |
|---|---|---|---|---|---|---|
| "measures \PROTMARKERS\ surface proteins" | 20 | `\PROTMARKERS` | `analysis/class_c/oracle_shape_test.py:67` (`ISOTYPES`), `class_c_protein_oracle.py:16` | 24 measured minus 4 isotype controls | new, see 4.2 | 24 - 4 = 20 |
| "the mean signature beats energy retrieval" | +0.242 / +0.146 | `\SHAPEMEANORACLEMEAN` / `\SHAPEMEANORACLEENERGY` | `results/upgrade/oracle_shape_test.json` | `mean_vs_oracleMEAN`, `energy_vs_oracleMEAN` | R5-01 | `0.242099` / `0.146191` |
| "the distributional score leads, and by a wider margin" | +0.529 / +0.334 | `\SHAPEDISTORACLEENERGY` / `\SHAPEDISTORACLEMEAN` | same | `energy_vs_oracleDIST`, `mean_vs_oracleDIST` | R5-02 | `0.529107` / `0.333988` |
| "The reversal holds independently in each immune condition" | flips in 3 of 3 | none (qualitative) | same | `per_condition.*.flips` | R5-03 | Control, IFN$\gamma$, Co-culture all `true` |
| "at $n = 213$, 227 and 219 of 659 queries" | 213 / 227 / 219 / 659 | `\SHAPENCTRL` / `\SHAPENIFN` / `\SHAPENCO` / `\SHAPEN` | same | `per_condition.*.n`, `n_queries` | R5-04 | 213 + 227 + 219 = 659 |
| "tracks a candidate's own response magnitude" | +0.791 | `\ENERGYCANDMAG` | `results/upgrade/class_c_magnitude_control_v2.json` | `energydist_vs_candmag_rho_median` | R4-29 | `0.790985` |
| "climbs from +0.125 to +0.352" | +0.125 / +0.352 | `\SHAPEMAGMEAN` / `\SHAPEMAGDIST` | `results/upgrade/oracle_shape_test.json` | `magmatch_vs_oracleMEAN`, `magmatch_vs_oracleDIST` | R5-05 | `0.124653` / `0.352353` |
| "leads that scalar by +0.177 ... against +0.022" | +0.177 / +0.022 | `\SHAPEEDGEDIST` / `\SHAPEEDGEMEAN` | same | `magnitude_confound.*` | R5-06 | `0.176754` / `0.021538` |

**`\ENERGYCANDMAG` is installed** (`+0.791`). It was a bare literal in the existing R4 and SI text as
well, so defining it removes three literals, not one.

---

## 4. Deleted or relocated source material

### 4.1 Deleted from the section

| Current text | Location | Reason |
|---|---|---|
| "It is something we did not anticipate and consider the sharpest result in this paper" | [:574](../latex/PopRetrieve_manuscript.tex#L574) | author-centred discovery narration; also one of three competing "central result" markers in the current draft |
| "A field that validates distributional methods against distributional readouts, and mean-based methods against mean readouts, will find each vindicated, and neither finding will be about biology." | [:576-578](../latex/PopRetrieve_manuscript.tex#L576) | relocated to Discussion, evaluator-robustness control. It appears near-verbatim at [:1229](../latex/PopRetrieve_manuscript.tex#L1229); the two collapse into one instance there |
| "That is the mirror image of the Class-A alignment this paper is about, arising now between two \emph{external} criteria" | [:559](../latex/PopRetrieve_manuscript.tex#L559) | the comparison is now carried by the structural argument in paragraph 2 without the self-reference |
| "Whether that makes it a real advantage or an unfalsifiable one is the question this paper leaves open, and we prefer to leave it open than to answer it with a criterion of our own choosing." | [:588-590](../latex/PopRetrieve_manuscript.tex#L588) | replaced by the A-4 formulation: the analysis does not determine which representation is more useful for an external decision |
| "This is not circularity in the Class-A sense of a method grading its own objective" | [:573](../latex/PopRetrieve_manuscript.tex#L573) | negative definition ("not X but Y"); paragraph 6 states positively what the experiment does establish |
| "the same 218,331 cells" | [:549](../latex/PopRetrieve_manuscript.tex#L549) | **provenance failure, see 4.2** |

### 4.2 The cell count is withheld, not merely moved. U-2 resolved and re-opened.

The audit flagged "20 surface proteins in the same 218,331 cells" as unverified. Tracing it produced a
worse finding than expected, and the number is now **blocked**:

- `analysis/class_c/class_c_protein_oracle.py:85` records that the **protein file has 218,331 rows and
  the cached RNA tensor has 218,023**, and that the row orders do not correspond.
- `figures/source_data/ed1_dataset_scale.csv` line 3, which backs the paper's own Extended Data
  Fig. 1a, reports Frangieh at **218,023** cells. **The main text and Extended Data Fig. 1 currently
  disagree with each other.**
- Both `oracle_shape_test.py` and `class_c_protein_oracle.py` join **by barcode** and analyse only the
  intersection, so the analysis unit is smaller than either file and equals neither 218,331 nor
  218,023. The joined count is printed to stdout (`oracle_shape_test.py:106`) and was never persisted.
- The protein panel has the same shape of error: the assay measures **24** markers, four of which are
  isotype controls that the script drops, leaving **20**. The published sentence pairs the
  **post-filter** protein count with a **pre-join** cell count.

**Action taken.** `analysis/class_c/oracle_shape_test.py` now writes
`results/upgrade/oracle_shape_join_provenance.json` carrying `n_cells_protein_file`,
`n_cells_rna_file`, `n_cells_joined_by_barcode`, `n_markers_measured`,
`n_isotype_controls_dropped`, `n_markers_used`, the marker list, the join rule, the ADT
normalization, and a SHA-256 for each source h5ad.

**Action blocked.** The script cannot be re-run here: `data/raw/frangieh2021/` does not exist on this
machine and `anndata`, `scanpy` and `scipy` are not installed. The prose above therefore states the
join qualitatively ("in the same cells whose RNA the retrieval scores read"), which is exactly what
the barcode join licenses and what the section's argument needs, and prints **no cell count at all**.
`\SHAPECELLS` is intentionally undefined; the macro block carries a `TODO(U-2)` recording why.

**Risk if this is left as is:** none for R5's argument, which does not depend on the count. But the
main text and Extended Data Fig. 1 disagreement is a live defect that a reviewer can find in thirty
seconds, and it must be fixed before submission whichever way the re-run lands.

### 4.3 Relocated to Methods

| Content | Current location | Destination |
|---|---|---|
| Construction of both protein criteria (CLR normalization, isotype exclusion, control referencing, MIN_CELLS / MAX_CELLS subsampling) | [:562-567](../latex/PopRetrieve_manuscript.tex#L562) | Methods, "The oracle-shape test" |
| Why the immune condition cannot be pooled (condition confounds with perturbation) | `oracle_shape_test.py` docstring, not currently in the manuscript | Methods, same subsection |
| The barcode-join hazard (positional concatenation pairs each cell's protein response with another cell's RNA) | `class_c_protein_oracle.py:83-91`, not currently in the manuscript | Methods, same subsection. This is a real reproducibility hazard for anyone reusing Perturb-CITE-seq and is worth one sentence |

---

## 5. Exact word count

Counted on the prose of section 2 only, macros expanded to their printed values, LaTeX commands and
markup excluded.

```
544 words
```

Target 500 to 600. Inside band, 56 words of headroom.

Paragraph lengths: 92, 93, 83, 53, 97, 126. Measured by
`scratchpad/wc_prose.py`, which expands every macro to its printed value, resolves `\ref` to a single
token and strips remaining LaTeX before counting.

The 53-word fourth paragraph is the swap itself and is short by design: it is the section's load-bearing
sentence pair and nothing else belongs in it. The 126-word closing paragraph carries the interpretation
and the single scope boundary together, per the finding to boundary structure.

---

## 6. Grep checklist

Every numeral in the prose must resolve to a locked macro or to an explicitly listed literal. Run
from the repository root after the section is installed in the `.tex`.

```bash
# 1. No bare numeric literal in the R5 prose except the two whitelisted below.
#    Whitelist: "four isotype controls", a count written in words.
grep -noE '[+-]?[0-9]+\.[0-9]+' manuscript/rewrite/R5_oracle_form.md | sed -n '1,40p'

# 2. Every macro used in R5 is defined exactly once.
for m in PROTMARKERS SHAPEN SHAPENCTRL SHAPENIFN SHAPENCO \
         SHAPEMEANORACLEMEAN SHAPEMEANORACLEENERGY SHAPEDISTORACLEENERGY SHAPEDISTORACLEMEAN \
         SHAPEMAGMEAN SHAPEMAGDIST SHAPEEDGEDIST SHAPEEDGEMEAN; do
  n=$(grep -c "newcommand{\\\\$m}" manuscript/latex/PopRetrieve_manuscript.tex)
  printf '%-24s defined %s time(s)\n' "$m" "$n"
done          # every line must read "defined 1 time(s)"

# 3. Macro values match the artifact.
python3 - <<'PY'
import json, re, pathlib
j = json.load(open("results/upgrade/oracle_shape_test.json"))
tex = pathlib.Path("manuscript/latex/PopRetrieve_manuscript.tex").read_text()
def macro(n):
    return re.search(r"newcommand\{\\%s\}\{([^}]*)\}" % n, tex).group(1)
checks = [("SHAPEMEANORACLEMEAN", j["mean_vs_oracleMEAN"]),
          ("SHAPEMEANORACLEENERGY", j["energy_vs_oracleMEAN"]),
          ("SHAPEDISTORACLEENERGY", j["energy_vs_oracleDIST"]),
          ("SHAPEDISTORACLEMEAN",   j["mean_vs_oracleDIST"]),
          ("SHAPEMAGMEAN",          j["magmatch_vs_oracleMEAN"]),
          ("SHAPEMAGDIST",          j["magmatch_vs_oracleDIST"]),
          ("SHAPEEDGEDIST",  j["magnitude_confound"]["energy_minus_magmatch_under_DIST"]),
          ("SHAPEEDGEMEAN",  j["magnitude_confound"]["energy_minus_magmatch_under_MEAN"])]
for name, truth in checks:
    printed = float(macro(name))
    ok = abs(printed - round(truth, 3)) < 5e-4
    print(f"{name:26s} macro {printed:+.3f}  artifact {truth:+.6f}  {'OK' if ok else 'MISMATCH'}")
n = [j["per_condition"][c]["n"] for c in ("Control", "IFNγ", "Co-culture")]
print("per-condition n", n, "sum", sum(n), "vs SHAPEN", macro("SHAPEN"),
      "OK" if sum(n) == int(macro("SHAPEN")) else "MISMATCH")
print("flips 3/3:", all(j["per_condition"][c]["flips"] for c in j["per_condition"]))
PY

# 4. No forbidden phrasing.
grep -niE "did not anticipate|sharpest result|cannot lose|we prefer to leave|not merely|218,331" \
     manuscript/rewrite/R5_oracle_form.md   # expect hits ONLY inside sections 4.1 and 4.2

# 5. No em dashes anywhere.
awk '/^## 2\./,/^## 3\./' manuscript/rewrite/R5_oracle_form.md \\
  | grep -cP '\\x{2014}'   # expect 0. Scoped to the prose and written as a
                              # codepoint so the check cannot match itself.

# 6. No cell count is printed in the prose.
awk '/^## 2\./,/^## 3\./' manuscript/rewrite/R5_oracle_form.md | grep -cE '218,?0?23|218,?331'   # expect 0
```

**Checklist result, measured 2026-07-29. All six items pass.**

| Item | Result |
|---|---|
| 1 bare numeric literals | none in the prose; every value resolves to a macro |
| 2 macros defined once | 14 of 14, `\ENERGYCANDMAG` included |
| 3 macro values against artifact | `SHAPEMEANORACLEMEAN` +0.242 / +0.242099, `SHAPEMEANORACLEENERGY` +0.146 / +0.146191, `SHAPEDISTORACLEENERGY` +0.529 / +0.529107, `SHAPEDISTORACLEMEAN` +0.334 / +0.333988, `SHAPEMAGMEAN` +0.125 / +0.124653, `SHAPEMAGDIST` +0.352 / +0.352353, `SHAPEEDGEDIST` +0.177 / +0.176754, `SHAPEEDGEMEAN` +0.022 / +0.021538, `ENERGYCANDMAG` +0.791 / +0.790985; per-condition n 213 + 227 + 219 = 659 = `SHAPEN`; flips 3 of 3. **ALL OK** |
| 4 forbidden phrasing | 0 hits in the prose |
| 5 em dashes in prose | 0 |
| 6 no cell count printed | 0 hits |

The em-dash check was self-matching on first writing (the grep pattern contained the character it
searched for) and is now written as a codepoint escape scoped to the prose.
