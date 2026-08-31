# Two-axis synthesis — from collapse thresholds to a deployment envelope (RQ1–RQ3)

**Inputs:** quality axis = `collapse-threshold.md` (per-problem HumanEval+ pass@1_plus, McNemar/Cochran,
Mac, hardware-independent); performance axis = `RESULTS.md §9` (median tok/s, peak RSS, Jetson power, per
tier). Figures: `figures/fig1–4`. Decisions/justification: `../decisions.md` D1–D22.

---

## 1. The structural result that makes the synthesis possible

The two axes **separate cleanly**, and that separation is itself the primary finding:

- **Quality is a property of (model × quant) alone.** Greedy + seed-0 makes pass@1 deterministic
  (run-to-run variance = 0.000, RESULTS §2), and the emitted code is byte-identical across tiers. So the
  collapse threshold does **not** move with hardware (RQ3 answered: **no shift**).
- **Performance is a property of (model × quant × tier).** Throughput, memory and energy change with the
  backend; quality does not.

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
  (0.616 vs 0.610) while throughput **doubles** (78 → 166 tok/s) and memory **halves** (3.2 → 1.2 GB).
  Quantising to Q4 costs nothing measurable and buys 2×/2×. The curve tracks *right* holding altitude.
- **Phi — no free lunch; you pay quality almost immediately.** The curve collapses **near-vertically**:
  Q4 already sheds ~10 points for a modest speed gain, and Q8 (the safe rung) is only ~1.7× faster than
  F16. A general model gives you a much worse bargain than a specialised one of *twice the size*.

So the deployable operating points are: **Qwen @ Q4_K_M** (aggressive, free) or **Qwen @ Q3_K_M** (one
rung further, still safe, more memory headroom); **Phi @ Q8_0** (the only safe rung, and it barely
fits the edge — §4).

## 4. The deployment envelope and the local↔cloud handoff (RQ2/RQ3 applied)

A rung is **deployable on a tier** iff it clears three gates simultaneously:
(a) **quality-safe** (§2), (b) **fits memory without swap** (fig4; both edge devices verified swap-free),
(c) **meets a throughput SLO**. Reading the three gates across the tiers:

| case | Mac (Metal) | Jetson (CUDA) | Pi 5 (CPU) | handoff verdict |
|---|---|---|---|---|
| **Qwen @ Q4_K_M** | 166 tok/s, 1.2 GB | 40 tok/s, 1.8 GB | 11 tok/s, 2.1 GB | **serves locally on all three** — the happy path |
| **Qwen @ Q3_K_M** | 143 | **18.6** (GPU dip) | 12.8 | Pi *beats* Jetson here (§5); still local everywhere |
| **Phi @ Q8_0** | 58 tok/s, 6.5 GB | 14.6 tok/s, 6.5 GB | **2.8 tok/s**, 6.5 GB | edge *runs* it but the **Pi violates any interactive SLO** → hand off |
| **Phi @ F16** | 35 tok/s, 9.8 GB | **won't fit (>8 GB)** | **won't fit** | **forced off the edge** → cloud/Mac only |

Two distinct handoff triggers emerge, and they are different in kind:

1. **Memory-forced handoff (hard).** Phi-3 F16 (~9.8 GB) exceeds the 8 GB edge budget outright (fig4).
   The edge devices *cannot* run the full-precision 3.8B model at all — quantisation is not an
   optimisation here, it is the price of admission. And because Phi collapses at Q4, the *only* rung that
   is both quality-safe and edge-fitting is **Q8_0** — a single viable point, with no margin.
2. **Throughput-forced handoff (soft, SLO-dependent).** Even when a rung fits and is quality-safe, the
   Pi's CPU decode (Phi Q8 = 2.8 tok/s) will miss an interactive latency target that the Jetson (14.6)
   and Mac (58) meet. The handoff boundary is therefore **not** a fixed device property — it moves with
   the SLO you set.

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
- **RQ3 (does the threshold shift with tier):** **no** — quality is hardware-independent (§1); only the
  *cost* shifts, and the shift is large (~15× Mac-vs-Pi) and occasionally non-monotone (§5).
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
- SLO thresholds in §4 are illustrative ("interactive"); the *shape* of the handoff boundary is the
  finding, not a specific tok/s cutoff.
