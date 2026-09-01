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
- **The collapse finding is expected robust**: it is driven by *quantization* (a 20–40 pp effect), which
  dwarfs the backend numerical noise; and divergences flip in **both** directions (some tiers win a problem,
  some lose it), so aggregate pass@1 should be close across tiers even though individual problems differ.
  But **per-tier quality *equivalence* cannot be asserted** — confirming it would need full per-device
  quality runs (2×5×164 on each tier), which is infeasible on the Pi/Jetson (the reason quality is Mac-only).
- **RQ3 reframed:** the *quality collapse threshold* (a property of model×quant) is measured once and is
  robust to the small cross-backend noise; what shifts per tier is performance/energy. But the earlier
  wording "outputs are byte-identical / quality is exactly hardware-independent" is **too strong** and is
  corrected to "quality is *approximately* hardware-independent — dominated by quantization, with a small,
  measured backend-numerics effect that can flip individual problems."

## Not yet quantified (optional follow-up)
The 8-problem sample establishes *that* divergence and correctness-flips occur; it does **not** quantify the
aggregate rate or the net effect on pass@1. A larger spot-check (e.g. K=50 per tier, scored with EvalPlus)
would bound the per-tier pass@1 spread — worth doing if the write-up needs a number on it. Flagged, not run.
