# MBPP+ robustness extension — REGISTERED (2026-09-16, decided by the student)

**Purpose:** the dissertation's single-benchmark external-validity threat (Ch3 §3.8) gets a
measured answer: does the collapse pattern replicate on a second execution-scored benchmark?
MBPP+ (~378 problems, same EvalPlus harness) roughly triples the problem count behind the
quality axis. **Status: registered on branch `product-demo` (the bench's working branch);
this registration is pushed BEFORE any run, and the registration + analysis are carried to
`main` for reporting.** Classification: a **registered robustness extension** — it postdates
the proposal, so it is NOT confirmatory and is reported as exploratory-registered, separate
from the RQ1 claims it stress-tests.

## Why MBPP+ is clean here

MBPP+ was deliberately **held reserved** throughout the project: never used in any training,
tuning, threshold or design decision (the E4 training data was decontaminated against it
precisely to preserve this). No instrument in the study has seen it.

## Scope (fixed; no expansion)

- **Cells: 2 models × 5 naive rungs, CLOSED-BOOK ONLY** (Qwen2.5-Coder-1.5B-Instruct +
  Phi-3-mini-4k-instruct; F16/Q8_0/Q4_K_M/Q3_K_M/Q2_K; the existing study ggufs, shas as per
  the study manifests). ~378 problems per cell.
- **Explicitly OUT (recorded so it stays out):** E1-style context conditions on MBPP+;
  imatrix cells on MBPP+; the 7B; any perf/energy cells. This is a quality-axis replication
  of the confirmatory core only.
- **Constants:** llama.cpp b9951, greedy, seed 0, study caps (768 gen / 4096 ctx), Mac
  quality axis (D4/D25 proxy logic inherited), per-model chat template as embedded.

## Dataset + harness

- EvalPlus MBPP+ dataset; **record the evalplus package version and dataset hash in the run
  manifest** (pin at run time; the version used for scoring is part of provenance).
- `run_pilot.py` gains a dataset flag (mechanical edit; review the diff before running —
  instrument-fairness rule). `EVALPLUS_MAX_MEMORY_BYTES=-1` set; stale `*_eval_results.json`
  caches deleted before scoring (the standing rule); per-problem eval_results snapshotted to
  `pilot/eval-results/mac/` as for HumanEval+.

## Instrument gate (runs first, before the ladder)

**F16 pass@1 (plus) ≥ 0.40 for BOTH models** (the study's GO-floor logic applied to the new
benchmark). Below it → STOP and inspect prompt construction/extraction for MBPP's format
(three-shot vs zero-shot conventions differ) before any ladder cell runs; a template fix is
an instrument fix (allowed, dated); a genuine sub-floor score is a reportable finding and
the extension stops there.

## Registered analysis + expectations

- Per-rung pass@1 with bootstrap CIs; **paired-difference intervals vs each model's F16**
  (B = 10,000, seed 0); paired exact McNemar per rung with **Holm** adjustment within each
  model's family; the 5pp margin applied as a descriptive replication yardstick.
- **Registered expectation (directional, qualitative):** the HumanEval+ pattern reproduces —
  Qwen degrades materially only at Q2_K; Phi breaks earlier (by Q4_K_M); orderings, not
  exact magnitudes, are the success criterion. Divergence from the pattern is equally
  reportable (research symmetry) and would itself be informative about benchmark-dependence.
- Report: `irp/analysis/mbpp-robustness.md` (tables + verdict + caveats), cross-referenced
  into the results chapter's external-validity discussion on `main`.

## Timebox + governance

**Two bench days** from first cell to committed analysis; whatever is unfinished then is
dropped and recorded. Deviations dated before the affected run where foreseeable. The
write-up lien continues to govern: if the drafts need the student's attention, this waits.
