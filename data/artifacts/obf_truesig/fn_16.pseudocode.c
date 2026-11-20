
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

ulonglong fn_16(uchar *in,ulonglong len,ulonglong arg,uchar *out,ulonglong out_cap)

{
  byte *pbVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  ulonglong uVar5;
  ulonglong uVar6;
  ulonglong uVar7;
  uint uVar8;
  
  uVar4 = (uint)(arg >> 0x20) ^ (uint)arg;
  if (len != 0) {
    uVar8 = 0;
    uVar5 = 0;
    uVar6 = len;
    do {
      while( true ) {
        uVar7 = uVar6 + 1;
        if ((((int)uVar7 * (int)uVar6 & 1U) != 0) || (DAT_00104010 != 0)) {
          uVar4 = DAT_00104008 + (uVar4 ^ (uint)(uVar6 << 7)) * 0x2d6b;
          uVar4 = uVar4 >> 0xb ^ uVar4;
        }
        uVar4 = uVar4 << 7 | uVar4 >> 0x19;
        uVar3 = (uint)uVar5;
        uVar2 = uVar3 | 1;
        uVar6 = uVar7;
        if (((uVar2 * uVar2 & 7) != 1) || (DAT_00104008 != 0x3c71)) break;
        pbVar1 = in + uVar5;
        uVar8 = uVar8 + 0x1f9;
        uVar5 = uVar5 + 1;
        uVar4 = uVar4 + (uint)*pbVar1 * 0x9d + uVar3;
        if (len == uVar5) goto LAB_001011c0;
      }
      uVar5 = uVar5 + 1;
      uVar4 = uVar4 + 0x51e3 ^ uVar8;
      uVar8 = uVar8 + 0x1f9;
    } while (len != uVar5);
  }
LAB_001011c0:
  if (DAT_00104010 != 0) {
    uVar8 = 0;
    do {
      uVar4 = uVar4 >> 5 ^ uVar4 * 8 ^ uVar8;
      uVar8 = uVar8 + 1;
    } while (uVar8 < DAT_00104010);
  }
  uVar4 = (uVar4 >> 0xf ^ uVar4) * 0x3b9d;
  return (ulong)(uVar4 >> 0xd ^ uVar4);
}

