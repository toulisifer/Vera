
ulong fn_20(long param_1,ulong param_2,ulong param_3,long param_4,ulong param_5)

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
  if (param_2 <= param_5) {
    uVar6 = param_2 + 7;
    local_18 = 0x706050403020100;
    do {
      uVar5 = (1 - param_2) + uVar6;
      uVar4 = param_3 / uVar5;
      param_3 = param_3 % uVar5;
      if (((((int)uVar6 + 1) * (int)uVar6 & 1U) != 0) || (DAT_00104018 != 0)) {
        uVar4 = (ulong)DAT_00104010 + (uVar6 << 7 ^ uVar4) * 0x2d6b;
        uVar4 = uVar4 >> 0xb ^ uVar4;
      }
      uVar1 = *(undefined1 *)((long)&local_18 + uVar6 + (-0x18 - param_2) + 0x18);
      *(undefined1 *)((long)&local_18 + uVar6 + (-0x18 - param_2) + 0x18) =
           *(undefined1 *)((long)&local_18 + param_3);
      uVar6 = uVar6 - 1;
      *(undefined1 *)((long)&local_18 + param_3) = uVar1;
      param_3 = uVar4;
    } while (param_2 != uVar6);
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
          *(undefined1 *)(param_4 + uVar4) =
               *(undefined1 *)
                (param_1 + (uVar5 - 8) + (ulong)*(byte *)((long)&local_10 + (uVar4 - uVar5)));
          uVar3 = uVar4 + 1;
        } while (uVar5 != uVar4 + 1);
LAB_00101258:
        uVar4 = uVar4 + 1;
        uVar5 = uVar5 + 8;
      } while (uVar5 <= uVar6);
    }
    if (uVar4 < uVar6) {
      do {
        *(undefined1 *)(param_4 + uVar4) = *(undefined1 *)(param_1 + uVar4);
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

