# Model file checksums

SHA-256 of every model file the configs reference, recorded per device by `hash_models.py` after the measurement campaign.
The quantised files were made once on the Mac and copied byte-for-byte to the edge devices; agreement across devices is the
evidence that the hashed files are the measured files. Upstream F16 files are the uploader's; quantised files are locally made.

| File | Model | Rung | Size (bytes) | SHA-256 | Devices | Agreement |
|---|---|---|---|---|---|---|
| `Phi-3-mini-4k-instruct-Q2_K.gguf` | phi-3-mini-4k-instruct | Q2_K | 1,508,216,256 | `effa79e1bf7edad39dbe80533baabc395235ba1543976ba3674dde2eb19b8cb3` | viper-jetson, viper-mbp.local, viper-pi5 | all agree |
| `Phi-3-mini-4k-instruct-Q3_K_M.gguf` | phi-3-mini-4k-instruct | Q3_K_M | 1,962,554,304 | `a08b16d6ea8d47fe3b13f6f1ab572590434433441d09d30d494ebcd8bc17002b` | viper-jetson, viper-mbp.local, viper-pi5 | all agree |
| `Phi-3-mini-4k-instruct-Q4_K_M.gguf` | phi-3-mini-4k-instruct | Q4_K_M | 2,396,770,752 | `fcc2c8d0536acea1b8751eb406453a589ba4d98ec549bf520732bee27523bf1d` | viper-jetson, viper-mbp.local, viper-pi5 | all agree |
| `Phi-3-mini-4k-instruct-Q8_0.gguf` | phi-3-mini-4k-instruct | Q8_0 | 4,061,221,824 | `49a323d0b284896256bcb741c5ca60fee85ac8268f9d878cf97bc6cc150340f4` | viper-jetson, viper-mbp.local, viper-pi5 | all agree |
| `Phi-3-mini-4k-instruct-f16.gguf` | phi-3-mini-4k-instruct | F16 | 7,643,296,704 | `f53d06d3c9c7e8a5638d08ec21381f2a39076bb817c8110688a306da3c5fc5a2` | viper-mbp.local | single device |
| `Qwen2.5-Coder-1.5B-Instruct-f16.gguf` | qwen2.5-coder-1.5b-instruct | F16 | 3,093,669,376 | `b10310f9b1ab63bd14b9710e84516e7b18b522079fd0c96812f948f9f817e68d` | viper-jetson, viper-mbp.local, viper-pi5 | all agree |
| `Qwen2.5-Coder-7B-Instruct-f16.gguf` | qwen2.5-coder-7b-instruct | F16 | 15,237,853,696 | `d8e374f171cbf20a79619dc6e0926124c7690497609bc94bdad18ef6a86cdee0` | viper-mbp.local, viper-pi5 | all agree |
| `Qwen_Qwen3-4B-bf16.gguf` | qwen3-4b | F16 | 8,051,285,184 | `52486602bdca589fd1507962537b4fc7fa2f1fc57222fa36a960cf691d4960c8` | viper-mbp.local | single device |
| `phi-3-mini-4k-instruct-imat-Q2_K.gguf` | phi-3-mini-4k-instruct | Q2_K | 1,508,216,576 | `4ca7eab2f9009f448a3cad39a8b55b2eedc827e1039004718501fa100c15529b` | viper-mbp.local | single device |
| `phi-3-mini-4k-instruct-imat-Q3_K_M.gguf` | phi-3-mini-4k-instruct | Q3_K_M | 1,962,554,624 | `b2411783a1d31a3cd6cfaea248759289fb010c4786c7f3ec59ee9613c3f8bfd9` | viper-mbp.local | single device |
| `phi-3-mini-4k-instruct-imat-Q4_K_M.gguf` | phi-3-mini-4k-instruct | Q4_K_M | 2,396,771,072 | `7264532897d48e6a7324f43278622896cc0c8a2e6cebc538f184e2b49c561eab` | viper-mbp.local | single device |
| `qwen2.5-coder-1.5b-e4r2-f16.gguf` | qwen2.5-coder-1.5b-e4 | F16 | 3,093,669,440 | `b10217c20779c4c026a176668b2381cc41cbf32cab9bc317ec54b38eef1ae189` | viper-mbp.local | single device |
| `qwen2.5-coder-1.5b-e5-raft-f16.gguf` | qwen2.5-coder-1.5b-e5 | F16 | 3,093,669,440 | `d858bca82836a67a0f0a5d890cb8c683058aabaa068b450516dbb74310241f24` | viper-mbp.local | single device |
| `qwen2.5-coder-1.5b-instruct-Q2_K.gguf` | qwen2.5-coder-1.5b-instruct | Q2_K | 676,304,896 | `93645bf7197606c78a38fd19cf06963f03fdfdfb1c14341905f8a98b4415e322` | viper-jetson, viper-mbp.local, viper-pi5 | all agree |
| `qwen2.5-coder-1.5b-instruct-Q3_K_M.gguf` | qwen2.5-coder-1.5b-instruct | Q3_K_M | 824,178,688 | `ef9e1312b85b35c376ac5de546529f89f4e3b1fd21f6691d809f3331a4e614dd` | viper-jetson, viper-mbp.local, viper-pi5 | all agree |
| `qwen2.5-coder-1.5b-instruct-Q4_K_M.gguf` | qwen2.5-coder-1.5b-instruct | Q4_K_M | 986,048,512 | `15846378962c6bfad84110d0f8c250f2511e150ba730c03edde69c4f8fc3faab` | viper-jetson, viper-mbp.local, viper-pi5 | all agree |
| `qwen2.5-coder-1.5b-instruct-Q8_0.gguf` | qwen2.5-coder-1.5b-instruct | Q8_0 | 1,646,573,056 | `4a34fa30c9d4dfc244eb4e78ff18c1a751352f6d06e01d21e346dae5fff568ff` | viper-jetson, viper-mbp.local, viper-pi5 | all agree |
| `qwen2.5-coder-1.5b-instruct-imat-Q2_K.gguf` | qwen2.5-coder-1.5b-instruct | Q2_K | 676,305,216 | `e67f0501f079461066906bdb85e5e4ee3262776f88816b616f02a36e7f05e0a3` | viper-jetson, viper-mbp.local, viper-pi5 | all agree |
| `qwen2.5-coder-1.5b-instruct-imat-Q3_K_M.gguf` | qwen2.5-coder-1.5b-instruct | Q3_K_M | 824,179,008 | `91563087e83259ac591b4dc64ec4eb8efd681e31738f58897ed78ac3b70024ae` | viper-mbp.local | single device |
| `qwen2.5-coder-1.5b-instruct-imat-Q4_K_M.gguf` | qwen2.5-coder-1.5b-instruct | Q4_K_M | 986,048,832 | `ed756b2fca29def19fe58a4d81af86b03d1f1956016d15f3b109ea5a013b6d20` | viper-mbp.local, viper-pi5 | all agree |
| `qwen2.5-coder-7b-instruct-Q2_K.gguf` | qwen2.5-coder-7b-instruct | Q2_K | 3,015,940,608 | `0ab9fbec57b2a68ab436d002c7cfdff441aa208d96f39444e975f76fe3664fae` | viper-jetson, viper-mbp.local, viper-pi5 | all agree |
| `qwen2.5-coder-7b-instruct-Q3_K_M.gguf` | qwen2.5-coder-7b-instruct | Q3_K_M | 3,808,391,680 | `404880589e9802953657ff718995ed58c8722a8737ba54aaa9f7ede70005f1cf` | viper-jetson, viper-mbp.local, viper-pi5 | all agree |
| `qwen2.5-coder-7b-instruct-Q4_K_M.gguf` | qwen2.5-coder-7b-instruct | Q4_K_M | 4,683,074,048 | `0e8c54b55a10b64eff7be7f3aa9596dd39b471e399fbbc1469bf36c4e66c7b86` | viper-jetson, viper-mbp.local, viper-pi5 | all agree |
| `qwen2.5-coder-7b-instruct-Q8_0.gguf` | qwen2.5-coder-7b-instruct | Q8_0 | 8,098,525,696 | `f728664193246875d99c7797d2d56a71f5a680963ae6052f1e1fa4d40724c652` | viper-jetson, viper-mbp.local, viper-pi5 | all agree |
| `qwen2.5-coder-7b-instruct-imat-Q2_K.gguf` | qwen2.5-coder-7b-instruct | Q2_K | 3,015,940,896 | `5405a8a2acb7082c149e5d15835825865e33ec746991ce36251ad0948e5d80c7` | viper-jetson, viper-mbp.local | all agree |
| `qwen2.5-coder-7b-instruct-imat-Q4_K_M.gguf` | qwen2.5-coder-7b-instruct | Q4_K_M | 4,683,074,336 | `6a289cd6c8554b784e0b6cf1c2cb78d1a78b7a6c6efd7087776c7d0dcb18ef9e` | viper-mbp.local | single device |

## Per-device records

- `Phi-3-mini-4k-instruct-Q2_K.gguf` on **viper-jetson** (Linux-6.8.12-1021-tegra-aarch64-with-glibc2.39): `effa79e1bf7edad39dbe80533baabc395235ba1543976ba3674dde2eb19b8cb3`, 1,508,216,256 bytes, hashed 2026-10-24T10:56:36Z
- `Phi-3-mini-4k-instruct-Q2_K.gguf` on **viper-mbp.local** (macOS-26.6.2-arm64-arm-64bit): `effa79e1bf7edad39dbe80533baabc395235ba1543976ba3674dde2eb19b8cb3`, 1,508,216,256 bytes, hashed 2026-10-24T10:49:16Z
- `Phi-3-mini-4k-instruct-Q2_K.gguf` on **viper-pi5** (Linux-6.18.39+rpt-rpi-2712-aarch64-with-glibc2.41): `effa79e1bf7edad39dbe80533baabc395235ba1543976ba3674dde2eb19b8cb3`, 1,508,216,256 bytes, hashed 2026-10-24T10:58:03Z
- `Phi-3-mini-4k-instruct-Q3_K_M.gguf` on **viper-jetson** (Linux-6.8.12-1021-tegra-aarch64-with-glibc2.39): `a08b16d6ea8d47fe3b13f6f1ab572590434433441d09d30d494ebcd8bc17002b`, 1,962,554,304 bytes, hashed 2026-10-24T10:56:36Z
- `Phi-3-mini-4k-instruct-Q3_K_M.gguf` on **viper-mbp.local** (macOS-26.6.2-arm64-arm-64bit): `a08b16d6ea8d47fe3b13f6f1ab572590434433441d09d30d494ebcd8bc17002b`, 1,962,554,304 bytes, hashed 2026-10-24T10:49:16Z
- `Phi-3-mini-4k-instruct-Q3_K_M.gguf` on **viper-pi5** (Linux-6.18.39+rpt-rpi-2712-aarch64-with-glibc2.41): `a08b16d6ea8d47fe3b13f6f1ab572590434433441d09d30d494ebcd8bc17002b`, 1,962,554,304 bytes, hashed 2026-10-24T10:58:03Z
- `Phi-3-mini-4k-instruct-Q4_K_M.gguf` on **viper-jetson** (Linux-6.8.12-1021-tegra-aarch64-with-glibc2.39): `fcc2c8d0536acea1b8751eb406453a589ba4d98ec549bf520732bee27523bf1d`, 2,396,770,752 bytes, hashed 2026-10-24T10:56:36Z
- `Phi-3-mini-4k-instruct-Q4_K_M.gguf` on **viper-mbp.local** (macOS-26.6.2-arm64-arm-64bit): `fcc2c8d0536acea1b8751eb406453a589ba4d98ec549bf520732bee27523bf1d`, 2,396,770,752 bytes, hashed 2026-10-24T10:49:16Z
- `Phi-3-mini-4k-instruct-Q4_K_M.gguf` on **viper-pi5** (Linux-6.18.39+rpt-rpi-2712-aarch64-with-glibc2.41): `fcc2c8d0536acea1b8751eb406453a589ba4d98ec549bf520732bee27523bf1d`, 2,396,770,752 bytes, hashed 2026-10-24T10:58:03Z
- `Phi-3-mini-4k-instruct-Q8_0.gguf` on **viper-jetson** (Linux-6.8.12-1021-tegra-aarch64-with-glibc2.39): `49a323d0b284896256bcb741c5ca60fee85ac8268f9d878cf97bc6cc150340f4`, 4,061,221,824 bytes, hashed 2026-10-24T10:56:36Z
- `Phi-3-mini-4k-instruct-Q8_0.gguf` on **viper-mbp.local** (macOS-26.6.2-arm64-arm-64bit): `49a323d0b284896256bcb741c5ca60fee85ac8268f9d878cf97bc6cc150340f4`, 4,061,221,824 bytes, hashed 2026-10-24T10:49:16Z
- `Phi-3-mini-4k-instruct-Q8_0.gguf` on **viper-pi5** (Linux-6.18.39+rpt-rpi-2712-aarch64-with-glibc2.41): `49a323d0b284896256bcb741c5ca60fee85ac8268f9d878cf97bc6cc150340f4`, 4,061,221,824 bytes, hashed 2026-10-24T10:58:03Z
- `Phi-3-mini-4k-instruct-f16.gguf` on **viper-mbp.local** (macOS-26.6.2-arm64-arm-64bit): `f53d06d3c9c7e8a5638d08ec21381f2a39076bb817c8110688a306da3c5fc5a2`, 7,643,296,704 bytes, hashed 2026-10-24T10:49:16Z
- `Qwen2.5-Coder-1.5B-Instruct-f16.gguf` on **viper-jetson** (Linux-6.8.12-1021-tegra-aarch64-with-glibc2.39): `b10310f9b1ab63bd14b9710e84516e7b18b522079fd0c96812f948f9f817e68d`, 3,093,669,376 bytes, hashed 2026-10-24T10:56:36Z
- `Qwen2.5-Coder-1.5B-Instruct-f16.gguf` on **viper-mbp.local** (macOS-26.6.2-arm64-arm-64bit): `b10310f9b1ab63bd14b9710e84516e7b18b522079fd0c96812f948f9f817e68d`, 3,093,669,376 bytes, hashed 2026-10-24T10:49:16Z
- `Qwen2.5-Coder-1.5B-Instruct-f16.gguf` on **viper-pi5** (Linux-6.18.39+rpt-rpi-2712-aarch64-with-glibc2.41): `b10310f9b1ab63bd14b9710e84516e7b18b522079fd0c96812f948f9f817e68d`, 3,093,669,376 bytes, hashed 2026-10-24T10:58:03Z
- `Qwen2.5-Coder-7B-Instruct-f16.gguf` on **viper-mbp.local** (macOS-26.6.2-arm64-arm-64bit): `d8e374f171cbf20a79619dc6e0926124c7690497609bc94bdad18ef6a86cdee0`, 15,237,853,696 bytes, hashed 2026-10-24T10:49:16Z
- `Qwen2.5-Coder-7B-Instruct-f16.gguf` on **viper-pi5** (Linux-6.18.39+rpt-rpi-2712-aarch64-with-glibc2.41): `d8e374f171cbf20a79619dc6e0926124c7690497609bc94bdad18ef6a86cdee0`, 15,237,853,696 bytes, hashed 2026-10-24T10:58:03Z
- `Qwen_Qwen3-4B-bf16.gguf` on **viper-mbp.local** (macOS-26.6.2-arm64-arm-64bit): `52486602bdca589fd1507962537b4fc7fa2f1fc57222fa36a960cf691d4960c8`, 8,051,285,184 bytes, hashed 2026-10-24T10:49:16Z
- `phi-3-mini-4k-instruct-imat-Q2_K.gguf` on **viper-mbp.local** (macOS-26.6.2-arm64-arm-64bit): `4ca7eab2f9009f448a3cad39a8b55b2eedc827e1039004718501fa100c15529b`, 1,508,216,576 bytes, hashed 2026-10-24T10:49:16Z
- `phi-3-mini-4k-instruct-imat-Q3_K_M.gguf` on **viper-mbp.local** (macOS-26.6.2-arm64-arm-64bit): `b2411783a1d31a3cd6cfaea248759289fb010c4786c7f3ec59ee9613c3f8bfd9`, 1,962,554,624 bytes, hashed 2026-10-24T10:49:16Z
- `phi-3-mini-4k-instruct-imat-Q4_K_M.gguf` on **viper-mbp.local** (macOS-26.6.2-arm64-arm-64bit): `7264532897d48e6a7324f43278622896cc0c8a2e6cebc538f184e2b49c561eab`, 2,396,771,072 bytes, hashed 2026-10-24T10:49:16Z
- `qwen2.5-coder-1.5b-e4r2-f16.gguf` on **viper-mbp.local** (macOS-26.6.2-arm64-arm-64bit): `b10217c20779c4c026a176668b2381cc41cbf32cab9bc317ec54b38eef1ae189`, 3,093,669,440 bytes, hashed 2026-10-24T10:49:16Z
- `qwen2.5-coder-1.5b-e5-raft-f16.gguf` on **viper-mbp.local** (macOS-26.6.2-arm64-arm-64bit): `d858bca82836a67a0f0a5d890cb8c683058aabaa068b450516dbb74310241f24`, 3,093,669,440 bytes, hashed 2026-10-24T10:49:16Z
- `qwen2.5-coder-1.5b-instruct-Q2_K.gguf` on **viper-jetson** (Linux-6.8.12-1021-tegra-aarch64-with-glibc2.39): `93645bf7197606c78a38fd19cf06963f03fdfdfb1c14341905f8a98b4415e322`, 676,304,896 bytes, hashed 2026-10-24T10:56:36Z
- `qwen2.5-coder-1.5b-instruct-Q2_K.gguf` on **viper-mbp.local** (macOS-26.6.2-arm64-arm-64bit): `93645bf7197606c78a38fd19cf06963f03fdfdfb1c14341905f8a98b4415e322`, 676,304,896 bytes, hashed 2026-10-24T10:49:16Z
- `qwen2.5-coder-1.5b-instruct-Q2_K.gguf` on **viper-pi5** (Linux-6.18.39+rpt-rpi-2712-aarch64-with-glibc2.41): `93645bf7197606c78a38fd19cf06963f03fdfdfb1c14341905f8a98b4415e322`, 676,304,896 bytes, hashed 2026-10-24T10:58:03Z
- `qwen2.5-coder-1.5b-instruct-Q3_K_M.gguf` on **viper-jetson** (Linux-6.8.12-1021-tegra-aarch64-with-glibc2.39): `ef9e1312b85b35c376ac5de546529f89f4e3b1fd21f6691d809f3331a4e614dd`, 824,178,688 bytes, hashed 2026-10-24T10:56:36Z
- `qwen2.5-coder-1.5b-instruct-Q3_K_M.gguf` on **viper-mbp.local** (macOS-26.6.2-arm64-arm-64bit): `ef9e1312b85b35c376ac5de546529f89f4e3b1fd21f6691d809f3331a4e614dd`, 824,178,688 bytes, hashed 2026-10-24T10:49:16Z
- `qwen2.5-coder-1.5b-instruct-Q3_K_M.gguf` on **viper-pi5** (Linux-6.18.39+rpt-rpi-2712-aarch64-with-glibc2.41): `ef9e1312b85b35c376ac5de546529f89f4e3b1fd21f6691d809f3331a4e614dd`, 824,178,688 bytes, hashed 2026-10-24T10:58:03Z
- `qwen2.5-coder-1.5b-instruct-Q4_K_M.gguf` on **viper-jetson** (Linux-6.8.12-1021-tegra-aarch64-with-glibc2.39): `15846378962c6bfad84110d0f8c250f2511e150ba730c03edde69c4f8fc3faab`, 986,048,512 bytes, hashed 2026-10-24T10:56:36Z
- `qwen2.5-coder-1.5b-instruct-Q4_K_M.gguf` on **viper-mbp.local** (macOS-26.6.2-arm64-arm-64bit): `15846378962c6bfad84110d0f8c250f2511e150ba730c03edde69c4f8fc3faab`, 986,048,512 bytes, hashed 2026-10-24T10:49:16Z
- `qwen2.5-coder-1.5b-instruct-Q4_K_M.gguf` on **viper-pi5** (Linux-6.18.39+rpt-rpi-2712-aarch64-with-glibc2.41): `15846378962c6bfad84110d0f8c250f2511e150ba730c03edde69c4f8fc3faab`, 986,048,512 bytes, hashed 2026-10-24T10:58:03Z
- `qwen2.5-coder-1.5b-instruct-Q8_0.gguf` on **viper-jetson** (Linux-6.8.12-1021-tegra-aarch64-with-glibc2.39): `4a34fa30c9d4dfc244eb4e78ff18c1a751352f6d06e01d21e346dae5fff568ff`, 1,646,573,056 bytes, hashed 2026-10-24T10:56:36Z
- `qwen2.5-coder-1.5b-instruct-Q8_0.gguf` on **viper-mbp.local** (macOS-26.6.2-arm64-arm-64bit): `4a34fa30c9d4dfc244eb4e78ff18c1a751352f6d06e01d21e346dae5fff568ff`, 1,646,573,056 bytes, hashed 2026-10-24T10:49:16Z
- `qwen2.5-coder-1.5b-instruct-Q8_0.gguf` on **viper-pi5** (Linux-6.18.39+rpt-rpi-2712-aarch64-with-glibc2.41): `4a34fa30c9d4dfc244eb4e78ff18c1a751352f6d06e01d21e346dae5fff568ff`, 1,646,573,056 bytes, hashed 2026-10-24T10:58:03Z
- `qwen2.5-coder-1.5b-instruct-imat-Q2_K.gguf` on **viper-jetson** (Linux-6.8.12-1021-tegra-aarch64-with-glibc2.39): `e67f0501f079461066906bdb85e5e4ee3262776f88816b616f02a36e7f05e0a3`, 676,305,216 bytes, hashed 2026-10-24T10:56:36Z
- `qwen2.5-coder-1.5b-instruct-imat-Q2_K.gguf` on **viper-mbp.local** (macOS-26.6.2-arm64-arm-64bit): `e67f0501f079461066906bdb85e5e4ee3262776f88816b616f02a36e7f05e0a3`, 676,305,216 bytes, hashed 2026-10-24T10:49:16Z
- `qwen2.5-coder-1.5b-instruct-imat-Q2_K.gguf` on **viper-pi5** (Linux-6.18.39+rpt-rpi-2712-aarch64-with-glibc2.41): `e67f0501f079461066906bdb85e5e4ee3262776f88816b616f02a36e7f05e0a3`, 676,305,216 bytes, hashed 2026-10-24T10:58:03Z
- `qwen2.5-coder-1.5b-instruct-imat-Q3_K_M.gguf` on **viper-mbp.local** (macOS-26.6.2-arm64-arm-64bit): `91563087e83259ac591b4dc64ec4eb8efd681e31738f58897ed78ac3b70024ae`, 824,179,008 bytes, hashed 2026-10-24T10:49:16Z
- `qwen2.5-coder-1.5b-instruct-imat-Q4_K_M.gguf` on **viper-mbp.local** (macOS-26.6.2-arm64-arm-64bit): `ed756b2fca29def19fe58a4d81af86b03d1f1956016d15f3b109ea5a013b6d20`, 986,048,832 bytes, hashed 2026-10-24T10:49:16Z
- `qwen2.5-coder-1.5b-instruct-imat-Q4_K_M.gguf` on **viper-pi5** (Linux-6.18.39+rpt-rpi-2712-aarch64-with-glibc2.41): `ed756b2fca29def19fe58a4d81af86b03d1f1956016d15f3b109ea5a013b6d20`, 986,048,832 bytes, hashed 2026-10-24T10:58:03Z
- `qwen2.5-coder-7b-instruct-Q2_K.gguf` on **viper-jetson** (Linux-6.8.12-1021-tegra-aarch64-with-glibc2.39): `0ab9fbec57b2a68ab436d002c7cfdff441aa208d96f39444e975f76fe3664fae`, 3,015,940,608 bytes, hashed 2026-10-24T10:56:36Z
- `qwen2.5-coder-7b-instruct-Q2_K.gguf` on **viper-mbp.local** (macOS-26.6.2-arm64-arm-64bit): `0ab9fbec57b2a68ab436d002c7cfdff441aa208d96f39444e975f76fe3664fae`, 3,015,940,608 bytes, hashed 2026-10-24T10:49:16Z
- `qwen2.5-coder-7b-instruct-Q2_K.gguf` on **viper-pi5** (Linux-6.18.39+rpt-rpi-2712-aarch64-with-glibc2.41): `0ab9fbec57b2a68ab436d002c7cfdff441aa208d96f39444e975f76fe3664fae`, 3,015,940,608 bytes, hashed 2026-10-24T10:58:03Z
- `qwen2.5-coder-7b-instruct-Q3_K_M.gguf` on **viper-jetson** (Linux-6.8.12-1021-tegra-aarch64-with-glibc2.39): `404880589e9802953657ff718995ed58c8722a8737ba54aaa9f7ede70005f1cf`, 3,808,391,680 bytes, hashed 2026-10-24T10:56:36Z
- `qwen2.5-coder-7b-instruct-Q3_K_M.gguf` on **viper-mbp.local** (macOS-26.6.2-arm64-arm-64bit): `404880589e9802953657ff718995ed58c8722a8737ba54aaa9f7ede70005f1cf`, 3,808,391,680 bytes, hashed 2026-10-24T10:49:16Z
- `qwen2.5-coder-7b-instruct-Q3_K_M.gguf` on **viper-pi5** (Linux-6.18.39+rpt-rpi-2712-aarch64-with-glibc2.41): `404880589e9802953657ff718995ed58c8722a8737ba54aaa9f7ede70005f1cf`, 3,808,391,680 bytes, hashed 2026-10-24T10:58:03Z
- `qwen2.5-coder-7b-instruct-Q4_K_M.gguf` on **viper-jetson** (Linux-6.8.12-1021-tegra-aarch64-with-glibc2.39): `0e8c54b55a10b64eff7be7f3aa9596dd39b471e399fbbc1469bf36c4e66c7b86`, 4,683,074,048 bytes, hashed 2026-10-24T10:56:36Z
- `qwen2.5-coder-7b-instruct-Q4_K_M.gguf` on **viper-mbp.local** (macOS-26.6.2-arm64-arm-64bit): `0e8c54b55a10b64eff7be7f3aa9596dd39b471e399fbbc1469bf36c4e66c7b86`, 4,683,074,048 bytes, hashed 2026-10-24T10:49:16Z
- `qwen2.5-coder-7b-instruct-Q4_K_M.gguf` on **viper-pi5** (Linux-6.18.39+rpt-rpi-2712-aarch64-with-glibc2.41): `0e8c54b55a10b64eff7be7f3aa9596dd39b471e399fbbc1469bf36c4e66c7b86`, 4,683,074,048 bytes, hashed 2026-10-24T10:58:03Z
- `qwen2.5-coder-7b-instruct-Q8_0.gguf` on **viper-jetson** (Linux-6.8.12-1021-tegra-aarch64-with-glibc2.39): `f728664193246875d99c7797d2d56a71f5a680963ae6052f1e1fa4d40724c652`, 8,098,525,696 bytes, hashed 2026-10-24T10:56:36Z
- `qwen2.5-coder-7b-instruct-Q8_0.gguf` on **viper-mbp.local** (macOS-26.6.2-arm64-arm-64bit): `f728664193246875d99c7797d2d56a71f5a680963ae6052f1e1fa4d40724c652`, 8,098,525,696 bytes, hashed 2026-10-24T10:49:16Z
- `qwen2.5-coder-7b-instruct-Q8_0.gguf` on **viper-pi5** (Linux-6.18.39+rpt-rpi-2712-aarch64-with-glibc2.41): `f728664193246875d99c7797d2d56a71f5a680963ae6052f1e1fa4d40724c652`, 8,098,525,696 bytes, hashed 2026-10-24T10:58:03Z
- `qwen2.5-coder-7b-instruct-imat-Q2_K.gguf` on **viper-jetson** (Linux-6.8.12-1021-tegra-aarch64-with-glibc2.39): `5405a8a2acb7082c149e5d15835825865e33ec746991ce36251ad0948e5d80c7`, 3,015,940,896 bytes, hashed 2026-10-24T10:56:36Z
- `qwen2.5-coder-7b-instruct-imat-Q2_K.gguf` on **viper-mbp.local** (macOS-26.6.2-arm64-arm-64bit): `5405a8a2acb7082c149e5d15835825865e33ec746991ce36251ad0948e5d80c7`, 3,015,940,896 bytes, hashed 2026-10-24T10:49:16Z
- `qwen2.5-coder-7b-instruct-imat-Q4_K_M.gguf` on **viper-mbp.local** (macOS-26.6.2-arm64-arm-64bit): `6a289cd6c8554b784e0b6cf1c2cb78d1a78b7a6c6efd7087776c7d0dcb18ef9e`, 4,683,074,336 bytes, hashed 2026-10-24T10:49:16Z
