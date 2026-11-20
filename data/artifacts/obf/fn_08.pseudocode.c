
uint fn_08(long param_1,long param_2)

{
  uint uVar1;
  uint uVar2;
  long lVar3;
  uint uVar4;
  uint uVar5;
  long lVar6;
  long lVar7;
  uint uVar8;
  
  if (DAT_00104010 == 0) {
    uVar2 = 0xffffffff;
  }
  else {
    uVar4 = 0;
    uVar2 = 0xffffffff;
    do {
      uVar2 = uVar2 >> 5 ^ uVar2 * 8 ^ uVar4;
      uVar4 = uVar4 + 1;
    } while (uVar4 < DAT_00104010);
  }
  if (param_2 == 0) {
    return ~uVar2;
  }
  uVar4 = (int)param_2 * 0x1f9;
  uVar8 = 0;
  lVar6 = 0;
  do {
    uVar2 = uVar2 ^ *(byte *)(param_1 + lVar6);
    lVar7 = lVar6 + 1;
    lVar3 = param_2;
    uVar5 = uVar4;
    if ((((int)lVar6 * (int)lVar7 & 1U) != 0) || (DAT_00104010 != 0)) {
      uVar2 = (uVar2 ^ uVar8) * 0x2d6b + DAT_00104008;
      uVar2 = uVar2 ^ uVar2 >> 0xb;
    }
    do {
      while ((uVar1 = (uint)lVar3 | 1, (uVar1 * uVar1 & 7) == 1 && (DAT_00104008 == 0x3c71))) {
        lVar3 = lVar3 + 1;
        uVar2 = -(uVar2 & 1) & 0xf7179bf5 ^ uVar2 >> 1;
        uVar5 = uVar5 + 0x1f9;
        if (param_2 + 8 == lVar3) goto LAB_00101200;
      }
      lVar3 = lVar3 + 1;
      uVar2 = uVar2 + 0x51e3 ^ uVar5;
      uVar5 = uVar5 + 0x1f9;
    } while (param_2 + 8 != lVar3);
LAB_00101200:
    uVar8 = uVar8 + 0x80;
    lVar6 = lVar7;
    if (lVar7 == param_2) {
      return ~uVar2;
    }
  } while( true );
}

