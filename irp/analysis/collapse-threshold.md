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
- **Collapse threshold — PRE-REGISTERED definition (verbatim from the submitted proposal, Methodology):**
  a configuration is *quality-acceptable* if **pass@1 stays within five percentage points (5pp) of the
  model's F16 baseline** ("one threshold, all tiers"); the **collapse threshold is the first rung whose
  pass@1 falls more than 5pp below F16**. This registered margin is the primary criterion.
- **Reported alongside it (also pre-registered):** the paired **McNemar exact** significance test (§2), and
  **bootstrap 95% CIs on each pass@1**, with **margin verdicts reported together with their intervals**.
  The proposal explicitly anticipated that a 164-problem CI (~±7pp) is *wider* than the 5pp margin, so a
  rung's margin verdict "may be inconclusive even where McNemar rejects" — §3b confirms exactly this at the
  two boundary rungs. The margin criterion and McNemar **agree on the threshold** (Qwen Q2, Phi Q4; §4).

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

## 3b. Pre-registered 5pp margin + bootstrap 95% CIs

Drop = F16 − rung (positive = degradation); percentile bootstrap, B = 10 000, seed 0, resampling the 164
paired per-problem outcomes. **pass@1 CI** is the registered per-estimate interval (~±7pp as predicted);
**drop CI** is the *paired* interval (tighter — the correct one for the margin verdict, and why McNemar can
reject where the per-estimate CIs overlap).

**Qwen2.5-Coder-1.5B** — margin threshold = **Q2_K**:

| rung | pass@1 (95% CI) | drop vs F16 (95% CI) | 5pp verdict |
|---|---|---|---|
| F16 | 0.610 [0.537, 0.683] | — | baseline |
| Q8_0 | 0.616 [0.543, 0.689] | −0.6pp [−3.0, +1.2] | within 5pp |
| Q4_K_M | 0.616 [0.543, 0.689] | −0.6pp [−5.5, +3.7] | within 5pp |
| Q3_K_M | 0.585 [0.512, 0.659] | +2.4pp [−3.0, +7.9] | within 5pp (point) — **CI straddles 5pp → inconclusive** |
| Q2_K | 0.384 [0.311, 0.457] | +22.6pp [+14.6, +30.5] | **outside 5pp → collapse** |

**Phi-3-mini-3.8B** — margin threshold = **Q4_K_M**:

| rung | pass@1 (95% CI) | drop vs F16 (95% CI) | 5pp verdict |
|---|---|---|---|
| F16 | 0.646 [0.573, 0.720] | — | baseline |
| Q8_0 | 0.628 [0.555, 0.701] | +1.8pp [−0.6, +4.9] | within 5pp |
| Q4_K_M | 0.549 [0.470, 0.628] | +9.8pp [+3.0, +16.5] | **outside 5pp → collapse (point)** — CI straddles 5pp |
| Q3_K_M | 0.427 [0.348, 0.500] | +22.0pp [+14.6, +29.9] | **outside 5pp → collapse** |
| Q2_K | 0.220 [0.159, 0.280] | +42.7pp [+34.1, +51.2] | **outside 5pp → collapse** |

**Reading (as pre-registered):** the point-estimate margin threshold matches McNemar exactly (Qwen Q2, Phi
Q4). At the **two boundary rungs the drop CI straddles 5pp**, so the *margin* verdict there is formally
**inconclusive at 95%** — Qwen Q3 (+2.4pp, may be up to +7.9) and Phi Q4 (+9.8pp, may be as little as
+3.0). This is exactly the tension the proposal flagged: **Phi Q4's McNemar rejects (p = 0.007) yet its 5pp
margin verdict is CI-inconclusive** — the two tests answer different questions (McNemar: "is there *any*
paired change?"; margin: "is the drop specifically ≥5pp?"). The threshold *location* is robust; the
boundary rung's *acceptability* is reported with its stated uncertainty rather than overclaimed.

## 4. Thresholds + the model-dependent finding
_Both the pre-registered 5pp margin (§3b) and McNemar (§3) give the same threshold per model:_
- **Qwen2.5-Coder-1.5B (code-specialised):** within 5pp of F16 through Q3 (point drops ≤ +2.4pp; McNemar
  p ≥ 0.52); **collapses at Q2** (drop +22.6pp, 95% CI [+14.6, +30.5]; McNemar p = 1.2×10⁻⁷; 44% of
  F16-passes break). → **Threshold = Q2 (≈2-bit).**
- **Phi-3-mini-3.8B (general):** within 5pp only at Q8; **collapses at Q4** (drop +9.8pp; McNemar
  p = 0.007; 23% break), worsening monotonically to Q2 (+42.7pp, 70% break). → **Threshold = Q4 (≈4-bit).**
  _(The Q4 margin verdict is CI-inconclusive at 95% — §3b — but the threshold location is corroborated by
  McNemar and by the unambiguous Q3/Q2 drops.)_
- **⭐ The collapse threshold is MODEL-DEPENDENT**, and the difference is statistically robust: the
  code-specialised model tolerates aggressive quantisation **two rungs further** before significant loss.
  This is RQ1's answer, now grounded in paired significance testing rather than eyeballed curves.

## 5. RQ mapping
- **RQ1 (how far can we quantise before collapse):** answered per model (§4).
- **RQ3 (does the threshold shift with hardware tier?):** **No meaningful shift — but with a measured
  caveat, not "by construction".** pass@1 is deterministic *within* a device, and the collapse threshold is
  a large quantization effect (20–40 pp). The pre-registered **cross-device spot-check
  (`cross-device-check.md`) found outputs are NOT byte-identical across backends** — Metal/CUDA/CPU
  floating-point differences change greedy decoding on a minority of problems and can flip individual
  pass/fail. So the emitted code is *not* strictly hardware-independent; the *threshold* is robust because
  quantization dwarfs that backend noise, but exact per-tier pass@1 is a **validated proxy (Mac), not an
  identity**. The quality-(mostly)-independent / performance-(strongly)-dependent separation stands as the
  finding, now stated with its real uncertainty rather than asserted "by construction".

## 6. Caveats
- pass@1 from per-problem eval_results is authoritative; run-CSV parsed values may differ by ≤1 problem.
- HumanEval+ contamination inflates absolute levels equally across rungs → the *relative* collapse (the
  threshold) is robust (RESULTS §5 caveat).
- Single dataset (HumanEval+, n=164); MBPP+ / a second task = future work. McNemar exact handles the
  small discordant counts; no multiple-comparison correction applied (thresholds are unambiguous — the
  significant rungs sit at p ≤ 0.007, far from 0.05).
