"""Test V3 trên evidence thật của corpus (data/artifacts)."""
import json

import pytest

from vera.common import ARTIFACTS, load_vectors
from vera.verify import behaviour
from vera.verify.fingerprints import find_algorithm, is_variant_claim
from vera.verify.v3 import Evidence, check_alg, check_const, qualifying_values


def ev(fn, cfg):
    return Evidence(json.loads((ARTIFACTS / cfg / f"{fn}.evidence.json").read_text()))


def const(text, *vals):
    return {"type": "CONST", "text": text, "asserted_values": list(vals)}


def test_number_extraction_rules():
    nums, _ = qualifying_values(const("Computes CRC-32 over 64 bytes using 32-bit words and 0xEDB88320", "0xEDB88320"))
    assert nums == [0xEDB88320]
    nums, _ = qualifying_values(const("Uses 0x80 and 255 and 65521"))
    assert nums == [65521]  # 0x80 (2 chữ số hex) và 255 (3 chữ số thập phân) bị bỏ
    nums, strs = qualifying_values(const("basis", "cbf29ce484222325"))
    assert nums == [0xCBF29CE484222325] and not strs
    nums, _ = qualifying_values(const("Adds -0x61C88647 each round"))
    assert nums == [-0x61C88647]


@pytest.mark.parametrize("cfg", ["plain", "opt", "obf"])
def test_characteristic_constants_supported(cfg):
    assert check_const(const("poly", "0xEDB88320"), ev("fn_01", cfg))["label"] == "supported"
    assert check_const(const("delta", "0x9E3779B9"), ev("fn_05", cfg))["label"] == "supported"
    assert check_const(const("basis", "0xCBF29CE484222325"), ev("fn_02", cfg))["label"] == "supported"
    assert check_const(const("modulus 65521"), ev("fn_03", cfg))["label"] == "supported"


def test_negated_constant_form():
    r = check_const(const("delta", "0x9E3779B9"), ev("fn_05", "opt"))
    assert r["found"][0]["form"] in ("neg", "imm")


def test_string_in_rodata():
    alpha = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
    assert check_const(const("table", alpha), ev("fn_07", "obf"))["label"] == "supported"
    assert check_const(const("table", alpha), ev("fn_14", "obf"))["label"] == "unsupported"


def test_absent_constant_is_unsupported_not_contradicted():
    r = check_const(const("uses", "0x12345678"), ev("fn_01", "opt"))
    assert r["label"] == "unsupported"
    assert check_const(const("uses the constant 0x5678"), ev("fn_16", "opt"))["label"] == "unsupported"


def test_alg_fingerprint():
    assert check_alg("CRC-32", ev("fn_01", "obf"))["label"] == "supported"
    assert check_alg("CRC-32", ev("fn_08", "obf"))["label"] == "unsupported"  # near-miss: đa thức khác
    assert check_alg("TEA", ev("fn_01", "opt"))["label"] == "unsupported"
    assert check_alg("RC4", ev("fn_06", "opt"))["label"] == "unsupported"  # không có hằng đặc trưng


def test_find_algorithm_names():
    assert find_algorithm("Computes the CRC32 checksum") == "CRC-32"
    assert find_algorithm("This is CRC-32C (Castagnoli)") == "CRC-32C"
    assert find_algorithm("Implements the Tiny Encryption Algorithm") == "TEA"
    assert find_algorithm("An XTEA block cipher") == "XTEA"
    assert find_algorithm("Encodes to base64") == "Base64"
    assert find_algorithm("Iterates bytes and steals a tea bag") == "TEA"  # giới hạn đã biết: khớp theo từ
    assert find_algorithm("Implements CRC-16/XMODEM.") == "CRC-16/XMODEM"
    assert find_algorithm("CRC-16/CCITT checksum") == "CRC-16/CCITT-FALSE"
    assert find_algorithm("custom checksum") is None
    assert is_variant_claim("a variant of CRC-32") and not is_variant_claim("computes CRC-32")


def test_oracle_verifies_and_contradicts():
    assert behaviour.check_oracle("CRC-32", load_vectors("fn_01"))["label"] == "verified"
    r = behaviour.check_oracle("CRC-32", load_vectors("fn_08"))
    assert r["label"] == "contradicted" and r["counterexample"]["vector"]
    assert behaviour.check_oracle("MD5", load_vectors("fn_01")) is None


def io(text, when, returns=None, writes_out=None):
    d = {"when": when}
    if returns is not None:
        d["returns"] = returns
    if writes_out is not None:
        d["writes_out"] = writes_out
    return {"type": "IO", "text": text, "asserted_values": [], "io": d}


def test_io_claims():
    v = load_vectors("fn_01")
    assert behaviour.check_io(io("0 for empty", "len == 0", "0"), v)["label"] == "verified"
    assert behaviour.check_io(io("0xFFFFFFFF for empty", "len == 0", "0xFFFFFFFF"), v)["label"] == "contradicted"
    assert behaviour.check_io(io("ERR when out_cap < len", "out_cap < len", "ERR"), v)["label"] == "contradicted"
    v6 = load_vectors("fn_06")
    assert behaviour.check_io(io("ERR when out_cap < len", "out_cap < len", "ERR"), v6)["label"] == "verified"
    assert behaviour.check_io(io("returns len", "out_cap >= 0", "len"), v6)["label"] == "unsupported"  # sai DSL


def side(text):
    return {"type": "SIDE", "text": text, "asserted_values": []}


def test_side_claims():
    crc, rc4 = load_vectors("fn_01"), load_vectors("fn_06")
    assert behaviour.check_side(side("Writes the 4-byte checksum to the output buffer."), crc)["label"] == "contradicted"
    assert behaviour.check_side(side("The function does not write to out."), crc)["label"] == "verified"
    assert behaviour.check_side(side("Writes exactly len bytes to out."), rc4)["label"] == "verified"
    assert behaviour.check_side(side("Does not modify the input or output buffers."), rc4)["label"] == "contradicted"
    assert behaviour.check_side(side("Uses a local stack buffer of 256 bytes."), rc4)["label"] == "unsupported"


def test_stats():
    from vera.report.stats import auroc, mcnemar_exact, wilson
    lo, hi = wilson(5, 50)
    assert 0.04 < lo < 0.05 and 0.21 < hi < 0.22
    assert auroc([0.9, 0.8], [0.1, 0.2]) == 1.0 and auroc([0.5], [0.5]) == 0.5
    assert mcnemar_exact(0, 0) == 1.0 and mcnemar_exact(0, 8) < 0.01
