
uint64_t fn_17(uint8_t *in,size_t len,uint64_t arg,uint8_t *out,size_t out_cap)

{
  uint64_t uVar1;
  size_t out_cap_local;
  uint8_t *out_local;
  uint64_t arg_local;
  size_t len_local;
  uint8_t *in_local;
  size_t i;
  size_t cnt;
  size_t total;
  size_t c;
  
  i = 0;
  cnt = 0;
  total = 0;
  while( true ) {
    if ((len <= i) || (in[i] == '\0')) {
      if (out_cap < cnt) {
        uVar1 = 0xffffffffffffffff;
      }
      else {
        i = 0;
        for (c = 0; c < cnt; c = c + 1) {
          out[c] = in[i];
          i = i + in[i + 1] + 2;
        }
        uVar1 = cnt << 0x20 | total;
      }
      return uVar1;
    }
    if ((len < i + 2) || (len < i + in[i + 1] + 2)) break;
    total = total + in[i + 1];
    cnt = cnt + 1;
    i = i + in[i + 1] + 2;
  }
  return 0xffffffffffffffff;
}

