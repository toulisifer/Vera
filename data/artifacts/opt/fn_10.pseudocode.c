
uint fn_10(byte *param_1,long param_2)

{
  byte bVar1;
  uint uVar2;
  uint uVar3;
  byte *pbVar4;
  
  if (param_2 != 0) {
    pbVar4 = param_1 + param_2;
    uVar2 = 0;
    uVar3 = 1;
    do {
      bVar1 = *param_1;
      param_1 = param_1 + 1;
      uVar3 = (uVar3 + bVar1) % 0xffef;
      uVar2 = (uVar2 + uVar3) % 0xffef;
    } while (pbVar4 != param_1);
    return uVar2 << 0x10 | uVar3;
  }
  return 1;
}

