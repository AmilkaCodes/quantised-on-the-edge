# E2a PROTOCOL — model-scale arms: tool-trained gate rerun (Arm 4) + Mac-only 7B ladder (Arm 5)

**Status: PRE-REGISTERED BY COMMIT.** Parameters below are fixed BEFORE any E2a measurement; later
changes are dated amendments committed before the affected run.

> **ACTIVATION (2026-09-13, student decision):** Arms 4 and 5 of `e2-proposal.md` are activated ahead
> of the October supervision meeting — the student judges it early enough to secure supervisor
> agreement to scope changes, mirroring the E1 gate-2 precedent (runs proceed, supervisor briefed,
> any objection triggers re-examination of the affected runs). **Ethics delta: nil** — two additional
> public open-weights models on the same public benchmark + already-approved corpora; no participants,
> no personal data (Section-5 answers unchanged; one-line note for the ethics record).
> Arms 1–3 of e2-proposal.md remain NOT activated.

## 0. Constants (inherited unless stated)
Engine llama.cpp **b9951** pinned (Mac Metal build) · greedy, seed 0 · HumanEval+ (EvalPlus) ·
Mac quality axis (36 GB — F16 anchors fit; D4/D25 proxy logic) · provenance manifest per run +
this protocol's commit hash · all outcomes reportable (research symmetry).

## 1. Arm 4 — is the agentic floor TRAINING or SCALE? (RQ1c follow-up; descriptive)
**Question:** the Condition D gate failed at F16 with a non-tool-trained 1.5B coder (M1 = 0/20).
Does a function-calling-trained small model pass the same gate — and does a prompted-JSON framing
(Taheri's IFFC result) rescue calling even for the non-tool-trained model?

- **4a — native-template gate, tool-trained model.** Model: **Qwen3-4B** (function-calling-trained;
  Taheri's small-model sweet spot), GGUF **F16 from bartowski** (D7 consistency; exact file + sha256
  recorded in the runbook at download). Same harness (`e1_agentic.py`), same tool, same first-20
  problems, max 4 turns, **generation cap 2048 tokens for this probe only** (the model may emit a
  reasoning trace; the 768 study cap would truncate it — probe-local parameter, recorded). Thinking
  behaviour left at the model template's default; the rendered template is captured in the run log.
- **4b — prompted-JSON (IFFC-style) condition, BOTH models at F16.** No `tools` parameter: the tool
  is described in plain instruction text and the model is asked to reply with exactly one JSON object
  `{"name": "search_docs", "arguments": {"query": "..."}}` when it wants the tool, else the final
  answer. Parser: first syntactically valid JSON object in the reply with those keys. Same
  M1/M2/M3 definitions (M1 = valid parse + correct name + non-empty string query on the first turn).
  Models: Qwen3-4B and Qwen2.5-Coder-1.5B-Instruct → with 4a and the original D gate this yields a
  **2×2: (tool-trained vs not) × (native template vs prompted-JSON)**.
- **Metrics/report:** M1/M2/M3 per cell, descriptive; the E1 gate's ≥50% M1 line is the comparison
  reference, not a go/no-go (this probe IS the experiment). **Timebox: one bench day.**

## 2. Arm 5 — in-family scale: Qwen2.5-Coder-7B-Instruct ladder (Mac-only)
**Question:** does scale (1.5B → 7B, same family, specialisation held constant) move the collapse
threshold, and does it dissolve the open-book context harm? (Tests Yazan's optimistic 7B headline
with execution scoring into the sub-4-bit region his FP16-vs-AWQ design never reached.)

- **Model/artefacts:** F16 GGUF from **bartowski** (file + sha256 recorded at download);
  self-quantised **naive ladder at b9951, no imatrix (D6): Q8_0, Q4_K_M, Q3_K_M, Q2_K** — identical
  recipe to the 1.5B/3.8B.
- **Runs (Mac only; edge cells explicitly out of scope for now — 7B does not fit the study's edge
  envelope at F16/Q8-Jetson and is deferred):**
  1. Closed-book quality: 5 rungs × 164 (`--condition closed`).
  2. Open-book quality: 5 rungs × 164, **same frozen artefact byte-identical** (`--condition open`).
  3. Optional Mac perf cells per rung (tok/s, TTFT, RSS, powermetrics) — cheap, run if time allows.
- **Analysis (same machinery, same scripts extended):** pass@1 plus from per-problem eval_results;
  **5pp margin vs the 7B's OWN F16** + McNemar F16-vs-rung (per condition) → per-condition collapse
  threshold; within-rung McNemar open-vs-closed + bootstrap CIs on Δ(B−A) → the scale × context
  interaction.
- **Pre-stated expectations (exploratory-confirmatory, both reportable):**
  H-A5a: the 7B threshold sits at Q2_K or deeper (no earlier collapse than the 1.5B).
  H-A5b: the open-book harm shrinks at 7B relative to the 1.5B (Yazan's model-strength mechanism);
  a NON-shrinking harm would be the stronger finding (context fragility not rescued by scale).
- **Timebox: three bench days** (download + quantise + 10 quality cells + analysis); overrun → stop
  and report whatever completed.

## 3. Order of work
Downloads + sha256 → 4a gate → 4b 2×2 → 7B quantise ladder → closed sweep → open sweep → analysis →
single results doc (`irp/analysis/e2a-results.md`). Config for the new models lives in
`configs/mac-e2a.yaml` (the registered study configs are untouched).

## 4. Deviations
_Dated, before the affected run where foreseeable._

- **2026-09-13 (before any Arm-4 run):** bartowski ships Qwen3-4B's full-precision GGUF as **bf16**
  (`Qwen_Qwen3-4B-bf16.gguf`), not f16. The probe's full-precision anchor is therefore BF16; the rung
  is still labelled "F16" in harness output in the sense of *full-precision anchor*. Functionally
  equivalent for the gate question; recorded for exactness. (7B artefact is true f16:
  `Qwen2.5-Coder-7B-Instruct-f16.gguf`.)
