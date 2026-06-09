# Benchmarks

AMD Radeon RX 580 (RADV POLARIS10, 8192 MiB, 256 GB/s theoretical)
llama.cpp build 9544 (98d5e8ba8), Vulkan backend
Intel Core i5-7600K @ 3.80GHz, 4 threads
CachyOS (Arch Linux)

All models Q4_K_M unless noted. KV cache: q4_0. Flash attention: on.
Prompt: ~2130 tokens (system + padded instruction, tested at 16K context). Generation: 512 tokens, temp=0.
Bandwidth utilization = `tg_tps × model_size_gb / 256`.

## Single-user generation (batch=1)

| model | size | ctx | elapsed_s | pp_tps | tg_tps (avg) | bw util % |
|---|---|---|---|---|---|---|
| Llama-3.2-3B-Instruct-Q4_K_M | 2.02 | 120576 | 13 | 470.10 | 61.40 | 48.4 |
| Qwen3.5-4B-Q4_K_M | 2.74 | 262144 | 18 | 361.41 | 39.90 | 42.7 |
| gemma-4-E4B-Q4_K_M | 4.98 | 131072 | 22 | 306.06 | 34.67 | 67.4 |
| Qwen3.5-9B-Q4_K_M | 5.87 | 66560 | 29 | 204.40 | 25.66 | 58.8 |

## Generation throughput vs model size

| Model | File size | tg_tps | GB/s read | BW util |
|---|---|---|---|---|
| Llama-3.2-3B-Instruct Q4_K_M | 2.02 GB | 61.40 | 124.0 | 48.4% |
| Qwen3.5-4B Q4_K_M | 2.74 GB | 39.90 | 109.3 | 42.7% |
| gemma-4-E4B Q4_K_M | 4.98 GB | 34.67 | 172.7 | 67.4% |
| Qwen3.5-9B Q4_K_M | 5.87 GB | 25.66 | 150.6 | 58.8% |

Gemma achieves the highest utilization (67.4%) per GB transferred, suggesting it benefits from architecture-specific Vulkan optimizations.

## Prompt processing throughput

| Model | pp_tps |
|---|---|
| Llama-3.2-3B-Instruct Q4_K_M | 470.10 |
| Qwen3.5-4B Q4_K_M | 361.41 |
| gemma-4-E4B Q4_K_M | 306.06 |
| Qwen3.5-9B Q4_K_M | 204.40 |

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
| Non-MTP | 39.90 | baseline |
| MTP (temp=0) | 38.18 | -4.3% |

MTP does not help on Polaris. The verification pass overhead exceeds any batching benefit, even at greedy sampling where acceptance rate should be near 100%. In real-world use (Open WebUI, temp=1.0, penalties), acceptance rate was measured at 41.7% — well below the break-even threshold.

## Environment

- GPU: AMD Radeon RX 580 (Polaris 10, 8 GB GDDR5, 256 GB/s)
- Driver: RADV (amdgpu) via Vulkan
- CPU: Intel Core i5-7600K (4C/4T, 3.80 GHz)
- RAM: 16 GB DDR4
- OS: CachyOS (Arch Linux)
- llama.cpp: commit 98d5e8ba8 (build 9544)
