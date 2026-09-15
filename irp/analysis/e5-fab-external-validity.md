# FAB external validity — measured (stage-V, 2026-09-15)

**Registration:** `e5-validity-stage.md` (dated override of the stage-4 clause; paper-package
work; dissertation HOLD boundary unchanged). The measured companion to `e5-fab-validity.md`
§10: the four measurable components of the external-validity limit, each with pre-registered
predictions. Constants: b9951, n=120/cell, temp 0 seed 0 unless stated.

## V-A — generator robustness (four generations, seed blocks 1000/3000/4000/5000)

| | v1 | v2 | v3 | v4 | mean ± range |
|---|---:|---:|---:|---:|---|
| 7B F16 anchors A / B | 0.000/0.992 | 0.000/0.992 | 0.000/1.000 | 0.000/0.983 | necessity + sufficiency invariant |
| 1.5B F16 B | 0.983 | 0.892 | 0.950 | 0.908 | 0.933 ± 0.046 |
| 1.5B naive Q2 B | 0.592 | 0.492 | 0.550 | 0.467 | — |
| **collapse depth (pp)** | −39.1 | −40.0 | −40.0 | −44.1 | **−40.8 ± 2.5** |
| 1.5B naive Q2 O | 0.408 | 0.383 | 0.492 | 0.450 | B > O in **4/4** |
| 1.5B imat Q2 B | 0.933 | 0.833 | 0.950 | 0.900 | — |
| **rescue size (pp)** | +34.1 | +34.1 | +40.0 | +43.3 | **+37.9 ± 4.6** |
| 1.5B imat Q2 O | 0.967 | 0.992 | 1.000 | 0.950 | O ≥ B restored in 4/4 |

Absolute F16 levels vary by generation (±5 pp — per-seed difficulty is real); the collapse
depth and rescue size are tight. The paper's variability statement writes itself.

## V-B — documentation-format realism (Sphinx/reST rewrite of v1; semantics + example values verbatim)

| cell | terse (v1) | Sphinx | read |
|---|---:|---:|---|
| 7B F16 B | 0.992 | 1.000 | sufficiency under realistic format ✓ |
| 1.5B F16 B | 0.983 | 1.000 | format realism costs nothing at full precision |
| 1.5B naive Q2 B | 0.592 | 0.667 | collapse persists (−33.3 pp); richer pages help a little |
| 1.5B naive Q2 O | 0.408 | **0.767** | **the B>O inversion is ABOLISHED** (O > B restored) |
| 1.5B imat Q2 B / O | 0.933 / 0.967 | 0.933 / 0.992 | rescue size format-independent |

**Registered prediction (pattern format-invariant) confirmed — with a mechanism refinement:**
a single *rich, structured* page (directive header, field lists, doctest example) does not
trigger the one-page fixation that a single terse page does. The R1b mechanism is prompt
bulk/structure, not page count per se; the deployment corollary tightens to "never ship a
TERSE single-page context to a collapse-rung model". Realistic docs make the collapse-rung
regime kinder without touching the collapse or the rescue.

## V-C — name realism (fab_r1: plausible English API names, invented semantics; A = measured baseline)

| cell | syllabic (v1) | realistic (r1) |
|---|---:|---:|
| 7B F16 A | 0.000 | **0.000** |
| 1.5B F16 A | 0.000 | **0.000** |
| 1.5B Q2 A | 0.000 | **0.000** |
| 7B F16 B | 0.992 | 0.983 |
| 1.5B F16 B | 0.983 | 0.942 |
| 1.5B naive Q2 B | 0.592 | 0.692 (depth −25.0) |
| 1.5B imat Q2 B | 0.933 | 0.900 (rescue +20.8) |

**The strongest stage-V result: necessity does NOT depend on name obscurity.** With realistic
names (`coreforge.compute_digest` style) and invented semantics, closed-book remains exactly
0.000 at every cell measured — guessing requires the exact module.function pair and the
jargon prompts give no route to it. §9's necessity-realism trade-off largely dissolves: FAB
can sit at the Zan-style realism midpoint at zero necessity cost. The collapse persists with
realistic names (shallower, −25 pp — familiar name-shapes are easier for a degraded model to
emit than gibberish), and the rescue persists (+20.8 pp).

## V-D — decoding robustness (v1, temperature 0.2, 3 samples/task, seeds 0–2)

| cell | greedy | temp 0.2 ×3 |
|---|---:|---:|
| 1.5B F16 B | 0.983 | 0.917 |
| 1.5B naive Q2 B | 0.592 | **0.592** |
| 1.5B imat Q2 B | 0.933 | 0.925 |

The collapse and the rescue are not greedy-decoding artefacts; sampling shaves a few points at
F16 and changes nothing at Q2 (collapse identical to three decimals).

## Verdict

All four registered predictions held; two were exceeded (r1's perfect necessity; Sphinx's
inversion abolition). **The headline claims — collapse at the cliff, calibration rescue — are
now shown invariant to generator seed (4 generations), documentation format, name realism,
and decoding regime.** Remaining external-validity gap, recorded for the paper's future work:
real post-cutoff libraries (necessity unverifiable by construction — the reason FAB exists)
and repository-scale context.

## Caveats
- Realism variants measured on the headline cells only (not full ladders/conditions).
- Sphinx and r1 effects at Q2 (+7.5 / +10.0 pp on B) are single-generation, descriptive.
- V-D used k=3 at one temperature; not a full sampling study.
