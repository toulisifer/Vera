# E0 — kiểm tra năng lực model

| Cấu hình | Hàm | Schema | Số lần gọi | Compile | FEPR | algorithm (đúng?) | claim giữ / loại |
|---|---|---|---|---|---|---|---|
| obf | fn_01 | ✅ | 1 | ❌ 28:7: error: ‘DAT_00104010’ undeclared (first use in this fu | 0.00 | unknown ❌ | 12 / 0 |
| obf | fn_05 | ✅ | 1 | ❌ 37:49: error: ‘DAT_00104010’ undeclared (first use in this f | 0.00 | unknown ❌ | 8 / 1 |
| obf | fn_08 | ✅ | 1 | ❌ 28:7: error: ‘DAT_00104010’ undeclared (first use in this fu | 0.00 | unknown ✅ | 11 / 0 |
| obf | fn_14 | ✅ | 1 | ✅ | 0.08 | unknown ✅ | 5 / 2 |
| obf | fn_18 | ✅ | 2 | ✅ | 0.04 | unknown ✅ | 9 / 1 |
| opt | fn_01 | ✅ | 1 | ✅ | 0.00 | CRC-32 ✅ | 4 / 0 |
| opt | fn_05 | ✅ | 1 | ✅ | 0.32 | unknown ❌ | 6 / 0 |
| opt | fn_08 | ✅ | 1 | ✅ | 1.00 | unknown ✅ | 4 / 1 |
| opt | fn_14 | ✅ | 1 | ✅ | 0.10 | unknown ✅ | 6 / 0 |
| opt | fn_18 | ✅ | 1 | ✅ | 0.12 | unknown ✅ | 4 / 2 |
| plain | fn_01 | ✅ | 1 | ✅ | 1.00 | CRC-32 ✅ | 6 / 0 |
| plain | fn_05 | ✅ | 1 | ✅ | 0.32 | unknown ❌ | 4 / 1 |
| plain | fn_08 | ✅ | 1 | ✅ | 1.00 | unknown ✅ | 5 / 0 |
| plain | fn_14 | ✅ | 1 | ❌ 32:13: error: ‘i’ undeclared (first use in this function) | 0.00 | unknown ✅ | 4 / 1 |
| plain | fn_18 | ✅ | 2 | ❌ 30:20: error: missing terminating ' character | 0.00 | unknown ✅ | 4 / 1 |

| Cấu hình | Đúng schema | Compile | FEPR = 1 | Thuật toán đúng | Phải thử lại | Claim giữ / loại |
|---|---|---|---|---|---|---|
| obf | 5/5 | 2/5 | 0/5 | 3/5 | 1/5 | 45 / 4 |
| opt | 5/5 | 5/5 | 1/5 | 4/5 | 0/5 | 24 / 3 |
| plain | 5/5 | 3/5 | 2/5 | 4/5 | 1/5 | 23 / 3 |

Cổng E0: đúng schema 15/15 (đạt ≥ 80%); compile ở plain 3/5 (đạt ≥ 50%).
