#include "vera.h"

VERA_FN(fn_09)
{
    uint64_t h = 0xCBF29CE484222325ull;
    (void)arg; (void)out; (void)out_cap;
    for (size_t i = 0; i < len; i++) {
        h ^= in[i];
        OBF_GUARD(h, i, h *= 0x00000100000001B5ull);
        OBF_JUNK(h, len);
    }
    OBF_SPIN(h);
    return h;
}
