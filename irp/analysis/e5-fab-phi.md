# E5/R3 — Phi-3 FAB ladders: benefit-follows-the-cliff generalises across models (2026-09-15)

**Registration:** `e5-stage4-completion.md` R3. Phi-3-mini-4k-instruct (3.8B, general model;
generation cliff **Q4_K_M** in the main study; E2b moved it to Q2 under calibration). Same
frozen FAB v1, runner, n=120/cell. All A cells 0.000 (docs-necessity model-independent; no
instrument alert fired).

## Naive ladder

| rung | A | B | R | O |
|---|---:|---:|---:|---:|
| F16 | 0.000 | 0.875 | 0.900 | 0.950 |
| Q8_0 | 0.000 | 0.875 | 0.900 | 0.950 |
| Q4_K_M | 0.000 | **0.775** | 0.800 | 0.875 |
| Q3_K_M | 0.000 | 0.650 | 0.675 | 0.800 |
| Q2_K | 0.000 | **0.217** | 0.292 | 0.383 |

## Calibrated arm (E2b imat artefacts)

| rung | B: naive → imat | O: naive → imat |
|---|---|---|
| Q4_K_M | 0.775 → **0.958** (25/3, p = 2.7×10⁻⁵) | 0.875 → **0.992** |
| Q3_K_M | 0.650 → 0.842 | 0.800 → 0.900 |
| Q2_K | 0.217 → 0.425 | 0.383 → **0.892** (61/0, p = 8.7×10⁻¹⁹) |

## Answers to the three registered questions

1. **Does Phi exploit necessary context at F16? Yes** — 0.000 → 0.875 closed→open; the general
   model reads docs nearly as well as the coder pair despite far weaker closed-book coding.
2. **⭐ Does Phi's FAB collapse sit at ITS cliff (Q4), not Qwen's (Q2)? YES — the cross-model
   confirmation.** Degradation onset is exactly Q4 (B −10 pp, 20/8, p = .036), deepening
   monotonically below it to Q2's −65.8 pp (83/4, p = 3×10⁻²⁰) — while the Qwen 1.5B at the
   same Q4 rung was still at 0.967. Same bits, different models, damage tracks each model's own
   quality cliff. **"Benefit follows the cliff" is a property of the model×recipe cliff, not of
   bit-width — now shown with cliffs three rungs apart.**
3. **Does calibration move the collapse as it moved the cliff? Yes, with the depth pattern the
   claim predicts.** E2b moved Phi's generation cliff Q4→Q2; on FAB, calibration fully rescues
   Q4 (0.958/0.992 — above F16) and partially rescues Q2 (B 0.425; O 0.892) — Q2 is where the
   relocated cliff now SITS, so partial rescue at the new edge is the expected signature.
   (Contrast Qwen, whose cliff calibration pushed past Q2 entirely → full 0.933/0.967 rescue.)

## Fine structure

- **The die-first ordering replicates cross-model:** at every degraded rung O > R > B (clean
  docs most robust; distractor filtering goes first). Phi shows NO B>O inversion at any rung —
  the inversion is not universal.
- **But the single-call anomaly IS present, in a stronger form:** at naive Q2, Phi's B singles
  are 0.029 vs chains 0.48 — near-total single-call failure across all conditions, the same
  fixation family as Qwen's one-page effect (R1b), expressed differently. Deep-collapse
  small-model context processing fails on the SIMPLEST prompt shapes first — a robust,
  counter-intuitive signature now seen in two unrelated models.

## Caveats
- One seed, FAB v1 generation; cross-model comparisons unpaired (McNemar used within-model only).
- Phi F16 exploitation (0.875) sits below the Qwen pair (0.983/0.992) — instrument difficulty
  interacts with coding skill; qualitative cross-model reads only, per registration.
