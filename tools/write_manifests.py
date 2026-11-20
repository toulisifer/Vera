"""Sinh corpus/manifest/fn_XX.json từ bảng ground truth bên dưới.

Bảng này là nơi DUY NHẤT sửa ground truth. Sau khi sửa, chạy lại:
    python tools/write_manifests.py
Manifest phải được chốt và gắn tag git (vd. `ground-truth-v1`) TRƯỚC lượt chạy chính E1;
mọi thay đổi sau đó ghi vào docs/changelog-ground-truth.md.
"""
from __future__ import annotations

import json

from vera.common import MANIFEST, SRC
from vera.constants import encodings


def c(value: int, width: int, role: str, note: str = "") -> dict:
    d = {"value": f"0x{value:X}", "width": width, "role": role, "encodings": encodings(value, width)}
    if note:
        d["compiler_note"] = note
    return d


MOD_NOTE = "-O2 thay phép chia/modulo cho hằng bằng phép nhân với số nghịch đảo (magic number); giá trị gốc có thể không xuất hiện dưới dạng immediate."

HASH_IO = {"returns": "giá trị băm/checksum (zero-extend lên 64 bit)", "writes_out": False, "uses_arg": False}

FUNCS = {
    # ------------------------------------------------------------ kinh điển
    "fn_01": dict(group="classic", algorithm="CRC-32", oracle="CRC-32", profile="bytes",
                  description="Tính CRC-32 chuẩn (IEEE 802.3, dạng reflected) trên len byte của in. "
                              "Thanh ghi khởi tạo 0xFFFFFFFF, mỗi byte được XOR vào byte thấp rồi dịch phải 8 lần, "
                              "mỗi lần XOR với đa thức đảo bit 0xEDB88320 nếu bit thấp bằng 1. "
                              "Kết quả được XOR với 0xFFFFFFFF và trả về. Không dùng arg, không ghi out.",
                  io=HASH_IO, consts=[c(0xEDB88320, 32, "đa thức reflected"), c(0xFFFFFFFF, 32, "init và xorout")]),
    "fn_02": dict(group="classic", algorithm="FNV-1a (64-bit)", oracle="FNV-1a-64", profile="text",
                  description="Tính băm FNV-1a 64-bit trên in. Bắt đầu từ offset basis 0xCBF29CE484222325; "
                              "với mỗi byte, XOR byte vào h rồi nhân với FNV prime 0x100000001B3 (mod 2^64). "
                              "Trả về h. Không dùng arg, không ghi out.",
                  io=HASH_IO, consts=[c(0xCBF29CE484222325, 64, "offset basis"), c(0x100000001B3, 64, "FNV prime")]),
    "fn_03": dict(group="classic", algorithm="Adler-32", oracle="Adler-32", profile="text",
                  description="Tính checksum Adler-32 trên in. Hai tổng a (khởi tạo 1) và b (khởi tạo 0) "
                              "được cập nhật theo từng byte: a = (a + byte) mod 65521, b = (b + a) mod 65521. "
                              "Trả về (b << 16) | a. Không dùng arg, không ghi out.",
                  io=HASH_IO, consts=[c(65521, 32, "modulus (số nguyên tố lớn nhất < 2^16)", MOD_NOTE)]),
    "fn_04": dict(group="classic", algorithm="djb2", oracle="djb2", profile="text",
                  description="Tính băm chuỗi djb2 (Bernstein) 32-bit trên in. Khởi tạo h = 5381; "
                              "với mỗi byte h = h * 33 + byte (mod 2^32), phép nhân 33 viết dạng (h << 5) + h. "
                              "Trả về h. Không dùng arg, không ghi out.",
                  io=HASH_IO, consts=[c(5381, 32, "giá trị khởi tạo")]),
    "fn_05": dict(group="classic", algorithm="TEA", oracle="TEA", profile="bytes",
                  description="Mã hóa một khối 64-bit bằng TEA với 32 vòng. Khối lấy từ in[0..8], khóa 128-bit từ "
                              "in[8..24] (các từ 32-bit little-endian). Mỗi vòng cộng delta 0x9E3779B9 vào sum và "
                              "cập nhật v0, v1 bằng dịch trái 4, dịch phải 5, cộng khóa và XOR. Ghi 8 byte bản mã vào out "
                              "và trả 8; trả VERA_ERR nếu len < 24 hoặc out_cap < 8. Không dùng arg.",
                  io={"returns": "8, hoặc VERA_ERR khi len < 24 hay out_cap < 8", "writes_out": True, "uses_arg": False},
                  consts=[c(0x9E3779B9, 32, "delta (tỉ lệ vàng)"), c(0xC6EF3720, 32, "sum sau 32 vòng (có thể xuất hiện khi compiler tính trước)")]),
    "fn_06": dict(group="classic", algorithm="RC4", oracle="RC4", profile="bytes",
                  description="Mã hóa luồng RC4. Khóa 8 byte là arg ở dạng little-endian. KSA khởi tạo S = 0..255 và "
                              "hoán vị với j = j + S[i] + key[i mod 8]; PRGA sinh keystream và XOR với in, ghi len byte "
                              "vào out. Trả len; trả VERA_ERR và không ghi gì nếu out_cap < len.",
                  io={"returns": "len, hoặc VERA_ERR khi out_cap < len", "writes_out": True, "uses_arg": True},
                  consts=[c(256, 32, "kích thước S-box"), c(255, 32, "mask 0xFF")]),
    "fn_07": dict(group="classic", algorithm="Base64 encode", oracle="Base64", profile="bytes",
                  description="Mã hóa Base64 chuẩn (RFC 4648) với bảng chữ cái A-Z a-z 0-9 + / và đệm '='. "
                              "Mỗi nhóm 3 byte thành 4 ký tự; nhóm cuối 1 hoặc 2 byte được đệm. Ghi 4*ceil(len/3) byte "
                              "vào out (không có NUL) và trả số byte đó; trả VERA_ERR nếu out_cap không đủ. Không dùng arg.",
                  io={"returns": "4*ceil(len/3), hoặc VERA_ERR khi out_cap không đủ", "writes_out": True, "uses_arg": False},
                  consts=[], strings=["ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"]),
    # ------------------------------------------------------------- near-miss
    "fn_08": dict(group="near_miss", algorithm="near-miss của CRC-32", pair_of="fn_01", oracle=None, profile="bytes",
                  difference="Đa thức reflected 0xF7179BF5 thay cho 0xEDB88320; init/xorout giữ nguyên.",
                  description="Tính một CRC 32-bit kiểu reflected giống hệt CRC-32 về cấu trúc (init 0xFFFFFFFF, dịch "
                              "phải từng bit, xorout 0xFFFFFFFF) nhưng dùng đa thức 0xF7179BF5 không chuẩn. Vì vậy "
                              "kết quả khác CRC-32 và khác mọi CRC-32 có tên trong catalogue. Không dùng arg, không ghi out.",
                  io=HASH_IO, consts=[c(0xF7179BF5, 32, "đa thức tự chọn"), c(0xFFFFFFFF, 32, "init và xorout")]),
    "fn_09": dict(group="near_miss", algorithm="near-miss của FNV-1a (64-bit)", pair_of="fn_02", oracle=None, profile="text",
                  difference="Prime 0x100000001B5 thay cho 0x100000001B3; offset basis giữ nguyên.",
                  description="Băm kiểu FNV-1a 64-bit: offset basis chuẩn 0xCBF29CE484222325, mỗi byte XOR vào h rồi "
                              "nhân với 0x100000001B5 — khác FNV prime chuẩn 2 đơn vị. Trả h. Không dùng arg, không ghi out.",
                  io=HASH_IO, consts=[c(0xCBF29CE484222325, 64, "offset basis chuẩn"), c(0x100000001B5, 64, "hệ số nhân tự chọn")]),
    "fn_10": dict(group="near_miss", algorithm="near-miss của Adler-32", pair_of="fn_03", oracle=None, profile="text",
                  difference="Modulus 65519 thay cho 65521.",
                  description="Checksum kiểu Adler-32 với hai tổng a (khởi tạo 1) và b (khởi tạo 0), nhưng lấy modulo "
                              "65519 thay vì 65521. Trả (b << 16) | a. Không dùng arg, không ghi out.",
                  io=HASH_IO, consts=[c(65519, 32, "modulus tự chọn", MOD_NOTE)]),
    "fn_11": dict(group="near_miss", algorithm="near-miss của djb2", pair_of="fn_04", oracle=None, profile="text",
                  difference="Khởi tạo 7477 thay cho 5381 và hệ số nhân 41 thay cho 33.",
                  description="Băm chuỗi dạng nhân-cộng 32-bit giống djb2: h = h * 41 + byte (mod 2^32), khởi tạo "
                              "h = 7477. Trả h. Không dùng arg, không ghi out.",
                  io=HASH_IO, consts=[c(7477, 32, "giá trị khởi tạo tự chọn")]),
    "fn_12": dict(group="near_miss", algorithm="near-miss của TEA", pair_of="fn_05", oracle=None, profile="bytes",
                  difference="Delta 0x8EB7AE2F thay cho 0x9E3779B9; số vòng, cấu trúc vòng và bố trí khóa giữ nguyên.",
                  description="Mạng Feistel 32 vòng có cấu trúc giống hệt TEA (khối từ in[0..8], khóa từ in[8..24]) "
                              "nhưng hằng cộng vào sum mỗi vòng là 0x8EB7AE2F. Ghi 8 byte vào out, trả 8; VERA_ERR nếu "
                              "len < 24 hoặc out_cap < 8. Không dùng arg.",
                  io={"returns": "8, hoặc VERA_ERR khi len < 24 hay out_cap < 8", "writes_out": True, "uses_arg": False},
                  consts=[c(0x8EB7AE2F, 32, "delta tự chọn"), c((0x8EB7AE2F * 32) & 0xFFFFFFFF, 32, "sum sau 32 vòng")]),
    "fn_13": dict(group="near_miss", algorithm="near-miss của RC4", pair_of="fn_06", oracle=None, profile="bytes",
                  difference="KSA dùng j = j + S[i] + (key[i mod 8] XOR i) thay cho j = j + S[i] + key[i mod 8]; PRGA giữ nguyên.",
                  description="Mã hóa luồng giống RC4 (khóa 8 byte từ arg, S-box 256 byte, PRGA chuẩn) nhưng lịch khóa "
                              "XOR thêm chỉ số i vào byte khóa trước khi cộng. Keystream vì vậy khác RC4. Ghi len byte vào "
                              "out, trả len; VERA_ERR nếu out_cap < len.",
                  io={"returns": "len, hoặc VERA_ERR khi out_cap < len", "writes_out": True, "uses_arg": True},
                  consts=[c(256, 32, "kích thước S-box"), c(255, 32, "mask 0xFF")]),
    "fn_14": dict(group="near_miss", algorithm="near-miss của Base64 encode", pair_of="fn_07", oracle=None, profile="bytes",
                  difference="Bảng chữ cái 64 ký tự bị xáo trộn (seed 20260924); cơ chế đệm '=' giữ nguyên.",
                  description="Mã hóa kiểu Base64 (3 byte thành 4 ký tự, đệm '=') nhưng dùng một hoán vị tự chọn của "
                              "bảng chữ cái chuẩn. Kỹ thuật này hay gặp trong malware để che chuỗi. Ghi 4*ceil(len/3) byte "
                              "vào out, trả số byte đó; VERA_ERR nếu out_cap không đủ.",
                  io={"returns": "4*ceil(len/3), hoặc VERA_ERR khi out_cap không đủ", "writes_out": True, "uses_arg": False},
                  consts=[], strings=["AfhmdLEr3GMxg2S/a91UZnTlHOI5KYzevFCwNQ+P4tWV7cpXRbDuykjJsoi6q80B"]),
    # -------------------------------------------------------------- tự thiết kế
    "fn_15": dict(group="custom", algorithm="tự thiết kế: run-length encoding", oracle=None, profile="runs",
                  description="Nén run-length: mỗi dãy byte giống nhau liên tiếp (tối đa 255) được ghi thành cặp "
                              "(độ dài, giá trị) vào out. Lượt đầu tính kích thước cần; nếu out_cap không đủ thì trả "
                              "VERA_ERR và không ghi gì. Trả số byte đã ghi (luôn chẵn). Không dùng arg.",
                  io={"returns": "số byte ghi vào out, hoặc VERA_ERR", "writes_out": True, "uses_arg": False},
                  consts=[c(255, 32, "độ dài run tối đa")]),
    "fn_16": dict(group="custom", algorithm="tự thiết kế: checksum cuộn", oracle=None, profile="bytes",
                  description="Checksum cuộn 32-bit: h khởi tạo bằng XOR hai nửa của arg; với byte thứ i, xoay trái h "
                              "7 bit rồi cộng byte * 0x9D + i. Cuối cùng trộn h ^= h >> 15, h *= 0x3B9D, h ^= h >> 13. "
                              "Trả h (32-bit). Không ghi out.",
                  io={"returns": "checksum 32-bit", "writes_out": False, "uses_arg": True},
                  consts=[c(0x3B9D, 32, "hệ số trộn cuối")]),
    "fn_17": dict(group="custom", algorithm="tự thiết kế: parser TLV", oracle=None, profile="tlv",
                  description="Duyệt chuỗi bản ghi [type:1][n:1][value:n] cho tới hết input hoặc tới type 0x00. "
                              "Nếu một bản ghi bị cắt cụt, trả VERA_ERR. Nếu out_cap nhỏ hơn số bản ghi, trả VERA_ERR và "
                              "không ghi. Ngược lại ghi type của từng bản ghi vào out và trả (số bản ghi << 32) | tổng độ dài value. "
                              "Không dùng arg.",
                  io={"returns": "(count << 32) | total_value_bytes, hoặc VERA_ERR", "writes_out": True, "uses_arg": False},
                  consts=[]),
    "fn_18": dict(group="custom", algorithm="tự thiết kế: máy trạng thái kiểm tra ngoặc", oracle=None, profile="brackets",
                  description="Kiểm tra ngoặc (), [], {} cân bằng bằng ngăn xếp sâu tối đa 64, bỏ qua nội dung trong "
                              "chuỗi \"...\" (có ký tự thoát \\). Trả 0 nếu hợp lệ; vị trí tính từ 1 của byte lỗi đầu tiên "
                              "(ngoặc đóng sai, hoặc mở quá 64 tầng); len + 1 nếu hết input khi còn ngoặc mở hay chuỗi "
                              "chưa đóng. Không dùng arg, không ghi out.",
                  io={"returns": "0 | vị trí lỗi (1-based) | len + 1", "writes_out": False, "uses_arg": False},
                  consts=[]),
    "fn_19": dict(group="custom", algorithm="tự thiết kế: XOR xoay theo vị trí", oracle=None, profile="text",
                  description="Với byte thứ i: lấy byte khóa k = byte thứ (i mod 8) của arg (little-endian), xoay trái k "
                              "(i mod 8) bit, rồi out[i] = in[i] XOR k XOR (i mod 256). Trả len; VERA_ERR và không ghi "
                              "nếu out_cap < len. Đầu ra dài đúng bằng đầu vào và hàm không dùng hằng đặc trưng nào, "
                              "nên chỉ nhận diện được qua hành vi. Vì phép XOR tự đảo, gọi lại hàm với cùng arg trên "
                              "đầu ra sẽ khôi phục đầu vào.",
                  io={"returns": "len, hoặc VERA_ERR khi out_cap < len", "writes_out": True, "uses_arg": True},
                  consts=[]),
    "fn_20": dict(group="custom", algorithm="tự thiết kế: hoán vị byte theo khóa", oracle=None, profile="bytes",
                  description="Tạo hoán vị p của 8 vị trí từ arg (khai triển arg theo hệ cơ số giai thừa, hoán đổi từ "
                              "vị trí 7 về 1). Với mỗi khối 8 byte đầy đủ: out[b+n] = in[b+p[n]]; phần đuôi dưới 8 byte "
                              "được chép nguyên. Trả len; VERA_ERR và không ghi nếu out_cap < len.",
                  io={"returns": "len, hoặc VERA_ERR khi out_cap < len", "writes_out": True, "uses_arg": True},
                  consts=[]),
}


def main() -> None:
    MANIFEST.mkdir(parents=True, exist_ok=True)
    for fn_id, f in FUNCS.items():
        doc = {
            "id": fn_id,
            "group": f["group"],
            "algorithm_label": f["algorithm"],
            "pair_of": f.get("pair_of"),
            "difference_from_standard": f.get("difference"),
            "oracle": f["oracle"],
            "source": f"corpus/src/{fn_id}.c",
            "description": f["description"],
            "io_semantics": f["io"],
            "input_profile": f["profile"],
            "characteristic_constants": f["consts"],
            "characteristic_strings": f.get("strings", []),
        }
        assert (SRC / f"{fn_id}.c").exists(), fn_id
        (MANIFEST / f"{fn_id}.json").write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"[manifest] ghi {len(FUNCS)} manifest")


if __name__ == "__main__":
    main()
