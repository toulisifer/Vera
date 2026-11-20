#include "vera.h"

VERA_FN(fn_19)
{
    uint8_t k, r;
    if (out_cap < len)
        return VERA_ERR;
    for (size_t i = 0; i < len; i++) {
        k = (uint8_t)(arg >> (8 * (i & 7)));
        r = (uint8_t)(i & 7);
        OBF_JUNK(k, i + len);
        k = (uint8_t)((k << r) | (k >> ((8 - r) & 7)));
        OBF_GUARD(k, i, out[i] = in[i] ^ k ^ (uint8_t)i);
    }
    return len;
}
