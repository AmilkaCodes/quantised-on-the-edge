# xdev-full: full-ladder cross-device replication of the quality axis — analysis record

**Protocol:** `irp/extensions/xdev-full-protocol.md` (registered 2026-10-24, commit 267ecb8). **Data:** `proposal-dev/pilot/results/<tier>/xdev_*_full164.json`;
scored on the Mac by `score_xdev_full.py` → `results/xdev_full164_summary.{json,md}` (commit a58185d, 2026-10-25). **Status:** Qwen complete on three tiers (15 cells);
Phi-3 Mac reference complete (5 cells); Phi-3 Jetson NOT MEASURED — CAPACITY (deviation recorded in the protocol); Phi-3 Pi 5 optional, pending.
**Not yet in the report** (document c, 2026-10-24, submitted for the formative as is); to be written into §3.3.1, §4.2, §4.4, §5.3, Table D.5 and Appendix A afterwards.

## 1. Determinism check: the Mac reproduces September exactly
All ten Mac reference cells reproduce Table 4.1 to the third decimal (Qwen 0.610, 0.616, 0.616, 0.585, 0.384; Phi-3 0.646, 0.628, 0.549, 0.427, 0.220).
Within-device greedy decoding is deterministic over a five-week gap and a re-run through a different driver script.

## 2. Reading against the registered interpretation map (Qwen2.5-Coder-1.5B, n = 164)

| Rung | Mac | Jetson (identity; flips b/c; p) | Pi 5 (identity; flips b/c; p) | Map verdict |
|---|---|---|---|---|
| F16 | 0.610 | 0.610 (1.000; 0/0; 1.00) | 0.616 (0.976; 0/1; 1.00) | holds |
| Q8_0 | 0.616 | 0.598 (0.927; 3/0; 0.25) | 0.616 (0.945; 0/0; 1.00) | holds (Jetson −1.8 points, within two) |
| Q4_K_M | 0.616 | 0.616 (0.841; 3/3; 1.00) | 0.628 (0.720; 2/4; 0.69) | holds; the † flag at this rung is resolved by measurement |
| Q3_K_M | 0.585 | 0.585 (0.884; 1/1; 1.00) | 0.591 (0.817; 2/3; 1.00) | holds; the † flag at this rung is resolved by measurement |
| Q2_K | 0.384 | 0.360 (0.689; 5/1; 0.22) | 0.348 (0.585; 10/4; 0.18) | **weak form fails on the pass@1 criterion** (−2.4 and −3.6 points; flips not significant) |

Per the map, Q2_K is re-stated per tier: drop from own F16 is 22.6 (Mac), 25.0 (Jetson), 26.8 (Pi 5). Every tier's interval lies wholly beyond the
five-point margin, so the registered verdict (collapsed) is unchanged on every tier; the collapse is deeper on the edge tiers, not shallower. No cell
of the deployment map changes for Qwen.

**The pattern that is new:** output identity against the Mac falls monotonically with precision (Jetson 1.000 → 0.927 → 0.841 → 0.884 → 0.689;
Pi 5 0.976 → 0.945 → 0.720 → 0.817 → 0.585), and the net flip direction at Q2_K is Mac-pass/device-fail (b > c on both tiers). The backends' low-bit
kernels diverge more the fewer bits they share, and the divergence costs correctness rather than adding it. This extends Yuan et al.'s cross-configuration
non-determinism to the precision axis and is reportable as a finding, with the caveat that the flips are not individually significant.

## 3. Phi-3 on the Jetson: not measured, and why that is itself a result
Two attempts (default slots; `--parallel 1`) failed identically: the server was OOM-killed a few problems into every cell. The slot hypothesis was tested
and falsified (post-load headroom 862 against 894 MB); the mechanism is per-generation allocation of roughly 300 MB that is not released, against under
1 GB of headroom after loading Phi-3 Q8_0 (4.06 GB) with the CUDA runtime on a 7.5 GB usable tier, at the registered 4,096 context. Details and the
A/B probe are in the protocol's Deviations section. The solutions completed before each kill are byte-identical to the Mac's.

Consequence for the report: Figure 4.4 marks Phi-3 Q8_0 on the Jetson as deployable on the strength of the ten-prompt performance cells, which the
server's prefix cache serves from one slot. That verdict stands for short interactive use and must carry a stated condition: the 8 GB tier could not
sustain a 164-problem batch at full context. This is a capacity qualification, not a quality result, and belongs in §4.4 and §5.4 beside the Phi-3 Q8_0
recommendation.

## 4. What changes in the report when this is written in (estimated +80 words, funded)
- §3.3.1: the two registered checks plus the full-ladder replication (dated) for Qwen on both edge tiers.
- §4.2: rewritten around the table above; the identity gradient; Q2_K re-stated per tier; Qwen's two † flags resolved; Phi-3's flags remain (not cross-checked).
- §4.4 and §5.4: the Phi-3 Q8_0 Jetson condition (short interactive use, not sustained batch).
- §5.3 Reliability: "checked for one model at two rungs" becomes "checked for the specialised model at every rung on both edge tiers; the general model's
  edge verdicts rest on the Mac measurement and on a tier that could not hold it for a full run".
- Table D.5: a companion table with the 15 Qwen cells; Appendix A: the xdev-full entry with its deviation.
- Glossary: nothing new.
