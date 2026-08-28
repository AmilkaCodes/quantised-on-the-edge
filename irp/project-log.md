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

## Pending

- [x] ~~Verify the £349.30 line item~~ → confirmed from invoice 2026-08-27 (16GB RAM-price inflation)
- [ ] Confirm exact delivery date from courier email (~25 Aug)
- [x] ~~Save the invoice into the repo~~ → done: `irp/setup/pi5/PiHut_Invoice_Personal_Info_Redacted.pdf`
      (personal info redacted before committing — correct instinct for a public-ish repo)
- [ ] Confirm SSD fitted in the HAT+; take assembly photos
- [x] ~~Jetson order~~ → **ordered; kit + SanDisk Ultra 64GB microSD ARRIVED 2026-08-28**;
      Integral 500GB NVMe 2280 still in transit. Prices/invoice to record (see
      `irp/setup/jetson/jetson.md`). Setup proceeds from microSD — SSD not blocking.
- [ ] Pi first boot: reflash to OS Lite (documented) → headless SSH → `irp/setup/pi5/pi5.md`
