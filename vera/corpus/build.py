"""Biên dịch 20 hàm × 3 cấu hình thành shared object, và biên dịch runner.

    python -m vera.corpus.build
"""
from __future__ import annotations

import json
import platform
import subprocess
import sys

from vera.common import (BIN, BUILD, BUILD_CONFIGS, COMMON_CFLAGS, DATA, FN_IDS, INCLUDE, ROOT,
                         RUNNER, SRC, so_path)

CC = "gcc"


def tool_version(cmd: list[str]) -> str:
    return subprocess.run(cmd, capture_output=True, text=True, check=True).stdout.splitlines()[0]


def build_runner() -> None:
    BUILD.mkdir(exist_ok=True)
    subprocess.run([CC, "-O2", "-Wall", "-o", str(RUNNER), str(ROOT / "harness" / "runner.c"), "-ldl"],
                   check=True)


def build_all() -> list[str]:
    warnings = []
    for cfg in BUILD_CONFIGS.values():
        (BIN / cfg.name).mkdir(parents=True, exist_ok=True)
        for fn_id in FN_IDS:
            out = so_path(fn_id, cfg.name)
            cmd = [CC, *COMMON_CFLAGS, *cfg.cflags, f"-I{INCLUDE}", "-o", str(out), str(SRC / f"{fn_id}.c")]
            p = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
            if p.returncode != 0:
                sys.exit(f"[build] {fn_id}/{cfg.name} lỗi:\n{p.stderr}")
            if p.stderr.strip():
                warnings.append(f"{fn_id}/{cfg.name}: {p.stderr.strip()}")
            if cfg.strip:
                subprocess.run(["strip", "--strip-all", str(out)], check=True)
    return warnings


def main() -> None:
    build_runner()
    warnings = build_all()
    info = {
        "gcc": tool_version([CC, "--version"]),
        "strip": tool_version(["strip", "--version"]),
        "platform": platform.platform(),
        "common_cflags": [f for f in COMMON_CFLAGS if not f.startswith("-ffile-prefix-map")],
        "configs": {c.name: {"cflags": list(c.cflags), "strip": c.strip} for c in BUILD_CONFIGS.values()},
    }
    (DATA / "build_info.json").write_text(json.dumps(info, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for w in warnings:
        print("[build] cảnh báo:", w)
    print(f"[build] xong {len(FN_IDS) * len(BUILD_CONFIGS)} shared object — {info['gcc']}")


if __name__ == "__main__":
    main()
