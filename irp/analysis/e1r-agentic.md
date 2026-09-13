# E1-R Probe R1 results — model-chosen retrieval under grammar constraint (RQ1c revisited)

**Runs:** 2026-09-13, Mac, per `../extensions/e1r-protocol.md` (`400edc8`); grammar
`e1/search_call.gbnf` (committed pre-run); harness `e1/e1r_grammar.py`. Two-stage single-call
design: stage-1 query decoding grammar-constrained (malformed syntax impossible), stage-2 =
Condition-B-format injection of the model's own top-2 BM25 chunks (runtime 13-gram guard).
Qwen2.5-Coder-1.5B only (protocol). Gate record: `results/mac/r1_F16_gateK20/`.

## Gate (F16, K=20): **PASS — M1′ = 20/20**
The same model that produced 0/20 valid native tool calls (E1 gate) and degenerated 20/20 under
`tool_choice` forcing produced **20/20 non-degenerate, sensible queries** once GBNF carried the
syntax (e.g. "python mean absolute deviation function", "rolling max python typing list tuple").
**The E1 capability deficit was FORMAT, not intent-formulation** — deleted by a 6-line grammar.

## Ladder (5 × 164): query quality, degeneration, and paired pass@1

| rung | M1′ | stage-2 degen | R1 pass@1 | A (closed) | B (fixed BM25) | R1−A | p | R1−B | p |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| F16 | 0.988 | 5 | 0.561 | 0.610 | 0.537 | −0.049 | .185 | +0.024 | .597 |
| Q8_0 | 0.988 | 5 | 0.555 | 0.616 | 0.543 | −0.061 | .087 | +0.012 | .860 |
| Q4_K_M | 0.988 | 6 | 0.512 | 0.616 | 0.549 | **−0.104** | **.002** | −0.037 | .327 |
| Q3_K_M | 0.982 | 5 | 0.494 | 0.585 | 0.549 | **−0.091** | **.008** | −0.055 | .163 |
| **Q2_K** | **0.860** | **26** | 0.268 | 0.384 | 0.287 | **−0.116** | **.003** | −0.018 | .701 |

## Findings
1. **Scaffolding fully repairs the protocol layer.** With grammar-constrained decoding, query
   formulation is near-perfect (M1′ ≈ 0.99) down to Q3_K_M — the "agentic floor" of E1/E2a was a
   formatting-and-policy artefact, not an inability to express retrieval intent.
2. **The query-formulation machinery breaks at the collapse rung**: M1′ drops to 0.860 at Q2_K with
   stage-2 degeneration jumping 5→26 — the collapse-rung signature appearing in yet another
   subsystem (query writing), independent of generation quality itself.
3. **Model-chosen context does not rescue open-book.** R1 tracks fixed-BM25 B everywhere (all
   R1−B n.s.) and is **significantly worse than closed-book at Q4/Q3/Q2** (p = .002/.008/.003) —
   letting the model choose the query changes nothing about the harm; harm deepens down the ladder.
4. Combined with R2 (oracle): **neither agency over selection nor quality of selection makes
   injected context help.** The scaffolding question is answered on both sides: *syntax is
   scaffolding-fixable; context-exploitation is not.*

## RQ1c REVISIT answer (one line)
**With the protocol layer scaffolded away, an edge-class model can drive retrieval competently at
full precision — but the retrieved context still does not pay, and both the query machinery and the
context benefit collapse together at the quantisation cliff.** Fine-tuning remains Future Work
(e1r-protocol binding rule).
