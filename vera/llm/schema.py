"""Schema output của LLM, kiểm tra hợp lệ và bộ lọc claim mơ hồ.

Schema được truyền cho Ollama qua tham số `format` (structured output) VÀ được kiểm
lại ở đây, vì model nhỏ vẫn có thể trả giá trị sai kiểu hoặc chuỗi rỗng.
"""
from __future__ import annotations

import re

CLAIM_TYPES = ["ALG", "CONST", "IO", "CF", "SIDE", "NAME"]

# DSL nhỏ cho claim IO (kiểm bằng vector ở tuần 3). Chỉ vài mẫu phổ biến; claim IO
# không có trường io hoặc không parse được thì giữ nhãn unsupported.
IO_WHEN = r"^(always|len == \d+|len < \d+|len >= \d+|out_cap < len|out_cap < \d+|arg == \d+)$"
IO_RETURNS = r"^(len|ERR|0x[0-9a-fA-F]+|\d+)$"

SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
        "proposed_name": {"type": "string"},
        "algorithm": {"type": "string"},
        "self_confidence": {"type": "number"},
        "claims": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "type": {"type": "string", "enum": CLAIM_TYPES},
                    "text": {"type": "string"},
                    "asserted_values": {"type": "array", "items": {"type": "string"}},
                    "confidence": {"type": "number"},
                    "io": {
                        "type": "object",
                        "properties": {
                            "when": {"type": "string"},
                            "returns": {"type": "string"},
                            "writes_out": {"type": "boolean"},
                        },
                    },
                },
                "required": ["id", "type", "text", "asserted_values", "confidence"],
            },
        },
        "recovered_c": {"type": "string"},
    },
    "required": ["summary", "proposed_name", "algorithm", "self_confidence", "claims", "recovered_c"],
}


def validate(doc: object, fn_id: str) -> list[str]:
    """Trả danh sách lỗi; rỗng nghĩa là hợp lệ."""
    errs: list[str] = []
    if not isinstance(doc, dict):
        return ["output không phải object JSON"]
    for key in SCHEMA["required"]:
        if key not in doc:
            errs.append(f"thiếu trường {key}")
    if errs:
        return errs
    for key in ("summary", "proposed_name", "algorithm", "recovered_c"):
        if not isinstance(doc[key], str) or not doc[key].strip():
            errs.append(f"{key} rỗng hoặc sai kiểu")
    if not isinstance(doc["self_confidence"], (int, float)) or not 0 <= doc["self_confidence"] <= 1:
        errs.append("self_confidence phải trong [0, 1]")
    if not isinstance(doc["claims"], list) or not doc["claims"]:
        errs.append("claims rỗng")
    else:
        for i, c in enumerate(doc["claims"]):
            if not isinstance(c, dict):
                errs.append(f"claim {i} không phải object"); continue
            if c.get("type") not in CLAIM_TYPES:
                errs.append(f"claim {i}: type {c.get('type')!r} không hợp lệ")
            if not isinstance(c.get("text"), str) or not c["text"].strip():
                errs.append(f"claim {i}: text rỗng")
            if not isinstance(c.get("asserted_values"), list):
                errs.append(f"claim {i}: asserted_values phải là mảng")
            conf = c.get("confidence")
            if not isinstance(conf, (int, float)) or not 0 <= conf <= 1:
                errs.append(f"claim {i}: confidence phải trong [0, 1]")
    rc = doc.get("recovered_c", "")
    if isinstance(rc, str) and not re.search(rf"\b{fn_id}\s*\(", rc):
        errs.append(f"recovered_c không định nghĩa {fn_id}")
    return errs


HEDGES = re.compile(r"\b(may|might|possibly|probably|likely|seems?|appears?|perhaps|could be|maybe|presumably)\b", re.I)
NUMBER = re.compile(r"0x[0-9a-fA-F]+|\b\d+\b")


def _norm(text: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9 ]", " ", text.lower()).split())


def filter_claims(claims: list[dict]) -> tuple[list[dict], list[dict]]:
    """Loại claim mơ hồ theo hướng dẫn; trả (giữ lại, bị loại kèm lý do)."""
    kept, dropped, seen = [], [], set()
    for c in claims:
        text = c["text"].strip()
        reason = None
        if HEDGES.search(text):
            reason = "rào đón"
        elif len(text.split()) < 4:
            reason = "quá ngắn, không có hành vi cụ thể"
        elif c["type"] == "CONST" and not c["asserted_values"] and not NUMBER.search(text):
            reason = "CONST không nêu giá trị"
        elif _norm(text) in seen:
            reason = "trùng claim khác"
        if reason:
            dropped.append({**c, "drop_reason": reason})
        else:
            seen.add(_norm(text))
            kept.append(c)
    return kept, dropped


def parse_io(c: dict) -> dict | None:
    """Trả trường io nếu đúng DSL, ngược lại None (claim IO giữ nhãn unsupported)."""
    io = c.get("io")
    if not isinstance(io, dict) or not isinstance(io.get("when"), str):
        return None
    when = " ".join(io["when"].split())
    if not re.match(IO_WHEN, when):
        return None
    ret = io.get("returns")
    if ret is not None and not (isinstance(ret, str) and re.match(IO_RETURNS, ret.strip())):
        return None
    if ret is None and not isinstance(io.get("writes_out"), bool):
        return None
    return {"when": when, "returns": ret.strip() if ret else None, "writes_out": io.get("writes_out")}
