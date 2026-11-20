
uint64_t fn_13(uint8_t *in,size_t len,uint64_t arg,uint8_t *out,size_t out_cap)

{
  uint8_t uVar1;
  long lVar2;
  long in_FS_OFFSET;
  size_t out_cap_local;
  uint8_t *out_local;
  uint64_t arg_local;
  size_t len_local;
  uint8_t *in_local;
  uint8_t t;
  uint i;
  uint j;
  size_t n;
  uint8_t k [8];
  uint8_t s [256];
  
  lVar2 = *(long *)(in_FS_OFFSET + 0x28);
  j = 0;
  if (out_cap < len) {
    len = 0xffffffffffffffff;
  }
  else {
    for (i = 0; i < 8; i = i + 1) {
      k[i] = (uint8_t)(arg >> ((byte)(i << 3) & 0x3f));
    }
    for (i = 0; i < 0x100; i = i + 1) {
      s[i] = (uint8_t)i;
    }
    for (i = 0; i < 0x100; i = i + 1) {
      j = (k[i & 7] ^ i) + s[i] + j & 0xff;
      uVar1 = s[i];
      s[i] = s[j];
      s[j] = uVar1;
    }
    j = 0;
    i = 0;
    for (n = 0; n < len; n = n + 1) {
      i = i + 1 & 0xff;
      j = j + s[i] & 0xff;
      uVar1 = s[i];
      s[i] = s[j];
      s[j] = uVar1;
      out[n] = in[n] ^ s[(uint)s[j] + (uint)s[i] & 0xff];
    }
  }
  if (lVar2 == *(long *)(in_FS_OFFSET + 0x28)) {
    return len;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}

