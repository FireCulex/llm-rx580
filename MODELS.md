# Models

All GGUF files stored at `/mnt/wd_black/Downloads/models/`. All Q4_K_M unless noted.

| Short name | File on disk | Source | Download |
|---|---|---|---|
| llama-3.2-3B | `llama-3.2-3b-instruct-q4_k_m.gguf` | `unsloth/Llama-3.2-3B-Instruct-GGUF` | [HF link](https://huggingface.co/unsloth/Llama-3.2-3B-Instruct-GGUF/resolve/main/Llama-3.2-3B-Instruct-Q4_K_M.gguf) |
| gemma-4-E4B | `gemma-4-E4B-it-Q4_K_M.gguf` | `unsloth/gemma-4-E4B-it-GGUF` | [HF link](https://huggingface.co/unsloth/gemma-4-E4B-it-GGUF/resolve/main/gemma-4-E4B-it-Q4_K_M.gguf) |
| Qwen3.5-4B | `Qwen3.5-4B.Q4_K_M.gguf` | `unsloth/Qwen3.5-4B-GGUF` | [HF link](https://huggingface.co/unsloth/Qwen3.5-4B-GGUF/resolve/main/Qwen3.5-4B-Q4_K_M.gguf) |
| Qwen3.5-4B-MTP | `Qwen3.5-4B-Q4_K_M-MTP.gguf` | `unsloth/Qwen3.5-4B-MTP-GGUF` | [HF link](https://huggingface.co/unsloth/Qwen3.5-4B-MTP-GGUF/resolve/main/Qwen3.5-4B-Q4_K_M.gguf) |
| Qwen3.5-9B | `Qwen3.5-9B.Q4_K_M.gguf` | `unsloth/Qwen3.5-9B-GGUF` | [HF link](https://huggingface.co/unsloth/Qwen3.5-9B-GGUF/resolve/main/Qwen3.5-9B-Q4_K_M.gguf) |

## Download with huggingface-cli

```bash
pip install huggingface_hub hf_transfer
# example — substitute repo + filename from table above
huggingface-cli download unsloth/Llama-3.2-3B-Instruct-GGUF \
  --include "Llama-3.2-3B-Instruct-Q4_K_M.gguf" --local-dir /mnt/wd_black/Downloads/models/
```


