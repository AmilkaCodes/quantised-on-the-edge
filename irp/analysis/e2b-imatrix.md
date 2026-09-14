# E2b results — imatrix-calibrated quantisation (E2 Arm 1)

**Run:** 2026-09-14, Mac, per `../extensions/e2b-protocol.md` (`72e1c43`). Calibration: bartowski
`calibration_datav3.txt` (sha `200e109b…`, HumanEval-free), `llama-imatrix` at b9951 over each study
model's F16, calibrated Q4/Q3/Q2 requantised (`…-imat-*.gguf`). Closed 6 cells + open collapse-rung
cells ×164; paired McNemar + bootstrap CIs vs the naive ladder; margins vs the shared naive F16.

## H-E2b1 — closed-book: calibrated (I) vs naive (N), pass@1 plus

| model·rung | N | I | I−N (95% CI) | p | drop vs F16: N → I |
|---|---:|---:|---|---:|---|
| Qwen Q4_K_M | 0.616 | 0.616 | +0.000 [−0.043,+0.043] | 1.000 | −0.6 → −0.6 pp (nothing to fix) |
| Qwen Q3_K_M | 0.585 | 0.628 | +0.043 [+0.000,+0.091] | .119 | +2.5 → **−1.8 pp** |
| **Qwen Q2_K** | 0.384 | 0.530 | **+0.146 [+0.067,+0.226]** | **.0004** | +22.6 → **+8.0 pp** |
| **Phi Q4_K_M** | 0.549 | 0.628 | **+0.079 [+0.012,+0.146]** | **.029** | +9.7 → **+1.8 pp (within margin)** |
| **Phi Q3_K_M** | 0.427 | 0.628 | **+0.201 [+0.134,+0.268]** | **<.0001** | +21.9 → **+1.8 pp (within margin)** |
| **Phi Q2_K** | 0.220 | 0.360 | **+0.140 [+0.067,+0.213]** | **.0004** | +42.6 → +28.6 pp |

**⭐ Calibration moves Phi-3's collapse threshold TWO RUNGS: Q4_K_M → Q2_K.** Calibrated Phi at Q4
*and* Q3 sits 1.8 pp below its F16 — inside the pre-registered margin — where the naive ladder had
already broken. Qwen's threshold stays at Q2_K but the cliff is **halved** (+22.6 → +8.0 pp,
I−N +14.6 pp p=.0004). The benefit is model-dependent in mirror image of the collapse itself: the
general model (which broke early) is rescued wholesale; the code-specialised model (already robust
to Q3) gains only at its cliff.

## H-E2b2 — context harm at the collapse rung, calibrated vs naive

| cell | naive Δ(open−closed) | calibrated Δ |
|---|---|---|
| Phi @ Q4_K_M | −0.152 (p=.001) | **−0.037 (p=.377, n.s.)** |
| Qwen @ Q2_K | −0.098 (p=.007) | **−0.128 (p<.001) — persists** |

**⭐ The context harm follows the cliff, not the bit-width.** Calibration un-breaks Phi's Q4 —
and the context harm there *vanishes* (reverting to Phi's F16-level ≈0 harm). Calibration only
*softens* Qwen's Q2 (still +8.0 pp outside the margin) — and the context harm there *persists* in
full. Fifth appearance of the collapse-rung signature, now with an **intervention showing the
co-movement**: context-exploitation failure co-varies with residual quantisation damage, wherever
calibration relocates it.

## Reading
1. **"Use imatrix quants" is now a measured recommendation, not folklore:** stock public
   calibration (exactly what downloaded GGUFs use) buys +8 to +20 pp at the low rungs, two full
   rungs of threshold for the fragile model, at zero inference cost.
2. **D6 is vindicated in both directions:** the naive ladder was required to *see* the collapse
   (calibration masks +14–20 pp of it — precisely the masking D6 predicted); the calibrated arm
   then measures the mask. Control → experiment, as designed.
3. **The E1/E1-R conclusion stands, refined:** context still cannot help these models — but the
   *harm* is not a fixed property of a rung; it is a property of *being near one's collapse*, and
   calibration moves the collapse. (Qwen@Q2 calibrated remains cliff-adjacent → harm persists;
   Phi@Q4 calibrated is no longer a cliff → harm gone, though context still doesn't *help*.)

## Caveats
- One calibration corpus (the ecosystem default); code-domain calibration untested (future work —
  might further favour the coder model).
- Open cells only at the two naive collapse rungs (registered scope); a full calibrated open ladder
  was not run.
- Qwen Q3 I−N (+4.3 pp) has CI touching zero (p=.119) — reported, not leaned on.
- Two open-cell comparisons — small pre-registered scope; interpretation leans on the co-movement
  pattern across E1/E1-R/E2a/E2b, not on these two cells alone.
