# Phụ lục — kiểm tra chất lượng corpus

Sinh bởi `python -m vera.corpus.check`. Compiler: `gcc (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0`.

## A. Đối chiếu oracle tham chiếu (50 vector mỗi hàm)

Hàm kinh điển phải khớp đúng oracle của nó; near-miss và tự thiết kế không được khớp trọn oracle nào.

| Hàm | Nhóm | Oracle liên quan | Oracle khớp nhiều nhất | Đạt |
|---|---|---|---|---|
| fn_01 | classic | oracle CRC-32: 50/50 | CRC-32 (50/50) | ✅ |
| fn_02 | classic | oracle FNV-1a-64: 50/50 | FNV-1a-64 (50/50) | ✅ |
| fn_03 | classic | oracle Adler-32: 50/50 | Adler-32 (50/50) | ✅ |
| fn_04 | classic | oracle djb2: 50/50 | djb2 (50/50) | ✅ |
| fn_05 | classic | oracle TEA: 50/50 | TEA (50/50) | ✅ |
| fn_06 | classic | oracle RC4: 50/50 | RC4 (50/50) | ✅ |
| fn_07 | classic | oracle Base64: 50/50 | Base64 (50/50) | ✅ |
| fn_08 | near_miss | oracle cặp CRC-32: 1/50 | CRC-32 (1/50) | ✅ |
| fn_09 | near_miss | oracle cặp FNV-1a-64: 1/50 | FNV-1a-64 (1/50) | ✅ |
| fn_10 | near_miss | oracle cặp Adler-32: 19/50 | Adler-32 (19/50) | ✅ |
| fn_11 | near_miss | oracle cặp djb2: 0/50 | CRC-32 (0/50) | ✅ |
| fn_12 | near_miss | oracle cặp TEA: 17/50 | TEA (17/50) | ✅ |
| fn_13 | near_miss | oracle cặp RC4: 4/50 | RC4 (4/50) | ✅ |
| fn_14 | near_miss | oracle cặp Base64: 5/50 | Base64 (5/50) | ✅ |
| fn_15 | custom | — | RC4 (2/50) | ✅ |
| fn_16 | custom | — | CRC-32 (0/50) | ✅ |
| fn_17 | custom | — | TEA (10/50) | ✅ |
| fn_18 | custom | — | Fletcher-32 (3/50) | ✅ |
| fn_19 | custom | — | RC4 (4/50) | ✅ |
| fn_20 | custom | — | RC4 (4/50) | ✅ |

## B. Obfuscation còn tồn tại sau -O2

Số lệnh / lệnh nhảy có điều kiện / basic block của fn_XX (capstone). Tiêu chí: jcc(obf) ≥ 1.30 × jcc(opt).

| Hàm | plain: lệnh | opt: lệnh / jcc / block | obf: lệnh / jcc / block | jcc obf/opt | Đạt |
|---|---|---|---|---|---|
| fn_01 | 40 | 25 / 3 / 7 | 82 / 11 / 18 | 3.67 | ✅ |
| fn_02 | 29 | 13 / 2 / 4 | 64 / 8 / 15 | 4.00 | ✅ |
| fn_03 | 53 | 33 / 2 / 6 | 86 / 8 / 19 | 4.00 | ✅ |
| fn_04 | 30 | 18 / 2 / 6 | 63 / 8 / 17 | 4.00 | ✅ |
| fn_05 | 239 | 75 / 3 / 7 | 114 / 8 / 13 | 2.67 | ✅ |
| fn_06 | 126 | 113 / 7 / 14 | 151 / 11 / 21 | 1.57 | ✅ |
| fn_07 | 220 | 113 / 5 / 16 | 155 / 9 / 24 | 1.80 | ✅ |
| fn_08 | 40 | 25 / 3 / 7 | 82 / 11 / 18 | 3.67 | ✅ |
| fn_09 | 29 | 13 / 2 / 4 | 64 / 8 / 15 | 4.00 | ✅ |
| fn_10 | 53 | 33 / 2 / 6 | 86 / 8 / 19 | 4.00 | ✅ |
| fn_11 | 31 | 17 / 2 / 6 | 63 / 8 / 18 | 4.00 | ✅ |
| fn_12 | 239 | 75 / 3 / 7 | 114 / 8 / 13 | 2.67 | ✅ |
| fn_13 | 127 | 113 / 7 / 13 | 152 / 11 / 21 | 1.57 | ✅ |
| fn_14 | 220 | 113 / 5 / 16 | 155 / 9 / 24 | 1.80 | ✅ |
| fn_15 | 94 | 87 / 13 / 28 | 117 / 18 / 30 | 1.38 | ✅ |
| fn_16 | 42 | 25 / 2 / 4 | 73 / 9 / 14 | 4.50 | ✅ |
| fn_17 | 91 | 44 / 8 / 15 | 84 / 12 / 24 | 1.50 | ✅ |
| fn_18 | 96 | 90 / 24 / 44 | 187 / 34 / 66 | 1.42 | ✅ |
| fn_19 | 62 | 30 / 3 / 7 | 61 / 8 / 14 | 2.67 | ✅ |
| fn_20 | 113 | 68 / 8 / 17 | 101 / 13 / 22 | 1.62 | ✅ |

## C. Rò rỉ tên thuật toán trong binary

Không có.
