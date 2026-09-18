# Cross-device low-rung spot-check — results (2026-09-18)

**Registration:** `irp/extensions/xdev-lowrung-addendum.md` (committed before the run).
Cell: Qwen2.5-Coder-1.5B-Instruct × Q3_K_M, K=50 first HumanEval+ problems, Mac (Metal) vs
Jetson (CUDA), `cross_device_check.py` (identical prompts/greedy/seed/caps via
`run_pilot.generate`), scored with the in-process canonical-oracle scorer
(`score_xdev_direct.py`, parameterised — mechanical diff in the same registration commit).

## Results

| readout | Q3_K_M (this cell) | Q4_K_M baseline (same pair) |
|---|---|---|
| output byte-identity (Mac vs Jetson) | **46/50 = 0.92** | 45/50 = 0.90 |
| pass@1 per tier | 0.660 / 0.660 (identical) | 0.740 / 0.760 |
| pass-pattern flips | **0/50 (0.0 pp)** | 1/50 (2.0 pp) |
| noise gate (identical solutions scoring differently) | 0 — clean | 0 — clean |

## Verdict

**The registered expectation's first clause is violated in the favourable direction and its
second clause holds with margin to spare.** Divergence did NOT worsen at the lower rung
(identity 0.92 vs 0.90; the flip-mechanism prediction of worse low-rung divergence is not
supported at this K), and pass-pattern disagreement is exactly zero — the implied tier noise
at the near-margin rung is 0.0 pp against the 5 pp margin. Under the addendum's symmetric
reporting rule: **the result strengthens the single-tier quality-axis proxy; the Q3_K_M
margin verdict is not tier-fragile.** Ch3 §3.2/§3.8's named caveat ("proxy validated at
Q4_K_M only") can now cite a low-rung measurement: one sentence for §3.8, data here.

## Caveats
K=50, one edge tier (CUDA; the Pi's CPU backend not re-checked at Q3 — the Q4 three-way check
covers it), one model, one low rung; identity rates carry ±~0.08 binomial noise at this K.
The conclusion drawn is the registered one only: margin verdicts at Q3 are not threatened by
Mac↔Jetson tier noise.
