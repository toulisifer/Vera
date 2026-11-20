# Reproducing VeRA's results

You need **only Docker** (Linux, or Docker Desktop on Windows/macOS). No GPU, LLM, Ghidra, Python or GCC.

Linux / macOS / WSL:

```bash
tar xzf vera-source.tar.gz && cd vera      # or: git clone <repo-url> vera && cd vera
repro/run.sh                               # all experiments, ~20–40 min
repro/run.sh E1                            # main run only, ~5 min
```

Windows (Docker Desktop running), in PowerShell:

```powershell
tar xzf vera-source.tar.gz; cd vera
powershell -ExecutionPolicy Bypass -File repro\run.ps1
```

The first run downloads `ubuntu:24.04` and `python:3.12-slim` (~200 MB) and installs GCC inside the container.

What it does, inside a clean Ubuntu 24.04 container (GCC 13.3.0):

1. Rebuilds the 60 binaries and 1,000 I/O vectors from source and compares them with the committed copies.
2. Runs the unit tests, the corpus checks and the V3 self-test.
3. Replays every LLM answer from the committed cache (`data/cache/llm`, keyed by SHA-256 of the request),
   then re-runs V1 (in a sandboxed `python:3.12-slim` container), V1b/V3 labelling and all metrics.
4. Recomputes E4 self-consistency, E6 stability and the gold-set scores (kappa, precision/recall, corrected HR).

Each step prints `giống hệt bản commit` ("identical to the committed result"), `KHÁC` ("differs") or `LỖI` ("error").
The last line is the verdict: `TÁI LẬP ĐẠT` = reproduced; `KHÔNG ĐẠT` = some step failed or differed (exit code 1).

Re-running the LLM itself (not just replaying it) needs Ollama with `qwen2.5-coder:7b` (Q4_K_M):
`scripts/run_experiment.sh E1` — see the main README. Outputs at temperature 0 are near-deterministic but not
guaranteed bit-identical across GPUs/Ollama versions; E6 measures this variance.

## Report back

If it fails, please open a GitHub issue with the last ~25 lines of output, `docker --version` and your OS.
Record the result in `repro/RESULTS.md`.
