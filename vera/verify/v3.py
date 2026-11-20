"""V3 — neo bằng chứng tĩnh cho claim CONST và ALG.

Nhãn V3: supported | unsupported. V3 KHÔNG BAO GIỜ gán contradicted: vắng bằng chứng không
phải là bằng chứng mâu thuẫn (chỉ V1b và kiểm IO/SIDE bằng thực thi mới gán contradicted).

Chuẩn hóa hằng trước khi so khớp (Evidence.find):
  imm      immediate hoặc displacement (lea eax,[rdx-0x61c8864f]) trong lệnh, xét theo mọi
           độ rộng mà giá trị có dấu của nó vừa (mov rax, -1 khớp 0xFFFFFFFF và
           0xFFFFFFFFFFFFFFFF, nhưng 0x12345678 KHÔNG khớp 0x5678)
  neg      số đối (compiler đổi add C thành sub -C)
  bswap    đảo byte (hằng dùng theo big-endian)                         — chỉ ở chế độ CONST
  split    hai nửa cao/thấp cùng có mặt dưới dạng immediate             — chỉ ở chế độ CONST
  table    byte little/big-endian của hằng nằm trong .rodata/.data
  bytes    các byte của hằng được ghi bằng các lệnh mov byte liên tiếp        — chỉ ở chế độ CONST
  shift    lũy thừa của 2 (≥ 2^8) thành lệnh dịch bit shl/sal/shr/sar k       — chỉ ở chế độ CONST
  magic    phép chia/modulo cho hằng d thành phép nhân với đúng ceil(2^s/d)
           (kể cả biến thể "add" lưu magic − 2^32), chỉ tính immediate của lệnh imul/mul
  string   chuỗi nằm trong section dữ liệu
Hằng trong claim chỉ được so ở độ rộng 32 và 64 bit (immediate 8/16 bit được mở rộng lên):
so ở 16 bit làm 65521 = 0xFFF1 "khớp" số đối 15 — nguồn false support đã gặp ở self-test.

Giới hạn đã biết: hằng dạng 2^k ± 1 (vd. modulo 65537) bị -O0/-O2 biến thành chuỗi dịch/cộng
và không còn dấu vết dạng số — cần thực thi ký hiệu, ngoài phạm vi.

Trích số từ claim: chỉ lấy hex từ 3 chữ số hoặc thập phân từ 4 chữ số; bỏ cụm mô tả
("CRC-32", "32-bit", "64 bytes", "8 rounds") trước khi trích.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from vera.verify.fingerprints import FINGERPRINTS

WIDTHS = (8, 16, 32, 64)   # độ rộng dùng để chỉ mục immediate
CLAIM_WIDTHS = (32, 64)    # độ rộng dùng để so hằng của claim
DESCRIPTIVE = re.compile(
    r"\b[A-Za-z]+[-_]?\d+[A-Za-z]*\b"                                         # CRC-32, SHA256, Base64, fn_01
    r"|\b\d+[- ]?(bits?|bytes?|rounds?|times|iterations?|entries|elements|chars?|characters?)\b"
    r"|\b(param|local|uVar|iVar|lVar|bVar|DAT)_?\w*", re.I)
HEX = re.compile(r"-?\b0x([0-9a-fA-F]+)\b")
DEC = re.compile(r"(?<![\w.])-?\d+(?![\w.])")


def qualifying_values(claim: dict) -> tuple[list[int], list[str]]:
    """Số (int, có thể âm) và chuỗi mà claim khẳng định, sau khi lọc theo quy tắc trích số."""
    nums: list[int] = []
    strs: list[str] = []

    def take_number(tok: str) -> None:
        tok = tok.strip().rstrip("uUlL")
        neg = tok.startswith("-")
        body = tok.lstrip("-")
        if body.lower().startswith("0x"):
            digits = body[2:]
            if len(digits.lstrip("0")) >= 3 and re.fullmatch(r"[0-9a-fA-F]+", digits):
                nums.append(-int(digits, 16) if neg else int(digits, 16))
        elif body.isdigit() and len(body) >= 4:
            nums.append(-int(body) if neg else int(body))

    for v in claim.get("asserted_values") or []:
        v = str(v).strip().strip("'\"")
        if re.fullmatch(r"-?(0x[0-9a-fA-F]+|\d+)[uUlL]*", v):
            take_number(v)
        elif re.fullmatch(r"[0-9a-fA-F]{6,16}", v) and not v.isdigit():
            take_number("0x" + v)  # model ghi hằng hex thiếu tiền tố 0x (vd. "cbf29ce484222325")
        elif len(v) >= 4:
            strs.append(v)
    text = DESCRIPTIVE.sub(" ", claim.get("text", ""))
    for m in HEX.finditer(text):
        take_number(m.group())
    for m in DEC.finditer(HEX.sub(" ", text)):
        take_number(m.group())
    # giữ thứ tự, bỏ trùng
    return list(dict.fromkeys(nums)), list(dict.fromkeys(strs))


def _fits(v: int, w: int) -> bool:
    return -(1 << (w - 1)) <= v < (1 << w)


def _bswap(u: int, w: int) -> int:
    return int.from_bytes(u.to_bytes(w // 8, "little"), "big")


@dataclass
class Match:
    form: str
    detail: str


class Evidence:
    """Chỉ mục hóa evidence.json để tra hằng nhanh."""

    def __init__(self, ev: dict):
        self.ev = ev
        self.imm_by_width: dict[int, set[int]] = {w: set() for w in WIDTHS}
        self.mul_imms: list[int] = []      # immediate của imul/mul — ứng viên magic
        self.shift_imms: set[int] = set()  # số bit dịch của shl/sal/shr/sar
        self.byte_imms: list[int] = []     # immediate 8-bit theo thứ tự lệnh
        items = [(i["value"], i["size"] or 8, i["insn"].split()[0]) for i in ev["immediates"]]
        # displacement 32-bit có dấu (lea/địa chỉ) cũng có thể mang hằng
        items += [(d["value"], 8, "disp") for d in ev.get("displacements", [])]
        for value, size, mnem in items:
            bits = size * 8
            u = value & ((1 << bits) - 1)
            sv = u - (1 << bits) if u >> (bits - 1) else u
            for w in WIDTHS:
                if _fits(sv, w):
                    self.imm_by_width[w].add(sv % (1 << w))
                if w >= bits:  # zero-extend lên độ rộng lớn hơn
                    self.imm_by_width[w].add(u)
            if mnem in ("imul", "mul"):
                self.mul_imms.append(u)
            if mnem in ("shl", "sal", "shr", "sar"):
                self.shift_imms.add(u)
            if size == 1 and mnem == "mov":
                self.byte_imms.append(u)
        self.blob = bytes.fromhex("".join(s["hex"] for s in ev["sections"]))
        self.strings = [s["text"] for s in ev["strings"]]

    def _imm(self, u: int, w: int) -> bool:
        return u in self.imm_by_width[w]

    def find(self, v: int, strict: bool = False) -> Match | None:
        for w in CLAIM_WIDTHS:
            if not _fits(v, w):
                continue
            mask = (1 << w) - 1
            u = v & mask
            if self._imm(u, w):
                return Match("imm", f"0x{u:X} ({w}-bit)")
            if self._imm((-u) & mask, w):
                return Match("neg", f"-0x{u:X} xuất hiện dạng 0x{(-u) & mask:X} ({w}-bit)")
            if w >= 32:
                le = u.to_bytes(w // 8, "little")
                if le in self.blob:
                    return Match("table", f"byte LE {le.hex()} trong section dữ liệu")
                if not strict and le[::-1] in self.blob:
                    return Match("table", f"byte BE {le[::-1].hex()} trong section dữ liệu")
                if not strict and self._imm(_bswap(u, w), w):
                    return Match("bswap", f"0x{_bswap(u, w):X}")
        if not strict:
            if v > 0xFFFFFFFF and v < (1 << 64):
                hi, lo = v >> 32, v & 0xFFFFFFFF
                if self._imm(hi, 32) and self._imm(lo, 32):
                    return Match("split", f"hi32 0x{hi:X} + lo32 0x{lo:X}")
            elif 0xFFFF < v <= 0xFFFFFFFF:
                hi, lo = v >> 16, v & 0xFFFF
                if self._imm(hi, 16) and self._imm(lo, 16):
                    return Match("split", f"hi16 0x{hi:X} + lo16 0x{lo:X}")
        if not strict and 0 < v and v & (v - 1) == 0 and v >= 256 and (v.bit_length() - 1) in self.shift_imms:
            return Match("shift", f"dịch {v.bit_length() - 1} bit thay cho nhân/chia {v}")
        if not strict and 0xFFFF < v < (1 << 64):
            nb = (v.bit_length() + 7) // 8
            seq = list(v.to_bytes(nb, "little"))
            for i in range(len(self.byte_imms) - nb + 1):
                if self.byte_imms[i:i + nb] == seq:
                    return Match("bytes", f"{nb} lệnh mov byte liên tiếp {bytes(seq).hex()}")
        m = self._magic(v)
        if m:
            return m
        return None

    def _magic(self, d: int) -> Match | None:
        """Phép chia/modulo cho hằng d được thay bằng nhân với đúng ceil(2^s/d)."""
        if d < 3 or d >= (1 << 32) or d & (d - 1) == 0:
            return None
        for m in self.mul_imms:
            for cand in (m, m + (1 << 32)):  # biến thể "add": magic lưu dạng m − 2^32
                if cand.bit_length() < 20:
                    continue
                for s in range(32, 96):
                    if cand == -(-(1 << s) // d):
                        return Match("magic", f"nhân với 0x{m:X} = ceil(2^{s}/{d})"
                                              + (" − 2^32" if cand != m else ""))
        return None

    def find_string(self, s: str) -> Match | None:
        if any(s in t for t in self.strings) or s.encode(errors="ignore") in self.blob:
            return Match("string", f"'{s[:40]}' trong section dữ liệu")
        return None


def check_const(claim: dict, ev: Evidence) -> dict:
    nums, strs = qualifying_values(claim)
    if not nums and not strs:
        return {"label": "unsupported", "method": "V3", "reason": "không có giá trị đủ điều kiện để kiểm"}
    found, missing = [], []
    for v in nums:
        m = ev.find(v)
        (found if m else missing).append({"value": hex(v) if v >= 0 else f"-0x{-v:X}",
                                          **({"form": m.form, "detail": m.detail} if m else {})})
    for s in strs:
        m = ev.find_string(s)
        (found if m else missing).append({"value": s[:60], **({"form": m.form, "detail": m.detail} if m else {})})
    if missing:  # mọi giá trị claim nêu phải có mặt
        return {"label": "unsupported", "method": "V3", "found": found, "missing": missing}
    return {"label": "supported", "method": "V3", "found": found}


def check_alg(algorithm: str, ev: Evidence) -> dict:
    alts = FINGERPRINTS.get(algorithm)
    if alts is None:
        return {"label": "unsupported", "method": "V3", "reason": f"không có dấu vân tay cho {algorithm}"}
    if not alts:
        return {"label": "unsupported", "method": "V3", "reason": f"{algorithm} không có hằng đặc trưng"}
    for alt in alts:
        hits = []
        for item in alt:
            m = ev.find_string(item) if isinstance(item, str) else ev.find(item, strict=True)
            if not m:
                break
            hits.append({"value": item if isinstance(item, str) else hex(item), "form": m.form})
        else:
            return {"label": "supported", "method": "V3", "fingerprint": hits}
    return {"label": "unsupported", "method": "V3", "reason": f"thiếu hằng đặc trưng của {algorithm}"}
