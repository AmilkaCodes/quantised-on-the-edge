# E5/G3 — FAB quantisation ladders: necessary-context exploitation vs the cliff (2026-09-14)

**Registration:** `irp/extensions/e5-false-api-raft.md` (branch `extended-work`). Instrument:
FAB v1 frozen (tasks sha e6568060…, 120 tasks/cell). Runner: `e5/fab_run.py` (temp 0, seed 0,
llama.cpp b9951 Metal). Conditions: A closed · B open (+3 distractors) · R BM25 k=2 · O oracle.
G1/G2 validity gates passed before these ladders ran (7B F16: A 0.000, B 0.992 — recorded in the
registration doc).

## The ladders (pass@1, n=120 per cell)

**Qwen2.5-Coder-7B-Instruct (naive ladder):**

| rung | A | B | R | O |
|---|---:|---:|---:|---:|
| F16 | 0.000 | 0.992 | 0.958 | 1.000 |
| Q8_0 | 0.000 | 0.992 | 0.958 | 1.000 |
| Q4_K_M | 0.000 | 0.992 | 0.958 | 1.000 |
| Q3_K_M | 0.000 | 1.000 | 0.967 | 1.000 |
| Q2_K | 0.000 | 0.958 | 0.958 | **1.000** |

**Qwen2.5-Coder-1.5B-Instruct (naive ladder):**

| rung | A | B | R | O |
|---|---:|---:|---:|---:|
| F16 | 0.000 | 0.983 | 0.958 | 0.958 |
| Q8_0 | 0.000 | 0.983 | 0.958 | 0.958 |
| Q4_K_M | 0.000 | 0.967 | 0.900 | 0.925 |
| Q3_K_M | 0.000 | 0.875 | 0.883 | 0.958 |
| Q2_K | 0.000 | **0.592** | 0.592 | **0.408** |

Paired McNemar (exact, two-sided), 1.5B F16→Q2: **B broke 47 / rescued 0 (p = 1.4×10⁻¹⁴)** ·
R 44/0 (p = 1.1×10⁻¹³) · O 68/2 (p = 4.2×10⁻¹⁸). 7B F16→Q2 B: 4/0, p = .125 (n.s.).

## Findings

1. **⭐ The dissertation's E1 negative is now bounded, not overturned — and the bound is sharp.**
   At full precision the 1.5B exploits *necessary* context nearly perfectly (B 0.983, one point
   under the 7B). E1's "context never helps" was task structure (self-contained problems), not
   a capability deficit. FAB is the instrument E1 said it lacked, and it says so with a 0.000→0.983
   closed→open swing.
2. **⭐ Necessary-context exploitation collapses at the SAME rung as generation — and falls
   HARDER.** The 1.5B's HumanEval closed-book collapse at Q2 was −22.6 pp; its FAB open-book
   collapse is **−39.1 pp** (0.983→0.592, 47 broke/0 rescued). Quantisation's residual damage
   destroys context-benefit faster than it destroys generation. This is the positive-control
   twin of the E2b "harm follows the cliff" claim: **benefit follows the cliff too** — context-use
   is the first casualty of the cliff in both directions (imposed-harm when unnecessary,
   lost-benefit when necessary).
3. **⭐ Scale immunises exploitation as it immunised generation.** The 7B ladder is flat to Q2's
   −3.4 pp (n.s.); oracle stays 1.000 at every rung. The quantisation-collapse story is a
   small-model story on both instruments.
4. **The degradation has fine structure — what dies first is distractor filtering, then
   docs-following inverts.** At Q3 the 1.5B holds oracle at 0.958 while distractor-laden B falls
   to 0.875: filtering degrades before following. At Q2 the order INVERTS: O 0.408 < B 0.592
   (McNemar p = .007 — real, not noise; O's Q3→Q2 fall is 69 broke/3 rescued, p = 2.6×10⁻¹⁷).
   **Recorded hypothesis (testable in the per-task rows):** each doc page carries a worked
   example; B's five pages supply five in-context examples where O supplies one or two. At the
   collapse rung the model's instruction-following is largely gone and it leans on
   pattern-copying from examples — so *more* pages help even when most are distractors. If it
   holds, the mechanism of collapse-rung context processing is example-mimicry, not
   comprehension — a strong claim for the follow-on paper, not asserted here.
5. **Retrieval is a solved sub-problem when docs are necessary and lexically matched.** R tracks
   B within noise at every rung of both models (identical 0.592 at the 1.5B's Q2). BM25 over an
   80-page corpus is not the bottleneck; the model's context processing is. (Designed contrast
   with E1, where retrieval had nothing useful to fetch.)

## Implications for stage 2 (RAFT)

The stage-2 premise is now measured rather than assumed: there IS a large, real capability
(0.983 at F16) that quantisation destroys (0.592 at Q2) — so "can RAFT-style training make the
capability survive the ladder?" has headroom on both sides, unlike the HumanEval setting where
the best possible RAFT outcome was a null. Per the registration, stage 2 waits until the student
has seen this G3 read. Design note carried forward: the finding-4 inversion suggests RAFT
training data should vary distractor count and example density, and the no-docs control arm
remains mandatory.

## Caveats
- One seed, temp 0, single benchmark generation (seed-1000 block); FAB semantics are synthetic
  micro-APIs — external validity to real library docs is argued, not measured.
- Multiple comparisons uncorrected (headline p-values survive any correction).
- The B>O inversion at Q2 is significant but its mechanism (example-density hypothesis) is
  untested; the per-task rows and transcripts are committed for that analysis.
- 7B Q2 dip (−3.4 pp) is descriptive only (p = .125).
