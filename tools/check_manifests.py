"""Đối chiếu manifest với mã nguồn và vector — chạy trước khi chốt ground truth.

    python tools/check_manifests.py

Kiểm: writes_out khớp việc vector có ghi out; uses_arg khớp việc đổi arg làm đổi kết quả
(chạy lại binary plain với arg khác); hằng/chuỗi đặc trưng có trong source; pair_of chỉ ở near-miss.
"""
from __future__ import annotations

import sys

from vera.common import FN_IDS, SRC, load_manifest, load_vectors, run_vectors, so_path

ERR = "0xffffffffffffffff"


def main() -> None:
    probs = []
    for fn in FN_IDS:
        m = load_manifest(fn)
        src = (SRC / f"{fn}.c").read_text().lower()
        vs = load_vectors(fn)
        io = m["io_semantics"]
        wrote = any(v["out"] != "" for v in vs if v["ret"] != ERR)
        if wrote != io["writes_out"]:
            probs.append(f"{fn}: writes_out={io['writes_out']} nhưng vector cho thấy ghi out={wrote}")
        sub = vs[14:24]
        alt = [dict(v, arg="0x0123456789abcdef") for v in sub]
        r1, r2 = run_vectors(so_path(fn, "plain"), fn, sub), run_vectors(so_path(fn, "plain"), fn, alt)
        varies = any(not a.same_as(b) for a, b in zip(r1, r2))
        if varies != io["uses_arg"]:
            probs.append(f"{fn}: uses_arg={io['uses_arg']} nhưng đổi arg làm đổi kết quả={varies}")
        for c in m["characteristic_constants"]:
            v = int(c["value"], 16)
            if "sau 32 vòng" in c["role"]:
                continue  # hằng suy ra, không nằm nguyên văn trong source
            if f"0x{v:x}" not in src and f"0x{v:08x}" not in src and f"0x{v:016x}" not in src and str(v) not in src:
                probs.append(f"{fn}: hằng {c['value']} không thấy trong source")
        for s in m["characteristic_strings"]:
            if s.lower() not in src:
                probs.append(f"{fn}: chuỗi đặc trưng không có trong source")
        if (m["group"] == "near_miss") != bool(m["pair_of"]):
            probs.append(f"{fn}: pair_of không khớp nhóm")
    print("\n".join(probs) if probs else "[manifest] khớp mã nguồn và vector ở cả 20 hàm")
    sys.exit(1 if probs else 0)


if __name__ == "__main__":
    main()
