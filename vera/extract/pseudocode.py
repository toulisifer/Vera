"""Sinh pseudocode cho LLM từ MỘT backend duy nhất cho toàn bộ lượt chạy.

    python -m vera.extract.pseudocode [--backend ghidra|objdump]

Backend mặc định là Ghidra headless. objdump chỉ là phương án dự phòng: nếu dùng thì
áp dụng cho cả 60 item, không trộn (quy tắc single-backend). Backend đã dùng được ghi
vào data/artifacts/backend.json và driver từ chối chạy tiếp bằng backend khác.

Ghi data/artifacts/<config>/fn_XX.pseudocode.c.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from vera.common import ARTIFACTS, BIN, CONFIGS, FN_IDS, ROOT, so_path

GHIDRA_SCRIPT_DIR = ROOT / "harness" / "ghidra"


def ghidra_home() -> Path:
    env = os.environ.get("VERA_GHIDRA")
    if env:
        return Path(env)
    found = sorted(glob.glob(os.path.expanduser("~/tools/ghidra_*_PUBLIC")))
    if not found:
        sys.exit("Không tìm thấy Ghidra: đặt VERA_GHIDRA hoặc giải nén vào ~/tools/ghidra_*_PUBLIC")
    return Path(found[-1])


def ghidra_version(home: Path) -> str:
    props = (home / "Ghidra" / "application.properties").read_text()
    return re.search(r"application\.version=(\S+)", props).group(1)


def run_ghidra(cfg: str) -> None:
    home = ghidra_home()
    out_dir = ARTIFACTS / cfg
    with tempfile.TemporaryDirectory(prefix="vera-ghidra-") as proj, tempfile.TemporaryDirectory() as tmp_out:
        cmd = [str(home / "support" / "analyzeHeadless"), proj, f"vera_{cfg}",
               "-import", *[str(so_path(f, cfg)) for f in FN_IDS],
               "-scriptPath", str(GHIDRA_SCRIPT_DIR),
               "-postScript", "VeraExportDecomp.java", tmp_out,
               "-deleteProject"]
        p = subprocess.run(cmd, capture_output=True, text=True)
        ok = re.findall(r"VERA_OK (fn_\d\d)", p.stdout + p.stderr)
        fails = re.findall(r"VERA_FAIL .*", p.stdout + p.stderr)
        if fails or len(set(ok)) != len(FN_IDS):
            sys.exit(f"[pseudocode] Ghidra lỗi ở {cfg}: {fails or 'thiếu output'}\n{p.stderr[-2000:]}")
        for fn_id in FN_IDS:
            shutil.copy(Path(tmp_out) / f"{fn_id}.c", out_dir / f"{fn_id}.pseudocode.c")


def run_objdump(cfg: str) -> None:
    for fn_id in FN_IDS:
        p = subprocess.run(["objdump", "-d", "-M", "intel", "--no-show-raw-insn", f"--disassemble={fn_id}",
                            str(so_path(fn_id, cfg))], capture_output=True, text=True, check=True)
        body = p.stdout.split(f"<{fn_id}>:", 1)[1]
        (ARTIFACTS / cfg / f"{fn_id}.pseudocode.c").write_text(f"; {fn_id} — objdump -d -M intel\n{body.strip()}\n")


def backend_version(backend: str) -> str:
    if backend == "ghidra":
        return ghidra_version(ghidra_home())
    return subprocess.run(["objdump", "--version"], capture_output=True, text=True).stdout.splitlines()[0]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", choices=["ghidra", "objdump"], default="ghidra")
    args = ap.parse_args()

    lock = ARTIFACTS / "backend.json"
    if lock.exists():
        prev = json.loads(lock.read_text())["backend"]
        if prev != args.backend:
            sys.exit(f"[pseudocode] lượt chạy này đã chốt backend '{prev}'; xóa {lock} nếu thật sự muốn đổi toàn bộ")
    for cfg in CONFIGS:
        (ARTIFACTS / cfg).mkdir(parents=True, exist_ok=True)
        (run_ghidra if args.backend == "ghidra" else run_objdump)(cfg)
        print(f"[pseudocode] {cfg}: {len(FN_IDS)} file ({args.backend})")
    lock.write_text(json.dumps({"backend": args.backend, "version": backend_version(args.backend),
                                "binaries": str(BIN.relative_to(ROOT))}, indent=2) + "\n")


if __name__ == "__main__":
    main()
