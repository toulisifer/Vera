#include "vera.h"

VERA_FN(fn_03)
{
    uint32_t a = 1u, b = 0u;
    (void)arg; (void)out; (void)out_cap;
    for (size_t i = 0; i < len; i++) {
        OBF_GUARD(a, i, a = (a + in[i]) % 65521u);
        OBF_JUNK(b, len);
        b = (b + a) % 65521u;
    }
    OBF_SPIN(a);
    return ((uint64_t)b << 16) | a;
}
