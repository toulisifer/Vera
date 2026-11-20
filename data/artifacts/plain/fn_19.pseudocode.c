
uint64_t fn_19(uint8_t *in,size_t len,uint64_t arg,uint8_t *out,size_t out_cap)

{
  byte bVar1;
  byte bVar2;
  size_t out_cap_local;
  uint8_t *out_local;
  uint64_t arg_local;
  size_t len_local;
  uint8_t *in_local;
  uint8_t k;
  uint8_t r;
  size_t i;
  
  if (out_cap < len) {
    len = 0xffffffffffffffff;
  }
  else {
    for (i = 0; i < len; i = i + 1) {
      bVar1 = (byte)(arg >> (sbyte)(((uint)i & 7) << 3));
      bVar2 = (byte)i & 7;
      out[i] = in[i] ^ ((byte)((int)(uint)bVar1 >> (-bVar2 & 7)) | bVar1 << bVar2) ^ (byte)i;
    }
  }
  return len;
}

