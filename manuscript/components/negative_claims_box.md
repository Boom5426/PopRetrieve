> **SUPERSEDED IN PART, audited 2026-07-27.** This is a working document. It predates the July
> 2026 audit, which retracted or revised numbers this file may still quote, among them the
> "5.1x structure collapse" (R1), the MoA-nDCG statistics computed over 165 undefined sentinel
> values (R2), the Class A/B contrast that compared two different scorers (R4), the HIR-Bench
> predictability AUC of 0.640 (R11), the claim that no Class C metric was available (R14), and
> the "0 of 37 real-data tasks" count (R13). **Read [CORRECTIONS.md](../../CORRECTIONS.md) before quoting any
> number below**, and treat `manuscript/latex/PopRetrieve_manuscript.tex` as the authority for
> anything that reaches the paper. Where this file and CORRECTIONS.md disagree, CORRECTIONS.md
> is right.

# What This Study Does Not Claim

*This box is a standalone guardrail file and is reproduced verbatim in the main
manuscript (Results, adjacent to the central falsification result). Its purpose is
to make the paper's boundaries explicit and pre-empt over-reading.*

---

> ### What this study does not claim
>
> 1. **We do not claim that PopRetrieve provides better therapeutic recommendations.**
>    All positive gains are measured under an energy-based, objective-aligned proxy
>    (Class A). The clause that used to stand here, "no therapeutic-utility metric (Class C) is
>    available in this study", is **RETRACTED**: a Class C experiment against GDSC viability has
>    been in the repository the whole time (CORRECTIONS.md R14). What the paper claims under
>    Class C is stated in the Results and is conditional on the oracle's construction.
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
>    tasks clear it for PopRetrieve, 2 for the mean). The seed is not a replicate: it re-draws
>    which drugs are tested and re-clusters the minority subpopulation. Under
>    resampling, only **2 of the 10** threshold-crossing cross-line tasks survive, while
>    drugs that do *not* cross it in the recorded run cross it in **1 to 4 of 10** resamples (R13 corrected the range from 2-4).
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
>    It is a mean-based cosine proxy and is not PopRetrieve's own score, but it rewards
>    covering the minority state, which is exactly what `coverage_worst` optimizes.
>    It is *task-proximal*, not independent. MoA-nDCG is the only fully independent
>    judge here, and it is the one on which PopRetrieve shows nothing.
>
> 6. **We do not claim that the current gate reliably transfers to all real
>    retrieval tasks.** The information-condition gate is experimental; it does not
>    isolate oracle-independent PopRetrieve gains in partial-observed real data; its
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
> 8. **We do not claim that PopRetrieve predicts resistance.** The exp15 resistance
>    analysis is exploratory and hypothesis-generating; there is no drug
>    timecourse, survival, or post-treatment readout, and the PopRetrieve-versus-mean
>    minority-rescue contrast is near-null.
>
> 9. **We do not benchmark live PDGrapher.** Perturbation predictors are treated as
>    candidate-response *sources*, not as models under test. The "we do not benchmark live
>    scGen" half of this item is **SUPERSEDED**: the published scGen VAE was subsequently run
>    within-context and is reported (learning check 0.420 PASS, induced divergence 0.972 against
>    its own baseline, ~3% of the real divergence reproduced; CORRECTIONS.md R32). Published CPA
>    was also attempted and did not converge, which is reported as such.
>
> 10. **We do not claim that all CMap implementations are algebraically identical to
>    PopRetrieve.** The exact identity is limited to the implemented cosine mean-signature
>    kernel (`mean_cosine = cmap_cosine = 0.3885`); the rank-based WTCS variant is a
>    monotone sibling of the same signature, not an algebraic identity.

---

**Why the box matters.** The manuscript's credibility rests on holding a real
Class A positive and a real Class B null at once. Each negative claim above marks
the exact edge of what the evidence supports, so that the positive anchors
(mathematical unification; distributional signal exists on response-available
populations) cannot be misread as therapeutic-utility claims.
