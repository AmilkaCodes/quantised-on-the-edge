# E5 — False-API benchmark (FAB) + RAFT arm (extended work, branch-isolated)

**Status: REGISTERED 2026-09-14 on branch `extended-work` (student directive, dated).** The
student is drafting the dissertation on `main`; this programme runs in parallel on this branch
and is **not load-bearing for the dissertation** — it is the PhD-seed pairing named in the E4
spec's sequencing rationale ("build the docs-required benchmark, then test whether RAFT-style
training lets small quantised models pass it"). Nothing here merges to `main` without student
review; the write-up lien (methods+results drafts on track by 2026-09-28) continues to govern
the dissertation and is the student's own allocation; if the write-up needs the bench or the
student's attention, this branch pauses without ceremony.

## Why this exists (the recorded blockers it unblocks)

1. **E1/E1-R/E2a's honest limit:** HumanEval+ problems are self-contained, so context has near-
   zero headroom to help — Δ(open−closed) ≤ 0 everywhere is evidence about *imposed unnecessary
   context*, not about context-exploitation capacity. The fair test needs problems **unsolvable
   without reference material**.
2. **RAFT was sequenced, not rejected**, for four recorded reasons (E4 spec) — the first being
   that no instrument could detect a RAFT success. FAB is that instrument; building it comes
   first, and its validity gates (below) come before any training.

## Stage 1 — the FAB instrument (the deliverable even if RAFT slips)

**Design: a deterministic, seed-generated fictitious Python library.** Invented module and
function names (syllable-generated, no real-world collisions), invented semantics (argument
orders, unit systems, framing/checksum conventions, error behaviours) that **cannot be guessed
from pretraining** — docs-necessity by construction, contamination-proof by construction.

- **Generation:** `proposal-dev/pilot/e5/fab_build.py`, seed 0, fully deterministic; committed
  manifest with shas of every artefact. Hidden reference implementation (executes tests) is
  never shown to the model; docs pages (per-function: signature, semantics, worked example) are
  the open-book material.
- **Eval set:** ~120 tasks across ~10 API families. Each task = natural-language problem
  requiring 1–3 false-API calls; ≥5 test cases (incl. edge); reference solution.
- **Train pool (for RAFT, stage 2):** disjoint families from a different seed block; zero
  name overlap enforced by an automated sweep at build time (the 13-gram discipline applies to
  prose; name-disjointness is the sharper guarantee here).
- **Conditions (reusing the E1 instrument stack):** A closed-book (no docs) · B open-book
  (correct doc page + distractor pages, fixed) · R BM25 retrieval over the full false-doc
  corpus (frozen index, k=2, the e1 chunker) · O oracle (correct page only).
- **Build-time self-validation gates (hard):** every reference solution passes its tests under
  the hidden implementation; every task's required function names appear in NO other family;
  docs pages contain no reference-solution 13-grams beyond the API signatures themselves.

**Instrument-validity gates (measured BEFORE any training; stock models):**
- **G1 docs-necessity:** stock 7B closed-book pass@1 ≤ 0.10 (if higher, names/semantics are
  guessable → regenerate harder).
- **G2 docs-sufficiency:** stock 7B open-book (B) pass@1 ≥ 0.60 (if lower, the benchmark is
  measuring difficulty, not context-exploitation → simplify semantics/docs and rebuild).
- **G3 the headline measurement (no training needed):** the 1.5B and 7B ladders on A/B/R/O —
  *does Δ(B−A) > 0 survive quantisation, and where does it collapse?* This is the direct,
  novel complement to the dissertation's negative result: the first measurement of
  quantisation's effect on **necessary**-context exploitation. G3 alone justifies the branch.

## Stage 2 — RAFT arm (gated on G1∧G2; per the recorded four-reason design)

- **Intervention:** LoRA (MLX, isolated e4-venv, same pipeline as E4) on Qwen2.5-Coder-1.5B:
  (problem + docs-with-distractors → solution) triples built ONLY from the train families.
- **The control arm the E4 spec demanded:** same solutions trained WITHOUT docs in the prompt —
  separates context-handling repair from "more coding practice near the distribution".
- **Readout:** F16 gate on FAB eval A/B/R/O (does trained Δ(B−A) exceed stock Δ(B−A), and does
  the no-docs control NOT show the gain?) → if pass, merge-then-quantise naive ladder (the H4b
  question transplanted to context-exploitation: does the trained capability survive rungs?).
- **E4-α lessons applied at design time:** native ChatDataset format + `--mask-prompt` from the
  start; training examples END with the code answer (never a call/lookup) so no
  respond-then-stop attractor; gate batteries not val loss; composition gate (does it still
  solve no-docs tasks?) before any ladder.

## Ethics (delta from the standing all-No position)
- All synthesis is deterministic script generation (no scraped data, no personal data, no
  frontier-API outputs — the TRAP path stays closed; no local-model synthesis needed at all
  for the benchmark since semantics are programmatic).
- FAB is contamination-proof against public benchmarks by construction (invented names);
  the reserved MBPP+ remains untouched.
- Training compute: LoRA-scale, same envelope as E4-α (recorded for proportionality).

## Timeboxes and order
1. FAB generator + self-validation (bench-free) → commit frozen artefact.
2. G1/G2 validity gates (Mac, stock 7B, ~an evening) → recalibrate/rebuild if failed (the
   generator is parameterised for difficulty; recalibration is a dated deviation, cheap).
3. G3 ladders (Mac; 1.5B all rungs + 7B all rungs, conditions A/B/R/O) — the headline.
4. Stage-2 RAFT only after G1∧G2 hold and the student has seen the G3 read.

## Gate outcomes (2026-09-14, same day — stock 7B @ F16, n=120 per condition)

| condition | pass@1 | single | chain |
|---|---:|---:|---:|
| A closed-book | **0.000** | 0.000 | 0.000 |
| B open-book (+3 distractors) | **0.992** | 1.000 | 0.980 |
| R BM25 k=2 (80-page corpus) | 0.958 | 0.986 | 0.920 |
| O oracle (correct pages only) | 1.000 | 1.000 | 1.000 |

**G1 PASS (0.000 ≤ 0.10)** — the false API is unguessable; docs-necessity holds by measurement,
not just construction. **G2 PASS (0.992 ≥ 0.60)** — docs are sufficient; the instrument's
dynamic range at F16 is effectively the whole interval. R ≈ B says lexical retrieval is
near-sufficient when docs are necessary and jargon-matched (BM25's home turf — the designed
contrast with E1's HumanEval setting, where retrieval had nothing useful to fetch).
One harness fairness fix recorded pre-gate (smoke): the scorer supplies `import <module>`
since the task text says to assume it works. **FAB is a valid instrument; G3 authorised.** G3 COMPLETE same day — ladders + stats in `irp/analysis/e5-fab-g3.md`; headline: 1.5B necessary-context exploitation 0.983 at F16 collapses to 0.592 at Q2_K (47 broke/0 rescued, p=1.4e-14), harder than generation collapsed on HumanEval; 7B flat (n.s.). Stage 2 (RAFT) now awaits the student's review of the G3 read, per this registration.

## Stage-2 ACTIVATION (2026-09-14, student go — "go on stage 2"; pre-registered before any build/run)

- **Train pool:** seed block 2000+ via the frozen generator machinery — 30 training families
  (+3 held-out valid families). **Name-disjointness sweep vs the eval block is a hard build
  gate** (zero module/function name overlap). Eval tasks, docs, and seeds untouched.
- **Two arms, identical solutions, one variable (the registered control design):**
  - **RAFT arm:** user turn = docs (correct pages + k distractor pages, k ∈ {0,1,3} varied
    deterministically per task — the G3 finding-4 knob) + task; assistant turn = reference
    solution in a fenced block. Native ChatDataset `{messages}`, `--mask-prompt`
    (E4-α lessons: single templating; examples END with code; no call-and-stop attractor).
  - **Control arm:** identical tasks and solutions, NO docs in the user turn — separates
    docs-conditioned learning from task-distribution practice.
- **Training (both arms, pre-registered):** mlx_lm lora, Qwen2.5-Coder-1.5B-Instruct, iters 600,
  batch 4, num-layers 16, seed 0, isolated e4-venv; sequential runs (Metal contention).
- **F16 gate (pre-registered criteria):**
  1. RAFT-arm FAB eval: B ≥ stock's 0.983 band (no degradation; A must stay 0.000 — names
     are disjoint, so any A > 0 is leakage and fails the gate);
  2. **Composition gate:** HumanEval+ closed-book n=164 within noise of stock 0.610 (the
     E4-α only-that failure screen);
  3. Control-arm FAB eval B shows NO material gain over stock (else gains are practice, not
     docs-use).
- **If gate passes:** merge-then-quantise naive ladder (Q8/Q4/Q3/Q2), FAB B/R/O per rung —
  **the H4b-transplant headline: does trained context-exploitation survive the ladder better
  than stock's (Q2 B: stock 0.592)?** The F16 ceiling (stock 0.983) means the measurement
  lives on the ladder, not at F16 — recorded so the F16 gate is read as a screen, not the result.
- **Timebox:** data build + both trainings + gate ≈ 1 bench day; ladder ≈ half a day more.
  E4's two-iteration discipline applies per arm (one rebuild each on instrument-artefact
  grounds only; a genuine gate FAIL is a result, not a retry ticket).

## Stage-2 CLOSURE (2026-09-14, same day): gate FAIL on criteria 1 (FAB B 0.775 vs 0.983) and
2 (HumanEval+ 0.262 vs 0.610); ladder not run; both arms closed. Mechanism verified — with
`--mask-prompt` and train tasks the base model already solves with docs, there was zero
context-exploitation gradient; both arms converged to identical format-narrowing (120/120
byte-identical eval outputs) that taxed chains, oracle-following, and general coding. A=0.008 is
name-prior guessing (FAB/28; name absent from training data — verified), not leakage. Full
analysis: `irp/analysis/e5-raft-stage2.md`. A meaningful RAFT retest requires train tasks the
base model FAILS with docs (new registration, student decision).

## Stage-3 REGISTRATION (2026-09-14, student go — "proceed with the untested improvement paths"):
two NON-TRAINING levers, pre-registered before runs. Model weights untouched in both.

- **Lever 1 — calibrated quantisation (E2b transplant):** existing committed 1.5B imatrix
  artefacts (imat-Q4/Q3/Q2, bartowski calibration set, E2b provenance) on FAB conditions B and O,
  vs the naive-ladder G3 baselines. **Question:** does calibration rescue necessary-context
  exploitation at the cliff as it rescued generation (prediction from "benefit follows the
  cliff": naive Q2 B 0.592 should move up materially)?
- **Lever 2 — example-dense documentation (the G3 finding-4 test):** a parallel docs set —
  identical functions, semantics, and tasks; each doc page carries THREE worked examples instead
  of one (deterministic, computed via the hidden impl; frozen FAB v1 files untouched; separate
  `families_dense.json` + `_dense`-suffixed results). Cells: naive 1.5B Q2/Q3 × B/O (the
  degradation region) + F16 B (control: density must not hurt at full precision).
  **Question:** if collapse-rung context processing is example-mimicry (the recorded
  hypothesis), dense docs should lift Q2 cells — and O@Q2 (0.408, the inversion) most of all.
- Readout thresholds are NOT pre-committed (these are exploratory improvement measurements, not
  gates); paired per-task comparison vs G3 baselines with McNemar, reported either way.

## Deviations
- (2026-09-14, stage-2 design note) The G3 finding-4 "example density" knob is NOT varied in
  this first RAFT pass (docs pages keep one worked example each); only distractor count is
  varied. Recorded so a null on distractor-robustness is not misread as covering the
  example-density hypothesis.
