# E2c NOTE — 7B edge-tier perf cells (deployment leg of the memory-matched claim)

**Status: COMPLETE (2026-09-14, same day)** — all cells run on all three tiers; both fit-attempt
rungs resolved (Jetson Q8_0 does-not-fit as predicted; Pi F16 **fits**, 0.8 tok/s). Results +
verdicts in `irp/analysis/e2a-results.md` (E2c deployment-leg section). Deviations: none.

Originally: **PRE-REGISTERED BY COMMIT** (2026-09-14, per the project-log rule for this loose end:
register-first, frozen before runs; ethics delta nil; existing machinery only). **Question:** the
E2a memory-matched headline (7B@Q2_K 2.9 GB = 0.793 vs 1.5B@F16 3.1 GB = 0.610) rests on the Mac
quality axis. Does the 7B actually **run acceptably on the edge tiers** — against the registered
SLO floors (≥8–10 tok/s sustained, TTFT ≤1–2 s, RAM without swap)?

## Cells (standard perf mode: N=10×3, warm-up discard, medians+means, per-tier software power)
- **Mac (36 GB):** 7B × all 5 rungs (also closes e2a-protocol §2's optional Mac perf item).
- **Pi 5 (16 GB):** 7B × Q8_0, Q4_K_M, Q3_K_M, Q2_K; **F16 attempted once** — expected borderline
  (~14.5 GB weights + KV vs 15.8 GB usable, swap-free rule): the attempt outcome (loads/fails) is
  itself the precision-fit datapoint, recorded either way.
- **Jetson (8 GB):** 7B × Q4_K_M, Q3_K_M, Q2_K; **Q8_0 attempted once** (7.7 GB + KV vs 7.3 GB
  usable — expected not to fit; recorded either way).
- Closed-book prompts only (perf mode does not score); llama.cpp b9951 per-device builds as
  recorded; artefacts = the committed naive 7B ladder (shas logged at quantise time).

## Analysis / reporting
Per-tier table (median tok/s, mean+median TTFT, peak RSS, mean W, J/token) + verdicts against the
registered floors; the memory-matched claim then carries its deployment leg or its honest bound
("7B@Q2 quality-per-byte wins; edge serving feasible/infeasible per tier as measured"). Report in
`irp/analysis/e2a-results.md` (deployment-leg section) + synthesis pointer. **Timebox: one bench
day.** No quality cells, no new conditions, no further expansion.

## Deviations
_(none yet)_
