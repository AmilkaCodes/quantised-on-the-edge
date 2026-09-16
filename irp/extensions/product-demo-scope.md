# Product-demo branch — scope, design record, and gating (2026-09-16)

**Branch `product-demo`, cloned from `extended-work` at stage-V close (a5bba6b)** so every
material the demo needs travels with it: the FAB instrument + validity case, all harnesses
(fab_run, run_pilot, docs_index/BM25, GBNF grammar, execution scorer), the imat artefact
recipes, the per-tier perf CSVs, and the full analysis set. This document is the note of the
2026-09-15/16 discussions (recorded before any build, per house rule) and the branch's
governing scope.

**GATE LIFTED for demo scaffolding + ring-1/2 tests (2026-09-16, student directive: "proceed with the necessary demo scaffolding and tests"; student reviewing in detail).** The user-study and token-economics gates below stand unchanged. Original gating text (superseded for scaffolding/tests only): nothing on this branch executes until the dissertation's methods+results
drafts are on track (the 2026-09-28 lien). `main` = write-up; `extended-work` = closed
measurement record (its stage-V hard state is unchanged by this clone); `product-demo` = the
applied endpoint, assembled later. A user study is post-submission only (ethics: human
participants flips the Self-Assessment from all-No — form redo + supervisor sign-off first).

---

## Part 1 — the demo: a local code assistant in VS Code, prescribed by the evidence

**Concept (student's, 2026-09-15):** an end product that works in VS Code and helps finish
code, running entirely on local hardware. Assessment: not a new design problem — **the study
already prescribes the configuration**; the demo's value is that every choice cites a
committed measurement.

### Architecture (three pieces, two already exist)
1. **Serving:** llama-server b9951 (the study binary on all three devices) — OpenAI-compatible
   API + `/infill` for fill-in-the-middle (Qwen2.5-Coder is FIM-trained: mid-line completion,
   not just chat).
2. **Editor client:** no extension needs writing — Continue (Apache-2.0) or llama.vscode point
   at a local llama-server via config. A custom thin extension is optional UX polish only.
3. **The recipe = the research:** imat-quantised artefact, tier-matched size, scaffold-side
   retrieval only when docs are necessary, no agentic tool loop.

### Tier table (all figures from committed CSVs; SLO floor ≥8–10 tok/s)
| tier | model | disk | RAM in use | measured speed | verdict |
|---|---|---|---|---|---|
| Mac | 7B imat-Q4 (or Q2) | 4.7 GB | ~5 GB | ~56 tok/s | comfortable |
| Jetson 8 GB | 7B imat-Q2 | 2.9 GB | ~3.7 GB | 11.1 tok/s | **7B: yes** |
| Pi 5 16 GB | 1.5B imat-Q4/Q2 | 0.65–1 GB | ~1.1 GB | 14.5 tok/s | **7B: no (max 3.4 tok/s, E2c) — 1.5B ships** |

imat costs nothing at inference (R2: tok/s/RSS/power identical to naive on both devices) →
never ship naive quants.

### Product rules imposed by the findings
- No context injection into self-contained completions (imposed-context harm, every scale).
- When docs are needed: BM25 over pinned docs, k=2 (R ≈ B on FAB at every rung).
- Never a terse single page to a collapse-rung model (R1b + stage-V: fixation is terse-page-
  shaped; Sphinx-style rich pages are safe).
- No tool-calling loop in the model (can't/won't/only-that); orchestration is deterministic
  scaffold.

### Test plan (three rings, cheapest first)
1. **Bench replay:** existing lab vs the served product config (HumanEval+ closed, FAB, perf
   harness SLOs) — all committed code, ~a day.
2. **Editor-loop measurement:** keystroke-to-first-token + suggestion latency inside VS Code
   per tier (small new script; the only unmeasured quantity).
3. **Dogfooding** by the student (ethics-clean). **User study = post-submission + ethics
   approval** (see gating).

### Timebox
Demo assembly (Continue config + pinned artefacts + README-with-citations): **1–2 days.**
Anything beyond (custom extension, UX) is product work, out of scope for this branch's first
milestone.

---

## Part 2 — hybrid frontier/local architecture: how the local stack saves frontier tokens

**Student's observation (2026-09-16):** the study assumed frontier models for heavy work; the
local tools built for the study (docs parsing/retrieval, syntax checks, execution scoring)
are exactly what frontier agents burn tokens doing in-context. Assessment: correct, and it
inverts the framing — *frontier as the expensive specialist; local stack does everything that
doesn't need it.* Frontier agentic sessions bleed tokens in three places (context stuffing,
iteration loops, structured-output retries); each has a measured local answer:

1. **Local retrieval, hits-only across the wire.** Frozen BM25 (8,239 chunks) selects k=2
   pages locally (R ≈ B, FAB) — the frontier receives two chunks, not a manual.
2. **Local verification, error-tail-only returns.** Run code locally (subprocess + tests);
   the frontier's next turn gets a ~30-token stderr tail, not the re-pasted file. A local
   `py_compile`/lint gate means trivially-broken drafts never reach the API.
3. **Local-first generation, escalate-on-fail.** 7B@imat-Q2 = 0.793 HumanEval+ closed at
   2.9 GB → ~4 in 5 self-contained tasks never touch the API; the escalated fifth arrives
   with its failing test attached (a better prompt than the raw task). The E1
   capability-forced handoff, run in reverse as a cost policy.
4. **Structured output is local.** GBNF grammar → M1′ 0.988: guaranteed-valid JSON from a
   1.5B for extraction/formatting/boilerplate; never pay frontier rates for schema-filling.
5. **The router is dumb by design.** The evidence forbids local-model orchestration
   (can't/won't/only-that): frontier plans + writes hard code; local models generate and
   format; deterministic scaffold retrieves, checks, runs, and routes on static rules.

**Caveats (recorded, not glossed):** a local "does this need docs?" necessity gate is
unmeasured (keep it rule-based: unknown import → retrieve); local summarisation-for-frontier
is untested and suspect under the imposed-context findings; the savings arithmetic is
structural, not yet measured in tokens.

## Part 3 — the registered-but-gated experiment: hybrid token economics

**Design (frozen now; execution gated per the top of this file):** same task set, two arms —
(a) frontier-only agentic baseline; (b) local-first hybrid (rules-routed, mechanisms 1–5).
**Outcomes:** API tokens billed, pass rate, wall-clock, $ per solved task. Novel, cheap-ish,
and the direct "why edge models, in money" answer. Ethics: frontier API use for *measurement*
is inside the standing posture (the TRAP — training on frontier outputs — stays closed);
API spend is the student's call at execution time. Instruments: the existing task sets and
harnesses on this branch; the only new code is the router and a token-accounting wrapper.

## Materials manifest (all present on this branch via the clone)
- Instrument: `proposal-dev/pilot/e5/` (fab_build/fab_run + fab, fab_v2–v4, fab_r1,
  families_sphinx/dense; manifests with shas)
- Scaffold: `proposal-dev/pilot/e1/docs_index.py` (BM25 + chunker), `search_call.gbnf`
- Harnesses: `run_pilot.py` (perf + conditions + EvalPlus scoring), execution scorer in fab_run
- Artefact recipes: imatrix files + quantise provenance (E2b), per-device configs in
  `proposal-dev/pilot/configs/`
- Evidence base: `irp/analysis/` (consolidated summary, validity case + measured external
  validity, stage analyses), `irp/extensions/` (registrations + decision log)
