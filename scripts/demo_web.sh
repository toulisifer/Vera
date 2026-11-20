#!/usr/bin/env bash
# Demo VeRA trên trình duyệt, chạy ngay trong máy ảo Ubuntu:  scripts/demo_web.sh
# Máy chủ tự tìm AI (Ollama) VERA_OLLAMA, mặc định localhost:11434.
# Ollama ở máy khác: export VERA_OLLAMA=http://<host>:11434
cd "$(dirname "$0")/.."
export PYTHONPATH=.
pkill -f "python -m [v]era.webapp" 2>/dev/null
docker info >/dev/null 2>&1 || { echo "Docker chưa chạy: sudo systemctl start docker"; exit 1; }
( sleep 4; xdg-open "http://localhost:8765/#tructiep" >/dev/null 2>&1 ) &
exec .venv/bin/python -m vera.webapp --port 8765
