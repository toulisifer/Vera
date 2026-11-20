#include "vera.h"

VERA_FN(fn_12)
{
    uint32_t v0, v1, k0, k1, k2, k3, s = 0u;
    (void)arg;
    if (len < 24 || out_cap < 8)
        return VERA_ERR;
    v0 = VERA_LD32(in);
    v1 = VERA_LD32(in + 4);
    k0 = VERA_LD32(in + 8);
    k1 = VERA_LD32(in + 12);
    k2 = VERA_LD32(in + 16);
    k3 = VERA_LD32(in + 20);
    for (unsigned r = 0; r < 32; r++) {
        s += 0x8EB7AE2Fu;
        OBF_JUNK(v0, r + len);
        v0 += ((v1 << 4) + k0) ^ (v1 + s) ^ ((v1 >> 5) + k1);
        OBF_GUARD(v1, r + len, v1 += ((v0 << 4) + k2) ^ (v0 + s) ^ ((v0 >> 5) + k3));
    }
    VERA_ST32(out, v0);
    VERA_ST32(out + 4, v1);
    return 8;
}
