"""Test các phần phục vụ demo: diễn giải tiếng Việt, chú thích code, tạo hàm near-miss lúc demo."""
import pytest

from vera import live
from vera.report import explain as X

# Lượt chạy thật lúc demo 02/10 (0xEDB88320 → 0x3CFE2F6D): code AI dùng uint64_t, chỉ đúng 1/50
V1_WIDTH_BUG = {"compiled": True, "n": 50, "match": 1, "fails": [
    {"v": "v01", "exp": "0x00000000e84154a5", "got": "0xff000000174154a5"},
    {"v": "v02", "exp": "0x00000000e12f4c01", "got": "0xffffff001ed0b301"}]}
RC_WIDTH_BUG = """uint64_t fn_99(const uint8_t *in, size_t len, uint64_t arg, uint8_t *out, size_t out_cap) {
  if (len != 0) {
    uint64_t result = 0xFFFFFFFFFFFFFFFF;
    return ~result;
  }
  return 0;
}"""


def test_explain_v1_detects_32_vs_64_bit():
    msg = X.explain_v1(V1_WIDTH_BUG)
    assert "1/50" in msg and "nhầm số 32-bit với 64-bit" in msg


def test_explain_v1_all_match_and_compile_error():
    assert "50/50" in X.explain_v1({"compiled": True, "n": 50, "match": 50})
    assert "DAT_" in X.explain_v1({"compiled": False, "err": "error: 'DAT_00104010' undeclared"})


def test_annotate_recovered_marks_64_bit_register():
    notes = X.annotate_recovered(RC_WIDTH_BUG, writes_out_truth=False, v1=V1_WIDTH_BUG)
    assert notes == [{"line": 2, "kind": "contradicted", "note": "nghi: lẽ ra là 32-bit"}]


def test_annotate_recovered_marks_fake_out_write_and_dat():
    rc = "x = DAT_00104010;\nout[i] = 1;\n"
    kinds = [n["note"] for n in X.annotate_recovered(rc, writes_out_truth=False, v1={"compiled": True})]
    assert kinds == ["biến Ghidra đặt tên, không tồn tại", "hàm thật không ghi out"]


@pytest.mark.parametrize("raw,want", [("c0ffee01", "0xC0FFEE01"), ("0x3cfe2f6d", "0x3CFE2F6D"), (None, None)])
def test_normalize_hex(raw, want):
    assert live.normalize_hex(raw) == want


def test_normalize_hex_rejects_non_hex():
    with pytest.raises(SystemExit):
        live.normalize_hex("12G4")


def test_mutate_replaces_characteristic_constant():
    assert live.constants_of("fn_01")[0] == "0xEDB88320"
    src, note = live.mutate("fn_01", None, "3CFE2F6D")
    assert "0x3CFE2F6D" in src and "EDB88320" not in src.upper() and "CRC-32" in note
