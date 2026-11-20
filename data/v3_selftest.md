# Self-test V3

## 1. False alarm (20 hằng đã biết × 2 mức tối ưu)

| Ngữ cảnh | Hằng | -O0 | -O2 |
|---|---|---|---|
| mul32 | `0x5BD1E995` | ✅ imm | ✅ imm |
| xor32 | `0xDEADBEEF` | ✅ imm | ✅ imm |
| add32_hi | `0x9E3779B1` | ✅ neg | ✅ imm |
| add32 | `0x2545F491` | ✅ imm | ✅ imm |
| mask31 | `0x7FFFFFFF` | ✅ imm | ✅ imm |
| mask_alt | `0x00FF00FF` | ✅ imm | ✅ imm |
| mask_hi | `0xFFFF0000` | ✅ imm | ✅ imm |
| cmp32 | `0x12345678` | ✅ imm | ✅ imm |
| cmp16 | `0xABCD` | ✅ imm | ✅ imm |
| mul64 | `0xC6A4A7935BD1E995` | ✅ imm | ✅ imm |
| xor64 | `0x87C37B91114253D5` | ✅ imm | ✅ imm |
| mod_prime | `65537` | ❌ | ❌ |
| mod_small | `10007` | ✅ imm | ✅ imm |
| div | `1000003` | ✅ magic | ✅ magic |
| table | `0x1F2E3D4C` | ✅ table | ✅ table |
| table64 | `0xA5A5A5A55A5A5A5A` | ✅ table | ✅ table |
| neg_dec | `-12345` | ✅ neg | ✅ imm |
| store | `0x0BADF00D` | ✅ bytes | ✅ imm |
| mul_pow2 | `4096` | ✅ shift | ✅ shift |
| string | `VeRA-selftest-key` | ✅ string | ✅ string |

Tỉ lệ bỏ sót: -O0 5%, -O2 5% (ngưỡng ≤ 5%).

## 2. False support (claim ALG sai trên 60 item)

0/1290 claim sai được V3 đánh supported (mục tiêu 0).


**Cổng V3: ĐẠT**
