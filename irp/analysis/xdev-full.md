# Full-ladder cross-device replication (xdev-full) — results

**Protocol:** `irp/extensions/xdev-full-protocol.md`, registered 2026-10-24 before any
measurement. **Class:** registered validation addendum, not confirmatory; no registered verdict
or threshold changes as a result. **Instrument:** HumanEval+, all 164 problems, closed-book,
greedy, seed 0, 768-token cap, llama.cpp b9951 per tier, identical GGUF bytes (SHA-256
agreement in `proposal-dev/pilot/CHECKSUMS.md`). Generation by `cross_device_check.py`
(tag `full164`, so the registered K = 50 files are untouched); scoring on the Mac only by
`score_xdev_full.py` (EvalPlus 0.3.1, plus status). 24 valid cells.

## 1. Mac determinism (the reference's own check)

Every Mac cell was regenerated through the same script and compared with the September
snapshots: **all 1,640 solutions across all ten cells are byte-identical**, including both
collapse rungs where outputs degenerate and run to the cap. Within-device greedy decoding at
seed 0 therefore reproduces exactly across a six-week gap, which is both the premise of the
two-axes split (§3.3.1) and the condition that makes the Mac a sound reference here. Because
the text is identical, Table 4.1's pass@1 values are reproduced exactly without re-scoring.

## 2. Qwen2.5-Coder-1.5B — all five rungs, both edge tiers

Mac reference in the first column; Δ is device minus Mac.

| rung | Mac | Jetson | Δ | p | Pi 5 | Δ | p |
|---|---:|---:|---:|---:|---:|---:|---:|
| F16 | 0.610 | 0.610 | 0.0 | 1.000 | 0.616 | +0.6 | 1.000 |
| Q8_0 | 0.616 | 0.598 | −1.8 | .250 | 0.616 | 0.0 | 1.000 |
| Q4_K_M | 0.616 | 0.616 | 0.0 | 1.000 | 0.628 | +1.2 | .688 |
| Q3_K_M | 0.585 | 0.585 | 0.0 | 1.000 | 0.591 | +0.6 | 1.000 |
| Q2_K | 0.384 | **0.360** | **−2.4** | .219 | **0.348** | **−3.6** | .180 |

**Weak form holds at F16, Q8_0, Q4_K_M and Q3_K_M on both tiers** — every |Δ| ≤ 1.8 pp, every
p ≥ 0.25. The † tier-uncertain flags at those rungs are resolved by measurement: the
Mac-measured verdicts stand for the edge tiers.

**Weak form fails at Q2_K on both tiers**, on the pass@1 clause alone (flips not significant).
Per the interpretation map, the Q2_K verdict is re-stated per tier rather than inherited.
Both tiers fall *below* the Mac and both show b > c, so the direction agrees across two
unrelated backends; no pooled test was registered, so this is reported as an observation, not
a verdict.

**At F16 the Jetson is byte-identical to the Mac** (identity 1.000, zero flips) — the *strong*
form, which neither K = 50 check reached.

## 3. Phi-3-mini — Pi 5 only

| rung | Mac | Pi 5 | Δ | identity | flips (b/c) | p | verdict |
|---|---:|---:|---:|---:|---|---:|---|
| Q8_0 | 0.628 | 0.634 | +0.6 | 0.896 | 1 / 2 | 1.000 | holds |
| Q4_K_M | 0.549 | 0.524 | **−2.5** | 0.634 | 6 / 2 | .289 | **fails** (pass@1 clause) |
| Q3_K_M | 0.427 | 0.445 | +1.8 | 0.524 | 3 / 6 | .508 | holds |
| Q2_K | 0.220 | 0.244 | **+2.4** | 0.201 | 5 / 9 | .424 | **fails** (pass@1 clause) |

The two failures are in *opposite* directions (Pi lower at Q4, higher at Q2), both with
balanced, non-significant flips — consistent with sampling noise around a stable underlying
score rather than a systematic tier effect, though the registered rule records them as
failures either way.

**Jetson Phi-3: NOT MEASURED — CAPACITY.** Both attempts ended in server OOM kills a few
problems into each cell (deviation recorded in the protocol, with the falsified first
diagnosis retained). Phi-3-mini Q8_0 leaves under 1 GB of headroom on the 7.5 GB tier and
each generation allocates ~300 MB that is not released. The tier can serve Phi-3 for short
interactive use — the main study's perf cells did exactly that — but cannot sustain a
164-problem batch at 4,096 context. This is reportable beside the existing capacity verdicts.

## 4. The mechanism: identity and equivalence are largely decoupled

Output-identity against the Mac decays monotonically with quantisation on every tier, while
aggregate pass@1 does not:

| | F16 | Q8_0 | Q4_K_M | Q3_K_M | Q2_K |
|---|---:|---:|---:|---:|---:|
| Qwen, Jetson | 1.000 | 0.927 | 0.841 | 0.884 | 0.689 |
| Qwen, Pi 5 | 0.976 | 0.945 | 0.720 | 0.817 | 0.585 |
| Phi-3, Pi 5 | — | 0.896 | 0.634 | 0.524 | 0.201 |

The sharpest case is Phi-3 at Q2_K on the Pi: **only 20% of solutions are textually identical
to the Mac's, yet pass@1 differs by 2.4 pp with balanced flips.** Backend arithmetic changes
*which* solutions are produced far more than it changes *how many* are correct, because the
flips run both ways and largely cancel. The Pi diverges further than the Jetson at every
quantised rung, consistent with CPU arithmetic departing from Metal more than CUDA does.

This is why the strong form fails while the weak form mostly holds, and it is the substantive
justification for measuring the quality axis once: aggregate pass@1 is portable across tiers
in a way that individual generations are not — until the collapse rung, where the cancellation
stops being reliable.

## 5. What changes in the dissertation

- §4.2: the † tier-uncertain flags at F16, Q8_0, Q4_K_M and Q3_K_M are removed for Qwen on
  both edge tiers and replaced by measured agreement; Q2_K carries a per-tier re-statement.
- Table D.5: extended from the two K = 50 checks to the full 24-cell matrix.
- The Jetson Phi-3 capacity result joins the deployment map's existing capacity findings.
- No registered verdict in Table 4.1 is rewritten (the addendum is validation, not
  confirmation).

## 6. Caveats

One run per cell (greedy, so the run is the cell); the two-point band and p ≥ 0.05 rule are
the registered criteria and are applied mechanically, including where a failure is 0.4 pp
outside the band; no multiplicity adjustment across the 14 device-vs-Mac comparisons, which
would only make failures harder to declare; the Jetson Phi-3 row is absent, not null, so
Phi-3's tier transfer is evidenced on one edge tier only.


## Status (2026-10-28)
Complete and scored; NOT yet in the report (document h submitted for the formative on 2026-10-26 without it). To be written in as part of the single post-feedback rewrite (document i); the section-by-section plan is in `irp/HANDOFF.md`.

## Status (2026-11-09)
WRITTEN IN to document i (`assessment/Formative_Assignment/final/COM00151M_Formative_SummativeLength_Amilka-Moses_2026-11-09i.docx`): Section 3.3.1 (the third registered check and its rule), Section 4.2 (full results, identity decay, Jetson Phi-3 unmeasured), Section 4.4 (Phi-3 Q8_0 Jetson verdict conditioned to short interactive use), Section 5.3 (reliability), Table 4.1 (Qwen † flags removed; Phi-3 † now means 'replicated on the Pi 5 only'), Table D.5 (nine replication rows) and Appendix A (registered design and the OOM deviation). Glossary row for the † flag updated.
