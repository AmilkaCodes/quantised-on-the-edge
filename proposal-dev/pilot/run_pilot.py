#!/usr/bin/env python3
"""
run_pilot.py — coding-task quantization de-risk harness.

Drives a (model x quant) matrix against a local `llama-server` (OpenAI-compatible API),
generates HumanEval+ solutions, scores them with EvalPlus (sandboxed), and records
pass@1 (base + plus), a parse-rate ladder, and Mac-side latency/memory into a CSV.

The SAME script runs on Mac / Pi / Jetson — only configs/mac.yaml (ngl, paths) changes.

⚠️ NOT executed by its author — validate with `--smoke` (2 problems) FIRST. The first real
   run is expected to be a debugging pass (fix template/extraction issues before trusting numbers).
⚠️ EvalPlus executes model-generated code during scoring — run in a throwaway venv/container.

Usage:
    python run_pilot.py --config configs/mac.yaml                 # full matrix
    python run_pilot.py --config configs/mac.yaml --smoke         # 2 problems, sanity-check the pipeline
    python run_pilot.py --config configs/mac.yaml --only qwen2.5-coder-1.5b-instruct:Q4_K_M
    python run_pilot.py --config configs/mac.yaml --no-manage-server --server-pid 12345
"""
from __future__ import annotations
import argparse, ast, csv, hashlib, json, os, platform, re, signal, subprocess, sys, threading, time
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

RESULTS_ROOT = Path(__file__).parent / "results"   # per-device subdir chosen at runtime

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
        self._stopped = threading.Event()   # NB: don't name this `_stop` — it shadows Thread._stop()

    def run(self):
        while not self._stopped.is_set():
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
            self._stopped.wait(self.interval)

    def stop(self):
        self._stopped.set()

    @property
    def peak_mb(self) -> float:
        return round(self.peak / (1024 * 1024), 1)


class PowerSampler(threading.Thread):
    """Sample board power in the background; report mean watts. Auto-selects a backend:
      - Jetson: `tegrastats` VDD_IN (mW) — whole-board DC input power (streamed).
      - Pi 5:   `vcgencmd pmic_read_adc` — Σ per-rail V×I (polled), i.e. power DOWNSTREAM of the PMIC.
      - Mac:    `powermetrics` (needs root) — SoC power domains (CPU+GPU+ANE, mW); GPU dominates on Metal.
      - unknown: no software route → self-disables (mean_w=None).
    IMPORTANT: the three backends measure at DIFFERENT boundaries (board-input vs PMIC-rail-sum vs
    SoC-domains), so ABSOLUTE watts are NOT directly comparable across tiers; the WITHIN-tier trend along
    the quant ladder (and the derived J/token shape) is. `.backend` records which route was used.
    The Mac route needs root: run the sweep with a NOPASSWD sudoers entry for powermetrics, or as root
    (`sudo -n powermetrics` is tried, then plain `powermetrics` when already euid 0)."""
    def __init__(self, interval_ms: int = 500):
        super().__init__(daemon=True)
        self.interval_ms = interval_ms
        self._stopped = threading.Event()
        self.samples_mw: list[int] = []
        self.proc = None
        self.backend: str | None = None

    def run(self):
        # Backend 1 — Jetson: stream tegrastats VDD_IN (instantaneous board input power).
        try:
            self.proc = subprocess.Popen(["tegrastats", "--interval", str(self.interval_ms)],
                                         stdout=subprocess.PIPE, text=True)
            self.backend = "tegrastats/VDD_IN"
        except (FileNotFoundError, OSError):
            self.proc = None
        if self.proc:
            for line in self.proc.stdout:
                if self._stopped.is_set():
                    break
                m = re.search(r"VDD_IN (\d+)mW", line)
                if m:
                    self.samples_mw.append(int(m.group(1)))
            return
        # Backend 2 — Pi 5: poll the PMIC (sum of rail V×I). One probe to detect, then loop.
        if self._pi_pmic_mw() is not None:
            self.backend = "pmic/rail-sum"
            while not self._stopped.is_set():
                mw = self._pi_pmic_mw()
                if mw is not None:
                    self.samples_mw.append(mw)
                self._stopped.wait(self.interval_ms / 1000)
            return
        # Backend 3 — Mac: powermetrics (SoC power domains; needs root). Prefer `sudo -n` (works with a
        # NOPASSWD sudoers entry), else run directly when already root. Sums CPU+GPU+ANE per sample block
        # (uses the "Combined Power" line when powermetrics prints one).
        if sys.platform == "darwin":
            base = ["powermetrics", "--samplers", "cpu_power", "-i", str(self.interval_ms)]
            cmd = base if os.geteuid() == 0 else ["sudo", "-n"] + base
            try:
                self.proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                             stderr=subprocess.DEVNULL, text=True)
                self.backend = "powermetrics/SoC"
            except (FileNotFoundError, OSError):
                self.proc = None
            if self.proc:
                cur: dict[str, float] = {}
                for line in self.proc.stdout:
                    if self._stopped.is_set():
                        break
                    if line.startswith("*** Sampled"):          # block delimiter → flush previous block
                        if cur:
                            self.samples_mw.append(self._mac_block_mw(cur)); cur = {}
                        continue
                    m = re.search(r"(CPU|GPU|ANE|Combined) Power[^:]*:\s*([\d.]+)\s*mW", line)
                    if m:
                        cur[m.group(1)] = float(m.group(2))
                if cur:
                    self.samples_mw.append(self._mac_block_mw(cur))
                return
        # Backend 4 — unknown / no software power route.
        self.backend = None

    @staticmethod
    def _mac_block_mw(cur: dict) -> int:
        """One powermetrics sample block → total SoC mW: the 'Combined' line if present, else CPU+GPU+ANE."""
        if "Combined" in cur:
            return int(cur["Combined"])
        return int(cur.get("CPU", 0) + cur.get("GPU", 0) + cur.get("ANE", 0))

    @staticmethod
    def _pi_pmic_mw() -> "int | None":
        """Total power (mW) = Σ over PMIC rails of V×I, parsed from `vcgencmd pmic_read_adc`.
        Sums only rails reporting BOTH a current and a voltage (excludes monitor-only rails such
        as EXT5V/BATT) → this is PMIC-downstream power, NOT the USB-C wall input (boundary caveat)."""
        try:
            out = subprocess.run(["vcgencmd", "pmic_read_adc"],
                                 capture_output=True, text=True, timeout=5).stdout
        except (FileNotFoundError, OSError, subprocess.SubprocessError):
            return None
        amps, volts = {}, {}
        for line in out.splitlines():
            ma = re.search(r"(\S+)_A current\(\d+\)=([\d.]+)A", line)
            if ma:
                amps[ma.group(1)] = float(ma.group(2))
            mv = re.search(r"(\S+)_V volt\(\d+\)=([\d.]+)V", line)
            if mv:
                volts[mv.group(1)] = float(mv.group(2))
        rails = [k for k in amps if k in volts]
        if not rails:
            return None
        return int(round(sum(volts[k] * amps[k] for k in rails) * 1000))

    def stop(self):
        self._stopped.set()
        if self.proc:
            try:
                self.proc.terminate()
            except Exception:
                pass

    @property
    def mean_w(self) -> float | None:
        return round(sum(self.samples_mw) / len(self.samples_mw) / 1000, 2) if self.samples_mw else None


def port_in_use(host: str, port: int) -> bool:
    """True if something is already listening on host:port (e.g. a stale/orphan server)."""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex((host, int(port))) == 0


def launch_server(cfg, model, quant) -> subprocess.Popen:
    gguf = Path(model["gguf_dir"]) / quant["file"]
    if not gguf.exists():
        sys.exit(f"GGUF not found: {gguf}")
    # Guard: if the port is already taken, our new server can't bind and would die silently,
    # while wait_ready() sees the STALE server's /health=200 → every cell gets served the WRONG
    # model (a false flat curve). Refuse to run until the port is free.
    if port_in_use(cfg["host"], cfg["port"]):
        sys.exit(f"Port {cfg['port']} is already in use — a stale llama-server is likely still "
                 f"running and would silently serve the WRONG model. Kill it first:\n"
                 f"    lsof -ti tcp:{cfg['port']} | xargs kill")
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


def wait_ready(cfg, proc: subprocess.Popen | None = None) -> None:
    url = f"http://{cfg['host']}:{cfg['port']}/health"
    deadline = time.time() + cfg["server_ready_timeout_s"]
    while time.time() < deadline:
        # If OUR launched server has already exited, a /health=200 can only be some OTHER
        # process — do not trust it (that was the orphan-server mis-serving bug).
        if proc is not None and proc.poll() is not None:
            raise RuntimeError(f"llama-server exited early (code {proc.returncode}) before becoming "
                               f"healthy — refusing to generate against another process on the port.")
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


def generate(client: OpenAI, model_label: str, problems: dict, cfg, openbook: dict | None = None) -> tuple[list, dict]:
    """Return (samples, timing_stats). Greedy, streaming for TTFT.
    openbook (E1 Condition B): {task_id -> full user message} — sent VERBATIM instead of the closed-book
    INSTRUCTION wrap (the artefact already contains chunk1\\n\\nchunk2\\n\\n<INSTRUCTION-wrapped prompt>)."""
    samples, ttfts, tok_rates = [], [], []
    n = len(problems)
    for i, (task_id, p) in enumerate(problems.items(), 1):
        prompt = openbook[task_id] if openbook else INSTRUCTION.format(prompt=p["prompt"])
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
        "ttfts": ttfts,          # raw per-prompt (ms) — for perf-axis mean±std aggregation
        "tok_rates": tok_rates,  # raw per-prompt (tok/s)
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
    # EVALPLUS_MAX_MEMORY_BYTES=-1 → EvalPlus skips resource.setrlimit(), which raises
    # "current limit exceeds maximum limit" (EINVAL) for RLIMIT_AS/RLIMIT_DATA on macOS.
    eval_env = {**os.environ, "EVALPLUS_MAX_MEMORY_BYTES": "-1"}
    proc = subprocess.run(
        [sys.executable, "-m", "evalplus.evaluate", "--dataset", "humaneval", "--samples", str(target)],
        capture_output=True, text=True, env=eval_env,
    )
    out = proc.stdout + "\n" + proc.stderr
    print(out)
    rates = [float(x) for x in re.findall(r"pass@1\s*[:=]\s*([0-9.]+)", out)]
    base = rates[0] if len(rates) >= 1 else None
    plus = rates[1] if len(rates) >= 2 else base
    return base, plus


def _mean_std(xs) -> tuple[float | None, float | None]:
    import statistics
    xs = [x for x in xs if x is not None]
    if not xs:
        return (None, None)
    m = round(statistics.mean(xs), 1)
    s = round(statistics.pstdev(xs), 1) if len(xs) > 1 else 0.0
    return (m, s)


def _median(xs) -> float | None:
    import statistics
    xs = [x for x in xs if x is not None]
    return round(statistics.median(xs), 1) if xs else None


def run_perf(cfg, client, problems, out, device, args, openbook: dict | None = None) -> None:
    """Performance axis: for each (model x quant), run N prompts x K repeats against a warm
    server, measuring tok/s + TTFT (mean±std over all N*K generations), peak RSS, and mean power via
    the per-tier software route (Jetson tegrastats VDD_IN; Pi 5 vcgencmd PMIC rail-sum; Mac powermetrics
    SoC domains, needs root). NO evalplus scoring (quality is the Mac's job, hardware-independent)."""
    csfx = "" if openbook is None else "_open"
    perf_csv = out / f"perf_results{csfx}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    fields = ["timestamp", "device", "model", "quant", "n_prompts", "repeats",
              "mean_tok_s", "std_tok_s", "median_tok_s",
              "mean_ttft_ms", "std_ttft_ms", "median_ttft_ms",
              "peak_rss_mb", "mean_power_w", "llama_cpp_tag"]
    with perf_csv.open("w", newline="") as f:
        csv.DictWriter(f, fieldnames=fields).writeheader()

    for model in cfg["models"]:
        for quant in model["quants"]:
            tag = f"{model['name']}:{quant['label']}"
            if args.only and args.only != tag:
                continue
            print(f"\n=== PERF {tag}  (N={len(problems)} x {args.perf_repeats} repeats) ===")
            server = rss = pw = None
            try:
                server = launch_server(cfg, model, quant)
                wait_ready(cfg, server)
                rss = RSSSampler(server.pid); rss.start()
                pw = PowerSampler(); pw.start()          # no-op off-Jetson
                # Warm-up: one DISCARDED generation so the cold first-token (model just loaded) does
                # not inflate the recorded TTFT. Pre-registered latency is warm latency; the harness
                # must provably exclude the cold start. (Also record median below, robust to outliers.)
                if problems:
                    print("      [warm-up] discarded generation to prime the server ...")
                    generate(client, quant["label"], dict(list(problems.items())[:1]), cfg, openbook)
                all_tok, all_ttft = [], []
                for r in range(args.perf_repeats):
                    _, stats = generate(client, quant["label"], problems, cfg, openbook)
                    all_tok += stats.get("tok_rates", [])
                    all_ttft += stats.get("ttfts", [])
                rss.stop(); rss.join()
                pw.stop(); pw.join()
                peak = rss.peak_mb
                power = pw.mean_w
                mtok, stok = _mean_std(all_tok)
                mttft, sttft = _mean_std(all_ttft)
                row = {"timestamp": utcstamp(), "device": device, "model": model["name"],
                       "quant": quant["label"], "n_prompts": len(problems), "repeats": args.perf_repeats,
                       "mean_tok_s": mtok, "std_tok_s": stok, "median_tok_s": _median(all_tok),
                       "mean_ttft_ms": mttft, "std_ttft_ms": sttft, "median_ttft_ms": _median(all_ttft),
                       "peak_rss_mb": peak, "mean_power_w": power, "llama_cpp_tag": cfg.get("llama_cpp_tag")}
                with perf_csv.open("a", newline="") as f:
                    csv.DictWriter(f, fieldnames=fields).writerow(row)
                jpt = round(power / _median(all_tok), 3) if power and _median(all_tok) else None
                print(f"    -> tok/s {mtok}±{stok} (med {_median(all_tok)}) | ttft {mttft}±{sttft}ms "
                      f"(med {_median(all_ttft)}) | peak {peak}MB | power {power}W [{pw.backend}] "
                      f"| ~{jpt} J/tok  (n={len(all_tok)})")
            finally:
                if rss and rss.is_alive(): rss.stop()
                if pw and pw.is_alive(): pw.stop()
                if server: stop_server(server)

    print(f"\nDone (perf). Results: {perf_csv}")
    print("Perf axis = latency/memory/power only (no pass@1 — that's the Mac quality axis).")


def accel_provenance() -> dict:
    """Best-effort accelerator/thermal provenance for the manifest (reproducibility): Jetson JetPack/L4T
    release + power mode + jetson_clocks state; Pi PMIC throttle flags. Empty on the Mac. All best-effort
    (missing tools/permission -> field omitted); never fails the run."""
    info = {}
    try:
        rel = Path("/etc/nv_tegra_release")
        if rel.exists():
            info["l4t_release"] = rel.read_text().strip().splitlines()[0]
    except Exception:
        pass
    for key, cmd in [("nvpmodel", ["nvpmodel", "-q"]),
                     ("jetson_clocks", ["jetson_clocks", "--show"]),
                     ("pi_throttled", ["vcgencmd", "get_throttled"]),
                     ("pi_temp", ["vcgencmd", "measure_temp"])]:
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if r.returncode == 0 and r.stdout.strip():
                info[key] = " | ".join(r.stdout.strip().splitlines())[:300]
        except (FileNotFoundError, OSError, subprocess.SubprocessError):
            pass
    return info


# ----------------------------- main -----------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/mac.yaml")
    ap.add_argument("--smoke", action="store_true", help="run only 2 problems to validate the pipeline")
    ap.add_argument("--only", help="restrict to one 'model:quant' (e.g. phi-3-mini-4k-instruct:Q4_K_M)")
    ap.add_argument("--no-manage-server", dest="manage", action="store_false", default=None)
    ap.add_argument("--server-pid", type=int, help="PID of an already-running server (for memory sampling)")
    ap.add_argument("--perf", action="store_true",
                    help="performance axis: latency/memory/power on a small prompt set, N repeats, NO scoring")
    ap.add_argument("--perf-n", type=int, default=10, help="perf: number of prompts (default 10)")
    ap.add_argument("--perf-repeats", type=int, default=3, help="perf: repeats per cell (default 3)")
    ap.add_argument("--condition", choices=["closed", "open", "oracle"], default="closed",
                    help="E1: 'open' = frozen BM25 artefact (Condition B); 'oracle' = E1-R upper-bound "
                         "selection artefact (Probe R2)")
    ap.add_argument("--openbook-artefact", default=None,
                    help="artefact path override; defaults per condition (e1/openbook_prompts.jsonl / "
                         "e1/oracle_prompts.jsonl)")
    args = ap.parse_args()

    cfg = yaml.safe_load(Path(args.config).read_text())
    if args.manage is not None:
        cfg["manage_server"] = args.manage

    # Per-device isolation: results + provenance live under results/<device>/ so machines
    # never clobber each other's files. `device` comes from the per-device config.
    device = str(cfg.get("device", "unknown"))
    out = RESULTS_ROOT / device
    out.mkdir(parents=True, exist_ok=True)

    problems = dict(get_human_eval_plus())
    if args.smoke:
        problems = dict(list(problems.items())[:2])
    elif args.perf:
        problems = dict(list(problems.items())[:args.perf_n])
    mode = ' (SMOKE)' if args.smoke else (f' (PERF {len(problems)}x{args.perf_repeats})' if args.perf else '')
    print(f"Loaded {len(problems)} HumanEval+ problems{mode} | device={device}")

    # E1 Condition B: load the frozen open-book artefact and restrict to the requested problems.
    condition = args.condition
    openbook, openbook_sha = None, None
    if condition != "closed":
        art = Path(args.openbook_artefact or
                   {"open": "e1/openbook_prompts.jsonl", "oracle": "e1/oracle_prompts.jsonl"}[condition])
        allc = {json.loads(l)["task_id"]: json.loads(l)["content"] for l in art.read_text().splitlines()}
        missing = [t for t in problems if t not in allc]
        if missing:
            sys.exit(f"open-book artefact missing {len(missing)} requested problems, e.g. {missing[:3]}")
        openbook = {t: allc[t] for t in problems}
        openbook_sha = hashlib.sha256(art.read_bytes()).hexdigest()
        print(f"  condition={condition.upper()} | artefact {art.name} sha256 {openbook_sha[:16]}… ({len(openbook)} prompts)")

    # Provenance manifest — every recorded run is self-describing (reproducibility).
    vm = psutil.virtual_memory()
    manifest = {
        "device": device, "timestamp": utcstamp(),
        "os": platform.platform(), "processor": platform.processor() or platform.machine(),
        "cpu_count": os.cpu_count(), "ram_gb": round(vm.total / (1024**3), 1),
        "python": platform.python_version(), "llama_cpp_tag": cfg.get("llama_cpp_tag"),
        "config_file": str(args.config), "smoke": args.smoke,
        "condition": condition, "openbook_artefact_sha256": openbook_sha,
        "accelerator": accel_provenance(),   # JetPack/power-mode (Jetson) · throttle/temp (Pi) · {} (Mac)
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print(f"  manifest: {manifest['os']} | {manifest['cpu_count']} cores | {manifest['ram_gb']}GB")

    base_url = f"http://{cfg['host']}:{cfg['port']}/v1"
    client = OpenAI(base_url=base_url, api_key="sk-noauth")

    if args.perf:
        run_perf(cfg, client, problems, out, device, args, openbook)
        return

    csfx = "" if condition == "closed" else f"_{condition}"
    results_csv = out / f"pilot_results{csfx}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    fields = ["timestamp", "device", "model", "quant", "condition", "n", "parse_rate",
              "pass@1_base", "pass@1_plus",
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
                    wait_ready(cfg, server)
                    sampler = RSSSampler(server.pid)
                elif args.server_pid:
                    sampler = RSSSampler(args.server_pid)
                if sampler:
                    sampler.start()

                samples, stats = generate(client, quant["label"], problems, cfg, openbook)

                if sampler:
                    sampler.stop(); sampler.join()
                peak_mb = sampler.peak_mb if sampler else None
                if server:
                    stop_server(server); server = None  # free memory before scoring

                samples_path = out / f"samples_{model['name']}_{quant['label']}{csfx}{'_smoke' if args.smoke else ''}.jsonl"
                with samples_path.open("w") as sf:
                    for s in samples:
                        sf.write(json.dumps(s) + "\n")

                base, plus = score_with_evalplus(samples_path)

                row = {
                    "timestamp": utcstamp(), "device": device, "model": model["name"], "quant": quant["label"],
                    "condition": condition,
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
