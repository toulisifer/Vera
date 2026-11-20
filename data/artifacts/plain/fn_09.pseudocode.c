
uint64_t fn_09(uint8_t *in,size_t len,uint64_t arg,uint8_t *out,size_t out_cap)

{
  size_t out_cap_local;
  uint8_t *out_local;
  uint64_t arg_local;
  size_t len_local;
  uint8_t *in_local;
  uint64_t h;
  size_t i;
  
  h = 0xcbf29ce484222325;
  for (i = 0; i < len; i = i + 1) {
    h = (h ^ in[i]) * 0x100000001b5;
  }
  return h;
}

