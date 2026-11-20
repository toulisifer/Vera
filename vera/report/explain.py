"""Diễn giải kết quả kiểm chứng bằng câu tiếng Việt thường và chú thích dòng code — cho demo.

Dùng chung bởi trang web tĩnh (vera.report.web) và demo trực tiếp (vera.webapp). Không đổi
nhãn hay số liệu nào: chỉ diễn đạt lại bằng chứng mà L3 đã tìm ra, cho người không chuyên đọc.
Kèm hàm dịch câu nhận định sang tiếng Việt qua Ollama, có cache theo nội dung.
"""
from __future__ import annotations

import hashlib
import json
import re
import urllib.request

from vera.common import DATA
from vera.llm import client

TAG_VI = {
    "len0": "đầu vào rỗng", "len1": "đầu vào 1 byte", "len3": "đầu vào 3 byte", "len8": "đầu vào 8 byte",
    "len23": "đầu vào 23 byte", "len24": "đầu vào 24 byte", "len64": "đầu vào 64 byte",
    "all00": "32 byte toàn số 0", "allff": "32 byte toàn 0xFF", "cap0": "vùng đầu ra dung lượng 0",
    "cap_half": "vùng đầu ra thiếu chỗ", "cap7_len24": "vùng đầu ra chỉ 7 byte", "arg0": "tham số arg = 0",
    "argmax": "tham số arg lớn nhất",
}
FORM_VI = {
    "imm": "nằm trực tiếp trong một lệnh máy",
    "neg": "dưới dạng số đối (compiler đổi phép cộng thành phép trừ)",
    "table": "trong bảng dữ liệu của chương trình",
    "bswap": "dưới dạng đảo thứ tự byte",
    "split": "bị tách làm hai nửa trong hai lệnh",
    "bytes": "được ghi từng byte một",
    "shift": "dưới dạng phép dịch bit (nhân/chia cho lũy thừa của 2)",
    "magic": "dưới dạng phép nhân “thần kỳ” mà compiler dùng thay cho phép chia",
    "string": "trong vùng chuỗi ký tự của chương trình",
}
WHEN_VI = {"always": "mọi đầu vào", "out_cap < len": "vùng đầu ra nhỏ hơn đầu vào"}


def tag_vi(tag: str | None) -> str:
    if not tag:
        return "một đầu vào"
    return TAG_VI.get(tag) or ("dữ liệu ngẫu nhiên" if tag.startswith("rand") else tag.replace("_", " "))


def when_vi(cond: str) -> str:
    if cond in WHEN_VI:
        return WHEN_VI[cond]
    m = re.fullmatch(r"(len|out_cap|arg) (==|<|>=) (\d+)", cond)
    if not m:
        return cond
    name = {"len": "độ dài đầu vào", "out_cap": "dung lượng vùng đầu ra", "arg": "tham số arg"}[m.group(1)]
    op = {"==": "bằng", "<": "nhỏ hơn", ">=": "từ"}[m.group(2)]
    return f"{name} {op} {m.group(3)}"


def explain(claim: dict, v: dict) -> str:
    """Một câu tiếng Việt: VeRA đã làm gì và vì sao ra nhãn này."""
    lab, method, t = v["label"], v.get("method"), claim.get("type")
    ce = v.get("counterexample") or {}
    if t == "CONST":
        if lab == "supported":
            parts = [f"số {f['value']} {FORM_VI.get(f.get('form'), 'trong binary')}" for f in v.get("found", [])]
            return "VeRA lục trong mã máy và tìm thấy " + "; ".join(parts) + ", nên câu này có bằng chứng."
        if v.get("missing"):
            miss = ", ".join(m["value"] for m in v["missing"])
            return (f"VeRA tìm trong mã máy nhưng không thấy {miss}. Chưa đủ để nói là sai, vì compiler "
                    "có thể đã biến đổi con số này.")
        return ("Con số trong câu quá ngắn hoặc không cụ thể (VeRA chỉ kiểm số đủ dài để tránh trùng ngẫu "
                "nhiên), nên không kiểm.")
    if t == "ALG":
        alg = v.get("algorithm")
        if lab == "verified":
            return (f"AI nói đây là {alg}. VeRA chạy {alg} chuẩn với cùng 50 bộ dữ liệu: cả 50 kết quả giống "
                    "hệt hàm thật, nên câu này đúng.")
        if lab == "contradicted":
            return (f"AI nói đây là {alg}. VeRA chạy {alg} chuẩn với {tag_vi(ce.get('tag'))}: hàm thật trả "
                    f"{ce.get('expected_ret')}, còn {alg} chuẩn trả {ce.get('oracle_ret')}. Hai kết quả khác nhau, "
                    "nên AI gọi sai tên.")
        if v.get("variant_claim"):
            return f"AI chỉ nói hàm “giống” {alg}, không khẳng định là {alg} chuẩn, nên VeRA không bác bỏ."
        if alg:
            return (f"VeRA chưa có cài đặt chuẩn của {alg} để chạy so sánh, nên chỉ kiểm được dấu hiệu tĩnh "
                    "và chưa kết luận.")
        return "Câu không nêu tên một thuật toán cụ thể nào, nên không có gì để chạy so sánh."
    if t == "IO":
        io = v.get("io") or {}
        if lab == "verified":
            return (f"VeRA chạy hàm với các bộ dữ liệu có {when_vi(io.get('when', ''))}: lần nào kết quả cũng "
                    "đúng như AI nói.")
        if lab == "contradicted":
            return (f"Với {tag_vi(ce.get('tag'))}, hàm thật cho kết quả khác điều AI nói "
                    f"({ce.get('observed', '').replace('ret ', 'trả ')}).")
        return ("AI không viết câu này ở dạng máy đọc được (thiếu điều kiện có cấu trúc), nên VeRA không chạy "
                "thử tự động được.")
    if t == "SIDE":
        detail = (v.get("detail") or "") + (ce.get("observed") or "")
        if lab == "contradicted" and "không vector hợp lệ nào ghi out" in detail:
            return ("VeRA chạy hàm 50 lần với 50 bộ dữ liệu khác nhau: không lần nào hàm ghi gì ra vùng đầu ra "
                    "(out). Câu này AI bịa.")
        if lab == "contradicted":
            return f"Với {tag_vi(ce.get('tag'))}, hàm thật có ghi ra vùng đầu ra (out), trái với điều AI nói."
        if lab == "verified" and "không vector nào ghi out" in detail:
            return "VeRA chạy hàm 50 lần: không lần nào hàm ghi ra vùng đầu ra (out), đúng như AI nói."
        if lab == "verified" and "in không đổi" in detail:
            return "Sau 50 lần chạy, dữ liệu đầu vào không bị thay đổi, đúng như AI nói."
        if lab == "verified":
            return ("Hàm có ghi ra vùng đầu ra (out) ở các lần chạy hợp lệ, đúng như AI nói. VeRA chỉ kiểm "
                    "có ghi hay không, chưa kiểm ghi cái gì.")
        return "Câu này nói về tác dụng phụ theo cách VeRA chưa có mẫu để kiểm tự động."
    if t == "CF":
        return "Câu nói về cấu trúc vòng lặp hoặc rẽ nhánh. VeRA chưa có cách tự động kiểm loại câu này."
    return "Câu nói về mục đích hay tên gọi chung. VeRA chưa có cách tự động kiểm loại câu này."


def explain_v1(v1: dict, src_writes_out: bool | None = None) -> str:
    """Diễn giải kết quả chạy mã AI viết lại."""
    if not v1.get("compiled"):
        err = v1.get("err") or v1.get("compile_error") or ""
        if "DAT_" in err:
            return ("Code AI viết lại không biên dịch được: AI chép nguyên tên DAT_… mà Ghidra đặt cho dữ liệu toàn cục "
                    "(bảng tra, hoặc biến của phần làm rối) vào code, nhưng trong code AI biến đó không tồn tại.")
        return "Code AI viết lại không biên dịch được, nên không chạy thử được."
    n, ok = v1.get("n") or v1.get("n_vectors") or 50, v1.get("match") if "match" in v1 else v1.get("n_match")
    if ok == n:
        return f"Code AI viết lại cho kết quả giống hệt hàm thật ở cả {n}/{n} bộ dữ liệu."
    msg = f"Code AI viết lại chỉ đúng {ok}/{n} bộ dữ liệu."
    fails = v1.get("fails") or [{"exp": f["expected_ret"], "got": f["got_ret"]} for f in v1.get("failures", [])]
    if fails and all(f.get("exp") and f.get("got") and f["got"].endswith(f["exp"][-8:])
                     and f["got"][2:10] == "ffffffff" and f["exp"][2:10] == "00000000" for f in fails):
        msg += (" Nửa sau của kết quả luôn đúng, nửa trước bị điền toàn “f”: AI dùng biến 64-bit thay cho 32-bit, "
                "nên phép đảo bit làm hỏng phần thừa.")
    elif fails and all(f.get("exp") and f.get("got") and f["exp"][2:10] == "00000000"
                       and f["got"][2:10] != "00000000" for f in fails):
        f = fails[0]
        msg += (f" Ví dụ: đúng là {f['exp']}, code AI trả {f['got']}. Hàm thật luôn trả số 32-bit (nửa trước toàn 0), "
                "còn code AI trả số có nửa trước khác 0: dấu hiệu AI nhầm số 32-bit với 64-bit (kiểu biến "
                "hoặc ép kiểu).")
    elif fails:
        f = fails[0]
        msg += f" Ví dụ: đúng là {f['exp']}, code AI trả {f['got']}."
    return msg


# ------------------------------------------------------------------ chú thích code
def annotate_pseudo(pseudo: str, claims: list[dict], changed: str | None = None,
                    extra: list[str] | None = None) -> list[dict]:
    """[{line, note, kind}] cho pseudocode: dòng chứa con số AI nhắc tới, và con số bị đổi (demo trực tiếp)."""
    out = []
    lines = pseudo.strip("\n").split("\n")
    asked = {}
    for c in claims:
        for h in re.findall(r"0x[0-9a-fA-F]{3,}", c["text"]):
            asked.setdefault(h.lower(), c)
    for i, ln in enumerate(lines):
        low = ln.lower()
        if changed and changed.lower().replace("0x", "") in low.replace("0x", ""):
            out.append({"line": i, "kind": "key", "note": "con số vừa đổi"})
            continue
        for h, c in asked.items():
            if h in low:
                out.append({"line": i, "kind": c["label"], "note": f"AI nhắc tới {h}"})
                break
        else:
            for e in extra or []:
                if e.lower().startswith("0x") and e.lower() in low:
                    out.append({"line": i, "kind": "key", "note": "con số đáng chú ý"})
                    break
    return out


def annotate_recovered(rc: str, writes_out_truth: bool | None, v1: dict) -> list[dict]:
    out = []
    lines = rc.strip("\n").split("\n")
    sign_bug = "32-bit" in explain_v1(v1)
    for i, ln in enumerate(lines):
        if "DAT_" in ln:
            out.append({"line": i, "kind": "contradicted", "note": "biến Ghidra đặt tên, không tồn tại"})
        elif writes_out_truth is False and re.search(r"\bout\s*\[", ln) and "=" in ln.split("out", 1)[1][:20]:
            out.append({"line": i, "kind": "contradicted", "note": "hàm thật không ghi out"})
        elif sign_bug and re.match(r"\s*(uint64_t|unsigned long|ulong)\s+\w+\s*=", ln):
            out.append({"line": i, "kind": "contradicted", "note": "nghi: lẽ ra là 32-bit"})
    return out


def annotate_source(src: str, highlight: list[str], note: str) -> list[dict]:
    out = []
    for i, ln in enumerate(src.strip("\n").split("\n")):
        if any(h and h.lower().replace("0x", "") in ln.lower().replace("0x", "") for h in highlight):
            out.append({"line": i, "kind": "key", "note": note})
    return out


# ------------------------------------------------------------------ dịch tiếng Việt
TRANS_CACHE = DATA / "demo" / "translations.json"
TRANS_SYSTEM = ("Dịch từng câu sau sang tiếng Việt tự nhiên, dễ hiểu cho người không chuyên. Giữ nguyên các con số hex, "
                "tên thuật toán và tên biến (out, in, len, param_1…). Gợi ý: 'out' là vùng đầu ra, 'len' là độ dài đầu "
                "vào, 'checksum' giữ nguyên. Trả JSON {\"vi\": [...]} đúng số câu, đúng thứ tự.")


def _load_cache() -> dict:
    try:
        return json.loads(TRANS_CACHE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def translate(texts: list[str], model: str = "qwen2.5-coder:7b", save: bool = True) -> list[str]:
    """Dịch các câu tiếng Anh sang tiếng Việt; lỗi gì thì trả lại câu gốc (demo không được dừng vì dịch)."""
    cache = _load_cache()
    key = lambda s: hashlib.sha1(s.encode()).hexdigest()[:16]
    todo = [t for t in dict.fromkeys(texts) if key(t) not in cache]
    if todo:
        body = {"model": model, "stream": False, "options": {"temperature": 0},
                "format": {"type": "object", "properties": {"vi": {"type": "array", "items": {"type": "string"}}},
                           "required": ["vi"]},
                "messages": [{"role": "system", "content": TRANS_SYSTEM},
                             {"role": "user", "content": json.dumps(todo, ensure_ascii=False)}]}
        if "qwen3" in model:
            body["think"] = False
        try:
            req = urllib.request.Request(f"{client.OLLAMA_URL}/api/chat", data=json.dumps(body).encode(),
                                         headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=300) as r:
                vi = json.loads(json.load(r)["message"]["content"])["vi"]
            if len(vi) == len(todo):
                for en, v in zip(todo, vi):
                    cache[key(en)] = v
                if save:
                    TRANS_CACHE.parent.mkdir(parents=True, exist_ok=True)
                    TRANS_CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=0), encoding="utf-8")
        except (OSError, ValueError, KeyError):
            pass
    return [cache.get(key(t), "") for t in texts]


def cached_translation(text: str) -> str:
    return _load_cache().get(hashlib.sha1(text.encode()).hexdigest()[:16], "")
