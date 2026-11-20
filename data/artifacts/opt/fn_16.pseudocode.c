
uint fn_16(long param_1,long param_2,undefined8 param_3)

{
  byte *pbVar1;
  uint uVar2;
  int iVar3;
  long lVar4;
  
  uVar2 = (uint)((ulong)param_3 >> 0x20) ^ (uint)param_3;
  if (param_2 != 0) {
    lVar4 = 0;
    do {
      pbVar1 = (byte *)(param_1 + lVar4);
      iVar3 = (int)lVar4;
      lVar4 = lVar4 + 1;
      uVar2 = (uint)*pbVar1 * 0x9d + iVar3 + (uVar2 << 7 | uVar2 >> 0x19);
    } while (param_2 != lVar4);
  }
  uVar2 = (uVar2 >> 0xf ^ uVar2) * 0x3b9d;
  return uVar2 >> 0xd ^ uVar2;
}

