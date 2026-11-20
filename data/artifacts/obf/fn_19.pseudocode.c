
ulong fn_19(long param_1,ulong param_2,ulong param_3,long param_4,ulong param_5)

{
  byte bVar1;
  uint uVar2;
  byte bVar3;
  ulong uVar4;
  ulong uVar5;
  ulong uVar6;
  
  if (param_5 < param_2) {
    uVar6 = 0xffffffffffffffff;
  }
  else {
    uVar6 = 0;
    if (param_2 != 0) {
      uVar4 = 0;
      uVar6 = param_2;
      do {
        while( true ) {
          uVar5 = uVar6 + 1;
          bVar3 = (byte)(param_3 >> (sbyte)(((uint)uVar4 & 7) << 3));
          if ((((int)uVar5 * (int)uVar6 & 1U) != 0) || (DAT_00104010 != 0)) {
            bVar3 = (bVar3 ^ (byte)(uVar6 << 7)) * 'k' + (char)DAT_00104008;
          }
          uVar2 = (uint)uVar4 | 1;
          uVar6 = uVar5;
          if (((uVar2 * uVar2 & 7) == 1) && (DAT_00104008 == 0x3c71)) break;
          uVar4 = uVar4 + 1;
          if (param_2 == uVar4) {
            return param_2;
          }
        }
        bVar1 = (byte)uVar4 & 7;
        *(byte *)(param_4 + uVar4) =
             (bVar3 << bVar1 | bVar3 >> 8 - bVar1) ^ *(byte *)(param_1 + uVar4) ^ (byte)uVar4;
        uVar4 = uVar4 + 1;
      } while (param_2 != uVar4);
      return param_2;
    }
  }
  return uVar6;
}

