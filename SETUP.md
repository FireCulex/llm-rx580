# Setup

Build llama.cpp with Vulkan support:

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
cmake -B build -DGGML_VULKAN=ON
cmake --build build -j$(nproc)
```

Requires `glslc` (Vulkan SDK), `cmake`, and a Vulkan-capable driver.

## Hardware

GPU: AMD Radeon RX 580 (Polaris, 2017)
- VRAM: 8 GB GDDR5
- Bus: 256-bit @ 8 Gbps
- Bandwidth: 256 GB/s
