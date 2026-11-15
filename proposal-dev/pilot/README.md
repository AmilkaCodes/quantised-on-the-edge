# Measurement harness — setup & run

Drives a **(model × quant)** matrix against a local **`llama-server`** (OpenAI-compatible API),
scores HumanEval+ (and MBPP+) with **EvalPlus**, and logs pass@1 + latency/memory to a CSV with a
provenance manifest per run. This harness drove the full study: the Mac pilot, the Pi 5 and Jetson
campaigns, the cross-device replication and the registered side studies.

> ⚠️ **EvalPlus executes model-generated code** during scoring. Use a **throwaway venv** (ideally a container/VM).

## Folder layout
```
pilot/
├── run_pilot.py, configs/, requirements.txt           ← the harness and per-device configurations
├── cross_device_check.py, score_xdev*.py              ← cross-device scoring and comparison
├── hash_models.py, CHECKSUMS.md, CHECKSUMS.json       ← SHA-256 of every model file, per device
├── e1/, e4/                                           ← frozen prompt artefacts and fine-tuning gates
├── results/<device>/                                  ← perf/energy CSVs, manifests, cross-device records
├── eval-results/mac/                                  ← per-problem EvalPlus scoring snapshots
└── local/                                             ← GITIGNORED, per-machine: llama.cpp build · GGUFs · .venv
```
Everything heavy and machine-specific lives in **`local/`** (never synced — each device builds/downloads its own).
The per-device configs point into `local/`.

---

## 0. Prerequisites
- Python 3.10+
- `git`, a C/C++ toolchain + CMake (to build llama.cpp)
- Disk for the GGUF files (F16 of a 3.8B model ≈ 7.6 GB)

## 1. Build llama.cpp (pin ONE tag; use the SAME tag on every device)
The study used **b9951 (commit 082b326f)** on all three tiers; every run's `manifest.json` records the tag.
```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
git checkout b9951
```
Build per device:
- **MacBook (Metal, Apple Silicon)** — Metal is on by default:
  ```bash
  cmake -B build && cmake --build build --config Release -j
  ```
- **Jetson Orin Nano (CUDA)** — match JetPack's CUDA:
  ```bash
  cmake -B build -DGGML_CUDA=ON && cmake --build build --config Release -j
  ```
- **Raspberry Pi 5 (CPU)** — plain CPU build:
  ```bash
  cmake -B build && cmake --build build --config Release -j
  ```
`llama-server` lands at `build/bin/llama-server`. Put that path in the device config's `server_bin`.

## 2. Get the GGUF model files
Download the quant ladder (F16, Q8_0, Q4_K_M, Q3_K_M, Q2_K) for each model from a reputable uploader
(Qwen / Microsoft official, or bartowski). Put them in the `gguf_dir` set in the device config, with the
file names matching the config. Expected SHA-256 for every file used in the study is in `CHECKSUMS.md` /
`CHECKSUMS.json` (recorded per device by `hash_models.py`).
- Qwen2.5-Coder-1.5B-Instruct-GGUF
- Phi-3-mini-4k-instruct-GGUF

If you only have F16 weights, quantise with llama.cpp's `llama-quantize`:
```bash
./build/bin/llama-quantize model-f16.gguf model-Q4_K_M.gguf Q4_K_M
```

## 3. Python env
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## 4. Pick or adapt a config in configs/
One YAML per device and campaign (`mac.yaml`, `pi5.yaml`, `jetson.yaml`, plus the side-study variants).
Set `llama_cpp_tag`, `server_bin`, each model's `gguf_dir`, and confirm the quant `file` names.
`ngl: 999` offloads all layers to the GPU (Mac/Jetson); `ngl: 0` on the Pi.

## 5. Smoke-test the pipeline (do this FIRST)
```bash
python run_pilot.py --config configs/mac.yaml --smoke --only qwen2.5-coder-1.5b-instruct:Q4_K_M
```
This runs **2 problems** end-to-end (server → generate → sanitise → evaluate → CSV). Confirm:
- the server loads and `/health` returns 200,
- generations come back and `parses=True` for most,
- EvalPlus prints a `pass@1` line,
- a CSV row is written under `results/<device>/`.
If `parse=False` everywhere or pass@1 is 0/near-0 on the smoke run, it's almost certainly a
**chat-template or code-extraction bug**, not a floor effect — fix before the full run.

## 6. Full run
```bash
python run_pilot.py --config configs/mac.yaml
```
2 models × 5 quants = 10 configs × 164 problems.
Output: `results/<device>/perf_results_<timestamp>.csv`, per-config `samples_*.jsonl`, and a dated
`manifest.json` (device, OS, llama.cpp tag, config path) — the provenance record every reported
number traces back to.

Handy flags:
- `--only <model>:<quant>` — run a single cell (e.g. re-run one that looked off).
- `--no-manage-server --server-pid <pid>` — point at a server you started by hand (memory still sampled if you pass the PID).

## 7. Score and verify
Per-problem EvalPlus snapshots for every quality cell live under `eval-results/mac/`;
`irp/analysis/scripts/final_audit.py` (repository root) recomputes all 36 reported quality cells from
them and ends with `PROBLEMS: 0`. Cross-device agreement is checked by `cross_device_check.py` and the
`score_xdev*.py` scripts against `results/<device>/`.

---

### What the harness measures (per model × quant)
| Column | Meaning |
|---|---|
| `parse_rate` | fraction of solutions that `ast.parse` cleanly (top of the graded ladder) |
| `pass@1_base` | HumanEval base tests (greedy, 1 sample) |
| `pass@1_plus` | HumanEval+ extra tests — stricter; the sensitive detector of subtly-wrong code |
| `mean_ttft_ms` | mean time-to-first-token (client-side, streaming) |
| `mean_tok_s` | mean decode tokens/sec (client-side, approx) |
| `peak_rss_mb` | peak RSS of the `llama-server` process (+ children) during the run |
| `llama_cpp_tag` | the pinned build tag (provenance) |

### Notes / caveats baked in
- **Greedy (temperature 0)** → deterministic pass@1. Repeat runs confirmed stability (reliability).
- **Contamination caveat:** HumanEval may be partly in training data — this measures *relative* degradation across
  quant levels (unaffected by contamination), not absolute capability; stated in the report.
