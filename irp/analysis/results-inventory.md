# Master results inventory — claim → evidence → display → data (created 2026-09-14)

_The examiner-proofing ledger: every claim the write-up makes, traced to its analysis home, its
display asset, and its primary data artefacts. Provenance rule: each results CSV/JSON was
committed alongside the device `manifest.json` of its run — the **commit** is the provenance
record (engine llama.cpp b9951, greedy seed 0, HumanEval+ 164/EvalPlus throughout; conditions and
artefact hashes in the paired manifest). Paths relative to repo root. Display assets marked
**TO-BUILD** are the figure debt (extend `irp/analysis/make_figs.py`; current figs dated
2026-09-01 predate E1 onward)._

## Confirmatory core (pre-registered; RQ1–RQ3)

| # | Claim (headline) | Analysis home | Display | Primary data (commit) |
|---|---|---|---|---|
| C1 | RQ1/1a: collapse thresholds — Qwen safe through Q3, Q2 −22.6pp (p=1.2×10⁻⁷); Phi breaks at Q4 (−9.7pp, p=.007); 5pp margin rule | `collapse-threshold.md` | `figures/fig1_collapse.png` (current) | Authoritative source = per-problem `samples_*-sanitized_eval_results.json` (Mac-side; **deliberately untracked** per `.gitignore` — CSVs+manifest are the committed record); run CSVs `results/mac/pilot_results_202607*.csv` (ae0991e) carry the aggregates |
| C2 | RQ2/2a: latency/memory/energy per tier; Q3 GPU energy trap; feasibility map | `../proposal-dev/pilot/RESULTS.md` §9 | figs 2–5 (current) | `results/{mac,pi5,jetson}/perf_results_20260830-31*.csv`, `mac_peakmem_timeL_20260831.csv` (09165b4, 267ce49, 2f7f72c) |
| C3 | RQ3: deployment envelope + registered SLO gate (Qwen@Q4 clears all tiers incl. Pi, closed-book) | `synthesis.md` | `figures/fig3_tradeoff.png` (current) | derived from C1+C2 artefacts |
| C4 | D25: outputs do NOT match across tiers (3/8 differ, correctness flips on HumanEval/5) → Mac quality axis = aggregate proxy | `cross-device-check.md` | table in text (no fig needed) | `results/*/xdev_*.json` (see file dates; open-book variant K=25, 4/25 diverge — `e1-openbook.md` caveats) |

## E1 / E1-R (registered exploratory: context + agentic)

| # | Claim | Analysis home | Display | Primary data (commit) |
|---|---|---|---|---|
| C5 | RQ1b: frozen doc-context NEVER helps; harm peaks at each model's collapse rung (Qwen Q2 −9.8pp p=.007; Phi Q4 −15.2pp p=.0008) | `e1-openbook.md` | **TO-BUILD: per-rung Δ(B−A) chart, both models** | `results/mac/pilot_results_open_20260912_144604.csv` (ae44cb2); prompts artefact `e1/openbook_prompts.jsonl` sha 95069f4b… |
| C6 | E1 perf tie-in: context cost = prefill+KV = tier property; Pi open-book TTFT 4,957ms breaks the 1–2s floor | `e1-openbook.md` (perf section) | **TO-BUILD: TTFT/RSS closed-vs-open per tier** | `results/{mac,pi5,jetson}/perf_results*_2026091{2,4}*.csv` (f5cca4a, dca0582) |
| C7 | RQ1c: tool use broken AT F16 (M1 0/20, closed-book 0.90 same problems) — breaks before generation | `e1-agentic.md` | table (small) | `results/mac/agentic_qwen2.5-coder-1.5b-instruct_F16/` summary+transcripts |
| C8 | R1: grammar deletes the syntax failure (M1′ 20/20); query quality ≈0.99 to Q3, breaks at Q2 (0.86, degen 5→26); own-chosen context still ≈B, < A at Q4/Q3/Q2 | `e1r-agentic.md` | **TO-BUILD: fold into C5 chart (add R1 series) + M1′ ladder inset** | `results/mac/r1_*/{summary.json,stage1.jsonl}` (3135cf1); grammar `e1/search_call.gbnf` |
| C9 | R2: oracle O ≤ A everywhere, significant exactly at collapse rungs; O ≈ B → selection is not the lever; "cannot exploit even ideal context" | `e1r-oracle.md` | **TO-BUILD: add O series to C5 chart** | `results/mac/pilot_results_oracle_20260913_200950.csv` (8e2ad75); oracle artefact sha 875fe30d…, sweep report `e1/e1r-oracle-sweep-report.md` |

## E2 family (registered exploratory: scale, calibration, deployment)

| # | Claim | Analysis home | Display | Primary data (commit) |
|---|---|---|---|---|
| C10 | E2a-5: 7B does NOT collapse (threshold None); memory-matched 7B@Q2 2.9GB 0.793 beats 1.5B@F16 3.1GB 0.610 (+18pp) | `e2a-results.md` | **TO-BUILD: 7B ladder + memory-matched bar pair** | `results/mac/pilot_results_20260913_121309.csv` (9665cc8) |
| C11 | E2a-5 open: context harm survives scale — 7B hurt at every rung incl. F16 (all p≤.019); open ladder degrades faster than closed | `e2a-results.md` | **TO-BUILD: add 7B to C5-style chart** | `results/mac/pilot_results_open_20260913_131210.csv` (849bf84) |
| C12 | E2a-4: invocation = policy dial (4B nudge 0.00 → mandate 0.40 → force 0.80, M3=1.0; 1.5B zero at every setting, degenerates forced 20/20); reasoning receipts | `e2a-results.md` | **TO-BUILD: dose-response bars** | `results/mac/agentic_qwen3-4b_F16*/`, `agentic_...instruct_F16_{policy,forced,json}_cap2048/` (9665cc8 + follow-up) |
| C13 | E2b: calibration moves Phi's threshold TWO rungs (Q4→Q2) + halves Qwen's Q2 cliff; **context harm follows the cliff, not bit-width** | `e2b-imatrix.md` | **TO-BUILD: calibrated-vs-naive paired ladder; harm co-movement panel** | `results/mac/pilot_results_20260914_005313.csv`, `pilot_results_open_20260914_01{2715,3127}.csv` (fb466b2); calibration sha 200e109b… |
| C14 | E2c: Jetson serves 7B@Q2 at 11.1 tok/s (deploys); Pi fails floor at every rung (max 3.4); Pi uniquely FITS F16 (0.8, batch-only); Q3 dip = GPU-kernel only | `e2a-results.md` (E2c section) | **TO-BUILD: three-tier deployment/SLO map** | `results/jetson/perf_results_20260914_092435.csv`, `results/pi5/perf_results_20260914_092659.csv`, `results/mac/perf_results_20260914_091846.csv` (caba164, 5217e2c, dca0582) |

## E4-α (registered exploratory: fine-tune probe)

| # | Claim | Analysis home | Display | Primary data (commit) |
|---|---|---|---|---|
| C15 | E4-α: FC-LoRA yields spontaneous well-formed calls BUT tools-in-context mode collapse ("only-that": 16/20 hallucinate the task fn as tool; no-tools control codes fine) — gate FAIL, reportable; completes can't/won't/only-that | `e4-alpha.md` | table + 1 transcript excerpt box | `results/mac/agentic_qwen2.5-coder-1.5b-e4_F16*/` (caba164); training data + sweeps per `e4-finetuned-toolcalling-spec.md` stage-0 |

## Cross-cutting display assets (the two thesis-level figures)

- **TO-BUILD (signature figure): collapse-rung signature alignment** — five phenomena on one
  rung axis per model: quality drop, imposed-context harm, J/token, R1 query degeneration,
  calibrated-harm co-movement. Sources: C1, C5, C2, C8, C13.
- **TO-BUILD: six-claim spine graphic** for the discussion chapter (from
  `implications-synthesis.md`) — optional, only if it earns its space.

## Open items (small, honest)

1. ~~Per-problem data archival~~ → **CLOSED 2026-09-14 (`7a421d1`):** per-problem
   `*_eval_results.json` snapshots now TRACKED under `proposal-dev/pilot/eval-results/`
   (56 files, 5.7MB; coverage verified complete — closed/open/oracle/R1 ladders both models,
   all imatrix cells incl. both registered open cells, full 7B ladders, 3× xdev). Source of
   truth remains `results/<device>/` per its README (stale-cache caution noted there). Every
   paired statistic is now independently checkable from the repo. Residual to-do at
   submission time only: include this folder in the dissertation's Artefact Directory zip.
2. ~~7B energy scope~~ → **CLOSED 2026-09-14 (`053e680`):** power WAS measured on all three
   tiers and verified engaged against run logs. **Binding scope caveat (now in `e2a-results.md`
   E2c caveats):** per-tier boundaries differ (Mac = SoC package only; Pi = PMIC-downstream
   rail-sum; Jetson = whole-board DC input) → **J/token is within-tier comparable ONLY**, gross
   not marginal (no idle subtraction). Cross-tier absolute J/token flatters the Mac, penalises
   the Jetson. Any cross-tier energy sentence in the write-up carries this statement or is
   dropped — and `fig5_energy` (plus any successor) must say "within-tier comparison" in its
   caption.
3. Figure build session (extend `make_figs.py` — all source CSVs are in-repo, so this machine
   works; no Mac dependency) — after formative lit-review + methodology drafts exist, except
   the two early figures if a results sample goes to the supervisor.
