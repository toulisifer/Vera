"""Kiểm tra chất lượng corpus (một phần của E0) và xuất phụ lục data/corpus_report.md.

    python -m vera.corpus.check

1. Oracle: hàm kinh điển phải khớp oracle của nó trên cả 50 vector; hàm near-miss phải
   KHÁC oracle của hàm cặp; không hàm near-miss/tự thiết kế nào được khớp trọn một oracle
   bất kỳ trong thư viện (nếu khớp, nó thực ra là thuật toán có tên).
2. Obfuscation còn sống sau -O2: đếm lệnh, lệnh nhảy có điều kiện và basic block của
   fn_XX trong bản opt và obf (capstone). Tiêu chí: obf có ≥ 30% lệnh nhảy có điều kiện
   nhiều hơn opt.
3. Tên hàm/đường dẫn không lộ thuật toán trong chuỗi của binary.
"""
from __future__ import annotations

import json
import sys

from capstone import CS_ARCH_X86, CS_MODE_64, CS_GRP_JUMP, CS_GRP_RET, Cs

from vera.common import BIN, CONFIGS, DATA, FN_IDS, load_manifest, load_vectors, so_path
from vera.corpus.vectors import pad_out
from vera.elfutil import load
from vera.oracles import ORACLES

OBF_MIN_RATIO = 1.30
LEAK_WORDS = ["crc", "fnv", "adler", "djb", "tea", "rc4", "base64", "rle", "tlv", "bracket"]


# ------------------------------------------------------------------ oracle
def oracle_matches(oracle_name: str, fn_id: str) -> int:
    """Số vector mà oracle cho đúng (ret, out) như binary gốc."""
    o = ORACLES[oracle_name]
    n = 0
    for v in load_vectors(fn_id):
        ret, out = o.run(bytes.fromhex(v["in"]), int(v["arg"], 16), v["out_cap"])
        if f"0x{ret:016x}" == v["ret"] and out.hex() == pad_out(v["out"], v["out_cap"]):
            n += 1
    return n


def check_oracles() -> tuple[list[str], list[str]]:
    rows, errors = [], []
    for fn_id in FN_IDS:
        man = load_manifest(fn_id)
        matches = {name: oracle_matches(name, fn_id) for name in ORACLES}
        full = [k for k, n in matches.items() if n == 50]
        if man["group"] == "classic":
            own = matches[man["oracle"]]
            ok = own == 50 and full == [man["oracle"]]
            note = f"oracle {man['oracle']}: {own}/50"
        else:
            pair = load_manifest(man["pair_of"])["oracle"] if man["pair_of"] else None
            ok = not full
            note = f"oracle cặp {pair}: {matches[pair]}/50" if pair else "—"
        best = max(matches, key=matches.get)
        rows.append(f"| {fn_id} | {man['group']} | {note} | {best} ({matches[best]}/50) | {'✅' if ok else '❌'} |")
        if not ok:
            errors.append(f"{fn_id}: oracle khớp trọn = {full}")
    return rows, errors


# ------------------------------------------------------- obfuscation survival
def cfg_stats(so) -> dict:
    obj = load(so)
    code, addr = obj.code, obj.fn_addr
    md = Cs(CS_ARCH_X86, CS_MODE_64)
    md.detail = True
    insns = list(md.disasm(code, addr))
    jcc = 0
    leaders = {addr}
    for i, ins in enumerate(insns):
        if ins.group(CS_GRP_JUMP) or ins.group(CS_GRP_RET):
            if ins.mnemonic != "jmp" and ins.group(CS_GRP_JUMP):
                jcc += 1
            if ins.operands and ins.op_str.startswith("0x"):
                leaders.add(int(ins.op_str, 16))
            if i + 1 < len(insns):
                leaders.add(insns[i + 1].address)
    return {"insns": len(insns), "jcc": jcc, "blocks": len(leaders), "bytes": len(code)}


def check_obfuscation() -> tuple[list[str], list[str], dict]:
    rows, errors, stats = [], [], {}
    for fn_id in FN_IDS:
        s = {c: cfg_stats(so_path(fn_id, c)) for c in CONFIGS}
        stats[fn_id] = s
        ratio = s["obf"]["jcc"] / max(s["opt"]["jcc"], 1)
        ok = ratio >= OBF_MIN_RATIO
        rows.append(f"| {fn_id} | {s['plain']['insns']} | {s['opt']['insns']} / {s['opt']['jcc']} / {s['opt']['blocks']} "
                    f"| {s['obf']['insns']} / {s['obf']['jcc']} / {s['obf']['blocks']} | {ratio:.2f} | {'✅' if ok else '❌'} |")
        if not ok:
            errors.append(f"{fn_id}: obf/opt jcc = {ratio:.2f} < {OBF_MIN_RATIO}")
    return rows, errors, stats


# ------------------------------------------------------------------- leaks
def check_leaks() -> list[str]:
    errors = []
    for c in CONFIGS:
        for fn_id in FN_IDS:
            blob = so_path(fn_id, c).read_bytes().lower()
            for w in LEAK_WORDS:
                if w.encode() in blob:
                    errors.append(f"{fn_id}/{c}: chuỗi '{w}' xuất hiện trong binary")
    return errors


def main() -> None:
    o_rows, o_err = check_oracles()
    b_rows, b_err, stats = check_obfuscation()
    l_err = check_leaks()
    build = json.loads((DATA / "build_info.json").read_text())
    md = [
        "# Phụ lục — kiểm tra chất lượng corpus",
        "",
        f"Sinh bởi `python -m vera.corpus.check`. Compiler: `{build['gcc']}`.",
        "",
        "## A. Đối chiếu oracle tham chiếu (50 vector mỗi hàm)",
        "",
        "Hàm kinh điển phải khớp đúng oracle của nó; near-miss và tự thiết kế không được khớp trọn oracle nào.",
        "",
        "| Hàm | Nhóm | Oracle liên quan | Oracle khớp nhiều nhất | Đạt |",
        "|---|---|---|---|---|",
        *o_rows,
        "",
        "## B. Obfuscation còn tồn tại sau -O2",
        "",
        f"Số lệnh / lệnh nhảy có điều kiện / basic block của fn_XX (capstone). Tiêu chí: jcc(obf) ≥ {OBF_MIN_RATIO:.2f} × jcc(opt).",
        "",
        "| Hàm | plain: lệnh | opt: lệnh / jcc / block | obf: lệnh / jcc / block | jcc obf/opt | Đạt |",
        "|---|---|---|---|---|---|",
        *b_rows,
        "",
        "## C. Rò rỉ tên thuật toán trong binary",
        "",
        "Không có." if not l_err else "\n".join(f"- {e}" for e in l_err),
        "",
    ]
    (DATA / "corpus_report.md").write_text("\n".join(md), encoding="utf-8")
    (DATA / "cfg_stats.json").write_text(json.dumps(stats, indent=1) + "\n", encoding="utf-8")
    print("\n".join(md))
    errors = o_err + b_err + l_err
    if errors:
        print("\n[check] KHÔNG ĐẠT:\n  " + "\n  ".join(errors))
        sys.exit(1)
    print("[check] corpus đạt mọi tiêu chí")


if __name__ == "__main__":
    main()
