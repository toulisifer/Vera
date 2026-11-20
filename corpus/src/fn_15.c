#include "vera.h"

VERA_FN(fn_15)
{
    size_t need = 0, i = 0, o = 0, r;
    (void)arg;
    /* Lượt 1: đếm số byte cần ghi, để không ghi gì nếu out_cap thiếu. */
    while (i < len) {
        r = 1;
        while (i + r < len && in[i + r] == in[i] && r < 255)
            r++;
        OBF_JUNK(need, r + i);
        need += 2;
        i += r;
    }
    if (out_cap < need)
        return VERA_ERR;
    i = 0;
    while (i < len) {
        r = 1;
        while (i + r < len && in[i + r] == in[i] && r < 255)
            r++;
        out[o++] = (uint8_t)r;
        OBF_GUARD(o, i + r, out[o++] = in[i]);
        i += r;
    }
    return o;
}
