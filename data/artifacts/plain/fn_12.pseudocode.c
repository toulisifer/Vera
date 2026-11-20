
uint64_t fn_12(uint8_t *in,size_t len,uint64_t arg,uint8_t *out,size_t out_cap)

{
  uint64_t uVar1;
  size_t out_cap_local;
  uint8_t *out_local;
  uint64_t arg_local;
  size_t len_local;
  uint8_t *in_local;
  uint32_t v0;
  uint32_t v1;
  uint32_t s;
  uint r;
  uint32_t k0;
  uint32_t k1;
  uint32_t k2;
  uint32_t k3;
  
  s = 0;
  if ((len < 0x18) || (out_cap < 8)) {
    uVar1 = 0xffffffffffffffff;
  }
  else {
    v0 = *(uint32_t *)in;
    v1 = *(uint32_t *)(in + 4);
    for (r = 0; r < 0x20; r = r + 1) {
      s = s + 0x8eb7ae2f;
      v0 = v0 + (*(int *)(in + 0xc) + (v1 >> 5) ^ v1 * 0x10 + *(int *)(in + 8) ^ s + v1);
      v1 = v1 + (*(int *)(in + 0x14) + (v0 >> 5) ^ v0 * 0x10 + *(int *)(in + 0x10) ^ s + v0);
    }
    *out = (uint8_t)v0;
    out[1] = (uint8_t)(v0 >> 8);
    out[2] = (uint8_t)(v0 >> 0x10);
    out[3] = (uint8_t)(v0 >> 0x18);
    out[4] = (uint8_t)v1;
    out[5] = (uint8_t)(v1 >> 8);
    out[6] = (uint8_t)(v1 >> 0x10);
    out[7] = (uint8_t)(v1 >> 0x18);
    uVar1 = 8;
  }
  return uVar1;
}

