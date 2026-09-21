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
- **RQ1b** (**registered extension, NOT confirmatory** — corrected 2026-09-21: the submitted
  proposal names context-following only as "a natural extension" in its limitations; RQ1b and
  H1c were added with the E1 protocol on 2026-09-12, registered before measurement but after
  the proposal, so they sit in the exploratory-registered class per Ch3 §3.1's firewall.
  **ANSWERED 2026-09-12**; cross-device spot-check DONE same day — 4/25 diverge, inherits D25
  aggregate-proxy status, see `e1-openbook.md` caveats): does
  reference-documentation context ("open-book" retrieval over the official Python
  documentation) mitigate quantisation-induced degradation relative to closed-book generation?
  **Answer: NO — Δ(B−A) ≤ 0 at every rung for both models; the distraction cost peaks at each
  model's own collapse rung (Qwen Q2 −0.098 p=.007; Phi Q4 −0.152 p=.0008); collapse thresholds
  unchanged. See `irp/analysis/e1-openbook.md`.**
- **RQ1c** (exploratory, GATED — **ANSWERED AT THE GATE 2026-09-12**): at which quantisation level
  does the reliable, structured tool use required for "agentic" assistant operation break down, and
  does it break before or after generation quality? **Answer: it is already broken at F16 —
  M1 valid-call rate 0/20 (gate FAIL, probe stopped per the binding rule) while closed-book pass@1
  is 0.90 on the same problems → tool operation breaks BEFORE generation, at the floor. Forced-mode
  diagnostic: wrong call wrapper + degeneration. See `irp/analysis/e1-agentic.md`.**
- **RQ1b/RQ1c REVISIT (registered 2026-09-13, `irp/extensions/e1r-protocol.md`) — ANSWERED
  2026-09-13 (same day, inside timebox):** two instrument-modified probes tested whether the E1
  negatives are fundamental or scaffolding-fixable. **R1 (grammar-constrained, model-chosen
  retrieval): gate PASS — M1′ 20/20 at F16; the E1 "agentic floor" was FORMAT, not intent
  (a 6-line GBNF deletes it). But the model's own-chosen context still does not pay: R1 ≈ B
  everywhere, R1 significantly below closed-book at Q4/Q3/Q2 (p=.002/.008/.003), and the query
  machinery itself breaks at Q2 (M1′ 0.86, degeneration 5→26). R2 (oracle selection): O ≤ A at
  every rung for both models — significant exactly at each collapse rung (Qwen Q2 p=.020, Phi Q4
  p=.021) — and O ≈ B throughout: selection quality is not the lever. Verdict per the registered
  map: syntax is scaffolding-fixable; context-exploitation is not — quantised small models cannot
  exploit even ideal context on self-contained tasks.** See `irp/analysis/e1r-agentic.md`,
  `irp/analysis/e1r-oracle.md`. Fine-tuning remains Future Work (binding).
  _BOUNDED (2026-09-15, branch `extended-work`, scope decision pending): on docs-NECESSARY
  tasks (FAB) the same models exploit context near-perfectly at F16 and lose the ability at
  each model's own collapse rung; calibration restores it. The "self-contained tasks"
  qualifier above is therefore load-bearing — any write-up wording keeps it._
- **RQ2** (confirmatory — ANSWERED): how do inference latency and peak memory scale with
  quantisation level across CPU-only, edge-GPU and unified-memory tiers?
- **RQ2a** (confirmatory — ANSWERED): which configurations are feasible on each?
- **RQ3** (confirmatory — ANSWERED closed-book): for each tier, at which quantisation level
  does each model meet pre-defined quality and performance thresholds ("good enough")?

## Registered exploratory extensions (beyond the proposal's RQ set — all CLOSED 2026-09-14)

_Each registered before running (protocol committed first), each exploratory and firewalled from
the confirmatory RQ1–3 claims; multiple comparisons uncorrected and stated as such._

- **E2a** (`e2a-protocol.md` — ANSWERED 2026-09-13): scale arms. **Arm 5:** the 7B does NOT
  collapse anywhere on the naive ladder (threshold None; Q2 −4.9pp n.s.) → collapse is a
  small-model phenomenon; memory-matched, 7B@Q2 (2.9GB, 0.793) beats 1.5B@F16 (3.1GB, 0.610);
  BUT open-book harm is significant at every 7B rung incl. F16 → scale rescues
  quantisation-robustness, not context-robustness. **Arm 4:** invocation decomposes into
  can't (1.5B degenerates under coercion) / won't-by-policy (4B: nudge 0.00 → mandate 0.40 →
  force 0.80, M3=1.0, first-person reasoning receipts). See `e2a-results.md`.
- **E2b** (`e2b-protocol.md` — ANSWERED 2026-09-14): imatrix calibration moves Phi's threshold
  TWO rungs (Q4→Q2) and halves Qwen's Q2 cliff; **the context harm follows the cliff, not the
  bit-width** (vanishes at calibrated Phi-Q4, persists at cliff-adjacent calibrated Qwen-Q2) —
  5th collapse-rung-signature appearance, first with intervention co-movement; D6 vindicated
  both directions. See `e2b-imatrix.md`.
- **E2c** (`e2c-7b-edge-perf.md` — ANSWERED 2026-09-14): deployment leg of the memory-matched
  claim. Jetson serves 7B@Q2 at 11.1 tok/s (deploys); Pi fails the throughput floor at every
  rung (1.5B stays that tier's only interactive option) but uniquely FITS F16 (0.8 tok/s,
  batch-only); Q3_K_M throughput dip = GPU-kernel artefact (absent on Pi CPU). Appended to
  `e2a-results.md`.
- **E4-α** (`e4-finetuned-toolcalling-spec.md` amendment — CLOSED 2026-09-14, gate FAIL,
  reportable): FC-LoRA on the 1.5B produced spontaneous well-formed calls BUT
  tools-in-context mode collapse ("only-that": 16/20 hallucinate the task's own function as a
  tool; no-tools control codes perfectly) → completes the can't/won't/only-that triad; β (H4b
  ladder) not run; iteration 3 formative-feedback-gated. Method lesson: gate batteries, not
  loss curves. See `e4-alpha.md`.
- **E5** (`e5-raft-benchmark-spec.md`, superseded banner — RUN ON BRANCH `extended-work`
  ONLY, HOLD decision 2026-09-19): docs-necessary fictitious-API programme. Not part of the
  dissertation's evidence; the dissertation carries one qualitative boundary paragraph
  (`drafts/boundary-paragraph.md`, HARD RULE: no branch number, direction or finding) and
  presents the programme as designed future work (`irp/future-work.md`).
- **E6 / MBPP+ robustness extension** (`e6-mbpp-replication.md` + `mbpp-extension.md` —
  ANSWERED 2026-09-16, **COMPLETED AND CORRECTED 2026-09-18**): registered cross-benchmark
  replication on MBPP+ (dataset held reserved throughout), predictions on record pre-run.
  **Authoritative analysis: `irp/analysis/mbpp-robustness.md`** (full 2×5 grid, n=378/cell,
  plus-status convention; gate pass 0.638/0.661). E6's partial grid is superseded on two
  counts recorded in its correction banner: it lacked Phi's Q8_0/Q3_K_M cells, and its
  1.5B/Phi tables were CSV-parsed base∧plus rather than the study's plus-status.
  **Findings: the deep-rung collapse replicates (Qwen Q2 −21.4pp, Phi Q2 −39.9pp); break
  points shift ONE rung in opposite directions (Qwen Q2→Q3, Phi Q4→Q3, converging at Q3),
  with the Qwen shift attributable to resolution as much as benchmark (HE+'s interval
  contains the MBPP+ estimate); the 7B's immunity and the memory-matched +18pp advantage do
  NOT transfer (−9.0pp significant; parity 0.640 vs 0.630, base∧plus).** Claim-wording
  constraints in the spine's cross-benchmark amendment.
- **Cross-device low-rung addendum** (`xdev-lowrung-addendum.md` — ANSWERED 2026-09-18):
  registered validation of the single-tier quality proxy at the near-margin rung. **Qwen
  Q3_K_M, K=50, Mac vs Jetson: identity 0.92 (vs 0.90 at Q4), pass flips 0/50.** The
  registered expectation (worse divergence at lower rungs) was violated favourably; the Q3
  margin verdict is not tier-fragile. See `irp/analysis/xdev-lowrung.md`.

## Hypotheses

- **H1a** (tested — REJECTED H0a): pass@1 at ≤Q2_K is significantly below the model's F16
  baseline (H0a: no difference). Result: Qwen Q2 p=1.2×10⁻⁷; Phi breaks earlier (Q4, p=0.007).
- **H1b** (tested — REJECTED H0b on HE+): the collapse level differs between the two models
  (H0b: identical). The proposal registered no decision rule beyond the threshold
  locations; one was fixed in Ch3 §3.5 on 2026-09-21 (commit 2d91ac1) BEFORE the statistic
  was computed (data pack item 14): between-model difference of per-problem drops on the
  shared problems, tested only at rungs where the descriptive verdicts differ, Holm over
  those rungs. Result: HE+ rejected at Q4_K_M (+10.4 pp, Holm p = .020) and Q3_K_M
  (+19.5 pp, p < .0001), Phi collapses earlier; descriptive thresholds Qwen Q2, Phi Q4.
  MBPP+: not distinguishable at this resolution (no eligible rung: both descriptive
  thresholds are Q3), which is the scope note the spine carries.
- **H1c** (registered with the E1 protocol 2026-09-12, not in the proposal — exploratory-
  registered class; TESTED 2026-09-12): the open-book benefit (Δ pass@1, open − closed)
  changes with quantisation level (H0c: constant). **Result: the effect is not constant — it spikes at each
  model's collapse rung (Phi Δ ranges −0.018 (F16) → −0.152 (Q4, p=.0008)) — but the shape is a
  collapse-rung spike, not a monotone slope; claim kept descriptive (per-rung Δ + CIs), no
  difference-of-differences test was registered.**
- RQ1c carries **no confirmatory hypothesis** — exploratory; descriptive reliability metrics
  (M1 valid-tool-call rate, M2 loop behaviour, M3 conditional pass@1).

## Where each is answered / to be answered

| RQ / extension | Evidence home |
|---|---|
| RQ1/1a | `irp/analysis/collapse-threshold.md` (+ CIs, 5pp margin) |
| RQ1b | `irp/analysis/e1-openbook.md`; boundary tests `e1r-oracle.md` (O ≤ A) |
| RQ1c | `irp/analysis/e1-agentic.md`; revisit `e1r-agentic.md`; grid `e2a-results.md` Arm 4 |
| RQ2/2a | `proposal-dev/pilot/RESULTS.md` §9 (3 tiers + energy) |
| RQ3 | `irp/analysis/synthesis.md` (deployment envelope, registered SLO gate) |
| E2a/E2c | `irp/analysis/e2a-results.md` (scale bound, memory-matched + deployment leg) |
| E2b | `irp/analysis/e2b-imatrix.md` (calibration moves the cliff; harm follows it) |
| E4-α | `irp/analysis/e4-alpha.md` (only-that; gate batteries lesson) |
| E6 / MBPP+ | `irp/analysis/mbpp-robustness.md` (authoritative full grid); `e6-mbpp-replication.md` (superseded partial grid, corrections noted) |
| xdev addendum | `irp/analysis/xdev-lowrung.md` (low-rung proxy validation) |
| Data pack | `irp/analysis/data-pack-computations.md` (bpw, truncation, Holm/CIs, J/token forms, idle, prompt lengths, floors) |
| Whole-arc synthesis | `irp/analysis/implications-synthesis.md` (six-claim spine + E6 amendment) |

## Design + governance pointers
- E1 design + mechanism decisions: `irp/extensions/e1-context-conditions.md` (D27 in the
  register; frozen BM25 retrieval, contamination sweep, Condition D guardrails)
- Ethics: Self-Assessment form amended 2026-09-12 (all Section-5 answers remain No);
  supervisor acknowledgment pending
- HARD GATE: no RQ1b/RQ1c measurement until the E1 protocol document is committed
