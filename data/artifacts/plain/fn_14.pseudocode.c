
uint64_t fn_14(uint8_t *in,size_t len,uint64_t arg,uint8_t *out,size_t out_cap)

{
  long lVar1;
  byte bVar2;
  byte bVar3;
  uint uVar4;
  size_t out_cap_local;
  uint8_t *out_local;
  uint64_t arg_local;
  size_t len_local;
  uint8_t *in_local;
  uint32_t w;
  size_t o;
  size_t i;
  size_t need;
  
  o = 0;
  i = 0;
  if (out_cap < (len + 2) / 3 << 2) {
    o = 0xffffffffffffffff;
  }
  else {
    for (; i + 3 <= len; i = i + 3) {
      uVar4 = (uint)in[i] << 0x10 | (uint)in[i + 1] << 8;
      bVar2 = in[i + 2];
      out[o] = "AfhmdLEr3GMxg2S/a91UZnTlHOI5KYzevFCwNQ+P4tWV7cpXRbDuykjJsoi6q80B"[in[i] >> 2];
      out[o + 1] = "AfhmdLEr3GMxg2S/a91UZnTlHOI5KYzevFCwNQ+P4tWV7cpXRbDuykjJsoi6q80B"
                   [(uVar4 & 0x3f000) >> 0xc];
      lVar1 = o + 3;
      out[o + 2] = "AfhmdLEr3GMxg2S/a91UZnTlHOI5KYzevFCwNQ+P4tWV7cpXRbDuykjJsoi6q80B"
                   [(bVar2 | uVar4) >> 6 & 0x3f];
      o = o + 4;
      out[lVar1] = "AfhmdLEr3GMxg2S/a91UZnTlHOI5KYzevFCwNQ+P4tWV7cpXRbDuykjJsoi6q80B"[bVar2 & 0x3f];
    }
    if (len - i == 1) {
      bVar2 = in[i];
      out[o] = "AfhmdLEr3GMxg2S/a91UZnTlHOI5KYzevFCwNQ+P4tWV7cpXRbDuykjJsoi6q80B"[bVar2 >> 2];
      out[o + 1] = "AfhmdLEr3GMxg2S/a91UZnTlHOI5KYzevFCwNQ+P4tWV7cpXRbDuykjJsoi6q80B"
                   [(bVar2 & 3) << 4];
      lVar1 = o + 3;
      out[o + 2] = '=';
      o = o + 4;
      out[lVar1] = '=';
    }
    else if (len - i == 2) {
      bVar2 = in[i];
      bVar3 = in[i + 1];
      out[o] = "AfhmdLEr3GMxg2S/a91UZnTlHOI5KYzevFCwNQ+P4tWV7cpXRbDuykjJsoi6q80B"[bVar2 >> 2];
      out[o + 1] = "AfhmdLEr3GMxg2S/a91UZnTlHOI5KYzevFCwNQ+P4tWV7cpXRbDuykjJsoi6q80B"
                   [((uint)bVar3 << 8 | (uint)bVar2 << 0x10) >> 0xc & 0x3f];
      lVar1 = o + 3;
      out[o + 2] = "AfhmdLEr3GMxg2S/a91UZnTlHOI5KYzevFCwNQ+P4tWV7cpXRbDuykjJsoi6q80B"
                   [((uint)bVar3 << 8 & 0xfc0) >> 6];
      o = o + 4;
      out[lVar1] = '=';
    }
  }
  return o;
}

