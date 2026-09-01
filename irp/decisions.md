# IRP Decision Register — choices, rationale, and justification

**Purpose:** one place recording every substantive methodological/engineering decision, *why* it was
made, and the strength of its justification. **Feeds the IRP methods chapter + the reproducibility
claim.** Each decision is tagged:
- **[LIT]** literature-/protocol-grounded (strongest — cites a source or the pre-registered protocol)
- **[RESULTS]** data-driven (grounded in observed pilot/measurement results)
- **[PRAGMATIC]** engineering/resource constraint (weakest — state it honestly as such)

Sources referenced: `proposal-dev/pilot-protocol.md`, `proposal-dev/candidate-topic.md`
(Week-N feed-throughs + Design-decision log), `proposal-dev/pilot/RESULTS.md`, the two near-twin
papers (`week-02/reading-extracts/{shi-2025,nguyen-2025}…`), and this project log.

---

## 1. Task, metric, models

**D1 — Primary task = code generation (HumanEval+).** **[RESULTS]+[LIT]**
The Mac pilot cleared the pre-committed GO bar (F16 pass@1 ≥ 40% + a visible collapse) — so coding is
*measurably* viable, not just chosen (RESULTS.md §3/§6). It's also the most *sensitive* task to
quantization damage and the least-gameable (execution-based), per the pilot protocol's task rationale
(pilot-protocol.md §2).

**D2 — Metric = HumanEval+ pass@1 (plus), execution-based.** **[RESULTS]+[LIT]**
The pilot showed that at Q2 the code still *parses* (parse_rate ≈1.0) while being wrong — so a
parse-rate or perplexity proxy would miss the collapse; only execution-based pass@1 catches it
(RESULTS.md §5, HumanEval/9 example). HumanEval+ chosen over vanilla for ~80× more tests → catches
subtly-wrong code (pilot-protocol.md §2).

**D3 — Models = Qwen2.5-Coder-1.5B + Phi-3-mini-3.8B (dropped TinyLlama, Qwen-0.5B).** **[LIT]**
Need code-capable models with headroom above the 40% floor, else a floor effect kills construct
validity (candidate-topic Design-decision log, pt 2). Confirmed by results: both cleared ~0.68–0.70
F16 base.

## 2. Two-axes measurement design

**D4 — Quality measured ONCE (Mac, hardware-independent); performance measured PER device.** **[LIT]**
pass@1 with greedy+seed-0 is deterministic and hardware-independent, so it is measured once; latency,
throughput and memory are hardware-dependent and measured per tier (candidate-topic Week-4 feed-through
(3); Williams's design≠method licenses realising a causal question through software instrumentation).
Confirmed empirically: determinism variance = 0.000 (RESULTS.md §2).

**D5 — Keep all three tiers: Pi (CPU), Jetson (edge-GPU), Mac (consumer-GPU/Metal).** **[LIT]**
The strong contrast is **CPU-only vs accelerated**, which separates the quantization effect from the
hardware-acceleration effect; Jetson-vs-Mac alone is the *weak* comparison (both accelerated,
unified-memory). (candidate-topic Design-decision log, pt 4.) The near-twins motivate it: Shi & Ding
(2025) cover only datacentre GPUs (A100/H100); Nguyen & Nguyen (2025) only CPU-only SBCs — neither
spans the CPU→consumer-GPU→edge-GPU tiers, which is the gap this study fills.

## 3. Quantization recipe

**D6 — Self-quantise a naive ladder (F16→Q8_0→Q4_K_M→Q3_K_M→Q2_K), NO imatrix, identical across
models + devices.** **[LIT]+[RESULTS]**
imatrix (importance-matrix) calibration deliberately props up low-bit quality — using pre-made
(imatrix) quants would **mask the very collapse being measured**. Naive `llama-quantize` keeps the
collapse honest and the curves comparable. Five rungs span lossless-ish → deployment sweet-spot →
aggressive, enough to see a curve (pilot-protocol.md §2). The collapse duly appeared (RESULTS.md §4).

**D7 — One full-precision source per model → self-quantise the rest.** **[PRAGMATIC]+[LIT]**
Qwen F16 downloaded (bartowski); Phi-3 has no F16 on bartowski, so its F16 was **converted from the
`microsoft/Phi-3-mini-4k-instruct` source** via `convert_hf_to_gguf.py`, then quantised with the same
build — keeping the recipe identical so the two curves stay comparable.

**D8 — Pin llama.cpp b9951 (commit 082b326) on ALL devices.** **[LIT]**
Identical inference stack = a fair cross-device comparison (hold the software constant, vary only the
hardware — the Week-4 internal-validity/confound-control point). Metal (Mac), CUDA sm_87 (Jetson),
CPU/ARM (Pi) builds of the *same* tag.

## 4. Performance-axis protocol (`run_pilot.py --perf`)

**D9 — N = 10 prompts (first 10 HumanEval+, deterministic).** **[LIT]**
Pre-registered "small fixed prompt set (~5–10 prompts … NOT the full HumanEval suite)"
(candidate-topic Design-decision log, pt 3). Valid because subsetting only adds noise to a *pass-rate*
estimate (pilot-protocol.md §2) — the perf axis measures throughput/memory, and each generation emits
hundreds of tokens, so tok/s is stable from a handful of prompts. (Quality, which needed the full 164,
is already done.)

**D10 — K = 3 repeats; report mean ± std AND median.** **[LIT]**
Pre-registered "rerun 2–3× … for reliability" (pilot-protocol.md §3 step 6, §7); reliability =
repeatability → report mean ± spread (Week-4 feed-through; Abdulai & Owusu-Ansah 2014, "conclusions
can be verified by … others"). Repeats matter *here specifically* because latency/memory are
stochastic (thermal, DVFS, scheduling) — unlike the deterministic pass@1, which needed none.

**D11 — Warm-up discard (1 generation per cell) + median TTFT.** **[RESULTS]+[LIT]**
Observed: TTFT std > mean (e.g. 38.1 ± 54.7 ms) — a cold first-token after model load inflating the
spread (project-log 2026-08-30 review). Pre-registered latency is *warm* latency, so the harness now
discards one warm-up generation and also records the median (robust to outliers). (`run_pilot.py`
c49f3a2.)

**D12 — No evalplus scoring in perf mode.** **[LIT]**
Quality is hardware-independent (measured once on the Mac, D4); re-scoring per device is redundant and
infeasible on the Pi's CPU (hours). Perf mode records latency/memory/power only.

**D13 — Software power capture on ALL THREE tiers: Jetson (`VDD_IN`), Pi 5 (PMIC rail-sum), Mac
(`powermetrics`).** **[PRAGMATIC]+[LIT]** _(REVISED 2026-08-31 — see D23; the original "the Pi has no
software power sensor / Mac deferred" was **wrong/superseded**.)_
Completes the **performance–energy–quality triad** (adopted from Shi & Ding 2025; power also measured
by Nguyen & Nguyen 2025). The Jetson exposes whole-board `VDD_IN`; the **Pi 5 exposes per-rail V/I via
`vcgencmd pmic_read_adc`** (Σ V×I = power downstream of the PMIC — D23); the **Mac exposes SoC-domain
power via `powermetrics`** (CPU+GPU+ANE; captured 2026-08-31 via a scoped NOPASSWD sudoers rule for
`/usr/bin/powermetrics` so the harness can sample it without an interactive prompt). All three swept with
J/token derived. **Boundary caveat:** the three routes measure at different points (board-input vs
PMIC-rail-sum vs SoC-domains), so *absolute* cross-tier watts/J-per-token are **not** directly comparable
— the *within-tier* trend along the quant ladder is, and a fair *absolute* cross-tier comparison would
need one common external meter (the only remaining energy future-work). What changed vs the original D13:
the Pi and Mac energy stories are now **real data**, not future work.

**D14 — Measurement machine must be otherwise-idle.** **[LIT]+[RESULTS]**
"Control background load" is a named internal-validity confound (Week-4). The Pi/Jetson are dedicated
headless devices → naturally quiescent (a strength). The Mac (a general-use laptop) must be quiesced;
the first Mac perf run was **invalidated because the Mac was in use** and re-run idle. Caveat: even
"idle", the Mac carries desktop/IDE overhead the headless edge devices don't — noted as a limitation.

**D15 — Peak memory = RAM without swap; verified swap-free on both edge devices (0 B).** **[LIT]**
Pre-registered "peak memory within RAM **without swap**" (pi5 zram / Jetson swap watch-items). Both
confirmed swap-free post-reboot, so swap cannot mask memory overflow. Re-verify at measurement time.

**D21 — Mac peak memory validated via `/usr/bin/time -l`; the perf RSSSampler figures stand.** **[RESULTS]**
Ran a post-load `/usr/bin/time -l` peak-RSS pass per Mac cell (B1, 2026-08-31). It showed the perf-run
`peak_rss` is **not** under-counted (post-load footprints are monotonic and slightly *below* the perf RSS,
which also captures generation-time KV growth). The feared mmap/Metal under-count was a **cold-2-problem-smoke
artifact only**. Correction to the earlier assumption. Residual caveat: Mac uses different memory accounting
than Pi/Jetson, so cross-tier memory is compared Pi-vs-Jetson. (Method note: a generation-based version hung —
dropped the gen; and Mac measurements must run `caffeinate` + lid-open, per D14, after a fold silently slept a run.)

**D22 — Phi-3 Q2_K memory/TTFT anomaly is a generation-time effect; mechanism left open.** **[RESULTS]**
B1+B2 (2026-08-31): Q2_K's static footprint is smallest+monotonic; the anomaly appears only during generation.
A single-prompt probe did **not** confirm the "degenerate rambling" hypothesis (Q2 output was *shorter* than Q3),
so it's intermittent/prompt-dependent — **not overclaimed**; flagged for per-prompt instrumentation as future work.

**D23 — Pi 5 power instrumented in software via the PMIC (`vcgencmd pmic_read_adc`); corrects D13.**
**[RESULTS]**
Verified live 2026-08-31: the Pi 5's PMIC reports per-rail current and voltage for every rail; summing
V×I over the rails that report both (excluding monitor-only rails EXT5V/BATT) gives board power
**downstream of the PMIC** — idle ≈ 2.4 W, under Qwen-Q4 CPU load ≈ 6.9 W. The harness `PowerSampler`
now auto-selects a backend — Jetson `tegrastats`/VDD_IN (streamed), Pi 5 PMIC rail-sum (polled), Mac
none — so `mean_power_w` and the derived **J/token** are captured on both edge tiers. This **corrects
D13's earlier false claim** that the Pi had no software power route (it does; the claim was made without
checking). Energy-per-token is derived in analysis as `mean_power_w ÷ median_tok_s`; the CSV schema is
unchanged (the `device` column disambiguates the measurement boundary). Comparability caveat as in D13:
absolute cross-tier J/token is not apples-to-apples (different boundaries), but the per-tier quant-ladder
shape is valid — and it flips the raw-watts reading of the GPU Q3 dip (fewest watts, but *worst* J/token).

**D24 — Performance/energy axis reported descriptively (median + mean±std), NO inferential tests.**
**[RESULTS]+[LIT]**
Unlike the quality axis (paired Cochran's Q + McNemar — `collapse-threshold.md`), the performance and
energy axes are reported with **medians and mean±std, without significance testing — deliberately.**
Justification: the measured spread is negligible against the effects. `std_tok_s` = **0.0–0.4 tok/s**
across cells, while cross-rung and cross-tier differences are **tens** of tok/s (Qwen Mac F16 78 → Q4 165;
tiers 165/40/11 at Q4) — effect sizes ~100× the standard deviation, so a significance test would be
theatre (it would "confirm" what is already visually unambiguous). **K=3 repeats (D10) exist precisely to
quantify that spread**, and the spread being tiny *is* the reliability evidence. This contrasts with the
quality axis, where the real uncertainty is the 164-problem *sample* → paired tests were warranted there
and not here. Where a statistic *is* noise-dominated (cold-start TTFT, std > mean) the **median** is used
for exactly that reason (D11). The **J/token** figures inherit this: derived from median tok/s × mean
power, reported as point values with the ladder *shape* (not absolute cross-tier levels) as the claim.

## 5. Hardware / infrastructure

**D16 — Boot both edge devices from NVMe.** **[PRAGMATIC]**
~5× faster model loading (25 GB of GGUFs re-read across sweeps) + reliability for long unattended
runs. **Methodologically neutral** — storage touches no dependent variable.

**D17 — Headless, key-only SSH, static IPs via router DHCP reservation.** **[LIT]+[PRAGMATIC]**
Headless = no desktop RAM/CPU inside the measurement (protects the peak-memory DV — the reason for the
OS-Lite/console decisions). Key-only SSH + fixed addressing = reproducible, secure LAN setup.

**D18 — Clone llama.cpp FULL (never `--depth 1`) on every device.** **[RESULTS]**
The shallow clone broke the server's embedded web-UI build (`llama-ui-embed: missing loading.html`);
the full clone fixed it. `--target llama-server` did NOT sidestep it (the server embeds the UI).

**D19 — Jetson stays on JetPack 7.2.1 (6.2 fallback kept but unused).** **[RESULTS]**
The boot hang at "Exiting boot services" was a **missed 30-s capsule `Y`** (user error on an unattended
install), not a version/hardware incompatibility — proven by a successful attended re-run.

## 6. Ethics / integrity (from the proposal)

**D20 — Automated metrics only; no human-rated strand.** **[LIT]**
Keeps the study approval-free (no human data) *and* keeps reliability = repeatability (adding raters
would require inter-coder reliability + ethics approval). (Week-5 feed-through.)

---

_Update this register whenever a decision is made or reversed — with the reason and, where possible,
a literature or results citation rather than a bare assertion._
