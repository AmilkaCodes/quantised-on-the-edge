# E1 design note — context conditions ("open-book") and the oracle probe

**Status:** designed, NOT started. Prepared 2026-09-01 as an activatable extension for the
supervisor conversation. Scope position: outside the current pre-registration, but **named in
the submitted proposal as the natural extension** ("results characterise closed-book generation
(HumanEval+); retrieval-grounded deployment may shift the usable threshold, and testing whether
quantisation degrades context-following at the same rate is a natural extension" — Expected
outcomes). Activating it = executing the proposal's own future-work line, not improvising scope.

## The question

Closed-book generation (current study) measures what a model can produce from a signature +
docstring alone. Deployed local assistants increasingly run **retrieval-grounded** ("open-book"):
relevant code/docs arrive in the prompt. Does context help — and critically, **does the help
survive quantisation?** Two distinct failure modes are conflated in the current design's blind
spot: losing the ability to *generate*, and losing the ability to *use help*. E1 separates them.

## Why "give it the solutions" is the wrong main condition (but a useful probe)

Musing recorded from design discussion (2026-09-01):

- **As the main open-book condition: no.** With the target's own reference solution in-context,
  pass@1 ceilings by construction at full precision (the task reduces to copying). The metric
  stops discriminating between rungs at the top, so it cannot measure "open-book performance" —
  and it resembles no real deployment (if you had the solution you wouldn't ask).
- **As a deliberate probe: yes, with honest labelling.** Failure to reproduce a *provided*
  correct solution isolates in-context copying/attention fidelity from generation ability. If a
  low-bit model can't even exploit the answer sitting in its prompt, that is direct,
  interpretable evidence that quantisation damages context utilisation itself. Ceiling expected
  at F16; the finding is any sub-ceiling behaviour down the ladder.

## The three conditions

| condition | prompt contains | measures | expectation at F16 |
|---|---|---|---|
| **A — closed-book** (done) | signature + docstring | generation ability | current baselines |
| **B — retrieval-style few-shot** (main E1) | k similar HumanEval problems **with their solutions** (never the target's own) | realistic assisted coding; whether the context *benefit* survives quantisation | modest lift over A |
| **C — oracle probe** (optional) | the target's own reference solution | pure context-utilisation fidelity | ≈ ceiling |

Everything else held identical to the pre-registered protocol: same 164 problems, greedy +
seed 0, execution-based pass@1 (plus), same 5-rung ladder, same pinned b9951, Mac quality axis
(aggregate-proxy status per D25 applies unchanged).

## The analysis

- Per-condition collapse thresholds (same machinery: 5pp margin + McNemar + bootstrap CIs).
- **The headline statistic is the interaction:** Δ(B−A) per rung — does the context benefit
  shrink as bits drop? Three interpretable outcomes, all reportable (research symmetry):
  context benefit survives (open-book rescues low-bit models), shrinks (context-following
  degrades *faster* than generation — the proposal's conjecture), or inverts.
- C reported only as a probe curve (fraction reproducing the oracle), never as "open-book
  pass@1".

## Cost + side-benefits

- Harness: prompt-construction change only (retrieval = nearest-neighbour over HumanEval
  docstrings or fixed exemplar sets; k∈{1,3} to bound prompt length). Scoring unchanged.
- Compute: ≈ one Mac compute-day per condition per model-sweep (quality axis re-run at 164×5×2).
- **Free RQ2 tie-in:** longer prompts grow TTFT and KV-cache memory — measuring B's perf cells
  connects context length to the 8GB edge memory envelope (context has a *memory price* on
  exactly the devices that motivated the study).

## Scope + ethics

- Pre-registration: E1 is an extension; if activated, register its thresholds/conditions BEFORE
  running (same discipline as the main study — write the E1 protocol first, then measure).
- Ethics: same public benchmark, automated metrics, no human data — substantively inside the
  Fast-Track approval; **confirm the approval wording covers the added conditions with a
  one-line query before running** (consistent with the RQ4-descoping precedent).

## Trigger

Activate only on supervisor steer (brief question 3) or if the write-up's external-validity
critique demands it. Not required for the dissertation (synthesis §7).
