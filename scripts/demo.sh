#!/usr/bin/env bash
# Demo VeRA trên một hàm:  scripts/demo.sh [fn_XX] [plain|opt|obf]   (mặc định fn_08 opt)
cd "$(dirname "$0")/.."
PYTHONPATH=. exec .venv/bin/python -m vera.demo "${1:-fn_08}" "${2:-opt}" "${@:3}"
