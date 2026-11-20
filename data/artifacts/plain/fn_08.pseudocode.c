
uint64_t fn_08(uint8_t *in,size_t len,uint64_t arg,uint8_t *out,size_t out_cap)

{
  size_t out_cap_local;
  uint8_t *out_local;
  uint64_t arg_local;
  size_t len_local;
  uint8_t *in_local;
  uint32_t h;
  uint b;
  size_t i;
  
  h = 0xffffffff;
  for (i = 0; i < len; i = i + 1) {
    h = h ^ in[i];
    for (b = 0; b < 8; b = b + 1) {
      h = -(h & 1) & 0xf7179bf5 ^ h >> 1;
    }
  }
  return (ulong)~h;
}

