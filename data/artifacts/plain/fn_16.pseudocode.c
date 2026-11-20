
uint64_t fn_16(uint8_t *in,size_t len,uint64_t arg,uint8_t *out,size_t out_cap)

{
  uint uVar1;
  size_t out_cap_local;
  uint8_t *out_local;
  uint64_t arg_local;
  size_t len_local;
  uint8_t *in_local;
  uint32_t h;
  size_t i;
  
  h = (uint)(arg >> 0x20) ^ (uint)arg;
  for (i = 0; i < len; i = i + 1) {
    h = (h << 7 | h >> 0x19) + (uint)in[i] * 0x9d + (int)i;
  }
  uVar1 = (h ^ h >> 0xf) * 0x3b9d;
  return (ulong)(uVar1 ^ uVar1 >> 0xd);
}

