# Pilot harness — setup & run

Drives a **(model × quant)** matrix against a local **`llama-server`** (OpenAI-compatible API),
scores HumanEval+ with **EvalPlus**, and logs pass@1 + latency/memory to a CSV.
Design rationale + go/no-go criteria: [`../pilot-protocol.md`](../pilot-protocol.md). Record the run in [`RESULTS.md`](RESULTS.md).

> ⚠️ **Untested by its author** (no models/GPU on that machine). Run `--smoke` first; expect the first real
> run to be a debugging pass (fix chat-template / code-extraction issues before trusting numbers — the protocol's AMBER clause).
> ⚠️ **EvalPlus executes model-generated code** during scoring. Use a **throwaway venv** (ideally a container/VM).

## Folder layout
```
pilot/
├── run_pilot.py, configs.yaml, requirements.txt   ← tracked (syncs to every device)
├── README.md, SETUP-mac.md, RESULTS.md            ← tracked
├── local/          ← GITIGNORED, per-machine: local/llama.cpp (built here) · local/models (GGUFs) · local/.venv
└── results/        ← run outputs: *.csv tracked (recorded numbers sync back) · *.jsonl gitignored
```
Everything heavy and machine-specific lives in **`local/`** (never synced — each device builds/downloads its own).
The `configs.yaml` paths already point into `local/`.

---

## 0. Prerequisites
- Python 3.10+
- `git`, a C/C++ toolchain + CMake (to build llama.cpp)
- Disk for the GGUF files (F16 of a 3.8B model ≈ 7.6 GB)

## 1. Build llama.cpp (pin ONE tag; use the SAME tag on every device)
```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
git checkout <TAG>          # e.g. a release tag like b3xxx — RECORD THIS in RESULTS.md + configs.yaml
```
Build per device:
- **MacBook (Metal, Apple Silicon)** — Metal is on by default:
  ```bash
  cmake -B build && cmake --build build --config Release -j
  ```
- **Jetson Orin Nano (CUDA, later)** — match JetPack's CUDA:
  ```bash
  cmake -B build -DGGML_CUDA=ON && cmake --build build --config Release -j
  ```
- **Raspberry Pi 5 (CPU, later)** — plain CPU build:
  ```bash
  cmake -B build && cmake --build build --config Release -j
  ```
`llama-server` lands at `build/bin/llama-server`. Put that path in `configs.yaml → server_bin`.

## 2. Get the GGUF model files
Download the quant ladder (F16, Q8_0, Q4_K_M, Q3_K_M, Q2_K) for each model from a reputable uploader
(Qwen / Microsoft official, or bartowski). Put them in the `gguf_dir` you set in `configs.yaml`, with the
file names matching the config. **Record the exact source + revision** in RESULTS.md (reproducibility).
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

## 4. Fill in configs.yaml
Set `llama_cpp_tag`, `server_bin`, each model's `gguf_dir`, and confirm the quant `file` names.
`ngl: 999` on the Mac (offload all layers to Metal); later `ngl: 0` on the Pi.

## 5. Smoke-test the pipeline (do this FIRST)
```bash
python run_pilot.py --config configs.yaml --smoke --only qwen2.5-coder-1.5b-instruct:Q4_K_M
```
This runs **2 problems** end-to-end (server → generate → sanitise → evaluate → CSV). Confirm:
- the server loads and `/health` returns 200,
- generations come back and `parses=True` for most,
- EvalPlus prints a `pass@1` line,
- a CSV row is written under `results/`.
If `parse=False` everywhere or pass@1 is 0/near-0 on the smoke run, it's almost certainly a
**chat-template or code-extraction bug**, not a floor effect — fix before the full run.

## 6. Full run
```bash
python run_pilot.py --config configs.yaml
```
2 models × 5 quants = 10 configs × 164 problems. Roughly half a day of compute on the Mac.
Output: `results/pilot_results_<timestamp>.csv` + per-config `samples_*.jsonl`.

Handy flags:
- `--only <model>:<quant>` — run a single cell (e.g. re-run one that looked off).
- `--no-manage-server --server-pid <pid>` — point at a server you started by hand (memory still sampled if you pass the PID).

## 7. Record + decide
Paste the CSV into [`RESULTS.md`](RESULTS.md), add the collapse-curve observation and two qualitative
examples (an FP16 pass vs a Q2 break), and make the **GO / NO-GO** call against the *pre-committed* criteria.

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
- **Timings are client-side and secondary** here (the pilot's decision variable is pass@1). The clean per-device
  latency/memory story comes later on the Pi/Jetson; on the Mac these mainly validate the measurement tooling.
- **Greedy (temperature 0)** → deterministic pass@1. Re-run a couple of cells to confirm stability (reliability).
- **Contamination caveat:** HumanEval may be partly in training data — this measures *relative* degradation across
  quant levels (unaffected by contamination), not absolute capability. State this in the write-up.
