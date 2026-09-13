# E2 PROPOSAL — can anything make context help a quantised edge model? (NOT ACTIVATED)

**Status: PROPOSAL ONLY (2026-09-12).** No E2 measurement runs until (1) supervisor discussion
(October meeting agenda item), (2) a committed E2 protocol fixing all parameters (same discipline as
E1: registered-before-run, gated, timeboxed). This note exists so the decision is taken on evidence,
not improvised. Written per the E1 escalation rule: *any expansion = new logged decision + supervisor
input + calendar check.*

## Evidence motivating (and shaping) E2 — all committed, 2026-09-12
1. **RQ1b:** frozen BM25 doc-context never helps (Δ ≤ 0, all 10 cells) and hurts most at each model's
   collapse rung (Qwen Q2 −0.098 p=.007; Phi Q4 −0.152 p=.0008). Thresholds unmoved.
2. **RQ1c:** the agentic (asked-for-context) mechanism is inoperable at F16 (M1 = 0/20; wrong-wrapper
   + degeneration under coercion) — no quantisation needed to break it.
3. **Perf tie-in:** context costs prefill + KV memory per tier — the Pi loses its registered TTFT
   compliance to open-book regardless of quality.
4. **Mechanism check (Tier-1):** harm is NOT explained by retrieval relevance or context length; the
   one weak uncorrected signal points the other way (higher-scoring chunks break more). ⇒ **naive
   BM25-score-thresholded gating is dropped as an arm** — score ≠ usefulness.

**The E2 question:** is "closed-book only" fundamental at this model scale, or an artefact of *stock*
components (naive quants, sparse retrieval, naive prompt assembly)? Each arm below attacks one word of
"stock". All outcomes reportable (research symmetry); a null on every arm *strengthens* the
dissertation's closed-book recommendation rather than weakening it.

## Proposed arms (ranked; at most ONE runs before the write-up is on track)

**Arm 1 — imatrix-calibrated quantisation (recommended).**
Re-quantise the same ladder with importance-matrix calibration (same b9951 `llama-imatrix` +
`llama-quantize`), then rerun the closed + open quality sweeps. Settles two things at once: (a) does
calibration shift the *collapse threshold* (D6's deliberate naive-ladder control becomes a measured
comparison), and (b) does it restore *context-robustness* at low bits (does the collapse-rung
distraction spike shrink)? Cost: calibration + requantise ≈ hours unattended; 2 Mac sweep-days.
Grounding: Dettmers's 4-bit case + the Afrin/Jin quantization-strategy extracts in the corpus.

**Arm 2 — dense retrieval.**
Swap BM25 for a pinned open-weights embedding retriever, same corpus/chunks/k. D27 excluded embeddings
to avoid a confound; in E2 the confound *is* the manipulation, cleanly A/B'd against the frozen BM25
artefact. Settles: is the harm about *content quality* (DocPrompting's 56% vs 9.7% recall gap says
retrieval quality was the ceiling)? Tier-1 makes this the right retrieval fix — better content, not
better gating. Cost: ≈1 sweep-day + one pinned dependency; ethics note: one added open-weights model.

**Arm 3 — placement/framing micro-arm (cheapest).**
Same frozen chunks, two prompt variants: docs *after* the problem; and an explicit "reference material —
may be irrelevant; ignore if unhelpful" preface. Settles: is the harm positional/instructional
(lost-in-the-middle; instruction-binding) rather than content-driven? Could run headline-rungs-only
(Qwen Q2, Phi Q4 + F16 anchors) at ~⅓ sweep cost.

**Arm 4 — tool-trained small-model gate rerun (near-free; added 2026-09-13).**
Rerun the Condition D gate (20 problems, F16, Mac, same harness) with a function-calling-trained small
model — Taheri's results point at Qwen-3 4B (Think) as the small-model sweet spot, and IFFC-style
prompted-JSON framing as a second cheap variant. Settles the size-vs-training attribution in
`e1-implications.md` directly: if a tool-trained 4B passes the gate our 1.5B failed, the floor is
training, not scale. Cost: ~1–2 h including model download; descriptive only. (Mac RAM re-checked
2026-09-13: 36 GB — no feasibility constraint.)

**Arm 5 — in-family scale ladder: Qwen2.5-Coder-7B (added 2026-09-13).**
Full closed-book (optionally + open-book) ladder for the 7B sibling of our 1.5B — same family, so
**scale is isolated with specialisation held constant**. Makes Yazan's optimistic 7B headline ("if a
7B LLM performs the task well, quantization does not impair it") testable with execution-based scoring
into the sub-4-bit collapse region his two-point FP16-vs-AWQ design never reached, and asks whether the
collapse-rung context-harm spike vanishes with scale. Feasible: Mac 36 GB hosts the F16 anchor
(~15 GB); Pi 16 GB runs Q8-down; Jetson 8 GB runs Q4-down (a richer precision-fit boundary, not a
broken one). Cost: ~2–4 Mac compute-days + edge perf cells + analysis — the most expensive arm; only
viable if the write-up is well ahead of schedule.

**Dropped: BM25-score-thresholded selective retrieval** — Tier-1 shows score does not separate harmful
from harmless injections; a gate keyed on it has no empirical basis.

## Guardrails (pre-commitments)
- Registered E2 protocol before any run; parameters frozen; deviations dated.
- Calendar gate: no E2 run until the dissertation's methods + results chapters have first full drafts.
- One arm maximum initially; expansion only by a further logged decision.
- Ethics: arms 1/3 add nothing (same corpora/models); arm 2 adds one pinned open-weights embedding
  model — one-line ethics-form note if adopted.

## Ask for the supervisor
1. Do the E1 results justify one E2 arm, or should the project go straight to write-up with E2 as
   future work? 2. If one arm: Arm 1 (calibration) is our recommendation — agreed? 3. Confirm the
   calendar gate above matches the submission timeline.
