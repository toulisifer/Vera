
uint fn_08(byte *param_1,long param_2)

{
  uint uVar1;
  int iVar2;
  byte *pbVar3;
  
  if (param_2 != 0) {
    pbVar3 = param_1 + param_2;
    uVar1 = 0xffffffff;
    do {
      uVar1 = uVar1 ^ *param_1;
      iVar2 = 8;
      do {
        uVar1 = -(uVar1 & 1) & 0xf7179bf5 ^ uVar1 >> 1;
        iVar2 = iVar2 + -1;
      } while (iVar2 != 0);
      param_1 = param_1 + 1;
    } while (param_1 != pbVar3);
    return ~uVar1;
  }
  return 0;
}

