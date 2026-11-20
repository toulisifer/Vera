"""Thư viện cài đặt tham chiếu cho V1b (oracle tham chiếu).

Mỗi thuật toán có hai tầng:
  * lõi chuẩn (`crc32(data)`, `rc4(key, data)`...) — kiểm bằng test vector công bố
    trong tests/test_oracles.py trước khi được dùng làm bằng chứng;
  * adapter theo chữ ký chung của VeRA: (in, arg, out_cap) -> (ret, out_buffer),
    với cùng quy ước như corpus (docs/conventions.md): out được tô 0xCC trước,
    thiếu out_cap thì trả VERA_ERR và không ghi.

Khi model nói "hàm này là X", V1b chạy ORACLES[X] trên 50 vector và so với output
của binary gốc.
"""
from __future__ import annotations

import base64 as _b64
import struct
from dataclasses import dataclass
from typing import Callable

VERA_ERR = 0xFFFFFFFFFFFFFFFF
M32 = 0xFFFFFFFF
M64 = 0xFFFFFFFFFFFFFFFF


# ---------------------------------------------------------------- lõi chuẩn
def _crc_reflected(data: bytes, poly: int, init: int, xorout: int, width: int) -> int:
    mask = (1 << width) - 1
    h = init
    for c in data:
        h ^= c
        for _ in range(8):
            h = (h >> 1) ^ (poly if h & 1 else 0)
    return (h ^ xorout) & mask


def _crc_normal(data: bytes, poly: int, init: int, xorout: int, width: int) -> int:
    mask = (1 << width) - 1
    top = 1 << (width - 1)
    h = init
    for c in data:
        h ^= c << (width - 8)
        for _ in range(8):
            h = ((h << 1) ^ poly) if h & top else (h << 1)
            h &= mask
    return (h ^ xorout) & mask


def crc32(d: bytes) -> int: return _crc_reflected(d, 0xEDB88320, M32, M32, 32)
def crc32c(d: bytes) -> int: return _crc_reflected(d, 0x82F63B78, M32, M32, 32)
def crc32_bzip2(d: bytes) -> int: return _crc_normal(d, 0x04C11DB7, M32, M32, 32)
def crc16_arc(d: bytes) -> int: return _crc_reflected(d, 0xA001, 0, 0, 16)
def crc16_ccitt_false(d: bytes) -> int: return _crc_normal(d, 0x1021, 0xFFFF, 0, 16)
def crc16_xmodem(d: bytes) -> int: return _crc_normal(d, 0x1021, 0, 0, 16)
def crc16_kermit(d: bytes) -> int: return _crc_reflected(d, 0x8408, 0, 0, 16)


def fnv1a_64(d: bytes) -> int:
    h = 0xCBF29CE484222325
    for c in d:
        h = ((h ^ c) * 0x100000001B3) & M64
    return h


def fnv1_64(d: bytes) -> int:
    h = 0xCBF29CE484222325
    for c in d:
        h = ((h * 0x100000001B3) & M64) ^ c
    return h


def fnv1a_32(d: bytes) -> int:
    h = 0x811C9DC5
    for c in d:
        h = ((h ^ c) * 0x01000193) & M32
    return h


def adler32(d: bytes) -> int:
    a, b = 1, 0
    for c in d:
        a = (a + c) % 65521
        b = (b + a) % 65521
    return (b << 16) | a


def fletcher32(d: bytes) -> int:
    """Theo Wikipedia: từ 16-bit little-endian, đệm 0 nếu độ dài lẻ, modulo 65535."""
    if len(d) % 2:
        d = d + b"\x00"
    s1 = s2 = 0
    for (w,) in struct.iter_unpack("<H", d):
        s1 = (s1 + w) % 65535
        s2 = (s2 + s1) % 65535
    return (s2 << 16) | s1


def djb2(d: bytes) -> int:
    h = 5381
    for c in d:
        h = (h * 33 + c) & M32
    return h


def djb2_xor(d: bytes) -> int:
    h = 5381
    for c in d:
        h = ((h * 33) ^ c) & M32
    return h


def sdbm(d: bytes) -> int:
    h = 0
    for c in d:
        h = (c + (h << 6) + (h << 16) - h) & M32
    return h


def tea_encrypt(v: tuple[int, int], k: tuple[int, int, int, int]) -> tuple[int, int]:
    v0, v1 = v
    s = 0
    for _ in range(32):
        s = (s + 0x9E3779B9) & M32
        v0 = (v0 + ((((v1 << 4) + k[0]) & M32) ^ ((v1 + s) & M32) ^ (((v1 >> 5) + k[1]) & M32))) & M32
        v1 = (v1 + ((((v0 << 4) + k[2]) & M32) ^ ((v0 + s) & M32) ^ (((v0 >> 5) + k[3]) & M32))) & M32
    return v0, v1


def xtea_encrypt(v: tuple[int, int], k: tuple[int, int, int, int], rounds: int = 32) -> tuple[int, int]:
    v0, v1 = v
    s = 0
    for _ in range(rounds):
        v0 = (v0 + (((((v1 << 4) & M32) ^ (v1 >> 5)) + v1) & M32 ^ (s + k[s & 3]) & M32)) & M32
        s = (s + 0x9E3779B9) & M32
        v1 = (v1 + (((((v0 << 4) & M32) ^ (v0 >> 5)) + v0) & M32 ^ (s + k[(s >> 11) & 3]) & M32)) & M32
    return v0, v1


def rc4(key: bytes, data: bytes) -> bytes:
    s = list(range(256))
    j = 0
    for i in range(256):
        j = (j + s[i] + key[i % len(key)]) & 0xFF
        s[i], s[j] = s[j], s[i]
    i = j = 0
    res = bytearray()
    for c in data:
        i = (i + 1) & 0xFF
        j = (j + s[i]) & 0xFF
        s[i], s[j] = s[j], s[i]
        res.append(c ^ s[(s[i] + s[j]) & 0xFF])
    return bytes(res)


# ------------------------------------------------- adapter theo chữ ký VeRA
@dataclass(frozen=True)
class Oracle:
    name: str
    aliases: tuple[str, ...]
    run: Callable[[bytes, int, int], tuple[int, bytes]]  # (in, arg, out_cap) -> (ret, out_buffer)


def _blank(out_cap: int) -> bytearray:
    return bytearray(b"\xcc" * out_cap)


def _hash(fn: Callable[[bytes], int]) -> Callable[[bytes, int, int], tuple[int, bytes]]:
    return lambda d, arg, cap: (fn(d), bytes(_blank(cap)))


def _block_cipher(enc) -> Callable[[bytes, int, int], tuple[int, bytes]]:
    def run(d: bytes, arg: int, cap: int) -> tuple[int, bytes]:
        out = _blank(cap)
        if len(d) < 24 or cap < 8:
            return VERA_ERR, bytes(out)
        v = struct.unpack_from("<2I", d, 0)
        k = struct.unpack_from("<4I", d, 8)
        out[0:8] = struct.pack("<2I", *enc(v, k))
        return 8, bytes(out)
    return run


def _rc4_run(d: bytes, arg: int, cap: int) -> tuple[int, bytes]:
    out = _blank(cap)
    if cap < len(d):
        return VERA_ERR, bytes(out)
    out[0:len(d)] = rc4(arg.to_bytes(8, "little"), d)
    return len(d), bytes(out)


def _b64_run(urlsafe: bool) -> Callable[[bytes, int, int], tuple[int, bytes]]:
    def run(d: bytes, arg: int, cap: int) -> tuple[int, bytes]:
        out = _blank(cap)
        enc = _b64.urlsafe_b64encode(d) if urlsafe else _b64.b64encode(d)
        if cap < len(enc):
            return VERA_ERR, bytes(out)
        out[0:len(enc)] = enc
        return len(enc), bytes(out)
    return run


_ALL = [
    Oracle("CRC-32", ("crc32", "crc-32/iso-hdlc", "crc32 ieee", "crc-32 ieee"), _hash(crc32)),
    Oracle("CRC-32C", ("crc32c", "castagnoli", "crc-32/iscsi"), _hash(crc32c)),
    Oracle("CRC-32/BZIP2", ("crc32 bzip2", "crc-32/bzip2"), _hash(crc32_bzip2)),
    Oracle("CRC-16/ARC", ("crc16", "crc-16", "crc16 arc"), _hash(crc16_arc)),
    Oracle("CRC-16/CCITT-FALSE", ("crc16 ccitt", "crc-ccitt", "crc-16/ccitt"), _hash(crc16_ccitt_false)),
    Oracle("CRC-16/XMODEM", ("crc16 xmodem", "crc-16/xmodem", "xmodem"), _hash(crc16_xmodem)),
    Oracle("CRC-16/KERMIT", ("crc16 kermit", "crc-16/kermit", "kermit"), _hash(crc16_kermit)),
    Oracle("FNV-1a-64", ("fnv-1a", "fnv1a", "fnv-1a 64", "fnv1a64"), _hash(fnv1a_64)),
    Oracle("FNV-1-64", ("fnv-1", "fnv1", "fnv-1 64"), _hash(fnv1_64)),
    Oracle("FNV-1a-32", ("fnv-1a 32", "fnv1a32"), _hash(fnv1a_32)),
    Oracle("Adler-32", ("adler32", "adler"), _hash(adler32)),
    Oracle("Fletcher-32", ("fletcher32", "fletcher"), _hash(fletcher32)),
    Oracle("djb2", ("djb2", "djb hash", "bernstein hash"), _hash(djb2)),
    Oracle("djb2-xor", ("djb2a", "djb2 xor"), _hash(djb2_xor)),
    Oracle("sdbm", ("sdbm", "sdbm hash"), _hash(sdbm)),
    Oracle("TEA", ("tea", "tiny encryption algorithm"), _block_cipher(tea_encrypt)),
    Oracle("XTEA", ("xtea",), _block_cipher(xtea_encrypt)),
    Oracle("RC4", ("rc4", "arc4", "arcfour"), _rc4_run),
    Oracle("Base64", ("base64", "base-64"), _b64_run(False)),
    Oracle("Base64url", ("base64url", "url-safe base64"), _b64_run(True)),
]

ORACLES: dict[str, Oracle] = {o.name: o for o in _ALL}


def _norm(s: str) -> str:
    return " ".join(s.lower().replace("_", " ").replace("-", " ").split())


def lookup(algorithm: str) -> Oracle | None:
    """Tìm oracle theo tên model nêu ("CRC32", "crc-32", "Adler32"...). Không có → None."""
    key = _norm(algorithm)
    for o in _ALL:
        if key == _norm(o.name) or key in {_norm(a) for a in o.aliases}:
            return o
    return None
