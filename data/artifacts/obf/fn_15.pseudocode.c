
ulong fn_15(long param_1,ulong param_2,undefined8 param_3,long param_4,ulong param_5)

{
  char *pcVar1;
  char cVar2;
  uint uVar3;
  long lVar4;
  ulong uVar5;
  ulong uVar6;
  ulong uVar7;
  ulong uVar8;
  bool bVar9;
  
  if (param_2 == 0) {
    return 0;
  }
  uVar5 = 0;
  uVar8 = 0;
  do {
    uVar7 = uVar8 + 1;
    if (uVar7 < param_2) {
      lVar4 = 2;
      cVar2 = *(char *)(param_1 + uVar8);
      if (*(char *)(param_1 + 1 + uVar8) == cVar2) {
        do {
          uVar7 = lVar4 + uVar8;
          if (param_2 - uVar8 == lVar4) break;
          pcVar1 = (char *)(param_1 + uVar8) + lVar4;
          bVar9 = lVar4 != 0xff;
          lVar4 = lVar4 + 1;
        } while (*pcVar1 == cVar2 && bVar9);
      }
    }
    if ((((uVar7 + 1) * uVar7 & 1) != 0) || (DAT_00104010 != 0)) {
      uVar5 = (ulong)DAT_00104008 + (uVar7 << 7 ^ uVar5) * 0x2d6b;
      uVar5 = uVar5 >> 0xb ^ uVar5;
    }
    uVar5 = uVar5 + 2;
    uVar8 = uVar7;
  } while (uVar7 < param_2);
  if (param_5 < uVar5) {
    return 0xffffffffffffffff;
  }
  uVar5 = 0;
  uVar8 = 1;
  uVar7 = 0;
  if (param_2 < 2) goto LAB_00101250;
  do {
    uVar6 = uVar8;
    lVar4 = 1;
    do {
      if (*(char *)(param_1 + uVar6) != *(char *)(param_1 + uVar7)) break;
      if (lVar4 == 0xff) {
        lVar4 = 0xffffffff;
        break;
      }
      uVar6 = uVar6 + 1;
      lVar4 = lVar4 + 1;
    } while (uVar6 < param_2);
    while( true ) {
      *(char *)(param_4 + uVar5) = (char)lVar4;
      uVar3 = (uint)uVar6 | 1;
      if (((uVar3 * uVar3 & 7) == 1) && (DAT_00104008 == 0x3c71)) {
        *(undefined1 *)(param_4 + 1 + uVar5) = *(undefined1 *)(param_1 + uVar7);
        uVar5 = uVar5 + 2;
      }
      else {
        uVar5 = uVar5 + 0x51e4 ^ uVar6 * 0x1f9;
      }
      if (param_2 <= uVar6) {
        return uVar5;
      }
      uVar8 = uVar6 + 1;
      uVar7 = uVar6;
      if (uVar8 < param_2) break;
LAB_00101250:
      uVar6 = uVar8;
      lVar4 = 1;
    }
  } while( true );
}

