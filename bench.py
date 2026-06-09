#!/usr/bin/env python3
"""bench.py — llama-server benchmark for RX 580 Vulkan

Starts llama-server with a model, sends timed requests, reports tok/s.
Drop-in replacement for bench.sh.
"""

from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import requests

# ── config ────────────────────────────────────────────────────────────────────

LLAMA_SERVER = os.environ.get("LLAMA_SERVER", "llama-server")
HOST = "127.0.0.1"
PORT = 8899
BASE_URL = f"http://{HOST}:{PORT}"

PROMPT_LENGTHS = [16384]
N_GEN = 512
REPETITIONS = 3

LOG_FILE = Path("/tmp/llama-bench-server.log")

GPU_BW_GBS = 256  # RX 580 theoretical memory bandwidth (GB/s)


@dataclass
class Model:
    name: str
    path: str
    extra_args: str = ""


MODELS = [
    Model(
        name="Llama-3.2-3B-Instruct-Q4_K_M",
        path="/mnt/wd_black/Downloads/models/Llama-3.2-3B-Instruct-Q4_K_M.gguf",
        extra_args="--reasoning off --reasoning-budget 0",
    ),
    Model(
        name="gemma-4-E4B-Q4_K_M",
        path="/mnt/wd_black/Downloads/models/gemma-4-E4B-it-Q4_K_M.gguf",
        extra_args="--reasoning off --reasoning-budget 0",
    ),
    Model(
        name="Qwen3.5-4B-Q4_K_M",
        path="/mnt/wd_black/Downloads/models/Qwen3.5-4B-Q4_K_M.gguf",
        extra_args="--reasoning off --reasoning-budget 0",
    ),
    Model(
        name="Qwen3.5-4B-Q4_K_M-MTP",
        path="/mnt/wd_black/Downloads/models/Qwen3.5-4B-Q4_K_M-MTP.gguf",
        extra_args="--reasoning off --reasoning-budget 0 --spec-type draft-mtp --spec-draft-n-max 2",
    ),
    Model(
        name="Qwen3.5-9B-Q4_K_M",
        path="/mnt/wd_black/Downloads/models/Qwen3.5-9B-Q4_K_M.gguf",
        extra_args="--reasoning off --reasoning-budget 0",
    ),
]


# ── helpers ───────────────────────────────────────────────────────────────────


def cleanup(proc: subprocess.Popen | None) -> None:
    if proc is None:
        return
    proc.terminate()
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()


def wait_for_server(timeout: int = 120) -> None:
    for _ in range(timeout):
        try:
            r = requests.get(f"{BASE_URL}/health", timeout=2)
            if r.ok:
                return
        except requests.RequestException:
            pass
        time.sleep(1)
    sys.exit(1)


def check_thinking() -> None:
    if not LOG_FILE.exists():
        return
    import re

    text = LOG_FILE.read_text()
    matches = re.findall(r"thinking = (\d+)", text)
    if not matches:
        return
    status = matches[-1]
    if status == "1":
        print(">> thinking: ENABLED — results may be skewed")


def make_prompt(n_tokens: int) -> tuple[str, str]:
    system = "You are a helpful assistant. Always write long, detailed responses. Never stop early. Continue generating until you have completely finished your response."
    instruction = "Write a detailed, thorough explanation of how neural networks work. Include specific examples, mathematical concepts, and historical context. Be comprehensive and do not stop writing until you have covered the topic completely."
    unit = "padding "
    repeats = (n_tokens // 8) + 1
    user = instruction + " " + unit * repeats
    return system, user


def run_bench_request(system: str, user: str, n_gen: int) -> dict:
    payload = {
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "max_tokens": n_gen,
        "temperature": 0,
        "stream": False,
    }

    start_ns = time.time_ns()
    r = requests.post(
        f"{BASE_URL}/v1/chat/completions",
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=300,
    )
    end_ns = time.time_ns()
    r.raise_for_status()

    data = r.json()
    elapsed_s = (end_ns - start_ns) / 1_000_000_000

    usage = data.get("usage", {})
    pt = usage.get("prompt_tokens", "?")
    ct = usage.get("completion_tokens", "?")

    timings = data.get("timings", {})
    pp = timings.get("prompt_per_second")
    tg = timings.get("predicted_per_second")
    pp = int(pp) if pp else "?"
    tg = int(tg) if tg else "?"

    return {
        "prompt_tokens": pt,
        "completion_tokens": ct,
        "elapsed_s": round(elapsed_s),
        "pp_tps": pp,
        "tg_tps": tg,
    }


def get_server_version() -> str:
    try:
        result = subprocess.run(
            [LLAMA_SERVER, "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        lines = [
            l
            for l in result.stdout.splitlines() + result.stderr.splitlines()
            if "MANGOHUD" not in l
            and "[info]" not in l
            and "[warning]" not in l
        ]
        return lines[0] if lines else "unknown"
    except Exception:
        return "unknown"


def extract_ctx_from_log() -> str:
    if not LOG_FILE.exists():
        return "?"
    import re

    text = LOG_FILE.read_text()
    matches = re.findall(r"n_ctx\s*=\s*(\d+)", text)
    return matches[-1] if matches else "?"


# ── main ──────────────────────────────────────────────────────────────────────


def main() -> None:
    print(f"# RX 580 Vulkan llama-server benchmark")
    print(f"# {time.strftime('%c')}")
    print(f"# llama-server: {get_server_version()}")
    print()

    header = (
        f"| {'model':<30s} | {'size':<5s} | {'ctx':<7s}"
        f" | {'elapsed_s':<10s} | {'pp_tps':<12s}"
        f" | {'tg_tps (avg)':<15s} | {'bw util %':<12s} |"
    )
    sep = (
        f"|{'-'*30}--|{'-'*5}--|{'-'*7}--|{'-'*10}--"
        f"|{'-'*12}--|{'-'*15}--|{'-'*12}--|"
    )
    print(header)
    print(sep)

    for model in MODELS:
        model_size_gb = os.path.getsize(model.path) / 1_000_000_000

        cmd = [
            LLAMA_SERVER,
            "-m", model.path,
            "-fit", "on",
            "-ngl", "99",
            "-np", "1",
            "-fa", "on",
            "-ctk", "q4_0", "-ctv", "q4_0",
            "--host", HOST,
            "--port", str(PORT),
            "--no-webui",
        ] + model.extra_args.split()
        cmd = [c for c in cmd if c]

        proc = subprocess.Popen(
            cmd,
            stdout=LOG_FILE.open("w"),
            stderr=subprocess.STDOUT,
        )

        try:
            wait_for_server()
            check_thinking()

            ctx = extract_ctx_from_log()

            for prompt_len in PROMPT_LENGTHS:
                system, user = make_prompt(prompt_len)

                results: list[dict] = []
                for _ in range(REPETITIONS):
                    results.append(run_bench_request(system, user, N_GEN))

                cold = results[0]
                ok = cold["completion_tokens"] == N_GEN

                if ok:
                    tg_samples = [
                        r["tg_tps"] for r in results
                        if isinstance(r["tg_tps"], (int, float))
                    ]
                    avg_tg = int(sum(tg_samples) / len(tg_samples)) if tg_samples else "?"

                    bw_pct = round(avg_tg * model_size_gb / GPU_BW_GBS * 100, 1) if isinstance(avg_tg, (int, float)) else "?"
                    row = (
                        f"| {model.name:<30s} | {model_size_gb:<5.2f} | {ctx!s:<7s}"
                        f" | {cold['elapsed_s']!s:<10s} | {cold['pp_tps']!s:<12s}"
                        f" | {avg_tg!s:<15s} | {bw_pct!s:<12s} |"
                    )
                else:
                    row = (
                        f"| {model.name:<30s} | {model_size_gb:<5.2f} | {ctx!s:<7s}"
                        f" | {'N/A':<10s} | {'N/A':<12s}"
                        f" | {'N/A':<15s} | {'N/A':<12s} |"
                    )
                print(row)

        finally:
            cleanup(proc)

    print()
    print("# done")


if __name__ == "__main__":
    main()
