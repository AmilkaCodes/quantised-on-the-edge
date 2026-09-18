# E6 — MBPP+ cross-benchmark replication: results (2026-09-16)

> **METRIC-CONVENTION CORRECTION (2026-09-18, verified by recomputation from the committed
> per-problem snapshots):** the 1.5B and Phi tables below are **CSV-parsed values, which for
> MBPP+ record base∧plus**, not the study's `plus_status` convention. Recomputation gives, for
> Qwen: plus 0.638/0.627/0.630/0.571/0.423 against the base∧plus 0.630/0.616/0.619/0.563/0.418
> printed here (a 2–3 problem gap per cell, systematic); Phi plus reads 0.661/0.664/0.640/
> 0.474/0.262 against 0.659/0.661/0.638/0.468/0.249. **`mbpp-robustness.md` is the authoritative
> MBPP+ analysis** (plus-status throughout, matching every other analysis in this study and the
> convention fixed in the R1 re-score appendix); the results chapter draws from it, not from the
> tables below. The 7B and imatrix MBPP+ cells here are likewise CSV-parsed base∧plus and have
> no committed per-problem snapshot, so their plus-status values await a re-score (samples
> Mac-side; scoring only, no generation). Deltas and directions are unaffected by the
> convention: every conclusion below stands, and the parity reading of the memory-matched
> comparison is robust either way (plus_status can only raise both sides).
>
> **Grid-completeness correction (2026-09-18):** E6's grid lacked Phi Q8_0/Q3_K_M. With the fill-in cells run
> under the twin `mbpp-extension.md` registration, Phi's MBPP+ break point is **Q3_K_M**
> (−18.8 pp; Q4 −2.1 pp within margin) — ONE rung below its HumanEval+ Q4 cliff, not two as
> the P4 discussion below inferred from the partial grid. The completed analysis
> (`mbpp-robustness.md`) also resolves a significant Qwen Q3 step (−6.6 pp) that HumanEval+'s
> n=164 left within margin. The benchmark-relativity conclusion stands, at one-rung scale.

**Registration:** `e6-mbpp-replication.md` (extensions), predictions P1–P4 on record pre-run.
13 cells, closed-book, n=378, MBPP+ (held clean since first registrations; provenance chain in
the registration). HumanEval+ (HE+) comparators from the committed study tables. Paired exact
McNemar on plus-status throughout.

## Ladders (pass@1, HumanEval+ comparator in parentheses)

| model / rung | F16 | Q8_0 | Q4_K_M | Q3_K_M | Q2_K |
|---|---:|---:|---:|---:|---:|
| 1.5B naive | 0.630 (0.610) | 0.616 | 0.619 (0.616) | 0.563 (0.585) | **0.418** (0.384) |
| 1.5B imat | — | — | 0.624 | 0.585 | **0.471** |
| 7B naive | 0.730 (0.841) | — | — | — | 0.640 (0.793) |
| Phi-3 naive | 0.659 (0.646) | — | 0.638 | — | **0.249** |

## Prediction scorecard (the honest ledger)

- **P1 — 1.5B collapse: CONFIRMED, in magnitude as well as direction.** F16→Q4 n.s.
  (10/7, p = .63); F16→Q2 **−21.2 pp** (91 broke / 10 rescued, p = 1.7×10⁻¹⁷) vs HE+'s
  −22.6 pp. The study's central result — flat to the Q4 knee, cliff at Q2 — transfers to a
  second benchmark almost number-for-number.
- **P2 — 7B robustness: FAILS BOTH CLAUSES as stated.** The 7B's F16→Q2 drop is −9.0 pp and
  **significant** (49/15, p = 2.4×10⁻⁵), not small/n.s. as on HE+ (−4.9, n.s.). And the
  memory-matched comparison collapses to parity: 7B@Q2 0.640 vs 1.5B@F16 0.630
  (38/35, p = .82) — on HE+ it was +18 pp. Scale still *attenuates* the collapse
  (−9 vs −21 pp) but no longer erases it, and the memory-matched advantage is
  benchmark-dependent.
- **P3 — imat rescue: REAL BUT MINORITY — fails as worded.** +5.3 pp at Q2, significant
  (52/31, p = .028), yet only ~25% of the drop recovered (HE+ recovered ~half). The
  calibration rescue of *generation* is benchmark-dependent in size. (Contrast: the
  context-exploitation rescue on FAB was +34 to +56 pp — the big rescue lives on the
  context axis, not the generation axis.)
- **P4 — Phi cliff at Q4: FAILS.** Q4 is flat on MBPP+ (−2.1 pp, 20/12, p = .21); the cliff
  appears at Q2 with a catastrophic −41.0 pp (159/8, p = 1.4×10⁻³⁷). On HE+ (and on FAB),
  Phi's cliff sat at Q4. **Cliff location is benchmark-relative.**

## What the divergences mean (the finding inside the replication)

The robust invariant is the **1.5B Q2 collapse** — same rung, same size, both benchmarks.
Around it, three quantities move with the task distribution:
1. **Cliff locations are model × recipe × benchmark**, not model × recipe. MBPP+ does not
   surface the Q4 damage in Phi that HumanEval+ and FAB both exposed; the damage is latent
   until the task distribution stresses it. Claim-wording consequence for every "at the
   model's own cliff" sentence: the cliff must be named *per instrument* (FAB and HE+ agreed
   for Phi; MBPP+ dissents — consistent with monotone latent damage surfacing at
   distribution-dependent thresholds, an interpretation to argue, not assert).
2. **The scale advantage shrinks on MBPP+** (7B−1.5B at F16: +10.0 pp vs HE+'s +23.1) and
   with it the memory-matched bombshell softens to a tie. The deployment claim "7B@Q2 beats
   1.5B@F16 memory-matched" must carry a benchmark qualifier.
3. **The imat generation-rescue is partial here** — reinforcing the stage-3 reading that
   calibration's dramatic effects are on context-exploitation; on generation it buys a real
   but modest margin.

## Caveats
- One benchmark pair; MBPP+ and HE+ differ in difficulty profile non-uniformly by model
  (1.5B and Phi score higher on MBPP+, the 7B lower) — "easier/harder" is not a single axis.
- 13 cells, uncorrected; the headline p-values survive any correction; P3's p = .028 does not
  survive Bonferroni across the 7 tests reported — treat the rescue size as descriptive.
- Same INSTRUCTION wrap as HE+ (registered); MBPP+'s docstring prompts may interact with the
  wrap differently across models — a level effect, controlled within-benchmark by pairing.
