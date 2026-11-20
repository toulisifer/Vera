
int fn_04(byte *param_1,long param_2)

{
  int iVar1;
  byte *pbVar2;
  byte *pbVar3;
  
  if (param_2 != 0) {
    iVar1 = 0x1505;
    pbVar2 = param_1;
    do {
      pbVar3 = pbVar2 + 1;
      iVar1 = iVar1 * 0x21 + (uint)*pbVar2;
      pbVar2 = pbVar3;
    } while (param_1 + param_2 != pbVar3);
    return iVar1;
  }
  return 0x1505;
}

