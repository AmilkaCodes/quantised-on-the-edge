# E2b PROTOCOL — imatrix-calibrated quantisation arm (E2 Arm 1, activated)

**Status: PRE-REGISTERED BY COMMIT.** Activation 2026-09-14 (student decision; supervisor briefed in
the standing chase thread per the E1/E2a precedent; ethics delta nil — same models, same benchmark,
one additional public calibration text). Parameters fixed below BEFORE any measurement; later
changes = dated amendments. **Timebox: complete by 2026-09-16 or dropped.**

**Question:** D6 deliberately used a NAIVE ladder so calibration could not mask the collapse. E2b
flips that control into a measured comparison: **does importance-matrix calibration (the stock
deployment remedy) shift the collapse threshold or reduce low-bit degradation — and does it restore
context-robustness at the collapse rung?**

## Design
- **Models:** the two study models (Qwen2.5-Coder-1.5B-Instruct, Phi-3-mini-4k-instruct). The 7B is
  excluded — it has no collapse to rescue.
- **Calibration data (fixed):** bartowski's public `calibration_datav3.txt` — the file used for the
  public imatrix GGUF ecosystem, i.e. exactly what "stock calibrated quants" means in deployment
  (URL + sha256 recorded in the runbook at download; fallback if unreachable: wikitext-2-raw test
  split, recorded as a deviation). **It contains no HumanEval material; the standard contamination
  logic applies (calibration text is never benchmark text).**
- **Artefacts:** per model, `llama-imatrix` (b9951) over the model's F16 GGUF with the calibration
  text → `.imatrix` file (sha-logged); then `llama-quantize --imatrix` → **calibrated Q4_K_M,
  Q3_K_M, Q2_K** (filenames `…-imat-<rung>.gguf`, sha-logged). Q8_0/F16 unaffected by calibration —
  the shared naive F16 remains the baseline for all margins.
- **Runs (Mac quality axis, study caps, greedy/seed-0):**
  1. **Closed-book:** 2 models × {Q4_K_M, Q3_K_M, Q2_K} calibrated = 6 cells × 164.
  2. **Open-book (context-robustness check):** calibrated collapse rung only — Qwen Q2_K and
     Phi Q4_K_M — 2 cells × 164, same frozen Condition-B artefact.
- **Analysis (same machinery):** per rung, paired McNemar + bootstrap CI of **calibrated (I) vs
  naive (N)** on the same 164 problems; 5pp-margin threshold recomputed on the calibrated ladder
  (vs the shared F16); at the collapse rungs, Δ(open−closed) calibrated vs naive (does calibration
  shrink the context harm?).
- **Pre-stated expectations (all outcomes reportable):** H-E2b1: calibration reduces the collapse-
  rung drop (literature: calibrated low-bit quants outperform naive). H-E2b2 (open): the context
  harm at the collapse rung shrinks under calibration IF the harm is precision-noise-driven; a
  persistent harm despite calibration further generalises the E1/E1-R conclusion.

## Reporting
`irp/analysis/e2b-imatrix.md`; decisions register gains the D6-control-flipped note; RQ file gains
a dated clause under RQ1/RQ1b. Deviations below, dated, before affected runs.

## Deviations
_(none yet)_
