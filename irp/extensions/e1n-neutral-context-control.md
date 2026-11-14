# E1-N — neutral-context control (REGISTERED 2026-11-14, commit ea4c51e; RUN 2026-11-14)

**Registration, 2026-11-14:** the student decided to run the control. This file, the selection
script `proposal-dev/pilot/e1/e1n_build_neutral.py`, the frozen artefact
`proposal-dev/pilot/e1/neutral_prompts.jsonl` (sha256 `bc7c2d3b03d0248c…`) and its manifest
`e1n-build-manifest.json` are committed together **before any model output exists**; that commit is
the registration. Two details fixed at registration (not changes to the rule above them): (i) pair
length is measured with the Condition-B builder's own proxy (est_tokens = ceil(chars/4)), so N and B
are length-matched on the same scale; (ii) Condition B's 13-gram contamination rule is applied to the
neutral chunks too, so neither condition can carry reference-solution text. Build check: 164/164
pairs within ±20 % of B (N/B ratio min 0.80, median 0.99, max 1.20); rebuild is byte-identical.
The harness gains `--condition neutral` (outputs suffixed `_neutral`, so Condition B's files are not
touched).

**Status (original draft note): DRAFT 2026-11-14, written in response to the external reviewer's g-draft feedback
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

## Result (run 2026-11-14, 22:25 UTC, after registration commit ea4c51e at 22:24:55 UTC)

Run manifest `proposal-dev/pilot/results/mac/manifests/manifest_e1n_neutral_20261114_222503.json`
(artefact sha256 `bc7c2d3b…` as registered; llama.cpp b9951; parse rate 1.0; 78.6 tok/s). One run,
no re-run, no deviation. Scoring snapshot
`proposal-dev/pilot/eval-results/mac/samples_qwen2.5-coder-1.5b-instruct_F16_neutral-sanitized_eval_results.json`;
analysis `irp/analysis/e1n_analysis.py` (its B − A line reproduces Table D.8's F16 row exactly).

| Condition | HumanEval+ pass@1 |
|---|---|
| A closed-book | 0.610 (100/164) |
| B frozen documentation | 0.537 (88/164) |
| N neutral documentation | 0.567 (93/164) |

| Contrast | Difference (pp) [95% CI] | Exact McNemar p | Discordant pairs |
|---|---|---|---|
| B − A | −7.3 [−14.0, −0.6] | 0.050 | 22 / 10 |
| N − A | −4.3 [−10.4, +1.8] | 0.25 | 17 / 10 |
| N − B | +3.0 [−4.3, +9.8] | 0.49 | 14 / 19 |

Anchor correction: the prediction text above gives B ≈ 0.543 at F16; Table D.8's F16 value is
0.537 (0.543 is Q8_0). The rule is applied to the measured cells, so nothing turns on it.

**Reading against the registered predictions: outcome 3 (intermediate).** N lies between A and B
and its interval overlaps both anchors. Read mechanically, the intervals meet the letter of
outcome 2: N − A spans zero and B − A excludes it, though only just (p = 0.050). Outcome 2 also
assumes N is distinguishable from B, and it is not (N − B spans zero). The rule does not cover
"≈ both" explicitly, so the defensible reading is the registered intermediate one: by point
estimate about 4.3 of the 7.3 points (≈ 60 %) follow from the presence and length of prepended
context and about 3.0 (≈ 40 %) from the documentation's content; n = 164 cannot separate the two.
Consequences for the report (student's decision): Section 4.5's "prompt-format or harness effect
this study did not isolate" can become "a neutral-context control of equal length recovered under
half of the loss (N 0.567 vs A 0.610 and B 0.537; neither contrast significant), so the harm is
partly presence and partly content and n = 164 does not apportion it". Section 5.4's closed-book
advice stands as written, because no prepended context, relevant or not, ever helped.
