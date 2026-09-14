# E4 — Fine-tuned tool-calling under quantisation (ACTIVATED, STAGED — amendment below)

> **ACTIVATION AMENDMENT (2026-09-14, student decision — an explicit, dated override of the
> "supervisor conversation first" clause below):** the student elects not to wait for the October
> meeting; the **formative (October) becomes the review gate** and its feedback the supervision
> input, with the supervisor informed via the standing chase thread (same pattern as E1/E2a
> activations; ethics delta handled at stage 0 below). The override is risk-managed by STAGING:
>
> - **Stage α (activated now; runs after E2c frees the bench):** data path chosen + licence
>   verified AT SOURCE + decontaminated → **ONE LoRA training run** (MLX, 1.5B) → **F16 gate**
>   on the E1/E1-R battery (M1 native + M1′; H4a). **Hard timebox: 10 calendar days of effort;
>   at most TWO training iterations inside it.** Gate outcome either way is a reportable finding.
> - **Stage β (gated):** the quantisation ladder (H4b — merge-then-quantise, naive recipe, the
>   novel measurement) runs ONLY if the α gate passes; it is cheap (~1 bench day) once a working
>   adapter exists. Further iteration beyond α's two runs = **formative-feedback-gated**, full stop.
> - **Write-up lien (binding):** E4-α is additive, never load-bearing — the dissertation's
>   contribution remains E1/E1-R/E2a/E2b regardless of α's outcome; any week α slips, the
>   write-up claims the time back; α aborts unconditionally if the first full methods+results
>   drafts are not on track by 2026-09-28.
> - **Ethics (stage 0, before any training):** dataset licence verified at source; training data
>   decontaminated against HumanEval+ (13-gram discipline) AND disjoint from any named future
>   benchmark (MBPP+ reserved); Self-Assessment form gains the dataset/licence line (Section 5
>   remains all-No); no frontier-API synthesis (the TRAP path stays closed — local/open only).

**Original status (superseded as above): SPECIFIED ONLY (2026-09-13). Not in scope for this
dissertation** (scope hold of 2026-09-13 stands; escalation rules bind). This spec exists so the dissertation's Future Work
section can present a designed study rather than a wish, and so the follow-on (post-submission
project / publication / PhD seed) starts from a plan. **The E1/E1-R instrument stack — grammar,
frozen index, contamination sweeps, harness, metrics, analysis machinery — is the laboratory
this study would reuse; its marginal cost is the training.**

## Stage-0 record (2026-09-14, pre-training decisions — dated, fixed before any training run)
- **Data = Glaive FC v2, licence VERIFIED AT SOURCE via the HF datasets API: `apache-2.0`, ungated**
  (Hermes FC v1 apache-2.0 as fallback; xLAM excluded — gated). Format inspected: `system` block of
  JSON tool definitions + `chat` dialogues with `<functioncall>` turns AND explicit
  refusal/irrelevance examples ("I don't have the capability…") — the latter retained deliberately:
  the E2a grid showed invocation *policy* is half the deficit.
- **Transformation:** Glaive dialogues re-rendered into the Qwen chat-template hermes format
  (`<tool_call>` JSON) — training the model in exactly the wrapper the stock 1.5B failed to emit;
  sampled to the low-thousands scale per the resource analysis; a small locally-synthesised
  `search_docs`-specific supplement only if the α gate shows domain-transfer failure (dated
  decision if so).
- **Decontamination (before training):** 13-gram sweep of all training text vs HumanEval+
  prompts+canonical solutions (and MBPP+ held reserved); sweep report committed with the dataset.
- **Training stack:** ISOLATED venv (`~/pilot-work/e4-venv`, mlx-lm; study venv verified untouched
  — evalplus + pinned transformers intact). Base = `Qwen/Qwen2.5-Coder-1.5B-Instruct` HF weights
  (prefetched); pipeline = mlx_lm.lora → fuse to HF → `convert_hf_to_gguf.py` → the SAME naive
  b9951 quantise recipe (merge-then-quantise, as specified).

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

## Why E4 (tool-calling) and not RAFT (context-handling fine-tune) — sequencing rationale (2026-09-14)

The obvious thematic follow-up to the E1/E1-R/E2b headline (context-exploitation is not
scaffolding-fixable and follows residual quantisation damage) is a RAFT-style fine-tune
(retrieval-augmented fine-tuning with distractor documents; Zhang et al. 2024, arXiv:2403.10131 —
verify at source before citing). It is deliberately NOT the next experiment, for four recorded
reasons; write-up should carry this as the justification for the chosen Future-Work ordering.

1. **The current benchmark cannot detect a RAFT success.** Per the e1r-oracle caveat, HumanEval+
   problems are self-contained: context has near-zero headroom to *help*, so the best achievable
   RAFT outcome on this instrument is Δ(open−closed) ≈ 0 — and distractor training would likely
   reach it degenerately, by teaching the model to IGNORE injected context. "Harm eliminated" is
   indistinguishable from "context disregarded"; it demonstrates nothing about *exploiting*
   context. Positive exploitation requires a **docs-required benchmark** (problems unsolvable
   without the reference material) — a benchmark-construction project (design, validation, its
   own contamination story) that must precede the training project.
2. **Structurally worse contamination surface.** RAFT training data = (problem + docs → solution)
   code-generation triples — the eval set's own task family. Even 13-gram-clean, any gain invites
   the reading "more coding practice near the benchmark distribution", separable from genuine
   context-handling repair only via a no-docs control arm (doubling the training matrix). E4's
   function-calling dialogues are disjoint from HumanEval+ by construction.
3. **E4's success criterion is crisp with real headroom.** The deficit is demonstrated in-study
   at F16 (1.5B M1 0/20; degeneration 20/20 under coercion) and the capability's existence proof
   is in-study (Qwen3-4B forced M1 0.80, M3 = 1.0). Instruments exist and discriminate; H4b
   (does the trained capability survive the ladder?) is unmeasured anywhere. RAFT's readout on
   current instruments is a null dressed as a win; E4's is 0 → ~0.8 plus a novel ladder.
4. **Interpretive asymmetry.** A "successful" RAFT invites "you trained it to ignore context —
   closed-book already does that for free." A successful E4 restores a discrete, measurable
   protocol behaviour and opens a new measurement. One result defends itself.

**Status of RAFT: sequenced, not rejected.** It is blocked on an instrument that does not yet
exist (the docs-required benchmark); E4 is blocked only on the supervisor conversation. The
pairing "build the docs-required benchmark, then test whether RAFT-style training lets small
quantised models pass it" is the PhD-seed-shaped follow-on, and Future Work should present it
exactly so.

## Why not now (recorded once, bindingly)
12 weeks remain; the write-up owns ≥6; 3–5 weeks of training-project risk cannot fit without
endangering the dissertation. The measured E1/E1-R results are the contribution; this spec is
their forward edge. Any change to this status = supervisor conversation first.
