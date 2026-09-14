# Results coherence audit — 2026-09-14 (pre-figure-build)

_Requested check: "search the results for anything incoherent or unexplainable" before building
the batch-2 figures. Method: recompute pass@1(plus) for every cell from the per-problem
`eval-results` snapshots (`7a421d1`) and cross-check against every value in the committed
analysis tables; probe suspicious aggregate ties at per-problem level; census the perf CSVs.
Script: session scratchpad `audit_results.py` (methodology recorded here; one-shot QA tool)._

## Verdict

**52 of 53 table cells reproduce exactly (tolerance 0.004). One systematic discrepancy found
(R1, all 5 rungs). Both suspicious aggregate ties are genuine coincidences. Perf CSVs clean,
with one tooling trap documented. Nothing threatens any registered conclusion.**

## 1. Quality cells — recompute vs committed tables

All A (closed), B (open), O (oracle) cells for both models × 5 rungs, all 7B closed/open cells,
and all 6 imatrix closed + 2 imatrix open cells **match the analysis tables exactly**.

**EXCEPTION — R1 (all 5 rungs, same direction):** the eval-results snapshot re-score reads
1–2 problems HIGHER than the published values at every rung:

| rung | e1r-agentic.md (= `r1_*/summary.json` `pass@1_plus`) | snapshot recompute | Δ (problems) |
|---|---:|---:|---:|
| F16 | 0.555 | 0.5610 | +1 |
| Q8_0 | 0.549 | 0.5549 | +1 |
| Q4_K_M | 0.506 | 0.5122 | +1 |
| Q3_K_M | 0.482 | 0.4939 | +2 |
| Q2_K | 0.262 | 0.2683 | +1 |

- Source identified: the analysis consumed the harness `summary.json` values; the snapshot was
  (re-)scored by EvalPlus at archive time. The `eval-results/README.md` stale-cache caution is
  the likely mechanism on one side or the other.
- **Impact on conclusions: none.** Every R1 claim (R1 ≈ B, R1 < A at Q4/Q3/Q2, cliff at Q2)
  holds under either set; the shift is ≤2/164 per rung, one-directional, and smaller than any
  reported effect.
- **Resolution owed (Mac, minutes):** clear the EvalPlus cache, re-score the R1 samples fresh,
  adjudicate which set is authoritative, align `e1r-agentic.md` + paired stats to it, and note
  the correction dated. Until then, figures and prose use the published summary values, and
  this table is the discrepancy record.

## 2. Suspicious aggregate ties — genuine, not copy-bugs

- Qwen Q2_K: B = O = 0.2866. Per-problem disagreements between the two runs: **38** → distinct
  runs; the tie is coincidental.
- Phi Q8_0: A = O = 0.6280. Per-problem disagreements: **28** → distinct runs; coincidental.

(Also confirms O ≈ B / O ≈ A cells are NOT artefacts of accidentally re-scoring the same file.)

## 3. Full-grid sweep

Every snapshot file is claimed by a committed analysis table — no orphan cells, no unexplained
runs in the archive.

## 4. Perf CSV census

- All CSVs parse clean; no negative values; no empty numeric fields in used columns.
- Cell counts as registered: study-model 5-rung files (mac 10 rows; jetson 9 — Phi F16 absent
  as recorded; pi5 9); E1 tie-in single-cell files (Qwen Q4 closed+open × 3 devices); 7B E2c
  files (mac 5, pi5 5, jetson 3 — F16/Q8_0 do-not-fit as registered).
- **Tooling trap (documented for reuse):** `make_figs.py`'s `perf()` globs the LATEST CSV per
  device — since E2c, the latest files are 7B-only, so re-running it naively would NaN the
  study models' perf figures. `make_figs2.py` pins every source file explicitly; if fig2/4/5
  are ever regenerated, pin their sources the same way.

## Figures built from this audit's clean baseline (batch 2, `make_figs2.py`)

fig6_conditions (A/B/O/R1 ladders), fig7_context_cost (tier TTFT/RSS closed-vs-open),
fig8_scale (7B ladders + memory-matched), fig9_dose_response (invocation dial),
fig10_imatrix (calibration + harm co-movement), fig11_deployment (7B tok/s vs SLO floor),
fig12_signature (collapse-rung alignment). Quality values recomputed from the snapshots at
plot time (single authority); R1 series from the published summaries per §1; M1′/degeneration
ladder reported as an in-text table (fig12 row 4 carries the break qualitatively).
