# What This Study Does Not Claim

*This box is a standalone guardrail file and is reproduced verbatim in the main
manuscript (Results, adjacent to the central falsification result). Its purpose is
to make the paper's boundaries explicit and pre-empt over-reading.*

---

> ### What this study does not claim
>
> 1. **We do not claim that EvalShift provides better therapeutic recommendations.**
>    All positive gains are measured under an energy-based, objective-aligned proxy
>    (Class A); no therapeutic-utility metric (Class C) is available in this study.
>
> 2. **We do not claim oracle-independent therapeutic utility improvement.** Under
>    the oracle-independent metric (Class B) the advantage is absent or adverse: on
>    the *same scorer* and the *same queries* that earn a Class-A gain of **+0.129**,
>    MoA-nDCG is **−0.037**. On 239 real-data tasks the minority-coverage advantage is
>    statistically real and practically negligible (mean **+0.0018**, Wilcoxon
>    p = 1.3e-7, on a metric ranging [0.60, 1.00]), and it lives **only** in the
>    constructed cell-line mixtures (+0.0043, against +0.0003 in the natural data and
>    +0.00003 under predicted candidates).
>
> 3. **We do not report a count of "distributionally dominant" real tasks, and no such
>    count should be quoted from this work.** The 0.01 threshold sits at 0.77 sd of the
>    nonzero-difference distribution, inside its noise band, and it is one-sided (11
>    tasks clear it for EvalShift, 2 for the mean). The seed is not a replicate: it re-draws
>    which drugs are tested and re-clusters the minority subpopulation. Under
>    resampling, only **2 of the 10** threshold-crossing cross-line tasks survive, while
>    drugs that do *not* cross it in the recorded run cross it in 2-4 of 10 resamples.
>    (Earlier drafts said "0 of 37"; 37 is the QUICK sanity task count, quoted as if it
>    were the real-data result. See CORRECTIONS.md R13.)
>
> 4. **We do not claim that HDAC inhibitors are a validated regime for distributional
>    retrieval.** Exactly two tasks survive seed resampling, A549→MCF7 Abexinostat
>    (+0.090 ± 0.013, 10/10 seeds) and Belinostat (+0.081 ± 0.027, 10/10), both HDAC
>    inhibitors. With n=2, one cell-line pair and one drug class, that is a
>    hypothesis, not a result.
>
> 5. **We do not claim that minority-state coverage is fully oracle-independent.**
>    It is a mean-based cosine proxy and is not EvalShift's own score, but it rewards
>    covering the minority state, which is exactly what `coverage_worst` optimizes.
>    It is *task-proximal*, not independent. MoA-nDCG is the only fully independent
>    judge here, and it is the one on which EvalShift shows nothing.
>
> 6. **We do not claim that the current gate reliably transfers to all real
>    retrieval tasks.** The information-condition gate is experimental; it does not
>    isolate oracle-independent EvalShift gains in partial-observed real data; its
>    reliability axis is anti-correlated with true response divergence (ρ = −0.21);
>    and the dataset-level divergence criterion admits our **negative control**
>    (CD34+, measured cosine 0.186) just as readily as our positive anchor. Its
>    apparent success at flagging mean-collapsed predicted responses is a
>    **tautology**: the rule returns `no_DART` unconditionally for that information
>    condition, so it cannot return anything else.
>
> 7. **We do not claim that HIR-Bench is a biological ground truth.** It is a
>    constructive synthetic benchmark with a specified latent welfare oracle; its
>    phase boundary is expected by design.
>
> 8. **We do not claim that EvalShift predicts resistance.** The exp15 resistance
>    analysis is exploratory and hypothesis-generating; there is no drug
>    timecourse, survival, or post-treatment readout, and the EvalShift-versus-mean
>    minority-rescue contrast is near-null.
>
> 9. **We do not benchmark live scGen or live PDGrapher.** Perturbation predictors
>    are treated as candidate-response *sources*, not as models under test; the
>    scGen result uses an in-repo CPA-linear fallback with the backend
>    provenance-stamped in all outputs.
>
> 10. **We do not claim that all CMap implementations are algebraically identical to
>    EvalShift.** The exact identity is limited to the implemented cosine mean-signature
>    kernel (`mean_cosine = cmap_cosine = 0.3885`); the rank-based WTCS variant is a
>    monotone sibling of the same signature, not an algebraic identity.

---

**Why the box matters.** The manuscript's credibility rests on holding a real
Class A positive and a real Class B null at once. Each negative claim above marks
the exact edge of what the evidence supports, so that the positive anchors
(mathematical unification; distributional signal exists on response-available
populations) cannot be misread as therapeutic-utility claims.
