# Quy ước corpus VeRA

## Chữ ký chung

```c
uint64_t fn_XX(const uint8_t *in, size_t len, uint64_t arg, uint8_t *out, size_t out_cap);
```

- Hàm trả một giá trị: checksum/hash (zero-extend lên 64 bit), số byte đã ghi, hoặc mã trạng thái.
- Hàm ghi `out` thì **không ghi byte nào** khi `out_cap` không đủ, và trả `VERA_ERR = 0xFFFFFFFFFFFFFFFF`.
- Không gọi hàm thư viện, không malloc, không I/O, không trạng thái toàn cục. Không hàm phụ: toàn bộ logic
  nằm trong `fn_XX` (macro thì được) để bản plain không lộ tên hàm phụ.
- Tên biến trung tính (`h`, `acc`, `s`, `i`, `j`, `k`...). Bản plain giữ debug info (tên biến, kiểu),
  nên tên biến không được lộ thuật toán.
- Byte ↔ từ 32-bit theo little-endian (`VERA_LD32`, `VERA_ST32`).
- Giới hạn (ghi vào Limitations): không có hàm gọi hệ thống, mạng, file hay cấu trúc dữ liệu động.

## Quy ước theo từng loại hàm (dùng chung với oracle tham chiếu)

| Loại | Quy ước |
|---|---|
| Hash/checksum | Trả giá trị; không dùng `out`. |
| Mã khối 64-bit (TEA...) | Khối = `in[0..8]`, khóa = `in[8..24]`; `len < 24` hoặc `out_cap < 8` → `VERA_ERR`; ghi 8 byte, trả 8. |
| Mã luồng (RC4...) | Khóa 8 byte = `arg` little-endian; `out_cap < len` → `VERA_ERR`; trả `len`. |
| Base64 | Có đệm `=`, không NUL; trả `4*ceil(len/3)`. |

## Ba cấu hình biên dịch

| Cấu hình | Cờ | Strip | Obfuscation |
|---|---|---|---|
| plain | `-O0 -g` | không | không |
| opt | `-O2` | `strip --strip-all` | không |
| obf | `-O2 -DVERA_OBF` | `strip --strip-all` | opaque predicate + junk code ở mức source |

Chung: `-std=c11 -fPIC -shared -Wall -Wextra`. Phiên bản GCC ghi trong `data/build_info.json`.
Strip vẫn giữ `.dynsym`, nên tên `fn_XX` (trung tính) còn lại để `dlopen` được.

Macro obfuscation ở `corpus/include/vera.h`: `OBF_GUARD` (bogus control flow), `OBF_JUNK` (nhánh chết),
`OBF_SPIN` (vòng lặp chạy 0 lần). Predicate dựa vào biến `volatile` và tính chất số học phụ thuộc
đầu vào để -O2 không xóa được. Tiêu chí kiểm trên binary: jcc(obf) ≥ 1,3 × jcc(opt)
(`python -m vera.corpus.check`, bảng ở `data/corpus_report.md`).

## Vector I/O

50 vector/hàm, seed cố định theo tên hàm. Bắt buộc có: len 0, 1, 3, 8, 23, 24, 64; toàn 0x00; toàn 0xFF;
`out_cap` = 0, thiếu một nửa, `out_cap = 7` với len 24; `arg = 0` và `arg = 2^64-1`; cộng vector biên
riêng theo `input_profile` (run 255/256, TLV cụt, lồng ngoặc 64/65 tầng...).
Output kỳ vọng lấy từ bản plain và phải khớp opt và obf trên cả 50 vector.
`out` được tô 0xCC trước khi gọi; file JSON lưu `out` đã cắt các byte `cc` ở cuối.

## Tra cứu hằng near-miss (ngày 2026-09-24)

| Hàm | Hằng | Kết quả tra |
|---|---|---|
| fn_08 | đa thức 0xF7179BF5 | không có trong catalogue CRC (reveng), không có kết quả web |
| fn_09 | 0x100000001B5 | không trùng hằng băm có tên |
| fn_10 | modulus 65519 | không phải biến thể Adler có tên |
| fn_11 | init 7477, nhân 41 | không trùng djb2/sdbm/Java hashCode (31, init 0) |
| fn_12 | delta 0x8EB7AE2F | không có kết quả web; khác 0x9E3779B9, 0x61C88647, hằng RC5 |
| fn_13 | KSA `key[i%8] ^ i` | không trùng RC4-drop/Spritz/VMPC |
| fn_14 | bảng chữ cái xáo trộn | khác Base64 chuẩn và base64url |

Ngoài ra `vera.corpus.check` xác nhận bằng thực thi: không hàm near-miss/tự thiết kế nào khớp trọn
bất kỳ oracle nào trong thư viện 18 thuật toán.
