# Programme implications — the full E1→E4 arc (discussion-chapter feed, refreshed 2026-09-14)

_Learning-mode framing note; the student owns and adapts this in assessed prose. Supersedes the
scope of `e1-implications.md` (kept as the E1-era record) now that the experimental programme is
closed: E1, E1-R, E2a, E2b, E2c, E4-α all run, analysed, committed. Companion analyses:
`e1-openbook.md`, `e1-agentic.md`, `e1r-agentic.md`, `e1r-oracle.md`, `e2a-results.md` (incl. the
E2c deployment leg), `e2b-imatrix.md`, `e4-alpha.md`._

## The thesis, as the measurements left it

> **Generation repatriates; orchestration does not — and at edge scale the two cannot yet be
> traded into each other.** Scaffolding buys syntax but not context-exploitation (E1-R);
> fine-tuning buys invocation but spends task completion (E4-α); scale buys
> quantisation-robustness but not context-robustness (E2a). The edge case for LLMs is strongest
> exactly where the measurements put it: closed-book, specialised, quantised to the knee, on the
> right tier — with orchestration in the scaffold or the cloud.

## Six claims the write-up can now carry, each with its evidence spine

1. **Quantisation collapse is a small-model phenomenon.** 1.5B loses 22.6 pp at Q2_K
   (p = 1.2×10⁻⁷); the same naive recipe at 7B loses 4.9 pp n.s. — threshold **None** on the
   5pp-margin rule. (E2a Arm 5.)
2. **Context harm is universal and tracks residual quantisation damage, not bit-width.**
   Imposed doc-context hurts at every scale and every rung tested — the 7B significantly at all
   five rungs *including F16* — and is worst wherever the quality cliff sits: at the 1.5B's
   collapse rung; at the 7B's Q2; and when E2b's calibration moves Phi's cliff two rungs and
   halves Qwen's Q2 drop, **the harm moves with the cliff**. Oracle-quality retrieval does not
   rescue it (O ≤ A everywhere). (E1, E2a, E2b, E1-R R2.)
3. **The invocation deficit decomposes into can't / won't / only-that.** Stock 1.5B *can't*
   (degenerates under coercion); tool-trained 4B *won't-by-policy* (nudge 0.00 → mandate 0.40 →
   force 0.80, M3 = 1.0 throughout, with first-person reasoning receipts dismissing the tool);
   FC-LoRA-tuned 1.5B does *only-that* — calls spontaneously but abandons the task whenever
   tools are in context (16/20 hallucinate the task's own function as a tool; the no-tools
   control codes perfectly). (E1 Condition D, E2a Arm 4, E4-α.)
4. **Scaffolding repairs syntax, not semantics.** Grammar-constrained decoding eliminates the
   wrong-wrapper failure class outright (M1′), but what arrives in the context still doesn't
   help — the boundary between what deterministic machinery can and cannot buy back is sharp
   and measured. (E1-R R1/R2.)
5. **Memory-matched, a big-quantised model beats a small-full-precision one — where it can be
   served.** 7B@Q2_K (2.9 GB) 0.793 vs 1.5B@F16 (3.1 GB) 0.610, +18 pp. Deployment leg (E2c):
   the Jetson serves it above the SLO floor (11.1 tok/s); the Pi cannot at any rung (max 3.4
   tok/s — 1.5B stays that tier's only interactive option); the Pi is nonetheless the only edge
   tier holding the 7B at F16 (fits, 0.8 tok/s, batch-only). Quality-per-byte advice is
   **tier-conditional**, and the study can state each tier's answer with measurements.
6. **The Q3_K_M throughput dip is an implementation artefact, not an information effect.**
   Slower than both neighbours and worst in J/token on Metal *and* CUDA at 7B, yet the Pi CPU
   ladder is cleanly monotone — the signature lives in GPU dequant kernels. This cleanly
   separates the throughput-side anomaly from the quality-side collapse signature (which is
   backend-independent), and inoculates the write-up against conflating them.

## What E4-α adds even as a FAIL

The field's standard remedy ("fine-tune it in") is now *measured* at this scale, with the failure
mechanism isolated by control: capability ingredients appeared (spontaneous calls, sensible
payloads, domain transfer) but coupled to task abandonment — the policy lever and completion
lever are not independent at LoRA-1.5B. Two method lessons for the methods chapter: run 1's val
loss lied on malformed data; run 2's honest val loss was still blind to policy inversion —
**gate batteries on the deployment task are the only trustworthy readout for behaviour-targeted
fine-tuning**. H4b (does trained tool-calling survive the ladder?) remains nobody's measurement,
now with a sharpened premise: the artefact must first pass a composition gate.

## Named future work (each blocked on something specific, none a debt)

- **Docs-necessary benchmark** → the fair test of edge-RAG and the RAFT premise (blocked on
  instrument construction; the sequencing rationale is recorded in the E4 spec).
- **E4 iteration 3** — the `search_docs`-domain supplement with post-tool-response *code*
  answers targets the only-that failure directly (blocked on formative feedback, per amendment).
- **β/H4b ladder** on any artefact that passes the composition gate.
- **7–8B tool-calling gate on the consumer tier** (the 4B existence proof suggests it passes).

## Governance state (what binds now)

- All arms closed within their registrations; deviations dated; fit-attempts resolved either-way
  as registered.
- **The write-up lien is now the governing constraint:** methods+results first drafts on track by
  **2026-09-28**, else nothing else runs. The formative (October) is the review gate; its
  feedback is the supervision input for any E4 iteration 3.

## For the supervisor thread / formative

1. Does the six-claim spine match their reading? (Especially claim 2's "harm follows the cliff".)
2. The can't/won't/only-that triad as the agentic story's organising device — too cute, or right?
3. Tier-conditional deployment advice as the applied conclusion (Jetson yes / Pi no / Mac trivially).
4. E4-α as a reported negative with mechanism — placement: results chapter or discussion?
