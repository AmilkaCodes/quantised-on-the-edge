# Cross-device validation addendum — low-rung spot-check (REGISTERED 2026-09-18, before the run)

**What this is:** data-pack item 8 (formative-plan; the one named-not-done item both external
review passes independently flagged as worth doing — "protects RQ3's verdicts"). The study's
cross-device proxy validation covers Q4_K_M only; the flip mechanism predicts worse divergence
at lower rungs, and ~2 pp of tier noise is material against the 5 pp margin at near-margin
rungs. This addendum converts the Ch3 §3.2/§3.8 caveat into a measurement.

## Design (fixed)
- **One cell: Qwen2.5-Coder-1.5B-Instruct × Q3_K_M, K = 50, Mac vs Jetson.** Rung choice
  reasoned: Q3_K_M is the rung whose margin verdict sits nearest the 5 pp boundary on
  HumanEval+ (−2.5 pp from F16), so tier noise is most consequential there; it is also one
  rung below the validated Q4. One edge tier per the plan's scope (Jetson: the CUDA backend,
  maximally different from Metal). K = 50 first HumanEval+ problems (the xdev convention).
- **Machinery unchanged:** `cross_device_check.py` (reuses `run_pilot.generate` — identical
  prompts, greedy, seed 0, caps) on each device; scoring via `score_xdev_direct.py` (the
  in-process canonical-oracle scorer, D25 rationale), parameterised for model/rung/device
  list — a mechanical edit, diff reviewed before running.
- **Readouts:** (1) solution-identity rate across tiers (byte-identical extracted solutions);
  (2) pass-pattern divergence: per-problem pass agreement, with any flips listed; (3) the
  implied bound on tier noise at Q3 vs the 5 pp margin.

## Registered expectation
Divergence at Q3_K_M exceeds the Q4_K_M baseline (identity < the Q4 rate) but pass-pattern
disagreement stays ≪ 5 pp — i.e. the flip mechanism is real but does not threaten margin
verdicts. Either violation direction is reportable (research symmetry): near-zero divergence
strengthens the proxy claim; >5 pp pass divergence would flag the Q3 margin verdict as
tier-fragile and be reported as such in Ch3.

## Governance
Registered on `main` (the reporting branch; the write-up consumes the result directly).
Runtime ~30–60 min total (Jetson generation is the long pole). Report:
`irp/analysis/xdev-lowrung.md` + a sentence into Ch3 §3.8. Deviations dated before the
affected step where foreseeable.

## OUTCOME (2026-09-18, same day): run complete — expectation's divergence clause violated
FAVOURABLY (Q3 identity 0.92 vs Q4 pairwise 0.90 — no low-rung worsening at this K); pass
flips 0/50 (0.0 pp vs the 5 pp margin). Proxy strengthened; Q3 margin verdict not
tier-fragile. Report: `irp/analysis/xdev-lowrung.md`.
