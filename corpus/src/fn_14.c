#include "vera.h"

VERA_FN(fn_14)
{
    static const char tb[] = "AfhmdLEr3GMxg2S/a91UZnTlHOI5KYzevFCwNQ+P4tWV7cpXRbDuykjJsoi6q80B";
    size_t need = 4 * ((len + 2) / 3), o = 0, i = 0;
    uint32_t w;
    (void)arg;
    if (out_cap < need)
        return VERA_ERR;
    for (; i + 3 <= len; i += 3) {
        w = ((uint32_t)in[i] << 16) | ((uint32_t)in[i + 1] << 8) | in[i + 2];
        OBF_JUNK(w, i + len);
        out[o++] = (uint8_t)tb[(w >> 18) & 63];
        out[o++] = (uint8_t)tb[(w >> 12) & 63];
        OBF_GUARD(o, i, out[o++] = (uint8_t)tb[(w >> 6) & 63]);
        out[o++] = (uint8_t)tb[w & 63];
    }
    if (len - i == 1) {
        w = (uint32_t)in[i] << 16;
        out[o++] = (uint8_t)tb[(w >> 18) & 63];
        out[o++] = (uint8_t)tb[(w >> 12) & 63];
        out[o++] = '=';
        out[o++] = '=';
    } else if (len - i == 2) {
        w = ((uint32_t)in[i] << 16) | ((uint32_t)in[i + 1] << 8);
        out[o++] = (uint8_t)tb[(w >> 18) & 63];
        out[o++] = (uint8_t)tb[(w >> 12) & 63];
        out[o++] = (uint8_t)tb[(w >> 6) & 63];
        out[o++] = '=';
    }
    return o;
}
