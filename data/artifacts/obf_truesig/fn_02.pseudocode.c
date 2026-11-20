
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

ulonglong fn_02(uchar *in,ulonglong len,ulonglong arg,uchar *out,ulonglong out_cap)

{
  uint uVar1;
  ulong uVar2;
  ulonglong uVar3;
  ulong uVar4;
  
  uVar2 = 0xcbf29ce484222325;
  if (len != 0) {
    uVar3 = 0;
    uVar4 = 0;
    do {
      uVar1 = (uint)uVar3 | 1;
      if (((uVar1 * uVar1 & 7) == 1) && (DAT_00104008 == 0x3c71)) {
        uVar2 = (in[uVar3] ^ uVar2) * 0x100000001b3;
      }
      else {
        uVar2 = (in[uVar3] ^ uVar2) + 0x51e3 ^ uVar4;
      }
      if (((((int)len + 1) * (int)len & 1U) != 0) || (DAT_00104010 != 0)) {
        uVar2 = (ulong)DAT_00104008 + (uVar2 ^ len << 7) * 0x2d6b;
        uVar2 = uVar2 >> 0xb ^ uVar2;
      }
      uVar3 = uVar3 + 1;
      uVar4 = uVar4 + 0x1f9;
    } while (len != uVar3);
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

