
ulong fn_19(long param_1,ulong param_2,ulong param_3,long param_4,ulong param_5)

{
  byte bVar1;
  ulong uVar2;
  byte bVar3;
  
  if (param_2 <= param_5) {
    if (param_2 != 0) {
      uVar2 = 0;
      do {
        bVar1 = (byte)uVar2 & 7;
        bVar3 = (byte)(param_3 >> bVar1 * '\b');
        *(byte *)(param_4 + uVar2) =
             (bVar3 << bVar1 | bVar3 >> 8 - bVar1) ^ *(byte *)(param_1 + uVar2) ^ (byte)uVar2;
        uVar2 = uVar2 + 1;
      } while (param_2 != uVar2);
    }
    return param_2;
  }
  return 0xffffffffffffffff;
}

