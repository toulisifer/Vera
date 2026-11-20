
uint64_t fn_15(uint8_t *in,size_t len,uint64_t arg,uint8_t *out,size_t out_cap)

{
  long lVar1;
  size_t out_cap_local;
  uint8_t *out_local;
  uint64_t arg_local;
  size_t len_local;
  uint8_t *in_local;
  size_t need;
  size_t i;
  size_t o;
  size_t r;
  
  need = 0;
  o = 0;
  for (i = 0; i < len; i = i + r) {
    for (r = 1; ((r + i < len && (in[i + r] == in[i])) && (r < 0xff)); r = r + 1) {
    }
    need = need + 2;
  }
  if (out_cap < need) {
    o = 0xffffffffffffffff;
  }
  else {
    for (i = 0; i < len; i = i + r) {
      for (r = 1; ((r + i < len && (in[i + r] == in[i])) && (r < 0xff)); r = r + 1) {
      }
      lVar1 = o + 1;
      out[o] = (uint8_t)r;
      o = o + 2;
      out[lVar1] = in[i];
    }
  }
  return o;
}

