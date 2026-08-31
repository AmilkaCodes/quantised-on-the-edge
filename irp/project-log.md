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
- [ ] Assembly photos — take before/if reopening (methods-appendix + thermal-debug value).

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
- [ ] **Phi-3 Q2_K anomaly — rerun that cell before the Mac perf axis is treated final.** Peak
      RSS 5,672MB at Q2_K > Q4_K_M (5,033MB) > expectations, and TTFT 134ms ≈ 2× every other
      rung; Qwen declines monotonically, Phi-3 breaks pattern at exactly one rung. Real
      (dequant buffers) vs artifact (RSS spike during load) — one rerun decides.
- [ ] **TTFT warm-up exclusion — make the harness provably match the pre-registered words.**
      Rows show TTFT std > mean (e.g. 38.1±54.7ms) = a cold first generation inflating spread.
      Drop the first generation per server start (or record median TTFT alongside mean).
- [x] **Q3_K_M throughput dip REPRODUCED on both models with error bars** (Qwen 146<163,
      Phi 77<85 tok/s) — independent confirmation of the "runtime effect, not a model effect"
      claim in the proposal's Figure 1 caption. PowerSampler self-disable verified (power field
      empty on Mac, as designed).
- [ ] **Jetson SSH hardening to pi5 parity:** `PasswordAuthentication no` in sshd_config
      (key login already confirmed working).
- [ ] **Provenance mapping note in jetson.md:** hostname `viperjet` ↔ manifest `device=jetson`
      (one device, two labels — state it once).
- [ ] **jetson.md tidy (Mac-side):** remove the stale duplicate Phase-5 checkboxes below the
      2026-08-30 session block.
- [ ] Remaining device opens: Jetson swap check (`nvzramconfig`, mirrors pi5 zram watch-item);
      `sudo nvme list` for the Integral's identity; power/thermal under sustained load + confirm
      the bundled DC supply holds MAXN_SUPER; stage Phi-3 quants; verify kit box contents blank.

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
- [ ] Pi first boot: reflash to OS Lite (documented) → headless SSH → `irp/setup/pi5/pi5.md`
- [ ] Jetson install (2026-08-29 when NVMe lands): boot USB → capsule update (`Y`) → BSP → NVMe →
      first-boot setup → MAXN SUPER → llama.cpp/CUDA build spike (`irp/setup/jetson/jetson.md` Ph2–5)

