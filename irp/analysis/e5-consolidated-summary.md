# E5 / extended-work — consolidated summary (stage-4 complete, 2026-09-15)

**Status: ALL measurement on this branch is COMPLETE** (stage-4 hard clause: no stage-5).
This is the one-page read for the include-or-hold decision and the supervisor briefing.
Registrations: `e5-false-api-raft.md`, `e5-stage4-completion.md`, decisions in
`e5-decision-log.md`; analyses: `e5-fab-g3.md`, `e5-raft-stage2.md`, `e5-stage3-levers.md`,
`e5-inversion-mechanism.md`, `e5-fab-phi.md`, `e5-fab-v2-replication.md`.

## What was built
**FAB** — a deterministic false-API benchmark where documentation is *necessary* by
construction and contamination is impossible by construction. Validated: closed-book 0.000 for
all three models at every rung; open-book 0.99 (7B F16). Replicated on a second generation
(v2: anchors identical). The instrument E1 said it lacked.

## The five findings (each pre-registered, each replicated or mechanism-verified)

1. **Small models CAN exploit necessary context at full precision.** 1.5B F16 open-book 0.983
   (7B 0.992; Phi-3 0.875). The dissertation's "context never helps" is a task-structure
   result, now cleanly bounded by instrument.
2. **⭐ Quantisation destroys context-exploitation at each model's OWN quality cliff — and
   harder than it destroys generation.** Qwen 1.5B: collapse at Q2 (0.983→0.592, p=1.4×10⁻¹⁴;
   deeper than its −22.6 pp generation collapse). Phi-3: collapse onset exactly at ITS Q4
   cliff (0.875→0.775→0.650→0.217, p=3×10⁻²⁰ at Q2) while Qwen was intact at Q4. 7B: no cliff,
   no collapse (flat, n.s.). Cliffs three rungs apart, damage follows the cliff both times.
3. **⭐ Calibrated quantisation rescues it — causally, cross-model, for free.** Same bits,
   imatrix rounding: Qwen Q2 B 0.592→0.933 / O 0.408→0.967 (p≤5.9×10⁻¹¹; cliff pushed past
   Q2 → full rescue). Phi: full rescue at Q4 (0.958/0.992, above F16), partial at Q2 (B 0.425,
   O 0.892) — exactly where E2b relocated its cliff. Deployment cost verified on both edge
   devices: tok/s, RSS, power identical to naive (Pi 14.5 vs 14.8 tok/s; Jetson 32.4 vs 32.3).
4. **Training subtracts at this scale; the other cheap lever is a null.** RAFT LoRA (with the
   no-docs control): both arms came out byte-identical (120/120) — mask-prompt + train tasks
   the base model already solves = zero context-exploitation gradient; only format-narrowing
   learned (FAB B −21 pp, HumanEval+ 0.610→0.262). Example-dense docs: +3–6 pp, n.s., F16
   control inert. **Measured lever ranking: imatrix ≫ docs formatting ≈ 0 > LoRA (< 0).**
5. **Collapse-rung context processing has a bizarre, robust fine structure.** Distractor
   filtering dies before docs-following (O > B at degraded rungs, both models). At the deep
   collapse, the SIMPLEST prompts fail first: Qwen's one-page fixation (O singles 0.314; one
   content-irrelevant extra page → 0.671 — registered prediction confirmed) and Phi's
   near-total single-call failure (B singles 0.029 vs chains 0.48). The B>O inversion is
   Qwen-specific (direction replicates on v2, significance does not); the singles-first
   failure is cross-model.

## The deployment sentence (all clauses now measured)

> On edge hardware, quantisation silently breaks a model's ability to use the documentation you
> give it — at the model's own quality cliff, before and harder than it breaks generation. The
> fix is in the quantiser: calibrated (imatrix) quantisation restores context-exploitation at
> identical memory, speed, and power, verified on Raspberry Pi 5 and Jetson Orin Nano. Prompt
> engineering does not fix it (though never send a collapse-rung model a single-page context),
> and naive LoRA fine-tuning makes it worse.

## Include-or-hold — DECIDED 2026-09-15: HOLD, with the boundary stated on main

Student decision (reasoned; recorded on main in `supervisor-briefing-2026-09.md` and
`drafts/boundary-paragraph.md`, commit bebd6e5):
- **"Selective include" was rejected as incoherent:** findings 2–3 rest on finding 1, and
  finding 1 drags the full FAB validity case (necessity/contamination-by-construction,
  determinism, v2 replication) into the dissertation's methods chapter — a thin methods
  write-up of a major claim, an examiner's obvious line of attack on a result that is not
  load-bearing for the registered RQs. The rubric prices depth (Methodology 30% + Results
  30%), not ambition; scope is graded as "appropriate", not as size.
- **Hold the results, keep the knowledge:** the dissertation gains ONE Limitations/Discussion
  paragraph stating the scope boundary of its negative context result (bounded to
  self-contained benchmarks by construction) — drafted in two variants on main, no branch
  results claimed; the follow-up-reference variant is pending the supervisor's answer on
  York's convention for completed-but-unreported work.
- **The branch stays intact as one publishable unit** (findings 1–5 + FAB) and the PhD-seed
  package. Splitting it would give the dissertation a fragment and the paper a hole.
- Superseded-spec banner and claim-wording audit applied on main (the "in-weights"
  premise corrected; the self-contained qualifier marked load-bearing).

## Honest limits (carry into any use)
Synthetic micro-APIs (external validity argued, not measured); two generations of one
generator family; one seed per cell at temp 0; n=120/cell; cross-model reads qualitative;
example-density and B>O-inversion effects below detection at this n.
