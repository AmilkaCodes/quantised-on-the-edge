# E2a results — Arm 4 (agentic 2×3 grid) + Arm 5 (7B scale ladder)

**Runs:** 2026-09-13, Mac, per `../extensions/e2a-protocol.md` (activation + deviations dated there).
Artefacts: Qwen3-4B bf16 sha `52486602…`; Qwen2.5-Coder-7B-Instruct f16 sha `d8e374f1…`; 7B naive
ladder Q8_0/Q4_K_M/Q3_K_M/Q2_K sha-logged at quantise time. Probe cells at gen-cap 2048 / n_ctx 8192
(probe-local, registered); 7B sweeps at the study caps (768/4096). **Status: Arm 4 complete;
Arm 5 closed-book complete; Arm 5 open-book sweep running; micro-probes (reasoning capture,
policy-prompt) pending.**

## Arm 4 — the agentic grid (K=20, F16 anchors, M1 = valid first-turn call)

| model | native (nudge) | prompted-JSON (IFFC-style) | forced (`tool_choice` on turn 0) |
|---|---|---|---|
| **Qwen2.5-Coder-1.5B** (not tool-trained) | 0.00 | 0.00 | **0.00 — M2: degeneration 20/20** |
| **Qwen3-4B** (tool-trained) | 0.00 | 0.00 | **0.80** — M3 = 1.0 · overall 0.80 |

(The original 768-cap E1 gate — 1.5B native, M1 0/20 — is the registered E1 result; the native cells
here are the matched-parameter probe reruns. Overall pass: 1.5B 0.90, 4B 0.80, both ≈ their
closed-book competence in every cell.)

**Findings.**
1. **Voluntary invocation is zero everywhere.** No model, no framing, produced a single unforced tool
   call in 120 episodes. The prompted-JSON reframe (Taheri's IFFC) did not change *invocation* —
   their result concerns format accuracy *when calls are required by the query*, not willingness to
   call when the task is self-contained. On HumanEval-style prompts, both models simply answer — and
   Condition B independently shows that judgement is *correct* (docs don't help).
2. **Capability decomposes exactly as the two-layer hypothesis predicted (e1-implications):** forced,
   the tool-trained 4B executes the protocol at **80% valid calls with every completed tool-phase
   episode passing (M3 = 1.0)** — while the non-tool-trained 1.5B **degenerates in 20/20 episodes**
   under the same coercion (the repetition pathology, systematic). Coercion reveals capability in the
   trained model and produces pathology in the untrained one. *Can't (1.5B) vs won't-by-policy (4B),
   now with numbers.*
3. **Mechanical caveat:** the 4B's 4 non-valid forced episodes produced *empty* output (no call, no
   answer, all 4 failed) — consistent with the hidden reasoning trace exhausting the 2048 cap; the
   harness did not capture `reasoning_content` (patch queued; reasoning-capture probe will verify).
   M1-forced is therefore reported as 0.80 with this mechanism flagged, not interpreted as format
   failure.
4. **Deployment reading:** tool use at the edge is an *engineered* behaviour — scaffold-forced or
   trained-in, never volunteered. Under the deployment-realistic condition (scaffold forces the
   call), the tool-capable 4B works flawlessly and tool-mediated docs did not degrade it
   (overall 0.80 forced = 0.80 native). The quantisation-ladder version of this question remains
   unrun (RQ1c's original gate logic: it was gated on F16 reliability, which only the 4B passes,
   and only under forcing — a registered follow-up decision, not an automatic escalation).

## Arm 5 — Qwen2.5-Coder-7B closed-book ladder (pass@1 plus, n=164)

| rung | pass@1 | drop vs F16 (95% CI) | McNemar p |
|---|---:|---|---:|
| F16 | 0.841 | — | — |
| Q8_0 | 0.848 | −0.006 [−0.018, +0.000] | 1.000 |
| Q4_K_M | 0.854 | −0.012 [−0.037, +0.012] | 0.625 |
| Q3_K_M | 0.835 | +0.006 [−0.024, +0.037] | 1.000 |
| Q2_K | 0.793 | **+0.049 [+0.000, +0.104]** | 0.115 |

**⭐ H-A5a answered: the 7B does not collapse anywhere on the ladder.** 5pp-margin threshold =
**None** (Q2_K's +4.9 pp sits inside the margin; n.s.). The quantisation collapse is a
**small-model phenomenon**: the 1.5B lost 22.6 pp at Q2 (p = 1.2×10⁻⁷); the same naive recipe at 7B
loses 4.9 pp n.s.
**⭐ The memory-matched comparison is the deployment bombshell:** the 7B at Q2_K is a **2.9 GB**
artefact scoring **0.793** — versus the 1.5B at F16 (**3.1 GB**) scoring **0.610**. At *matched
memory*, an aggressively quantised larger model beats a full-precision smaller one by **+18 pp**.
(Decode-speed and edge-tier costs for the 7B are pending the perf cells; the quality-per-byte
ordering is already unambiguous.)

## Arm 5 — 7B open-book vs closed-book (H-A5b; pass@1 plus, n=164)

| rung | closed A | open B | Δ(B−A) (95% CI) | McNemar p | broke/rescued |
|---|---:|---:|---|---:|---:|
| F16 | 0.841 | 0.780 | −0.061 [−0.104, −0.018] | **0.013** | 12/2 |
| Q8_0 | 0.848 | 0.768 | −0.079 [−0.128, −0.037] | **0.001** | 14/1 |
| Q4_K_M | 0.854 | 0.768 | −0.085 [−0.134, −0.037] | **0.001** | 16/2 |
| Q3_K_M | 0.835 | 0.768 | −0.067 [−0.122, −0.018] | **0.019** | 15/4 |
| Q2_K | 0.793 | 0.701 | **−0.091** [−0.152, −0.037] | **0.004** | 20/5 |

**⭐ H-A5b answered with the stronger branch: the context harm does NOT shrink with scale.** The 7B is
significantly hurt by injected doc-context at **every** rung, F16 included — despite having no
quantisation collapse at all. The dissociation is the finding:
- **Scale rescues quantisation-robustness** (closed ladder flat: F16→Q2 −4.9 pp n.s.) …
- **… but not context-robustness** (open harm −6 to −9 pp everywhere, all significant; worst at Q2).
- **The open-book ladder degrades faster than the closed one** (open F16→Q2 −7.9 pp vs closed
  −4.9 pp): quantisation damages context-use *before* it damages generation, even at 7B — the
  sharpest H1c-flavoured evidence in the study, consistent with Liu et al.'s full-precision context
  fragility at frontier scale.

## Arm 4 follow-up — the invocation spectrum + the reasoning evidence (2026-09-13)

**Policy cells (system-role MANDATE, K=20):** 4B M1 = **0.40** (M3 = 1.0 again; overall 0.80);
1.5B M1 = **0.00** (mandate cannot create absent capability). The 4B's invocation rate is therefore a
clean **dose-response in instruction strength**:

> **nudge 0.00 → mandate 0.40 → force 0.80** — and at every level where a tool phase completes,
> M3 = 1.0 and overall pass is unchanged (0.80). Invocation is a *policy dial*, not a capability
> cliff, for the tool-trained model; for the untrained model every setting of the dial reads zero.

**Reasoning probe (K=5, native, `reasoning_content` captured):** in **4 of 5** episodes the tool
never enters the model's deliberation at all — thousands of characters of problem-solving reasoning
with no mention of `search_docs`. In the fifth (HumanEval/4) the model **explicitly weighs the
instruction and dismisses it**:
> "the user mentioned that I should first call search_docs … But in this case, the function is
> straightforward, and the code is simple."
Direct first-person evidence of invocation-policy override: relevance judgement beats instruction —
and per Condition B, that judgement is *empirically correct* on this task. (Also explains the 4
empty forced episodes: hidden reasoning traces consuming the cap.)

## Caveats
- Probe cells K=20 (K=5 for the reasoning probe), descriptive, multiple comparisons uncorrected.
- Closed-7B Q2 drop CI touches +0.104 (honest uncertainty); bf16-anchor deviation for the 4B.
- The 7B open-book harm is 5 tests, all p ≤ .019 — Q8/Q4/Q2 survive Bonferroni (α = .01).
- 7B Mac perf cells (tok/s/TTFT/RSS/power per rung) remain optional/unrun.
