# E5 / extended-work — decision log (what was decided, and why)

_Dated record of every material decision on the `extended-work` branch, with rationale. House
pattern: register-before-run; deviations dated; negative results reportable. Companion to
`e5-false-api-raft.md` (registration + gate outcomes) and the analyses in `irp/analysis/`._

## Governance

1. **Branch isolation (2026-09-14, student directive).** All extended work lives on
   `extended-work`; `main` is reserved for the student's dissertation write-up. *Why:* the
   write-up lien (drafts on track by 2026-09-28) governs the dissertation; the branch lets the
   experimental programme advance without touching the submission line. Nothing merges without
   student review.
2. **E5 registered before any build (same day).** Protocol committed with validity gates,
   stage criteria, and timeboxes before a line of generator code ran. *Why:* the programme's
   pre-registration discipline is the evidential basis for every claim; extended work inherits
   it wholesale.
3. **Stage-2 criteria and hyperparameters pre-registered before the data build.** Gate
   thresholds (B ≥ stock band, A = 0, HumanEval within noise, control no-gain) and training
   knobs (iters 600, batch 4, 16 layers, seed 0) fixed in the registration first. *Why:* a
   gate you can move after seeing results is not a gate (E4-α lesson formalised).
4. **Gate FAIL accepted as a result; no retry.** Stage 2 closed same day it failed. *Why:* the
   registration says a genuine FAIL is a result, not a retry ticket; the two-iteration
   discipline exists to stop tuning-until-it-passes. The one rebuild allowance is for
   instrument artefacts only, and the failure was verified not to be one.

## Instrument design (FAB)

5. **False API with invented names and invented parameterised semantics — not a real library.**
   *Why:* docs-necessity and contamination-proofing hold **by construction**: nothing in
   pretraining can supply a syllabic name (`baxkev_cv`) or an arbitrary weight tuple, so
   closed-book failure is guaranteed to mean "docs needed", and no public-benchmark sweep is
   even required. A real-library benchmark can never bound what pretraining already knows.
6. **Deterministic template generation — no LLM synthesis.** *Why:* reproducibility to the
   byte from a seed; zero scraped/personal data; the frontier-API TRAP path (provider ToS)
   stays closed; the ethics position stays all-No with nothing new to disclose.
7. **Task prompts use invented jargon ("the zoru envelope") that maps to functions only via
   the docs; function names never appear in prompts (build-gate V2).** *Why:* the only route
   from prompt to passing tests must run through the documentation — that is the construct.
8. **Docs teach semantics fully (formula + one worked example).** *Why:* G2 (docs-sufficiency)
   must be reachable; a model may legitimately reimplement instead of call — both are
   context-exploitation, which is the thing measured.
9. **Validity gates G1/G2 measured on a stock model BEFORE any training.** *Why:* E1's core
   limitation was an instrument that could not detect the effect of interest; FAB had to prove
   it could (G1 0.000 / G2 0.992) before any intervention claim could be built on it.
10. **G3 (stock ladders) run before RAFT.** *Why:* the training-free measurement — where
    necessary-context exploitation dies on the ladder — is novel on its own and justifies the
    branch even if every training arm fails (it did; G3 stands).
11. **Harness supplies the module import (fixed pre-gate after smoke).** *Why:* the task text
    says "assume `import <mod>` works"; models that took this literally were failing on a
    technicality. Instrument-fairness discipline: fix the harness, never the score.
12. **F16 for validity gates despite Q4 being 3× faster.** *Why:* instrument validation must be
    unimpeachable; rung effects are the object of study, so the validator must sit at the
    reference rung.

## Stage 2 (RAFT) design

13. **Two arms, identical tasks and solutions, docs-in-prompt the only variable.** *Why:* the
    E4 spec's recorded objection to RAFT was that gains could be "more coding practice near the
    distribution"; the control arm is the separator. (It worked — too well: it exposed that
    BOTH arms learned the same thing.)
14. **Train pool from a disjoint seed block with a hard name-disjointness gate.** *Why:*
    train/test hygiene at the level that matters for invented APIs (names, not n-grams). The
    gate caught a real collision on first build (function names, not modules) and was widened —
    the gate earned its keep.
15. **Distractor-count cycling {3,0,1} in training; example-density deliberately NOT varied
    (dated deviation).** *Why:* one knob per experiment; a null on distractor-robustness must
    not be misread as covering the G3 finding-4 example-density hypothesis.
16. **E4-α lessons baked in: native ChatDataset, `--mask-prompt`, examples end with code.**
    *Why:* run-1's double-templating artefact and the call-and-stop attractor were both
    format-level traps already paid for once.
17. **Mechanism verified before accepting the FAIL:** arm outputs diffed (120/120 identical),
    adapter/gguf checksums compared, leakage grep run (name absent from training data),
    differential probe executed. *Why:* E4 run-1 taught that a gate FAIL can be an instrument
    artefact; a FAIL is only a result once the artefact explanations are eliminated.
18. **A = 0.008 recorded as name-prior guessing, not leakage.** *Why:* verified — the guessed
    name exists nowhere in training data; tuned models learned the generator's syllable
    distribution. Instrument note for any future trained-model evaluation on condition A:
    widen the name space.
19. **RAFT retest requires harder train tasks and a new registration (not run).** *Why:* the
    stage-2 mechanism showed the hypothesis was unfalsifiable at this difficulty — the base
    model already solved train tasks with docs, so no context-exploitation gradient existed.
    Rerunning the same design with different knobs would measure nothing.

## Current step (registered in the addendum below the registration's closure)

20. **Proceed with the two non-training levers** — (a) imatrix-calibrated quants on FAB,
    (b) example-dense docs at the collapse rungs. *Why:* stage-2 showed training subtracts at
    this scale; both remaining levers leave the model untouched, both have existing evidence
    behind them (E2b's cliff-moving; G3 finding-4's inversion), and both are cheap
    (existing artefacts / docs-format change only). Frozen eval artefacts stay untouched —
    the dense-docs variant is a parallel docs file, clearly suffixed, never overwriting FAB v1.
