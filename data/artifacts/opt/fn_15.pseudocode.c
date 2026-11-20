
long fn_15(long param_1,ulong param_2,undefined8 param_3,long param_4,ulong param_5)

{
  char *pcVar1;
  char cVar2;
  ulong uVar3;
  long lVar4;
  long lVar5;
  long lVar6;
  ulong uVar7;
  
  lVar5 = 0;
  lVar4 = 0;
  uVar7 = 0;
  if (param_2 != 0) {
    while (lVar6 = lVar4, uVar7 + 1 < param_2) {
      cVar2 = *(char *)(param_1 + uVar7);
      lVar4 = 2;
      if (*(char *)(param_1 + 1 + uVar7) == cVar2) {
        do {
          lVar5 = lVar4;
          if (lVar5 == param_2 - uVar7) goto LAB_00101171;
        } while ((((char *)(param_1 + uVar7))[lVar5] == cVar2) && (lVar4 = lVar5 + 1, lVar5 != 0xff)
                );
        uVar7 = uVar7 + lVar5;
        lVar4 = lVar6 + 2;
        if (param_2 <= uVar7) break;
      }
      else {
        lVar4 = lVar6 + 2;
        uVar7 = uVar7 + 1;
      }
    }
LAB_00101171:
    lVar5 = -1;
    if (lVar6 + 2U <= param_5) {
      lVar5 = 0;
      uVar7 = 0;
      do {
        uVar3 = uVar7 + 1;
        pcVar1 = (char *)(param_1 + uVar7);
        if (param_2 <= uVar3) {
          lVar4 = 1;
LAB_00101204:
          *(char *)(param_4 + lVar5) = (char)lVar4;
          *(char *)(param_4 + lVar5 + 1) = *pcVar1;
          return lVar5 + 2;
        }
        lVar4 = 1;
        while (*(char *)(param_1 + uVar3) == *pcVar1) {
          if (lVar4 == 0xff) {
            lVar4 = 0xffffffff;
            break;
          }
          uVar3 = uVar3 + 1;
          lVar4 = lVar4 + 1;
          if (param_2 <= uVar3) goto LAB_00101204;
        }
        *(char *)(param_4 + lVar5) = (char)lVar4;
        lVar5 = lVar5 + 2;
        *(char *)(param_4 + -1 + lVar5) = *pcVar1;
        uVar7 = uVar3;
      } while (uVar3 < param_2);
    }
  }
  return lVar5;
}

