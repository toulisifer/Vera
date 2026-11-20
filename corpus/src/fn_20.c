#include "vera.h"

/*
 * Hoán vị byte trong từng khối 8 byte theo khóa arg (khai triển arg theo hệ cơ số
 * giai thừa để chọn hoán vị). Phần đuôi không đủ 8 byte được chép nguyên.
 */
VERA_FN(fn_20)
{
    uint8_t p[8], t;
    uint64_t sd = arg;
    size_t b, n;
    if (out_cap < len)
        return VERA_ERR;
    for (n = 0; n < 8; n++)
        p[n] = (uint8_t)n;
    for (n = 7; n > 0; n--) {
        size_t j = (size_t)(sd % (n + 1));
        sd /= (n + 1);
        OBF_JUNK(sd, n + len);
        t = p[n]; p[n] = p[j]; p[j] = t;
    }
    for (b = 0; b + 8 <= len; b += 8)
        for (n = 0; n < 8; n++)
            OBF_GUARD(t, b + n, out[b + n] = in[b + p[n]]);
    for (; b < len; b++)
        out[b] = in[b];
    return len;
}
