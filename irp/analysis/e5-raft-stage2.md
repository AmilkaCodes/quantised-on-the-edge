# E5 stage-2 — RAFT arm: gate FAIL with mechanism (CLOSED 2026-09-14)

**Registration:** `irp/extensions/e5-false-api-raft.md` (stage-2 activation, pre-registered
criteria + hyperparams). **Verdict: gate FAIL on criteria 1 and 2; the quantisation ladder does
not run. Both training arms are closed. This is a result, not a retry ticket (per registration).**

## What was run
Two LoRA arms (mlx_lm, 1.5B, iters 600, batch 4, 16 layers, seed 0, `--mask-prompt`, native
ChatDataset), identical tasks and solutions from 30 disjoint seed-2000 families (name-disjointness
vs eval verified; 360 examples/arm): **RAFT** (docs + k∈{0,1,3} distractors in the user turn) vs
**control** (no docs). Fused → F16 GGUF → FAB eval battery + HumanEval+ composition check.

## Gate results (F16, n=120 FAB / n=164 HumanEval+)

| cell | stock 1.5B | RAFT arm | control arm | criterion |
|---|---:|---:|---:|---|
| FAB A closed | 0.000 | 0.008 | 0.008 | =0.000 → *see instrument note* |
| FAB B open | 0.983 | **0.775** | **0.775** | ≥0.983 band → **FAIL** |
| FAB R | 0.958 | 0.717 | — | — |
| FAB O oracle | 0.958 | 0.725 | — | — |
| HumanEval+ closed | 0.610 | **0.262** | — | within noise of 0.610 → **FAIL** |

Training signatures: RAFT val loss 0.971→**0.001** by iter 200 (nothing left to learn — the base
model already solves train tasks when docs are present). Control val loss 0.523→**0.951 rising**
(no docs → no generalisable mapping; memorisation only, as designed).

## The mechanism (verified, not conjectured)

1. **The two arms are behaviourally IDENTICAL post-training: 120/120 FAB-B outputs byte-identical**
   (adapters and GGUFs differ by checksum; separate servers; a train-prompt differential probe
   run). With `--mask-prompt` both arms optimised the *same* completions — docs entered only as
   conditioning — and since docs-present emission was already near-zero-loss for the base model,
   **there was no gradient signal for context-exploitation at all**. The only direction gradient
   descent found was output-format narrowing, and both arms found the same one.
2. **Format-narrowing is the damage.** ~6.7 epochs (600 iters × batch 4 over 360 examples) locked
   "emit `import lib; def solve: return lib.call(x)`" — degrading chains most (FAB B chain
   0.98→0.62), oracle included (0.958→0.725, so docs-*following* itself, not just distractor
   handling), and general coding by −34.8 pp (HumanEval+ 0.610→0.262). The E4-α *only-that*
   phenomenon, reproduced in a second training domain with a controlled design.
3. **Instrument note — the A=0.008 cell is name-prior guessing, not leakage.** Both arms pass the
   same single task (FAB/28) closed-book by emitting the exact invented name `vorjullib.baxkev_cv`
   — which appears NOWHERE in either training file (verified by grep; disjointness gate held).
   Fine-tuning taught the *syllable prior* of the name generator; greedy decoding then guessed one
   name right out of a ~2,400-name space across 120 tickets. Stock models (no tuned prior) scored
   0.000. Future FAB iterations should widen the name space if trained models are evaluated on A.

## What this means

- **The RAFT hypothesis is not falsified — it was unfalsifiable at this train-task difficulty.**
  Training on docs-tasks the base model already solves with docs provides zero learnable
  context-exploitation signal. A meaningful RAFT test needs train tasks the base model FAILS
  with docs present (harder semantics, longer chains) so the gradient has something to teach.
  That is a new experiment (new registration, student decision), not a rerun.
- **The consistent programme finding hardens:** three trainings (E4 runs 1–2 at the protocol
  level, E5 both arms at the context level) show naive small-LoRA behaviour-tuning on
  format-regular data *subtracts* general capability and adds only format. Fine-tuning is not a
  free lever at 1.5B; every gain must be audited against composition gates.
- **The un-run cheap levers gain priority:** the two non-training interventions proposed after G3
  (imatrix-calibrated quants on FAB; example-dense doc formatting at Q2) are now the *only*
  untested improvement paths — and both leave the model untouched, which this result suggests is
  exactly where the edge deployment answer lives (echoing E2c: pick artefact and docs format,
  don't retrain).

## Ladder status
Not run (gate-gated). The H4b-transplant question (does trained context-exploitation survive
rungs?) remains open pending an artefact that passes the composition gate.
