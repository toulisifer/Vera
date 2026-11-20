"""Phiên làm việc tương tác của VeRA: khởi động, kiểm tra thành phần, rồi gõ lệnh ở dấu nhắc vera>.

    python -m vera.shell

Mỗi lệnh phân tích gọi đúng vera.cli.run (biên dịch, Ghidra, AI, kiểm chứng, sandbox), không dùng kết quả soạn sẵn.
"""
from __future__ import annotations

import argparse
import cmd
import difflib
import json
import os
import shlex
import subprocess
import time
import urllib.request
from pathlib import Path

# Đặt VERA_OLLAMA nếu Ollama chạy ở máy khác (vd. máy host của VM)
os.environ.setdefault("VERA_OLLAMA", "http://localhost:11434")

from vera import cli, live  # noqa: E402
from vera.common import (ARTIFACTS, BUILD_CONFIGS, DATA, FN_IDS, SRC, load_manifest,  # noqa: E402
                         so_path)
from vera.corpus.vectors import PROFILES  # noqa: E402
from vera.extract.pseudocode import ghidra_home  # noqa: E402
from vera.llm import client  # noqa: E402
from vera.verify import sandbox  # noqa: E402


def check(name: str, fn) -> bool:
    try:
        detail = fn()
        print(f"  [ ok ] {name:8} {detail}")
        return True
    except BaseException as e:  # ghidra_home() gọi sys.exit khi không tìm thấy
        print(f"  [FAIL] {name:8} {e}")
        return False


def ollama() -> str:
    with urllib.request.urlopen(f"{client.OLLAMA_URL}/api/version", timeout=5) as r:
        ver = json.load(r)["version"]
    with urllib.request.urlopen(f"{client.OLLAMA_URL}/api/tags", timeout=5) as r:
        models = [m["name"] for m in json.load(r)["models"]]
    if client.DEFAULT_MODEL not in models:
        raise RuntimeError(f"ollama {ver} chưa có model {client.DEFAULT_MODEL}")
    # nạp model vào GPU và giữ đến khi Ollama tắt (mặc định Ollama gỡ model sau 5 phút rảnh)
    t = time.time()
    body = json.dumps({"model": client.DEFAULT_MODEL, "keep_alive": -1}).encode()
    req = urllib.request.Request(f"{client.OLLAMA_URL}/api/generate", data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        json.load(r)
    return f"{ver}  model {client.DEFAULT_MODEL} loaded ({time.time() - t:.0f} s)  ({client.OLLAMA_URL})"


def docker() -> str:
    p = subprocess.run(["docker", "image", "inspect", "-f", "{{.Id}}", sandbox.IMAGE],
                       capture_output=True, text=True, timeout=20)
    if p.returncode != 0:
        raise RuntimeError(p.stderr.strip() or "docker không chạy (sudo systemctl start docker)")
    ver = subprocess.run(["docker", "version", "-f", "{{.Server.Version}}"], capture_output=True, text=True).stdout
    return f"{ver.strip()}  sandbox image {sandbox.IMAGE}"


def corpus() -> str:
    n_so = sum(so_path(f, c).exists() for f in FN_IDS for c in BUILD_CONFIGS)
    n_vec = sum(len(json.loads(p.read_text())["vectors"]) for p in (DATA / "vectors").glob("fn_*.json"))
    return f"{len(FN_IDS)} functions x {len(BUILD_CONFIGS)} configs = {n_so} binaries, {n_vec} vectors"


def fn_arg(args: list[str], i: int = 0) -> str:
    if len(args) <= i or args[i] not in FN_IDS:
        raise ValueError(f"cần tên hàm fn_01 … fn_20")
    return args[i]


def cfg_arg(args: list[str], i: int) -> str:
    c = args[i] if len(args) > i else "opt"
    if c not in BUILD_CONFIGS:
        raise ValueError(f"cấu hình phải là {' / '.join(BUILD_CONFIGS)}")
    return c


def e1_item(run: Path, fn: str, cfg: str) -> dict | None:
    """Kết quả đã lưu của một item trong lượt chạy; None nếu AI trả lời sai schema."""
    ana = json.loads((run / cfg / f"{fn}.analysis.json").read_text())
    if not ana.get("schema_valid"):
        return None
    ver = json.loads((run / cfg / f"{fn}.verdicts.json").read_text())
    v1p = run / cfg / f"{fn}.v1.json"
    v1 = json.loads(v1p.read_text()) if v1p.exists() else {}
    counts = {k: 0 for k in ("verified", "supported", "unsupported", "contradicted")}
    for cl in ver["claims"]:
        counts[cl["verdict"]["label"]] += 1
    return {"algorithm": ana["output"].get("algorithm"), "claims": ver["claims"], "counts": counts,
            "v1": f"{v1['n_match']}/{v1['n_vectors']}" if v1.get("compiled") else "lỗi dịch"}


class Shell(cmd.Cmd):
    prompt = "vera> "
    intro = "Gõ help để xem lệnh.\n"

    def onecmd(self, line: str) -> bool:
        try:
            return super().onecmd(line)
        except (ValueError, FileNotFoundError) as e:
            print(f"lỗi: {e}")
        except SystemExit as e:  # vera.cli báo lỗi bằng sys.exit(thông báo)
            if e.code not in (None, 0):
                print(e.code)
        except KeyboardInterrupt:
            print("\n(đã dừng)")
        return False

    def emptyline(self) -> bool:
        return False

    def default(self, line: str) -> None:
        print(f"không có lệnh {line.split()[0]!r}; gõ help")

    # ------------------------------------------------------------- xem dữ liệu
    def do_list(self, _: str) -> None:
        """list                    20 hàm của bộ dữ liệu và nhóm của chúng"""
        for f in FN_IDS:
            m = load_manifest(f)
            print(f"  {f}  {m['group']:9}  {m['input_profile']:8}  {m['algorithm_label']}")

    def do_source(self, line: str) -> None:
        """source fn_XX            mã nguồn C của hàm (AI không được xem file này)"""
        print((SRC / f"{fn_arg(line.split())}.c").read_text().rstrip())

    def do_diff(self, line: str) -> None:
        """diff fn_XX fn_YY        so sánh mã nguồn hai hàm"""
        a, b = fn_arg(line.split(), 0), fn_arg(line.split(), 1)
        la, lb = (SRC / f"{a}.c").read_text().splitlines(), (SRC / f"{b}.c").read_text().splitlines()
        for d in difflib.unified_diff(la, lb, f"{a}.c", f"{b}.c", n=0, lineterm=""):
            print(d)

    def do_inspect(self, line: str) -> None:
        """inspect fn_XX [cfg]     binary mà người phân tích nhận được (file, ký hiệu, chuỗi)"""
        args = line.split()
        so = so_path(fn_arg(args), cfg_arg(args, 1))
        for c in (["file", "-b", so], ["nm", "-D", "--defined-only", so]):
            print("$ " + " ".join(map(str, c)))
            print(subprocess.run(c, capture_output=True, text=True).stdout.rstrip())
        print(f"$ strings {so} | wc -l")
        out = subprocess.run(["strings", so], capture_output=True, text=True).stdout.splitlines()
        print(f"{len(out)} printable strings; {so.stat().st_size} bytes")

    def do_pseudo(self, line: str) -> None:
        """pseudo fn_XX [cfg]      mã giả Ghidra — thứ duy nhất AI được xem"""
        args = line.split()
        print((ARTIFACTS / cfg_arg(args, 1) / f"{fn_arg(args)}.pseudocode.c").read_text().rstrip())

    # ------------------------------------------------------------- phân tích
    def do_analyze(self, line: str) -> None:
        """analyze fn_XX [cfg]     hỏi AI về hàm có sẵn rồi kiểm chứng từng câu"""
        args = line.split()
        cli.run(argparse.Namespace(target=fn_arg(args), config=cfg_arg(args, 1), profile="bytes",
                                   show_pseudo=False))

    def do_mutate(self, line: str) -> None:
        """mutate fn_XX HEX [cfg]  đổi hằng đặc trưng của hàm thành HEX, tạo hàm mới rồi phân tích"""
        args = line.split()
        fn = fn_arg(args)
        if len(args) < 2:
            raise ValueError("cần giá trị hex mới, ví dụ: mutate fn_01 1234ABCD")
        src, note = live.mutate(fn, None, args[1])
        new = live.normalize_hex(args[1])
        path = DATA / "live" / f"mutate-{time.strftime('%Y%m%d-%H%M%S')}.c"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(src)
        print(note)
        for d in difflib.unified_diff((SRC / f"{fn}.c").read_text().splitlines(), src.splitlines(),
                                      f"{fn}.c", path.name, n=0, lineterm=""):
            print(d)
        cli.run(argparse.Namespace(target=str(path), config=cfg_arg(args, 2),
                                   profile=load_manifest(fn)["input_profile"], show_pseudo=False))
        print(f"(mã nguồn hàm mới: {path.relative_to(DATA.parent)}; hằng {new})")

    def do_check(self, line: str) -> None:
        """check FILE.c [profile]  phân tích một file C bất kỳ viết theo VERA_FN(...)"""
        args = shlex.split(line)
        if not args:
            raise ValueError("cần đường dẫn file .c")
        prof = args[1] if len(args) > 1 else "bytes"
        if prof not in PROFILES:
            raise ValueError(f"profile phải là {' / '.join(PROFILES)}")
        cli.run(argparse.Namespace(target=str(Path(args[0]).expanduser()), config="opt", profile=prof,
                                   show_pseudo=False))

    def do_results(self, line: str) -> None:
        """results [fn_XX]         kết quả thí nghiệm E1: cả 20 hàm x 3 cấu hình (hoặc chi tiết một hàm)"""
        run = DATA / "runs" / "E1"
        args = line.split()
        if args:
            fn = fn_arg(args)
            print(f"{fn}  {load_manifest(fn)['algorithm_label']}  (E1, model trả lời lúc chạy thí nghiệm)")
            for c in BUILD_CONFIGS:
                v = e1_item(run, fn, c)
                if v is None:
                    print(f"  {c:5}  AI trả lời sai schema, không chấm")
                    continue
                print(f"  {c:5}  AI: {v['algorithm']!r}  {v['counts']}  V1 {v['v1']}")
                for cl in v["claims"]:
                    if cl["verdict"]["label"] == "contradicted":
                        vd = cl["verdict"]
                        ce = vd.get("counterexample", {})
                        if "oracle_ret" in ce:
                            why = f"binary={ce['expected_ret']} oracle {vd['algorithm']}={ce['oracle_ret']}"
                            if ce["expected_ret"] == ce["oracle_ret"]:  # V1b so cả ret lẫn byte ghi ra out
                                why += " (ret giống nhau, khác ở byte ghi ra out)"
                        else:
                            why = ce.get("observed", "")
                        print(f"         CONTRADICTED {cl['type']:5} {cl['text'][:70]}")
                        print(f"           {vd['method']}: {ce.get('vector', '')} ({ce.get('tag', '')}) {why}")
            return
        print("E1: mỗi ô = câu bị bác/tổng câu | số vector code AI viết lại chạy khớp binary (trên 50)")
        print(f"{'':6}{'':10}{'':24}" + "".join(f"   {c:<17}" for c in BUILD_CONFIGS))
        tot = {"contra": 0, "claims": 0, "fepr1": {c: 0 for c in BUILD_CONFIGS}}
        for fn in FN_IDS:
            m = load_manifest(fn)
            cells = []
            for c in BUILD_CONFIGS:
                v = e1_item(run, fn, c)
                if v is None:
                    cells.append(f"   {'(sai schema)':<17}")
                    continue
                n, k = len(v["claims"]), v["counts"]["contradicted"]
                tot["contra"] += k
                tot["claims"] += n
                tot["fepr1"][c] += v["v1"] == "50/50"
                mark = "!" if k else " "
                cells.append(f" {mark} {f'{k}/{n}':<5}| {v['v1']:<10}")
            print(f"{fn:6}{m['group']:10}{m['algorithm_label'][:23]:24}" + "".join(cells))
        print(f"tổng: {tot['contra']}/{tot['claims']} câu bị bác; code đúng 50/50: "
              + ", ".join(f"{c} {tot['fepr1'][c]}/20" for c in BUILD_CONFIGS))
        print("(! = có câu bị bác; 'results fn_XX' để xem câu nào và bằng chứng)")

    # ------------------------------------------------------------- hệ thống
    def do_status(self, _: str) -> None:
        """status                  kiểm tra lại các thành phần"""
        startup_checks()

    def do_clear(self, _: str) -> None:
        """clear                   xóa màn hình"""
        os.system("clear")

    def do_exit(self, _: str) -> bool:
        """exit                    thoát"""
        return True

    do_quit = do_exit

    def do_EOF(self, _: str) -> bool:
        print()
        return True

    def do_help(self, line: str) -> None:
        if line:
            return super().do_help(line)
        for name in ("list", "source", "diff", "inspect", "pseudo", "results", "analyze", "mutate", "check",
                     "status", "clear", "exit"):
            print("  " + getattr(self, f"do_{name}").__doc__)


def startup_checks() -> bool:
    print("checking components:")
    ok = [check("ollama", ollama), check("docker", docker),
          check("ghidra", lambda: str(ghidra_home())), check("corpus", corpus)]
    return all(ok)


def main() -> None:
    print("VeRA — verification of LLM explanations of binary functions")
    if not startup_checks():
        print("một số thành phần chưa sẵn sàng; sửa rồi gõ status để kiểm tra lại")
    print()
    try:
        Shell().cmdloop()
    except KeyboardInterrupt:
        print()


if __name__ == "__main__":
    main()
