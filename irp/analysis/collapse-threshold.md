# Collapse-threshold analysis — quality axis (RQ1)

**Data:** per-problem HumanEval+ pass/fail (plus tests), Mac quality run, llama.cpp b9951, greedy/seed-0,
**n = 164 problems, identical at every quant rung.** Source: `proposal-dev/pilot/results/mac/
samples_*-sanitized_eval_results.json`. Analysis code: `irp/analysis/collapse_stats.py`.
_(pass@1 here is recomputed from the per-problem eval_results — authoritative; may differ from the run
CSV's parsed pass@1 by ≤1 problem, rounding/parse.)_

## 1. Construct — "quality collapse" (operationalised)
- **Task:** code generation. **Metric:** HumanEval+ **pass@1 (plus tests)** — execution-based, the
  stricter EvalPlus test suite (catches subtly-wrong code; RESULTS §5/§9 show why parse-rate or
  perplexity would miss it).
- **Collapse threshold** = the lowest-precision rung at which pass@1_plus shows **both** (a) a
  *statistically significant* drop from the F16 baseline (paired McNemar exact, p < 0.05) **and**
  (b) a *material* effect (net drop ≥ ~10 points). Reported per model.

## 2. Hypotheses
- **Omnibus** — H₀: pass@1_plus equal across all five rungs; H₁: not all equal. Test: **Cochran's Q**
  (k = 5 related binary conditions on the same 164 problems).
- **Pairwise (locates the threshold)** — H₀: pass@1_plus at rung q = F16; H₁: rung q < F16.
  Test: **McNemar exact** (paired discordant pairs), F16 vs each rung.
- **Why paired, why these tests:** greedy + seed-0 makes pass@1 **deterministic** (run-to-run variance
  = 0, confirmed RESULTS §2), so the only uncertainty is the 164-problem sample; the *same* problems are
  scored at every rung → paired binary data → Cochran's Q (omnibus) + McNemar (pairwise) are the correct
  tests, not an unpaired two-proportion test.

## 3. Results (pass@1 plus)

| rung | Qwen-1.5B | Phi-3-3.8B |
|---|---:|---:|
| F16 | 0.610 | 0.646 |
| Q8_0 | 0.616 | 0.628 |
| Q4_K_M | 0.616 | 0.549 |
| Q3_K_M | 0.585 | 0.427 |
| Q2_K | 0.384 | 0.220 |

**Omnibus (Cochran's Q, df=4):** Qwen Q=73.7, p=3.8×10⁻¹⁵ · Phi-3 Q=141.4, p=1.4×10⁻²⁹ — **both reject
H₀**: pass rate depends on quant level.

**Pairwise (McNemar exact, F16 vs rung; "broken" = share of the F16-passing problems that fail at the rung):**

| F16 vs | Qwen net drop | Qwen p | Qwen broken | Phi net drop | Phi p | Phi broken |
|---|---:|---:|---:|---:|---:|---:|
| Q8_0 | −0.006 | 1.00 (n.s.) | 1% | +0.018 | 0.38 (n.s.) | 4% |
| Q4_K_M | −0.006 | 1.00 (n.s.) | 7% | +0.098 | **0.007** | 23% |
| Q3_K_M | +0.024 | 0.52 (n.s.) | 13% | +0.220 | **1.0×10⁻⁷** | 40% |
| Q2_K | +0.226 | **1.2×10⁻⁷** | 44% | +0.427 | **1.0×10⁻¹⁷** | 70% |

## 4. Thresholds + the model-dependent finding
- **Qwen2.5-Coder-1.5B (code-specialised):** F16 ≈ Q8 ≈ Q4 ≈ Q3 (no significant loss through Q3,
  McNemar p ≥ 0.52); **collapses at Q2** (p = 1.2×10⁻⁷; −0.226; 44% of F16-passes break).
  → **Threshold = Q2 (≈2-bit).**
- **Phi-3-mini-3.8B (general):** significant loss already at **Q4** (p = 0.007; 23% break), worsening
  monotonically to Q2 (70% break). → **Threshold = Q4 (≈4-bit).**
- **⭐ The collapse threshold is MODEL-DEPENDENT**, and the difference is statistically robust: the
  code-specialised model tolerates aggressive quantisation **two rungs further** before significant loss.
  This is RQ1's answer, now grounded in paired significance testing rather than eyeballed curves.

## 5. RQ mapping
- **RQ1 (how far can we quantise before collapse):** answered per model (§4).
- **RQ3 (does the threshold shift with hardware tier?):** **No — by construction and confirmed.** pass@1
  is hardware-independent (deterministic given model × quant; the tier changes only *speed/memory/energy*,
  not the emitted code). So the *quality* collapse threshold is a property of (model × quant), identical
  across Pi/Jetson/Mac; what shifts per tier is the *performance cost* of operating at a given rung
  (RESULTS §9). **That quality-independent / performance-dependent separation is itself a finding.**

## 6. Caveats
- pass@1 from per-problem eval_results is authoritative; run-CSV parsed values may differ by ≤1 problem.
- HumanEval+ contamination inflates absolute levels equally across rungs → the *relative* collapse (the
  threshold) is robust (RESULTS §5 caveat).
- Single dataset (HumanEval+, n=164); MBPP+ / a second task = future work. McNemar exact handles the
  small discordant counts; no multiple-comparison correction applied (thresholds are unambiguous — the
  significant rungs sit at p ≤ 0.007, far from 0.05).
