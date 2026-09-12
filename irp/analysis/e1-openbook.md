# E1 Condition B results — open-book (docs-RAG) vs closed-book (RQ1b / H1c)

**Run:** 2026-09-12, Mac quality axis (D4/D25 aggregate-proxy logic), llama.cpp b9951, greedy/seed-0,
full 164 HumanEval+, EvalPlus plus-tests. Open-book = the frozen artefact
(`proposal-dev/pilot/e1/openbook_prompts.jsonl`, sha256 `95069f4b…`: top-2 BM25 chunks from the pinned
Python-3.12 docs + the unchanged closed-book prompt; contamination-swept, 0 ≥13-gram overlaps).
Protocol: `irp/extensions/e1-protocol.md` (commit `8375d3c`); analysis: `e1_analysis.py`
(paired McNemar B-vs-A on the same 164 problems + bootstrap 95% CIs, B=10 000, seed 0).
Raw: `results/mac/pilot_results_open_20260912_144604.csv` + per-problem eval_results (regenerable).

## Results (pass@1 plus; Δ = open − closed; * = McNemar p < 0.05)

**Qwen2.5-Coder-1.5B (code-specialised):**

| rung | closed A | open B | Δ(B−A) | Δ 95% CI | McNemar p | broke/rescued |
|---|---:|---:|---:|---|---:|---:|
| F16 | 0.610 | 0.537 | −0.073 | [−0.140, −0.006] | 0.050 | 22/10 |
| Q8_0 | 0.616 | 0.543 | −0.073 | [−0.134, −0.006] | 0.043* | 21/9 |
| Q4_K_M | 0.616 | 0.549 | −0.067 | [−0.134, −0.006] | 0.061 | 20/9 |
| Q3_K_M | 0.585 | 0.549 | −0.037 | [−0.104, +0.024] | 0.362 | 18/12 |
| **Q2_K** | 0.384 | 0.287 | **−0.098** | [−0.165, −0.030] | **0.007*** | 24/8 |

**Phi-3-mini-3.8B (general):**

| rung | closed A | open B | Δ(B−A) | Δ 95% CI | McNemar p | broke/rescued |
|---|---:|---:|---:|---|---:|---:|
| F16 | 0.646 | 0.628 | −0.018 | [−0.085, +0.049] | 0.728 | 18/15 |
| Q8_0 | 0.628 | 0.610 | −0.018 | [−0.085, +0.049] | 0.720 | 17/14 |
| **Q4_K_M** | 0.549 | 0.396 | **−0.152** | [−0.238, −0.067] | **0.0008*** | 39/14 |
| Q3_K_M | 0.427 | 0.402 | −0.024 | [−0.098, +0.049] | 0.627 | 21/17 |
| Q2_K | 0.220 | 0.177 | −0.043 | [−0.104, +0.018] | 0.265 | 18/11 |

**5pp collapse thresholds are condition-invariant:** Qwen Q2_K and Phi Q4_K_M in *both* conditions.

## Findings

1. **⭐ Frozen sparse doc-context never helps — it mildly hurts, in all 10 cells (Δ ≤ 0 everywhere).**
   For self-contained HumanEval+ problems, top-2 BM25 chunks from the Python docs are mostly
   tangentially relevant (as the protocol pre-registered via DocPrompting's BM25 recall ≈ 9.7%), so the
   injected context acts as a **distraction, not a resource**. The pre-registered "near-zero F16 lift is
   itself reportable" outcome landed — and slightly below zero.
2. **⭐ The largest, most significant harm sits at each model's own collapse rung.** Qwen's worst Δ is
   at **Q2_K** (−0.098, p = 0.007 — its collapse rung); Phi's worst is at **Q4_K_M** (−0.152,
   p = 0.0008 — *its* collapse rung, 39 closed-book passes broken). A model at its quantisation cliff is
   **least able to ignore irrelevant context** — the "context-following degrades alongside/faster than
   generation" conjecture, manifesting as amplified distraction cost. (Two models, one alignment each —
   suggestive pattern, stated as such.)
3. **The collapse threshold itself does not move with condition** — open-book neither rescues nor
   accelerates the 5pp threshold (Q2/Q4 in both conditions). Deployment-wise, **closed-book Qwen @ Q4_K_M
   remains the best operating point**; naive doc-stuffing is counterproductive, and more so under
   aggressive quantisation.
4. **H1c verdict (the pre-registered interaction):** the open-book effect is **not constant** across the
   ladder — Phi's Δ ranges from −0.018 (F16) to −0.152 (Q4) — but the shape is a **spike at the collapse
   rung**, not a monotone slope. H0c (constant benefit) is untenable descriptively at Phi-Q4; the formal
   claim is kept modest: per-rung Δ with CIs as reported, no difference-of-differences test registered.

## Caveats (carry into the write-up)
- **10 comparisons, no correction pre-registered:** under Bonferroni (α=0.005) Phi-Q4 (0.0008) survives;
  Qwen-Q2 (0.007) survives BH-FDR but not strict Bonferroni; the borderline cells (Qwen F16 0.050,
  Q8 0.043, Q4 0.061) are reported as-is and not leaned on. The two headline cells are the robust ones.
- **This is BM25-only, k=2, docs-only, by design (D27):** the finding is about *frozen sparse
  doc-retrieval on self-contained problems* — not about retrieval-augmentation in general. Real assisted
  coding (project-local context, genuinely relevant snippets) may behave differently → external-validity
  limit + the E2 "beyond stock" question.
- Phi open-book parse_rate dipped slightly at Q3/Q2 (0.988/0.982) — context consumed budget/attention.
- Cross-device: the open-book quality axis inherits the D25 aggregate-proxy status — **confirmed by the
  pre-registered K=25 spot-check (2026-09-12, Qwen Q4 open-book, all three tiers): 4/25 outputs diverge
  (16%), 1/25 flips correctness** (HumanEval/10: Pi pass, Mac+Jetson fail — the reverse direction of the
  closed-book flip, consistent with backend divergences cancelling in aggregate). Same profile as
  closed-book (24% / 1-in-50).

## Mechanism check (exploratory, post-hoc): relevance does NOT explain which problems break

`e1_relevance_harm.py` (2026-09-12): among closed-book passers, does per-problem harm (closed-pass →
open-fail) track (a) the injected chunks' **BM25 relevance** or (b) **context length**? Answer:
**neither, in either model** — Phi shows no signal on any test (p ≈ 0.12–1.0); context length is null
everywhere; and the single nominal result (Qwen pooled, median-split Fisher p = 0.020, one of eight
uncorrected exploratory tests) runs **opposite** to the naive distraction story: the **higher**-relevance
half breaks *more* (63/230 vs 42/231). Two honest readings: (i) BM25 lexical overlap ≠ usefulness, so
"plausible-looking but unhelpful" text may be the worst distractor (obviously-irrelevant text is easier
to ignore), or (ii) harm is roughly uniform and the hint is noise. Either way, the harm is **not**
concentrated in low-scoring retrievals — which **undermines naive score-thresholded retrieval-gating as
a fix** (E2 planning consequence) and keeps the honest mechanism statement at "prepended
doc-context interferes broadly, not merely when it is obviously off-topic."
_Side-benefit: recomputing retrieval scores re-verified determinism — 164/164 problems' top-2 chunk
sources match the committed artefact._

## Perf tie-in — the price of context, per tier (Qwen Q4_K_M, same-session closed/open pairs, 2026-09-12)

| tier | TTFT mean, closed → open | decode tok/s | Δ peak RSS | note |
|---|---|---|---|---|
| Mac (Metal) | 23.5 → 113 ms (~5×) | 165 → 163 | +200 MB | invisible in absolute terms |
| Jetson (CUDA) | 77 → 1,184 ms (~15×) | 39.8 → 38.8 | +196 MB | at/near the registered 1–2 s TTFT floor |
| Pi 5 (CPU) | 589 → **4,957 ms** (~8×) | 11.0 → 10.0 | +243 MB | **breaks the registered TTFT floor outright** |

_Medians are cache-flattered (llama-server reuses the prompt prefix across the K=3 repeats → bimodal
cold/cached distributions, std > mean on the Pi); the means carry the honest cold prefills._
**Reading:** injected context costs **prefill latency and KV memory, not decode rate** — and that cost
is a *tier property*: negligible on the Mac, SLO-threatening on the edge GPU, SLO-breaking on the CPU
tier. So even under a hypothetical quality benefit, open-book would have cost the Pi its pre-registered
TTFT compliance; combined with RQ1b (quality harm) and RQ1c (tool-use floor), the closed-book-on-the-edge
recommendation is **overdetermined** — quality, capability, latency and memory all point the same way.
Raw: `results/{mac,jetson,pi5}/perf_results{,_open}_2026091*.csv`.

## RQ1b answer (one line)
**Reference-documentation context does not mitigate quantisation-induced degradation on HumanEval+ — it
adds a distraction cost that is worst exactly at each model's collapse rung, while leaving the collapse
threshold itself unchanged.**
