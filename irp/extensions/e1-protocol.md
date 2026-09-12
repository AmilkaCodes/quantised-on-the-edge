# E1 PROTOCOL — open-book (RQ1b) + agentic probe (RQ1c)

**Status: PRE-REGISTERED by commit.** This document fixes every parameter BEFORE any E1
measurement. Runs may begin only after (1) this file is committed unchanged and (2) the
supervisor acknowledges the amended ethics form. Any later change is a dated amendment
committed BEFORE the affected run, with rationale (deviation discipline as usual).

> **AMENDMENT 2026-09-12 (gate 2, student decision):** the amended ethics form was emailed to
> the supervisor 2026-09-12. The amendment changes no Section-5 answers (no participants, no
> personal data; one additional public, PSF-licensed corpus) — it is administrative diligence
> on an already-approved form, not a new permission request. **Decision: runs proceed pending
> acknowledgment**; the student will chase before the October supervision meeting, and any
> supervisor objection triggers re-examination of the affected runs. Rationale mirrors the
> RP-era precedent: scope and approval are kept aligned in the record, and the ethical
> substance was approved 2026-09-11.
_For the student to review and own before first run; refine wording freely — parameter values
change only by amendment._

## 0. Constants (inherited from the main study — unchanged)
Models: Qwen2.5-Coder-1.5B-Instruct, Phi-3-mini-4k-instruct · Ladder: F16, Q8_0, Q4_K_M,
Q3_K_M, Q2_K (naive llama-quantize, same artefacts as closed-book) · Engine: llama.cpp
**b9951** pinned, per-device builds as recorded · Decoding: greedy, seed 0, same generation
cap and stop conditions as the closed-book runs · Benchmark: HumanEval+ full 164, EvalPlus
scoring · Quality axis on the Mac (D25 aggregate-proxy logic; one cross-device spot-check of
K=25 open-book generations after the first full sweep) · Provenance manifest per run + the
open-book artefact's git commit hash.

## 1. Documentation corpus (Condition B + D shared)
- Source: official Python documentation, **one pinned version** (the 3.12 series docs as
  downloaded; record exact version string + retrieval date in the manifest).
- Scope: Library Reference + Language Reference + Tutorial (prose pages, plain-text
  extraction); no third-party content.
- Chunking: split on documentation section boundaries; any section > **1,500 characters** is
  split at paragraph boundaries into chunks ≤ 1,500 characters. No overlap.
- Index: **BM25** (rank_bm25 BM25Okapi, default parameters k1=1.5, b=0.75), lowercased
  whitespace/punctuation tokenisation. No embedding models anywhere in the pipeline (D27).

## 2. Condition B — frozen open-book prompts
- Query per problem: the problem's **signature + docstring, verbatim**.
- Retrieval: top **k = 2** chunks per problem.
- Prompt layout: [chunk 1]\n\n[chunk 2]\n\n[unchanged closed-book prompt]. Nothing else changes.
- Budget check: retrieved chunks + prompt + generation cap must fit **4,096 tokens** (Phi-3
  window); if a problem exceeds it, truncate chunk 2 (never the problem) and log the truncation.
- The 164 augmented prompts are generated ONCE on the Mac, saved as a single artefact
  (`openbook_prompts.jsonl`), contamination-swept (§3), then **committed**. All runs on all
  devices consume this artefact byte-identically.
- **Pre-registered expectation (stated for honesty, not tested):** the F16 open-book lift is
  expected to be MODEST — DocPrompting reports BM25 recall@10 ≈ 9.7% on Python-style intents
  (dense ≈ 56%) — and RQ1b's question is the INTERACTION down the ladder, not the size of the
  lift. A near-zero F16 lift is itself reportable (frozen sparse retrieval adds little for
  self-contained HumanEval+ problems) and does not abort the sweep.

## 3. Contamination sweep (pre-run validity gate for Condition B)
- Method (after Brown et al. 2020, §4/App. C precedent): n-gram overlap between EVERY retrieved
  chunk and EVERY canonical HumanEval+ reference solution, on normalised text (lowercase,
  collapsed whitespace).
- **Fail criterion: any shared 13-gram** between a chunk and any canonical solution → that
  chunk is replaced by the next-ranked BM25 chunk (and the sweep re-runs on the replacement).
- **Report threshold:** shared 8–12-grams are counted and reported (not failed).
- Output: a committed sweep report; the thesis line "no retrieved chunk shared a ≥13-gram
  overlap with any reference solution" must be literally true of the final artefact.

## 4. Condition B runs + analysis (RQ1b / H1c)
- Runs: 2 models × 5 rungs × 164 problems, open-book, Mac quality axis; same harness, CSV
  schema + `condition` column.
- Analysis (mirrors the closed-book machinery): per-rung pass@1 with bootstrap 95% CIs
  (B=10,000, seed 0); **within-rung paired McNemar, Condition B vs A** (same 164 problems);
  per-condition collapse thresholds via the pre-registered 5pp margin; **headline: the
  interaction** Δ(B−A) per rung, with all three outcomes reportable (benefit survives /
  shrinks / inverts — research symmetry).
- Optional perf tie-in (after quality sweep): per-tier TTFT + peak-memory cells at Q4_K_M
  open-book vs closed-book (the memory price of context on the 8GB edge).

## 5. Condition D — agentic probe (RQ1c; exploratory, gated)
- **Tool:** exactly one — `search_docs(query: str)` → returns the top-2 chunks from the SAME
  frozen index (§1). Sandboxed, no network, no filesystem.
- **Loop:** chat-template tool-calling as supported at b9951; max **4** assistant turns; then
  forced final answer.
- **GATE (runs first):** Qwen2.5-Coder-1.5B-Instruct at **F16**, first **20** HumanEval+
  problems. **Pass criterion: ≥ 50% of tool-expected turns produce a syntactically valid,
  schema-correct call (M1).** Fail → probe STOPS; the F16 floor is reported as a finding
  (expectation calibrated by TinyAgent's off-the-shelf failures and Taheri's Q4 crater).
- If gate passes: ladder probe — Qwen only, Mac only, **30** problems × 5 rungs.
- **Metrics:** M1 valid-call rate · M2 loop outcome per episode {completed / max-turns loop /
  hallucinated tool output / malformed abandonment / degeneration (repetition or special-token
  anomaly, categories after Yu et al.)} · M3 pass@1 conditional on a well-formed tool phase.
  Descriptive only — no hypothesis tests (RQ1c is exploratory).
- **Timebox:** harness build + validation ≤ 1 week of effort; overrun → gate closes, recorded.
- **Escalation rule (binding):** this probe IS the full RQ1c test; success does not
  auto-escalate (any expansion = new logged decision + supervisor input).

## 6. Deviations
_Recorded here, dated, as they occur — before the affected run where foreseeable._
