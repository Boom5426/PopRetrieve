# Figure caption drafts

Drafts for Figures 1–6. Panels marked *(schematic)* are illustrations, not data;
every other panel is generated directly from a `results/` CSV (source data mirrored
under `results/main_figures/source_data/`). Honest interpretation boundaries are noted
in italics — do not remove them without checking the underlying result.

Generating script: `src/plotting/plot_main_figures.py` (one-click:
`bash scripts/run_all_figures.sh`).

---

## Figure 1 — Distributional inverse drug retrieval for heterogeneous populations

**(A–D schematic; E data.)** (A) Forward perturbation prediction maps a drug to
predicted cell states; the inverse task studied here maps a query cell population to a
ranking over candidate drugs. (B) Collapsing a heterogeneous population to its mean
signature discards subpopulation structure. (C) We instead score candidates by a
population-to-population distance D(P_d, Q). (D) Because subpopulations respond
divergently, the mean-based ranking and the distributional ranking can disagree on the
top drug — a real decision flip (shown with data in Fig. 2D). (E) The three real
datasets placed on the subpopulation-response-divergence axis: CD34+ progenitor
lineages respond alike (cos≈0.95, below the gate), Frangieh immune contexts are
intermediate (cos≈0.65, at/across the gate), and distinct cell types under one drug are
near-orthogonal (cross-line cos≈0.14, above the gate). *The gate at cos≈0.9 is the
empirically-estimated threshold from Fig. 3, not a fitted value.*

## Figure 2 — Controlled SciPlex3 proof

**(A schematic; B–D data, 20 seeds.)** (A) A heterogeneous query is an α/(1−α) mixture
of two orthogonal MOA response modes (HDAC vs JAK) with known subpopulation labels; the
ground truth is the drug covering both subpopulations. (B) Hit@1 of covers-both,
averaged over α∈{0.5..0.9}, across three cell lines: mean-cosine (incumbent) is near
chance (0.11–0.36) while global energy (0.76–0.97) and coverage recover the correct
drug. (C) α crossover: as one subpopulation dominates, mean-cosine decays while global
energy holds (K562 bold; A549/MCF7 faint). (D) A representative real ranking flip (K562,
α=0.5): mean-cosine ranks a majority-biased drug (majority-only) first and covers-both
second, whereas global energy ranks covers-both first. *This is one representative query
chosen because it exhibits the flip; the population-level flip rate is quantified in the
exp07 ranking-flip analysis.*

## Figure 3 — Divergence gate: when is distribution-aware retrieval necessary?

**(A schematic; B–E data, 20 seeds.)** (A) The response-direction cosine between two
subpopulations' drug-response deltas. (B) The distributional advantage over mean-cosine
emerges as the subpopulation responses diverge (cosine falls below ≈0.9) and vanishes
when they are aligned. (C) The advantage is depth-robust: global energy already leads at
15–60 cells/subpopulation (the CD34-like regime, shaded). (D) The gate is
metric-agnostic — energy, RBF-MMD (median heuristic) and sliced-Wasserstein show the
same behaviour, all above mean-cosine (≈0). (E) Where the real datasets sit on the gate,
consistent with (B). *The λ-shift construction in (B,D) extrapolates the minority
response; the gate location (cos≈0.9) is stable across metrics and cell lines but its
exact value is construction-dependent.*

## Figure 4 — Semi-realistic positive (cross-line) and honest negative (CD34+)

**(All data.)** (A) For drugs reliable in both lines (split-half controlled), the same
drug drives two real cell types in near-orthogonal directions (cross-line cosine ≈0.1–0.2,
far below the within-line reliability band and the gate). (B) Cross-line retrieval
replicates the mean-out failure on real cell types: mean-cosine decays with α while
global energy holds (K562+A549 bold). (C) On primary CD34+ cells, natural lineages rank
drugs ≈like the whole-mean (agreement ρ≈0.68–0.73 for majorities), and a
matched-budget within-vs-between test finds no disagreement beyond the noise floor
(shaded). *The minority lineage c3 is at the noise floor and unreliable at this depth —
we therefore do not claim a real minority signal.* (D) Consequently, for plain
self-retrieval on this real primary source mean-cosine WINS (0.53 vs energy 0.34) — an
honest negative, predicted by the Fig. 3 gate.

## Figure 5 — Frangieh melanoma: natural evidence and the IFNGR1 instance

**(A schematic; B–D data, 20 seeds, bootstrap CIs.)** (A) Three immune microenvironments
(Control / IFNγ / Co-culture) act as natural subpopulations that a real tumour mixes.
(B) The immune-evasion KO IFNGR1 diverges across contexts only against the immune-OFF
Control (cross-context cosine 0.15 / 0.26), not between two immune-active contexts
(0.67). (C) IFNGR1 retrieval: mean-cosine fails (0.10–0.20) and global energy recovers
(0.65–0.80) exactly in the divergent contexts, while both succeed when the contexts are
concordant (0.95/0.95); error bars are 95% bootstrap CIs. (D) Across KOs, the
distributional advantage increases as cross-context divergence increases (Spearman ρ<0).
*Natural context-divergence is concentrated in a few immune genes and mostly moderate;
the aggregate retrieval is near-null and the per-KO Spearman trend is in the predicted
direction but not statistically significant (n≈2–4 strongly-divergent well-powered KOs).
IFNGR1 is presented as a within-gene controlled instance, not as distribution-level
proof.*

## Figure 6 — Theory: strict generalization of mean matching

**(A–C data; D schematic.)** (A) As within-population spread → 0, the energy distance
converges to 2‖μ_P−μ_Q‖ — mean matching is the zero-spread limit. (B) With a single
subpopulation (K=1), the coverage score equals the global energy distance for every
temperature β. (C) One temperature β interpolates monotonically from coverage-mean
(β→0) to coverage-worst (β→∞). (D) The resulting hierarchy: mean matching ⊂ global
energy (= K=1 coverage) ⊂ β-family subpopulation coverage. *All three propositions are
verified numerically (10/10 checks, synthetic and real cells) in exp06.*
