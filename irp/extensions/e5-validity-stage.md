# E5 stage-V — measuring FAB's external validity (REGISTERED 2026-09-15, before any run)

**Override, dated:** stage-4's hard clause ("no stage-5") bound the *include-or-hold decision
inputs*; that decision is MADE (HOLD, 845c81e) and the branch is now the paper package. The
student's directive of 2026-09-15 ("FAB fully validity to do") activates the validity
follow-on that `e5-fab-validity.md` §10 names as the instrument's largest limit — converting
"argued, not measured" into measured, FOR THE PAPER, not the dissertation. Same override
pattern as the E4 activation (explicit, dated, recorded before the affected runs). The
dissertation's HOLD boundary is unchanged; main is untouched.

**Scope rule:** stage-V measures the external-validity components that are measurable with the
existing laboratory. The literal real-library arm (hand-built tasks on a post-cutoff library)
is **explicitly OUT** — its necessity bound is unverifiable by construction (the exact problem
FAB solves) and it is paper-revision-scale work; recorded as the paper's own future work.

Constants: b9951, n=120/cell, paired exact McNemar within-instrument, artefacts frozen +
committed BEFORE scored runs. Headline cells throughout = 1.5B {F16 B; Q2 naive B,O;
Q2 imat B,O} — the collapse and the rescue, the claims that carry the paper.

## V-A — generator robustness (limit: "two generations of one family")
Build **v3 (seed 4000)** and **v4 (seed 5000)** with the fixed builder; V1–V3 must pass.
Cells per generation: stock-7B F16 {A, B} anchors + the five headline cells.
**Registered readout:** cross-generation table (v1–v4): G1/G2 anchors; collapse depth
(F16 B − naive Q2 B); rescue size (imat − naive Q2 B); B≥O direction at naive Q2. Report
mean ± range over four generations — the paper's variability statement.

## V-B — documentation-format realism (limit: terse synthetic doc pages)
`fab_docs_sphinx.py` rewrites v1's doc pages in realistic Sphinx/reST style (py:function
directive, prose description, :param:/:returns: fields, doctest-style example) —
**semantics and worked-example values unchanged, deterministic, v1 files untouched**
(parallel `families_sphinx.json`, `_sphinx` result suffix). Cells: 7B F16 B (sufficiency under
realistic format) + the five headline cells.
**Registered prediction:** the pattern (near-ceiling F16, Q2 collapse, imat rescue) is
format-invariant; absolute levels may shift a few pp (longer, boilerplate-heavy pages).

## V-C — name realism / the necessity dial (limit: syllabic names; §9's Zan-style midpoint)
Build **fab_r1 (seed 6000, `--realistic-names`)**: same invented parameterised semantics, but
plausible English API names (`streamkit.compute_digest` style, template-matched pools). Name
guessability becomes a MEASURED quantity: condition A is expected NONZERO (a correct-name
guess executes against the hidden impl and passes) and serves as the prior-knowledge baseline;
**the primary metric for this arm is Δ(B − A)**. Cells: 7B F16 {A, B}; 1.5B {F16 A, F16 B,
Q2 naive A, Q2 naive B, Q2 imat B}.
**Registered readout:** A_r1 − A_v1 quantifies how much of FAB's necessity comes from name
obscurity vs semantic obscurity; the collapse/rescue pattern should persist in Δ(B − A).

## V-D — decoding robustness (limit: "one seed, temperature 0 only")
v1, temperature 0.2, 3 samples/task (seeds 0,1,2), pass@1 = mean per-task pass rate. Cells:
1.5B {F16 B; Q2 naive B; Q2 imat B}.
**Registered prediction:** same ordering and rough magnitudes as greedy (F16 ≈ high ≫ naive
Q2, imat ≈ F16 band); the collapse and rescue are not greedy-decoding artefacts.

## Reporting
One file: `irp/analysis/e5-fab-external-validity.md` — the measured companion to
`e5-fab-validity.md` §10, updating §10's first bullet from "argued, not measured" to measured
components (generator, format, names, decoding) + the recorded out-of-scope real-library item.

## OUTCOME (same day): all four predictions held, two exceeded — full report in
`irp/analysis/e5-fab-external-validity.md`; `e5-fab-validity.md` §10 updated from "argued"
to measured. Stage-V closed; the branch's remaining external-validity gap (real libraries,
repo-scale context) is recorded as the paper's future work.

## Deviations
_(none — one build fix pre-freeze: realistic-name pools require module-scoped fn-name
uniqueness, recorded in the fab_build comments and the freeze commit.)_
