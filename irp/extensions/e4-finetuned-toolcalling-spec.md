# E4 — Fine-tuned tool-calling under quantisation (FUTURE-WORK SPEC, not activated)

**Status: SPECIFIED ONLY (2026-09-13). Not in scope for this dissertation** (scope hold of
2026-09-13 stands; escalation rules bind). This spec exists so the dissertation's Future Work
section can present a designed study rather than a wish, and so the follow-on (post-submission
project / publication / PhD seed) starts from a plan. **The E1/E1-R instrument stack — grammar,
frozen index, contamination sweeps, harness, metrics, analysis machinery — is the laboratory
this study would reuse; its marginal cost is the training.**

## Research question (RQ4-shaped)
Can task-specific fine-tuning restore reliable tool use in edge-class models — and does the
restored capability survive quantisation?
- **H4a:** fine-tuned ≫ raw at F16 tool use (expected; TinyAgent is the existence proof).
- **H4b (the novel unknown):** the fine-tuned tool-calling capability degrades down the
  quantisation ladder — at the same rung as generation quality, earlier, or later? Nobody has
  measured this.

## Design sketch
- Base: Qwen2.5-Coder-1.5B-Instruct (same base as the raw arm → clean comparison).
- Intervention: LoRA fine-tune for `search_docs`-style function calling; merge; then quantise
  the merged model down the SAME naive ladder (recipe decision: merge-then-quantise, recorded).
- Comparison: 2×5 factorial (fine-tuned vs raw × 5 rungs) on the E1-R instruments —
  M1/M1′/M2′/M3 + pass@1 vs Conditions A/B/O; raw Phi-3 as the general-model reference arm.
- Compute: LoRA at 1.5B feasible on the Mac (MLX) or one rented GPU; days not weeks of GPU time.
- Realistic total effort: 3–5 weeks (data verification → training + iteration →
  decontamination → evaluation battery).

## Ethics delta (what changes vs the current all-No position)
1. **Training data is the new centre of gravity.**
   - CLEAN paths: an openly-licensed existing function-calling dataset (verify licence AT
     SOURCE, per house discipline; check for scraped/personal content), or synthesis using a
     permissively-licensed OPEN model's outputs.
   - TRAP path: synthesising with frontier-API models (GPT-4/Claude) — provider terms restrict
     using outputs to train models; Section 4's "checked the T&Cs" could not be a clean Y.
2. **Self-Assessment route survives** with an open dataset: Section 4 gains dataset + licence;
   Section 5 stays all-No (no human data) — but re-run the form for the new project regardless.
3. **Model RELEASE (if open-sourced) is a new question:** answer the dual-use item
   substantively (releasing an artefact ≠ measuring one; low risk at 1.5B — say so, don't
   reflex-No), and note the responsibility for downstream misuse framing (cf. Egashira:
   quantisation itself is an attack surface — a released model invites local quantisation).
4. **Environmental proportionality extends to training compute** (LoRA-scale: modest; state it).
5. **New contamination surface:** decontaminate training data against HumanEval+ AND the
   tool-call eval set (train/test hygiene joins the sweep discipline; Brown-style n-gram
   checks apply).

## Resource analysis (2026-09-13): fully local, fully open — no frontier APIs needed
- **Data, path 1:** openly-licensed function-calling datasets (e.g. Glaive FC v2, commonly
  Apache-2.0; Hermes FC and others — VERIFY LICENCES AT SOURCE before use, house rule).
- **Data, path 2 (thematically perfect):** local synthesis — the 32GB Mac runs an Apache-2.0
  mid-size Qwen (14B comfortably; 32B at Q4) as the teacher. No API, no ToS clause, no data
  leaves the bench: a local model bootstrapping a local model.
- **Data scale is SMALL:** one tool (`search_docs`) — a few thousand curated examples, not
  TinyAgent's 80K general-API corpus. The pipeline collapses accordingly.
- **Training:** MLX LoRA on the Mac — hours-per-run for the 1.5B (3.8B feasible); no rented
  GPU required. Model licences explicitly permit fine-tuning (Qwen Apache-2.0, Phi-3 MIT).
- **Evaluation:** the E1/E1-R laboratory, unchanged.
- **Conclusion: every resource is in hand except calendar time (3–5 weeks).** This
  strengthens rather than weakens the scope hold — feasibility is not the constraint;
  the dissertation deadline is.

## Why not now (recorded once, bindingly)
12 weeks remain; the write-up owns ≥6; 3–5 weeks of training-project risk cannot fit without
endangering the dissertation. The measured E1/E1-R results are the contribution; this spec is
their forward edge. Any change to this status = supervisor conversation first.
