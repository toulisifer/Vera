#include "vera.h"

VERA_FN(fn_16)
{
    uint32_t h = (uint32_t)arg ^ (uint32_t)(arg >> 32);
    (void)out; (void)out_cap;
    for (size_t i = 0; i < len; i++) {
        OBF_JUNK(h, i + len);
        h = (h << 7) | (h >> 25);
        OBF_GUARD(h, i, h += (uint32_t)in[i] * 0x9Du + (uint32_t)i);
    }
    OBF_SPIN(h);
    h ^= h >> 15;
    h *= 0x3B9Du;
    h ^= h >> 13;
    return h;
}
