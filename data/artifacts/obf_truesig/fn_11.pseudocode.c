
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

ulonglong fn_11(uchar *in,ulonglong len,ulonglong arg,uchar *out,ulonglong out_cap)

{
  uint uVar1;
  ulong uVar2;
  ulonglong uVar3;
  uint uVar4;
  
  if (DAT_00104010 == 0) {
    uVar2 = 0x1d35;
  }
  else {
    uVar4 = 0;
    uVar2 = 0x1d35;
    do {
      uVar2 = (ulong)((uint)(uVar2 >> 5) ^ (int)uVar2 * 8 ^ uVar4);
      uVar4 = uVar4 + 1;
    } while (uVar4 < DAT_00104010);
  }
  if (len != 0) {
    uVar4 = 0;
    uVar3 = 0;
    do {
      uVar1 = (uint)uVar3 | 1;
      if (((uVar1 * uVar1 & 7) == 1) && (DAT_00104008 == 0x3c71)) {
        uVar1 = (uint)in[uVar3] + (int)uVar2 * 0x29;
      }
      else {
        uVar1 = (int)uVar2 + 0x51e3U ^ uVar4;
      }
      if (((((int)len + 1) * (int)len & 1U) != 0) || (DAT_00104010 != 0)) {
        uVar1 = (uVar1 ^ (uint)(len << 7)) * 0x2d6b + DAT_00104008;
        uVar1 = uVar1 ^ uVar1 >> 0xb;
      }
      uVar2 = (ulong)uVar1;
      uVar3 = uVar3 + 1;
      uVar4 = uVar4 + 0x1f9;
    } while (len != uVar3);
  }
  return uVar2;
}

