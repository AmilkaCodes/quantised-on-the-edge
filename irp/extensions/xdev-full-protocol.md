# Registered validation addendum: full-ladder cross-device replication of the quality axis (xdev-full)

**Registered:** 2026-10-24, by this commit, before any measurement. **Class:** registered validation (like the Q3_K_M
cross-device addendum), not a confirmatory analysis; no registered verdict or threshold changes as a result of it.

## Question
The confirmatory quality ladder (Table 4.1) was measured once, on the Mac, under the registered two-axes split (§3.3.1).
Two registered checks validated the transfer premise at Qwen Q4_K_M (three tiers, K = 50) and Qwen Q3_K_M (Mac against
Jetson, K = 50): the strong form (identical outputs) failed, the weak form (aggregate pass@1 within about one problem)
held. Neither collapse rung and no Phi-3 cell was checked. Does the weak form hold at every verdict-bearing rung on the
devices a deployer would use?

## Cells and instrument
- HumanEval+, all 164 problems, closed-book, greedy decoding, seed 0, the registered 768-token cap, the pinned llama.cpp
  build b9951 on each tier, the same GGUF bytes (SHA-256 agreement recorded in `proposal-dev/pilot/CHECKSUMS.md`).
- Generation on each tier by `cross_device_check.py` with K = 164 and the output tag `full164`, so the registered K = 50
  files are untouched. Scoring on the Mac only, by `score_xdev_full.py` (EvalPlus 0.3.1, plus status).
- Jetson: Qwen2.5-Coder-1.5B at F16, Q8_0, Q4_K_M, Q3_K_M, Q2_K; Phi-3-mini at Q8_0, Q4_K_M, Q3_K_M, Q2_K (F16 does not fit).
- Pi 5: Qwen2.5-Coder-1.5B at all five rungs; Phi-3-mini at Q8_0 to Q2_K if time allows (its Pi verdicts are already
  decided by the throughput gate, so these cells are optional).
- Mac: both models at every rung through the same script, as the reference and as a determinism check against the
  September snapshots (within-device greedy decoding is deterministic; any difference is itself a result).

## Measures
Per device and rung: plus-status pass@1 over 164; drop from the device's own F16 where it holds F16; output-identity rate
against the Mac; pass flips against the Mac split into b (Mac pass, device fail) and c (Mac fail, device pass) with the
exact two-sided McNemar p.

## Interpretation map (committed before the run)
- **Weak form holds** at a rung if the device's pass@1 is within two points of the Mac's and the flips are not
  significant (p ≥ 0.05): the Mac-measured verdict stands for that tier and the † tier-uncertain flag at that rung is
  resolved by measurement.
- **Weak form fails** at a rung if the device's pass@1 differs from the Mac's by more than two points or the flips are
  significant: the rung's verdict is re-stated per tier in §4.2 and the deployment map (Figure 4.4) is re-judged for that
  tier using the device's own pass@1 against the registered margin. The registered Mac verdicts in Table 4.1 are not
  rewritten; the per-tier result is reported beside them.
- Either direction is a result and is reported with the same prominence (symmetric reporting rule).

## Timebox and abort
Device time only; no code change to the harness beyond the output tag. Abort a cell if the server fails to load the
file or a run exceeds four hours on the Pi 5; an aborted cell is reported as not measured.

## Deviations

**2026-10-24, Jetson Phi-3 cells — server memory exhaustion, cells void, re-run with a
device-scoped launch fix (recorded before the re-run).**
The four Jetson Phi-3 cells completed with 142 to 155 of 164 solutions EMPTY and 594
"Connection error" warnings in the log: the server stopped answering a few problems into each
cell. The cells are void as measurements and are NOT reported as results; the scored rows they
produced (pass@1 0.043 to 0.110 against the Mac's 0.220 to 0.628, b up to 95, c = 0) are an
instrument artefact, not a tier effect. Evidence that it is an artefact: every solution that
DID complete before each failure is byte-identical to the Mac's, and all five Jetson Qwen
cells completed 164/164.

Diagnosis (measured, not inferred). A memory probe on the Jetson with Phi-3 Q8_0 shows the
model loading to 6,439 MB of 7,485 MB, leaving 1,045 MB; available memory then falls
monotonically with each generation (1,024 → 757 → 420 → 161 MB) and requests begin failing at
91 MB. The server log gives the cause: `n_slots = 4, n_ctx_slot = 4096` — llama-server's
default is four slots, each allocating the full context, so the harness reserves about 16k
tokens of KV cache for a workload that issues one request at a time. Phi-3 therefore does fit
this tier; the registered launch configuration over-allocates against it. (The main study's
Jetson Phi-3 perf cells survived because they are short and reuse ten repeated prompts, which
the server's prefix cache serves from one slot.)

Fix, scope, and why it cannot change a score: `--parallel 1` is added to the server launch
**on the Jetson only**, leaving the Mac repository's harness and the in-flight Pi 5 run
untouched. Slot count governs memory allocation, not decoding: with greedy decoding, seed 0
and sequential requests, the generated tokens are identical. This is an instrument fix under
the standing rule (fix the harness, never the score), of the same class as the FAB import
fix. **Built-in control:** the problems that completed before each crash are retained as
`*_oomvoid.json`; after the re-run, those same problems must still be byte-identical, which
tests output-neutrality directly. If any differ, the fix is not output-neutral and the cells
revert to not-measured.

**Outcome of the re-run, and a correction to the diagnosis above (2026-10-24, same day).**
The `--parallel 1` re-run **failed identically** — the same four cells completed the same
9, 22, 19 and 12 problems before the server stopped answering. The slot hypothesis is
therefore **tested and falsified**, and the paragraph above is wrong about the mechanism; it
is retained rather than deleted so the reasoning trail stays honest.

What an A/B probe (`--parallel` auto against 1) actually shows:

| | slots | available after load | available after each generation |
|---|---:|---:|---|
| auto | 4 | 862 MB | 464 → 70 MB, then requests fail |
| `--parallel 1` | 1 | 894 MB | 820 → 497 → 176 MB, then requests fail |

The flag does what it claims (4 slots → 1) and buys a little headroom, but **post-load
availability is essentially unchanged (862 against 894 MB)**, so slot count was never holding
the memory: KV allocation here is unified. The real mechanism is **per-generation allocation
of roughly 300 MB that is not released**, against a post-load headroom of under 1 GB; the
Linux OOM killer then terminates the server (`Killed` in both probe arms). Phi-3-mini at
Q8_0 (4.06 GB of weights plus CUDA runtime) simply does not leave enough room on a 7.5 GB
tier to sustain a 164-problem run at the registered 4,096 context.

**Resolution: the four Jetson Phi-3 cells are reported as NOT MEASURED — CAPACITY**, per the
abort clause. No further harness bending: two attempts is enough, and the limit is a property
of the tier rather than of the instrument. The Jetson harness has been reverted to the
registered launch command (the `--parallel 1` edit was device-local and is gone); both void
runs are retained as `*_oomvoid.json` and `*_oomvoid2.json`. The Jetson's five Qwen cells are
unaffected and complete at 164/164.

This is itself reportable alongside the capacity verdicts already in the deployment map: the
8 GB tier can serve Phi-3-mini for short interactive use (the main study's perf cells did
exactly that) but cannot sustain a long batch at full context.
