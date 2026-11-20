#include "vera.h"

/*
 * Máy trạng thái kiểm tra ngoặc () [] {} với chuỗi "..." và ký tự thoát \ trong chuỗi.
 * Trả 0 nếu hợp lệ; vị trí (tính từ 1) của byte lỗi đầu tiên; len + 1 nếu hết input
 * khi còn ngoặc mở hoặc chuỗi chưa đóng. Độ sâu tối đa 64.
 */
VERA_FN(fn_18)
{
    uint8_t st[64];
    size_t d = 0;
    unsigned q = 0; /* 0 = ngoài chuỗi, 1 = trong chuỗi, 2 = sau dấu thoát */
    uint8_t c;
    (void)arg; (void)out; (void)out_cap;
    for (size_t i = 0; i < len; i++) {
        c = in[i];
        OBF_JUNK(q, i + len);
        if (q == 2) {
            q = 1;
        } else if (q == 1) {
            if (c == '\\')
                q = 2;
            else if (c == '"')
                OBF_GUARD(q, i, q = 0);
        } else if (c == '"') {
            OBF_GUARD(q, i + d, q = 1);
        } else if (c == '(' || c == '[' || c == '{') {
            if (d == 64)
                return i + 1;
            OBF_GUARD(d, i, st[d++] = (uint8_t)(c == '(' ? ')' : c + 2));
        } else if (c == ')' || c == ']' || c == '}') {
            if (d == 0 || st[d - 1] != c)
                return i + 1;
            OBF_GUARD(d, i + len, d--);
            OBF_SPIN(d);
        }
    }
    return (d != 0 || q != 0) ? (uint64_t)len + 1 : 0;
}
