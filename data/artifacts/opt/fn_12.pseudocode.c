
undefined8 fn_12(uint *param_1,ulong param_2,undefined8 param_3,ulong *param_4,ulong param_5)

{
  uint uVar1;
  uint uVar2;
  int iVar3;
  
  if ((0x17 < param_2) && (7 < param_5)) {
    uVar2 = *param_1;
    iVar3 = 0;
    uVar1 = param_1[1];
    do {
      iVar3 = iVar3 + -0x714851d1;
      uVar2 = uVar2 + (uVar1 * 0x10 + param_1[2] ^ (uVar1 >> 5) + param_1[3] ^ iVar3 + uVar1);
      uVar1 = uVar1 + (uVar2 * 0x10 + param_1[4] ^ (uVar2 >> 5) + param_1[5] ^ iVar3 + uVar2);
    } while (iVar3 != -0x290a3a20);
    *param_4 = (((((((ulong)(uVar1 >> 0x18) << 8 | (ulong)(uVar1 >> 0x10 & 0xff)) << 8 |
                   (ulong)(uVar1 >> 8 & 0xff)) << 8 | (ulong)(uVar1 & 0xff)) << 8 |
                 (ulong)(uVar2 >> 0x18)) << 8 | (ulong)(uVar2 >> 0x10 & 0xff)) << 8 |
               (ulong)(uVar2 >> 8 & 0xff)) << 8 | (ulong)(uVar2 & 0xff);
    return 8;
  }
  return 0xffffffffffffffff;
}

