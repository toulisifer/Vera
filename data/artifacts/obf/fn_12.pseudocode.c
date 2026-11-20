
undefined8 fn_12(uint *param_1,ulong param_2,undefined8 param_3,ulong *param_4,ulong param_5)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  ulong uVar4;
  int iVar5;
  uint uVar6;
  
  if ((param_2 < 0x18) || (param_5 < 8)) {
    return 0xffffffffffffffff;
  }
  uVar6 = (int)param_2 * 0x1f9;
  uVar3 = *param_1;
  uVar2 = param_1[1];
  iVar5 = 0;
  do {
    while( true ) {
      uVar4 = param_2 + 1;
      iVar5 = iVar5 + -0x714851d1;
      if ((((uint)param_2 * (int)uVar4 & 1) != 0) || (DAT_00104010 != 0)) {
        uVar3 = ((uint)(param_2 << 7) ^ uVar3) * 0x2d6b + DAT_00104008;
        uVar3 = uVar3 >> 0xb ^ uVar3;
      }
      uVar1 = (uint)param_2 | 1;
      uVar3 = uVar3 + (uVar2 * 0x10 + param_1[2] ^ (uVar2 >> 5) + param_1[3] ^ iVar5 + uVar2);
      param_2 = uVar4;
      if (((uVar1 * uVar1 & 7) != 1) || (DAT_00104008 != 0x3c71)) break;
      uVar6 = uVar6 + 0x1f9;
      uVar2 = uVar2 + (uVar3 * 0x10 + param_1[4] ^ (uVar3 >> 5) + param_1[5] ^ iVar5 + uVar3);
      if (iVar5 == -0x290a3a20) goto LAB_0010120c;
    }
    uVar2 = uVar2 + 0x51e3 ^ uVar6;
    uVar6 = uVar6 + 0x1f9;
  } while (iVar5 != -0x290a3a20);
LAB_0010120c:
  *param_4 = (((((((ulong)(uVar2 >> 0x18) << 8 | (ulong)(uVar2 >> 0x10 & 0xff)) << 8 |
                 (ulong)(uVar2 >> 8 & 0xff)) << 8 | (ulong)(uVar2 & 0xff)) << 8 |
               (ulong)(uVar3 >> 0x18)) << 8 | (ulong)(uVar3 >> 0x10 & 0xff)) << 8 |
             (ulong)(uVar3 >> 8 & 0xff)) << 8 | (ulong)(uVar3 & 0xff);
  return 8;
}

