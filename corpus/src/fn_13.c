#include "vera.h"

VERA_FN(fn_13)
{
    uint8_t s[256], k[8], t;
    unsigned i, j = 0;
    if (out_cap < len)
        return VERA_ERR;
    for (i = 0; i < 8; i++)
        k[i] = (uint8_t)(arg >> (8 * i));
    for (i = 0; i < 256; i++)
        s[i] = (uint8_t)i;
    for (i = 0; i < 256; i++) {
        OBF_GUARD(j, i, j = (j + s[i] + (k[i & 7] ^ i)) & 0xFFu);
        t = s[i]; s[i] = s[j]; s[j] = t;
    }
    i = j = 0;
    for (size_t n = 0; n < len; n++) {
        i = (i + 1) & 0xFFu;
        j = (j + s[i]) & 0xFFu;
        OBF_JUNK(j, n + len);
        t = s[i]; s[i] = s[j]; s[j] = t;
        out[n] = in[n] ^ s[(s[i] + s[j]) & 0xFFu];
    }
    return len;
}
