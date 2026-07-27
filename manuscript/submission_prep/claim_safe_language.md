> **SUPERSEDED IN PART, audited 2026-07-27.** This is a working document. It predates the July
> 2026 audit, which retracted or revised numbers this file may still quote, among them the
> "5.1x structure collapse" (R1), the MoA-nDCG statistics computed over 165 undefined sentinel
> values (R2), the Class A/B contrast that compared two different scorers (R4), the HIR-Bench
> predictability AUC of 0.640 (R11), the claim that no Class C metric was available (R14), and
> the "0 of 37 real-data tasks" count (R13). **Read [CORRECTIONS.md](../../CORRECTIONS.md) before quoting any
> number below**, and treat `manuscript/latex/EvalShift_manuscript.tex` as the authority for
> anything that reaches the paper. Where this file and CORRECTIONS.md disagree, CORRECTIONS.md
> is right.

# EvalShift Manuscript — Claim-Safe Language Guide

Binding on all drafting. The manuscript's credibility rests on *not* overclaiming; a single
therapeutic-superiority sentence invites the "so what does it actually do?" rejection.

## Recommended phrases

- "information-conditioned advantage"
- "distributional retrieval under reliable candidate structure"
- "mean-collapsed signature retrieval" / "zero-variance special case"
- "metric-dependent gain"
- "boundary-aware / reliability-aware decision framework"
- "moderately predictable failure regimes"
- "diagnostic gate: recommend EvalShift / mean-sufficient / no-call"
- "candidate-response information condition"
- "the advantage is present under an energy-based proxy and absent under
  oracle-independent metrics"

## Phrases to avoid

- "better therapeutic recommendation" / "improves treatment"
- "universal drug ranking" / "universal decision layer"
- "predicts drug response" / "predicts resistance" / "identifies persister cells"
- "outperforms all baselines" / "state-of-the-art"
- "solves inverse design"
- "accurate" and "moderate" **for AUC 0.640**: that number is RETRACTED (R11). The honest
  statement is "moderately predictable" for the observable-feature AUC of 0.788, and it must
  travel with n_eff = 28 and the absence of any per-fold AUC distribution.
- "proves" (use "provides evidence that" / "is consistent with")

## Reviewer-risk responses

Short, pre-emptive answers to embed in Discussion / rebuttal.

**1. "Isn't this just energy distance?"**
No — the contribution is not the metric but the *information-condition framework*: (a) the
unification showing mean/signature retrieval is the zero-variance limit, (b) the diagnostic
gate that says when the distributional metric helps, and (c) the honest boundary audit.
EvalShift is a family (energy/MMD/sliced-Wasserstein/coverage), and the paper's message is about
*when* any of them helps, not that energy distance is novel.

**2. "Isn't observed candidate response an oracle setting?"**
Yes, and we say so explicitly. exp08's `observed` condition is the upper bound where true
candidate populations are available; exp09/exp12/exp13 test the realistic
partial-observed / predicted conditions. The point of the framework is precisely to
distinguish these regimes rather than conflate them.

**3. "Why does EvalShift fail on predicted responses?"**
Because current predictors collapse candidate populations toward the mean: measured
structure diagnostics show predicted populations have ~5× lower subpopulation-variance
ratio, ~2.7× lower diversity, and higher isotropy than real populations (exp09). With no
reliable structure to exploit, the distributional signal has nothing to add — which is the
thesis, not a defect.

**4. "Are the gains circular because energy-based utility favors energy-based methods?"**
We raise this ourselves. The energy-welfare regret proxy is aligned with EvalShift's objective,
so we treat its gains as proxy evidence and test oracle-independent metrics (MoA-recovery
nDCG, minority coverage) where the advantage is null (exp12: −0.013; the companion "exp13: 0/37"
is **RETRACTED**, R13, and must not be quoted). The
honest conclusion is metric-dependent gain, not universal superiority — this is a
conditional-go, and we report it as such.

**5. "Why should users trust the gate if AUC is only 0.640?"**
**This question is obsolete: AUC 0.640 is RETRACTED (R11).** The reframed answer uses the
observable-feature AUC of 0.788 at n_eff = 28. The gate's value is not perfect prediction but a
three-way triage — recommend / mean-sufficient / no-call — that in the transfer test
correctly flags predicted-mean tasks as no-DART 100% of the time (exp13). A moderate gate
that reliably catches the clear no-DART regime is useful even if the boundary is fuzzy.

**6. "Does this predict resistance?"**
No. exp15 is explicitly exploratory: divergent minority states are *enriched* for
resistance-associated programs (AXL/mesenchymal, IFN), but we have no drug timecourse or
survival readout, so we make no predictive resistance claim. It is a hypothesis-generating
observation, flagged as such.
