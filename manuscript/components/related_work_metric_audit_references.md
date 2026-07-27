# Related-Work Metric Audit — Annotated References

Verified citations grounding the field-level evaluation-circularity audit
(`evaluation_circularity_audit.md`, `related_work_metric_audit_table.csv`). Every
entry below was checked against the Crossref API (peer-reviewed) or the arXiv API
(conference/preprint) and resolves to a real record; preprints are labeled as such.
No reference is included that could not be verified. Each note states, in one line,
what the paper supports in the EvalShift audit and — where relevant — how it bounds
EvalShift's own claims.

Two tiers:
- **Tier 1 — method-family anchors:** the canonical papers for each of the seven
  method families, establishing what each family optimizes and which metric class it
  actually reports.
- **Tier 2 — evaluation-critique / benchmark:** the load-bearing tier — independent
  papers documenting that objective-aligned metrics overstate gains, that simple
  baselines match or beat complex methods under fair evaluation, and that the choice
  of metric can decide the winner.

---

## Tier 1 — Method-family anchors

### CMap / L1000 signature retrieval

1. **Lamb J, et al. (2006).** The Connectivity Map: using gene-expression signatures
   to connect small molecules, genes, and disease. *Science* 313:1929–1935.
   https://doi.org/10.1126/science.1132939
   — *Original Connectivity Map; scoring is enrichment of a query signature against
   reference mean signatures. Class A (objective-aligned). Anchors the "mean
   signature retrieval" family EvalShift generalizes.*

2. **Subramanian A, et al. (2017).** A Next Generation Connectivity Map: L1000
   platform and the first 1,000,000 profiles. *Cell* 171:1437–1452.
   https://doi.org/10.1016/j.cell.2017.10.049
   — *L1000-scale CMap; the weighted connectivity score (WTCS) is a GSEA-style rank
   enrichment of the mean signature. Supports EvalShift Result 1: WTCS is monotone in the
   same mean-collapsed quantity but not algebraically identical to the cosine
   identity (cmap_wtcs 0.4635 vs mean_cosine = cmap_cosine 0.3885).*

### Single-cell signature retrieval

3. **Peidli S, et al. (2024).** scPerturb: harmonized single-cell perturbation data.
   *Nature Methods* 21:531–540. https://doi.org/10.1038/s41592-023-02144-y
   — *Introduces E-distance (energy statistics) as a population-level perturbation
   metric. Doubles as an external precedent for EvalShift's energy score and for Result 1
   (the mean is the collapsed limit of a population distance), while remaining a
   Class A objective-aligned metric.*

### Single-cell perturbation predictors

4. **Lotfollahi M, Wolf FA, Theis FJ (2019).** scGen predicts single-cell
   perturbation responses. *Nature Methods* 16:715–721.
   https://doi.org/10.1038/s41592-019-0494-8
   — *VAE latent-vector arithmetic; evaluated by expression reconstruction
   (objective-aligned, Class A). The latent-linear class EvalShift's exp09 CPA-linear
   fallback represents.*

5. **Lotfollahi M, et al. (2023).** Predicting cellular responses to complex
   perturbations in high-throughput screens. *Molecular Systems Biology* 19:e11517.
   https://doi.org/10.15252/msb.202211517
   — *Compositional perturbation autoencoder (CPA); R²/DEG reconstruction metric
   aligned with the training loss. Class A (+B).*

6. **Hetzel L, et al. (2022).** Predicting cellular responses to novel drug
   perturbations at a single-cell resolution (chemCPA). *NeurIPS 35.* arXiv:2204.13545
   https://arxiv.org/abs/2204.13545
   — *Conference paper (verified via arXiv; no Crossref DOI). Extends CPA to unseen
   drugs via molecular structure; reconstruction metric on OOD drugs. Class A (+B).*

### Virtual-cell / perturbation foundation models

7. **Cui H, et al. (2024).** scGPT: toward building a foundation model for
   single-cell multi-omics using generative AI. *Nature Methods* 21:1470–1480.
   https://doi.org/10.1038/s41592-024-02201-0
   — *Foundation model; perturbation prediction evaluated by reconstruction/embedding
   metrics (Class A+B). Benchmarked in Ahlmann-Eltze et al. 2025 (ref. 12).*

8. **Hao M, et al. (2024).** Large-scale foundation model on single-cell
   transcriptomics (scFoundation). *Nature Methods* 21:1481–1491.
   https://doi.org/10.1038/s41592-024-02305-7
   — *Large sc foundation model; reconstruction/embedding-aligned evaluation.
   Benchmarked in Ahlmann-Eltze et al. 2025 and did not beat simple baselines.*

9. **Theodoris CV, et al. (2023).** Transfer learning enables predictions in network
   biology (Geneformer). *Nature* 618:616–624.
   https://doi.org/10.1038/s41586-023-06139-9
   — *Foundation model with in silico perturbation; downstream/embedding-aligned
   metrics (Class A+B).*

### Graph / target-based inverse design

10. **Roohani Y, Huang K, Leskovec J (2024).** Predicting transcriptional outcomes of
    novel multigene perturbations with GEARS. *Nature Biotechnology* 42:927–935.
    https://doi.org/10.1038/s41587-023-01905-6
    — *GRN-graph predictor; expression MSE / genetic-interaction-subtype precision
    (Class A+B). Benchmarked in Ahlmann-Eltze et al. 2025.*

11. **Guney E, et al. (2016).** Network-based in silico drug efficacy screening.
    *Nature Communications* 7:10331. https://doi.org/10.1038/ncomms10331
    — *Canonical network-proximity inverse design; the scoring graph is the
    evaluation graph (Class A). Shows the objective-alignment risk is not
    expression-specific — it spans the graph modality too.*

### PDGrapher-style target/drug graph methods

12. **Gonzalez G, et al. (2025).** Combinatorial prediction of therapeutic
    perturbations using causally inspired neural networks (PDGrapher). *Nature
    Biomedical Engineering.* https://doi.org/10.1038/s41551-025-01481-x
    — *Direct inverse-design end of the field; closed-loop target-ranking recall/nDCG
    (Class A+B). Adapted into EvalShift's retrieval frame in exp10.*

---

## Tier 2 — Evaluation-critique / benchmark (load-bearing)

13. **Ahlmann-Eltze C, Huber W, Anders S (2025).** Deep-learning-based gene
    perturbation effect prediction does not yet outperform simple linear baselines.
    *Nature Methods* 22:1657–1661. https://doi.org/10.1038/s41592-025-02772-6
    — **Keystone.** *Compared five foundation models and two other deep-learning
    models against deliberately simple baselines for single/double perturbation
    prediction; none outperformed the baselines. Independent, peer-reviewed
    reproduction of EvalShift's exp09 finding — objective-aligned reconstruction gains do
    not translate into an advantage over mean/linear baselines.*

14. **Kedzierska KZ, et al. (2025).** Zero-shot evaluation reveals limitations of
    single-cell foundation models. *Genome Biology* 26.
    https://doi.org/10.1186/s13059-025-03574-x
    — *Zero-shot evaluation shows single-cell foundation models (incl. scGPT,
    Geneformer) do not consistently beat simpler baselines. Independent support that
    foundation-model objective-aligned metrics overstate practical utility.*

15. **Wei X, et al. (2026).** Benchmarking algorithms for generalizable single-cell
    perturbation response prediction (scPerturBench). *Nature Methods.*
    https://doi.org/10.1038/s41592-025-02980-0
    — *Large multi-method benchmark using population-level metrics including
    E-distance/Wasserstein. Establishes that the field evaluates with the same
    distributional metric class EvalShift uses, and that generalization is hard.*

16. **"Evaluating Single-Cell Perturbation Response Models Is Far from
    Straightforward" (2026).** bioRxiv (preprint).
    https://doi.org/10.64898/2026.02.14.705879
    — **Key for the metric-taxonomy claim, and cited against EvalShift itself.** *Shows
    common distributional distances are strongly affected by scale, sparsity, and
    dimensionality: the Wasserstein distance fails in high-dimensional expression
    space under variance scaling, and the energy distance can overlook disruptions in
    gene–gene dependencies. Also reports complex models often underperform simple
    baselines. Substantiates the circularity thesis and honestly bounds EvalShift's own
    energy/coverage scores.*

17. **"The Metric Picks the Winner: Evaluation Choice Flips Model Rankings for
    Drug-Response Prediction in Unseen Chemistry" (2026).** arXiv:2606.12639
    (preprint). https://arxiv.org/abs/2606.12639
    — *Documents that the choice of evaluation metric flips model rankings for
    drug-response prediction in unseen chemistry — the same-method-different-verdict
    phenomenon EvalShift Result 3 demonstrates on a single task set.*

---

## Verification note

All DOIs above resolve via Crossref (peer-reviewed entries, refs. 1–5, 7–15) or the
arXiv API (refs. 6, 17); ref. 16 is a bioRxiv preprint whose DOI resolves. Titles,
first authors, years, and venues were confirmed against the returned metadata.
References 6, 16, and 17 are conference or preprint sources and are labeled as such;
all others are peer-reviewed journal articles. This bibliography contains no
unverified or fabricated entries.
