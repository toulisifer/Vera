
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

ulonglong fn_08(uchar *in,ulonglong len,ulonglong arg,uchar *out,ulonglong out_cap)

{
  uint uVar1;
  uint uVar2;
  ulonglong uVar3;
  uint uVar4;
  uint uVar5;
  ulonglong uVar6;
  ulonglong uVar7;
  uint uVar8;
  
  if (DAT_00104010 == 0) {
    uVar2 = 0xffffffff;
  }
  else {
    uVar4 = 0;
    uVar2 = 0xffffffff;
    do {
      uVar2 = uVar2 >> 5 ^ uVar2 * 8 ^ uVar4;
      uVar4 = uVar4 + 1;
    } while (uVar4 < DAT_00104010);
  }
  if (len == 0) {
    return (ulong)~uVar2;
  }
  uVar4 = (int)len * 0x1f9;
  uVar8 = 0;
  uVar6 = 0;
  do {
    uVar2 = uVar2 ^ in[uVar6];
    uVar7 = uVar6 + 1;
    uVar3 = len;
    uVar5 = uVar4;
    if ((((int)uVar6 * (int)uVar7 & 1U) != 0) || (DAT_00104010 != 0)) {
      uVar2 = (uVar2 ^ uVar8) * 0x2d6b + DAT_00104008;
      uVar2 = uVar2 ^ uVar2 >> 0xb;
    }
    do {
      while ((uVar1 = (uint)uVar3 | 1, (uVar1 * uVar1 & 7) == 1 && (DAT_00104008 == 0x3c71))) {
        uVar3 = uVar3 + 1;
        uVar2 = -(uVar2 & 1) & 0xf7179bf5 ^ uVar2 >> 1;
        uVar5 = uVar5 + 0x1f9;
        if (len + 8 == uVar3) goto LAB_00101200;
      }
      uVar3 = uVar3 + 1;
      uVar2 = uVar2 + 0x51e3 ^ uVar5;
      uVar5 = uVar5 + 0x1f9;
    } while (len + 8 != uVar3);
LAB_00101200:
    uVar8 = uVar8 + 0x80;
    uVar6 = uVar7;
    if (uVar7 == len) {
      return (ulong)~uVar2;
    }
  } while( true );
}

