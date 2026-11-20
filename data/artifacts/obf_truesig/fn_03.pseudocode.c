
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

ulonglong fn_03(uchar *in,ulonglong len,ulonglong arg,uchar *out,ulonglong out_cap)

{
  uint uVar1;
  ulong uVar2;
  uint uVar3;
  ulong uVar4;
  ulonglong uVar5;
  uint uVar6;
  
  if (len == 0) {
    uVar2 = 1;
    uVar4 = 0;
  }
  else {
    uVar4 = 0;
    uVar6 = 0;
    uVar5 = 0;
    uVar2 = 1;
    do {
      uVar3 = (uint)uVar4;
      uVar1 = (uint)uVar5 | 1;
      if (((uVar1 * uVar1 & 7) == 1) && (DAT_00104008 == 0x3c71)) {
        uVar1 = ((int)uVar2 + (uint)in[uVar5]) % 0xfff1;
      }
      else {
        uVar1 = (int)uVar2 + 0x51e3U ^ uVar6;
      }
      uVar2 = (ulong)uVar1;
      if (((((int)len + 1) * (int)len & 1U) != 0) || (DAT_00104010 != 0)) {
        uVar3 = (uVar3 ^ (uint)(len << 7)) * 0x2d6b + DAT_00104008;
        uVar3 = uVar3 ^ uVar3 >> 0xb;
      }
      uVar5 = uVar5 + 1;
      uVar6 = uVar6 + 0x1f9;
      uVar4 = (ulong)((uVar3 + uVar1) % 0xfff1);
    } while (len != uVar5);
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

