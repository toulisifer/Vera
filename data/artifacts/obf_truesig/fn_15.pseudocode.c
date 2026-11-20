
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

ulonglong fn_15(uchar *in,ulonglong len,ulonglong arg,uchar *out,ulonglong out_cap)

{
  uchar *puVar1;
  uchar uVar2;
  uint uVar3;
  long lVar4;
  ulong uVar5;
  ulong uVar6;
  ulonglong uVar7;
  ulong uVar8;
  bool bVar9;
  
  if (len == 0) {
    return 0;
  }
  uVar5 = 0;
  uVar8 = 0;
  do {
    uVar6 = uVar8 + 1;
    if (uVar6 < len) {
      lVar4 = 2;
      uVar2 = in[uVar8];
      if (in[uVar8 + 1] == uVar2) {
        do {
          uVar6 = lVar4 + uVar8;
          if (len - uVar8 == lVar4) break;
          puVar1 = in + uVar8 + lVar4;
          bVar9 = lVar4 != 0xff;
          lVar4 = lVar4 + 1;
        } while (*puVar1 == uVar2 && bVar9);
      }
    }
    if ((((uVar6 + 1) * uVar6 & 1) != 0) || (DAT_00104010 != 0)) {
      uVar5 = (ulong)DAT_00104008 + (uVar6 << 7 ^ uVar5) * 0x2d6b;
      uVar5 = uVar5 >> 0xb ^ uVar5;
    }
    uVar5 = uVar5 + 2;
    uVar8 = uVar6;
  } while (uVar6 < len);
  if (out_cap < uVar5) {
    return 0xffffffffffffffff;
  }
  uVar7 = 0;
  uVar8 = 1;
  uVar5 = 0;
  if (len < 2) goto LAB_00101250;
  do {
    uVar6 = uVar8;
    lVar4 = 1;
    do {
      if (in[uVar6] != in[uVar5]) break;
      if (lVar4 == 0xff) {
        lVar4 = 0xffffffff;
        break;
      }
      uVar6 = uVar6 + 1;
      lVar4 = lVar4 + 1;
    } while (uVar6 < len);
    while( true ) {
      out[uVar7] = (uchar)lVar4;
      uVar3 = (uint)uVar6 | 1;
      if (((uVar3 * uVar3 & 7) == 1) && (DAT_00104008 == 0x3c71)) {
        out[uVar7 + 1] = in[uVar5];
        uVar7 = uVar7 + 2;
      }
      else {
        uVar7 = uVar7 + 0x51e4 ^ uVar6 * 0x1f9;
      }
      if (len <= uVar6) {
        return uVar7;
      }
      uVar8 = uVar6 + 1;
      uVar5 = uVar6;
      if (uVar8 < len) break;
LAB_00101250:
      uVar6 = uVar8;
      lVar4 = 1;
    }
  } while( true );
}

