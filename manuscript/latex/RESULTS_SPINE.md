# EvalShift Results spine: claim -> Result -> figure -> panels

Editor pass 2026-07-12 (Nature-series editor lens). Lock this logic BEFORE writing prose or
building figures. Source of truth for the paper's skeleton; figures serve it.

Genre reminder: evaluation-methodology / methods-critique. EvalShift is a probe, not a product.
Every claim's prose weight must match its evidence weight. Honest ceiling: Nature Methods /
Cell Reports Methods class; figure polish does not lift genre.

## Decision summary (editor's calls, up for your override)

- **D1. Do NOT restructure the top-level Results.** Current R1-R6 already map 1:1 to C1-C6.
  No reordering, splitting, or merging of the load-bearing Results. This is a refine pass,
  not a rebuild.
- **D2. Promote R1 to a full unification theorem (the one substantive expansion).** R1 today
  states only the numerical identity (Hit@1 agrees to 3 decimals). The exp06 theory
  (beta-interpolation, energy = K=1 coverage, zero-variance limit) currently lives only in
  Methods. Because we are elevating C1 to its own Figure 2, R1 must carry the theorem, or the
  figure will outweigh its Result. Pull the theory up into R1 as first-class content.
- **D3. Downgrade R6 to a coda inside R5 (6 Results -> 5 Results + 1 coda).** R6 (resistance)
  is exploratory by its own admission (no timecourse, no survival, minority-rescue near-null).
  Giving it peer status with load-bearing R1-R4 mismatches claim strength to evidence strength.
  Keep the text; demote the header to a subsection under R5. Figure 6 unchanged (still covers
  both), but its resistance panel stays visually quarantined and labeled exploratory.

## The spine

Legend: [LB]=load-bearing, [SUP]=supporting, [EXP]=exploratory. Figure numbers are the
6-figure deck (renumbered +1 from current rendered fig2/3/4).

| # | Claim | weight | Result section | Figure | Panels (data source) |
|---|-------|--------|----------------|--------|----------------------|
| C1 | Mean/CMap is the zero-variance collapsed member of the distributional family; numerically identical | [LB] bedrock | R1 Mean-signature retrieval is a collapsed special case (EXPAND to theorem) | **Fig 2** unification | 2a beta-interpolation D_beta vs beta -> mean/worst limits (exp06 beta_interpolation.csv, 11 rows); 2b energy = K=1 coverage identity (exp06 degenerate_limit_real.csv); 2c Hit@1 ladder with mean=CMap=0.389 identity bracket (exp08 aggregate) |
| C2 | Objective-aligned metrics show large apparent distributional gains | [LB] | R2 Objective-aligned evaluation produces large apparent gains | **Fig 3** apparent gains | 3a Hit@1 ladder energy 0.837 vs 0.389 (exp08); 3b regret +0.119 n=621 p=4.3e-56 (exp12 per-query); 3c alpha-crossover K562 (exp01 controlled) |
| C3 | Gains are metric-class-dependent; collapse under oracle-independent criteria; gate cannot rescue | [LB] **the knife** | R3 Oracle-independent metrics collapse the apparent gains | **Fig 4** collapse (only 4-panel fig) | 4a Class A +0.119 vs Class B -0.013; 4b recommended +0.119 vs non-rec +0.122 (gate fails); 4c gate audit rho=-0.21; 4d exp13 0/37 |
| C4 | Collapse has a two-gate cause: structure preservation (5x collapse) + structure identifiability (ARI<0.15); conditional advantage absent | [LB] | R4 The information condition is a two-gate criterion | **Fig 5** two-gate | 5a Gate 1 structure preservation 0.046 vs 0.009 (exp09); 5b Gate 2 identifiability 9 methods ARI<0.15 on known-bimodal (controlled_mixture_ari); 5c coverage vs silhouette tertile rho=0.26 (coverage_by_identifiability) |
| C5 | HIR-Bench formalizes failure regimes; analytic flip boundary alpha*=B/(A+B); moderate predictability AUC 0.640; boundary by-design (honest) | [SUP] | R5 HIR-Bench formalizes failure regimes | **Fig 6** formalization + coda | 6a phase diagram alpha vs lambda (exp11 phase_diagram_source, 108 rows); 6b info-condition transfer (predicted_mean 100% no-DART); 6c predictability AUC 0.640 (exp11 FULL, NOT on-disk QUICK 0.5) |
| C6 | Response-divergent subpops enrich resistance programs; no functional validation | [EXP] coda under R5 | R5 coda: Exploratory resistance-associated divergence | **Fig 6d** quarantined | 6d AXL/mesenchymal +0.134 p=0.003, IFN p=1.9e-6 (exp15 enrichment_summary); dashed box + "exploratory" tag |
| - | Fig 1 concept hook (no Result; sets tension, does not spoil Fig 4 numbers) | - | (pitch, in Intro) | **Fig 1** concept | 1a AI schematic (subpop mixture vs mean collapse); 1b geometric intuition; 1c metric-class decides verdict tension |

## Consequential edits this spine implies (all mechanical once logic is signed off)

1. R1 expansion to theorem (D2): add beta-interpolation limit, energy=K=1 coverage identity,
   zero-variance limit as first-class R1 prose. Pull from Methods lines currently at ~445-447.
2. R6 -> R5 coda (D3): demote `### Result 6:` to `#### Resistance-associated divergence
   (exploratory)` under R5; renumber nothing else (there is no R7).
3. Figure-ref renumber +1: current manuscript refers to rendered figs as Fig 2/3/4; deck makes
   them Fig 3/4/5. One pass over all `Fig N` / `Figure N` refs in Results.
4. Result 4 already carries the conditional-negative paragraph (added 2026-07-12); it becomes
   panel-free supporting text (no new panel), consistent with "confirmed not rescued".
5. Claim-precision pass: every headline number in Results must trace to reference/
   manuscript_evidence_table.md. Known traps: HIR AUC 0.640 (FULL not QUICK 0.5); +0.119 =
   coverage_worst MEDIAN on recommended (not energy mean); non-rec +0.122 = mean_or_no_call only.

## What this spine does NOT change

- No new experiments (all data exists and is local).
- No claim strengthening: the sole large positive (Class A +0.119) stays labeled circular.
- Journal ceiling unchanged (Nature Methods / CRM). This pass makes the logic airtight, not
  the result bigger.

## Open decisions for you

- D3 (R6 downgrade): agree to demote resistance to an R5 coda, or keep it as standalone R6?
- Fig 1 concept: how hard should the hook be? Editor recommends tension-only, no Fig 4 numbers.
- Order after sign-off: refine Results prose first (R1 theorem + R6 coda + renumber), THEN build
  the deck from the locked Results. Editor recommends this order.
