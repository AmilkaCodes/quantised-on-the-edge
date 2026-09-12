# IRP research questions — canonical current set

_Single source of truth for the live RQ set (2026-09-12). The proposal's original set is frozen
in the submitted document; this file tracks the set as amended for the IRP, with status. Any
future change lands here first, with a dated note in the project log. Refine/revisit flag:
RQ1b/RQ1c wording to be reviewed once the E1 protocol is drafted and supervisor feedback lands._

## The set (canonical order)

- **RQ1** (confirmatory — ANSWERED): How far can weight quantisation be pushed before the
  functional correctness (HumanEval+ pass@1) of a small local code-generation model collapses
  below a defined threshold?
- **RQ1a** (confirmatory — ANSWERED): does the threshold differ between a code-specialised and
  a general-purpose model?
- **RQ1b** (confirmatory — **ANSWERED 2026-09-12**, cross-device spot-check pending): does
  reference-documentation context ("open-book" retrieval over the official Python
  documentation) mitigate quantisation-induced degradation relative to closed-book generation?
  **Answer: NO — Δ(B−A) ≤ 0 at every rung for both models; the distraction cost peaks at each
  model's own collapse rung (Qwen Q2 −0.098 p=.007; Phi Q4 −0.152 p=.0008); collapse thresholds
  unchanged. See `irp/analysis/e1-openbook.md`.**
- **RQ1c** (exploratory, GATED — TO PILOT; added 2026-09-12): at which quantisation level does
  the reliable, structured tool use required for "agentic" assistant operation break down, and
  does it break before or after generation quality? (Descriptive metrics; proceeds only if
  tool use is measurably reliable at F16.)
- **RQ2** (confirmatory — ANSWERED): how do inference latency and peak memory scale with
  quantisation level across CPU-only, edge-GPU and unified-memory tiers?
- **RQ2a** (confirmatory — ANSWERED): which configurations are feasible on each?
- **RQ3** (confirmatory — ANSWERED closed-book): for each tier, at which quantisation level
  does each model meet pre-defined quality and performance thresholds ("good enough")?

## Hypotheses

- **H1a** (tested — REJECTED H0a): pass@1 at ≤Q2_K is significantly below the model's F16
  baseline (H0a: no difference). Result: Qwen Q2 p=1.2×10⁻⁷; Phi breaks earlier (Q4, p=0.007).
- **H1b** (tested — REJECTED H0b): the collapse level differs between the two models
  (H0b: identical). Result: Qwen safe through Q3; Phi breaks at Q4.
- **H1c** (TESTED 2026-09-12): the open-book benefit (Δ pass@1, open − closed) changes with
  quantisation level (H0c: constant). **Result: the effect is not constant — it spikes at each
  model's collapse rung (Phi Δ ranges −0.018 (F16) → −0.152 (Q4, p=.0008)) — but the shape is a
  collapse-rung spike, not a monotone slope; claim kept descriptive (per-rung Δ + CIs), no
  difference-of-differences test was registered.**
- RQ1c carries **no confirmatory hypothesis** — exploratory; descriptive reliability metrics
  (M1 valid-tool-call rate, M2 loop behaviour, M3 conditional pass@1).

## Where each is answered / to be answered

| RQ | Evidence home |
|---|---|
| RQ1/1a | `irp/analysis/collapse-threshold.md` (+ CIs, 5pp margin) |
| RQ1b | E1 Condition B runs (protocol pending) → analysis extension |
| RQ1c | E1 Condition D gate pilot → probe (if gate passes) |
| RQ2/2a | `proposal-dev/pilot/RESULTS.md` §9 (3 tiers + energy) |
| RQ3 | `irp/analysis/synthesis.md` (deployment envelope, registered SLO gate) |

## Design + governance pointers
- E1 design + mechanism decisions: `irp/extensions/e1-context-conditions.md` (D27 in the
  register; frozen BM25 retrieval, contamination sweep, Condition D guardrails)
- Ethics: Self-Assessment form amended 2026-09-12 (all Section-5 answers remain No);
  supervisor acknowledgment pending
- HARD GATE: no RQ1b/RQ1c measurement until the E1 protocol document is committed
