# Benchmarks

AMD Radeon RX 580 (RADV POLARIS10, 8192 MiB, 256 GB/s theoretical)
llama.cpp build 9544 (98d5e8ba8), Vulkan backend
Intel Core i5-7600K @ 3.80GHz, 4 threads
CachyOS (Arch Linux)

All models Q4_K_M unless noted. KV cache: q4_0. Flash attention: on.
Prompt: ~2100 tokens (system + padded instruction). Generation: 512 tokens, temp=0.
Bandwidth utilization = `tg_tps × model_size_gb / 256`.

## Single-user generation (batch=1)

| model | size | ctx | prompt_tok | completion_tok | elapsed_s | pp_tps | tg_tps (avg) | bw util % |
|---|---|---|---|---|---|---|---|---|
| llama-3.2-3B-Q4_K_M | 2.02 | 122368 | 2129 | 512 | 12.75 | 476.41 | 61.84 | 48.8 |
| Qwen3.5-4B-Q4_K_M | 2.71 | 262144 | 2130 | 512 | 17.82 | 358.02 | 40.66 | 43.0 |
| gemma-4-E4B-Q4_K_M | 4.98 | 131072 | 2128 | 512 | 21.42 | 307.37 | 35.03 | 68.1 |
| Qwen3.5-9B-Q4_K_M | 5.63 | 86272 | 2130 | 512 | 28.52 | 204.65 | 25.86 | 56.9 |

## Generation throughput vs model size

| Model | File size | tg_tps | GB/s read | BW util |
|---|---|---|---|---|
| llama-3.2-3B Q4_K_M | 2.02 GB | 61.84 | 124.9 | 48.8% |
| Qwen3.5-4B Q4_K_M | 2.71 GB | 40.66 | 110.2 | 43.0% |
| gemma-4-E4B Q4_K_M | 4.98 GB | 35.03 | 174.3 | 68.1% |
| Qwen3.5-9B Q4_K_M | 5.63 GB | 25.86 | 145.6 | 56.9% |

Gemma achieves the highest utilization (68.1%) per GB transferred, suggesting it benefits from architecture-specific Vulkan optimizations.

## Prompt processing throughput

| Model | pp_tps |
|---|---|
| llama-3.2-3B Q4_K_M | 476.41 |
| Qwen3.5-4B Q4_K_M | 358.02 |
| gemma-4-E4B Q4_K_M | 307.37 |
| Qwen3.5-9B Q4_K_M | 204.65 |

## Quantization comparison (Qwen3.5-4B)

Data from `llama-bench` (raw Vulkan, no HTTP server overhead):

| Quant | Size (llama-bench) | tg128 | BW util |
|---|---|---|---|
| Q4_K_M | 2.51 GiB | 47.16 | 46.2% |
| Q8_0 | 4.16 GiB | 38.11 | 61.9% |

Q8_0 moves 66% more data but only drops 19% throughput — utilization climbs ~16pp because Polaris spends fewer ALU cycles dequantizing (no int4 dot product hardware).

## Speculative decoding (MTP)

Qwen3.5-4B Q4_K_M-MTP tested with `--spec-type draft-mtp --spec-draft-n-max 2` (temp=0):

| Variant | tg_tps | Diff |
|---|---|---|
| Non-MTP | 40.66 | baseline |
| MTP (temp=0) | 38.39 | -5.6% |

MTP does not help on Polaris. The verification pass overhead exceeds any batching benefit, even at greedy sampling where acceptance rate should be near 100%. In real-world use (Open WebUI, temp=1.0, penalties), acceptance rate was measured at 41.7% — well below the break-even threshold.

## Environment

- GPU: AMD Radeon RX 580 (Polaris 10, 8 GB GDDR5, 256 GB/s)
- Driver: RADV (amdgpu) via Vulkan
- CPU: Intel Core i5-7600K (4C/4T, 3.80 GHz)
- RAM: 16 GB DDR4
- OS: CachyOS (Arch Linux)
- llama.cpp: commit 98d5e8ba8 (build 9544)
