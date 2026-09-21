# MBPP+ robustness extension — results (2026-09-18)

**Registration:** `irp/extensions/mbpp-extension.md` (2026-09-16, pushed before any run;
completion note dated 2026-09-18 discloses the twin-registration cell provenance: 8/10 cells
executed under the same-day E6 registration with identical constants, 2 fill-in cells — Phi
Q8_0, Q3_K_M — run 2026-09-18 under this registration). **Classification: registered
robustness extension, exploratory-registered, reported separately from the RQ1 claims.**

**Provenance manifest:** llama.cpp b9951, greedy, seed 0, caps 768/4096, Mac; study ggufs
(shas per study manifests); **evalplus 0.3.1; MbppPlus-v0.2.0.jsonl, sha256 b54e762755248ca4…**;
stale eval-caches deleted before scoring; per-problem eval_results snapshotted (10 files) to
`pilot/eval-results/mac/`. Metric = plus-status pass@1 (the study's convention throughout;
the EvalPlus CLI's base∧plus printout reads marginally differently — the R1-re-score appendix
documents the distinction).

## Instrument gate
F16 plus pass@1: **Qwen 0.638, Phi-3 0.661 — both ≥ 0.40. GATE PASS**; ladder reported.

## Ladders (n=378/cell; Δ vs F16 with percentile bootstrap 95% CI, B=10,000, seed 0; exact McNemar, Holm within model)

**Qwen2.5-Coder-1.5B-Instruct** (F16 = 0.638):

| rung | pass@1 | Δ vs F16 | 95% CI | Holm p | 5 pp yardstick |
|---|---:|---:|---|---:|---|
| Q8_0 | 0.627 | −0.011 | [−0.021, −0.003] | .25 | within |
| Q4_K_M | 0.630 | −0.008 | [−0.029, +0.013] | .63 | within |
| Q3_K_M | 0.571 | −0.066 | [−0.098, −0.037] | 1.2×10⁻⁴ | **beyond** |
| Q2_K | 0.423 | **−0.214** | [−0.262, −0.167] | 6.8×10⁻¹⁷ | **beyond** |

**Phi-3-mini-4k-instruct** (F16 = 0.661):

| rung | pass@1 | Δ vs F16 | 95% CI | Holm p | 5 pp yardstick |
|---|---:|---:|---|---:|---|
| Q8_0 | 0.664 | +0.003 | [−0.005, +0.013] | 1.00 | within |
| Q4_K_M | 0.640 | −0.021 | [−0.050, +0.008] | .43 | within |
| Q3_K_M | 0.474 | **−0.188** | [−0.230, −0.146] | 2.5×10⁻¹⁶ | **beyond** |
| Q2_K | 0.262 | **−0.399** | [−0.452, −0.347] | 5.7×10⁻³⁷ | **beyond** |

_Note 2026-09-21 (Ch3 §3.5 interval-only verdict classes): the "5 pp yardstick" column above
is the registered POINT criterion (descriptive threshold location). Under the interval
classes, Qwen Q3_K_M is **inconclusive** (CI straddles 5 pp) and Phi Q4_K_M is
**inconclusive** (bootstrap upper limit sits on the margin at 5.0 pp; the exact conditional
check gives 4.9 and the primary-interval rule resolves the disagreement to inconclusive);
all other cells keep their class. Data pack item 13._

## Verdict against the registered expectation

**The directional pattern replicates, with one one-rung shift each — and in opposite
directions:**
- **Qwen:** the HumanEval+ picture (flat to Q4, cliff at Q2 −22.6 pp) reproduces in shape
  and Q2 magnitude (−21.4 pp) — but MBPP+ additionally *resolves* a significant, beyond-margin
  Q3 step (−6.6 pp, Holm 1.2×10⁻⁴) that HumanEval+ left inside the margin (−2.4 pp, n.s.).
  Triple the problem count sharpened, not changed, the picture: material degradation begins
  one rung earlier than HumanEval+ could see.
- **Phi-3:** breaks early as registered, but at **Q3_K_M** on MBPP+ (Q4 −2.1 pp within
  margin; Q3 −18.8 pp) versus **Q4_K_M** on HumanEval+ (−9.8 pp) — the break point sits one
  rung lower here.
- Orderings are identical on both benchmarks (Phi breaks before Qwen; Q2 catastrophic for
  both; Q8 flat for both). Exact break-rung locations are benchmark-dependent by one rung in
  either direction — reported as informative benchmark-dependence per the registration's
  research-symmetry clause, and consistent with monotone latent damage surfacing at
  task-distribution-dependent thresholds.
- *Correction to the twin E6 analysis:* E6 lacked the Phi Q3 cell and read Phi's MBPP+ cliff
  as "Q2, two rungs below HumanEval+"; the completed grid shows the break at Q3 (one rung).
  `e6-mbpp-replication.md` carries a matching correction note.

## Caveats
- Exploratory-registered (postdates the proposal); separate from confirmatory RQ1 claims.
- Same INSTRUCTION wrap as HumanEval+ (registered decision — comparability over wording fit);
  MBPP+'s docstring-style prompts may interact with the wrap differently per model (level
  effect only; within-benchmark pairing controls it).
- Single benchmark pair; difficulty profiles differ non-uniformly by model.
- Q8 Qwen CI excludes zero at tiny magnitude (−1.1 pp) — a resolution artefact of n=378,
  well within the 5 pp yardstick; not read as degradation.
