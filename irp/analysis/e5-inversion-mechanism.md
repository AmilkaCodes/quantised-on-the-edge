# E5 stage-4 R1 — the B>O inversion mechanism: a second-page effect (2026-09-15)

**Registration:** `irp/extensions/e5-stage4-completion.md` R1 (analysis-only; no inference).
Script: `e5/e5_inversion_analysis.py` over the committed G3/stage-3 per-task rows, with
condition contexts reconstructed deterministically (same logic as `fab_run.py`, verified
against the frozen v1 artefacts). Naive 1.5B unless stated. Exploratory, descriptive, one seed.

## 1. Context size vs pass, per rung: a regime shift at the cliff

| rung | O (405 ch) | R (574) | O_dense (569) | B (1255) | B_dense (1794) | Spearman rho(size, pass) |
|---|---:|---:|---:|---:|---:|---:|
| F16 | 0.958 | 0.958 | — | 0.983 | 0.983 | +0.89 (ceiling; range 2.5pp) |
| Q3_K_M | 0.958 | 0.883 | 0.975 | 0.875 | 0.892 | **−0.60** |
| Q2_K | 0.408 | 0.592 | 0.442 | 0.592 | 0.650 | **+0.97** |

At Q3 more context HURTS (the comprehension regime: distractors cost, filtering is failing).
At Q2 the relationship flips to near-perfectly positive. But size is NOT the driver: R (574
chars) matches B (1255) exactly at 0.592, while O_dense (569 chars, nearly identical size to
R) sits at 0.442. What R and B share is not volume; it is **having more than one page**.

## 2. The decomposition that cracks it: the inversion is a SINGLE-CALL phenomenon

Q2_K cells, pass@1 split by task type:

| condition | pages (singles) | singles | chains |
|---|---|---:|---:|
| O | 1 | **0.314** | 0.540 |
| O_dense | 1 (3 examples) | **0.300** | 0.640 |
| R | 2 | **0.657** | 0.500 |
| B | 4–5 | **0.657** | 0.500 |
| B_dense | 4–5 | 0.700 | 0.580 |

- **Chains show NO inversion** (O ≥ B: 0.540 vs 0.500); chain tasks receive two true pages
  under O. The whole B>O effect lives in single-call tasks.
- **Singles with exactly one page: ~0.31. Singles with a second page of ANY kind: ~0.657** —
  identical for R (whose second page is a lexically-similar distractor) and B (three
  family distractors). Content, relevance and count-beyond-two are all irrelevant; the jump
  is one page → two pages.
- **Example density does nothing for singles** (O 0.314 → O_dense 0.300) while helping
  chains-under-O (0.540 → 0.640), which retro-explains the lever-2 null: density was aimed
  at the wrong margin.

## 3. What the failures look like (error taxonomy + mimicry, Q2)

- O's Q2 failures are dominated by **wrong-value assertions (39)** and **syntax degeneration
  (15)**; B's by attribute errors (20, cross-page API confusion) with fewer assertions (16).
- The token-overlap mimicry metric is FLAT across rungs (B pass overlap 0.654 at F16 → 0.647
  at Q2): the strong copying hypothesis is not supported at token level.
- Per-task contingency at Q2: B-only 42 (30 single / 12 chain) vs O-only 20 (6 / 14) —
  the mirror of §2.

## 4. Refined hypothesis (recorded; one registered test)

**The one-page fixation hypothesis:** at the collapse rung, a prompt containing a SINGLE
documentation page puts the degraded model into a mode where it reproduces the page's worked
example rather than solving the task (consistent with the wrong-value assertion signature);
a second page, regardless of content, breaks the fixation. If true, "distractors help" was
never about redundancy or examples: it is prompt-structure, and the practical guidance for
collapse-rung open-book prompting is "never present exactly one reference page".

**R1b (registered amendment):** the clean test is condition **P (padded oracle)** = true
page(s) + exactly one same-family distractor, Q2_K naive 1.5B, n=120. Prediction: singles
recover from 0.314 to ≈0.65 (R/B level); chains unchanged. One cell; runner support committed
(`fab_run.py` cond `P`).

## Caveats
- One seed, one benchmark generation, descriptive throughout; the rho values are over 3–5
  condition points and carry no inferential weight.
- Size, page count and example count covary by design; the P cell is what separates
  page-count from everything else for singles. Dense cells already separate example density.
- Mimicry is measured as token-set overlap; a structural copy (same shape, different values)
  would evade it — the assertion-error signature is indirect evidence, not proof.
- Chain tasks under O receive two pages by construction, so "chains are immune" and "two
  pages suffice" are confounded with task difficulty; P on chains gives a partial handle.

## R1b — the padded-oracle test (RUN 2026-09-15; registered prediction CONFIRMED)

Condition P (true page + exactly ONE content-irrelevant same-family distractor), naive 1.5B:

| rung | O (1 page) | P (2 pages) | B (5 pages) | prediction |
|---|---:|---:|---:|---|
| Q2_K | 0.408 (singles 0.314) | **0.650 (singles 0.671)** | 0.592 | singles → ≈0.65 ✓ (registered) |
| Q3_K_M | 0.958 (singles 0.986) | 0.908 (singles 0.957) | 0.875 | P ≈ O for singles ✓; extra page costs a little, as the Q3 regime predicts |

**The one-page-fixation hypothesis survives its registered test.** At the collapse rung a
single-call task with exactly one doc page fails 2× more often than the same task with one
IRRELEVANT page added (0.314 → 0.671, content-free rescue); at Q3 the effect is absent and the
extra page reverts to a small cost. The Q2 inversion is therefore not about distractors helping
— it is about the one-page prompt shape specifically breaking the collapsed model on
single-call tasks. Deployment corollary (Q2 only): pad retrieval to ≥2 pages; never ship a
single-page context to a naively-quantised collapse-rung model. (Calibration remains the real
fix — imat Q2 O 0.967 needs no padding.)
