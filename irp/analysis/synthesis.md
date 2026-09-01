# Two-axis synthesis — from collapse thresholds to a deployment envelope (RQ1–RQ3)

**Inputs:** quality axis = `collapse-threshold.md` (per-problem HumanEval+ pass@1_plus, McNemar/Cochran,
Mac, hardware-independent); performance axis = `RESULTS.md §9` (median tok/s, peak RSS, Jetson power, per
tier). Figures: `figures/fig1–4`. Decisions/justification: `../decisions.md` D1–D22.

---

## 1. The structural result that makes the synthesis possible

The two axes **separate cleanly**, and that separation is itself the primary finding:

- **Quality is *approximately* a property of (model × quant).** Greedy + seed-0 makes pass@1
  **deterministic within a device** (re-run variance = 0.000, RESULTS §2). Across devices it is **not
  byte-identical**, however: the pre-registered cross-device spot-check (`cross-device-check.md`) found
  backend floating-point differences (Metal/CUDA/CPU) change greedy decoding on a minority of problems and
  can **flip individual pass/fail** (e.g. HumanEval/5: Jetson passes, Mac + Pi fail). Quantified at K=50
  (`cross-device-check.md`): **24% of outputs differ but only 1/12 flips correctness, so aggregate pass@1
  spans just ~2 pp across tiers (0.76–0.78)**. So the *collapse threshold* — a 20–40 pp quantization effect
  that dwarfs this backend noise — is robust and treated as hardware-independent (RQ3: **no meaningful
  shift**), and the Mac quality axis is a **good aggregate proxy** (tier-invariant to ~1 problem) — though
  exact per-tier pass@1 is not byte-for-byte identical.
- **Performance is a property of (model × quant × tier).** Throughput, memory and energy change with the
  backend — a large, first-order effect (unlike the small quality-side backend noise above).

Consequence: you can **choose the rung once** on quality grounds, then **read off the cost** of running
that rung on each tier. The collapse curve (fig1) sets the *floor* of admissible rungs; the performance
curves (fig2/fig4) set what each tier *charges* to operate there. This is the whole design in one sentence.

## 2. The quality-safe rung, per model (the floor)

From the paired tests (`collapse-threshold.md §4`), the **most aggressive rung with no significant loss
vs F16**:

| model | last quality-safe rung | first collapsed rung | headroom |
|---|---|---|---|
| **Qwen2.5-Coder-1.5B** (code-specialised) | **Q3_K_M** (p ≥ 0.52 through Q3) | Q2_K (p = 1.2×10⁻⁷; 44% of F16-passes break) | tolerates to ~3-bit |
| **Phi-3-mini-3.8B** (general) | **Q8_0** (p = 0.38) | Q4_K_M (p = 0.007; 23% break) | breaks already at 4-bit |

**⭐ Model-dependent threshold** — the code-specialised model survives **two rungs further**. This is the
sharpest single claim the study makes, and it is statistically robust, not eyeballed.

## 3. The trade-off knee (what you actually deploy)

Overlaying quality on speed (fig3, Mac tier) turns the floor into a *choice*:

- **Qwen — a genuine free lunch to Q4_K_M.** Q4 is the knee: quality is statistically identical to F16
  (0.616 vs 0.610) while throughput **doubles** (78 → 165 tok/s) and memory **halves** (3.2 → 1.2 GB).
  Quantising to Q4 costs nothing measurable and buys 2×/2×. The curve tracks *right* holding altitude.
- **Phi — no free lunch; you pay quality almost immediately.** The curve collapses **near-vertically**:
  Q4 already sheds ~10 points for a modest speed gain, and Q8 (the safe rung) is only ~1.7× faster than
  F16. A general model gives you a much worse bargain than a specialised one of *twice the size*.

So the deployable operating points are: **Qwen @ Q4_K_M** (aggressive, free) or **Qwen @ Q3_K_M** (one
rung further, still safe, more memory headroom); **Phi @ Q8_0** (the only safe rung, and it barely
fits the edge — §4).

## 4. The deployment envelope and the local↔cloud handoff (RQ2/RQ3 applied)

A rung is **deployable on a tier** iff it clears three gates simultaneously, all **pre-registered** (proposal
Methodology — the "good enough" definition, fixed before data collection):
(a) **quality-safe** — pass@1 within 5pp of F16 (§2);
(b) **fits RAM without swap** (fig4; both edge devices verified swap-free, D15);
(c) **meets the performance floor** — **≥ 8–10 tok/s sustained AND TTFT ≤ 1–2 s** (Nielsen's interactive
limits). These are *registered* floors, not an "illustrative" SLO, so the handoff boundary is **defined**,
not a knob. Reading the gates across tiers (median tok/s · median TTFT · peak RSS):

| case (rung is quality-safe?) | Mac (Metal) | Jetson (CUDA) | Pi 5 (CPU) | verdict vs the registered floor |
|---|---|---|---|---|
| **Qwen @ Q4_K_M** (✓ safe) | 165 tok/s · 60 ms · 1.2 GB | 40 · 64 ms · 1.8 GB | **10.9** · 106 ms · 2.1 GB | **all three PASS** — Pi *just* clears the 8–10 band; the happy path |
| **Qwen @ Q3_K_M** (✓ safe) | 143 · — | **18.6** (GPU trap, §5) | 12.7 · 90 ms | all pass the floor; Pi > Jetson here — but Q4 dominates Q3 on GPU |
| **Phi @ Q8_0** (✓ safe) | 58 · 6.1 GB | 14.6 · 6.5 GB | **2.6 tok/s** · 6.1 GB | **Pi FAILS the floor** (2.6 ≪ 8) → hand off; Jetson/Mac pass |
| **Phi @ F16** (✓ safe) | 36 · 9.8 GB | **won't fit (>8 GB)** | **won't fit** | **forced off the edge** → cloud/Mac only |

Two distinct handoff triggers emerge, different in kind — and both now bite against the *registered* floor:

1. **Memory-forced handoff (hard).** Phi-3 F16 (~9.8 GB) exceeds the 8 GB edge budget outright (fig4).
   The edge devices *cannot* run the full-precision 3.8B model at all — quantisation is the price of
   admission, not an optimisation. And because Phi collapses at Q4, the *only* rung both quality-safe and
   edge-fitting is **Q8_0** — a single viable point, no margin.
2. **Throughput-forced handoff (against the registered floor).** Even fitting and quality-safe, the Pi's
   CPU decode of **Phi @ Q8 = 2.6 tok/s misses the pre-registered 8–10 tok/s floor by ~3–4×** → that
   workload must hand off to the Jetson (14.6) / Mac (58) / cloud. The boundary is **fixed by the registered
   floor**, not chosen post hoc: **Qwen-Q4 on the Pi (10.9 tok/s) squeaks past it; Phi-Q8 on the Pi fails
   it.** (The Phi-Q2 Pi cell would also fail on TTFT — median 11.8 s, the D22 anomaly — but it is already
   quality-collapsed, so moot.)

**The synthesised recommendation** the study supports: *specialise the model, quantise to the knee, and
size the tier to the SLO.* A code-specialised 1.5B at Q4 serves interactively on every tier including a
CPU-only Pi; a general 3.8B forces you either to a bigger tier or to a cloud handoff, because its quality
breaks before its size does.

## 5. Where the tiers cross — the GPU-only Q3_K_M dip (a real handoff wrinkle)

The one place the tier ordering **inverts**: at Q3_K_M the Pi (12.8 tok/s) *overtakes* the Jetson (18.6,
down from 40 at Q4) — because the dip is **GPU-backend-specific** (Metal + CUDA, absent on CPU;
RESULTS §9 finding 2), localised to the GPU K-quant dequantisation kernel. Practically: **Q3_K_M is a
trap rung on the accelerated edge** — you pay for the GPU and get CPU-class throughput. For the Jetson,
Q4_K_M (40 tok/s) or Q2_K (32) is strictly better than Q3 (18.6); Q3's only advantage (a touch more
memory headroom than Q4) is not worth the ~2× throughput loss. This is a deployment rule that falls
straight out of the cross-tier data and would be invisible in any single-device study.

**The energy axis confirms the trap from a third angle, on both GPU backends (fig5, RESULTS §9).**
Energy-per-token has **two shapes**: on the **Pi (CPU) it falls monotonically** (Qwen 1.63 → 0.53 J/tok —
quantise as far as quality allows, it is a pure efficiency win), but on **both GPU tiers it is non-monotone**
— the Jetson (CUDA) optimum is Q4 (0.45 J/tok) with **Q3_K_M penalised *up* to 0.61 despite drawing the
fewest watts (11.3 W)**, and the **Mac (Metal) shows the identical shape** (Q4 optimum 0.16 J/tok, Q3 bumps
to 0.21) on entirely different silicon. So the Q3 dip is an **energy trap, not an energy saving** — the
raw-watts reading (which flags Q3 as "lowest power") reverses once you divide by throughput. Reproduced on
**two independent GPU backends** and **absent on the CPU**, it is the same GPU-kernel signature seen in
throughput, now corroborated in J/token. _(Boundary caveat: absolute J/token is not comparable across the
three power routes; the within-tier shape is — D13/D23.)_

## 6. What this feeds into the IRP

- **RQ1 (how far can we quantise before collapse):** per-model thresholds, §2 — grounded in paired
  significance tests.
- **RQ2 (the cost of operating there):** the deployment envelope, §4 — throughput/memory per tier at the
  quality-safe rung, with two named handoff triggers.
- **RQ3 (does the threshold shift with tier):** **no meaningful shift** — the collapse threshold is a
  quantization effect that dominates the small cross-backend numerical noise (`cross-device-check.md`); the
  *cost* (performance/energy) is what shifts per tier, and that shift is large (~15× Mac-vs-Pi) and
  occasionally non-monotone (§5). Caveat: outputs are **not** byte-identical across backends, so per-tier
  pass@1 is approximately — not exactly — equal (§1); the threshold *location* is robust, exact per-tier
  quality is a stated proxy.
- **The gap the near-twins leave** (Shi & Ding: datacentre GPUs only; Nguyen & Nguyen: CPU SBCs only) is
  exactly the CPU→edge-GPU→consumer-GPU span this synthesis quantifies (decisions D5).

### Honest limits (carry verbatim into the write-up)
- Single task/dataset (HumanEval+, n=164); MBPP+ / a second task = future work.
- **Energy** is software-captured on **all three tiers** (Mac powermetrics/SoC + Jetson VDD_IN + Pi 5
  PMIC rail-sum — corrected 2026-08-31, D13/D23). The three routes use different measurement boundaries,
  so *absolute* cross-tier J/token is not apples-to-apples (a common external meter would be needed for
  that); the *per-tier* J/token trend across the ladder is valid — and it reverses the raw-watts reading
  of the GPU Q3 dip (fewest watts, worst J/token) on both GPU backends.
- Cross-tier **memory** is cleanest **Pi-vs-Jetson** (identical instrumentation); Mac uses a different
  accounting path (D21).
- The Phi-3 Q2_K generation-time memory/TTFT spike is intermittent and **not** mechanistically pinned
  (D22) — flagged, not overclaimed.
- The §4 SLO floors (8–10 tok/s, TTFT 1–2 s per Nielsen) are the **pre-registered** "good enough"
  thresholds, applied as the primary gate — not illustrative. A different deployment context would set
  different floors, but these are the ones the proposal committed to and the verdicts use them.

## 7. Optional / future work — NONE required for the write-up

Data collection for every RQ is **complete** (quality + performance + energy, all three tiers, stats +
figures). The following would *strengthen* the study but are **explicitly scoped out** and **do not block
the dissertation** — they belong in the Future Work / Limitations section, not the results:

- **MBPP+ / a second coding task** — external validity beyond the single HumanEval+ dataset (n=164).
- **Q2_K anomaly, per-prompt instrumentation** — to pin the generation-time memory/TTFT spike mechanism
  (currently localised, not explained — D22).
- **Cross-tier *absolute* energy via one common external meter** — the only way to compare J/token across
  tiers at a single boundary; the current software routes differ (Mac SoC-domains · Jetson VDD_IN · Pi
  PMIC), so only the *within-tier* ladder shape is claimed (D13/D23).
- **Jetson sustained-load power/thermal (`jetson_clocks` / throttle watch)** — the one still-open device
  item in the setup log; a robustness characterisation, not an RQ input.

None of these requires re-running anything already collected; each is additive.
