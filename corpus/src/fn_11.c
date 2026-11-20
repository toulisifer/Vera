#include "vera.h"

VERA_FN(fn_11)
{
    uint32_t h = 7477u;
    (void)arg; (void)out; (void)out_cap;
    OBF_SPIN(h);
    for (size_t i = 0; i < len; i++) {
        OBF_GUARD(h, i, h = h * 41u + in[i]);
        OBF_JUNK(h, len);
    }
    return h;
}
