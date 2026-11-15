# Quantised on the edge: measurement data, protocols and analysis (COM00151M IRP)

**Report:** Quantised on the edge: quality, latency and memory trade-offs of small local code-generation LLMs across CPU,
consumer-GPU and edge-GPU hardware. **Student:** Amilka Moses. **Supervisor:** Seema Jehan.
**Assembled:** 2026-11-15 from working-repository commit `89c8912e27031627938c6d40ddc24b5d278ef00b` (the private development repository).
**Public release:** https://github.com/AmilkaCodes/quantised-on-the-edge, tag `v1.0-submission`.

## What this shows
Two small code-generation LLMs (Qwen2.5-Coder-1.5B-Instruct and Phi-3-mini 3.8B) measured down a five-rung GGUF quantisation ladder (F16 to Q2_K) on three hardware tiers (Raspberry Pi 5, Jetson Orin Nano, MacBook M3 Max): correctness on HumanEval+ and MBPP+, latency, memory and energy. Quality holds at the upper rungs and collapses at the deepest (2-3-bit) rungs, and where the collapse starts depends on the model, the re-quantisation recipe and the benchmark. All 36 reported quality cells recompute exactly from the per-problem records in this repository.

## Verify the numbers
```
git clone https://github.com/AmilkaCodes/quantised-on-the-edge
cd quantised-on-the-edge
python3 irp/analysis/scripts/final_audit.py
```
Standard library only; the last line should read `CELLS CHECKED: 36; PROBLEMS: 0`.

Paths below keep their repository-relative names, so the
"Referred to in" column of Table C.1 in the report maps directly onto this directory.

| Path | Contents | Referred to in |
|---|---|---|
| `proposal-dev/pilot/run_pilot.py`, `configs/` | The measurement harness and the per-device configuration files (with `cross_device_check.py`, `score_xdev.py`, `score_xdev_direct.py`, `score_xdev_full.py`, `requirements.txt`, `README.md`) | §3.3.4 |
| `proposal-dev/pilot/results/{mac,jetson,pi5}/` | Performance and energy CSVs with per-row timestamp, device, model, rung and build tag; cross-device JSON records and the full-replication summary; the per-tier `manifest.json` and the dated per-campaign manifests under `manifests/` | §3.3.5, §3.3.8, Tables 4.2, 4.3, D.5 to D.7, D.13 |
| `proposal-dev/pilot/CHECKSUMS.md`, `CHECKSUMS.json`, `hash_models.py` | SHA-256 of all 26 model files, recorded per device after the campaign; the 17 files held on more than one tier agree | §3.3.2, §3.3.8, §3.5, Table D.5 |
| `proposal-dev/pilot/eval-results/mac/` | Per-problem EvalPlus scoring snapshots for every quality cell (HumanEval+ and MBPP+, closed, open, oracle, grammar, calibrated, 7B) | §3.3.8, Tables 4.1, 4.4, D.1 to D.4, D.8 to D.17 |
| `proposal-dev/pilot/e1/` | The frozen open-book prompt artefact, the oracle artefact, the contamination sweep, the GBNF grammar and the E1-R harness | §3.3.3, §4.5 |
| `proposal-dev/pilot/e4/` | E4-α training configurations and gate transcripts | §4.5, Table D.18 |
| `irp/extensions/` | Every registered protocol, with its dated deviations | §3.3.7, Appendix A |
| `irp/analysis/` | Analysis records per extension, the data pack, the results inventory, `collapse_stats.py`, `e1_analysis.py`, the figure scripts and `figures/` | Chapters 3 and 4 |
| `irp/analysis/scripts/` | `final_audit.py` (recomputes all 36 quality cells), `paired_ci.py`, `agree_check.py`, `h1b_rule.py` | §3.3.5, §4.2, Appendix B |
| `irp/decisions.md`, `irp/project-log.md`, `irp/research-questions.md` | The decision register, the dated project log and the research-question ledger | §3.1, §3.3.7 |
| `LICENSE`, `LICENSE-DATA.md` | Code under MIT; data, protocols and figures under CC BY 4.0 | §3.3.8 |

## Recomputing the numbers
Every quality cell in Chapters 4 and 5 and Appendix D is recomputed from the per-problem snapshots by
`irp/analysis/scripts/final_audit.py`; the paired intervals by `paired_ci.py`; the cross-device agreement by `agree_check.py`;
the H1b add-on rule by `h1b_rule.py`. Performance and energy tables are read from the CSVs under `proposal-dev/pilot/results/`.
Model weights are not included: upstream files are pinned by checksum in every run's `manifest.json`, and the quantised
files are regenerated from them by the pinned `llama.cpp` build (b9951, commit 082b326f) named in the manifests.

## Ethics documents
The signed Self-Assessment Ethics form and its update are in the submitted artefact archive only, not in this public repository.

## This repository
This is the history-filtered public counterpart of the private working repository: exactly the paths listed above, with their full commit history, and nothing else. Assembled on 2026-11-15 from private working-repository commit `89c8912e27031627938c6d40ddc24b5d278ef00b` with git-filter-repo; the private repository also holds course materials, assessment drafts and administrative notes, which are not published. Where the project log or analysis notes cite paths outside the table above (setup logs, report drafts, admin), those files remain in the private repository by design.

## Traceability
Registration is by commit: each extension protocol in `irp/extensions/` was committed before its first measurement, and the
public repository's history carries the timestamps. This archive is the agreed artefact directory at the tagged release.
