# E5/R4 — FAB v2 replication: every headline reproduces on a fresh generation (2026-09-15)

**Registration:** `e5-stage4-completion.md` R4. fab_v2 = seed block 3000, same params, V1–V3
pass, frozen+committed before any scored run (tasks sha 679f476d…). Success criterion
(registered): direction + rough magnitude reproduce; G1/G2 thresholds for the anchors.

## Validity anchors (stock 7B F16)

| cell | v1 | v2 | gate |
|---|---:|---:|---|
| A closed | 0.000 | 0.000 | G1 PASS |
| B open | 0.992 | 0.992 | G2 PASS (identical) |

## Replication cells (1.5B)

| cell | v1 | v2 | verdict |
|---|---:|---:|---|
| F16 B | 0.983 | 0.892 | near-ceiling ✓ (v2 drew harder semantics for the 1.5B; 7B unaffected) |
| F16 O | 0.958 | 0.967 | ✓ |
| naive Q2 B | 0.592 | 0.492 | large collapse ✓ (−39.1 vs −40.0 pp from F16) |
| naive Q2 O | 0.408 | 0.383 | ✓ — and singles 0.314 → 0.271, chains 0.54 → 0.54: **the single-call fixation reproduces almost exactly** |
| imat Q2 B | 0.933 | 0.833 | large rescue ✓ (+34.1 vs +34.2 pp; 47/6, p = 5.8×10⁻⁹) |
| imat Q2 O | 0.967 | 0.992 | full rescue ✓, inversion gone ✓ |

**Verdict: REPLICATED.** All registered pattern elements reproduce — near-ceiling F16
exploitation, ~40 pp naive-Q2 collapse, ~34 pp imat rescue with full oracle restoration, B ≥ O
at naive Q2, and the single/chain fine structure. One honest nuance: the naive-Q2 B>O
*inversion* reproduces in direction (0.492 > 0.383) but not significance at this n
(36/23, p = .12; v1 was p = .007) — report the inversion as replicated-in-direction, with the
R1b padded-oracle mechanism test as its stronger evidence.

## Caveats
- Two generations, one seed each; both from the same generator family (template diversity, not
  generator diversity).
- v2's 1.5B F16 shift (0.983 → 0.892) shows per-generation difficulty varies for weaker
  models; cross-generation comparisons should be within-cell patterns, never raw pooling.
- Build-determinism deviations recorded in the stage-4 registration (salted-hash doc examples
  in v1; name-collision enforcement added for v2).
