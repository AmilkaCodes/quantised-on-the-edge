# E1 Condition D results — agentic tool-use probe (RQ1c): GATE FAILED at F16; probe stopped

**Run:** 2026-09-12, Mac, Qwen2.5-Coder-1.5B-Instruct **F16**, first 20 HumanEval+ problems —
the pre-registered gate (protocol §5, commit `8375d3c`; harness committed `19e85ac` *before* the run).
Mechanism: llama.cpp b9951 `--jinja` chat-template tool-calling (one sandboxed tool,
`search_docs(query)` → top-2 chunks from the same frozen index as Condition B), greedy/seed-0, max 4
assistant turns. Raw data: `results/mac/agentic_qwen2.5-coder-1.5b-instruct_F16/`
(`transcripts.jsonl` + `summary.json`).

## Gate result

| metric | value | gate criterion |
|---|---|---|
| **M1 — valid structured tool-call rate** | **0/20 (0%)** | pass ≥ 50% → **FAIL** |
| M2 — loop outcomes | completed 20/20 (all single-turn, no tool use) | — |
| M3 — pass@1 given valid tool phase | undefined (no valid tool phases) | — |
| overall pass@1 (canonical oracle) | **0.90 (18/20)** | — |

**Per the binding pre-registration: gate FAIL → the ladder probe does NOT run.** The F16 floor is the
RQ1c finding.

## What actually happens (instrument-fairness verified)

1. **The instrument is sound.** `/apply-template` confirms the rendered prompt carries the tool schema
   and explicitly instructs the Qwen format ("return a json object … within `<tool_call></tool_call>`
   XML tags"); llama-server's parser converts correctly-wrapped calls into structured `tool_calls`.
   The model was properly instructed and the channel works — the failures below are model behaviour.
2. **Unforced, the model ignores the tool entirely** — 20/20 episodes are single-turn direct answers
   with no tool attempt of any kind (not even a malformed one), scoring 0.90, i.e. its normal
   closed-book competence.
3. **Forced (`tool_choice: "required"`, diagnostic side-probe), it cannot produce the format:** it
   emits the call as a plain-text ` ```json ` block *without* the instructed `<tool_call>` wrapper —
   invisible to the parser — then **degenerates into newline repetition to the token cap**
   (finish_reason `length`; the Yu-et-al-style degeneration signature). So the failure has two layers:
   the instruction to use tools does not bind, and the native call format is beyond the model even
   under coercion.

## RQ1c answer (one line)

**For this edge-class model, reliable structured tool use is absent at full precision — the agentic
paradigm breaks before quantisation ever gets a chance to break it** (M1 = 0% at F16; the
"which rung does it break at" question is moot). Generation quality is intact at the same moment
(0.90 closed-book), so **tool operation breaks before generation** — the ordering RQ1c asked about,
answered at the floor.

## Synthesis with Condition B

The two conditions now tell one coherent story: **imposed** documentation context measurably *hurts*
this model class (Condition B: Δ ≤ 0 everywhere, worst at the collapse rung), and the **asked-for**
context mechanism is one it *cannot operate* (Condition D: 0% valid calls, format collapse under
coercion). Closed-book is not merely adequate for a 1.5B edge coder — it is the only mode the model
can actually drive. This is the calibrated expectation (TinyAgent's off-the-shelf failures; Taheri's
small-model function-calling craters) landing at its predicted floor, with the added nuance that the
model *knows better than to try* unforced.

## Limits (honest scope)
- One model (Qwen-1.5B; Phi-3 excluded by design — no real function-calling training), 20 problems,
  one tool, one mechanism (b9951 chat-template tool-calling), one prompt wording (fixed in the
  committed harness before the run). A fine-tuned-for-tools small model, a different call format
  (e.g. prompted-JSON with grammar constraints), or larger K could move M1 — that is future work, not
  a defect of the gate: the gate measured the *stock agentic paradigm* as deployed engines support it.
- "Ignores the tool" is itself prompt-sensitive; the forced-mode diagnostic exists precisely to
  separate "won't" from "can't" — both were observed, at their respective layers.
- Per the escalation rule, no expansion follows without a new logged decision + supervisor input.
