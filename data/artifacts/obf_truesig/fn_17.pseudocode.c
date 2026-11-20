
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

ulonglong fn_17(uchar *in,ulonglong len,ulonglong arg,uchar *out,ulonglong out_cap)

{
  uint uVar1;
  int iVar2;
  ulong uVar3;
  ulong uVar4;
  ulong uVar5;
  ulonglong uVar6;
  ulong uVar7;
  ulonglong uVar8;
  
  if (len == 0) {
    return 0;
  }
  uVar3 = 0;
  uVar7 = 0;
  uVar5 = 0;
  do {
    if (in[uVar5] == '\0') break;
    if (len < uVar5 + 2) {
      return 0xffffffffffffffff;
    }
    uVar4 = uVar5 + 2 + (ulong)in[uVar5 + 1];
    if (len < uVar4) {
      return 0xffffffffffffffff;
    }
    iVar2 = (int)(uVar5 + uVar7);
    if ((((iVar2 + 1) * iVar2 & 1U) != 0) || (DAT_00104010 != 0)) {
      uVar3 = ((uVar5 + uVar7) * 0x80 ^ uVar3) * 0x2d6b + (ulong)DAT_00104008;
      uVar3 = uVar3 >> 0xb ^ uVar3;
    }
    uVar3 = uVar3 + in[uVar5 + 1];
    uVar7 = uVar7 + 1;
    uVar5 = uVar4;
  } while (uVar4 < len);
  uVar8 = 0xffffffffffffffff;
  if ((uVar7 <= out_cap) && (uVar8 = uVar7 << 0x20 | uVar3, uVar7 != 0)) {
    uVar5 = 0;
    uVar3 = len * 0x1f9;
    uVar6 = len;
    do {
      uVar1 = (uint)uVar6 | 1;
      if (((uVar1 * uVar1 & 7) == 1) && (DAT_00104008 == 0x3c71)) {
        out[uVar6 - len] = in[uVar5];
      }
      else {
        uVar5 = uVar5 + 0x51e3 ^ uVar3;
      }
      uVar6 = uVar6 + 1;
      uVar3 = uVar3 + 0x1f9;
      uVar5 = (ulong)in[uVar5 + 1] + 2 + uVar5;
    } while (uVar6 != uVar7 + len);
  }
  return uVar8;
}

