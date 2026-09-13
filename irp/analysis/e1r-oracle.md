# E1-R Probe R2 results — oracle-retrieval open-book (RQ1b boundary test)

**Run:** 2026-09-13, Mac, per `../extensions/e1r-protocol.md` (commit `400edc8`); oracle artefact
`e1/oracle_prompts.jsonl` (sha `875fe30d…`, mean top-1 solution-overlap 0.607, 0 thirteen-gram
fails). Oracle = **measurement instrument** (upper-bound selection by overlap with the canonical
solution; solution used only for selection, never in any prompt) — not a deployable system.
Both models × 5 rungs × 164; paired McNemar + bootstrap CIs vs closed (A) and fixed-BM25 (B).

## Results (pass@1 plus; O−A negative = oracle context hurts vs closed-book)

**Qwen2.5-Coder-1.5B:**

| rung | A | B | O | O−A (CI) | p | O−B | p |
|---|---:|---:|---:|---|---:|---:|---:|
| F16 | 0.610 | 0.537 | 0.567 | −0.043 [−0.116,+0.030] | .324 | +0.030 | .487 |
| Q8_0 | 0.616 | 0.543 | 0.561 | −0.055 [−0.122,+0.012] | .175 | +0.018 | .720 |
| Q4_K_M | 0.616 | 0.549 | 0.591 | −0.024 [−0.085,+0.037] | .557 | +0.043 | .311 |
| Q3_K_M | 0.585 | 0.549 | 0.537 | −0.049 [−0.116,+0.018] | .200 | −0.012 | .864 |
| **Q2_K** | 0.384 | 0.287 | 0.287 | **−0.098 [−0.177,−0.024]** | **.020** | +0.000 | 1.000 |

**Phi-3-mini-3.8B:**

| rung | A | B | O | O−A (CI) | p | O−B | p |
|---|---:|---:|---:|---|---:|---:|---:|
| F16 | 0.646 | 0.628 | 0.622 | −0.024 [−0.091,+0.037] | .572 | −0.006 | 1.000 |
| Q8_0 | 0.628 | 0.610 | 0.628 | +0.000 [−0.061,+0.061] | 1.000 | +0.018 | .736 |
| **Q4_K_M** | 0.549 | 0.396 | 0.445 | **−0.104 [−0.189,−0.018]** | **.021** | +0.049 | .291 |
| Q3_K_M | 0.427 | 0.402 | 0.396 | −0.030 [−0.104,+0.043] | .511 | −0.006 | 1.000 |
| Q2_K | 0.220 | 0.177 | 0.189 | −0.030 [−0.091,+0.030] | .424 | +0.012 | .851 |

## Verdict (pre-registered interpretation map)
- **O ≤ A at every rung, both models** — oracle context never helps, and the only *significant*
  harms sit at each model's own collapse rung (Qwen Q2, Phi Q4): the **fourth** independent
  appearance of the collapse-rung signature (after imposed-BM25 harm, J/token, and R1 query
  degeneration). → **map branch: "quantised small models cannot exploit context even when it is
  ideal — the strongest form of the RQ1b finding."**
- **O ≈ B at every rung** (all n.s.) → **selection quality is not the lever.** E1's distraction
  cost was never about BM25 being bad at ranking; it is about what injected context does to these
  models on self-contained tasks.
- With E2a's 7B result (context harm survives scale), the combined claim is now: **context
  injection on self-contained code tasks costs quality for this model class regardless of retrieval
  quality, model choice of query, or scale — and the cost concentrates at the quantisation cliff.**

## Caveats
- Oracle ≠ task-necessity: HumanEval+ problems remain self-contained; the untested (and now clearly
  future-work) condition is a task where documentation is *required*. The oracle bounds selection
  quality, not task-relevance of context per se.
- Two significant cells out of 10 O-vs-A tests (both at pre-identified collapse rungs); others n.s.
  with CIs spanning zero — the uniform claim is "never helps", the significant claim is
  rung-localised. Exploratory probe; no correction registered.
