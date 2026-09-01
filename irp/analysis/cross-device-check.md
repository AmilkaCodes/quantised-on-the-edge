# Cross-device output spot-check (pre-registered) — RESULT: outputs do NOT match across tiers

**Pre-registered commitment** (submitted proposal, Methodology): _"the quality sweep … runs once; a
cross-device spot-check confirms outputs match."_ This is the premise that licenses measuring the quality
axis **once on the Mac** and treating it as hardware-independent (RQ3).

**Method.** `proposal-dev/pilot/cross_device_check.py` — reuses `run_pilot.generate()` so prompt
formatting, **temperature 0, seed 0, max_tokens** are identical to the quality run. One rung
(**Qwen2.5-Coder-1.5B, Q4_K_M**), first **8 HumanEval+ problems**, **identical GGUF bytes** (staged from
the Mac) and **identical llama.cpp b9951** on all three tiers; only the backend differs (Metal / CUDA /
CPU). Run 2026-09-01 on Mac, Jetson, Pi; extracted solutions diffed. Raw:
`results/{mac,pi5,jetson}/xdev_qwen2.5-coder-1.5b-instruct_Q4_K_M.json`.

## Result — the premise is FALSIFIED, not confirmed

**3 of 8 problems produced different code on at least one tier**, and the divergence **changes
correctness**, not just formatting:

| problem | Mac | Jetson | Pi | note |
|---|---|---|---|---|
| HumanEval/0,2,3,6,7 | — | — | — | identical across all three (5/8) |
| HumanEval/1 | balance-counter | depth-counter | stack | 3 different algorithms, **all correct** |
| HumanEval/4 | inline | intermediate var | = Mac | different code, **all correct** |
| **HumanEval/5** | wrong (`[1,4,2,4,3,4]`) | **correct** (`[1,4,2,4,3]`) | wrong (`[1,3,4,2]`) | **all 3 differ; correctness FLIPS** |

On **HumanEval/5** the three backends emitted three different `intersperse` implementations and
**Jetson passes while Mac and Pi both fail (in different wrong ways)** — verified by executing each against
the canonical case. So **per-problem pass@1 is backend-dependent.**

## Mechanism (why)
Greedy decoding at temperature 0 is `argmax` over logits. The backends (Metal/CUDA/CPU) do floating-point
reductions in different orders → tiny numerical differences → an occasional **different argmax at an early
token**, after which the whole generation diverges into a different program (sometimes correct, sometimes
not). This is consistent with the observed pattern: most problems identical, a minority diverging wholesale.

**Note the two determinisms are different:**
- **Within a device:** fully deterministic — re-runs are byte-identical (RESULTS §2, Mac variance 0.000).
- **Across devices:** **NOT** identical — a stable per-backend difference, not run-to-run randomness.

## Implication for the study (honest)
- The proposal's "a cross-device spot-check confirms outputs match" **does not hold**; the corrected claim
  is: **outputs mostly agree but are not identical across backends, and per-problem correctness can flip.**
- **The quality axis (measured on the Mac) is internally valid** and consistent (deterministic on its own
  backend), but it is a **proxy** for the Pi/Jetson, **not an exact predictor** of their per-problem pass@1.
- **The collapse finding is robust, and now quantified so**: it is driven by *quantization* (a 20–40 pp
  effect) which dwarfs the backend noise. The K=50 scoring (below) confirms **aggregate pass@1 spans only
  ~2 pp across tiers** (0.76–0.78) even though 24% of individual outputs differ — divergence rarely flips
  correctness (1/12). So the Mac axis is a **good aggregate proxy** (per-tier pass@1 tier-invariant to ~1
  problem); full per-device quality runs (2×5×164 each) remain infeasible on Pi/Jetson, but this bounds
  what they would have shown.
- **RQ3 reframed:** the *quality collapse threshold* (a property of model×quant) is measured once and is
  robust to the small cross-backend noise; what shifts per tier is performance/energy. But the earlier
  wording "outputs are byte-identical / quality is exactly hardware-independent" is **too strong** and is
  corrected to "quality is *approximately* hardware-independent — dominated by quantization, with a small,
  measured backend-numerics effect that can flip individual problems."

## Quantified at K=50 (2026-09-01)

Extended to the **first 50 HumanEval+ problems** on all three tiers (same rung/model/tag/GGUF). Scored
**in-process against the canonical oracle** (`score_xdev_direct.py`) — EvalPlus's parallel exec sandbox
proved unreliable here (Bitdefender throttles its many short-lived exec subprocesses → mass spurious
timeouts; identical code scored differently, so those numbers are discarded). The in-process scorer passes
a **noise gate**: all 38 identical-solution problems score identically across tiers (0 anomalies), so its
per-tier differences are real, not scoring noise.

| metric | value |
|---|---|
| output **identical** across all three tiers | **38/50 (76%)** |
| output **differs** on ≥1 tier | **12/50 (24%)** |
| pairwise identical: Mac↔Jetson / Mac↔Pi / Jetson↔Pi | 45/50 · 40/50 · 39/50 |
| **correctness flips** among the 12 divergent problems | **1/12** (HumanEval/5: Jetson pass, Mac + Pi fail) |
| **per-tier pass@1** over the same 50 (canonical oracle, base+plus) | **Mac 0.760 · Jetson 0.780 · Pi 0.760** |

**The number that matters:** outputs diverge often (24%), but divergence **rarely changes correctness**
(1 of 12), so **aggregate pass@1 spans just 2 pp across the three tiers (0.76–0.78 — a one-problem gap).**
So the design's "measure quality once on the Mac" is a **good aggregate proxy** — per-tier pass@1 is
tier-invariant to within ~1 problem on this sample — **while the per-problem premise ("outputs match") is
false.** Both statements are true and both belong in the write-up: the headline collapse result is safe;
the byte-identity claim is not.

_(Caveat: the in-process oracle mirrors EvalPlus's canonical-vs-candidate check on base+plus inputs but is
not the EvalPlus CLI; it is used only for this cross-device delta, where EvalPlus was unreliable. The main
quality axis §1–6 remains EvalPlus-scored on the Mac.)_
