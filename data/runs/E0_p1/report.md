# E0_p1 — kiểm tra năng lực model

| Cấu hình | Hàm | Schema | Số lần gọi | Compile | algorithm | claim giữ / loại |
|---|---|---|---|---|---|---|
| obf | fn_01 | ✅ | 2 | ❌ 28:7: error: ‘DAT_00104010’ undeclared (first use in this function) | unknown | 7 / 1 |
| obf | fn_05 | ❌ | 2 | ❌ schema không hợp lệ | unknown | 0 / 0 |
| obf | fn_08 | ✅ | 2 | ❌ 28:7: error: ‘DAT_00104010’ undeclared (first use in this function) | unknown | 6 / 1 |
| obf | fn_14 | ✅ | 2 | ❌ 26:30: error: expected expression before ‘!=’ token | unknown | 4 / 1 |
| obf | fn_18 | ✅ | 1 | ❌ 27:30: error: ‘DAT_00104018’ undeclared (first use in this function) | unknown | 9 / 1 |
| opt | fn_01 | ✅ | 1 | ✅ | CRC-32 | 5 / 0 |
| opt | fn_05 | ✅ | 2 | ✅ | unknown | 6 / 0 |
| opt | fn_08 | ✅ | 1 | ✅ | unknown | 5 / 0 |
| opt | fn_14 | ✅ | 1 | ❌ 26:88: error: subscripted value is neither array nor pointer nor vector | unknown | 3 / 1 |
| opt | fn_18 | ✅ | 1 | ✅ | unknown | 14 / 0 |
| plain | fn_01 | ✅ | 1 | ✅ | unknown | 7 / 0 |
| plain | fn_05 | ✅ | 2 | ✅ | unknown | 5 / 1 |
| plain | fn_08 | ✅ | 1 | ✅ | unknown | 7 / 0 |
| plain | fn_14 | ✅ | 1 | ✅ | unknown | 3 / 2 |
| plain | fn_18 | ✅ | 2 | ✅ | unknown | 4 / 1 |

| Cấu hình | Đúng schema | Compile | Phải thử lại | Claim giữ / loại |
|---|---|---|---|---|
| obf | 4/5 | 0/5 | 4/5 | 26 / 4 |
| opt | 5/5 | 4/5 | 1/5 | 33 / 1 |
| plain | 5/5 | 5/5 | 2/5 | 26 / 4 |

Cổng E0: đúng schema 14/15 (đạt ≥ 80%); compile ở plain 5/5 (đạt ≥ 50%).
