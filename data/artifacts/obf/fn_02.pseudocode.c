
ulong fn_02(long param_1,long param_2)

{
  uint uVar1;
  ulong uVar2;
  long lVar3;
  ulong uVar4;
  
  uVar2 = 0xcbf29ce484222325;
  if (param_2 != 0) {
    lVar3 = 0;
    uVar4 = 0;
    do {
      uVar2 = *(byte *)(param_1 + lVar3) ^ uVar2;
      uVar1 = (uint)lVar3 | 1;
      if (((uVar1 * uVar1 & 7) == 1) && (DAT_00104008 == 0x3c71)) {
        uVar2 = uVar2 * 0x100000001b3;
      }
      else {
        uVar2 = uVar2 + 0x51e3 ^ uVar4;
      }
      if (((((int)param_2 + 1) * (int)param_2 & 1U) != 0) || (DAT_00104010 != 0)) {
        uVar2 = (ulong)DAT_00104008 + (uVar2 ^ param_2 << 7) * 0x2d6b;
        uVar2 = uVar2 >> 0xb ^ uVar2;
      }
      lVar3 = lVar3 + 1;
      uVar4 = uVar4 + 0x1f9;
    } while (param_2 != lVar3);
  }
  if (DAT_00104010 != 0) {
    uVar4 = 0;
    do {
      uVar2 = uVar2 * 8 ^ uVar2 >> 5 ^ uVar4;
      uVar4 = uVar4 + 1;
    } while ((uint)uVar4 < DAT_00104010);
  }
  return uVar2;
}

