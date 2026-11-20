
uint64_t fn_03(uint8_t *in,size_t len,uint64_t arg,uint8_t *out,size_t out_cap)

{
  size_t out_cap_local;
  uint8_t *out_local;
  uint64_t arg_local;
  size_t len_local;
  uint8_t *in_local;
  uint32_t a;
  uint32_t b;
  size_t i;
  
  a = 1;
  b = 0;
  for (i = 0; i < len; i = i + 1) {
    a = (in[i] + a) % 0xfff1;
    b = (b + a) % 0xfff1;
  }
  return (ulong)a | (ulong)b << 0x10;
}

