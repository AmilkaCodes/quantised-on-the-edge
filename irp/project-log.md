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
- [ ] Confirm SSD fitted in the HAT+; take assembly photos
- [x] ~~Jetson order~~ → **ordered; kit + SanDisk Ultra 64GB microSD ARRIVED 2026-08-28**;
      Integral 500GB NVMe 2280 still in transit. Prices/invoice to record (see
      `irp/setup/jetson/jetson.md`). Setup proceeds from microSD — SSD not blocking.
- [x] ~~Pi first boot~~ → **done 2026-08-28: OS Lite headless, NVMe boot migration, fully logged
      in `irp/setup/pi5/pi5.md` (zero blanks).**
- [x] ~~Jetson install~~ → **done 2026-08-29/30: JetPack 7.2.1 on NVMe (attended attempt 3, D19),
      MAXN_SUPER, CUDA 13.2, llama.cpp b9951, smoke GREEN with GPU offload confirmed
      (`irp/setup/jetson/jetson.md` Ph2–5).**

