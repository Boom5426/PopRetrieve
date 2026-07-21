# Figure plan & registry (Phase 4 — BUILT)

Main figures 1–6, each written as PDF **and** SVG to `results/main_figures/`, with
per-panel source data under `results/main_figures/source_data/`.

- Generating script: `src/plotting/plot_main_figures.py`
- One-click: `bash scripts/run_all_figures.sh`  (set `DIDR_FIG_PNG=<dir>` for PNG previews)
- Captions: `paper/figure_captions.md`
- Style: DejaVu Sans; SVG text editable (`svg.fonttype=none`), PDF TrueType
  (`pdf.fonttype=42`) — ready for downstream Image2 refinement.

Every data panel reads an existing `results/exp0*` CSV — **no new experiments, no
fabricated data**. Panels marked (schematic) are illustrations and are labelled as such
on the figure and in the caption.

---

### Figure 1 — `fig1_problem_formulation.{pdf,svg}`
- **Panels:** A forward-vs-inverse (schematic) · B mean collapse (schematic) · C
  distributional matching (schematic) · D ranking-flip (schematic) · **E dataset ladder
  on the divergence axis (data)**
- **Source CSV:** `fig1_E_dataset_ladder.csv` ← `exp02_divergence_gate/dataset_positions_on_gate.csv`
- **Core message:** Inverse drug discovery is a distributional retrieval decision; real
  datasets span the response-divergence axis.

### Figure 2 — `fig2_controlled_sciplex3.{pdf,svg}`
- **Panels:** A query construction (schematic) · **B headline Hit@1 bars · C α crossover
  · D real ranking-flip ladder** (data)
- **Source CSVs:** `fig2_B_headline_hit1.csv`, `fig2_C_alpha_crossover.csv`,
  `fig2_D_ranking_flip_example.csv` ← `exp01_sciplex3_controlled/{metrics_summary,per_query_scores}.csv`
- **Core message:** On a controlled heterogeneous source mean-cosine fails (0.11–0.36);
  distributional scoring fixes it (0.76–0.97) and the top drug actually flips to covers-both.

### Figure 3 — `fig3_divergence_gate.{pdf,svg}`
- **Panels:** A cosine definition (schematic) · **B advantage vs divergence · C depth
  robustness · D metric robustness · E dataset positions** (data)
- **Source CSVs:** `fig3_B_divergence_sweep.csv`, `fig3_C_depth_sweep.csv`,
  `fig3_D_metric_robustness.csv`, `fig3_E_dataset_positions.csv` ← `exp02_divergence_gate/*`
- **Core message:** The distributional advantage is divergence-gated (~cos 0.9),
  depth-robust (≈60 cells), and metric-agnostic (energy/MMD/sliced-W).

### Figure 4 — `fig4_real_validation.{pdf,svg}`
- **Panels:** **A cross-line divergence · B cross-line retrieval · C CD34 lineage
  agreement + noise floor · D CD34 negative retrieval** (all data)
- **Source CSVs:** `fig4_A_crossline_divergence.csv`, `fig4_B_crossline_retrieval.csv`,
  `fig4_C_cd34_lineage_agreement.csv`, `fig4_C_cd34_noise_controls.csv`,
  `fig4_D_cd34_retrieval.csv` ← `exp03_crossline_semireal/*`, `exp04_cd34_negative/*`
- **Core message:** Failure replicates on real cell types (positive); CD34+ primary
  lineages respond alike so mean-cosine WINS (honest negative), exactly as the gate predicts.

### Figure 5 — `fig5_frangieh.{pdf,svg}`
- **Panels:** A immune-context setup (schematic) · **B IFNGR1 divergence · C IFNGR1
  ranking with bootstrap CIs · D per-KO divergence vs advantage** (data)
- **Source CSVs:** `fig5_B_ifngr1_divergence.csv`, `fig5_C_ifngr1_ranking.csv`,
  `fig5_D_gene_divergence_vs_advantage.csv` ← `exp05_frangieh_natural/*`
- **Core message:** On natural immune-context data the gate holds per-KO; IFNGR1 is a
  within-gene controlled instance where mean-out fails only when its contexts diverge.
- **Honest boundary (in caption):** aggregate is near-null; per-KO Spearman n.s. (few
  strongly-divergent KOs); IFNGR1 is an instance, not distribution-level proof.

### Figure 6 — `fig6_theory.{pdf,svg}`
- **Panels:** **A mean = zero-spread limit · B global = K=1 coverage · C β interpolation**
  (data) · D hierarchy (schematic)
- **Source CSVs:** `fig6_A_zero_spread_limit.csv`, `fig6_B_global_is_K1.csv`,
  `fig6_C_beta_interpolation.csv` ← `exp06_theory_limits/*`
- **Core message:** The distributional score strictly generalizes mean matching
  (mean ⊂ global energy ⊂ β-coverage), verified numerically.
