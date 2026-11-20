"""Demo từng bước VeRA trên MỘT hàm của corpus — dùng khi trình bày trước hội đồng.

    python -m vera.demo fn_08 opt            # nhấn Enter để sang bước tiếp
    python -m vera.demo fn_08 opt --no-pause # chạy liền một mạch

Đi qua 5 lớp: pseudocode Ghidra (L1) → phân tích của LLM (L2) → gán nhãn từng claim (L3, kèm
vector phản ví dụ) → chạy mã khôi phục trong sandbox Docker (V1) → lộ đáp án (ground truth).
Phân tích LLM lấy từ cache nếu đã có (cùng prompt, cùng model) nên không cần GPU; chưa có thì
gọi Ollama (đặt VERA_OLLAMA). V1 luôn chạy thật trong Docker.

Phần hiển thị (`present`) dùng chung với demo trực tiếp `vera.live`.
"""
from __future__ import annotations

import argparse
import sys
import textwrap

from vera.common import ARTIFACTS, SRC, load_manifest
from vera.llm import client
from vera.llm.schema import filter_claims
from vera.verify.label import label_item
from vera.verify.v1 import verify

C = {"verified": "\033[1;32m", "supported": "\033[32m", "unsupported": "\033[33m", "contradicted": "\033[1;31m",
     "h": "\033[1;36m", "dim": "\033[2m", "b": "\033[1m", "0": "\033[0m"}
VI = {"verified": "ĐÃ KIỂM CHỨNG", "supported": "CÓ BẰNG CHỨNG", "unsupported": "CHƯA KIỂM ĐƯỢC", "contradicted": "SAI"}
PAUSE = True


def step(title: str) -> None:
    if PAUSE:
        input(f"\n{C['dim']}[Enter để tiếp]{C['0']}")
    print(f"\n{C['h']}{'═' * 78}\n {title}\n{'═' * 78}{C['0']}")


def show_code(text: str, limit: int = 40) -> None:
    lines = text.strip("\n").splitlines()
    for ln in lines[:limit]:
        print(f"  {C['dim']}│{C['0']} {ln}")
    if len(lines) > limit:
        print(f"  {C['dim']}│ … ({len(lines) - limit} dòng nữa){C['0']}")


def evidence_text(v: dict) -> str:
    ce = v.get("counterexample")
    if ce:
        if ce.get("oracle_ret"):
            return f"vector {ce['vector']} ({ce.get('tag')}): binary thật trả {ce['expected_ret']}, cài đặt chuẩn trả {ce['oracle_ret']}"
        where = f"vector {ce['vector']}" + (f" ({ce['tag']})" if ce.get("tag") else "") if ce.get("vector") else "50 vector"
        return f"{where}: thực tế {ce.get('observed', '')}"
    if v.get("found"):
        return "tìm thấy trong binary: " + "; ".join(f"{f['value']} ({f.get('form')})" for f in v["found"])[:110]
    return v.get("detail") or v.get("reason") or ""


def present(fn: str, cfg: str, pseudo: str, res: dict, ev=None, vectors=None, truth=None, intro: str = "") -> None:
    """In 5 bước. truth = (tiêu đề, mô tả, mã nguồn) cho bước đáp án."""
    print(f"{C['b']}VeRA — kiểm chứng lời giải thích của LLM cho hàm nhị phân {fn} (cấu hình {cfg}){C['0']}")
    print(f"{C['dim']}{intro or 'Analyst chỉ có binary đã strip; VeRA kiểm từng câu nhận định của AI bằng bằng chứng.'}{C['0']}")

    step("1. Ghidra dịch ngược binary thành pseudocode (thứ duy nhất AI được đọc)")
    show_code(pseudo)

    step("2. AI giải thích hàm thành các câu nhận định (claim)")
    last = res["attempts"][-1]
    src = "cache" if last["cached"] else f"gọi trực tiếp, {last['seconds']} giây"
    out = res["output"] or {}
    print(f"  Model {C['b']}{res['model']}{C['0']} ({src}), prompt {res['prompt_version']}")
    if not res["schema_valid"]:
        print(f"  {C['contradicted']}AI trả lời sai định dạng sau 2 lần thử:{C['0']} {last['errors'][:2]}")
        return
    print(f"  Thuật toán AI nêu: {C['b']}{out.get('algorithm')}{C['0']}   tên đề xuất: {out.get('proposed_name')}")
    print(f"  Tóm tắt: {textwrap.shorten(out.get('summary', ''), 140)}")
    kept, dropped = filter_claims(out["claims"])
    for c in kept:
        print(f"   • [{c['type']:5}] {c['text']}  {C['dim']}(AI tự tin {c['confidence']}){C['0']}")
    if dropped:
        print(f"  {C['dim']}({len(dropped)} câu mơ hồ bị bộ lọc loại){C['0']}")
    print(f"\n  {C['b']}Câu nào AI nói sai?{C['0']}")

    step("3. VeRA chấm từng câu bằng bằng chứng (hằng trong binary, thuật toán chuẩn, đầu vào thật)")
    verdicts = label_item({**res, "fn": fn, "config": cfg, "claims": kept}, ev=ev, vectors=vectors)
    for c in verdicts["claims"]:
        v = c["verdict"]
        lab = v["label"]
        print(f"  {C[lab]}{VI[lab]:15}{C['0']} [{c['type']:5}] {textwrap.shorten(c['text'], 70)}")
        e = evidence_text(v)
        if e:
            print(f"  {'':15}  {C['dim']}↳ {v.get('method', '')}: {e}{C['0']}")
    n = verdicts["counts"]
    print(f"\n  Tổng: {C['verified']}{n['verified']} đã kiểm chứng{C['0']}, {C['supported']}{n['supported']} có bằng chứng{C['0']}, "
          f"{C['unsupported']}{n['unsupported']} chưa kiểm được{C['0']}, {C['contradicted']}{n['contradicted']} sai{C['0']}"
          f"   (chỉ 'sai' mới gọi là hallucination)")

    step("4. Chạy mã C mà AI viết lại, trong Docker, trên 50 đầu vào — so với binary gốc")
    show_code(out.get("recovered_c", ""), limit=25)
    print(f"  {C['dim']}… đang chạy trong Docker (không mạng, chỉ đọc, giới hạn tài nguyên){C['0']}")
    r = verify({**res, "fn": fn, "config": cfg}, vectors=vectors)
    if not r["compiled"]:
        print(f"  {C['contradicted']}Không biên dịch được:{C['0']} {r.get('compile_error')}")
    else:
        col = C["verified"] if r["fepr"] == 1.0 else C["contradicted"]
        print(f"  Kết quả: {col}{r['n_match']}/{r['n_vectors']} đầu vào cho kết quả giống binary gốc{C['0']}")
        for f in r["failures"][:3]:
            print(f"   {C['dim']}✗ vector {f['vector']} ({f['tag']}): đúng là {f['expected_ret']}, mã AI trả {f['got_ret']}{C['0']}")

    if truth:
        title, desc, source = truth
        step("5. Đáp án (VeRA không dùng phần này khi chấm)")
        print(f"  {C['b']}{title}{C['0']}")
        if desc:
            print(textwrap.fill(desc, 100, initial_indent="  ", subsequent_indent="  "))
        print()
        show_code(source, limit=30)
    print(f"\n{C['b']}Hết demo.{C['0']}")


def main() -> None:
    global PAUSE
    ap = argparse.ArgumentParser()
    ap.add_argument("fn", nargs="?", default="fn_08")
    ap.add_argument("config", nargs="?", default="opt", choices=["plain", "opt", "obf"])
    ap.add_argument("--no-pause", action="store_true")
    a = ap.parse_args()
    PAUSE = not a.no_pause and sys.stdin.isatty()
    pseudo = (ARTIFACTS / a.config / f"{a.fn}.pseudocode.c").read_text()
    res = client.analyze(a.fn, pseudo, "ghidra")
    m = load_manifest(a.fn)
    truth = (f"{m['algorithm_label']} — nhóm {m['group']}",
             (m.get("difference_from_standard") or "") + " " + m["description"], (SRC / f"{a.fn}.c").read_text())
    present(a.fn, a.config, pseudo, res, truth=truth)


if __name__ == "__main__":
    main()
