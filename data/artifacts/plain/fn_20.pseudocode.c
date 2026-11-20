
uint64_t fn_20(uint8_t *in,size_t len,uint64_t arg,uint8_t *out,size_t out_cap)

{
  uint8_t uVar1;
  long lVar2;
  ulong uVar3;
  long in_FS_OFFSET;
  size_t out_cap_local;
  uint8_t *out_local;
  uint64_t arg_local;
  size_t len_local;
  uint8_t *in_local;
  uint8_t t;
  uint64_t sd;
  size_t b;
  size_t n;
  size_t j;
  uint8_t p [8];
  
  lVar2 = *(long *)(in_FS_OFFSET + 0x28);
  if (out_cap < len) {
    len = 0xffffffffffffffff;
  }
  else {
    for (n = 0; n < 8; n = n + 1) {
      p[n] = (uint8_t)n;
    }
    sd = arg;
    for (n = 7; n != 0; n = n - 1) {
      uVar3 = sd % (n + 1);
      sd = sd / (n + 1);
      uVar1 = p[n];
      p[n] = p[uVar3];
      p[uVar3] = uVar1;
    }
    for (b = 0; b + 8 <= len; b = b + 8) {
      for (n = 0; n < 8; n = n + 1) {
        out[b + n] = in[p[n] + b];
      }
    }
    for (; b < len; b = b + 1) {
      out[b] = in[b];
    }
  }
  if (lVar2 == *(long *)(in_FS_OFFSET + 0x28)) {
    return len;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}

