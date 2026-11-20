#include "vera.h"

VERA_FN(fn_04)
{
    uint32_t h = 5381u;
    (void)arg; (void)out; (void)out_cap;
    OBF_SPIN(h);
    for (size_t i = 0; i < len; i++) {
        OBF_GUARD(h, i, h = ((h << 5) + h) + in[i]);
        OBF_JUNK(h, len);
    }
    return h;
}
