# E5 stage-4 — completion runs (REGISTERED 2026-09-15, branch `extended-work`)

**Purpose:** close every remaining measurement the E5 arc needs so the include-or-hold decision
(and the eventual paper) is made on a COMPLETE result set. Student directive 2026-09-15: "all
results and runs done before we consider anything else." Registered before any run, per house
rule. **Hard clause: stage-4 is the FINAL measurement stage on this branch. Anything not listed
here does not run; anything unfinished when the write-up needs the bench is dropped and
recorded. No stage-5.**

Constants inherited: llama.cpp b9951, temp 0, seed 0, FAB v1 frozen (tasks sha e6568060…),
n=120/cell, paired exact McNemar for same-instrument comparisons.

## R1 — B>O inversion mechanism analysis (Mac, ANALYSIS-ONLY, no inference)

Script: `proposal-dev/pilot/e5/e5_inversion_analysis.py` (committed with this registration).
Runs over the COMMITTED per-task rows + deterministically reconstructed prompts. Questions:
1. **Redundancy hypothesis (the weakened finding-4 variant):** at the 1.5B's Q2, does pass rate
   track total context size across conditions (O sparse < R < O dense < B sparse < B dense),
   and is the relationship absent at F16 (control)?
2. **Mimicry signal:** does the fraction of generated-code tokens present in the supplied doc
   pages rise at Q2 vs F16, and differ B vs O?
3. **Error taxonomy:** how do failure classes (timeout / NameError / wrong-value assertion /
   degeneration) shift down the ladder per condition?
4. **Chain vs single fine structure** at the collapse rung.
Exploratory, descriptive; report lands in `irp/analysis/e5-inversion-mechanism.md`.

**R1 STATUS: RUN 2026-09-15 (analysis-only, Windows-side, committed data) — report written.**
Headline: the inversion is a SINGLE-CALL phenomenon (Q2 singles: one page 0.314 vs two-or-more
pages 0.657, content-irrelevant; chains show no inversion) → refined **one-page fixation
hypothesis**, and the strong mimicry variant is unsupported (token overlap flat).

### R1b — padded-oracle cell (Mac, ~15 min; AMENDED IN before any stage-4 run)
The refined hypothesis's clean test: condition **P** (true page(s) + exactly ONE same-family
distractor; runner support committed) at **Q2_K, naive 1.5B, n=120**. **Registered
prediction: singles recover from 0.314 to ≈0.65 (the R/B level); chains ≈ unchanged.**
Optional twin at Q3_K_M (prediction: P ≈ O there, since the Q3 regime punishes extra pages)
if the Q2 cell confirms. Report appends to `e5-inversion-mechanism.md`.

## R2 — imatrix deployment-cost verification (Pi 5 + Jetson, ~minutes each)

The stage-3 deployment sentence claims the imatrix rescue is free at inference ("same bits,
different rounding"). Convert inference to measurement: ONE perf cell per edge device,
**1.5B imat-Q2_K**, standard perf mode (N=10×3, warm-up discard, study caps), compared against
the existing naive-Q2_K cells on the same devices. **Expectation (registered): tok/s, TTFT and
peak RSS within noise of naive Q2_K.** Any material deviation is itself a finding (kernel-path
difference) and gets investigated ONLY to the extent of one rerun.

## R3 — Phi-3 FAB ladders (Mac, ~1 bench day)

G3 ran the Qwen pair only; the two-model design that anchors the dissertation asks whether the
general model exploits necessary context and where it breaks (its cliff is Q4_K_M on
generation; E2b moved it to Q2 under calibration). Cells, all n=120:
- **Naive ladder:** Phi-3-mini-4k-instruct × {F16, Q8_0, Q4_K_M, Q3_K_M, Q2_K} × {A, B, R, O}
  (20 cells). A is expected 0.000 at every rung (docs-necessity is model-independent by
  construction; a nonzero A at any rung = instrument alert, stop and inspect).
- **Calibrated arm:** phi-3-…-imat (E2b artefacts) × {Q4_K_M, Q3_K_M, Q2_K} × {B, O} (6 cells).
**Registered questions:** (i) does Phi exploit necessary context at F16 (B vs its 0.646
HumanEval closed — different instruments, so read qualitatively)? (ii) does its FAB collapse
sit at Q4 (its generation cliff) rather than Q2 — the strongest available test of "benefit
follows the cliff" because the cliffs DIFFER between models? (iii) does calibration, which
moved Phi's cliff two rungs, move its FAB collapse the same two rungs? A yes on (ii)+(iii) is
the cross-model generalisation of the causal claim.

## R4 — second-generation replication (FAB v2, Mac, ~half a bench day)

One-seed fragility is the registered caveat on every FAB number. Replicate the headline cells
on a fresh generation:
- **Build:** generalise `fab_build.py` to accept `--seed-base` and `--out` (mechanical edit,
  no semantic change — diff reviewed before running), generate **fab_v2 with seed block 3000**,
  same params (10 families × 12 tasks). Self-validation V1–V3 must pass; commit fab_v2 +
  manifest BEFORE any scored run (same freeze discipline as v1).
- **Validity anchors (stock 7B F16):** A and B cells → G1/G2 thresholds as in v1 (A ≤ 0.10,
  B ≥ 0.60; expected ≈ 0.00 / ≥ 0.95).
- **Replication cells (1.5B):** {F16, Q2_K naive, Q2_K imat} × {B, O} (6 cells).
- **Registered success criterion (qualitative, this is a replication not a re-test):** the v1
  pattern reproduces in direction and rough magnitude — near-ceiling F16 exploitation, large
  Q2 naive collapse, large imat rescue, B ≥ O at naive Q2. Quantitative deltas reported with
  CIs; no pass/fail threshold beyond G1/G2.
Runner support: `fab_run.py --fab fab_v2` (results carry the `_fab_v2` suffix + fab_dir field).

## Explicitly OUT of stage-4 (recorded so they stay out)

RAFT retry (stage-2 closure stands: "not a retry ticket"); FAB v3 or harder benchmarks;
agentic conditions on FAB; repo-context transfer; additional model scales; FAB energy ladders;
any HumanEval re-runs. These are paper-stage or future-work items whatever the results.

## Reporting

R1 → `irp/analysis/e5-inversion-mechanism.md`. R2 → appended to `e5-stage3-levers.md`
(deployment-sentence verification note) + device manifests. R3 → `irp/analysis/e5-fab-phi.md`.
R4 → `irp/analysis/e5-fab-v2-replication.md`. Each with the standard caveats block. After
stage-4: the branch presents ONE consolidated summary for the include-or-hold decision and the
supervisor briefing; no further measurement.

## Deviations
_Dated, before the affected run where foreseeable._
