"""Các dạng một hằng có thể xuất hiện trong binary sau khi biên dịch.

Dùng ở hai nơi: sinh trường `encodings` trong manifest (ground truth), và chuẩn hóa
hằng khi V3 so khớp claim với evidence (tuần 3).
"""
from __future__ import annotations


def encodings(value: int, width: int) -> dict[str, str]:
    """Trả các dạng mã hóa của `value` rộng `width` bit (8/16/32/64)."""
    mask = (1 << width) - 1
    v = value & mask
    forms: dict[str, str] = {
        "imm": f"0x{v:0{width // 4}X}",
        "le_bytes": v.to_bytes(width // 8, "little").hex(),
        "neg": f"0x{(-v) & mask:0{width // 4}X}",  # add ↔ sub: compiler có thể dùng số đối
    }
    if v >> (width - 1):
        forms["signed"] = str(v - (1 << width))
        if width < 64:
            forms["sext64"] = f"0x{(v | (~mask & 0xFFFFFFFFFFFFFFFF)):016X}"
    if width == 64:
        forms["hi32"] = f"0x{v >> 32:08X}"
        forms["lo32"] = f"0x{v & 0xFFFFFFFF:08X}"
    if width >= 32:
        forms["hi16"] = f"0x{(v >> 16) & 0xFFFF:04X}"
        forms["lo16"] = f"0x{v & 0xFFFF:04X}"
    return forms
