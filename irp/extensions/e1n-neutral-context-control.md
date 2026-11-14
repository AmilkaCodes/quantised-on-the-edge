# E1-N — neutral-context control (DRAFT FOR REGISTRATION; not yet committed as registered, not yet run)

**Status: DRAFT 2026-11-14, written in response to the external reviewer's g-draft feedback
("Isolate the Qwen context harm. One control at F16 with neutral text of equal length is 164
problems on the MacBook. It turns 'an effect this study did not isolate' into a finding, and
it rescues the closed-book recommendation. Register it before running."). The student decides
whether to run it. If yes: commit this file first (that commit is the registration), then run;
if no: the report stands as written, the harm attributed to an unisolated prompt or harness
effect (Sections 4.5 and 5.4).**

## Question

Is the Qwen2.5-Coder-1.5B's constant open-book harm (about seven points at every rung above
Q3_K_M, 9.8 at Q2_K; Table D.8) caused by the retrieved documentation's **content**, or by the
**presence and length of prepended context** (prompt format, attention burden)?

## Design

- **Model and rung:** Qwen2.5-Coder-1.5B-Instruct, **F16 only**, MacBook (the validated quality
  axis). One condition, one run: n = 164 HumanEval+, greedy decoding, fixed seed, the same
  harness, chat template and 768-token cap as every other quality cell.
- **Condition N (neutral context):** for each problem, prepend **two chunks from the same frozen
  Python-documentation artefact as condition B**, in exactly condition B's prompt format, but
  selected to be irrelevant: a fixed-seed (seed 0) random draw from the corpus **excluding that
  problem's top-50 BM25 chunks**, redrawn (same seeded stream) until the pair's total token
  length is within 20% of that problem's condition-B pair. Selection script and the per-problem
  manifest committed with the run.
- **Why this rule:** same corpus, same format and near-equal length isolate *content relevance*
  as the only difference from condition B; condition A (closed-book) remains the no-context
  anchor. No new corpus enters the study (no new licence or ethics surface; inputs unchanged
  from the approved self-assessment).

## Registered predictions (fixed before the run)

Let A = closed-book, B = frozen documentation, N = neutral, all at F16
(A = 0.610, B ≈ 0.543 from Table D.8).

1. **N ≈ B, both below A** → the harm follows context presence/length, not content: the
   "prompt-format or harness effect" reading of Section 4.5 becomes a measured finding; the
   closed-book recommendation (Section 5.4) holds for irrelevant context of any content.
2. **N ≈ A, B < A** → the harm is specific to the documentation content; the harness-effect
   suspicion is withdrawn and Section 5.4's caveat is rewritten.
3. **Intermediate** → partial attribution; reported as such.

"≈" is read with the paired bootstrap interval and exact McNemar against each anchor,
exploratory grade, uncorrected, as for every E1 cell.

## Gate, timebox, reporting

- One run, no iteration; timebox one evening. A failed or contaminated run is re-run once and
  the deviation dated here.
- Scored with the standard pipeline into `proposal-dev/pilot/eval-results/mac/` with suffix
  `_neutral`; recomputation covered by `final_audit.py` conventions.
- Report plan: one sentence in Section 4.5 and one row block in Table D.8 (~40 body words,
  funded; funding candidates listed in `assessment/Summative_Assignment/reviewer-feedback-2026-11-14-pass14.md`).

## Cost

164 problems, one model, one rung, MacBook only: under an hour of device time at F16's
78 tok/s; no edge hardware needed.
