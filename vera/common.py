"""Đường dẫn, danh sách hàm, cấu hình biên dịch và cách gọi runner — dùng chung cho mọi lớp."""
from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "corpus"
SRC = CORPUS / "src"
INCLUDE = CORPUS / "include"
MANIFEST = CORPUS / "manifest"
DATA = ROOT / "data"
BIN = DATA / "binaries"
VECTORS = DATA / "vectors"
ARTIFACTS = DATA / "artifacts"  # L1: pseudocode + evidence
BUILD = ROOT / "build"  # sản phẩm trung gian, không commit
RUNNER = BUILD / "runner"

FN_IDS = [f"fn_{i:02d}" for i in range(1, 21)]
CONFIGS = ["plain", "opt", "obf"]

VERA_ERR = 0xFFFFFFFFFFFFFFFF
N_VECTORS = 50


@dataclass(frozen=True)
class BuildConfig:
    name: str
    cflags: tuple[str, ...]
    strip: bool


COMMON_CFLAGS = ("-std=c11", "-fPIC", "-shared", "-Wall", "-Wextra", f"-ffile-prefix-map={ROOT}=.")
BUILD_CONFIGS = {
    "plain": BuildConfig("plain", ("-O0", "-g"), strip=False),
    "opt": BuildConfig("opt", ("-O2",), strip=True),
    "obf": BuildConfig("obf", ("-O2", "-DVERA_OBF"), strip=True),
}


def so_path(fn_id: str, config: str) -> Path:
    return BIN / config / f"{fn_id}.so"


def load_manifest(fn_id: str) -> dict:
    return json.loads((MANIFEST / f"{fn_id}.json").read_text(encoding="utf-8"))


def load_vectors(fn_id: str) -> list[dict]:
    return json.loads((VECTORS / f"{fn_id}.json").read_text(encoding="utf-8"))["vectors"]


@dataclass
class RunResult:
    status: str  # OK | TIMEOUT | CRASH | BADLINE
    ret: int | None = None
    out: str | None = None  # hex của toàn bộ out_cap byte ("" nếu out_cap = 0)
    in_changed: bool = False
    overflow: bool = False
    detail: str = ""

    def same_as(self, other: "RunResult") -> bool:
        return (self.status, self.ret, self.out) == (other.status, other.ret, other.out)


def run_vectors(so: Path, symbol: str, vectors: list[dict], timeout: int = 2) -> list[RunResult]:
    """Chạy runner trên danh sách vector {in, arg, out_cap}; trả kết quả theo thứ tự."""
    lines = []
    for v in vectors:
        data = v["in"]
        arg = int(v["arg"], 16) if isinstance(v["arg"], str) else v["arg"]
        lines.append(f"{len(data) // 2} {arg:x} {v['out_cap']} {data or '-'}")
    p = subprocess.run(
        [str(RUNNER), str(so), symbol, str(timeout)],
        input="\n".join(lines) + "\n",
        capture_output=True,
        text=True,
        check=False,
    )
    if p.returncode != 0:
        raise RuntimeError(f"runner lỗi với {so}: {p.stderr.strip()}")
    results = []
    for raw in p.stdout.splitlines():
        parts = raw.split()
        if parts[0] == "OK":
            results.append(RunResult("OK", int(parts[1], 16), "" if parts[2] == "-" else parts[2],
                                     parts[3] == "1", parts[4] == "1"))
        else:
            results.append(RunResult(parts[0], detail=" ".join(parts[1:])))
    if len(results) != len(vectors):
        raise RuntimeError(f"runner trả {len(results)} dòng cho {len(vectors)} vector ({so})")
    return results
