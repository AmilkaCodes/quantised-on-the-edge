#!/usr/bin/env python3
"""Record SHA-256 checksums of every model file the configs reference, per device, and report cross-device agreement.

Run it from this folder on each device that holds model files (Mac, Jetson, Pi 5):

    python3 hash_models.py            # hashes every GGUF named in configs/*.yaml that exists on this machine
    python3 hash_models.py extra.gguf # ... plus any explicit paths

It appends this device's entries to CHECKSUMS.json (keyed by file name, one record per device) and regenerates
CHECKSUMS.md with a column that says whether every device that holds a file reports the same hash. Commit both files
and pull them on the next device before running there, so the JSON merges rather than forks.

The quantised files were produced once on the Mac and copied byte-for-byte to the edge devices (the cross-device checks of
Table D.5 depend on that), so matching hashes across devices are evidence that the files hashed here are the files measured.
No dependency beyond the standard library; PyYAML is used when present.
"""
import hashlib, json, os, platform, re, socket, sys, datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT_JSON = HERE / "CHECKSUMS.json"; OUT_MD = HERE / "CHECKSUMS.md"


def referenced_files():
    """(config name, model id, label, path) for every model file named in configs/*.yaml."""
    out = []
    try:
        import yaml
    except ImportError:
        yaml = None
    for cfg in sorted((HERE / "configs").glob("*.yaml")):
        text = cfg.read_text(encoding="utf-8")
        if yaml is not None:
            try:
                d = yaml.safe_load(text) or {}
                for m in d.get("models", []) or []:
                    gdir = m.get("gguf_dir", ""); mid = m.get("id") or m.get("name") or Path(gdir).name
                    for q in m.get("quants", []) or m.get("ladder", []) or []:
                        if isinstance(q, dict) and q.get("file"):
                            out.append((cfg.name, mid, q.get("label", ""), (HERE / gdir / q["file"])))
                continue
            except Exception:
                pass
        gdir = ""
        for ln in text.splitlines():  # fallback: regex over the two line shapes the configs use
            m = re.search(r'gguf_dir:\s*"([^"]+)"', ln)
            if m: gdir = m.group(1); continue
            m = re.search(r'label:\s*"([^"]+)".*?file:\s*"([^"]+)"', ln)
            if m and gdir: out.append((cfg.name, Path(gdir).name, m.group(1), HERE / gdir / m.group(2)))
    return out


def sha256(path, bufsize=1 << 24):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(bufsize), b""):
            h.update(chunk)
    return h.hexdigest()


def main(extra):
    device = socket.gethostname(); stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    plat = platform.platform()
    db = json.loads(OUT_JSON.read_text(encoding="utf-8")) if OUT_JSON.exists() else {"files": {}}
    seen = {}
    for cfg, mid, label, p in referenced_files():
        p = p.resolve()
        if not p.exists():
            seen.setdefault(p.name, None); continue
        if p.name in seen and seen[p.name]: continue
        print(f"hashing {p.name} ({p.stat().st_size / 1e9:.2f} GB) ...", flush=True)
        seen[p.name] = {"sha256": sha256(p), "size_bytes": p.stat().st_size, "model": mid, "label": label, "config": cfg, "path": str(p)}
    for e in extra:
        p = Path(e).resolve()
        if p.exists():
            print(f"hashing {p.name} ({p.stat().st_size / 1e9:.2f} GB) ...", flush=True)
            seen[p.name] = {"sha256": sha256(p), "size_bytes": p.stat().st_size, "model": "", "label": "", "config": "explicit", "path": str(p)}
    n = 0
    for name, rec in seen.items():
        if rec is None: continue
        entry = db["files"].setdefault(name, {"model": rec["model"], "label": rec["label"], "first_config": rec["config"], "devices": {}})
        entry["devices"][device] = {"sha256": rec["sha256"], "size_bytes": rec["size_bytes"], "hashed_at": stamp, "platform": plat, "path": rec["path"]}
        n += 1
    OUT_JSON.write_text(json.dumps(db, indent=2, sort_keys=True), encoding="utf-8")
    missing = sorted(k for k, v in seen.items() if v is None)
    # Markdown report
    lines = ["# Model file checksums", "",
             "SHA-256 of every model file the configs reference, recorded per device by `hash_models.py` after the measurement campaign.",
             "The quantised files were made once on the Mac and copied byte-for-byte to the edge devices; agreement across devices is the",
             "evidence that the hashed files are the measured files. Upstream F16 files are the uploader's; quantised files are locally made.", "",
             "| File | Model | Rung | Size (bytes) | SHA-256 | Devices | Agreement |", "|---|---|---|---|---|---|---|"]
    for name in sorted(db["files"]):
        e = db["files"][name]; devs = e["devices"]
        hashes = {d["sha256"] for d in devs.values()}
        agree = "single device" if len(devs) == 1 else ("all agree" if len(hashes) == 1 else "**MISMATCH**")
        any_dev = next(iter(devs.values()))
        lines.append(f"| `{name}` | {e.get('model','')} | {e.get('label','')} | {any_dev['size_bytes']:,} | `{sorted(hashes)[0]}`"
                     + ("" if len(hashes) == 1 else " (+%d other)" % (len(hashes) - 1)) + f" | {', '.join(sorted(devs))} | {agree} |")
    lines += ["", "## Per-device records", ""]
    for name in sorted(db["files"]):
        for dev, d in sorted(db["files"][name]["devices"].items()):
            lines.append(f"- `{name}` on **{dev}** ({d['platform']}): `{d['sha256']}`, {d['size_bytes']:,} bytes, hashed {d['hashed_at']}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\n{n} files hashed on {device}; {len(db['files'])} files in CHECKSUMS.json; report in CHECKSUMS.md")
    if missing: print("referenced by a config but not present on this device:", ", ".join(missing))


if __name__ == "__main__":
    main(sys.argv[1:])
