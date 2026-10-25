# Full-ladder cross-device replication (xdev-full, HumanEval+, n = 164, closed-book, greedy)

| Model | Rung | Device | pass@1 | Drop vs own F16 (pp) | Identical to Mac | Flips vs Mac (b: Mac pass, device fail; c: reverse) | McNemar p |
|---|---|---|---|---|---|---|---|
| phi-3-mini-4k-instruct | F16 | mac | 0.646 | +0.0 | reference |  |  |
| phi-3-mini-4k-instruct | Q8_0 | mac | 0.628 | +1.8 | reference |  |  |
| phi-3-mini-4k-instruct | Q4_K_M | mac | 0.549 | +9.8 | reference |  |  |
| phi-3-mini-4k-instruct | Q3_K_M | mac | 0.427 | +22.0 | reference |  |  |
| phi-3-mini-4k-instruct | Q2_K | mac | 0.220 | +42.7 | reference |  |  |
| qwen2.5-coder-1.5b-instruct | F16 | mac | 0.610 | +0.0 | reference |  |  |
| qwen2.5-coder-1.5b-instruct | F16 | jetson | 0.610 | +0.0 | 1.000 | b = 0, c = 0 | 1.000 |
| qwen2.5-coder-1.5b-instruct | F16 | pi5 | 0.616 | +0.0 | 0.976 | b = 0, c = 1 | 1.000 |
| qwen2.5-coder-1.5b-instruct | Q8_0 | mac | 0.616 | -0.6 | reference |  |  |
| qwen2.5-coder-1.5b-instruct | Q8_0 | jetson | 0.598 | +1.2 | 0.927 | b = 3, c = 0 | 0.250 |
| qwen2.5-coder-1.5b-instruct | Q8_0 | pi5 | 0.616 | +0.0 | 0.945 | b = 0, c = 0 | 1.000 |
| qwen2.5-coder-1.5b-instruct | Q4_K_M | mac | 0.616 | -0.6 | reference |  |  |
| qwen2.5-coder-1.5b-instruct | Q4_K_M | jetson | 0.616 | -0.6 | 0.841 | b = 3, c = 3 | 1.000 |
| qwen2.5-coder-1.5b-instruct | Q4_K_M | pi5 | 0.628 | -1.2 | 0.720 | b = 2, c = 4 | 0.688 |
| qwen2.5-coder-1.5b-instruct | Q3_K_M | mac | 0.585 | +2.4 | reference |  |  |
| qwen2.5-coder-1.5b-instruct | Q3_K_M | jetson | 0.585 | +2.4 | 0.884 | b = 1, c = 1 | 1.000 |
| qwen2.5-coder-1.5b-instruct | Q3_K_M | pi5 | 0.591 | +2.4 | 0.817 | b = 2, c = 3 | 1.000 |
| qwen2.5-coder-1.5b-instruct | Q2_K | mac | 0.384 | +22.6 | reference |  |  |
| qwen2.5-coder-1.5b-instruct | Q2_K | jetson | 0.360 | +25.0 | 0.689 | b = 5, c = 1 | 0.219 |
| qwen2.5-coder-1.5b-instruct | Q2_K | pi5 | 0.348 | +26.8 | 0.585 | b = 10, c = 4 | 0.180 |
