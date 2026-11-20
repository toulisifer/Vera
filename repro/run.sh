#!/usr/bin/env bash
# Tái lập toàn bộ kết quả VeRA trong một container Ubuntu 24.04 sạch. Một lệnh:
#
#   repro/run.sh            # mọi lượt chạy
#   repro/run.sh E1         # chỉ E1 (nhanh, ~5 phút)
#
# Chỉ cần Docker trên máy (Linux, hoặc Docker Desktop trên Windows/macOS — Windows dùng repro/run.ps1).
# Không cần GPU, Ollama, Ghidra, Python hay GCC trên máy.
# V1 chạy mã do LLM sinh trong container con (anh em, qua docker.sock); VERA_SANDBOX_INLINE=1 đưa file vào
# container con qua biến môi trường thay vì bind mount, nên chạy được với mọi loại Docker.
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
docker build -q -t vera-repro "$REPO/repro" >/dev/null
docker pull -q python:3.12-slim >/dev/null
exec docker run --rm -t \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v "$REPO":/src:ro \
  -e VERA_SANDBOX_INLINE=1 \
  vera-repro bash /src/scripts/reproduce.sh "$@"
