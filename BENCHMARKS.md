# Benchmarks

All models Q4_K_M unless noted. KV cache: q4_0. Flash attention: on.
Prompt: ~2130 tokens (system + padded instruction, tested at 16K context). Generation: 512 tokens, temp=0.
Bandwidth utilization = `tg_tps × model_size_gb / 256`.

## Single-user generation (batch=1)

| model | size | ctx | elapsed_s | pp_tps | tg_tps (avg) | bw util % |
|---|---|---|---|---|---|---|
| Llama-3.2-3B-Instruct-Q4_K_M | 2.02 | 131072 | 13 | 475 | 62 | 48.9 |
| gemma-4-E4B-Q4_K_M | 4.98 | 131072 | 22 | 274 | 35 | 36.3† |
| Qwen3.5-4B-Q4_K_M | 2.74 | 262144 | 18 | 340 | 38 | 40.7 |
| Qwen3.5-4B-Q4_K_M-MTP | 2.83 | 240384 | 19 | 335 | 37 | 41.0 |
| Qwen3.5-9B-Q4_K_M | 5.87 | 153600 | 28 | 204 | 24 | 55.0 |

## Generation throughput vs model size

| Model | File size | tg_tps | GB/s read | BW util |
|---|---|---|---|---|
| Llama-3.2-3B-Instruct Q4_K_M | 2.02 GB | 62 | 125.2 | 48.9% |
| Qwen3.5-4B Q4_K_M | 2.74 GB | 38 | 104.1 | 40.7% |
| Qwen3.5-4B Q4_K_M-MTP | 2.83 GB | 37 | 104.7 | 41.0% |
| gemma-4-E4B Q4_K_M | 4.98 GB | 35 | 93.0 | 36.3%† |
| Qwen3.5-9B Q4_K_M | 5.87 GB | 24 | 140.9 | 55.0% |

† Gemma-4-E4B is MoE (~7.5B total, ~4B active/token). Utilization estimated from active parameters (~2.5 GB).

## Prompt processing throughput

| Model | pp_tps |
|---|---|
| Llama-3.2-3B-Instruct Q4_K_M | 475 |
| Qwen3.5-4B Q4_K_M | 340 |
| Qwen3.5-4B Q4_K_M-MTP | 335 |
| gemma-4-E4B Q4_K_M | 274 |
| Qwen3.5-9B Q4_K_M | 204 |

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
| Non-MTP | 38 | baseline |
| MTP (temp=0) | 37 | -2.6% |

MTP does not help on Polaris. The verification pass overhead exceeds any batching benefit, even at greedy sampling where acceptance rate should be near 100%. In real-world use (Open WebUI, temp=1.0, penalties), acceptance rate was measured at 41.7% — well below the break-even threshold.

## Environment

- GPU: AMD Radeon RX 580 (Polaris 10, 8 GB GDDR5, 256 GB/s)
- Driver: RADV (amdgpu) via Vulkan
- CPU: Intel Core i5-7600K (4C/4T, 3.80 GHz)
- RAM: 16 GB DDR4
- OS: CachyOS (Arch Linux)
- llama.cpp: commit 98d5e8ba8 (build 9544)
