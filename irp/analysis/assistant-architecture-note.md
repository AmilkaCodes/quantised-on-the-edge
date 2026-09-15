# Where training belongs: the assistant-architecture synthesis (noted 2026-09-15)

**Status: RECORDED, INCLUSION PENDING** — the student is deciding whether a bounded version
of this enters the dissertation's discussion/implications or whether it stays paper-side.
Every evidence item below is tagged **[main]** or **[branch]** so both versions are
ready-made: the dissertation may use [main] items only (hard rule: no branch finding, number
or direction); the paper uses all of it.

## The rule the whole programme kept re-teaching

> **Train what's absent. Retrieve what changes. Calibrate what breaks.**

## Mapping the training options for an edge coding assistant

1. **Train the generator on repo data (internalise the codebase): NO.** Repo knowledge is
   the fastest-changing knowledge in the system — the textbook retrieval case (parametric
   memory is not revisable; Lewis) [main]. Training it in buys a retraining treadmill, and
   both measured LoRA attempts at this scale SUBTRACTED: E4-α broke task completion while
   teaching invocation [main]; the RAFT arm narrowed format and cost ~35pp of general coding
   [branch]. Never spend gradient on what a lookup can do.
2. **Train the generator on stable docs (e.g. Python stdlib): the tempting middle; the maths
   mostly says no.** The honest case is efficiency, not capability: context carries a
   measured prefill+KV price that breaks the interactive floor on the CPU tier (Pi open-book
   TTFT ×8.4, over the registered 1–2s floor) [main], so shorter prompts pay there — and
   only there (context is nearly free on Metal/CUDA) [main]. Against it: the capability
   being trained toward already exists untrained (near-ceiling docs-exploitation at F16)
   [branch]; LoRA finds degenerate shortcuts unless training tasks force a genuine
   exploitation gradient (tasks must be unsolvable WITHOUT the docs — the verified stage-2
   mechanism) [branch]; and whether trained-in knowledge survives the quantisation ladder is
   UNMEASURED by anyone (the H4b hole — the one generator-training question still worth a
   study; FW1) [main+branch gap].
3. **Where training genuinely belongs — none of it in the generator:**
   - **The retriever.** Train embeddings on repo data, not the model: BM25 recall on Python
     intents 9.73% vs 55.81% for a trained dense retriever (DocPrompting §6.2) [main
     corpus]; retrieval is solved only where queries lexically match docs [branch R
     condition; main-safe analogue: DocPrompting's dataset-dependence]. Cheap, frozen
     generator, no collapse interaction.
   - **The router (necessity detection).** The docs-help vs docs-hurt regimes have opposite
     signs, so the load-bearing decision is WHICH regime a task is in. Precedent for a tiny
     trained router: TinyAgent's DeBERTa-small tool-RAG classifier, recall 0.998 [main
     corpus]. A trained router in front of a stock generator implements conditional
     retrieval with zero risk to the code-writing model. (Corroborating colour [main]: the
     tool-trained 4B's own reasoning declined docs on tasks where docs would have hurt — the
     judgement was empirically correct per Condition B.)
   - **Protocol (tool-calling), only if the generator must be touched.** The one genuinely
     absent 1.5B capability [main]; but selection beats training: the tool-trained 4B
     executes flawlessly under a forcing scaffold [main], and teaching it cost completion
     twice [main E4-α; branch stage-2]. Prefer a base model that ships the protocol.
4. **Calibration is not optional in any variant.** The generator ships as calibrated
   (imatrix) quants: [main] E2b (threshold moves, harm follows the cliff);
   [branch] the exploitation rescue at identical measured deployment cost.

## The resulting architecture (one sentence)

The efficient edge assistant is a SYSTEM: three small trained parts (retriever embeddings,
necessity router, optionally a protocol-trained base chosen not tuned) around ONE frozen,
calibrated generator — not a trained model.

## Efficiency accounting (tier-conditional, [main])

Prompt-shortening via internalised knowledge pays only where prefill is the binding cost
(CPU tier); on accelerated tiers the efficiency levers are quant level (throughput/memory)
and calibration (quality at low rungs), not context length.

## Pending decision (student, sleeping on it)

Whether a bounded [main]-only version of this synthesis enters the dissertation's
discussion (it is derivable there from E1-perf, E2a/E2b, E4-α, DocPrompting and TinyAgent
alone, with the boundary paragraph covering the rest) or the synthesis stays whole,
paper-side. No drafting against it until decided.
