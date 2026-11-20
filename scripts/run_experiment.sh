#!/usr/bin/env bash
# Chạy trọn một lượt thí nghiệm: L2 (LLM) → V1 (Docker) → L3 (gán nhãn) → L4 (metric).
#
#   scripts/run_experiment.sh E1                                   # 20 hàm × 3 cấu hình, temperature 0
#   scripts/run_experiment.sh E6 --fns fn_01,...,fn_10 --samples 3 # độ ổn định
#   scripts/run_experiment.sh E4 --configs obf --temperature 0.7 --samples 5
#
# Biến môi trường: VERA_OLLAMA (URL Ollama), VERA_MODEL (model), VERA_SANDBOX_IMAGE (image Docker).
# Mọi tham số sau tên lượt chạy được chuyển nguyên cho `python -m vera.llm.run`.
set -euo pipefail
cd "$(dirname "$0")/.."
RUN="${1:?Cách dùng: scripts/run_experiment.sh <tên-lượt-chạy> [tham số vera.llm.run]}"
shift
export PYTHONPATH=.
PY=.venv/bin/python

echo "== L2: phân tích bằng LLM ($RUN)"
$PY -m vera.llm.run --run "$RUN" "$@"
echo "== V1: tương đương hàm vi sai trong Docker"
$PY -m vera.verify.v1 --run "$RUN"
echo "== L3: gán nhãn claim (V3, V1b, IO, SIDE)"
$PY -m vera.verify.label --run "$RUN"
echo "== L4: metric"
$PY -m vera.report.metrics --run "$RUN" > /dev/null
echo "Xong: data/runs/$RUN/results.md"
