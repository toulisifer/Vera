#!/usr/bin/env bash
# Demo trực tiếp (chạy trên máy ảo):  scripts/live_demo.sh [tham số của vera.live]
cd "$(dirname "$0")/.."
export PYTHONPATH=.
if ! curl -s -m 5 "${VERA_OLLAMA:-http://localhost:11434}/api/version" >/dev/null; then
  echo "Không thấy Ollama ở ${VERA_OLLAMA:-http://localhost:11434}. Bật Ollama trên Windows rồi chạy lại."
  exit 1
fi
docker info >/dev/null 2>&1 || { echo "Docker chưa chạy: sudo systemctl start docker"; exit 1; }
exec .venv/bin/python -m vera.live "$@"
