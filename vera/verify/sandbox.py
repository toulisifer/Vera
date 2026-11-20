"""Chạy runner trên một shared object KHÔNG tin cậy (mã do LLM sinh ra) bên trong Docker.

Container: không mạng, root filesystem chỉ đọc, user nobody, giới hạn bộ nhớ/CPU/số tiến trình,
cộng timeout bên ngoài. Bên trong, runner còn fork mỗi vector một tiến trình con có timeout
và rlimit riêng (harness/runner.c), nên hàm treo/crash chỉ làm hỏng vector đó.
"""
from __future__ import annotations

import base64
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from vera.common import RUNNER, RunResult

IMAGE = os.environ.get("VERA_SANDBOX_IMAGE", "python:3.12-slim")
DOCKER_LIMITS = ["--network", "none", "--read-only", "--user", "65534:65534",
                 "--memory", "256m", "--memory-swap", "256m", "--cpus", "1", "--pids-limit", "64",
                 "--cap-drop", "ALL", "--security-opt", "no-new-privileges"]
OUTER_TIMEOUT = 300  # giây cho cả 50 vector
INLINE = os.environ.get("VERA_SANDBOX_INLINE") == "1"  # không bind mount (xem run_untrusted)


def image_digest() -> str:
    p = subprocess.run(["docker", "image", "inspect", "--format", "{{.Id}}", IMAGE],
                       capture_output=True, text=True, check=True)
    return p.stdout.strip()


def run_untrusted(so: Path, symbol: str, vectors: list[dict], timeout: int = 2) -> list[RunResult] | str:
    """Trả danh sách RunResult, hoặc chuỗi mô tả lỗi nếu cả container thất bại."""
    lines = []
    for v in vectors:
        arg = int(v["arg"], 16) if isinstance(v["arg"], str) else v["arg"]
        lines.append(f"{len(v['in']) // 2} {arg:x} {v['out_cap']} {v['in'] or '-'}")
    with tempfile.TemporaryDirectory(prefix="vera-sbx-") as d:
        if INLINE:
            # Không bind mount: chép runner và .so (vài chục KB) qua biến môi trường vào tmpfs của container.
            # Dùng khi chạy Docker lồng nhau qua docker.sock (repro/run.sh), nơi đường dẫn trên máy chủ Docker
            # không trùng đường dẫn bên trong container (Docker Desktop trên Windows/macOS).
            env = {"VERA_RUNNER_B64": base64.b64encode(RUNNER.read_bytes()).decode(),
                   "VERA_SO_B64": base64.b64encode(so.read_bytes()).decode()}
            cmd = ["docker", "run", "--rm", "-i", *DOCKER_LIMITS,
                   "--tmpfs", "/w:rw,exec,nosuid,size=16m,mode=1777",
                   "-e", "VERA_RUNNER_B64", "-e", "VERA_SO_B64", IMAGE, "sh", "-c",
                   'printf %s "$VERA_RUNNER_B64" | base64 -d > /w/runner && printf %s "$VERA_SO_B64" | base64 -d '
                   '> /w/r.so && chmod 755 /w/runner && unset VERA_RUNNER_B64 VERA_SO_B64 && '
                   f'exec /w/runner /w/r.so {symbol} {int(timeout)}']
        else:
            shutil.copy(RUNNER, Path(d) / "runner")
            shutil.copy(so, Path(d) / "r.so")
            os.chmod(d, 0o755)
            env = {}
            cmd = ["docker", "run", "--rm", "-i", *DOCKER_LIMITS, "-v", f"{d}:/w:ro", IMAGE,
                   "/w/runner", "/w/r.so", symbol, str(timeout)]
        try:
            p = subprocess.run(cmd, input="\n".join(lines) + "\n", capture_output=True, text=True,
                               timeout=OUTER_TIMEOUT, env={**os.environ, **env})
        except subprocess.TimeoutExpired:
            return "container timeout"
    if p.returncode != 0:
        return f"container lỗi ({p.returncode}): {p.stderr.strip()[:300]}"
    results = []
    for raw in p.stdout.splitlines():
        parts = raw.split()
        if parts and parts[0] == "OK":
            results.append(RunResult("OK", int(parts[1], 16), "" if parts[2] == "-" else parts[2],
                                     parts[3] == "1", parts[4] == "1"))
        else:
            results.append(RunResult(parts[0] if parts else "EMPTY", detail=" ".join(parts[1:])))
    if len(results) != len(vectors):
        return f"runner trả {len(results)} dòng cho {len(vectors)} vector"
    return results
