# E4-α — Fine-tuned tool-calling, F16 gate (CLOSED 2026-09-14: FAIL, reportable)

**Registration:** `irp/extensions/e4-finetuned-toolcalling-spec.md` (activation amendment
2026-09-14; α closure recorded there same day). Both permitted training iterations used;
β (H4b quantisation ladder) gated off; further iteration is formative-feedback-gated.

## What was trained

| | Run 1 | Run 2 (final α iteration) |
|---|---|---|
| Data format | prompt/completion pairs of pre-rendered template text | **native ChatDataset `{messages, tools}`** per assistant turn |
| Flags | (default) | `--mask-prompt` (loss on final assistant turn only) |
| Data | Glaive FC v2 (apache-2.0, sha e9b5d671), seed 0, rebalanced to 46.7% call share; 1,400 call + 1,600 reply train / 150+150 valid; 13-gram-clean vs HumanEval+ AND MBPP+ (0 drops) | same source/seed/rebalance, re-emitted native + re-swept (0 drops); train sha 340309c5, valid sha 1826740e |
| Hyperparams | iters 800, batch 4, num-layers 16, seed 0 (`e4/e4-run1-config.json`) | identical + `--mask-prompt` |
| Val loss | 0.237 — **a liar** (measured template-text prediction on double-templated data) | 0.406 — honest, and **also uninformative** (see method lesson) |
| Outcome | instrument artefact: double templating taught "assistant-start → EOS" (dated deviation in spec) | genuine behavioural change; gate FAIL on the merits (below) |

Pipeline: `mlx_lm lora` (isolated e4-venv) → `mlx_lm fuse` → `convert_hf_to_gguf.py` →
F16 gguf served by the study's llama-server b9951 `--jinja` — the same instrument stack as
E1/E1-R (configs/mac-e4-gate.yaml, cap 2048, K=20).

## Gate results (K=20, HumanEval subset, both mechanisms)

| Cell | M1 valid | M2 outcomes | M3 | overall pass@1 | Gate |
|---|---|---|---|---|---|
| e4r2 F16 **native** | **0.00** | completed 16 · malformed_abandonment 4 | — | **0.00** | FAIL |
| e4r2 F16 **json** | **0.00** | completed 19 · degeneration 1 | — | **0.00** | FAIL |
| stock 1.5B F16 native (E1 baseline) | 0.00 | degeneration-dominated under coercion | — | (Condition A pass ≈ 0.61 closed-book) | — |
| Qwen3-4B F16 forced (E2a existence proof) | 0.80 | — | 1.0 | — | — |

## The decomposition (transcript-verified, all cells)

1. **Spontaneous call emission: ACHIEVED.** Probes (MLX adapter + fused gguf on llama-server)
   yield an unforced turn-1 `{"name": "search_docs", "arguments": {"query": "python prime
   number check"}}` — sensible payload, domain-transferred from Glaive's currency/news tools
   to the unseen `search_docs`. This is the exact behaviour stock 1.5B could not produce at
   any coercion level (E1: forced → degeneration 20/20).
2. **Wrapper token: NOT learned.** Calls arrive as bare JSON in `content`; MLX shows
   `<|im_start|>` where `<tool_call>` belongs; server parser → `tool_calls: null`. Native M1
   therefore reads 0 even where the payload is perfect (an E1-R echo: the wrong-wrapper
   failure class, now produced *by training* rather than despite it).
3. **Task-conditioned mode collapse — the headline.** First-turn taxonomy, native cell
   (n=20): **16 bare-JSON calls to the task's own function** (e.g.
   `{"name": "has_close_elements", "arguments": {...example inputs...}}`), **4 to
   search_docs**, **0 code**. The call is the model's final answer; no code ever follows.
   The json-mechanism cell degenerates differently (a memorised `!git clone` snippet 19/20).
4. **Control — no tools in context: coding INTACT.** The same gguf, same server, same
   HumanEval/0 prompt without a tools block → correct prose + correct function body.
   Coding is not forgotten; **the presence of tools switches it off**.

**Verdict: fine-tuning inverted the failure rather than repairing it.** Stock = *codes,
never calls*. e4-tuned = *calls, never codes*. E2a's can't (1.5B) / won't-by-policy (4B)
axis gains a third pole: **only-that** — at LoRA-1.5B scale the invocation-policy lever and
the task-completion lever moved together, not independently.

## Why (recorded hypothesis, not asserted)

Every Glaive-derived training example ends at an assistant turn with loss masked to that
turn; 46.7% end in a call; user turns are short chat requests. The set contains **zero
"tools present + long technical task → write code" examples**, so the learned policy
over-generalised: *tools in context ⇒ emit one call and stop*. The spec's pre-authorised
fix — a small locally-synthesised `search_docs`-domain supplement whose episodes continue
through the tool response into a *code* answer — targets exactly this, but is iteration 3
and therefore formative-feedback-gated.

## Method lessons (for the methods chapter)

- **Run 1:** validation loss on malformed (double-templated) data is a liar — 0.237 while
  the model had learned "assistant-start → EOS".
- **Run 2:** validation loss on *well-formed* data is honest and still blind — 0.406 while
  the model had learned to abandon its primary task whenever tools appear. Completion loss
  cannot see policy inversion because the held-out set shares the training distribution's
  blind spot. **Gate batteries on the deployment task are the only trustworthy readout for
  behaviour-targeted fine-tuning.**
- Instrument-fairness discipline paid twice: run 1's FAIL was rejected (artefact, root-caused
  to mlx_lm's CompletionsDataset re-templating); run 2's FAIL was accepted only after the
  no-tools control isolated the mechanism.

## Status of H4a / H4b

- **H4a (fine-tuned ≫ raw at F16 tool use): not demonstrated at this recipe/scale.** The
  ingredient behaviours (call emission, payload quality, domain transfer) were produced;
  their composition with task completion was not.
- **H4b (does trained tool-calling survive quantisation?): unmeasured — remains the novel
  open question**, now with a sharpened premise: the artefact to ladder must first pass a
  composition gate, which naive FC-LoRA at 1.5B does not.
