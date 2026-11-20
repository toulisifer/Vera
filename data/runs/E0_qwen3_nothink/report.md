# E0_qwen3_nothink — kiểm tra năng lực model

| Cấu hình | Hàm | Schema | Số lần gọi | Compile | FEPR | algorithm (đúng?) | claim giữ / loại |
|---|---|---|---|---|---|---|---|
| obf | fn_01 | ✅ | 1 | ✅ | 0.00 | unknown ❌ | 10 / 0 |
| obf | fn_05 | ✅ | 1 | ❌ 41:51: error: ‘DAT_00104010’ undeclared (first use in this f | 0.00 | unknown ❌ | 6 / 2 |
| obf | fn_08 | ✅ | 1 | ✅ | 0.00 | unknown ✅ | 11 / 0 |
| obf | fn_14 | ✅ | 2 | ✅ | 0.00 | unknown ✅ | 20 / 0 |
| obf | fn_18 | ❌ | 2 | ❌ schema không hợp lệ | — | — ✅ | 0 / 0 |
| opt | fn_01 | ✅ | 1 | ✅ | 0.02 | unknown ❌ | 6 / 0 |
| opt | fn_05 | ✅ | 1 | ❌ 38:45: error: expected ‘)’ before ‘;’ token | 0.00 | unknown ❌ | 8 / 2 |
| opt | fn_08 | ✅ | 1 | ✅ | 1.00 | unknown ✅ | 7 / 0 |
| opt | fn_14 | ✅ | 1 | ✅ | 0.12 | unknown ✅ | 11 / 4 |
| opt | fn_18 | ✅ | 1 | ❌ 30:12: error: redefinition of ‘local_10’ | 0.00 | unknown ✅ | 17 / 0 |
| plain | fn_01 | ✅ | 1 | ✅ | 1.00 | unknown ❌ | 8 / 0 |
| plain | fn_05 | ✅ | 1 | ✅ | 1.00 | unknown ❌ | 7 / 1 |
| plain | fn_08 | ✅ | 1 | ✅ | 1.00 | unknown ✅ | 7 / 0 |
| plain | fn_14 | ✅ | 1 | ❌ 33:80: error: expected ‘;’ before ‘)’ token | 0.00 | unknown ✅ | 8 / 0 |
| plain | fn_18 | ✅ | 2 | ❌ 31:16: error: missing terminating ' character | 0.00 | unknown ✅ | 16 / 1 |

| Cấu hình | Đúng schema | Compile | FEPR = 1 | Thuật toán đúng | Phải thử lại | Claim giữ / loại |
|---|---|---|---|---|---|---|
| obf | 4/5 | 3/5 | 0/5 | 3/5 | 2/5 | 47 / 2 |
| opt | 5/5 | 3/5 | 1/5 | 3/5 | 0/5 | 49 / 6 |
| plain | 5/5 | 3/5 | 3/5 | 3/5 | 1/5 | 46 / 2 |

Cổng E0: đúng schema 14/15 (đạt ≥ 80%); compile ở plain 3/5 (đạt ≥ 50%).
