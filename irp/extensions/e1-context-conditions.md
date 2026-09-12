# E1 design note — context conditions ("open-book") and the oracle probe

**Status: ACTIVATED (student decision 2026-09-12)** — open-book runs will be included alongside
closed-book. **Design revised on activation:** Condition B = **retrieval over official Python
reference documentation** (docs-RAG), not few-shot exemplars — closer to real deployed
assistants, and cleaner on contamination. Framed as a named sub-question:
**RQ1b — does reference-documentation context mitigate quantisation-induced degradation?**
(hypothesis-driven, self-documenting pre-registration). **HARD GATE: the E1 protocol document
must be written and committed BEFORE any measurement runs** (retrieval method + k + chunk size +
context cap + thresholds + the contamination-sweep criterion, all fixed in advance).

**Pre-registered validity check — contamination sweep (added 2026-09-12):** before any scored
run, an n-gram overlap check between every retrieved documentation chunk and the canonical
HumanEval+ reference solutions (a few problems resemble textbook examples). Threshold fixed in
the protocol; result gives the thesis its one-line defence: "no retrieved chunk shared >n-gram
overlap with reference solutions." ~An afternoon of work.

**Python docs licensing (VERIFIED at source 2026-09-12, docs.python.org/3/license.html):**
Quote: 'Python software and documentation are licensed under the Python Software Foundation
License Version 2.' Quote: 'Starting with Python 3.8.6, examples, recipes, and other code in
the documentation are dual licensed under the PSF License Version 2 and the Zero-Clause BSD
license.' Both permissive (use/copy/modify/distribute); research retrieval use clearly
permitted. Record the docs VERSION used in the provenance manifest (e.g. "Python 3.12.x docs,
retrieved YYYY-MM-DD").

_Original design note (2026-09-01) below — Condition B superseded as above; oracle probe
(Condition C) remains optional._ Scope position: outside the current pre-registration, but **named in
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
