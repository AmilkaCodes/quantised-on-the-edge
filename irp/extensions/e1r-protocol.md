# E1-R PROTOCOL — instrument-modified follow-up probes (pre-registered)

**Status: PRE-REGISTERED by commit, per the escalation rule** (a new, logged decision — student
2026-09-13 — with supervisor notification and a calendar check). **The question both probes
answer: are the E1 negative results fundamental to the model class, or fixable by scaffolding?**
Runs begin only after (1) this file is committed unchanged, (2) the supervisor chase email
includes the follow-up-probe line (same data, same sandbox, no ethical delta), and (3) each
probe's artefact (grammar file / oracle prompt set + sweep report) is committed. Changes after
first run = dated amendments. **TIMEBOX (binding): all E1-R harness work AND scored runs
complete by 2026-09-20; whatever is unfinished then is dropped and recorded.** No further
expansion of either probe under any outcome (Future Work absorbs the rest).

## Constants (inherited unchanged)
Engine b9951 · greedy, seed 0 · HumanEval+ 164 / EvalPlus scoring · Mac quality axis (D25
proxy logic) · same frozen docs corpus + BM25 index as E1 (§1 of e1-protocol) · manifests
carry condition + artefact hashes + this protocol's commit hash.

## Probe R1 — model-chosen retrieval under grammar constraint (RQ1c revisited)

**Design change from Condition D:** the multi-turn tool loop is replaced by a **two-stage,
single-call structure**, and syntax is guaranteed by **GBNF grammar-constrained decoding**
(a standard llama.cpp facility at b9951):
- **Stage 1:** the model, given the problem (signature + docstring) and a fixed instruction,
  generates ONE `search_docs` query — decoding constrained by a committed GBNF grammar to the
  call schema. Malformed syntax is impossible by construction (the E1 gate's failure mode —
  0/20 wrong-wrapper — is eliminated at the decoder).
- **Stage 2:** the top-2 BM25 chunks for the model's OWN query are injected exactly as in
  Condition B, and the model answers. Scoring unchanged.
- This makes R1 directly comparable: **A** (no context) vs **B** (fixed BM25 context) vs
  **R1** (model-chosen context) — same problems, same k, same injection format.

**Metrics:**
- **M1′ semantic query quality** (replaces M1, which the grammar satisfies by construction):
  a stage-1 query is *non-degenerate* iff it is non-empty, ≥3 tokens, not a verbatim repeat of
  the instruction, and contains ≥1 content token from the problem's signature or docstring
  (evaluated by script, committed before runs).
- **M2′ degeneration** in stage-2 answers (repetition / special-token anomaly, Yu categories).
- **M3 pass@1** per rung, paired vs A and vs B (McNemar + bootstrap CIs, 5pp margin per
  condition — the §4 machinery unchanged).

**Gate (runs first): Qwen2.5-Coder-1.5B-Instruct, F16, 20 problems → pass iff ≥50% of
stage-1 queries are non-degenerate (M1′).** Fail → probe stops; the finding ("even with
guaranteed syntax, the model cannot formulate a usable query at F16") is written. Pass →
**ladder: Qwen only, 5 rungs × 164** (full set, to enable exact pairing with A and B).
Phi-3 excluded (no reliable tool/chat template — as in E1).

## Probe R2 — oracle-retrieval open-book (RQ1b boundary test)

**Purpose:** E1's "context hurts" is bounded by frozen BM25's low recall. R2 measures the
**upper bound of retrieval quality** without adding any neural component (D27 preserved):
- **Oracle selection:** for each problem, rank ALL corpus chunks by normalised content-token
  overlap with the problem's **canonical reference solution**, take top-2. The solution is
  used ONLY to select which genuine documentation chunks appear; no solution text enters any
  prompt. **This is a measurement instrument (upper bound), never a deployable system — and is
  labelled as such wherever reported.**
- **Contamination guard unchanged:** the oracle prompt set passes the same 13-gram-fail /
  8–12-gram-report sweep before commit (selection-by-solution makes this guard MORE important,
  not less; any 13-gram hit → next-ranked chunk).
- **Runs: both models × 5 rungs × 164**, oracle condition (O), Mac.
- **Analysis:** per-rung paired McNemar O-vs-A and O-vs-B + CIs + margins. Pre-registered
  interpretation map: **O > A** → E1's distraction cost was retrieval quality (docprompting can
  help; future-work direction = better retrieval). **O ≤ A (hurts even with perfect
  selection)** → quantised small models cannot exploit context even when it is ideal — the
  strongest form of the RQ1b finding. **O ≈ B** → selection quality is not the lever. All
  outcomes reportable (research symmetry).

## Reporting
Both probes report in `irp/analysis/` (e1r-agentic.md, e1r-oracle.md) with the same claim
discipline as E1; RQ1b/RQ1c entries in `research-questions.md` gain dated REVISIT clauses;
the write-up presents E1 + E1-R together as "failure mode → scaffolding test", with the
fine-tuning path (TinyAgent route) remaining Future Work regardless of outcome.

## Deviations
_Dated, before the affected run where foreseeable._
