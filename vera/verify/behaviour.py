"""Kiểm chứng bằng thực thi ở mức claim: V1b (oracle tham chiếu) và claim IO/SIDE.

Cả hai dùng 50 vector đã có output kỳ vọng của binary gốc (data/vectors), nên không phải
chạy lại binary. Đây là nơi DUY NHẤT sinh nhãn "contradicted" (có vector làm phản ví dụ)
và nhãn "verified" (đúng trên mọi vector liên quan).
"""
from __future__ import annotations

import re

from vera.common import VERA_ERR
from vera.corpus.vectors import pad_out
from vera.llm.schema import parse_io
from vera.oracles import ORACLES


def _vec_ret(v: dict) -> int:
    return int(v["ret"], 16)


def _vec_len(v: dict) -> int:
    return len(v["in"]) // 2


def _wrote_out(v: dict) -> bool:
    return v["out"] != ""  # out được tô 0xCC; chuỗi rỗng sau khi cắt = không ghi byte nào


# ---------------------------------------------------------------- V1b
def check_oracle(algorithm: str, vectors: list[dict]) -> dict | None:
    """Chạy cài đặt tham chiếu của thuật toán model nêu. None nếu không có oracle."""
    o = ORACLES.get(algorithm)
    if o is None:
        return None
    for v in vectors:
        ret, out = o.run(bytes.fromhex(v["in"]), int(v["arg"], 16), v["out_cap"])
        if f"0x{ret:016x}" != v["ret"] or out.hex() != pad_out(v["out"], v["out_cap"]):
            return {"label": "contradicted", "method": "V1b",
                    "counterexample": {"vector": v["id"], "tag": v["tag"], "expected_ret": v["ret"],
                                       "oracle_ret": f"0x{ret:016x}"}}
    return {"label": "verified", "method": "V1b", "detail": f"oracle {algorithm} khớp {len(vectors)}/{len(vectors)} vector"}


# ---------------------------------------------------------------- IO
def _when(cond: str, v: dict) -> bool:
    n = _vec_len(v)
    if cond == "always":
        return True
    if cond == "out_cap < len":
        return v["out_cap"] < n
    m = re.fullmatch(r"(len|out_cap|arg) (==|<|>=) (\d+)", cond)
    lhs = {"len": n, "out_cap": v["out_cap"], "arg": int(v["arg"], 16)}[m.group(1)]
    rhs = int(m.group(3))
    return {"==": lhs == rhs, "<": lhs < rhs, ">=": lhs >= rhs}[m.group(2)]


def _expected(ret: str, v: dict) -> int:
    if ret == "len":
        return _vec_len(v)
    if ret == "ERR":
        return VERA_ERR
    return int(ret, 16) if ret.lower().startswith("0x") else int(ret)


def check_io(claim: dict, vectors: list[dict]) -> dict:
    io = parse_io(claim)
    if io is None:
        return {"label": "unsupported", "method": "IO", "reason": "không có trường io đúng DSL"}
    rel = [v for v in vectors if _when(io["when"], v)]
    if not rel:
        return {"label": "unsupported", "method": "IO", "reason": f"không vector nào thỏa '{io['when']}'"}
    for v in rel:
        bad = []
        if io["returns"] is not None and _vec_ret(v) != _expected(io["returns"], v) & VERA_ERR:
            bad.append(f"ret {v['ret']}")
        if io["writes_out"] is not None and _wrote_out(v) != io["writes_out"]:
            bad.append("có ghi out" if _wrote_out(v) else "không ghi out")
        if bad:
            return {"label": "contradicted", "method": "IO", "io": io,
                    "counterexample": {"vector": v["id"], "tag": v["tag"], "observed": ", ".join(bad)}}
    return {"label": "verified", "method": "IO", "io": io, "detail": f"đúng trên {len(rel)} vector thỏa điều kiện"}


# ---------------------------------------------------------------- SIDE
NEG = r"(does not|doesn't|do not|never|not|no|without)"
OUT = r"(\bout\b|output buffer|output parameter|\bout\[|out buffer)"
SIDE_NO_WRITE = re.compile(rf"{NEG}\s+(\w+\s+){{0,2}}(writ\w*|modif\w*|touch\w*|us\w*)\s+(\w+\s+){{0,5}}{OUT}", re.I)
SIDE_NO_OUTPUT_AT_ALL = re.compile(rf"{NEG}\s+(\w+\s+){{0,2}}(modify|modifies|touch\w*)\s+(the\s+)?(input\s+)?or\s+(the\s+)?output", re.I)
SIDE_WRITE = re.compile(rf"\b(writes?|stores?|copies|fills?|encodes? \w+ into|puts?)\b.*{OUT}", re.I)
SIDE_IN_UNCHANGED = re.compile(rf"{NEG}\s+(\w+\s+){{0,2}}modif\w*\s+(the\s+)?(\bin\b|input)", re.I)


def check_side(claim: dict, vectors: list[dict]) -> dict:
    """Chỉ hai mẫu đơn giản về out (có/không ghi) và một mẫu về in; còn lại unsupported."""
    text = claim["text"]
    ok_vs = [v for v in vectors if v["ret"] != f"0x{VERA_ERR:016x}"]
    any_write = any(_wrote_out(v) for v in ok_vs)
    if SIDE_NO_WRITE.search(text) or SIDE_NO_OUTPUT_AT_ALL.search(text):
        if any_write:
            v = next(v for v in ok_vs if _wrote_out(v))
            return {"label": "contradicted", "method": "SIDE",
                    "counterexample": {"vector": v["id"], "tag": v["tag"], "observed": "hàm có ghi out"}}
        return {"label": "verified", "method": "SIDE", "detail": "không vector nào ghi out"}
    if SIDE_WRITE.search(text):
        if not any_write:
            return {"label": "contradicted", "method": "SIDE",
                    "counterexample": {"vector": ok_vs[0]["id"] if ok_vs else None,
                                       "observed": "không vector hợp lệ nào ghi out"}}
        return {"label": "verified", "method": "SIDE", "detail": "hàm có ghi out trên vector hợp lệ"}
    if SIDE_IN_UNCHANGED.search(text):
        # runner kiểm in_changed khi sinh vector; corpus bảo đảm không hàm nào sửa in.
        return {"label": "verified", "method": "SIDE", "detail": "in không đổi trên mọi vector (runner kiểm)"}
    return {"label": "unsupported", "method": "SIDE", "reason": "mẫu câu ngoài phạm vi kiểm tự động"}
