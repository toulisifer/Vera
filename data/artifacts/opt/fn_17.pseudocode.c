
ulong fn_17(long param_1,ulong param_2,undefined8 param_3,undefined1 *param_4,ulong param_5)

{
  ulong uVar1;
  undefined1 *puVar2;
  undefined1 *puVar3;
  long lVar4;
  ulong uVar5;
  ulong uVar6;
  ulong uVar7;
  
  uVar7 = 0;
  uVar6 = 0;
  uVar1 = 0;
  if (param_2 == 0) {
    return 0;
  }
  do {
    if (*(char *)(param_1 + uVar1) == '\0') break;
    if (param_2 < uVar1 + 2) {
      return 0xffffffffffffffff;
    }
    uVar5 = (ulong)*(byte *)(param_1 + 1 + uVar1);
    uVar1 = uVar1 + 2 + uVar5;
    if (param_2 < uVar1) {
      return 0xffffffffffffffff;
    }
    uVar7 = uVar7 + uVar5;
    uVar6 = uVar6 + 1;
  } while (uVar1 < param_2);
  uVar1 = 0xffffffffffffffff;
  if ((uVar6 <= param_5) && (uVar1 = uVar6 << 0x20 | uVar7, uVar6 != 0)) {
    lVar4 = 0;
    puVar2 = param_4;
    do {
      puVar3 = puVar2 + 1;
      *puVar2 = *(undefined1 *)(param_1 + lVar4);
      lVar4 = (ulong)*(byte *)(param_1 + 1 + lVar4) + 2 + lVar4;
      puVar2 = puVar3;
    } while (puVar3 != param_4 + uVar6);
    return uVar1;
  }
  return uVar1;
}

