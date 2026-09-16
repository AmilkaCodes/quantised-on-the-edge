# E6 — MBPP+ cross-benchmark replication (REGISTERED 2026-09-16, before any run)

**The reserve is called in.** MBPP+ has been held clean since the original registrations
("MBPP+ reserved" — E4 stage-0; every training-data sweep in E4 and E5 swept against it with
0 drops; FAB's invented names cannot touch it; the stock ggufs are upstream artefacts that
never entered our pipeline). Student directive 2026-09-16 ("MBPP+ Registration, lets go!") —
the third dated gate-lift on this branch's measurement clause, same pattern as stage-V;
the dissertation HOLD boundary and `main` remain untouched.

**Question:** do the study's headline generation results replicate on a second, held-clean
public benchmark — or are they HumanEval+-specific?

## Scope (Mac quality axis only, closed-book only, n=378/cell)
Open-book conditions are OUT: MBPP+ problems are self-contained like HumanEval+, so the
Δ(open−closed) structural limits recorded in E1 apply identically; FAB remains the
necessary-context instrument. This is a generation-replication study only.

## Cells (13)
- **1.5B naive** × {F16, Q8_0, Q4_K_M, Q3_K_M, Q2_K} — the collapse ladder
- **1.5B imat** × {Q4_K_M, Q3_K_M, Q2_K} — the calibration rescue
- **7B naive** × {F16, Q2_K} — scale robustness + the memory-matched transplant
- **Phi-3 naive** × {F16, Q4_K_M, Q2_K} — the cliff-location cross-model check

## Registered predictions (falsifiable)
- **P1:** the 1.5B Q2_K collapse replicates in direction and significance (large paired drop
  F16→Q2; F16≈Q8≈Q4 within the 5 pp margin — the same threshold rule as the main study).
- **P2:** the 7B F16→Q2 drop is small/n.s.; memory-matched, 7B@Q2 > 1.5B@F16 on MBPP+.
- **P3:** 1.5B imat-Q2 recovers the majority of the naive Q2 drop (E2b transplant).
- **P4:** Phi's degradation begins at Q4_K_M (its cliff), not Q2.
Magnitudes are expected to differ from HumanEval+ (different task distribution, 378 vs 164);
direction + significance is the replication criterion. Paired exact McNemar within model.

## Instrument notes (decided pre-run)
- **Identical INSTRUCTION wrap for both benchmarks** — comparability over wording fit (the
  MBPP+ docstring includes an assert showing the exact signature, so the target is
  unambiguous). Registered so a wording-driven level shift is not misread.
- run_pilot patched (dataset-aware loader + `--dataset mbpp` scorer flag + `_mbpp` sample-file
  tag so HumanEval samples cannot be clobbered); patch committed before any scored run.
- House scoring rules apply: stale `*_eval_results.json` deleted before scoring;
  `EVALPLUS_MAX_MEMORY_BYTES=-1` (already in run_pilot).
- llama.cpp b9951, temp 0, seed 0, study caps (n_ctx 4096, max_tokens 768).

## Reporting
`irp/analysis/e6-mbpp-replication.md`: per-model ladders, deltas with McNemar, threshold
verdicts vs the HumanEval+ table, the memory-matched cell, and the standard caveats block.

## OUTCOME (same day — full analysis in `irp/analysis/e6-mbpp-replication.md`)
**P1 CONFIRMED in magnitude** (1.5B Q2 collapse −21.2 pp, p=1.7e-17; flat to Q4). **P2 FAILS
as stated** (7B drop −9.0 pp significant; memory-matched advantage collapses to parity).
**P3 fails as worded** (rescue real, p=.028, but ~25% not majority). **P4 FAILS** (Phi cliff
at Q2 on MBPP+, not Q4 — cliff location is benchmark-relative). The robust invariant is the
1.5B Q2 collapse; scale advantage, rescue size, and cliff locations are task-distribution-
dependent — claim-wording constraints recorded in the analysis for the write-up.

## Deviations
_(none)_
