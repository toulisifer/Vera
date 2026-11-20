"""Bảng dấu vân tay hằng cho claim ALG (V3) và nhận diện tên thuật toán trong claim.

Mỗi thuật toán có một hoặc nhiều phương án; một phương án là tập hằng/chuỗi BẮT BUỘC có mặt
đồng thời. Chỉ đưa vào hằng "mạnh" (không phải 0xFF, 0xFFFFFFFF...), và khớp theo chế độ chặt
hơn CONST (không chấp nhận đảo byte hay hằng bị tách đôi), để tránh trùng dấu vân tay ngẫu nhiên.

Thuật toán không có hằng đặc trưng (RC4, sdbm, Fletcher) có danh sách rỗng: V3 luôn trả
unsupported, và chỉ V1b (oracle) mới kết luận được.
"""
from __future__ import annotations

import re

B64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"

FINGERPRINTS: dict[str, list[list[int | str]]] = {
    "CRC-32": [[0xEDB88320], [0x04C11DB7], [0x77073096]],
    "CRC-32C": [[0x82F63B78], [0x1EDC6F41]],
    "CRC-32/BZIP2": [[0x04C11DB7]],
    "CRC-16/ARC": [[0xA001], [0x8005]],
    "CRC-16/CCITT-FALSE": [[0x1021]],
    "CRC-16/XMODEM": [[0x1021]],
    "CRC-16/KERMIT": [[0x8408]],
    "FNV-1a-64": [[0xCBF29CE484222325, 0x100000001B3]],
    "FNV-1-64": [[0xCBF29CE484222325, 0x100000001B3]],
    "FNV-1a-32": [[0x811C9DC5, 0x01000193]],
    "Adler-32": [[65521]],
    "Fletcher-32": [],
    "djb2": [[5381]],
    "djb2-xor": [[5381]],
    "sdbm": [],
    "TEA": [[0x9E3779B9], [0xC6EF3720]],
    "XTEA": [[0x9E3779B9], [0xC6EF3720]],
    "RC4": [],
    "Base64": [[B64 + "+/"]],
    "Base64url": [[B64 + "-_"]],
    # Không có oracle, nhưng model hay đoán nhầm sang các thuật toán này.
    "MD5": [[0xD76AA478, 0xE8C7B756]],
    "SHA-1": [[0x5A827999, 0x6ED9EBA1]],
    "SHA-256": [[0x428A2F98, 0x71374491]],
    "MurmurHash": [[0x5BD1E995], [0xCC9E2D51, 0x1B873593]],
    "xxHash32": [[0x9E3779B1, 0x85EBCA77]],
}

# Nhóm thuật toán có cùng dấu vân tay: V3 không phân biệt được, chỉ V1b phân biệt.
SAME_FINGERPRINT = [{"FNV-1a-64", "FNV-1-64"}, {"djb2", "djb2-xor"}, {"TEA", "XTEA"}, {"CRC-32", "CRC-32/BZIP2"},
                    {"CRC-16/CCITT-FALSE", "CRC-16/XMODEM"}]

# Tên thuật toán trong văn bản -> tên chuẩn. Thứ tự quan trọng: mẫu cụ thể đứng trước.
NAME_PATTERNS: list[tuple[str, str]] = [
    (r"crc[-_ ]?32[-_ /]?c\b|castagnoli", "CRC-32C"),
    (r"crc[-_ ]?32[-_ /]?bzip2", "CRC-32/BZIP2"),
    (r"xmodem", "CRC-16/XMODEM"),
    (r"kermit", "CRC-16/KERMIT"),
    (r"crc[-_ ]?16[-_ /]?ccitt|crc[-_ ]?ccitt", "CRC-16/CCITT-FALSE"),
    (r"crc[-_ ]?16", "CRC-16/ARC"),
    (r"crc[-_ ]?32|\bcrc\b", "CRC-32"),
    (r"fnv[-_ ]?1a[-_ ]?32", "FNV-1a-32"),
    (r"fnv[-_ ]?1a", "FNV-1a-64"),
    (r"fnv[-_ ]?1\b|\bfnv\b", "FNV-1-64"),
    (r"adler", "Adler-32"),
    (r"fletcher", "Fletcher-32"),
    (r"djb2a|djb2[-_ ]?xor", "djb2-xor"),
    (r"djb2|djb hash|bernstein", "djb2"),
    (r"\bsdbm\b", "sdbm"),
    (r"\bxtea\b", "XTEA"),
    (r"\btea\b|tiny encryption", "TEA"),
    (r"\brc4\b|arc4|arcfour", "RC4"),
    (r"base[-_ ]?64[-_ ]?url|url[-_ ]?safe base[-_ ]?64", "Base64url"),
    (r"base[-_ ]?64", "Base64"),
    (r"\bmd5\b", "MD5"),
    (r"sha[-_ ]?1\b", "SHA-1"),
    (r"sha[-_ ]?256", "SHA-256"),
    (r"murmur", "MurmurHash"),
    (r"xxhash", "xxHash32"),
]

VARIANT = re.compile(r"\b(variant|modified|custom|similar|resembl\w*|based on|derived|non-?standard|inspired|like)\b"
                     r"|-like\b", re.I)


def find_algorithm(text: str) -> str | None:
    t = text.lower()
    for pat, name in NAME_PATTERNS:
        if re.search(pat, t):
            return name
    return None


def is_variant_claim(text: str) -> bool:
    """"a variant of CRC-32", "CRC-like"... — không khẳng định là thuật toán chuẩn."""
    return bool(VARIANT.search(text))
