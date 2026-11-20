"""Demo TRỰC TIẾP: chạy toàn bộ pipeline trên một hàm tạo ra ngay tại buổi demo.

    python -m vera.live                                   # menu hỏi từng bước
    python -m vera.live --mutate fn_01                    # đổi một hằng của fn_01 thành số ngẫu nhiên
    python -m vera.live --mutate fn_01 --const 0xEDB88320 --to 0x1234ABCD
    python -m vera.live --fn fn_08 --config opt           # hàm có sẵn, gọi AI trực tiếp (bỏ qua cache)
    python -m vera.live --file /đường/dẫn/ham.c           # hàm C tự viết, dùng VERA_FN(fn_99)

Không dùng kết quả soạn sẵn: biên dịch → sinh 50 đầu vào và đáp án → Ghidra → AI (Ollama, gọi
trực tiếp) → VeRA gán nhãn → chạy mã AI viết lại trong Docker. Cần Ollama (VERA_OLLAMA) và Docker.
Kết quả mỗi lần chạy lưu ở data/live/<thời điểm>/ (không commit).
"""
from __future__ import annotations

import argparse
import json
import random
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from vera import demo
from vera.common import (BUILD, BUILD_CONFIGS, COMMON_CFLAGS, DATA, FN_IDS, INCLUDE, ROOT, SRC, load_manifest,
                         run_vectors)
from vera.corpus.build import build_runner
from vera.corpus.vectors import make_vectors, trim_out
from vera.extract.evidence import extract
from vera.extract.pseudocode import GHIDRA_SCRIPT_DIR, ghidra_home
from vera.llm import client
from vera.verify.v3 import Evidence

LIVE_FN = "fn_99"   # tên trung tính, không lộ thuật toán
HEX = re.compile(r"0x[0-9a-fA-F]{4,16}")
C = demo.C


def say(msg: str) -> None:
    print(f"{C['dim']}  … {msg}{C['0']}", flush=True)


def ask(prompt: str, default: str) -> str:
    try:
        v = input(f"{C['b']}{prompt}{C['0']} [{default}]: ").strip()
    except EOFError:
        v = ""
    return v or default


# ------------------------------------------------------------- chuẩn bị mã nguồn
def constants_of(fn: str) -> list[str]:
    """Hằng hex trong mã nguồn, hằng đặc trưng (theo manifest) đứng đầu."""
    src = (SRC / f"{fn}.c").read_text()
    found = list(dict.fromkeys(m.group().upper().replace("0X", "0x") for m in HEX.finditer(src)))
    key = [c["value"] for c in load_manifest(fn)["characteristic_constants"]]
    return sorted(found, key=lambda c: (c not in key, key.index(c) if c in key else 0))


def normalize_hex(v: str | None) -> str | None:
    if not v:
        return None
    v = v.strip()
    if not v.lower().startswith("0x"):
        v = "0x" + v
    if not re.fullmatch(r"0x[0-9a-fA-F]{1,16}", v):
        sys.exit(f"Giá trị {v!r} không phải số hex (chỉ dùng 0-9 và A-F)")
    return "0x" + v[2:].upper()


def mutate(fn: str, const: str | None, to: str | None) -> tuple[str, str]:
    src = (SRC / f"{fn}.c").read_text()
    consts = constants_of(fn)
    if not consts:
        sys.exit(f"{fn} không có hằng hex nào để đổi")
    old = const or consts[0]
    hit = re.search(re.escape(old), src, re.I)
    if not hit:
        sys.exit(f"Không thấy hằng {old} trong {fn}.c (có: {', '.join(consts)})")
    old = hit.group()
    width = len(old) - 2
    new = normalize_hex(to) or f"0x{random.getrandbits(width * 4) | 1:0{width}X}"
    note = f"Biến thể tạo lúc demo: hằng {old} của {fn} ({load_manifest(fn)['algorithm_label']}) được đổi thành {new}."
    return src.replace(old, new), note


def prepare_source(a) -> tuple[str, str, str]:
    """Trả (mã nguồn, mô tả đáp án, input profile)."""
    if a.file:
        src = Path(a.file).read_text()
        if "VERA_FN(" not in src:
            sys.exit("File phải định nghĩa hàm bằng VERA_FN(fn_99) và #include \"vera.h\"")
        return src, f"Hàm C tự viết: {a.file}", "bytes"
    if a.mutate:
        src, note = mutate(a.mutate, a.const, a.to)
        return src, note, load_manifest(a.mutate)["input_profile"]
    raise AssertionError


# ------------------------------------------------------------- các bước pipeline
def build(src: str, cfg_name: str, work: Path) -> Path:
    src = re.sub(r"VERA_FN\(\s*fn_\d+\s*\)", f"VERA_FN({LIVE_FN})", src)
    (work / f"{LIVE_FN}.c").write_text(src)
    cfg = BUILD_CONFIGS[cfg_name]
    so = work / f"{LIVE_FN}.so"
    p = subprocess.run(["gcc", *COMMON_CFLAGS, *cfg.cflags, f"-I{INCLUDE}", "-o", str(so), str(work / f"{LIVE_FN}.c")],
                       capture_output=True, text=True, cwd=ROOT)
    if p.returncode != 0:
        sys.exit(f"Biên dịch lỗi:\n{p.stderr}")
    if cfg.strip:
        subprocess.run(["strip", "--strip-all", str(so)], check=True)
    return so


def ground_truth_vectors(so: Path, profile: str) -> list[dict]:
    vs = make_vectors(LIVE_FN, profile)
    res = run_vectors(so, LIVE_FN, vs)
    for v, r in zip(vs, res):
        if r.status != "OK":
            sys.exit(f"Hàm gốc lỗi ở vector {v['id']}: {r.status} {r.detail}")
        v["ret"] = f"0x{r.ret:016x}"
        v["out"] = trim_out(r.out or "")
        v["arg"] = f"0x{v['arg']:016x}"
    return vs


def decompile(so: Path) -> str:
    with tempfile.TemporaryDirectory(prefix="vera-live-gh-") as proj, tempfile.TemporaryDirectory() as out:
        cmd = [str(ghidra_home() / "support" / "analyzeHeadless"), proj, "live", "-import", str(so),
               "-scriptPath", str(GHIDRA_SCRIPT_DIR), "-postScript", "VeraExportDecomp.java", out, "-deleteProject"]
        p = subprocess.run(cmd, capture_output=True, text=True)
        f = Path(out) / f"{LIVE_FN}.c"
        if not f.exists():
            sys.exit(f"Ghidra lỗi:\n{(p.stdout + p.stderr)[-1500:]}")
        return f.read_text()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--mutate", help="hàm corpus cần đổi một hằng (vd. fn_01)")
    ap.add_argument("--const", help="hằng cần đổi (mặc định: hằng hex đầu tiên trong mã nguồn)")
    ap.add_argument("--to", help="giá trị mới (mặc định: ngẫu nhiên, cùng độ rộng)")
    ap.add_argument("--fn", help="hàm corpus có sẵn, gọi AI trực tiếp")
    ap.add_argument("--file", help="file C tự viết")
    ap.add_argument("--config", default="opt", choices=list(BUILD_CONFIGS))
    ap.add_argument("--no-pause", action="store_true")
    a = ap.parse_args()
    demo.PAUSE = not a.no_pause and sys.stdin.isatty()

    if not (a.mutate or a.fn or a.file):
        print(f"{C['h']}VeRA — demo trực tiếp{C['0']}\n"
              "  1. Đổi một hằng số của hàm có sẵn (tạo hàm near-miss mới ngay bây giờ)\n"
              "  2. Hàm có sẵn trong corpus, gọi AI trực tiếp\n"
              "  3. File C tự viết")
        mode = ask("Chọn", "1")
        if mode == "1":
            a.mutate = ask("Hàm gốc (fn_01 … fn_20)", "fn_01")
            consts = constants_of(a.mutate)
            print(f"  Hằng trong {a.mutate}: {', '.join(consts) or '(không có)'}")
            a.const = ask("Hằng cần đổi", consts[0] if consts else "")
            a.to = ask("Giá trị mới, hex (vd. 1234ABCD; Enter = ngẫu nhiên)", "ngẫu nhiên")
            a.to = None if a.to == "ngẫu nhiên" else a.to
        elif mode == "2":
            a.fn = ask("Hàm (fn_01 … fn_20)", "fn_08")
        else:
            a.file = ask("Đường dẫn file C", str(ROOT / "demo" / "example_fn.c"))
        a.config = ask("Cấu hình (plain / opt / obf)", a.config)

    if a.fn and a.fn not in FN_IDS:
        sys.exit(f"Không có hàm {a.fn}")
    t0 = time.time()
    work = DATA / "live" / time.strftime("%Y%m%d-%H%M%S")
    work.mkdir(parents=True, exist_ok=True)
    if not (BUILD / "runner").exists():
        build_runner()

    if a.fn:  # hàm có sẵn: dùng binary và vector của corpus, chỉ gọi AI trực tiếp
        from vera.common import ARTIFACTS, load_vectors, so_path
        fn_id, so = a.fn, so_path(a.fn, a.config)
        pseudo = (ARTIFACTS / a.config / f"{a.fn}.pseudocode.c").read_text()
        vectors, ev = load_vectors(a.fn), None
        m = load_manifest(a.fn)
        truth = (f"{m['algorithm_label']} — nhóm {m['group']}", m["description"], (SRC / f"{a.fn}.c").read_text())
        intro = f"Hàm có sẵn {a.fn}; AI được gọi trực tiếp, không dùng kết quả lưu sẵn."
    else:
        src, note, profile = prepare_source(a)
        fn_id = LIVE_FN
        say(f"biên dịch ({a.config}: {' '.join(BUILD_CONFIGS[a.config].cflags)})")
        so = build(src, a.config, work)
        say("sinh 50 đầu vào và chạy hàm gốc để lấy đáp án")
        vectors = ground_truth_vectors(so, profile)
        say("Ghidra dịch ngược (khoảng 10–20 giây)")
        pseudo = decompile(so)
        ev = Evidence(extract(so))
        truth = ("Hàm tạo lúc demo", note, re.sub(r"VERA_FN\(\s*fn_\d+\s*\)", f"VERA_FN({LIVE_FN})", src))
        intro = note
    say(f"gửi pseudocode cho AI ({client.DEFAULT_MODEL} qua {client.OLLAMA_URL}) — khoảng 15–40 giây")
    for attempt in range(3):  # Ollama có thể đang khởi động lại hoặc nạp model vào GPU
        try:
            res = client.analyze(fn_id, pseudo, "ghidra", use_cache=False)
            break
        except OSError as e:
            if attempt == 2:
                sys.exit(f"Không gọi được Ollama ở {client.OLLAMA_URL}: {e}\n"
                         "Kiểm tra Ollama đang chạy và biến VERA_OLLAMA trỏ đúng địa chỉ.")
            say(f"Ollama chưa trả lời ({e}); thử lại sau 5 giây")
            time.sleep(5)
    say(f"chuẩn bị xong sau {time.time() - t0:.0f} giây")
    (work / "analysis.json").write_text(json.dumps(res, indent=1, ensure_ascii=False))
    (work / "pseudocode.c").write_text(pseudo)
    if so.parent != work:  # hàm có sẵn: lưu kèm binary của corpus để xem lại
        shutil.copy(so, work / so.name)
    demo.present(fn_id, a.config, pseudo, res, ev=ev, vectors=vectors, truth=truth, intro=intro)
    print(f"{C['dim']}Lưu tại {work.relative_to(ROOT)}{C['0']}")


if __name__ == "__main__":
    main()
