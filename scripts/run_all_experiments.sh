#!/usr/bin/env bash
# Chạy lượt chính E1 rồi các lượt phụ: E4 (độ bất định), E6 (độ ổn định), E1 với model thứ hai,
# và baseline LLM4Decompile cho V1.
# Mỗi lượt dùng scripts/run_experiment.sh; lượt nào đã có results.json thì bỏ qua (chạy lại an toàn).
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH=.
MAIN_MODEL="${VERA_MODEL:-qwen2.5-coder:7b}"
SECOND_MODEL="${VERA_SECOND_MODEL:-qwen3:8b}"
E6_FNS="fn_01,fn_03,fn_05,fn_07,fn_08,fn_10,fn_12,fn_14,fn_16,fn_18"   # 10 hàm: đủ ba nhóm

run() { local name="$1"; shift; [ -f "data/runs/$name/results.json" ] && { echo "== $name đã có, bỏ qua"; return; }
        VERA_MODEL="$1" scripts/run_experiment.sh "$name" "${@:2}"; }

run E1 "$MAIN_MODEL"
.venv/bin/python -m vera.report.case_studies --run E1
run E4 "$MAIN_MODEL" --configs obf --temperature 0.7 --samples 5
.venv/bin/python -m vera.report.consistency --e4 E4
run E6 "$MAIN_MODEL" --fns "$E6_FNS" --samples 3
.venv/bin/python -m vera.report.consistency --e6 E6
run E1_qwen3 "$SECOND_MODEL" --think off
if [ ! -f data/runs/E1_llm4decompile/results.json ]; then
  echo "== Baseline LLM4Decompile (V1)"
  .venv/bin/python -m vera.llm.llm4decompile --run E1_llm4decompile
  .venv/bin/python -m vera.verify.v1 --run E1_llm4decompile
  .venv/bin/python -m vera.verify.label --run E1_llm4decompile > /dev/null
  .venv/bin/python -m vera.report.metrics --run E1_llm4decompile > /dev/null
fi
echo "== Tất cả lượt phụ xong"
