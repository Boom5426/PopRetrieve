# DART Manuscript — Claim-Safe Language Guide

Binding on all drafting. The manuscript's credibility rests on *not* overclaiming; a single
therapeutic-superiority sentence invites the "so what does it actually do?" rejection.

## Recommended phrases

- "information-conditioned advantage"
- "distributional retrieval under reliable candidate structure"
- "mean-collapsed signature retrieval" / "zero-variance special case"
- "metric-dependent gain"
- "boundary-aware / reliability-aware decision framework"
- "moderately predictable failure regimes"
- "diagnostic gate: recommend DART / mean-sufficient / no-call"
- "candidate-response information condition"
- "the advantage is present under an energy-based proxy and absent under
  oracle-independent metrics"

## Phrases to avoid

- "better therapeutic recommendation" / "improves treatment"
- "universal drug ranking" / "universal decision layer"
- "predicts drug response" / "predicts resistance" / "identifies persister cells"
- "outperforms all baselines" / "state-of-the-art"
- "solves inverse design"
- "accurate" (for AUC 0.640 — use "moderate")
- "proves" (use "provides evidence that" / "is consistent with")

## Reviewer-risk responses

Short, pre-emptive answers to embed in Discussion / rebuttal.

**1. "Isn't this just energy distance?"**
No — the contribution is not the metric but the *information-condition framework*: (a) the
unification showing mean/signature retrieval is the zero-variance limit, (b) the diagnostic
gate that says when the distributional metric helps, and (c) the honest boundary audit.
DART is a family (energy/MMD/sliced-Wasserstein/coverage), and the paper's message is about
*when* any of them helps, not that energy distance is novel.

**2. "Isn't observed candidate response an oracle setting?"**
Yes, and we say so explicitly. exp08's `observed` condition is the upper bound where true
candidate populations are available; exp09/exp12/exp13 test the realistic
partial-observed / predicted conditions. The point of the framework is precisely to
distinguish these regimes rather than conflate them.

**3. "Why does DART fail on predicted responses?"**
Because current predictors collapse candidate populations toward the mean: measured
structure diagnostics show predicted populations have ~5× lower subpopulation-variance
ratio, ~2.7× lower diversity, and higher isotropy than real populations (exp09). With no
reliable structure to exploit, the distributional signal has nothing to add — which is the
thesis, not a defect.

**4. "Are the gains circular because energy-based utility favors energy-based methods?"**
We raise this ourselves. The energy-welfare regret proxy is aligned with DART's objective,
so we treat its gains as proxy evidence and test oracle-independent metrics (MoA-recovery
nDCG, minority coverage) where the advantage is null (exp12: −0.013; exp13: 0/37). The
honest conclusion is metric-dependent gain, not universal superiority — this is a
conditional-go, and we report it as such.

**5. "Why should users trust the gate if AUC is only 0.640?"**
We call it *moderate*, not accurate. The gate's value is not perfect prediction but a
three-way triage — recommend / mean-sufficient / no-call — that in the transfer test
correctly flags predicted-mean tasks as no-DART 100% of the time (exp13). A moderate gate
that reliably catches the clear no-DART regime is useful even if the boundary is fuzzy.

**6. "Does this predict resistance?"**
No. exp15 is explicitly exploratory: divergent minority states are *enriched* for
resistance-associated programs (AXL/mesenchymal, IFN), but we have no drug timecourse or
survival readout, so we make no predictive resistance claim. It is a hypothesis-generating
observation, flagged as such.
