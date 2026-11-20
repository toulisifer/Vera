#include "vera.h"

/*
 * Bản ghi: [type:1][n:1][value:n]. type = 0x00 là kết thúc (phần sau bị bỏ qua).
 * Thành công: trả (số bản ghi << 32) | tổng số byte value; out nhận type của từng bản ghi.
 * Bản ghi bị cắt cụt, hoặc out_cap nhỏ hơn số bản ghi: trả VERA_ERR, không ghi out.
 */
VERA_FN(fn_17)
{
    size_t i = 0, cnt = 0, total = 0;
    (void)arg;
    while (i < len && in[i] != 0x00) {
        if (i + 2 > len || i + 2 + in[i + 1] > len)
            return VERA_ERR;
        OBF_JUNK(total, i + cnt);
        total += in[i + 1];
        cnt++;
        i += 2 + (size_t)in[i + 1];
    }
    if (out_cap < cnt)
        return VERA_ERR;
    i = 0;
    for (size_t c = 0; c < cnt; c++) {
        OBF_GUARD(i, c + len, out[c] = in[i]);
        i += 2 + (size_t)in[i + 1];
    }
    return ((uint64_t)cnt << 32) | (uint64_t)total;
}
