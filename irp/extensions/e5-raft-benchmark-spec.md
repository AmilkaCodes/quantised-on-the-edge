# E5 — Docs-required benchmark + RAFT for edge-class models (SUPERSEDED SPEC)

> **SUPERSEDED 2026-09-15:** this programme was registered, built and COMPLETED on branch
> `extended-work` (registration `e5-false-api-raft.md`; consolidated read
> `e5-consolidated-summary.md` there). Two of this spec's premises were corrected by the
> results: (1) the deficit is NOT in-weights — the untrained 1.5B exploits necessary context
> near-perfectly at F16 (FAB B 0.983), so E1-R's negative was task structure, bounded by
> instrument; (2) RAFT was run with its control and SUBTRACTED (format-narrowing, no
> exploitation gradient), while imatrix calibration proved the decisive, deployment-free
> lever. This file is kept as the design-lineage record; do not cite its premises.

**Original status: SPECIFIED ONLY (2026-09-14). NOT dissertation scope; NOT a dissertation
deadline dependency.** This is the post-submission / PhD-seed / publication project the dissertation's
Future Work presents as designed. Nothing here runs while the write-up lien governs
(methods+results drafts on track by 2026-09-28; formative = review gate). Design reading and
spec refinement are the only permitted activity before submission, and only in writing breaks.

**The question:** can in-weights context-exploitation be trained into an edge-class model
(RAFT-style), and does the trained capability survive quantisation? The dissertation proved the
deficit is in-weights (E1-R: no scaffold reaches it) and that naive fine-tuning has coupled
levers (E4-α: trained invocation broke completion). E5 is the properly-instrumented answer.

## Phase 1 — the instrument: a docs-required code benchmark (the blocking dependency)

The dissertation's benchmark cannot detect a RAFT success (HumanEval+ is self-contained; best
case Δ≈0, reachable degenerately). E5 needs tasks unsolvable without the reference docs.

- **Construction precedent (verified, in corpus):** Zan et al. 2022 (EMNLP Findings) —
  pseudo-private libraries by systematic renaming (pandas→monkey, isin→incontain) + rephrased
  docs; Codex 12B pass@1 18.88→1.47 public→private = docs-required demonstrated at frontier
  scale. **Design decision open until Zan §4 + Zan 2023 are read in full:** rename-based
  (cheap; validated problems inherited; surface-transfer critique possible) vs from-scratch
  invented API (cleaner; costlier) vs hybrid (invented facade over real semantics).
- **Components:** fictitious library API docs (written properly, chunked exactly as the E1
  corpus — reuse chunker + BM25 index); 50–150 problems with EvalPlus-style unit tests
  (execution-scored, reuse pilot runner); canonical solutions; **API-level train/test split**
  (test-split APIs appear in NO training example — the split is at the API, not the problem).
- **Validation gates (before any training):** (1) closed-book baseline ≈ 0 verified empirically
  on all study models — the docs-required proof; (2) docs-conditioned solvability spot-checked
  by hand; (3) contamination sweep run anyway (13-gram discipline) despite by-construction
  safety; (4) difficulty calibration (oracle-docs condition should be well above floor at F16
  for at least the 7B, else the instrument has no headroom to measure).
- Effort estimate: 2–4 weeks part-time. This phase alone, with Phase 2, is publishable
  ("can edge-class models do docs-required tasks with retrieval at all?").

## Phase 2 — baselines on the new instrument (pre-training measurement)

Port Conditions A (closed) / B (frozen BM25) / O (oracle) unchanged. Models: 1.5B, Phi-3, 7B;
F16 first, ladder after. This re-asks RQ1b on tasks where context is *necessary* — the
dissertation's own registered caveat ("oracle ≠ task-necessity") answered. Prediction registered
here informally: A ≈ 0 by construction; B/O reveal whether untrained models can exploit
must-have context at all. Either outcome sets RAFT's headroom.

### The necessary-context ladder question (student insight, dictated 2026-09-14)

**Does necessary-context exploitation survive the quantisation ladder, and does it fail at the
same rung as generation or earlier?** The dissertation could not ask this: with Δ(open−closed)
≤ 0 everywhere on HumanEval+, there was no benefit to destroy. On a docs-required benchmark the
sign flips by construction: closed-book ≈ 0, so at F16 the context benefit Δ is potentially
near the whole score (~+0.9 if the model can exploit docs at all). **For the first time there
is headroom for quantisation to destroy a context benefit**, making Phase 2's ladder a novel
measurement BEFORE any training runs:

- **Branch (a) — untrained models show usable Δ at F16:** walk the ladder and compare the
  FAB docs-conditioned curve against the (already-measured) HumanEval+ closed-book generation
  curve per model. Same-rung break = more collapse-rung-signature evidence on a new capability;
  earlier break = context-exploitation is the MORE quantisation-fragile capability — consistent
  with the dissertation's 7B evidence that the open ladder degrades faster than the closed one,
  and the sharpest available extension of it. **The 1.5B's Q2_K rung is the cell of interest.**
- **Branch (b) — Δ ≈ 0 even at F16:** the dissertation's "cannot exploit even ideal context"
  finding extends to necessary-context tasks — its strongest possible form — and RAFT becomes
  the enabler rather than the enhancer; the ladder question then re-runs on the RAFT'd model
  (the H4b analogue: does the TRAINED benefit survive the ladder, and where does it break?).

Either branch produces the study's headline figure; the branch itself is a finding. Register
the branch logic and the per-rung Δ comparison in the Phase-2 protocol before any scored run.

## Phase 3 — RAFT training (the intervention)

- **Recipe (Zhang et al. 2024, arXiv:2403.10131 — v2 "Preprint, Under Review"; venue check
  owed per D26):** train on (question + relevant doc + distractor docs → answer) with a
  fraction of examples carrying no relevant doc; answers cite verbatim from the relevant doc,
  chain-of-thought style. Adapt to code: (problem + API-doc chunks + distractors → solution
  code), solutions referencing the doc'd API correctly.
- **Data synthesis: fully local** (E4 resource analysis holds) — Apache-2.0 mid-size Qwen
  teacher on the 32GB Mac generates problems+solutions against the invented API docs;
  **execution-filtered** (generated unit tests must pass) before admission; low thousands scale;
  train-split APIs only.
- **Controls (the E4-α lessons, binding):**
  1. **No-docs fine-tune control arm** — same problems, docs stripped: separates "learned to
     use docs" from "memorised the training APIs" (held-out APIs make this arm ≈ 0 if RAFT's
     mechanism is real).
  2. **Composition gate** — the tuned model must STILL pass closed-book HumanEval+ within
     margin of base (the only-that/mode-collapse guard) before any other cell is scored.
  3. **Gate batteries, not loss curves** — val loss was blind twice in E4-α; behaviour is
     scored only on the deployment-shaped battery.
- **Then the novel ladder (the E5 headline):** merge-then-quantise the RAFT model down the
  naive ladder + an imatrix arm. Questions nobody has measured: does trained
  context-exploitation survive quantisation? At which rung? Does E2b's "harm follows the
  cliff" become "benefit falls off the cliff"? Does calibration move it?

## Phase 4 — the assistant tie-in (the want, scoped honestly)

If Phase 3 lands: wire the RAFT model into the editor-completion scaffold (the sanctioned demo
harness) with docs retrieval over the fictitious library → the first measured edge coding
assistant with working context-use, on instruments that can prove it. Repo-context (VS-Code-
style) generalisation is explicitly a SEPARATE follow-on — different context distribution,
untested transfer (recorded boundary, not scope creep).

## Resources / ethics / governance

- **All compute + tooling in hand:** Mac MLX LoRA, E1/E1-R harness, chunker/BM25, EvalPlus
  runner, contamination sweeps, llama.cpp b9951 (or a NEW pinned build — decide + record; the
  b9951 pin belongs to the dissertation, a fresh project may re-pin).
- **Ethics:** same Self-Assessment shape (no human data; synthetic data from local open models;
  licences verified at source). If results are released (model or benchmark), the dual-use and
  release questions get substantive answers (benchmark release is LOW risk and HIGH value —
  a fictitious-API benchmark is contamination-proof for future users too).
- **Calendar: realistic 8–12 weeks part-time.** Sequencing: nothing before dissertation
  submission except reading (Zan §4, Zan 2023, RAFT in full) and this spec's refinement.
  Formative asks Seema the forward question: is this PhD-proposal-shaped?
- **Prerequisite reading before Phase 1 design freezes:** Zan 2022 §4 (construction method),
  Zan 2023 (LLM-era update), Zhang 2024 RAFT (full; venue check), DocPrompting §4 (re-read:
  pool construction), + a fresh staleness sweep ("docs-required code benchmark", "private
  library benchmark 2025/2026" — the field may have moved).
