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
_Dated here as they occur._
