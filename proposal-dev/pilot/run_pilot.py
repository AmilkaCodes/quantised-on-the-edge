#!/usr/bin/env python3
"""
run_pilot.py — coding-task quantization de-risk harness.

Drives a (model x quant) matrix against a local `llama-server` (OpenAI-compatible API),
generates HumanEval+ solutions, scores them with EvalPlus (sandboxed), and records
pass@1 (base + plus), a parse-rate ladder, and Mac-side latency/memory into a CSV.

The SAME script runs on Mac / Pi / Jetson — only configs.yaml (ngl, paths) changes.

⚠️ NOT executed by its author — validate with `--smoke` (2 problems) FIRST. The first real
   run is expected to be a debugging pass (fix template/extraction issues before trusting numbers).
⚠️ EvalPlus executes model-generated code during scoring — run in a throwaway venv/container.

Usage:
    python run_pilot.py --config configs.yaml                 # full matrix
    python run_pilot.py --config configs.yaml --smoke         # 2 problems, sanity-check the pipeline
    python run_pilot.py --config configs.yaml --only qwen2.5-coder-1.5b-instruct:Q4_K_M
    python run_pilot.py --config configs.yaml --no-manage-server --server-pid 12345
"""
from __future__ import annotations
import argparse, ast, csv, json, os, re, signal, subprocess, sys, threading, time
from pathlib import Path
from datetime import datetime, timezone

try:
    import yaml
    import psutil
    import requests
    from openai import OpenAI
except ImportError as e:
    sys.exit(f"Missing dependency: {e}. Run: pip install -r requirements.txt")

# EvalPlus dataset loader (API is stable; scoring is done via the CLI below).
try:
    from evalplus.data import get_human_eval_plus
except Exception as e:  # pragma: no cover
    sys.exit(f"Could not import evalplus dataset loader: {e}\nRun: pip install evalplus")

# Optional: EvalPlus's own code sanitiser (fallback to a regex extractor if unavailable).
try:
    from evalplus.sanitize import sanitize as evalplus_sanitize  # type: ignore
except Exception:
    evalplus_sanitize = None

OUT = Path(__file__).parent / "results"
OUT.mkdir(exist_ok=True)

INSTRUCTION = (
    "Please provide a self-contained Python solution that completes the following function. "
    "Return ONLY the completed function inside a single ```python code block, with no explanation.\n\n"
    "```python\n{prompt}\n```"
)


# ----------------------------- helpers -----------------------------
def utcstamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def extract_code(text: str, entry_point: str) -> str:
    """Pull the Python solution out of a chat reply. Prefer EvalPlus's sanitiser."""
    if evalplus_sanitize is not None:
        try:
            return evalplus_sanitize(text, entry_point)
        except Exception:
            pass
    # Fallback: take the first ```python ... ``` block, else the raw text.
    m = re.search(r"```(?:python)?\s*(.*?)```", text, re.DOTALL)
    return (m.group(1) if m else text).strip()


def parses(code: str) -> bool:
    try:
        ast.parse(code)
        return True
    except SyntaxError:
        return False


class RSSSampler(threading.Thread):
    """Poll a process's RSS in the background; report peak MB."""
    def __init__(self, pid: int, interval: float = 0.5):
        super().__init__(daemon=True)
        self.proc = psutil.Process(pid)
        self.interval = interval
        self.peak = 0
        self._stop = threading.Event()

    def run(self):
        while not self._stop.is_set():
            try:
                rss = self.proc.memory_info().rss
                # include child processes (llama-server may spawn workers)
                for c in self.proc.children(recursive=True):
                    try:
                        rss += c.memory_info().rss
                    except psutil.Error:
                        pass
                self.peak = max(self.peak, rss)
            except psutil.Error:
                break
            self._stop.wait(self.interval)

    def stop(self):
        self._stop.set()

    @property
    def peak_mb(self) -> float:
        return round(self.peak / (1024 * 1024), 1)


def launch_server(cfg, model, quant) -> subprocess.Popen:
    gguf = Path(model["gguf_dir"]) / quant["file"]
    if not gguf.exists():
        sys.exit(f"GGUF not found: {gguf}")
    cmd = [
        cfg["server_bin"], "-m", str(gguf),
        "-c", str(cfg["n_ctx"]), "-ngl", str(model["ngl"]),
        "--host", cfg["host"], "--port", str(cfg["port"]),
        "--seed", str(cfg["seed"]),
    ]
    print(f"    launching: {' '.join(cmd)}")
    # New process group so we can kill children cleanly.
    return subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                            start_new_session=True)


def wait_ready(cfg) -> None:
    url = f"http://{cfg['host']}:{cfg['port']}/health"
    deadline = time.time() + cfg["server_ready_timeout_s"]
    while time.time() < deadline:
        try:
            if requests.get(url, timeout=2).status_code == 200:
                return
        except requests.RequestException:
            pass
        time.sleep(1)
    raise TimeoutError("llama-server did not become healthy in time")


def stop_server(proc: subprocess.Popen) -> None:
    if proc is None:
        return
    try:
        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
    except Exception:
        proc.terminate()
    try:
        proc.wait(timeout=20)
    except Exception:
        proc.kill()


def generate(client: OpenAI, model_label: str, problems: dict, cfg) -> tuple[list, dict]:
    """Return (samples, timing_stats). Greedy, streaming for TTFT."""
    samples, ttfts, tok_rates = [], [], []
    n = len(problems)
    for i, (task_id, p) in enumerate(problems.items(), 1):
        prompt = INSTRUCTION.format(prompt=p["prompt"])
        t0 = time.perf_counter()
        ttft = None
        text = ""
        completion_tokens = None
        try:
            stream = client.chat.completions.create(
                model=model_label,
                messages=[{"role": "user", "content": prompt}],
                temperature=cfg["temperature"],
                max_tokens=cfg["max_tokens"],
                seed=cfg["seed"],
                stream=True,
                stream_options={"include_usage": True},
            )
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                    if ttft is None:
                        ttft = time.perf_counter() - t0
                    text += chunk.choices[0].delta.content
                if getattr(chunk, "usage", None):
                    completion_tokens = chunk.usage.completion_tokens
        except Exception as e:
            print(f"    [warn] generation failed for {task_id}: {e}")
        t_end = time.perf_counter()
        # decode-only tok/s (exclude prompt processing); best-effort, client-side.
        if ttft is not None and completion_tokens and completion_tokens > 1:
            decode_s = max(t_end - t0 - ttft, 1e-6)
            tok_rates.append((completion_tokens - 1) / decode_s)
        if ttft is not None:
            ttfts.append(ttft * 1000)  # ms
        code = extract_code(text, p["entry_point"])
        samples.append({"task_id": task_id, "solution": code})
        print(f"      [{i}/{n}] {task_id}  ttft={ttft and round(ttft*1000)}ms  parses={parses(code)}")
    stats = {
        "mean_ttft_ms": round(sum(ttfts) / len(ttfts), 1) if ttfts else None,
        "mean_tok_s": round(sum(tok_rates) / len(tok_rates), 1) if tok_rates else None,
        "parse_rate": round(sum(parses(s["solution"]) for s in samples) / len(samples), 3) if samples else 0.0,
    }
    return samples, stats


def score_with_evalplus(samples_path: Path) -> tuple[float | None, float | None]:
    """Sanitise + evaluate via EvalPlus CLI. Returns (pass@1 base, pass@1 plus)."""
    # 1) sanitise
    subprocess.run([sys.executable, "-m", "evalplus.sanitize", "--samples", str(samples_path)],
                   check=False)
    sanitized = samples_path.with_name(samples_path.stem + "-sanitized.jsonl")
    target = sanitized if sanitized.exists() else samples_path
    # 2) evaluate — parse pass@1 from stdout (robust across filename conventions)
    proc = subprocess.run(
        [sys.executable, "-m", "evalplus.evaluate", "--dataset", "humaneval", "--samples", str(target)],
        capture_output=True, text=True,
    )
    out = proc.stdout + "\n" + proc.stderr
    print(out)
    rates = [float(x) for x in re.findall(r"pass@1\s*[:=]\s*([0-9.]+)", out)]
    base = rates[0] if len(rates) >= 1 else None
    plus = rates[1] if len(rates) >= 2 else base
    return base, plus


# ----------------------------- main -----------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs.yaml")
    ap.add_argument("--smoke", action="store_true", help="run only 2 problems to validate the pipeline")
    ap.add_argument("--only", help="restrict to one 'model:quant' (e.g. phi-3-mini-4k-instruct:Q4_K_M)")
    ap.add_argument("--no-manage-server", dest="manage", action="store_false", default=None)
    ap.add_argument("--server-pid", type=int, help="PID of an already-running server (for memory sampling)")
    args = ap.parse_args()

    cfg = yaml.safe_load(Path(args.config).read_text())
    if args.manage is not None:
        cfg["manage_server"] = args.manage

    problems = dict(get_human_eval_plus())
    if args.smoke:
        problems = dict(list(problems.items())[:2])
    print(f"Loaded {len(problems)} HumanEval+ problems{' (SMOKE)' if args.smoke else ''}")

    base_url = f"http://{cfg['host']}:{cfg['port']}/v1"
    client = OpenAI(base_url=base_url, api_key="sk-noauth")

    results_csv = OUT / f"pilot_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    fields = ["timestamp", "model", "quant", "n", "parse_rate", "pass@1_base", "pass@1_plus",
              "mean_ttft_ms", "mean_tok_s", "peak_rss_mb", "llama_cpp_tag", "smoke"]
    with results_csv.open("w", newline="") as f:
        csv.DictWriter(f, fieldnames=fields).writeheader()

    for model in cfg["models"]:
        for quant in model["quants"]:
            tag = f"{model['name']}:{quant['label']}"
            if args.only and args.only != tag:
                continue
            print(f"\n=== {tag} ===")
            server, sampler = None, None
            try:
                if cfg["manage_server"]:
                    server = launch_server(cfg, model, quant)
                    wait_ready(cfg)
                    sampler = RSSSampler(server.pid)
                elif args.server_pid:
                    sampler = RSSSampler(args.server_pid)
                if sampler:
                    sampler.start()

                samples, stats = generate(client, quant["label"], problems, cfg)

                if sampler:
                    sampler.stop(); sampler.join()
                peak_mb = sampler.peak_mb if sampler else None
                if server:
                    stop_server(server); server = None  # free memory before scoring

                samples_path = OUT / f"samples_{model['name']}_{quant['label']}{'_smoke' if args.smoke else ''}.jsonl"
                with samples_path.open("w") as sf:
                    for s in samples:
                        sf.write(json.dumps(s) + "\n")

                base, plus = score_with_evalplus(samples_path)

                row = {
                    "timestamp": utcstamp(), "model": model["name"], "quant": quant["label"],
                    "n": len(problems), "parse_rate": stats["parse_rate"],
                    "pass@1_base": base, "pass@1_plus": plus,
                    "mean_ttft_ms": stats["mean_ttft_ms"], "mean_tok_s": stats["mean_tok_s"],
                    "peak_rss_mb": peak_mb, "llama_cpp_tag": cfg.get("llama_cpp_tag"),
                    "smoke": args.smoke,
                }
                with results_csv.open("a", newline="") as f:
                    csv.DictWriter(f, fieldnames=fields).writerow(row)
                print(f"    -> pass@1 base={base} plus={plus} | parse={stats['parse_rate']} "
                      f"| tok/s={stats['mean_tok_s']} | peak={peak_mb}MB")
            finally:
                if sampler and sampler.is_alive():
                    sampler.stop()
                if server:
                    stop_server(server)

    print(f"\nDone. Results: {results_csv}")
    print("Paste this CSV into RESULTS.md and make the GO / NO-GO call against the fixed criteria.")


if __name__ == "__main__":
    main()
