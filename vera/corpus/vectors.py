"""Sinh 50 vector I/O mỗi hàm và lấy output kỳ vọng từ bản plain.

    python -m vera.corpus.vectors

Output kỳ vọng lấy từ binary plain, rồi đối chiếu với opt và obf: ba cấu hình phải
cho kết quả giống hệt, nếu không thì obfuscation đã làm đổi ngữ nghĩa (lỗi corpus).

Định dạng data/vectors/fn_XX.json — arg/ret là chuỗi hex để không mất độ chính xác
64-bit ở ngôn ngữ khác; `out` là nội dung out_cap byte (khởi tạo 0xCC) đã cắt các
cặp "cc" ở cuối (khôi phục bằng pad_out).
"""
from __future__ import annotations

import hashlib
import json
import random
import sys

from vera.common import CONFIGS, FN_IDS, N_VECTORS, VECTORS, load_manifest, run_vectors, so_path

MAX64 = 0xFFFFFFFFFFFFFFFF


def default_cap(n: int) -> int:
    return 2 * n + 64  # đủ cho mọi hàm ghi out (Base64 cần 4n/3, RLE tối đa 2n)


def pad_out(out: str, out_cap: int) -> str:
    return out + "cc" * (out_cap - len(out) // 2)


def trim_out(out: str) -> str:
    while out.endswith("cc"):
        out = out[:-2]
    return out


# ------------------------------------------------------------- input profile
def gen_bytes(r: random.Random, n: int) -> bytes:
    return bytes(r.getrandbits(8) for _ in range(n))


def gen_text(r: random.Random, n: int) -> bytes:
    alphabet = b"abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.,:;-_/"
    return bytes(r.choice(alphabet) for _ in range(n))


def gen_runs(r: random.Random, n: int) -> bytes:
    res = bytearray()
    while len(res) < n:
        res += bytes([r.getrandbits(8)]) * r.choice([1, 1, 2, 3, 5, 8, 40, 255, 256, 300])
    return bytes(res[:n])


def gen_tlv(r: random.Random, n: int) -> bytes:
    """Chuỗi TLV hợp lệ dài khoảng n; 25% bị cắt cụt, 15% có terminator 0x00 và rác phía sau."""
    res = bytearray()
    while len(res) < n:
        k = r.randint(0, 20)
        res += bytes([r.randint(1, 255), k]) + gen_bytes(r, k)
    roll = r.random()
    if roll < 0.25 and len(res) > 2:
        res = res[: r.randint(1, len(res) - 1)]
    elif roll < 0.40:
        res += b"\x00" + gen_bytes(r, r.randint(0, 10))
    return bytes(res)


def gen_brackets(r: random.Random, n: int) -> bytes:
    """Chuỗi ngoặc cân bằng có chuỗi "..." và ký tự thoát; 50% bị làm hỏng một byte."""
    pairs = {"(": ")", "[": "]", "{": "}"}
    res, st = [], []
    while len(res) < n:
        roll = r.random()
        if roll < 0.35 and len(st) < 60:
            o = r.choice("([{")
            res.append(o); st.append(pairs[o])
        elif roll < 0.65 and st:
            res.append(st.pop())
        elif roll < 0.75:
            res.append('"' + "".join(r.choice(['a', '(', ']', '\\"', '\\\\', 'x']) for _ in range(r.randint(0, 4))) + '"')
        else:
            res.append(r.choice("abxyz ,;"))
    res += reversed(st)
    s = bytearray("".join(res).encode())
    if r.random() < 0.5 and s:
        s[r.randrange(len(s))] = ord(r.choice(')]}("\\'))
    return bytes(s)


PROFILES = {"bytes": gen_bytes, "text": gen_text, "runs": gen_runs, "tlv": gen_tlv, "brackets": gen_brackets}


def extras(profile: str) -> list[tuple[str, bytes]]:
    """Vector biên riêng cho từng profile, để phủ các nhánh hiếm."""
    if profile == "runs":
        return [("run_255", b"\x41" * 255), ("run_256", b"\x41" * 256), ("run_600", b"\x00" * 600)]
    if profile == "tlv":
        return [("tlv_empty_value", b"\x07\x00"), ("tlv_hdr_cut", b"\x07"), ("tlv_val_cut", b"\x07\x05abc"),
                ("tlv_term_first", b"\x00\x07\x01a"), ("tlv_max_value", b"\x09\xff" + bytes(255))]
    if profile == "brackets":
        return [("nest_64", b"(" * 64 + b")" * 64), ("nest_65", b"(" * 65 + b")" * 65),
                ("unterminated_str", b'("abc'), ("escaped_quote", b'["a\\"]"]'), ("mismatch", b"(]")]
    return []


# ------------------------------------------------------------------ vector
def make_vectors(fn_id: str, profile: str) -> list[dict]:
    seed = int(hashlib.sha256(f"vera-vectors-{fn_id}".encode()).hexdigest()[:16], 16)
    r = random.Random(seed)
    gen = PROFILES[profile]
    vs: list[tuple[str, bytes, int, int]] = []  # (tag, in, arg, out_cap)

    def add(tag: str, data: bytes, arg: int | None = None, cap: int | None = None) -> None:
        vs.append((tag, data, r.getrandbits(64) if arg is None else arg,
                   default_cap(len(data)) if cap is None else cap))

    # Edge case bắt buộc theo hướng dẫn: len 0/1, biên khối, toàn 0x00/0xFF, out_cap thiếu, arg 0/max.
    add("len0", b"")
    add("len1", gen(r, 1)[:1] or b"\x00")
    add("len3", gen(r, 3)[:3])
    add("len8", gen(r, 8)[:8])
    add("len23", gen(r, 23)[:23])
    add("len24", gen(r, 24)[:24])
    add("len64", gen(r, 64)[:64])
    add("all00", b"\x00" * 32)
    add("allff", b"\xff" * 32)
    add("cap0", gen(r, 16), cap=0)
    add("cap_half", gen(r, 16), cap=8)
    add("cap7_len24", gen(r, 24)[:24], cap=7)
    add("arg0", gen(r, 40), arg=0)
    add("argmax", gen(r, 40), arg=MAX64)
    for tag, data in extras(profile):
        add(tag, data)
    while len(vs) < N_VECTORS:
        n = r.choice([r.randint(2, 32), r.randint(33, 128), r.randint(129, 300)])
        add(f"rand{len(vs):02d}", gen(r, n))
    return [{"id": f"v{i:02d}", "tag": tag, "in": data.hex(), "arg": arg, "out_cap": cap}
            for i, (tag, data, arg, cap) in enumerate(vs[:N_VECTORS])]


def main() -> None:
    VECTORS.mkdir(parents=True, exist_ok=True)
    failed = False
    for fn_id in FN_IDS:
        man = load_manifest(fn_id)
        vs = make_vectors(fn_id, man["input_profile"])
        results = {c: run_vectors(so_path(fn_id, c), fn_id, vs) for c in CONFIGS}
        for i, (v, ref) in enumerate(zip(vs, results["plain"])):
            if ref.status != "OK" or ref.in_changed or ref.overflow:
                print(f"[vectors] {fn_id} {v['id']} ({v['tag']}): plain {ref}"); failed = True
            for c in CONFIGS[1:]:
                if not results[c][i].same_as(ref):
                    print(f"[vectors] {fn_id} {v['id']}: {c} khác plain"); failed = True
            v["ret"] = f"0x{ref.ret:016x}" if ref.ret is not None else None
            v["out"] = trim_out(ref.out or "")
            v["arg"] = f"0x{v['arg']:016x}"
        n_err = sum(1 for v in vs if v["ret"] == "0xffffffffffffffff")
        doc = {"fn": fn_id, "profile": man["input_profile"], "source_config": "plain",
               "cross_checked": CONFIGS, "vectors": vs}
        (VECTORS / f"{fn_id}.json").write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")
        print(f"[vectors] {fn_id}: {len(vs)} vector, {n_err} trả VERA_ERR, 3 cấu hình khớp")
    if failed:
        sys.exit("[vectors] CÓ LỖI — xem ở trên")


if __name__ == "__main__":
    main()
