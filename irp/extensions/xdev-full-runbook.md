# Runbook: full-ladder cross-device replication (xdev-full)

Protocol: `irp/extensions/xdev-full-protocol.md` (registered 2026-10-24). Nothing below changes a registered file; every
output carries the `full164` tag. Order: Mac first (fast, gives the reference), then Jetson, then Pi 5. Each device commits
its own `xdev_*_full164.json` files; scoring happens once, on the Mac, after everything is pulled.

## 0. On every device, before generating
```bash
cd <repo>/proposal-dev/pilot
git pull
source .venv/bin/activate            # the harness venv (openai, evalplus, psutil, pyyaml, requests)
ls local/models/qwen2.5-coder-1.5b-instruct local/models/phi-3-mini-4k-instruct   # the GGUF files must be present
lsof -i :8080 || true                # nothing should be listening; kill a stale llama-server if one is
```

## 1. Mac (reference; about 30 to 60 minutes)
```bash
cd <repo>/proposal-dev/pilot && source .venv/bin/activate
for r in F16 Q8_0 Q4_K_M Q3_K_M Q2_K; do
  python cross_device_check.py configs/mac.yaml qwen2.5-coder-1.5b-instruct $r 164 closed full164
done
for r in F16 Q8_0 Q4_K_M Q3_K_M Q2_K; do
  python cross_device_check.py configs/mac.yaml phi-3-mini-4k-instruct $r 164 closed full164
done
git add results/mac/xdev_*_full164.json && git commit -m "xdev-full: Mac reference generations (164 problems, both ladders)" && git push
```

## 2. Jetson (about 2 to 3 hours; run detached)
```bash
cd <repo>/proposal-dev/pilot && source .venv/bin/activate
nohup bash -c '
for r in F16 Q8_0 Q4_K_M Q3_K_M Q2_K; do
  python cross_device_check.py configs/jetson.yaml qwen2.5-coder-1.5b-instruct $r 164 closed full164
done
for r in Q8_0 Q4_K_M Q3_K_M Q2_K; do
  python cross_device_check.py configs/jetson.yaml phi-3-mini-4k-instruct $r 164 closed full164
done' > results/jetson/xdev_full164.log 2>&1 &
tail -f results/jetson/xdev_full164.log      # Ctrl-C leaves the job running
```
When it finishes (nine `wrote ... (164 solutions)` lines in the log):
```bash
git add results/jetson/xdev_*_full164.json results/jetson/xdev_full164.log
git commit -m "xdev-full: Jetson generations (164 problems)" && git push
```

## 3. Pi 5 (Qwen ladder overnight; Phi-3 optional, a further night)
```bash
cd <repo>/proposal-dev/pilot && source .venv/bin/activate
nohup bash -c '
for r in F16 Q8_0 Q4_K_M Q3_K_M Q2_K; do
  python cross_device_check.py configs/pi5.yaml qwen2.5-coder-1.5b-instruct $r 164 closed full164
done' > results/pi5/xdev_full164.log 2>&1 &
```
Optional second night (decides nothing on the deployment map, see the protocol):
```bash
nohup bash -c '
for r in Q8_0 Q4_K_M Q3_K_M Q2_K; do
  python cross_device_check.py configs/pi5.yaml phi-3-mini-4k-instruct $r 164 closed full164
done' > results/pi5/xdev_full164_phi.log 2>&1 &
```
Then commit and push as for the Jetson.

## 4. Score, on the Mac, after pulling every device's files
```bash
cd <repo>/proposal-dev/pilot && source .venv/bin/activate && git pull
python score_xdev_full.py
git add results/xdev_full164_summary.json results/xdev_full164_summary.md
git commit -m "xdev-full: scored on the Mac" && git push
```
The script prints one row per model, rung and device: pass@1, drop from own F16, identity against the Mac, flips b and c
against the Mac, and the McNemar p. The interpretation map in the protocol says what each row means.

## 5. Checks worth doing as you go
- The Mac rows should reproduce the September pass@1 values in Table 4.1 exactly (0.610, 0.616, 0.616, 0.585, 0.384;
  0.646, 0.628, 0.549, 0.427, 0.220). If any differ, stop and report it: within-device determinism is itself a claim.
- A run that stops early leaves a partial JSON; delete it and rerun that rung.
- Do not run the harness and a `--perf` run at the same time on a device.

## 6. Hand back
Tell me when the summary is pushed. I will pull, read it against the interpretation map, write §4.2 and Table D.5 to
match (dated as a post-registration validation), rebuild the document and refresh the artefact zips.
