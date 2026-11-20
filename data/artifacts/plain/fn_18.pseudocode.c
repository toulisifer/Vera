
uint64_t fn_18(uint8_t *in,size_t len,uint64_t arg,uint8_t *out,size_t out_cap)

{
  long lVar1;
  uint64_t uVar2;
  uint8_t uVar3;
  long in_FS_OFFSET;
  size_t out_cap_local;
  uint8_t *out_local;
  uint64_t arg_local;
  size_t len_local;
  uint8_t *in_local;
  uint8_t c;
  uint q;
  size_t d;
  size_t i;
  uint8_t st [64];
  
  lVar1 = *(long *)(in_FS_OFFSET + 0x28);
  d = 0;
  q = 0;
  i = 0;
  do {
    if (len <= i) {
      if ((d == 0) && (q == 0)) {
        uVar2 = 0;
      }
      else {
        uVar2 = len + 1;
      }
LAB_00101288:
      if (lVar1 != *(long *)(in_FS_OFFSET + 0x28)) {
                    /* WARNING: Subroutine does not return */
        __stack_chk_fail();
      }
      return uVar2;
    }
    uVar3 = in[i];
    if (q == 2) {
      q = 1;
    }
    else if (q == 1) {
      if (uVar3 == '\\') {
        q = 2;
      }
      else if (uVar3 == '\"') {
        q = 0;
      }
    }
    else if (uVar3 == '\"') {
      q = 1;
    }
    else if (((uVar3 == '(') || (uVar3 == '[')) || (uVar3 == '{')) {
      if (d == 0x40) {
        uVar2 = i + 1;
        goto LAB_00101288;
      }
      if (uVar3 == '(') {
        uVar3 = ')';
      }
      else {
        uVar3 = uVar3 + '\x02';
      }
      st[d] = uVar3;
      d = d + 1;
    }
    else if (((uVar3 == ')') || (uVar3 == ']')) || (uVar3 == '}')) {
      if ((d == 0) || (uVar3 != st[d - 1])) {
        uVar2 = i + 1;
        goto LAB_00101288;
      }
      d = d - 1;
    }
    i = i + 1;
  } while( true );
}

