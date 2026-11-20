
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

ulonglong fn_20(uchar *in,ulonglong len,ulonglong arg,uchar *out,ulonglong out_cap)

{
  undefined1 uVar1;
  uint uVar2;
  ulong uVar3;
  ulong uVar4;
  ulong uVar5;
  ulong uVar6;
  long in_FS_OFFSET;
  undefined8 local_18;
  long local_10;
  
  uVar6 = 0xffffffffffffffff;
  local_10 = *(long *)(in_FS_OFFSET + 0x28);
  if (len <= out_cap) {
    uVar6 = len + 7;
    local_18 = 0x706050403020100;
    do {
      uVar5 = (1 - len) + uVar6;
      uVar4 = arg / uVar5;
      uVar5 = arg % uVar5;
      if (((((int)uVar6 + 1) * (int)uVar6 & 1U) != 0) || (DAT_00104018 != 0)) {
        uVar4 = (ulong)DAT_00104010 + (uVar6 << 7 ^ uVar4) * 0x2d6b;
        uVar4 = uVar4 >> 0xb ^ uVar4;
      }
      uVar1 = *(undefined1 *)((long)&local_18 + uVar6 + (-0x18 - len) + 0x18);
      *(undefined1 *)((long)&local_18 + uVar6 + (-0x18 - len) + 0x18) =
           *(undefined1 *)((long)&local_18 + uVar5);
      uVar6 = uVar6 - 1;
      *(undefined1 *)((long)&local_18 + uVar5) = uVar1;
      arg = uVar4;
    } while (len != uVar6);
    uVar5 = 8;
    uVar4 = 0;
    if (7 < uVar6) {
      do {
        uVar3 = uVar5 - 8;
        do {
          while ((uVar4 = uVar3, uVar2 = (uint)uVar4 | 1, (uVar2 * uVar2 & 7) != 1 ||
                 (DAT_00104010 != 0x3c71))) {
            uVar3 = uVar4 + 1;
            if (uVar5 == uVar4 + 1) goto LAB_00101258;
          }
          out[uVar4] = in[(ulong)*(byte *)((long)&local_10 + (uVar4 - uVar5)) + (uVar5 - 8)];
          uVar3 = uVar4 + 1;
        } while (uVar5 != uVar4 + 1);
LAB_00101258:
        uVar4 = uVar4 + 1;
        uVar5 = uVar5 + 8;
      } while (uVar5 <= uVar6);
    }
    if (uVar4 < uVar6) {
      do {
        out[uVar4] = in[uVar4];
        uVar4 = uVar4 + 1;
      } while (uVar4 != uVar6);
    }
  }
  if (local_10 != *(long *)(in_FS_OFFSET + 0x28)) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
  return uVar6;
}

