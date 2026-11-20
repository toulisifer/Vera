#include "vera.h"

VERA_FN(fn_01)
{
    uint32_t h = 0xFFFFFFFFu;
    (void)arg; (void)out; (void)out_cap;
    OBF_SPIN(h);
    for (size_t i = 0; i < len; i++) {
        h ^= in[i];
        OBF_JUNK(h, i);
        for (unsigned b = 0; b < 8; b++)
            OBF_GUARD(h, len + b, h = (h >> 1) ^ (0xEDB88320u & (0u - (h & 1u))));
    }
    return (uint64_t)(h ^ 0xFFFFFFFFu);
}
