# Results-chapter data pack — computations (2026-09-18)

_Items from `formative-plan.md` §"Results-chapter data pack", computed from committed data
(sources named per item). Bench items 6 and 8 are DONE 2026-09-18 and report in their own
files: `mbpp-robustness.md` (full 2×5 grid, gate pass, one-rung break-point shifts both ways)
and `xdev-lowrung.md` (Q3 zero pass-flips; proxy strengthened); this file carries the rest.
**Every data-pack item is now closed except optional item 11 (no meter to hand).**_

## Item 12 — J/token exact-form recompute ✅

`mean_power_w / mean_tok_s` (the exact total-energy/total-tokens form under equal-interval
500 ms sampling) vs the original `mean_power_w / median_tok_s`, all perf rows (latest per
device×model×rung). **Result: the two forms differ by ≤0.7% on 45 of 46 rows** — negligible,
as Ch3 §3.4 commits. Single outlier: Pi/Phi-3/Q2_K at −4.9% (a straggler prompt widens the
mean–median tok/s gap on that row); footnote it, the qualitative reading is unchanged.
Headline values are stable under either form (e.g. Mac 1.5B Q4 0.148 both forms; Jetson 7B
Q2 1.741 both forms). Full table regenerable from the CSVs (script in this file's commit).

## Item 4 — per-rung file sizes + effective bits/weight ✅

From the Mac ggufs (sizes exact; params: Qwen 1,543.7 M, Phi-3 3,821 M):

| model | rung | size (GB) | effective bits/weight |
|---|---|---:|---:|
| Qwen 1.5B | F16 | 3.09 | 16.03 |
| | Q8_0 | 1.65 | 8.53 |
| | Q4_K_M | 0.99 | 5.11 |
| | Q3_K_M | 0.82 | 4.27 |
| | Q2_K | 0.68 | 3.50 |
| Phi-3-mini | F16 | 7.64 | 16.00 |
| | Q8_0 | 4.06 | 8.50 |
| | Q4_K_M | 2.40 | 5.02 |
| | Q3_K_M | 1.96 | 4.11 |
| | Q2_K | 1.51 | 3.16 |

(Q-labels' nominal bit-widths understate mixed-precision reality: "Q2_K" is ~3.2–3.5
effective bits — worth a sentence where Ch3 first names the rungs.)

## Item 5 — truncation/degeneration incidence at low rungs ✅

Solution token lengths (model's own tokenizer) vs the 768 cap, from the tracked
`eval-results/mac/` snapshots (n=164/cell):

| model | rung | median | p95 | ≥700 tok | ≥760 tok |
|---|---|---:|---:|---:|---:|
| Qwen 1.5B | F16–Q3 | 75–128 | 239–346 | 0 | 0 |
| | Q2_K | 80 | 293 | **5** | 1 |
| Phi-3 | F16–Q3 | 79–96 | 198–302 | 0 | 0 |
| | Q2_K | 95 | **764** | **20** | **16** |

**Finding:** cap-scale output is absent at every rung above Q2 and concentrates exactly at
the collapse rung — 12% of Phi's Q2 solutions sit at/near the hard cap (runaway
generation/degeneration), vs 3% for Qwen. Quantifies the degeneration component of low-rung
failure alongside pass@1.

## Items 3 + 2 — Holm adjustment + paired-difference bootstrap CIs ✅

Rung vs F16 within model (plus-status; exact McNemar; Holm within each model's 4-test
family; paired-difference percentile bootstrap, B=10,000, seed 0):

| model | rung | Δ pass@1 | 95% CI | McNemar p | Holm |
|---|---|---:|---|---:|---:|
| Qwen 1.5B | Q8_0 | +0.006 | [−0.012, +0.030] | 1.00 | 1.00 |
| | Q4_K_M | +0.006 | [−0.043, +0.055] | 1.00 | 1.00 |
| | Q3_K_M | −0.024 | [−0.079, +0.030] | .52 | 1.00 |
| | Q2_K | **−0.226** | [−0.305, −0.146] | 1.2×10⁻⁷ | **4.9×10⁻⁷** |
| Phi-3 | Q8_0 | −0.018 | [−0.043, +0.006] | .38 | .38 |
| | Q4_K_M | **−0.098** | [−0.165, −0.030] | .007 | **.014** |
| | Q3_K_M | **−0.220** | [−0.299, −0.140] | 1.0×10⁻⁷ | **3.0×10⁻⁷** |
| | Q2_K | **−0.427** | [−0.512, −0.341] | 1.0×10⁻¹⁷ | **4.0×10⁻¹⁷** |

Every confirmatory verdict survives Holm; every CI excludes zero exactly where the margin
verdicts fell, and the near-margin Qwen Q3 interval straddles zero — consistent with its
within-margin verdict and with the multiplicity stance stated in Ch3.

## Item 1 — bootstrap interval on the cross-tier divergence estimate ✅

Q4_K_M K=50 xdev (three tiers, committed solutions; in-process canonical-oracle scoring,
noise gate clean at 0): output-identity rate **38/50 = 0.760, 95% bootstrap CI
[0.640, 0.880]** (B=10,000, seed 0). Pass-level divergence: **1 flip/50 (2 pp)** — the known
HumanEval/5 Jetson flip. (The Q3_K_M companion runs under the registered
`xdev-lowrung-addendum.md`; reported separately.)

## Item 9 — perf ten-prompt set token lengths ✅

First 10 HumanEval+ prompts, INSTRUCTION-wrapped, model tokenizers:
**Qwen: mean 134.9 tokens (range 113–152); Phi-3: mean 159.8 (135–177).** Per-prompt table
regenerable (script in this commit). Chars 483–702.

## Item 10 — RQ3 floors' derivation ✅

The proposal's own words (final-body.md, Methodology): performance-acceptable "if it meets
floors from the stated use case of interactive code assistance: 8–10 tokens/s sustained,
time-to-first-token of one to two seconds per Nielsen's limits [24], and peak memory within
RAM without swap." Grounding: Nielsen (1993) response-time limits (1 s = uninterrupted
flow; the candidate-topic note keeps the fuller rationale). Ch3 restates this verbatim-with-
citation when the verdicts are given.

## Item 7 — idle draws ✅ (all three tiers, 2026-09-18, same sensors/boundaries as the study's load figures)

| device | idle draw | sensor/boundary |
|---|---:|---|
| Mac | **0.34 W** | powermetrics SoC Combined (n=15 @ 1 s) |
| Pi 5 | **1.76 W** | PMIC rail-sum (n=20 @ 0.5 s) |
| Jetson | **4.43 W** | tegrastats VDD_IN (n=20 @ 1 s) |

Note: the plan's "Pi ≈2.4 W known" figure was a different boundary/source; these
same-boundary values are the ones comparable to (and subtractable from) the study's load
figures, with the standing cross-tier scope caveat applying to idle exactly as to load.

## Item 11 — optional USB-C meter check
No inline meter to hand; the named §3.8 limitation stands (unchanged).

## Addendum — 7B + imatrix MBPP+ re-score (2026-09-18, student-requested)

Closes the open item named in `e6-mbpp-replication.md`'s metric-convention banner ("their
plus-status values await a re-score"). Five cells re-scored from committed sanitized samples
(scoring only, no generation; stale `*_eval_results.json` deleted first;
`EVALPLUS_MAX_MEMORY_BYTES=-1`; evalplus 0.3.1, MbppPlus-v0.2.0 sha b54e762755248ca4…):

| cell | base∧plus (CLI, as E6 recorded) | plus_status (study convention) | flips vs prior |
|---|---:|---:|---:|
| 7B F16 | 0.730 ✓ reproduced | **0.735** | 0 |
| 7B Q2_K | 0.640 ✓ | **0.646** | 0 |
| 1.5B imat Q4_K_M | 0.624 ✓ | **0.630** | 0 |
| 1.5B imat Q3_K_M | 0.585 ✓ | **0.595** | 0 |
| 1.5B imat Q2_K | 0.471 ✓ | **0.479** | 0 |

**Verification: clean.** Every CLI value reproduced to three decimals and no problem changed
status, so the E6 cells carry no scoring pathology and no stale-cache artefact. Per-problem
snapshots for all five are now committed (`pilot/eval-results/mac/`, 15 MBPP+ files total).

**Convention reconciliation (whole 13-cell E6 grid).** The gap between the two conventions is
0.3–1.3 pp per cell — 2–4 problems that pass the plus suite while failing the separately-timed
base suite (`Mbpp/734` in all five re-scored cells). The study counts `plus_status` everywhere
(verified across `e1_analysis.py`, `collapse_stats.py`, `e1_relevance_harm.py`,
`make_figs2.py`, `score_xdev.py` in the R1 appendix), so **`mbpp-robustness.md` remains the
authoritative MBPP+ analysis and the results chapter draws from it.**

**No verdict moves under harmonisation** (plus_status): P2's 7B drop −9.0 pp (49/15,
p = 2.4×10⁻⁵) and memory-matched parity +0.8 pp (38/35, p = .82; scale gap at F16 +9.8 pp);
P3's rescue +5.6 pp (52/31, p = .028), recovering 26% of the 21.4 pp naive-Q2 drop.

## Item 12 — exact conditional (and score-type) paired intervals beside the bootstrap ✅ (2026-09-21)

Third external review asked for a non-resampling interval on the paired drop, since the
bootstrap distribution is discrete on few discordant problems. Computed from the committed
snapshots (plus-status) for all 16 confirmatory F16-vs-rung cells; script
`paired_ci.py` (session scratchpad; b = F16 pass & rung fail, c = rung pass & F16 fail).
**Exact conditional** = Clopper–Pearson on c | (b+c), mapped to drop = (b+c)(1−2π)/n (dual to
exact McNemar). **Score-type** = inversion of the paired-difference score statistic with the
discordant probability at its restricted MLE (Tango-style; to be cross-checked against a
reference implementation before it is quoted in prose — the exact conditional is the one
Ch3 §3.5 names).

| bench | model | rung | b | c | drop | bootstrap 95% (items 2/3) | exact-cond 95% | verdict (exact) | score-type 95% |
|---|---|---|---:|---:|---:|---|---|---|---|
| HE+ | Qwen | Q8_0 | 1 | 2 | −0.6pp | [−3.0, +1.2] | [−1.8, +1.5] | within | [−3.8, +2.3] |
| HE+ | Qwen | Q4_K_M | 7 | 8 | −0.6pp | [−5.5, +3.7] | [−5.3, +4.3] | within | [−5.7, +4.4] |
| HE+ | Qwen | Q3_K_M | 13 | 9 | +2.4pp | [−3.0, +7.9] | [−3.7, +7.9] | straddles | [−3.4, +8.5] |
| HE+ | Qwen | Q2_K | 44 | 7 | +22.6pp | [+14.6, +30.5] | [+14.8, +27.6] | beyond | [+14.8, +30.6] |
| HE+ | Phi | Q8_0 | 4 | 1 | +1.8pp | [−0.6, +4.9] | [−1.3, +3.0] | within | [−1.2, +5.6] |
| HE+ | Phi | Q4_K_M | 24 | 8 | +9.8pp | [+3.0, +16.5] | [+2.6, +15.0] | straddles (point beyond) | [+3.2, +16.8] |
| HE+ | Phi | Q3_K_M | 42 | 6 | +22.0pp | [+14.6, +29.9] | [+14.5, +26.5] | beyond | [+14.5, +29.8] |
| HE+ | Phi | Q2_K | 74 | 4 | +42.7pp | [+34.1, +51.2] | [+35.6, +46.2] | beyond | [+34.3, +50.8] |
| MBPP+ | Qwen | Q8_0 | 4 | 0 | +1.1pp | (mbpp-robustness.md) | [−0.2, +1.1] | within | [+0.0, +2.7] |
| MBPP+ | Qwen | Q4_K_M | 10 | 7 | +0.8pp | | [−1.5, +2.8] | within | [−1.5, +3.2] |
| MBPP+ | Qwen | Q3_K_M | 31 | 6 | +6.6pp | [+3.7, +9.8] | [+3.5, +8.6] | straddles (point beyond) | [+3.7, +10.0] |
| MBPP+ | Qwen | Q2_K | 91 | 10 | +21.4pp | | [+17.4, +24.1] | beyond | [+16.8, +26.3] |
| MBPP+ | Phi | Q8_0 | 1 | 2 | −0.3pp | | [−0.8, +0.6] | within | [−1.7, +1.0] |
| MBPP+ | Phi | Q4_K_M | 20 | 12 | +2.1pp | | [−1.1, +4.9] | within | [−0.9, +5.3] |
| MBPP+ | Phi | Q3_K_M | 77 | 6 | +18.8pp | [+14.6, +23.0] | [+15.3, +20.8] | beyond | [+14.6, +23.3] |
| MBPP+ | Phi | Q2_K | 159 | 8 | +39.9pp | | [+36.0, +42.3] | beyond | [+34.6, +45.3] |

**Finding:** the exact conditional interval agrees with the bootstrap on every margin
verdict in all 16 cells (within / straddles / beyond identical; the two boundary rungs on
HE+ remain the inconclusive ones). The score-type interval is a little wider on the small
discordant counts and would move two near-zero cells (HE+ Phi Q8_0 upper +5.6; MBPP+ Phi
Q4_K_M upper +5.3) from "within" to "straddles" by under one point — recorded here, not
claimed, pending the reference cross-check. Under Ch3 §3.5's three-valued quality gate
(pass = interval within margin; fail = point beyond; marginal = point within, interval not):
Qwen Q3_K_M on HE+ is **marginal** (results-chapter rows and `synthesis.md` §4 carry the
qualifier); Phi Q4_K_M on HE+ and Qwen Q3_K_M on MBPP+ are **fail** by the registered point
criterion with their intervals reported.
