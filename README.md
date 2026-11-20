# VeRA: Verifying LLM Explanations of Binary Code

**VeRA** (Verification layer for LLM-assisted Reverse engineering Analysis) checks what a large language model
claims about a compiled function. It splits the LLM's explanation into small, testable claims and verifies each one
against evidence taken from the binary itself, instead of trusting the model.

<img width="2640" height="2060" alt="image" src="https://github.com/user-attachments/assets/cac4f0da-812a-4060-aa03-df09a62e4ac4" />


## Why

LLMs are increasingly used to explain decompiled code during reverse engineering and malware analysis. They often
sound right while being wrong, for example naming a well-known algorithm for a function that only looks similar.
VeRA measures how often that happens and catches it automatically.

## How it works

| Layer | What it does |
|---|---|
| **L0 Corpus** | 20 C functions (7 classic algorithms, 7 "near-miss" look-alikes, 6 custom), each built 3 ways (plain, `-O2`, obfuscated) = 60 binaries, 1,000 I/O test vectors |
| **L1 Extraction** | Ghidra headless decompiles each binary; Capstone extracts constants and other static evidence |
| **L2 LLM** | A local model (Qwen2.5-Coder 7B via Ollama) explains each function as structured JSON claims |
| **L3 Verification** | **V1** recompiles the LLM's recovered code and runs it on test vectors in a Docker sandbox; **V1b** checks algorithm claims against reference oracles; **V3** checks claimed constants and behaviour against binary evidence |
| **L4 Reporting** | Hallucination rate, verifier precision/recall and confidence intervals for every run |

## Key results (main run, Qwen2.5-Coder 7B)

| Measure | Result |
|---|---|
| Gold set agreement between two annotators (120 claims) | Cohen's kappa **0.93** |
| Precision when VeRA flags a claim as contradicted | **88%** [75%, 100%] |
| False support of a wrong algorithm in the V3 self-test | **0 / 1,290** |
| Raw hallucination rate | 6.4% → **26.2%** after correcting for missed errors |
| Wrong algorithm names on near-miss functions | **55.6%** of algorithm claims refuted |
| Self-reported confidence as an error predictor (temperature 0) | AUROC **0.53**, close to random |

Full tables with 95% confidence intervals are in [`data/SUMMARY.md`](data/SUMMARY.md).

## Quick start

View the results without installing anything: open `data/demo/VeRA_demo.html` in a browser.

Reproduce every number with Docker only:

```bash
repro/run.sh          # Linux / macOS / WSL
```

```powershell
powershell -ExecutionPolicy Bypass -File repro\run.ps1   # Windows
```

The script builds a clean Ubuntu 24.04 image, rebuilds the corpus, replays all cached LLM answers and recomputes
every metric. It ends with `TÁI LẬP ĐẠT` ("reproduction passed") when all numbers match.

Full development setup (Ubuntu 24.04, GCC 13, Ghidra 12.1.4, Ollama):

```bash
make setup            # create .venv and install dependencies
make                  # build corpus (60 binaries, 1,000 vectors) and run tests
export VERA_OLLAMA=http://localhost:11434
PYTHONPATH=. python -m vera.shell          # interactive demo
scripts/demo_web.sh                        # web demo at http://localhost:8765
```

## Project layout

| Path | Contents |
|---|---|
| `corpus/` | 20 C functions, shared header, ground-truth manifests |
| `harness/` | sandboxed test runner, Ghidra export script |
| `vera/` | extraction, LLM client, verifiers, gold set tools, reports, demo |
| `data/` | binaries, vectors, Ghidra output, LLM cache, results of every run |
| `repro/` | one-command reproduction in Docker |
| `docs/` | architecture diagrams, conventions, annotation guideline |
| `tests/` | unit tests for oracles, V3 and the demo |

Most internal documentation and code comments are in Vietnamese; [`HUONG_DAN_CHAY.md`](HUONG_DAN_CHAY.md) is a
step-by-step run guide in Vietnamese.

## Credits

Course project at FPT University (Ho Chi Minh City).
The system, dataset, experiments and demo were designed and implemented by
**Do Tien Thanh** ([@toulisifer](https://github.com/toulisifer)).

## License

[MIT](LICENSE)
