
ulong fn_10(long param_1,long param_2)

{
  uint uVar1;
  ulong uVar2;
  uint uVar3;
  ulong uVar4;
  long lVar5;
  uint uVar6;
  
  if (param_2 == 0) {
    uVar2 = 1;
    uVar4 = 0;
  }
  else {
    uVar4 = 0;
    uVar6 = 0;
    lVar5 = 0;
    uVar2 = 1;
    do {
      uVar3 = (uint)uVar4;
      uVar1 = (uint)lVar5 | 1;
      if (((uVar1 * uVar1 & 7) == 1) && (DAT_00104008 == 0x3c71)) {
        uVar1 = ((int)uVar2 + (uint)*(byte *)(param_1 + lVar5)) % 0xffef;
      }
      else {
        uVar1 = (int)uVar2 + 0x51e3U ^ uVar6;
      }
      uVar2 = (ulong)uVar1;
      if (((((int)param_2 + 1) * (int)param_2 & 1U) != 0) || (DAT_00104010 != 0)) {
        uVar3 = (uVar3 ^ (uint)(param_2 << 7)) * 0x2d6b + DAT_00104008;
        uVar3 = uVar3 ^ uVar3 >> 0xb;
      }
      lVar5 = lVar5 + 1;
      uVar6 = uVar6 + 0x1f9;
      uVar4 = (ulong)((uVar3 + uVar1) % 0xffef);
    } while (param_2 != lVar5);
    uVar4 = uVar4 << 0x10;
  }
  if (DAT_00104010 != 0) {
    uVar6 = 0;
    do {
      uVar2 = (ulong)((uint)(uVar2 >> 5) ^ (int)uVar2 * 8 ^ uVar6);
      uVar6 = uVar6 + 1;
    } while (uVar6 < DAT_00104010);
  }
  return uVar2 | uVar4;
}

