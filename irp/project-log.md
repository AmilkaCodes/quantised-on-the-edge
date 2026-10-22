# IRP Project Log — COM00151M Independent Research Project (2026/7)

**Project:** Quantised on the edge — quality, latency and memory trade-offs of small local
code-generation LLMs across CPU, consumer-GPU and edge-GPU hardware.
**Carried over from:** COM00150M Research Proposal (submitted 24 Aug 2026; mark pending).
Proposal artefacts, pilot harness, procurement decisions and reading corpus live in this same
repo — see `proposal-dev/` (pilot harness: `proposal-dev/pilot/`, per-device configs already in
place: `configs/{mac,pi5,jetson}.yaml`).

**Location note (2026-08-27):** IRP work consolidated INTO the RP repo (github.com/AmilkaCodes/RP)
so there is one working directory — this folder (`irp/`). The OneDrive module-11 folder keeps a
breadcrumb stub + university admin docs only.

**Log discipline:** dated entries, what happened when, commands/versions where relevant,
mistakes included. This feeds the IRP methods chapter and the reproducibility claim.

**Decision register:** consolidated methodological/engineering decisions + justifications (tagged
literature / results / pragmatic) live in **`irp/decisions.md`** — the primary methods-chapter feed.

---

## 2026-08-24 — Raspberry Pi order placed (WP1: procurement)

Ordered on receipt of final student-loan instalment. Supplier: The Pi Hut (per
`proposal-dev/procurement.md`). Verified against the order invoice (2026-08-27):

| Item (per invoice) | Price |
|---|---:|
| Raspberry Pi 5 Starter Kit — 16GB / UK (The Pi Hut) | £349.30 |
| Raspberry Pi M.2 HAT+ (Raspberry Pi) | £11.50 |
| Layer Case for Raspberry Pi M.2 HAT+ & Active Cooler (The Pi Hut) | £6.00 |
| Active Cooler for Raspberry Pi 5 (Raspberry Pi) | £4.80 |
| Subtotal (4 items) | £371.60 |
| Shipping | £3.80 |
| **Total** | **£375.40** |

- **Starter kit bought deliberately (decision reversal, reasoned):** the original procurement plan
  rejected the kit (its case conflicts with the Active Cooler). Reversed at order time because the
  kit ships with a **pre-flashed microSD card** — closing the boot-media gap and keeping the base
  software state **consistent and nameable for anyone replicating the setup**. The kit also covers
  the **27W PSU** (why no separate PSU line). The kit case goes unused — the Layer Case + Active
  Cooler stack replaces it, as planned.
- **Price note:** £349.30 reflects 2026 RAM-price inflation on the 16GB variant — verified from
  invoice, not an ordering error. (Proposal's resources line said "~£250"; record actuals —
  £375.40 — in the IRP report. The "affordable hardware" claim survives; the number just moved.)
- Storage: reusing an owned **512GB Steam Deck NVMe (M.2 2230)** in the HAT+ — no drive purchased.
  (Spare 2280 checked and found to be SATA — unusable on either board; see procurement gotchas.)

## 2026-08-25 (approx.) — Raspberry Pi delivered

Delivered next working day. _[Exact date to confirm from courier email.]_

## 2026-08-26/27 — Physical assembly (Pi 5 stack)

Assembled as-built, bottom to top (dictated 2026-08-27):

1. **Layer Case — bottom layer** as the base
2. **Raspberry Pi 5 board** mounted on it, standoffs in between
3. **Active Cooler** fitted on the Pi 5 (spring-pin mount into the board's two mounting holes,
   thermal pads pre-fitted)
4. **Standoffs (16mm)** up to the HAT level
5. **M.2 HAT+** on top
6. **Layer Case — top layer** closing the stack

- [x] ~~To confirm: SSD fitted before closing?~~ → **confirmed 2026-08-27: 512GB Deck NVMe
      installed in the HAT+ during assembly.**
- [x] ~~Assembly photos~~ → **WAIVED 2026-09-01, reasoned:** reproducibility is carried by the
      written record (part list + stack order + officially-documented fitment), and the
      thermal-debug value lapses once the sustained-load check proves the cooler works by
      measurement. Not worth reopening a working machine. Optional: one exterior "apparatus"
      shot of the closed stack for the dissertation, if the phone's ever nearby.

## 2026-08-27 — Setup planning (pre-boot decisions)

- **Headless-only administration decided** for both boards: no displays/keyboards. Rationale is
  methodological, not just convenience — a desktop environment consumes RAM and CPU inside the
  measurement, and peak memory is a dependent variable (critical on the 8GB Jetson).
- **Pi OS decision (2026-08-27): reflash to Raspberry Pi OS Lite (64-bit)** via Raspberry Pi
  Imager, with SSH key, hostname (`pi5.local`) and user preconfigured. The kit's pre-flashed card
  boots the desktop OS — wrong environment for measurement (RAM overhead vs the peak-memory DV).
  The reflash is a **documented setup step** (versions + Imager settings recorded in
  `irp/setup/pi5/pi5.md`), preserving the replication story: base = Starter Kit card, reflashed to a
  named OS Lite image.
- Jetson: headless first-boot config over USB-C serial console (no DP adapter needed).
- Network: both boards wired into the owned **gigabit switch**; SSH from the MacBook (control
  machine). Long runs inside `tmux`. Harness cloned from git on each device; results pushed back
  per device (`results/<device>/` + provenance manifest, per pilot structure).
- Setup recorded as it happens in `irp/setup/pi5/pi5.md` and `irp/setup/jetson/jetson.md` (commands as run,
  versions, deviations).

## 2026-08-28 — Jetson USB installer prepared (WP1: setup)

JetPack **7.2.1** first-boot prep on the Orin Nano Super (method changed since planning: JetPack 7.2
dropped SD-card images → the **Jetson ISO / USB-installer** flow). As-run detail in
`irp/setup/jetson/jetson.md`:

- **Firmware gate passed:** on-device UEFI = `36.4.7-gcid-42132812` (JetPack 6.x-gen, > 36.0) → ready
  for the 7.2.1 ISO path; no 6.x update needed.
- **Installer USB made + verified:** ISO `jetsoninstaller-r39.2.1-...-arm64.iso` (self-sha256
  `f31cf35…`; NVIDIA publishes no ISO hash), balenaEtcher 2.1.6 → **GRUB boot confirmed** on the
  devkit. DisplayPort monitor obtained → install runs monitor-attached (not headless serial).
- **Install deferred to 2026-08-29:** BSP goes **straight onto the Integral 500GB NVMe** (arrives
  tomorrow) — no microSD-first + clone (JetPack writes to the chosen target, and `rpi-clone` is
  Pi-only: Jetson boots via module UEFI/QSPI).

## 2026-08-30 — Network pinned static + Mac perf-axis review

**Static IPs in place** (router reservations): **pi5 = 192.168.0.210**, **jetson (viperjet) =
192.168.0.212** — closes the "DHCP drift" caveat on both devices. **Verification (done 2026-08-31,
recorded in each device's setup log):**
- [x] pi5: still `.210` post-reboot (`hostname -I` = 192.168.0.210, uptime 19h); `ssh pi5` connects key-only ✓
- [x] jetson: still `.212` post-reboot (`hostname -I` = 192.168.0.212); `ssh viperjet`/`ssh jetson` connect key-only ✓
- [x] Both setup logs note addressing = router DHCP reservation (not device-side static config) — reproducible from the router

**Review of the Mac perf axis + device state (flags from review, 2026-08-30):**
- [x] ~~Phi-3 Q2_K anomaly — rerun before Mac perf axis final~~ → **done 2026-08-31 (B1/B2):
      localised to generation time; static footprint smallest+monotonic; "rambling" hypothesis
      not confirmed → flagged, not overclaimed (D22).**
- [x] ~~TTFT warm-up exclusion~~ → **done 2026-08-31: harness discards 1 warm-up generation per
      cell + records median TTFT (c49f3a2, D11); Mac axis re-run idle with fixed harness.**
- [x] **Q3_K_M throughput dip REPRODUCED on both models with error bars** (Qwen 146<163,
      Phi 77<85 tok/s) — independent confirmation of the "runtime effect, not a model effect"
      claim in the proposal's Figure 1 caption. PowerSampler self-disable verified (power field
      empty on Mac, as designed).
- [x] ~~Jetson SSH hardening~~ → **done 2026-08-31: key-only, password auth disabled (aae2c0f).**
- [x] ~~Provenance mapping note~~ → **done: viperjet ↔ device=jetson noted in jetson.md (f9aa4f0).**
- [x] ~~jetson.md tidy~~ → **done (f9aa4f0).**
- [x] ~~Remaining device opens~~ → **closed 2026-08-31 (336c6e1, e414344, 8c5f6ac): NVMe identity
      recorded, both devices swap-clean (0B, D15), Phi-3 staged + full Jetson perf axis run, kit
      box contents verified.** Still open: **sustained-load power/thermal + `jetson_clocks`
      decision** (robustness characterisation, not an RQ input — synthesis §7).

## 2026-08-31 — Track A analysis: stats, figures, two-axis synthesis

Completed the analysis pass on the finished two-axis dataset (quality axis §1–6 + performance axis §9,
both committed). All artefacts under `irp/analysis/`.

- [x] **A#1 — collapse-threshold statistics** (`collapse-threshold.md` + `collapse_stats.py`). Paired
      tests on per-problem HumanEval+ pass/fail (same 164 problems at each rung; greedy+seed-0 →
      deterministic): **Cochran's Q** (omnibus, both models reject H₀) + **McNemar exact** (F16 vs each
      rung, locates the threshold). Result: **model-dependent collapse** — Qwen safe through Q3
      (collapse at Q2, p=1.2×10⁻⁷), Phi breaks already at Q4 (p=0.007). RQ1 answered with significance,
      not eyeballed curves.
- [x] **B (data-completeness tidy-ups) — done first, per instruction, documented with impact.** B1 Mac
      peak-RSS validated via `/usr/bin/time -l` (earlier under-count worry was a cold-smoke artifact;
      perf numbers stand → D21). B2 Phi-3 Q2_K anomaly localised to *generation time*; "rambling"
      hypothesis **not** confirmed → D22. Both recorded in `decisions.md` + RESULTS §9.
- [x] **A#4 — figures** (`figures/fig1–4.png` + reproducible `make_figs.py`). Built to the dataviz
      procedure (validated categorical palette, one-axis, direct labels, colorblind-safe); all four
      eyeballed for collisions/geometry before commit. Collapse curves / three-tier throughput (Q3 GPU
      dip) / quality–speed trade-off / peak memory (8 GB edge line).
- [x] **A#3 — two-axis synthesis** (`synthesis.md`). Combines the axes into a **deployment envelope**
      with two named handoff triggers: **memory-forced** (Phi-3 F16 >8 GB won't fit the edge at all;
      only Q8 is both quality-safe *and* edge-fitting) and **throughput-forced** (SLO-dependent; Pi CPU
      decode misses interactive targets the Jetson/Mac meet). Headline recommendation the data supports:
      *specialise the model, quantise to the knee, size the tier to the SLO.* Maps cleanly onto RQ1–RQ3.

**Decision-register update:** all A-phase choices already covered by D1–D22 (no new decisions — analysis
applied existing methodology). Figures/synthesis are outputs, not decisions.

## 2026-08-31 (later) — Energy axis completed: Pi PMIC + Mac powermetrics (corrects a false claim)

Triggered by the question "is there no cost-per-token on the Pi/Mac?" — checking it exposed an **error in
our own record**: D13/setup logs claimed the Pi had no software power sensor. **Wrong.**
- **Pi 5 power IS software-readable** via `vcgencmd pmic_read_adc` (Σ per-rail V×I, PMIC-downstream).
  Verified live (≈2.4 W idle). Instrumented in the harness (`PowerSampler` PMIC backend, polled);
  **full Pi power sweep run** 2026-08-31 (9 cells, N=10×3). Record corrected (D13 revised, **D23** added).
- **Mac** `powermetrics` backend added (SoC domains, CPU+GPU+ANE); **sweep DONE 2026-08-31** on an idle
  Mac under `caffeinate` (lid open), enabled by a scoped NOPASSWD sudoers rule for `/usr/bin/powermetrics`.
  ⭐ Mac (Metal) **reproduces the Q3_K_M energy trap** → confirmed on a **second GPU backend** (Jetson
  CUDA + Mac Metal), absent on the Pi CPU. Energy now captured on **all three tiers** (D13 revised again).
- **J/token computed** (Jetson + Pi; RESULTS §9 table + `fig5_energy.png`). **⭐ Finding:** two-shaped
  energy curve — **Pi CPU monotone** (Qwen 1.63→0.53 J/tok, pure efficiency win), **Jetson GPU
  non-monotone** with **Q3_K_M an energy *trap*** (0.61 J/tok despite fewest watts — it's slowest). The
  raw-watts "Q3 = lowest power" reading reverses in J/token; corroborates the GPU-kernel signature from a
  third angle. Boundary caveat carried everywhere (absolute cross-tier J/token not comparable; per-tier
  shape is).

## 2026-09-01 — Pre-registration alignment review (analysis vs proposal commitments)

Review of the completed analysis against the proposal's pre-registered commitments found **four
alignment gaps** — the science is done, but it must demonstrably be the science the proposal said
it would do. Pre-registration is the methodology's selling point; a marker reading both documents
will check. **To execute ASAP:**

- [x] **A. Apply the pre-registered 5pp margin explicitly.** ✅ DONE 2026-09-01. The proposal pre-registered
      "quality-acceptable if pass@1 stays within five percentage points of the model's F16
      baseline." The analysis currently defines "quality-safe" by McNemar significance instead.
      The verdicts almost certainly agree (Qwen Q3 −3.7pp = within margin ✓; Phi Q4 ~−11pp =
      outside ✓), but the registered criterion must be applied **explicitly and reported
      alongside** the tests — otherwise it looks silently swapped post hoc.
- [x] **B. Add the bootstrap CIs.** ✅ DONE 2026-09-01. The proposal (incl. the statistical-power addition) promised
      "bootstrap 95% confidence intervals accompany each pass@1 … margin verdicts are therefore
      reported with their intervals." None exist in `irp/analysis/` yet. ~20 lines in
      `collapse_stats.py`; a written commitment.
- [x] **C. Run + document the cross-device spot-check.** ✅ DONE 2026-09-01 — **and it FALSIFIED the
      assumption** (see results block below). Synthesis asserted outputs are
      "byte-identical across tiers" citing RESULTS §2 — but §2 is Mac-only re-run determinism.
      The proposal pre-registered "a cross-device spot-check confirms outputs match." Run it for
      real (one rung, a handful of problems, diff Mac/Pi/Jetson outputs) and record it —
      ~an hour, and it converts RQ3's central premise from assumption to evidence.
- [x] **D. Gate the deployment envelope on the pre-registered SLO, not an "illustrative" one.** ✅ DONE 2026-09-01.
      Registered floors exist: **8–10 tok/s sustained + TTFT 1–2 s (Nielsen)**. Apply them as the
      primary gate (Pi/Qwen-Q4 at 11 tok/s squeaks past; Pi/Phi-Q8 at 2.8 fails; Jetson/Q3 at
      18.6 passes but is dominated) — then generalise. Completes RQ3's "good enough" map exactly
      as the proposal defined it.

**Outcomes (all four done 2026-09-01):**
- **A + B** — `collapse-threshold.md` §1 now leads with the **registered 5pp margin** (McNemar kept
  alongside); new **§3b** reports pass@1 with **bootstrap 95% CIs** + the paired-drop CI and the 5pp
  verdict (`collapse_stats.py` extended). Margin threshold **agrees with McNemar** (Qwen Q2, Phi Q4).
  As the proposal anticipated, the two **boundary rungs** (Qwen Q3, Phi Q4) have drop-CIs **straddling
  5pp → margin-inconclusive** even where McNemar rejects — reported honestly, not overclaimed.
- **C — ⚠️ FINDING: the pre-registered "outputs match across devices" is FALSE.** `cross-device-check.md`
  + `cross_device_check.py` (Qwen Q4, 8 problems, identical GGUF+b9951, only backend differs): **3/8
  outputs differ across tiers and correctness FLIPS** — HumanEval/5: Jetson passes, Mac + Pi fail
  (differently). Mechanism: temp-0 greedy argmax + backend FP-order differences → different early token →
  whole generation diverges. Within-device determinism still holds (§2). **Impact:** the collapse
  threshold (a 20–40 pp quantization effect) is robust and stays the RQ3 headline, but the Mac quality
  axis is now stated as a **validated proxy, not an exact per-tier predictor**; "byte-identical / exactly
  hardware-independent" corrected everywhere (synthesis §1/§6, collapse-threshold §5, RESULTS §9, D4, new
  **D25**). Aggregate divergence rate not yet quantified (8-problem sample) — optional K≈50 follow-up.
- **D** — synthesis §4 deployment envelope now gated on the **registered floor** (≥8–10 tok/s + TTFT
  ≤1–2 s Nielsen + RAM-without-swap), not an illustrative SLO: **Qwen-Q4 on the Pi (10.9 tok/s) squeaks
  past; Phi-Q8 on the Pi (2.6) fails → handoff**. Boundary is now *defined*, not a knob.

_Also from the same review: log hygiene (tick the completed 08-30 checkboxes + stale Pending
items — done below), and the standing note that the biggest remaining risk is supervision timing,
not tech: get the supervisor's eyes on the design-as-executed + decision register early._

## 2026-09-01 (later) — Final verification list (everything left to test/verify)

Post A–D audit sweep: what remains before the dataset is fully closed and writing starts.
Items 1–4 ≈ one bench evening; item 5 ≈ half a day.

- [x] **1. Manifest gap — FIXED 2026-09-01** (`accel_provenance()` stamps l4t_release + nvpmodel;
      verified R39.2.1 + MAXN_SUPER; 08-30/31 retro-confirmed; D26). JetPack version + power mode not stamped.** D13 +
      jetson.md Phase 4 promise "provenance manifest fields per run: JetPack version + power
      mode"; `results/jetson/manifest.json` has neither. Fix: harness stamps
      `/etc/nv_tegra_release`, `nvpmodel -q` output, and `jetson_clocks` state for all future
      runs; dated addendum note that the 08-30/31 runs were at MAXN_SUPER per the setup log
      (honest retro-annotation, not a regenerated manifest).
- [x] **2. Pi thermal — DONE 2026-09-01: peak 71.4 °C, get_throttled=0x0 before & after → no throttling**
      (pi5.md; D26). Under sustained load** (pi5.md build-out, still open — validity guard for
      the CPU latency cells). Rerun one heavy cell (Phi Q8), watch `vcgencmd measure_temp`,
      then `get_throttled` = 0x0 after the run (sticky flags reset at boot, so it must be
      checked in-session) → licenses "no thermal throttling occurred during measurement".
- [x] **3. Jetson sustained-load — DONE 2026-09-01: peak junction 65.4 °C, VDD_IN ≈18 W, no throttle/cap
      events; jetson_clocks OFF recorded** (jetson.md Ph4; D26). `tegrastats` during a long cell — throttle/power-cap
      events, DC-supply-holds-MAXN_SUPER confirmation, and the `jetson_clocks` decision
      (record whether used per run). The one open device item from synthesis §7.
- [x] **4. Edge determinism — DONE 2026-09-01: K=50 re-run byte-identical on BOTH Pi and Jetson**
      (Mac already 0.000; D25/D26 now airtight on all three). Self-diff the K=50 set on Pi and
      Jetson (Mac already has variance-0.000 evidence) → makes D25's "deterministic per
      device, divergent across devices" airtight on all three tiers.
- [x] **5. Clean-clone reproducibility rehearsal — DONE 2026-09-01 (scoped): ✅ byte-identical.**
      Fresh `git clone` of HEAD into scratch → relinked `local/` → `~/pilot-work` (venv/models/llama.cpp)
      per SETUP-NOTES → reran the K=50 Qwen-Q4 cell → output **byte-identical to the committed result**.
      Validates "published harness, every result reproducible" by acting as own-replicator; the documented
      `local/` reconciliation step is sufficient. (Scoped = reused the built toolchain via the symlinks;
      a full from-scratch toolchain rebuild remains an option pre-submission but this closes the core
      claim.) Original (capstone):** fresh clone in a new directory
      on one device → follow the setup doc top-to-bottom → rerun a single cell → confirm it
      matches the committed CSV. Tests the "published harness, every result reproducible"
      claim by acting as own replicator; any friction found = documentation debt fixed cheap.
- [ ] **6. Supervisor review of the design-as-executed** (+ decision register as the agenda) —
      the verification no script runs; timing is the project's biggest remaining risk.
- [x] ~~Assembly photos~~ → waived 2026-09-01, reasoned (see 08-26/27 entry).

**Explicitly complete, no further action:** quality axis (stats + CIs + 5pp margin), perf axis
(3 tiers), energy axis (3 tiers), cross-device divergence (K=50, two scorers), Q2_K anomaly
(localised, D22), warm-up exclusion (D11), pre-registration alignment A–D. Scoped-out future
work stays scoped out (MBPP+, per-prompt Q2_K, external power meter).

## 2026-09-01 (evening) — Supervisor brief + E1 context-conditions design note

- **Supervisor brief drafted** (`irp/supervisor-brief.md`): state of play, three headline
  findings, audit trail, four questions, prepared extensions E1–E3. To be reviewed/voiced by
  the student before the meeting; decision register proposed as the meeting agenda.
- **E1 designed and recorded** (`irp/extensions/e1-context-conditions.md`): the "open-book"
  extension the proposal itself names as natural future work. Key design musing captured:
  giving the model the *target's own solution* is the wrong main condition (pass@1 ceilings by
  construction — measures copying, not assisted coding) but valuable as an honestly-labelled
  **oracle probe** of pure context-utilisation fidelity; the realistic main condition is
  **retrieval-style few-shot** (similar problems + their solutions, never the target's), with
  the headline statistic being the **interaction** — does the context benefit survive
  quantisation? Costed (~1 Mac compute-day per condition), stats machinery unchanged, free RQ2
  tie-in (context's KV-cache memory price on the 8GB edge). Trigger: supervisor steer only;
  if activated, pre-register the E1 protocol before measuring; confirm Fast-Track ethics
  wording covers it first.

## 2026-09-07 — IRP module starts; summative marking criteria found

Canvas rubric located and recorded (`irp/assessment/summative-marking-criteria.md`, with
distinction-band language verbatim + mapping to project assets). Weights: **Exec Summary 10 ·
Intro/Motivation 20 · Methodology 30 · Results/Analysis/Conclusion 30 · Academic Best Practice
10.** Key planning reads:
- **60% of marks (Methodology + Results) map directly onto the decision register (D1–D25) and
  `irp/analysis/`** — the project's strongest assets feed the heaviest criteria.
- "Wider reading" appears in three criteria → the RP formative lesson (literature doing critical
  work in EVERY section) now governs up to 80% of the mark.
- Methodology's ethics phrase is retrospective ("how methods were **applied**") — write applied
  ethics, not proposal-style prospective ethics.
- Exec Summary is a NEW component (no RP equivalent) — write last, mirror the finished report.
- Conclusion must refer back to points AND literature raised earlier — plan the lit review so the
  conclusion has named claims to return to.
- **Brief still outstanding** (word count, deadline, structure, formatting, appendix + AI-policy
  wording) — no assessed prose drafted until it lands. Module notes updated.

## 2026-09-08 — Unit 1 materials landed: converted + readings audited; supervisor identified

- **`irp/units/unit-1/` (25 docx + 1 PDF) converted to .md** (pandoc 3.8.3, all clean);
  units 2–4 empty (release later). `readings-index.md` compiled with holdings audit.
- **Reading gap: Biggam, *Succeeding with Your Master's Dissertation* (2015) — the module's
  named MAIN guidance text — not held. ACQUIRE via York Library e-book (Leganto).** Everything
  else already in `references/` (Dawson 2009+2015, Cottrell 2014, Creswell 6th-vs-4th edition
  mismatch noted, Zobel 3rd-vs-2nd noted — map chapters by title). Ross & Sheail 2017 provided
  in the unit folder.
- **Supervisor allocated: Seema Jehan** (per student note in 1.2.4) — Fast-Track ethics form
  emailed to her 2026-09-08, awaiting feedback. IRP mandates a completed+signed ethics form;
  full-PSEC route not expected (no human data — automated metrics on public benchmarks, per
  RP-era screening). **Honest note for the record:** module guidance says primary data
  collection should await ethics confirmation; this project's measurements (no human
  participants, public artefacts only) ran under the RP-era Fast-Track self-assessment —
  raise proactively in the first supervision meeting alongside the design-as-executed
  conversation (supervisor brief ready).
- Module shape (1.0): 16 weeks, 4 phases — definition/planning (wk 1–4), initiation/conducting,
  control/testing+analysis, closure/presentation; all units to be reviewed by end of Week 5.
- Next: full /process-week-style pass on unit-1 (summary, glossary, practice, extracts).

## 2026-09-09 — Unit 2 landed + converted; Biggam hunt continues; Bell 4th edn added

- **`irp/units/unit-2/` (8 docx) converted + `readings-index.md` compiled** (Initiation phase,
  weeks 5–8; module says work through by end of Week 2). Video transcripts captured in-file.
- **Biggam so far:** EBSCO ch3 (Referencing) + ch5 (Dissertation Introduction) + Figure 1.2
  skills PNG in `references/`; mapping settled (planning = EBSCO ch4, lit review = EBSCO ch6);
  **unit-2 adds Chapter 8 "Research methods" to the download list.** More downloads over coming
  days as quota allows.
- **New acquisitions needed from unit-2:** the unidentified **"S. Bennet"** text (ch3/ch5/ch21 —
  open the Leganto link to identify, then acquire) and the **Dawson & Dawson** process-models
  paper (York libproxy one-click). **Bell & Waters:** 4th edn now in `references/`
  (student-sourced) but module cites the **6th edn e-book + Chapter 13** — prefer the 6th via
  York, else map by title and cite the edition read.
- **Feed-through gold:** 2.4.1 names the pilot harness's category — an **experimental
  prototype** (Dawson's taxonomy: "explore the technical feasibility … explore and test
  performance") — adoptable vocabulary for the methodology chapter. 2.5's "do not 'tweak'
  material that has not worked … writing about the problems is likely to gain you credit" is
  direct licence for the deviations-as-evidence narrative. MoSCoW maps onto the project's
  scope tiers. Bell & Waters' research-diary advice describes this very log.

## 2026-09-10 — Biggam full 5th edn acquired (quota dance over) + economics/TCO discussion angle

- **Biggam 5th edn full PDF in `references/`** — TOC mapped; all remaining assignments servable
  by title (ch3 Preparing, ch6 Lit Review, ch7 Research Methods). Module's page cites are
  2015-edn; EBSCO 2015 chapter PDFs now optional page-exactness backups. Unit-1/2 reading
  shelves effectively COMPLETE.
- **Musing recorded (student, 2026-09-10): hardware + energy economics in 2026 as a Discussion
  angle.** (a) account for 2026 hardware and energy costs; (b) older hardware second-life —
  e.g. owned 64GB DDR4 vs buying DDR5 at 2026 RAM prices; (c) scales for organisations with
  amortised datacentre/fleet investments. **Assessment: adopt as Discussion-chapter
  interpretation, NOT new scope.** Basis:
  - It closes the loop to the proposal's own opening premise ("hardware organisations already
    own"; cloud token budgets) — feeds the rubric's "outcomes discussed in the broader context
    of the field" (Results 30%) and "conclusion refers back to points raised".
  - All inputs for an ILLUSTRATIVE cost-per-token exist: measured J/token per tier, actual
    hardware prices (£375.40 Pi stack / £320 nett Jetson / Mac owned), 2026 UK electricity
    price (cite a source when drafted). Present per-tier, order-of-magnitude, carrying the
    D13/D23 measurement-boundary caveat (absolute cross-tier J/token not comparable).
  - The 2026 RAM-price inflation is already a lived data point in this log (the £349.30 16GB
    Pi kit) — citable as context for the owned-hardware argument.
  - ~~DDR4 second-life claim~~ → **DROPPED (student decision, 2026-09-10):** unmeasured
    extrapolation, cut rather than caveated. The Discussion keeps only the measured anchor
    (an £80-class Pi 5 clears the interactive SLO at Q4) + the cost-per-token illustration.
  - Scope guard: ~a page in Discussion + a Future Work line (pairs with E3 external meter);
    no new RQs, no new measurements.

## 2026-09-10 (later) — Unit 3 processed; DDR4 angle dropped

- **`irp/units/unit-3/` (10 docx) converted + readings-index compiled.** Control phase (weeks
  9–12; work through by end of Week 4). **Nothing to acquire** — every assignment already on
  the shelf, with the module's edition-inconsistent Biggam chapter numbers resolved by title
  (An emotional journey → 5th-edn ch3; Limitations and potential hurdles → 5th-edn ch7;
  Zobel "Getting it wrong" → 3rd-edn ch5 pp.67–72, TOC-verified).
- **Write-up checklist item from 3.2.2:** testing evidence must be PRESENTED explicitly
  ("there needs to be evidence that this has taken place") — plan a testing/validation
  subsection collecting the harness self-checks, determinism tripwire, cross-device check and
  clean-clone rehearsal.
- Unit 3's content is largely a description of practices this project already executed and
  logged — the readings become citations FOR the existing record (Dawson ch7 trade-offs →
  descope/fallback decisions; Biggam limitations section → Limitations chapter; 3.3.2's
  "research is iterative" → the JetPack pivot + D25 revision as endorsed practice).
- DDR4 second-life discussion angle dropped (see amended 2026-09-10 entry above).

## 2026-09-10 (evening) — Unit 4 processed; ethics meeting brief prepared (meeting 2026-09-11)

- **Unit 4 (Closure/writing-up) converted + indexed — nothing to acquire; ALL FOUR UNITS now
  processed** within the module's first week (module asks for end of Week 5). Flagged for
  dedicated study: 4.2.1/4.2.2 examiner-psychology files + the two **example-project ZIPs**
  (real submitted Masters reports — calibration for structure/length/figures).
- **Ethics meeting brief written (`irp/ethics-meeting-brief.md`)** for tomorrow's supervisor
  meeting (Fast-Track approval). Core: the "HumanEval+ = human subjects?" name-flag disarmed
  from the primary source — Chen et al. 2021 §2.2 is literally titled "HumanEval: Hand-Written
  Evaluation Set" (human-WRITTEN problems, authored by the paper's own researchers as an
  anti-contamination measure; evaluation is by automated unit tests, explicitly IN CONTRAST to
  human evaluators — §1). Plus full form-sweep: §1.2 Yes/No adjudication left to supervisor,
  black-box training-data caveat, sandboxed code execution (with Chen et al. precedent),
  proactive "data already collected under RP-era screening, no primary human data" framing,
  licences verified, summarisation exclusion. Closing rule: don't over-defend; take the
  supervisor's steer on a signed declaration.

## 2026-09-11 — Literature review health-check (vs units 1.2.2/1.2.3 + IRP rubric)

**Verdict: strong as submitted (themes not summaries; named Liu-vs-Lee contradiction;
problematisation with warrant — since empirically vindicated); ~70% of the dissertation
chapter.** Actions for the IRP version:
- [ ] **Re-run the systematic search before writing** — "no study combines…" is frozen at
      mid-Aug 2026; confirm it survives September + log the re-search date (method evidence).
- [ ] **Add literature homes for two findings that lack them:** D25 cross-device divergence →
      FP non-determinism / backend-variance sources; Q3_K GPU trap → llama.cpp kernel grey-lit.
      (Collapse-thresholds and the 4-bit rule are already anchored.)
- [ ] **Reflexivity notch (deferred from RP review):** one sentence each on Kurt [2026] and
      Nguyen [2025] being preprints doing load-bearing work.
- [ ] **Structure per 1.2.2:** the dissertation lit-review chapter must END by deriving the
      RQs (RP moved derivation to the Intro for word economy).
- [ ] Expansion priority when brief lands: strand 4 (closest studies) grows most — Results/
      Conclusion call back to it. Skim Biggam ch6 before drafting.

## 2026-09-11 (later) — Ethics route settled: Self-Assessment form suffices

Supervisor meeting outcome: **the Self-Assessment Ethics form is all that is required** —
lightest of the three routes (Self-Assessment → Fast-Track → full PSEC). Per the form's own
rule, No to all Section-5 items ⇒ no ethical approval needed; the supervisor approves the form
directly and it is NOT forwarded to the ethics committee. All ten Section-5 answers are No for
this project. **Draft answers prepared: `irp/SelfAssessment-Ethics-DRAFT-answers.md`** (reuses
the verified Fast-Track content: RQs, non-expert methodology, data sources + licences verified
2026-07-21, sandbox note; HumanEval name clarification embedded in §4 to pre-empt the
name-flag). Fast-Track draft retained as backup detail. **APPROVAL COMPLETE 2026-09-11** — form signed and
supervisor-approved (Self-Assessment route; no committee involvement per the form's rule).
Signed copy: OneDrive module-11 admin folder. **The project's ethics story is closed:** RP-era
screening → deliberate scope-to-approval alignment (RQ4 descope, summarisation exclusion) →
Self-Assessment sign-off for the IRP.

## 2026-09-12 — E1 ACTIVATED: open-book (docs-RAG) runs join the study as RQ1b

Student decision: include open-book runs alongside closed-book. Design as revised on activation
(`irp/extensions/e1-context-conditions.md`):
- **RQ1b — "does reference-documentation context mitigate quantisation-induced degradation?"**
  Named sub-question, not "an extra condition" — hypothesis-driven framing for the supervisor
  conversation; makes the pre-registration self-documenting.
- **Condition B = retrieval over official Python reference documentation** (supersedes the
  few-shot-exemplars sketch). Oracle probe stays optional.
- **Pre-registered contamination sweep** before any scored run: n-gram overlap between every
  retrieved chunk and the canonical HumanEval+ solutions (threshold fixed in the protocol) →
  thesis defence line "no retrieved chunk shared >n-gram overlap with reference solutions".
- **Python docs licence VERIFIED at source 2026-09-12** (docs.python.org/3/license.html):
  PSF License v2 for docs; doc code examples dual PSF-2.0 + Zero-Clause BSD since 3.8.6 —
  permissive, research use clearly permitted. Record docs version + retrieval date in the
  provenance manifest.
- **Ethics impact: route unchanged** — all ten Self-Assessment answers stay No (public,
  openly-licensed documentation; no humans, no personal data). Action: one-line email to
  supervisor adding Python docs to the signed form's data-sources section (amendment diligence,
  mirroring the RQ4-descope precedent); update the form's §4 wording.
- **RQ impact:** RQ1 gains RQ1b + an interaction hypothesis (Δ(open−closed) per rung; three
  outcomes all reportable, research symmetry). RQ2 gains the optional context-memory tie-in
  (KV-cache price of context on the 8GB edge). RQ3's closed-book map remains canonical.
- **HARD GATE before measuring:** write + commit the E1 protocol (retrieval method, k, chunk
  size, context cap, sweep threshold, same 164/greedy/b9951) — protocol first, data second.

## 2026-09-12 (later) — E1's literature consequences mapped; NEAR-TWIN #3 caught

RQ1b changes the lit review in five ways (recorded in `candidate-reading-list.md` Tier 1c):
1. **New sub-strand (RAG-for-code + context use):** DocPrompting (ICLR23, the Condition-B
   design anchor), Lewis RAG (NeurIPS20, canonical), Lost in the Middle (TACL24 journal — the
   null-model for H1c: context use is fragile even unquantised), Brown et al. (NeurIPS20 —
   n-gram contamination-check precedent for the sweep). All peer-reviewed → audit rises to
   ~18 peer-reviewed anchors.
2. **★ NEAR-TWIN #3 FOUND by pre-claim search: Yazan et al. (arXiv:2406.10251 / CEUR-WS)** —
   quantisation × RAG measured directly, but FP16→INT4 only, 7–8B models, personalisation.
   RQ1b's gap is the unexplored region: full ladder into the collapse zone × execution-scored
   code × edge-class models × docs retrieval. Gap sentence to be written AGAINST this paper.
   (Third catch for the check-before-claiming discipline: Smaller=Weaker, Pape, now Yazan.)
3. **Gap statement extends:** "...and no study tests whether retrieval-grounded context shifts
   the collapse threshold across the full ladder" — verify via extended staleness-sweep terms
   before asserting.
4. **Narrative continuity:** the July formative already trailed "context-driven/RAG local
   models" as future experiments; proposal named the extension; RQ1b executes it — the
   proposal→dissertation arc is self-consistent.
5. Word budget: one new sub-strand (~200–300 words) when the brief's counts land.

## 2026-09-12 (evening) — Condition D added: agentic tool-use probe (gated, timeboxed)

Student proposal, adopted with guardrails: measure Option B after all — but as a **decomposed
probe**, not an end-to-end score. Tool-calling reliability becomes its own DV (M1 validity
rate, M2 loop behaviour, M3 conditional pass@1), which dissolves the D27 confound; the agentic
tool queries the SAME frozen BM25 index as Condition B, so delivery mechanism is the only
difference. Guardrails: **F16 gate pilot first** (Qwen-only, ~20 problems, Mac — a floor
result is itself a finding), Mac-only reduced-set ladder if the gate passes, **~1-week harness
timebox**, novelty search before claiming the gap. Framing captured: Option A's family
(inline completion, RAG assistants) = today's dominant paradigm → A primary, D forward-looking.
Full design in `irp/extensions/e1-context-conditions.md`; D27's scope consequence now has an
empirical answer path instead of only a future-work line.

## 2026-09-12 (night) — Writing-style note, canonical RQ file, methodology sync

- **`irp/writing-style.md` created:** the em-dash conversion guide (student-supplied
  2026-09-12: asides→commas/parentheses; pause/explanation→colon; list-summary→restructure;
  loose clauses→semicolon/split; "if a sentence needs an em dash it's doing too much") merged
  with the RP-era rules (definition→brackets; emphatic tail→full stop; contrast→conjunction;
  en dashes retained for ranges) + standing conventions (British English, IEEE, low quote
  density, D26 preprint practice). Applies to all dissertation prose.
- **`irp/research-questions.md` created — the canonical live RQ set** (RQ1→1a→1b→1c→2→2a→3)
  with per-RQ status (answered / to-run / gated), hypotheses incl. H1c and RQ1c's
  no-confirmatory-hypothesis note, evidence homes, and the hard gate. Future RQ changes land
  here first. Marked for refine/revisit after the E1 protocol + supervisor feedback.
- **`irp/supervisor-brief.md` status-updated:** E1 shown as ACTIVATED (RQ1b + RQ1c) with
  pointers; E2/E3 remain unactivated.

## 2026-09-12 (extraction pass) — All 17 lit-review extracts complete, quote-verified

Four parallel extraction agents processed the full queue → `irp/reading-extracts/` (18 files
incl. Pape, consolidated home). Every extract: house template, verbatim quotes with locators,
D26 preprint labelling, gap-notes positioned against the study; agents instructed to report
brief-vs-paper contradictions (the Pape lesson institutionalised) — and they found real ones.
4-quote cross-agent sample spot-verified character-exact against the PDFs. Headline
intelligence logged in `candidate-reading-list.md` (Extraction Pass Complete section):
Afrin's own pass@1 table leans our way; Jin's benchmark set contains zero execution-scored
code (reconciliation verified); Taheri UPGRADED to must-engage (they test FP16 vs Q4_K_M on
function calling — standard small models crater, two points only → RQ1c ladder gap sharpened);
TinyAgent confirms off-the-shelf SLMs fail calling at F16 (gate realism); DocPrompting's BM25
recall bounds expected open-book lift (E1 protocol note); Numerical-Nondeterminism may be
NeurIPS 2025 (upgrade check); Yu's 9.3%-of-failures quantisation statistic = motivation
evidence + M2 taxonomy input. **Literature acquisition + extraction phase CLOSED. Next: E1
protocol document (hard gate) → supervisor amendment ack → corpus build + contamination sweep
→ Condition B sweeps + RQ1c gate pilot. Then venue rechecks + staleness sweep before the
chapter drafts.**

## 2026-09-12 (bench session) — E1 EXECUTED END-TO-END: RQ1b + RQ1c answered in one day

The entire E1 runbook ran and closed today (all committed; hard gate honoured — protocol commit
`8375d3c` preceded every measurement):
- **Phase 1:** pinned Python-3.12 docs (sha256 `8173bb9b…`) → 8,239 chunks → BM25 → frozen
  `openbook_prompts.jsonl` (164, sha `95069f4b…`). **Contamination sweep: 0 ≥13-gram overlaps** —
  the thesis line holds literally. Committed before any run (eaf38aa).
- **Phase 2:** harness `--condition open` (verbatim artefact consumption; `_open` outputs;
  manifest carries condition + artefact sha); smoke green (545ee4f).
- **Phase 3 — RQ1b ANSWERED:** both models × 5 rungs × 164 open-book. **Δ(B−A) ≤ 0 in all 10
  cells; harm peaks at each model's own collapse rung** (Qwen Q2 −0.098 p=.007; Phi Q4 −0.152
  p=.0008, 39 passes broken); 5pp thresholds condition-invariant. K=25 spot-check: 4/25 diverge,
  1/25 flips (reverse direction vs closed-book) → D25 proxy status inherited. Perf tie-in
  (same-session pairs, all tiers): context costs prefill+KV, not decode — TTFT mean Mac 23→113 ms,
  Jetson 77→1,184 ms, **Pi 589→4,957 ms (breaks the registered floor)**; +200–243 MB RSS.
  (`irp/analysis/e1-openbook.md`.)
- **Phase 4 — RQ1c ANSWERED AT THE GATE:** Qwen F16, 20 problems → **M1 = 0/20 → FAIL → probe
  stopped per the binding rule.** Unforced it ignores the tool (and passes 0.90 closed-book);
  forced it emits the wrong wrapper then degenerates. Instrument fairness verified
  (/apply-template). Tool use breaks before generation, at the floor.
  (`irp/analysis/e1-agentic.md`; transcripts committed as the stopped-branch record.)
- **Tier-1 mechanism check (exploratory):** harm predicted by NEITHER retrieval relevance NOR
  context length; the one weak uncorrected signal points the other way (higher-scoring chunks
  break more) → **naive score-gating dropped**; honest statement = "prepended doc-context
  interferes broadly." Bonus: 164/164 recomputed retrievals match the artefact (determinism).
- **E2 proposal drafted, NOT activated** (`irp/extensions/e2-proposal.md`): arms ranked
  imatrix-calibration > dense-retrieval > placement/framing, score-gating dropped on Tier-1
  evidence; supervisor ask + calendar gate written in. Awaits October discussion.

**The day's one-sentence synthesis:** for edge-class coders, closed-book at the quantisation knee
is overdetermined — imposed context hurts (worst at the cliff), asked-for context is inoperable,
and the edge tiers can't afford context's latency/memory bill anyway.

## 2026-09-13 — Implications framing captured (discussion-chapter feed)

Post-E1 discussion ("does the repatriation case fall apart?") resolved and recorded in
**`irp/analysis/e1-implications.md`**: the boundary framing (*generation repatriates; orchestration
does not at this scale*; capability-forced handoff joins the memory/throughput triggers), the
Condition-B-IS-the-scaffold mirror, the size-vs-training separation for the gate failure
(instrument ruled out; fine-tuning, not scale, is the field's remedy), the candidate discussion-
chapter spine paragraph, and the three supervisor-meeting questions. RQ set unchanged.

## 2026-09-13 (later) — E2a ACTIVATED: tool-trained gate rerun + Mac-only 7B scale ladder

Student decision (early enough to bring the supervisor along; E1 gate-2 precedent): Arms 4+5 of the
E2 proposal activate as **E2a**, parameters frozen in `irp/extensions/e2a-protocol.md` BEFORE any
run. Arm 4: 2×2 probe — (tool-trained Qwen3-4B vs Qwen2.5-Coder-1.5B) × (native chat-template
tool-calling vs IFFC-style prompted-JSON), F16, first-20 gate problems, gen cap 2048 for the probe
(reasoning-trace budget). Arm 5: Qwen2.5-Coder-7B-Instruct, bartowski F16 → naive b9951 ladder (D6),
closed + open 164×5 on the Mac (36 GB F16 anchor verified); edge cells out of scope for now.
Ethics delta nil (two more public open-weights models, same benchmark/corpora). Arms 1–3 remain
proposal-only for October. Timeboxes: Arm 4 one bench day; Arm 5 three.

## 2026-09-13 — E1 results reviewed; builder-urge scope hold (repatriation claim REFINED, not lost)

Review verdict on the 2026-09-12 E1 execution: all three findings clean and disciplined —
RQ1b (frozen doc-context hurts, worst at each collapse rung; Δ≤0 all 10 cells), RQ1c (tool
use absent at F16 while closed-book = 0.90; gate honoured, probe stopped), perf tie-in
(context cost = prefill + KV, a tier property; Pi open-book TTFT 4,957ms BREAKS the
registered 1–2s floor → open-book is SLO-infeasible on the CPU tier). Boundary to carry into
the write-up: the RQ1b finding is bounded by this retrieval configuration (frozen BM25, k=2 —
the pre-registered modest-lift expectation); "this deployed RAG pattern hurts", not "context
can never help".

**Scope hold (student concern addressed):** the urge to BUILD a fine-tuned tool-calling model
that thrives under quantisation on the Pi = a different thesis (weeks of curation/training/
eval; TinyAgent is the existence proof that specialisation works). Decision: NOT in scope
(escalation rule + MoSCoW Won't-have stands). The repatriation claim is REFINED, not thrown
out: proven for the dominant closed-book/completion mode (Qwen@Q4 clears quality + SLO on all
tiers incl. the Pi); measured boundaries for context-augmented and agentic modes (distraction
cost, F16 tool floor, prefill price). Future Work will spec the follow-on build with measured
requirements (the F16 floor to cross, the Pi prefill budget, the distraction cost to avoid).
**Sanctioned outlet: a one-afternoon DEMO of the proven mode** — Qwen@Q4 on the Pi wired into
an editor as a live local completion assistant (screenshot + timed completion) = "artefacts
developed support this effectively" evidence for the methodology criterion, not new scope.

## 2026-09-13 (later) — E1-R pre-registered: the scaffolding question

Student decision (the sanctioned form of the builder's urge): two instrument-modified probes
asking whether the E1 negatives are fundamental to the model class or fixable by tooling —
**R1** (grammar-constrained, two-stage model-chosen retrieval: GBNF removes the syntactic
failure mode that closed the RQ1c gate; measures semantic query quality + pass@1 vs A and B)
and **R2** (oracle-retrieval open-book: upper-bound selection with the same contamination
guard; O-vs-A/O-vs-B decides whether E1's distraction cost was retrieval quality or context
handling). Registered per the escalation rule as a new logged decision with supervisor
notification (chase-email line) and calendar check; **binding timebox 2026-09-20**; no further
expansion under any outcome; fine-tuning stays Future Work. Protocol:
`irp/extensions/e1r-protocol.md`. Also noted: keep a student-authored reflections thread (the
"emotional journey" is rubric-relevant material for the process-evaluation/reflection parts
of the write-up).

## 2026-09-13 (late) — E1-R EXECUTED AND ANSWERED, same day, inside timebox

Both probes ran end-to-end (protocol 400edc8; artefacts committed pre-run; supervisor line sent):
- **R1 gate PASS — M1′ 20/20 at F16.** With GBNF carrying the syntax, the 1.5B formulates
  sensible queries every time: the E1 "agentic floor" was FORMAT + policy, never intent. Ladder:
  M1′ ≈0.99 to Q3 then breaks at Q2 (0.86, degen 5→26 — collapse-rung signature, 3rd subsystem);
  R1 pass@1 ≈ B everywhere, significantly below A at Q4/Q3/Q2 — model-chosen context doesn't pay.
- **R2 oracle: O ≤ A everywhere, O ≈ B everywhere** — significant harms exactly at the collapse
  rungs (4th signature appearance). Registered-map verdict: **syntax is scaffolding-fixable;
  context-exploitation is not** — these models cannot exploit even ideal context on
  self-contained tasks, at any selection quality, any query agency, and (per E2a) any scale.
- Write-ups: `e1r-agentic.md`, `e1r-oracle.md`; RQ file REVISIT clause answered. The E1→E1-R arc
  ("failure mode → scaffolding test") is complete; fine-tuning stays Future Work per the binding
  rule; E4 resourcing note stands as the costed future-work path.

## 2026-09-14 — E2b (imatrix arm) run and answered: calibration moves the cliff — and the context harm moves with it

Registered 72e1c43, chain ran overnight (imatrix x2 -> calibrated Q4/Q3/Q2 -> closed 6 cells +
open collapse-rung cells). **H-E2b1: calibration moves Phi-3's collapse threshold TWO rungs
(Q4->Q2; Q4/Q3 now within the 5pp margin at -1.8pp) and halves Qwen's Q2 cliff (+22.6->+8.0pp,
I-N +14.6pp p=.0004).** Model-dependent in mirror image of the collapse. **H-E2b2: the context
harm FOLLOWS the cliff, not the bit-width** — it vanishes at calibrated Phi-Q4 (no longer a
cliff) and persists at calibrated Qwen-Q2 (still cliff-adjacent): 5th collapse-rung-signature
appearance, now with an intervention demonstrating co-movement. D6 vindicated both ways (naive
ladder needed to SEE the collapse; calibrated arm measures the +14-20pp mask). "Use imatrix
quants" is now a measured recommendation. Write-up: `irp/analysis/e2b-imatrix.md`.

## 2026-09-14 (later) — Loose end registered: 7B edge-tier perf cells (deployment leg of the memory-matched claim)

Flagged in `e2a-results.md` caveats, promoted here so it cannot silently evaporate: the E2a
memory-matched headline (7B@Q2_K 2.9GB = 0.793 vs 1.5B@F16 3.1GB = 0.610, +18pp) currently rests
on the Mac quality axis only. Its **deployment leg is unmeasured**: does 7B-Q2 actually run
acceptably on the Pi and Jetson (tok/s, TTFT vs the registered SLO floor, peak RSS, J/token)?
This is the single most tempting remaining measurement — small, one bench day, existing machinery,
ethics delta nil. **Rule: it happens register-first (own protocol note, frozen before runs) and
only if the write-up schedule genuinely absorbs it; otherwise it is reported honestly as a bounded
claim ("quality-per-byte ordering measured; edge-tier feasibility of the 7B untested").**

## 2026-09-14 (later) — Why-not-RAFT rationale recorded (write-up feed)

The E4-vs-RAFT ordering question ("why fine-tune tool-calling next, not context-handling, when
context is the headline deficit?") is answered and recorded in the E4 spec (§"Why E4 and not
RAFT"): (1) HumanEval+ is self-contained, so RAFT success is undetectable on current instruments
— best case Δ≈0, reachable degenerately by learning to ignore context; a docs-required benchmark
must exist first; (2) RAFT's training data sits in the eval set's own task family (worse
contamination surface, needs a no-docs control arm); (3) E4 has in-study deficit (0/20) +
in-study existence proof (4B forced 0.80) + crisp headroom + the unmeasured H4b ladder;
(4) interpretive asymmetry. RAFT = sequenced not rejected; benchmark+RAFT pairing = the
PhD-seed follow-on. Discussion/Future-Work chapters should carry this ordering argument.

## 2026-09-14 (later) — E4 ACTIVATED (staged), overriding the supervisor-first clause: dated decision

Student decision: don't hold E4 for the October meeting — **the formative becomes the review
gate** and its feedback the supervision input (supervisor informed via the standing thread).
Override is risk-staged in the spec amendment: **α** = data (licence-verified, decontaminated,
open/local only) + ONE LoRA run (≤2 iterations, 10-day hard timebox) + F16 gate on the E1/E1-R
battery (H4a); **β** = the H4b quantisation ladder ONLY on α-pass (cheap once an adapter exists);
further iteration = formative-gated. **Write-up lien binding:** α is additive never load-bearing,
aborts unconditionally if first full methods+results drafts aren't on track by 2026-09-28.
Sequence: E2c completes → α begins. Stage-0 (data path + licences + decontamination) starts now
in parallel — no bench conflict.

## 2026-09-14 (later) — Formative = the governing deliverable; reflective thread registered

- **Summative brief not yet open on Canvas; the FORMATIVE is the working target** (Mon week 8,
  13:00; brief + template ingested, `irp/assessment/Formative_Assignment/`). It is the review
  gate for everything staged (E4 iteration 3, E5) and shapes supervision from here — treated
  as load-bearing despite carrying no marks. Plan: draft Literature Review + Methodology per
  the brief's suggestion; propose to the supervisor that part of the feedback time go to a
  results-chapter sample (campaign finished early; brief says feedback allocation is agreed
  jointly). Third person; RP formatting standards; IEEE.
- **Reflective thread registered (write-up-relevant, rubric-relevant):** the student's day job
  is Azure Local SME / Principal Cloud Engineer — professionally wired to ship working
  solutions. The recurring builder's urge vs research discipline (scope holds → registered
  probes → timeboxes → E4-α's gated build → E5 specced-not-built) is the process-evaluation
  arc for the report's reflective element. `irp/reflections.md` created with prompting
  questions — **content stays student-authored only.**

## Pending

- [x] ~~Verify the £349.30 line item~~ → confirmed from invoice 2026-08-27 (16GB RAM-price inflation)
- [ ] Confirm exact delivery date from courier email (~25 Aug)
- [x] ~~Save the invoice into the repo~~ → **REVERSED 2026-08-28: no invoices in the repo.**
      Both invoice PDFs turned out to carry name/address in the extractable text layer (the Pi
      one's black-box "redaction" was a graphics overlay — text intact underneath). Removed from
      tracking + gitignored; local copies deleted 2026-08-28 (originals remain in email). All
      evidential facts (supplier, items,
      prices, dates) are transcribed in the setup logs, which is what the IRP report cites.
      _Lesson for the log: verify PDF redaction by text extraction, not by appearance._
- [x] ~~7B edge-tier perf cells~~ → **done 2026-09-14 as E2c** (registered first:
      `irp/extensions/e2c-7b-edge-perf.md`): Jetson serves 7B@Q2 at 11.1 tok/s (memory-matched
      claim deploys on that tier); Pi fails the throughput floor at every rung (claim honestly
      bounded); Q3 dip localised to GPU kernels. Results appended to `e2a-results.md`.
- [x] ~~E4 activation question~~ → **superseded 2026-09-14 by the dated ACTIVATION AMENDMENT**
      (staged α/β, write-up lien, formative = review gate, supervisor informed via chase
      thread). α ran and CLOSED same day: gate FAIL, reportable (see `e4-alpha.md`); β does
      not run; iteration 3 is formative-feedback-gated.
- [x] ~~Confirm SSD fitted in the HAT+; take assembly photos~~ → both resolved earlier in this
      log: SSD fitment confirmed 2026-08-27 (assembly entry); photos waived 2026-09-01, reasoned.
- [x] ~~Jetson order~~ → **ordered; kit + SanDisk Ultra 64GB microSD ARRIVED 2026-08-28**;
      Integral 500GB NVMe 2280 still in transit. Prices/invoice to record (see
      `irp/setup/jetson/jetson.md`). Setup proceeds from microSD — SSD not blocking.
- [x] ~~Pi first boot~~ → **done 2026-08-28: OS Lite headless, NVMe boot migration, fully logged
      in `irp/setup/pi5/pi5.md` (zero blanks).**
- [x] ~~Jetson install~~ → **done 2026-08-29/30: JetPack 7.2.1 on NVMe (attended attempt 3, D19),
      MAXN_SUPER, CUDA 13.2, llama.cpp b9951, smoke GREEN with GPU offload confirmed
      (`irp/setup/jetson/jetson.md` Ph2–5).**


## 2026-10-09 — Ethics approval status VERIFIED from the signed form (not from memory)

The signed Self-Assessment (`IRP/Amilka-Moses-Self-Assessment-Ethics-form-signed.docx`, untracked, to move to
the admin folder) is the amended version: its data-sources section names the Python documentation corpus
and RQ1c (tool-use probe). Student date 11/09/2026; supervisor declaration Dr Seema Jehan, dated 15 Sep 26;
file last modified 2026-09-15 by the supervisor. So: **approved by the supervisor on 15 September 2026,
covering the core study, E1 open-book and the RQ1c probe.** The form does NOT name the fine-tuning probe
(E4-α) or the MBPP+ replication (E6); E4 activation (14 Sep) was communicated "via the standing thread".
Both stay within the same screening answers. **Action:** raise on 16 Oct whether a one-line amendment should
be recorded; the report's §3.7 must describe the approval exactly (draft wording in
`irp/assessment/Formative_Assignment/rubric-checklist-review-2026-10-09.md`, Edit 7). Also verified today
for the licence table: MBPP CC-BY-4.0; Qwen2.5-Coder-7B-Instruct Apache-2.0; llama.cpp MIT.

## 2026-10-11 — Safe-execution facts confirmed by the student (for §3.7) + one deviation to disclose

Student-confirmed: devices managed over key-based SSH on a private LAN, **no external network access** during
scoring; the EvalPlus virtual environment was **dedicated** to this study; **scoring ran as root (sudo)** (tier
coverage to confirm: Mac only, where `powermetrics` needs root, or all tiers). Harness fact: the memory limit
env var `EVALPLUS_MAX_MEMORY_BYTES=-1` is set unconditionally in `score_with_evalplus`, so EvalPlus's
per-process memory limit (default min(4 GB, system max)) was **disabled on every tier**. EvalPlus defaults
(config.py, read 2026-10-11): per-problem time limit = max(DEFAULT_MIN_TIME_LIMIT 4.0 s, DEFAULT_GT_TIME_LIMIT_FACTOR
4.0 × ground-truth runtime); student to confirm the installed version (`pip show evalplus` in the venv).
**Deviation from the signed form** ("no elevated privileges"): root execution + no memory cap. Report it in
§3.7 as a deviation with mitigations (draft wording in the rubric-checklist review, Edit 7); tell the
supervisor on 16 Oct. Recommended replication configuration: EvalPlus's Docker evaluator.

## 2026-10-11 (later) — CORRECTION: scoring did NOT run as root

The student's recollection ("it ran as sudo") conflated the sudoers rule with running as root. Repository
evidence: the harness runs `sudo -n powermetrics` only when `os.geteuid() != 0` (run_pilot.py L161), and the
2026-08-31 log entry and the power decision in decisions.md both record the Mac sweep as "enabled by a scoped
NOPASSWD sudoers rule for /usr/bin/powermetrics". So the harness and the EvalPlus scorer ran as the normal
user on every tier; only the power sampler binary was elevated. The only deviation from the form's sandbox
wording is the disabled EvalPlus memory limit (unconditional `EVALPLUS_MAX_MEMORY_BYTES=-1`). §3.7 wording
in the rubric-checklist review updated accordingly. Venv location on the Mac: `~/pilot-work/.venv`
(SETUP-NOTES), reached via the gitignored `proposal-dev/pilot/local/.venv` symlink.

## 2026-10-11 (later) — EvalPlus version and time-limit defaults CONFIRMED on the Mac venv

`pip show evalplus` → **0.3.1**. `evaluate --help`: `--min_time_limit` default **1.0** s, `--gt_time_limit_factor`
default **4.0**. So the per-problem limit that actually applied = max(1 s, 4 × ground-truth runtime). Note the
current upstream master sets the minimum to 4.0 s; the installed version's 1.0 s is what ran, and §3.7 now
says 1 s. Venv confirmed at `~/pilot-work/.venv`.

## 2026-10-11 (later) — Data-management decisions RECORDED (student)

- **Retention and location:** results, harness, protocols, analysis scripts and figures stay in the public
  repository `github.com/AmilkaCodes/RP` **indefinitely**, with a tagged release at submission. Signed or
  named documents (ethics form, invoices) are never in the repository; they travel only in the artefact ZIP
  and the student's private OneDrive copy. [Student: department's own retention period, if any, from the
  16 Oct meeting.]
- **Licences:** `LICENSE` (root) scopes the repository: code MIT, data/protocols/figures CC BY 4.0, prose all
  rights reserved; `LICENSE-DATA.md` carries the CC BY 4.0 links and attribution; README has a Licence section.
  Not yet committed or pushed (user-run). The dissertation's data-management paragraph can now state both
  licences as facts.

## 2026-10-11 (later) — [33] RESOLVED: Dmitrienko & D'Agostino 2013 read and extracted

Student obtained the *Statistics in Medicine* tutorial (vol. 32, pp. 5172–5218) via York library; PDF in
`references/`. Read §4–4.2 and §6.1–6.2; extract with verbatim quotes and printed-page locators in
`irp/reading-extracts/dmitrienko-2013_multiplicity-adjustment-tutorial.md`. It grounds the fixed-sequence
building block (§4.1, p. 5181: full level at each step, stop at first non-rejection) and its monotone-power
caveat (p. 5182, p. 5193); the two-direction construction in §3.5 remains the dissertation's own derivation.
Maurer, Hothorn & Lehmacher 1995 is dropped (never opened; not obtainable online).

## 2026-10-16 — Supervisor meeting (Dr Jehan): notes recorded, actions mapped

**Student's notes (tidied, content unchanged):**
- IRP marking differs from the RP: no project-management criterion. The introduction criterion covers project
  identification and the literature review together; the methodology criterion covers research methodology
  and ethical implications. Read the distinction wording closely; some markers are strict and rigid with the
  rubric and the section names, so the structure must be tight.
- Computational approach: what was used and why, or why not, with references; inside the methodology or as a
  separate section after it. Research methodology = approach, data collection, methodological structure,
  validity and limitations, with references justifying each choice and recording the alternatives. Compare
  several references to justify, or to show the limitations of, the computational approach.
- Computational-approach content: algorithms used, environment and tooling, implementation, data sources and
  ingestion. Give a lay overview at the start of each section (the marker may not know the topic), then the
  detail; diagrams for implementation and tooling; a research-methods-and-pipeline diagram at the start or
  in the overview; some description before data cleaning/pre-processing detail.
- Research gaps: a heading for each gap, discussed in detail; the same for the research questions.
- Results chapter: revisit the RQs first, then the results; how each RQ is answered, how well, limitations,
  and whether and how the results complement existing research, with references.
- Introduction: keep RQ1 general; do not write "HumanEval+ pass@1" inside the RQ.
- Literature review: start with the challenges, identify the gaps, then the methodology; connect the method
  to the research questions.
- Preprints: avoid wherever possible; arXiv citations heavily discouraged; find peer-reviewed versions or
  replacements.
- Ethics: coverage is good; additional sources that fit the form are fine; an additional form is submitted
  if needed. [Student to confirm which applies to MBPP+ and the fine-tuning probe.]
- Her suggested methodology layout: 3.1 The Philosophical Approach · 3.2 The Computational Approach ·
  3.3 Research Methods and Applied Pipeline (3.3.x subsections; her list was a generic example from another
  project) · 3.4 Methodological Limitations · 3.5 Ethical and Professional Considerations.
- First line of the notes, "Ask for clarification on marking": referent to confirm.

**Actions:** `irp/assessment/Formative_Assignment/meeting-2026-10-16-actions.md` (Ch3 restructure map, RQ
wording, per-gap and per-RQ headings, overview-first rule, preprint replacement list, summative results rule,
open questions for the student).

## 2026-10-20 — RP mark clarification answered; item closed

Marking team's reply (verbatim substance in `assignments/summative/SUMMATIVE-FEEDBACK.md`, bottom section): band
intended; ethics-in-methodology was a typo (no mark effect, Canvas to be corrected); data management and
reproducibility belong in the methodology with specifics ("exact llama.cpp commit hash, Python version and full
hardware specifications (CPU, RAM speed, OS build)"); Figure 1 needed its numbers in a table; moderation is by
regulation. No procedural ground; no appeal. IRP plan unchanged. New concrete action for the formative:
a devices-and-software table in Chapter 3 with commit hash, Python/EvalPlus versions and per-device CPU, RAM, OS build.

## 2026-10-20 — Table 3.1 Jetson row VERIFIED on the device (student-run commands)

Outputs captured over SSH: `/etc/nv_tegra_release` → `R39 (release), REVISION: 2.1, GCID: 46758480, BOARD: generic,
EABI: aarch64, DATE: Fri Aug 7 05:54:22 AM UTC 2026`, `KERNEL_VARIANT: oot`; `nvidia-jetpack` Version `7.2.1-b49`;
`uname -r` → `6.8.12-1021-tegra`; `nvcc --version` → `Build cuda_13.2.r13.2/compiler.37953736_0`; `nvpmodel -q` →
`NV Power Mode: MAXN_SUPER` (mode 2); `jetson_clocks --show` → SoC tegra234, "NVIDIA Jetson Orin Nano Engineering
Reference Developer Kit Super", CPUs 0–5 online, governor `schedutil`, MaxFreq 1,728,000 kHz, current frequencies
below max → clocks not pinned, consistent with D26 (`jetson_clocks` recorded OFF for all runs). Every value in
Table 3.1's Jetson row matches; the row now also states "jetson_clocks off".

## 2026-10-20 — Table 3.1 Pi and Mac rows VERIFIED on the devices (student-run commands)

Pi 5 (`viper-pi5`): `/etc/os-release` → `PRETTY_NAME="Debian GNU/Linux 13 (trixie)"`, `VERSION_ID="13"`; `uname -r` →
`6.18.39+rpt-rpi-2712`; `vcgencmd get_throttled` → `throttled=0x0`. MacBook Pro (`viper-mbp`): `sw_vers` → macOS
26.6.2, BuildVersion 25G83; `machdep.cpu.brand_string` → `Apple M3 Max`; `hw.memsize` → 38654705664 (36 GB). All match
Table 3.1; the table now states the Debian 13 base and the macOS build number. All three rows are device-verified.

## 2026-10-20 — Summative-length full draft built (8,936 words) and rubric-checked

The 19,300-word full draft was trimmed to the 9,000-word cap without changing any reported number: six passes
(two whole-file rewrites, then four exact-string deletion scripts, `trim_pass3.py` to `trim_pass6.py`). Per-cell
tables moved to a new Appendix D (18 tables); Figure 4.5 and body Table 4.2 dropped; figures and tables renumbered
without gaps. Built by `build_summative_draft.py` + `renumber_ieee.py` from a fresh unpack of the 2026-10-18 master;
XSD-validated; 46 references in first-appearance order (1–46, no gaps); executive summary 495 words. Master:
`final/COM00151M_Formative_SummativeLength_Amilka-Moses_2026-10-20.docx`; text copy beside it. Strict rubric-checklist review
(`review-note-2026-10-20.md`): improvement items listed (the §5.3 reflective slot is the
student's; §4.6 RQ sentences; a lay-reader sentence under Figure 4.4; appendix page count to check in Word).

## 2026-10-20 (evening) — Review items applied

Figures 3.2 (configuration file + manifest, drawn from the real files) and 3.3 (verdict classes on three real cells) added;
§4.6 now answers each RQ in a sentence; lay sentence under the deployment map; §4.5 leads name their findings; §5.3 reflective
paragraph drafted from the log for the student's approval; Stack Overflow 2025 survey (press release, read 20 Oct) and Qualcomm
2023 "The future of AI is hybrid" Part I (PDF read, §3.2.1 and §3.2.4) cited as practitioner and grey sources; 48 references
renumbered 1–48; body 8,960 by the build counter; executive summary 500; validated. Student items unchanged plus approval of
the reflective paragraph and a read of the two new sources.

## 2026-10-20 (night) — External reviewer's items applied; rebuilt at 8,932 declared words (incl. figure text)

Each item checked against the records before changing text (MBPP+ Qwen Q8_0 discordants recomputed from the snapshots: b = 4,
c = 0; 589 ms explained from `e1-openbook.md`; memory anomalies confirmed reproducible in the Pi 5 perf CSVs; interval-class
adoption dated from the 2026-09-21 note in `mbpp-robustness.md`). Two build defects found and fixed: appendix citations were not
renumbered (Appendix B cited [41] for Clopper–Pearson), and the glossary had been inserted inside the ToC field. Disposition table in
`review-note-2026-10-20.md`, addendum 2.

## 2026-10-21 — Reviewer's third pass fixed; the improvement plan applied; rebuilt at 8,959 declared words

Breakages from the earlier edits repaired (antecedent, fractured sentence, Table D.10, Q3_K_M addendum clause). The latency gate
is now applied to cold-inclusive first-token means from the run CSVs (Table 4.3), with the re-application reported in §4.4 (no
verdict changes). New analysis from the snapshots: Table 4.2 (what is lost at the cliff) and Table 4.6 (first beyond-margin rung
by model, recipe and benchmark; nine cells). Specialisation inference written out in §5.2. Methodology thresholds justified and
registered-versus-added statistics stated. Executive summary rewritten for a lay reader. Figure 4.1 rebuilt with intervals and
margins; deployment map reduced to symbols.

## 2026-10-21 (later) — Fourth reviewer pass implemented; master now the 21 Oct file

Reviewer's items recorded first (`reviewer-feedback-2026-10-21-pass4.md`) then implemented: page geometry (A4, 2.5 cm), 12 pt
captions, split lists, numbered H3s, ToC bookmark collision fixed; Figures 4.2, 4.3 and 4.5 redrawn at the printed size and the
pipeline figure restored as Figure 3.1; Qwen2.5-Coder and Phi-3 technical reports and the ACM Code cited (51 references, et al. and
DOI usage made consistent); quantisation background paragraph; E2b, E6 and E4-α design in the body; social, commercial and
professional issues stated; Table 4.5 numeric; MBPP+ reversal decomposed per problem; §5.1 walks the objectives; §6.3 gives each
direction its reason and design. Declared count 8971 (8677 body + 294 in figures).

## 2026-10-21 (night) — Fifth reviewer pass: five faults fixed, §5.4 evidence paragraph added

Creswell citation number corrected (a "Ch." qualifier the renumbering regex did not recognise; regex fixed), executive-summary
antecedent, pipeline figure clipping, acknowledgements corrections carried into the source, Figure 4.5 legend, Wei et al.;
§4.3/§4.4 trimmed to fund a §5.4 paragraph tying each recommendation to its cell and condition. Declared 8968.

## 2026-10-21 — Reference [15] (Giagnorio et al.) re-checked: published at ICPC 2026

The paper appears in the ICPC 2026 Research Track programme (Session 6, Mon 13 Apr 2026, Rio de Janeiro) and has an ACM Digital
Library entry (DOI 10.1145/3794763.3794810, seen in the search listing only; the DL page returned 403 here). "To appear" removed;
the entry now reads Proc. 34th IEEE/ACM ICPC, Rio de Janeiro, Brazil, Apr. 2026. Student to confirm page numbers through the
library. Rebuilt as `final/COM00151M_Formative_SummativeLength_Amilka-Moses_2026-10-21b.docx` (the 21 Oct file was open in Word).

## 2026-10-22 — Reference [15] page numbers confirmed from Crossref

Crossref record for DOI 10.1145/3794763.3794810: Proceedings of the 2026 34th IEEE/ACM International Conference on Program
Comprehension (ICPC '26, Rio de Janeiro), ACM, pages 195–206, published online 29 Jul 2026. Entry updated with the pages; rebuilt as `final/COM00151M_Formative_SummativeLength_Amilka-Moses_2026-10-21b.docx`.

## 2026-10-22 — Sixth reviewer pass implemented (Chapter 5 by criterion, numeric contrasts, contributions preview)

Recorded first in `reviewer-feedback-2026-10-22-pass6.md`, then implemented; funded by cuts in §4.3, §4.4, §2 and elsewhere. Build
`final/COM00151M_Formative_SummativeLength_Amilka-Moses_2026-10-21b.docx`: 8692 body + 284 figure words = 8976 declared.

## 2026-10-22 — Reviewer's closing items; content editing closed at 8978 declared

§1.3 renamed to match its contents, §5.4 antecedent restored with the ecosystem sentence as the closing line, glossary moved after
the lists per the brief's order. Remaining work is verification (three §5.2 pinpoints against the PDFs) and the artefact directory.

## 2026-10-22 — The three §5.2 comparisons verified by the student against the PDFs; sentences sharpened

Kurtic Table 3 confirmed (and the 70B's −4.6 on HumanEval+ added); Giagnorio §1 confirmed (recipe caveat and the size
corroboration added, pinpoint Sec. 1); Husom §4.2.1 confirmed verbatim, but the figures are five-task averages and the same section
reports a general Qwen2.5-1.5B dropping at q3_K_M, so the sentence now carries both and notes the instability of their HumanEval
column (fp16 0.62 against q8_0 0.85). Verification notes appended to the three extracts. Rebuilt `final/COM00151M_Formative_SummativeLength_Amilka-Moses_2026-10-21b.docx`, declared 8996.
