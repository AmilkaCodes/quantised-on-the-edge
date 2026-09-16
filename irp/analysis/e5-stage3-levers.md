# E5 stage-3 — the two non-training levers: calibration rescues, docs-formatting doesn't (2026-09-14)

**Registration:** stage-3 addendum in `e5-false-api-raft.md`. Both levers leave model weights
untouched. Baselines = the G3 naive-ladder cells (same frozen tasks, same runner, temp 0, n=120).
Exploratory measurements (no pre-committed thresholds); paired exact McNemar throughout.

## Lever 1 — imatrix-calibrated quantisation (E2b artefacts on FAB): **DECISIVE RESCUE**

1.5B, naive → calibrated (same bit-widths, same rungs):

| rung | B: naive → imat | O: naive → imat |
|---|---|---|
| Q4_K_M | 0.967 → 0.983 | 0.925 → 0.958 |
| Q3_K_M | 0.875 → 0.958 | 0.958 → 0.992 |
| Q2_K | 0.592 → **0.933** (+34.1 pp; 43/2, p = 5.9×10⁻¹¹) | 0.408 → **0.967** (+55.9 pp; 69/2, p = 2.2×10⁻¹⁸) |

- **⭐ "Benefit follows the cliff" is now CAUSAL.** G3 showed context-benefit collapsing where
  the quality cliff sits; E2b showed calibration moves the cliff. Stage-3 closes the loop:
  apply the cliff-moving intervention and the context-benefit returns — at Q2, to within 5 pp
  of full precision (0.933/0.967 vs F16's 0.983/0.958). Same bits, different rounding, +34/+56 pp.
- **⭐ The pathological B>O inversion is a naive-quantisation artefact.** Under calibration the
  ordering normalises (O 0.967 ≥ B 0.933; O−B no longer significant, p = .39). The bizarre
  "distractors help" regime exists only in the naively-quantised model.
- **The rescue is larger for context-exploitation than it was for generation.** E2b's HumanEval
  Q2 rescue was ≈ +15 pp; FAB's is +34/+56 pp — consistent with G3's finding that context-use
  is the cliff's first casualty: the faculty that falls furthest recovers furthest.

## Lever 2 — example-dense documentation (3 worked examples/page): **NULL (direction +, n.s.)**

| cell | sparse → dense | McNemar |
|---|---|---|
| F16 B (control) | 0.983 → 0.983 | no effect at full precision, as it should be |
| Q3 B | 0.875 → 0.892 | — |
| Q3 O | 0.958 → 0.975 | — |
| Q2 B | 0.592 → 0.650 | 15/8, p = .21 |
| Q2 O | 0.408 → 0.442 | 15/11, p = .56 |

- **The G3 finding-4 mimicry hypothesis is NOT supported in its strong form.** Density-per-page
  lifts every quantised cell a little, but not significantly, and the B>O inversion PERSISTS
  under dense docs (0.650 > 0.442). Whatever the collapse-rung model feeds on, it tracks
  **page count / total context redundancy** (B's 5 pages vs O's 1–2), not worked-example
  density per page. The hypothesis survives only in a weakened, untested variant ("more total
  redundant context helps at Q2") — recorded, not pursued.
- Practical read: docs formatting is NOT a usable edge-deployment lever at the collapse rung;
  artefact choice is.

## The deployment sentence this arc earns

> On an edge device, the fix for quantisation-broken context-use is **in the quantiser, not in
> the prompt and not in training**: calibrated quantisation recovers nearly all of the lost
> exploitation at identical memory cost, while docs formatting moves nothing significantly and
> LoRA fine-tuning (stage 2) actively subtracts. Rank the levers: imatrix ≫ formatting ≈ 0 > LoRA (< 0).

## Caveats
- Exploratory (registered as such); one seed, one benchmark generation; n=120 per cell.
- imat artefacts use the E2b bartowski calibration set — general-text calibration, not
  FAB-specific (which makes the rescue MORE striking, and rules out calibration-set leakage:
  the calibration text contains no FAB content by construction).
- Lever-2 nulls are 120-task cells; a small true effect (< ~8 pp) would not reach significance.

## R2 verification (2026-09-15, stage-4): the rescue is deployment-free — MEASURED

Registered expectation (tok/s, TTFT, RSS within noise of naive Q2_K) confirmed on both edge
tiers (N=10×3, study caps, b9951):

| device | metric | naive Q2_K | imat Q2_K |
|---|---|---:|---:|
| Pi 5 | med tok/s / peak RSS / mean W | 14.8 / 1,125 MB / 7.82 | 14.5 / 1,112 MB / 7.93 |
| Jetson | med tok/s / peak RSS / mean W | 32.3 / 1,506 MB / 15.22 | 32.4 / 1,516 MB / 15.19 |

The deployment sentence stands as measurement, not inference: calibrated quantisation buys the
context-exploitation rescue at identical inference cost on both edge devices.
