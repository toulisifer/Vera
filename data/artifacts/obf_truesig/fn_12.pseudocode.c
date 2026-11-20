
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

ulonglong fn_12(uchar *in,ulonglong len,ulonglong arg,uchar *out,ulonglong out_cap)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  ulonglong uVar4;
  int iVar5;
  uint uVar6;
  
  if ((len < 0x18) || (out_cap < 8)) {
    return 0xffffffffffffffff;
  }
  uVar6 = (int)len * 0x1f9;
  uVar3 = *(uint *)in;
  uVar2 = *(uint *)(in + 4);
  iVar5 = 0;
  do {
    while( true ) {
      uVar4 = len + 1;
      iVar5 = iVar5 + -0x714851d1;
      if ((((uint)len * (int)uVar4 & 1) != 0) || (DAT_00104010 != 0)) {
        uVar3 = ((uint)(len << 7) ^ uVar3) * 0x2d6b + DAT_00104008;
        uVar3 = uVar3 >> 0xb ^ uVar3;
      }
      uVar1 = (uint)len | 1;
      uVar3 = uVar3 + (uVar2 * 0x10 + *(int *)(in + 8) ^ (uVar2 >> 5) + *(int *)(in + 0xc) ^
                      iVar5 + uVar2);
      len = uVar4;
      if (((uVar1 * uVar1 & 7) != 1) || (DAT_00104008 != 0x3c71)) break;
      uVar6 = uVar6 + 0x1f9;
      uVar2 = uVar2 + (uVar3 * 0x10 + *(int *)(in + 0x10) ^ (uVar3 >> 5) + *(int *)(in + 0x14) ^
                      iVar5 + uVar3);
      if (iVar5 == -0x290a3a20) goto LAB_0010120c;
    }
    uVar2 = uVar2 + 0x51e3 ^ uVar6;
    uVar6 = uVar6 + 0x1f9;
  } while (iVar5 != -0x290a3a20);
LAB_0010120c:
  *(ulong *)out =
       (((((((ulong)(uVar2 >> 0x18) << 8 | (ulong)(uVar2 >> 0x10 & 0xff)) << 8 |
           (ulong)(uVar2 >> 8 & 0xff)) << 8 | (ulong)(uVar2 & 0xff)) << 8 | (ulong)(uVar3 >> 0x18))
         << 8 | (ulong)(uVar3 >> 0x10 & 0xff)) << 8 | (ulong)(uVar3 >> 8 & 0xff)) << 8 |
       (ulong)(uVar3 & 0xff);
  return 8;
}

