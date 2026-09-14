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

## Deviations
_(none yet)_
