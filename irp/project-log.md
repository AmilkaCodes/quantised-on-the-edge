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

- [ ] **1. Manifest gap (found 2026-09-01): JetPack version + power mode not stamped.** D13 +
      jetson.md Phase 4 promise "provenance manifest fields per run: JetPack version + power
      mode"; `results/jetson/manifest.json` has neither. Fix: harness stamps
      `/etc/nv_tegra_release`, `nvpmodel -q` output, and `jetson_clocks` state for all future
      runs; dated addendum note that the 08-30/31 runs were at MAXN_SUPER per the setup log
      (honest retro-annotation, not a regenerated manifest).
- [ ] **2. Pi thermal under sustained load** (pi5.md build-out, still open — validity guard for
      the CPU latency cells). Rerun one heavy cell (Phi Q8), watch `vcgencmd measure_temp`,
      then `get_throttled` = 0x0 after the run (sticky flags reset at boot, so it must be
      checked in-session) → licenses "no thermal throttling occurred during measurement".
- [ ] **3. Jetson sustained-load twin:** `tegrastats` during a long cell — throttle/power-cap
      events, DC-supply-holds-MAXN_SUPER confirmation, and the `jetson_clocks` decision
      (record whether used per run). The one open device item from synthesis §7.
- [ ] **4. Within-device determinism on the edge tiers:** self-diff the K=50 set on Pi and
      Jetson (Mac already has variance-0.000 evidence) → makes D25's "deterministic per
      device, divergent across devices" airtight on all three tiers.
- [ ] **5. Clean-clone reproducibility rehearsal (capstone):** fresh clone in a new directory
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

