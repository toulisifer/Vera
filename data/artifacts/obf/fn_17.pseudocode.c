
ulong fn_17(long param_1,ulong param_2,undefined8 param_3,long param_4,ulong param_5)

{
  uint uVar1;
  int iVar2;
  ulong uVar3;
  ulong uVar4;
  ulong uVar5;
  ulong uVar6;
  ulong uVar7;
  
  if (param_2 == 0) {
    return 0;
  }
  uVar4 = 0;
  uVar5 = 0;
  uVar7 = 0;
  do {
    if (*(char *)(param_1 + uVar7) == '\0') break;
    if (param_2 < uVar7 + 2) {
      return 0xffffffffffffffff;
    }
    uVar6 = (ulong)*(byte *)(param_1 + 1 + uVar7);
    uVar3 = uVar7 + 2 + uVar6;
    if (param_2 < uVar3) {
      return 0xffffffffffffffff;
    }
    iVar2 = (int)(uVar7 + uVar5);
    if ((((iVar2 + 1) * iVar2 & 1U) != 0) || (DAT_00104010 != 0)) {
      uVar4 = ((uVar7 + uVar5) * 0x80 ^ uVar4) * 0x2d6b + (ulong)DAT_00104008;
      uVar4 = uVar4 >> 0xb ^ uVar4;
    }
    uVar4 = uVar4 + uVar6;
    uVar5 = uVar5 + 1;
    uVar7 = uVar3;
  } while (uVar3 < param_2);
  uVar7 = 0xffffffffffffffff;
  if ((uVar5 <= param_5) && (uVar7 = uVar5 << 0x20 | uVar4, uVar5 != 0)) {
    uVar5 = uVar5 + param_2;
    uVar4 = 0;
    param_4 = param_4 - param_2;
    uVar3 = param_2 * 0x1f9;
    do {
      uVar1 = (uint)param_2 | 1;
      if (((uVar1 * uVar1 & 7) == 1) && (DAT_00104008 == 0x3c71)) {
        *(undefined1 *)(param_4 + param_2) = *(undefined1 *)(param_1 + uVar4);
      }
      else {
        uVar4 = uVar4 + 0x51e3 ^ uVar3;
      }
      param_2 = param_2 + 1;
      uVar3 = uVar3 + 0x1f9;
      uVar4 = (ulong)*(byte *)(param_1 + 1 + uVar4) + 2 + uVar4;
    } while (param_2 != uVar5);
  }
  return uVar7;
}

