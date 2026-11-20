
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

ulonglong fn_19(uchar *in,ulonglong len,ulonglong arg,uchar *out,ulonglong out_cap)

{
  byte bVar1;
  uint uVar2;
  byte bVar3;
  ulonglong uVar4;
  ulonglong uVar5;
  ulonglong uVar6;
  
  if (out_cap < len) {
    uVar6 = 0xffffffffffffffff;
  }
  else {
    uVar6 = 0;
    if (len != 0) {
      uVar4 = 0;
      uVar6 = len;
      do {
        while( true ) {
          uVar5 = uVar6 + 1;
          bVar3 = (byte)(arg >> (sbyte)(((uint)uVar4 & 7) << 3));
          if ((((int)uVar5 * (int)uVar6 & 1U) != 0) || (DAT_00104010 != 0)) {
            bVar3 = (bVar3 ^ (byte)(uVar6 << 7)) * 'k' + (char)DAT_00104008;
          }
          uVar2 = (uint)uVar4 | 1;
          uVar6 = uVar5;
          if (((uVar2 * uVar2 & 7) == 1) && (DAT_00104008 == 0x3c71)) break;
          uVar4 = uVar4 + 1;
          if (len == uVar4) {
            return len;
          }
        }
        bVar1 = (byte)uVar4 & 7;
        out[uVar4] = (bVar3 << bVar1 | bVar3 >> 8 - bVar1) ^ in[uVar4] ^ (byte)uVar4;
        uVar4 = uVar4 + 1;
      } while (len != uVar4);
      return len;
    }
  }
  return uVar6;
}

