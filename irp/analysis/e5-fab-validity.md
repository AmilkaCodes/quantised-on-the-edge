# FAB — the full instrument-validity case (2026-09-15, branch `extended-work`)

_The complete validity argument for the False-API Benchmark as a measurement instrument for
necessary-context exploitation. This is the paper's instrument section in long form and the
single reference the five findings' claims rest on. Sources: `e5-false-api-raft.md`
(registration + gates), `e5-decision-log.md` (design rationale), `fab-manifest.json` /
`fab_v2-manifest.json` (shas), `e5-fab-g3.md`, `e5-fab-phi.md`, `e5-fab-v2-replication.md`._

## 1. Construct

FAB operationalises **necessary-context exploitation**: the capability to read reference
documentation supplied in-prompt and produce executably correct code that could not have been
produced without it. The construct is deliberately distinct from (a) retrieval quality (the
R condition isolates it), (b) distractor filtering (the B-vs-O contrast isolates it), and
(c) general code competence (measured separately on HumanEval+). A model may call the
documented function or legitimately reimplement its semantics from the doc page; both count,
because both require extracting the semantics from the documentation, which is the construct.

## 2. Docs-necessity — by construction, then verified empirically (G1)

Function and module names are syllable-generated with no real-world collisions; semantics are
invented and parameterised (arbitrary weight tuples, rotation counts, moduli, separators),
so no pretraining corpus can supply either the name or the behaviour. Task prompts use
invented jargon ("the zoru envelope") that maps to functions only via the docs, and function
names never appear in task prompts (build gate V2). Closed-book success is therefore
impossible by design rather than assumed. Empirically: **condition A = 0.000 for all three
models at every rung tested, on both benchmark generations** (stock 7B F16 anchors: v1 0.000,
v2 0.000; G1 threshold ≤ 0.10 passed with no margin needed). The one nonzero A cell ever
observed (0.008, a post-training arm) was traced to learned name-prior guessing and verified
not to be leakage.

## 3. Docs-sufficiency (G2)

An instrument that only proves necessity could be measuring difficulty, not
context-exploitation. Doc pages therefore teach the semantics fully (formula plus one worked
example), and sufficiency is verified on a stock reference model before any intervention:
7B F16 open-book B = 0.992 (v1 and v2 identically), oracle O = 1.000, against the registered
G2 threshold ≥ 0.60. The instrument spans its full dynamic range (0.000 closed to ≈1.0 open
at the reference rung), so both improvements and collapses are measurable without ceiling or
floor artefacts at full precision.

## 4. Contamination — impossible by construction, swept anyway

The invented-name design makes benchmark leakage into pretraining impossible in the forward
direction and meaningless in the reverse. Two build gates enforce the internal equivalents:
V2 (name disjointness across families; names absent from all prompts) and V3 (no doc page
shares a 13-gram with any reference solution beyond the API signature itself, the same
conservative n-gram discipline the main study applies). The RAFT train pool used a disjoint
seed block with automated name-disjointness verification against the eval set, at the
function-name level (sharper than n-grams for code).

## 5. Scoring validity

Tests execute against a hidden reference implementation written to disk as a real importable
module; generated solutions run in a subprocess with a timeout, pass defined as exit 0. Build
gate V1 requires every reference solution to pass its own tests under the hidden
implementation before the benchmark is frozen. One instrument-fairness fix is on record: the
task text tells the model to assume the module import works, so the harness guarantees the
import rather than failing models on a technicality (fix the harness, never the score;
applied before gates, pre-registered rebuild allowance for instrument artefacts only).

## 6. Determinism and provenance

Generation is fully deterministic from a seed block; frozen artefacts are committed with
sha-256 manifests (v1 tasks e6568060…, v2 tasks 679f476d…); scoring runs greedy, temperature
0, seed 0, on the pinned llama.cpp build (b9951) on one machine. Honest deviation, dated in
the stage-4 registration: generalising the builder surfaced two latent v1 defects (doc-page
worked examples depended on a salted hash, so a rebuild reproduces v1 *tasks* byte-identically
but not its doc pages; and cross-family function-name collisions were unchecked, now retried
deterministically). v1 was left untouched and frozen (its committed artefacts remain the
instrument of record); the fixes apply to v2 onward. Frozen-artefact-plus-sha, not
rebuild-equality, is the reproducibility contract, and it held.

## 7. Internal validity of the condition contrasts

All conditions score the identical 120 tasks (70 single-call, 50 two-call chains), enabling
exact paired McNemar tests. Distractor selection for B (and the single pad page for P) is
seeded per task id, so every run of a condition presents byte-identical prompts. Conditions
differ only in the documentation block prepended to an otherwise identical prompt. One
registered interpretive constraint follows from the stage-4 mechanism analysis: page count,
total context size and example count covary across the condition set by design, so B-vs-O
contrasts are comparisons of *defined context packages*, not of a single isolated variable;
the P condition exists precisely to isolate page count where it mattered.

## 8. Replication across generations

A second generation (v2, fresh seed block, same parameters) reproduced: identical validity
anchors (A 0.000, B 0.992), near-ceiling F16 exploitation, the ~40 pp naive-Q2 collapse, the
~34 pp calibration rescue with full oracle restoration, B ≥ O at naive Q2, and the
single-call fine structure almost exactly. Two honest bounds: the naive-Q2 B>O inversion
replicates in direction but not significance at n = 120 (its stronger evidence is the R1b
mechanism test); and per-generation difficulty varies for weaker models (1.5B F16 B 0.983 v1
vs 0.892 v2), so cross-generation comparisons are within-cell patterns, never pooled scores.

## 9. Position among precedent instruments

Three designs occupy a necessity-realism trade-off. Held-out real functions (DocPrompting's
CoNaLa split) maximise realism but bound necessity weakly (pretraining may know the
function). Renamed real libraries (Zan et al.'s MonkeyEval/BeatNumEval) strengthen necessity
but preserve real semantics behind the renaming, leaving semantic priors partially available.
FAB's invented names AND invented semantics make necessity strongest and realism lowest.
The choice is deliberate: for a quantisation-ladder study the construct must be airtight at
every rung, and realism is the recorded external-validity cost, not a hidden one.

## 10. Threats and limits (carried on every claim)

- **External validity — MEASURED (stage-V, 2026-09-15; `e5-fab-external-validity.md`):** the
  headline pattern (collapse at the cliff, calibration rescue) is invariant to generator seed
  (4 generations: depth −40.8 ± 2.5 pp, rescue +37.9 ± 4.6 pp), documentation format
  (Sphinx/reST: pattern intact, and the terse-page fixation abolished — mechanism refinement),
  name realism (realistic API names: closed-book stays exactly 0.000 everywhere — necessity
  does not depend on name obscurity), and decoding regime (temp 0.2×3: Q2 collapse identical).
  The remaining unmeasured gap is real post-cutoff libraries and repository-scale context,
  recorded as the paper's future work (necessity there is unverifiable by construction — the
  reason FAB exists).
- **Statistical:** n = 120 per cell, one seed, temperature 0 only; effects below roughly 8 pp
  are not reliably detectable; multiple comparisons uncorrected (headline effects survive any
  correction; fine-structure effects are labelled descriptive).
- **Format sensitivity:** the one-page effect shows collapse-rung scores are sensitive to
  prompt structure, not only to information content; condition definitions are therefore part
  of the construct and are frozen with the instrument.
- **Cross-model comparisons** ride on each model's own chat template; they are read
  qualitatively (onset locations, orderings), with inferential pairing only within model.

## 11. What this case licenses, and what it does not

It licenses claims about small models' exploitation of necessary, in-prompt, short-form API
documentation on execution-scored micro-tasks, per rung and per condition, on this instrument
family, replicated across two generations. It does not license claims about real-library
documentation, long or repository-scale contexts, retrieval systems beyond frozen BM25, or
task families outside the template set. The five findings in `e5-consolidated-summary.md`
are worded within these bounds.
