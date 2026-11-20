#!/usr/bin/env bash
# Kiểm tra tái lập trên bản clone sạch — không cần GPU, Ollama hay Ghidra.
#
#   scripts/reproduce.sh            # mọi lượt chạy (khoảng 20–40 phút)
#   scripts/reproduce.sh E1         # chỉ các lượt được nêu
#
# 1. Clone repo (commit hiện tại) vào thư mục tạm, tạo venv, build lại corpus.
# 2. So 60 binary và 1.000 vector với bản đã commit.
# 3. Chạy test, kiểm tra corpus, self-test V3 (so với bản commit).
# 4. Mỗi lượt chạy: phát lại L2 từ cache LLM đã commit (data/cache/llm), chạy V1 → L3 → L4, so results.json.
#    E1_p2 dùng prompt cũ (p2) nên không phát lại L2: giữ analysis đã commit, chạy lại V1 → L3 → L4.
# 5. Tính lại E4 (self-consistency), E6 (độ ổn định), gold set (kappa, precision/recall, HR hiệu chỉnh).
# Yêu cầu: gcc, binutils, git, python3-venv, docker (image python:3.12-slim cho V1).
# Trong container Docker lồng nhau (repro/run.sh, run.ps1): VERA_SANDBOX_INLINE=1, không cần bind mount.
set -uo pipefail
SRC="$(cd "$(dirname "$0")/.." && pwd)"
ALL=(E1 E1_qwen3 E1_llm4decompile E4 E6 E1_p2)
if [ $# -eq 0 ]; then RUNS=("${ALL[@]}"); else RUNS=("$@"); fi
FAIL=0
WORK="$(mktemp -d "${TMPDIR:-/tmp}/vera-repro-XXXX")"
REF="$WORK/committed"
echo "== Clone sạch vào $WORK"
if git -C "$SRC" rev-parse --git-dir >/dev/null 2>&1; then git clone -q "$SRC" "$WORK/vera" || exit 1
else cp -a "$SRC" "$WORK/vera" && rm -rf "$WORK/vera/.venv"   # bản giải nén từ vera-source.tar.gz
     git -C "$WORK/vera" init -q && git -C "$WORK/vera" -c core.safecrlf=false add -A && git -C "$WORK/vera" -c user.name=repro -c user.email=repro@local commit -qm snapshot; fi
cd "$WORK/vera"
python3 -m venv .venv && .venv/bin/pip -q install -r requirements.txt || exit 1
export PYTHONPATH=.
PY=.venv/bin/python
CMP="$PY tools/compare_json.py"
mkdir -p "$REF" && cp -r data "$REF/"

docker image inspect python:3.12-slim >/dev/null 2>&1 || docker pull -q python:3.12-slim >/dev/null

echo "== Build lại corpus (GCC $(gcc -dumpfullversion))"
if ! $PY -m vera.corpus.build >/dev/null; then
  echo "   build corpus: LỖI TÁI LẬP"
  exit 1
fi
if ! $PY -m vera.corpus.vectors >/dev/null; then
  echo "   sinh vector: LỖI TÁI LẬP"
  exit 1
fi
if diff -r -q data/binaries "$REF/data/binaries" >/dev/null; then echo "   60 binary: giống hệt bản commit";
else echo "   60 binary: KHÁC bản commit (phiên bản GCC khác 13.3.0?) — các bước sau dùng bản commit"; FAIL=1; git checkout -q -- data/binaries; fi
if diff -r -q data/vectors "$REF/data/vectors" >/dev/null; then echo "   1.000 vector: giống hệt";
else echo "   1.000 vector: KHÁC — LỖI TÁI LẬP"; FAIL=1; git checkout -q -- data/vectors; fi

echo "== Test, kiểm tra corpus, self-test V3"
if ! $PY -m pytest -q tests | tail -1; then echo "   test: LỖI (có test thất bại)"; FAIL=1; fi
if ! $PY -m vera.corpus.check | tail -1; then echo "   kiểm corpus: LỖI"; FAIL=1; fi
$PY -m vera.verify.selftest >/dev/null && $CMP "self-test V3" data/v3_selftest.json "$REF/data/v3_selftest.json" || FAIL=1

KEYS="overall by_config by_group by_type by_type_config e2_matrix e3 v1 rq3_confidence_auroc"
llm_args() {
  $PY - "$1" <<'EOF'
import json, sys
r = json.load(open(f"data/runs/{sys.argv[1]}/run.json"))
a = ["--model", r["model"]["model"], "--temperature", str(r["temperature"]), "--samples", str(r["samples"]),
     "--fns", ",".join(r["fns"]), "--configs", ",".join(r["configs"]),
     "--num-predict", str(r.get("num_predict", 3072)), "--num-ctx", str(r.get("num_ctx", 8192))]
if r.get("think") is not None:
    a += ["--think", "on" if r["think"] else "off"]
print(" ".join(a))
EOF
}

for RUN in "${RUNS[@]}"; do
  D="data/runs/$RUN"
  case "$RUN" in
    E1_p2)
      echo "== $RUN: giữ analysis đã commit (prompt p2), chạy lại V1 → L3 → L4"
      find "$D" -name '*.v1.json' -o -name '*.verdicts.json' | xargs rm -f; rm -f "$D/results.json" ;;
    E1_llm4decompile)
      echo "== $RUN: phát lại LLM4Decompile từ cache"
      rm -rf "$D"; VERA_OFFLINE=1 $PY -m vera.llm.llm4decompile --run "$RUN" >/dev/null || { FAIL=1; continue; } ;;
    *)
      echo "== $RUN: phát lại L2 từ cache LLM"
      ARGS=$(llm_args "$RUN"); rm -rf "$D"
      VERA_OFFLINE=1 $PY -m vera.llm.run --run "$RUN" $ARGS >/dev/null || { FAIL=1; continue; } ;;
  esac
  $PY -m vera.verify.v1 --run "$RUN" >/dev/null || { FAIL=1; continue; }
  $PY -m vera.verify.label --run "$RUN" >/dev/null || { FAIL=1; continue; }
  $PY -m vera.report.metrics --run "$RUN" >/dev/null || { FAIL=1; continue; }
  $CMP "$RUN results" "$D/results.json" "$REF/$D/results.json" $KEYS || FAIL=1
  case "$RUN" in
    E4) $PY -m vera.report.consistency --e4 E4 >/dev/null || { FAIL=1; continue; }
        $CMP "E4 self-consistency (RQ3)" "$D/consistency.json" "$REF/$D/consistency.json" || FAIL=1 ;;
    E6) $PY -m vera.report.consistency --e6 E6 >/dev/null || { FAIL=1; continue; }
        $CMP "E6 độ ổn định" "$D/stability.json" "$REF/$D/stability.json" || FAIL=1 ;;
    E1) $PY -m vera.gold.score --run E1 --final >/dev/null || { FAIL=1; continue; }
        $CMP "gold set E5 (RQ4)" data/gold/E1/score.json "$REF/data/gold/E1/score.json" || FAIL=1 ;;
  esac
done

echo
if [ $FAIL -eq 0 ]; then echo "== KẾT LUẬN: TÁI LẬP ĐẠT — mọi kết quả giống hệt bản commit. Thư mục: $WORK";
else echo "== KẾT LUẬN: KHÔNG ĐẠT — có bước LỖI hoặc KHÁC bản commit (xem các dòng LỖI/KHÁC ở trên). Thư mục: $WORK"; fi
exit $FAIL
