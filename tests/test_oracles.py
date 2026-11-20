"""Kiểm mỗi cài đặt tham chiếu bằng test vector công bố, trước khi dùng làm bằng chứng (V1b)."""
import struct

import pytest

from vera import oracles as o

CHECK = b"123456789"  # chuỗi kiểm tra chuẩn trong catalogue CRC


@pytest.mark.parametrize("fn,expected", [
    (o.crc32, 0xCBF43926),
    (o.crc32c, 0xE3069283),
    (o.crc32_bzip2, 0xFC891918),
    (o.crc16_arc, 0xBB3D),
    (o.crc16_ccitt_false, 0x29B1),
    (o.crc16_xmodem, 0x31C3),
    (o.crc16_kermit, 0x2189),
])
def test_crc_check_values(fn, expected):
    assert fn(CHECK) == expected


def test_fnv():
    assert o.fnv1a_64(b"") == 0xCBF29CE484222325
    assert o.fnv1a_64(b"a") == 0xAF63DC4C8601EC8C
    assert o.fnv1_64(b"a") == 0xAF63BD4C8601B7BE
    assert o.fnv1a_32(b"a") == 0xE40C292C


def test_adler_fletcher():
    assert o.adler32(b"Wikipedia") == 0x11E60398
    assert o.fletcher32(b"abcde") == 0xF04FC729
    assert o.fletcher32(b"abcdef") == 0x56502D2A
    assert o.fletcher32(b"abcdefgh") == 0xEBE19591


def test_string_hashes():
    assert o.djb2(b"") == 5381
    assert o.djb2(b"a") == 5381 * 33 + 97
    assert o.djb2_xor(b"a") == (5381 * 33) ^ 97
    assert o.sdbm(b"a") == 97


def test_tea_xtea():
    assert o.tea_encrypt((0, 0), (0, 0, 0, 0)) == (0x41EA3A0A, 0x94BAA940)
    assert o.xtea_encrypt((0x41424344, 0x45464748), (0x00010203, 0x04050607, 0x08090A0B, 0x0C0D0E0F)) \
        == (0x497DF3D0, 0x72612CB5)


@pytest.mark.parametrize("key,pt,ct", [
    (b"Key", b"Plaintext", "bbf316e8d940af0ad3"),
    (b"Wiki", b"pedia", "1021bf0420"),
    (b"Secret", b"Attack at dawn", "45a01f645fc35b383552544b9bf5"),
])
def test_rc4(key, pt, ct):
    assert o.rc4(key, pt).hex() == ct


@pytest.mark.parametrize("pt,ct", [
    (b"", b""), (b"f", b"Zg=="), (b"fo", b"Zm8="), (b"foo", b"Zm9v"),
    (b"foob", b"Zm9vYg=="), (b"fooba", b"Zm9vYmE="), (b"foobar", b"Zm9vYmFy"),
])
def test_base64_rfc4648(pt, ct):
    ret, out = o.ORACLES["Base64"].run(pt, 0, 64)
    assert ret == len(ct) and out[:ret] == ct


def test_adapters_follow_conventions():
    # thiếu out_cap -> VERA_ERR, không ghi gì
    ret, out = o.ORACLES["RC4"].run(b"abc", 1, 2)
    assert ret == o.VERA_ERR and out == b"\xcc\xcc"
    ret, out = o.ORACLES["TEA"].run(bytes(23), 0, 8)
    assert ret == o.VERA_ERR
    ret, out = o.ORACLES["TEA"].run(bytes(24), 0, 8)
    assert out == struct.pack("<2I", 0x41EA3A0A, 0x94BAA940)


def test_lookup_aliases():
    assert o.lookup("CRC32").name == "CRC-32"
    assert o.lookup("crc-32c").name == "CRC-32C"
    assert o.lookup("FNV1a").name == "FNV-1a-64"
    assert o.lookup("ARCFOUR").name == "RC4"
    assert o.lookup("something custom") is None
