# llm-rx580

Benchmarking AMD Polaris (RX 580) on CachyOS (Arch Linux) with llama.cpp Vulkan backend.

Build instructions: `SETUP.md`.

## Run benchmarks

Single script — **`bench.py`** (Python, requires `requests` via `pip install requests`). Starts `llama-server`, hits `/v1/chat/completions`, reports prompt/token timing.

### Model paths

All models on `/mnt/wd_black/Downloads/models/`. See `bench.py:45-71` for the full list.

### Key `llama-server` flags used

| Flag | Value | Why |
|------|-------|-----|
| `-ngl` | 99 | Offload all layers to GPU |
| `-np` | 1 | Single batch for head-to-head comparisons |
| `-fa` | on | Flash attention |
| `-ctk` / `-ctv` | `q4_0` | KV cache quantization |
| `--reasoning` | off | Prevents model-internal thinking tokens from inflating timing |
| `--reasoning-budget` | 0 | Same |
| `-fit` | on | Auto-fit context to model+VRAM |

### Benchmark gotchas

- **`--reasoning off --reasoning-budget 0`** is critical for Qwen models — without it, the model emits hidden thinking tokens that distort completion timing.
- Bandwidth utilization formula: `tg_tps × model_size_gb / 256`.
- MTP (speculative decoding via `--spec-type draft-mtp`) does not help on Polaris — verification overhead exceeds any batching benefit.
- Q8_0 moves ~66% more data than Q4_K_M but only drops ~19% throughput — utilization climbs because Polaris lacks int4 dot-product hardware.
- Log written to `/tmp/llama-bench-server.log`.

## Results

See `BENCHMARKS.md`. Q4_K_M is the default quantization. Models tested: llama-3.2-3B, Qwen3.5-4B, gemma-4-E4B, Qwen3.5-9B.

## Structure

- `bench.py` — single entrypoint for all benchmarks
- `BENCHMARKS.md` — results & analysis
- `MODELS.md` — model download links and source info
- `SETUP.md` — build & hardware details
