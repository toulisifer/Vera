
uint fn_16(long param_1,long param_2,undefined8 param_3)

{
  byte *pbVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  long lVar5;
  long lVar6;
  long lVar7;
  uint uVar8;
  
  uVar4 = (uint)((ulong)param_3 >> 0x20) ^ (uint)param_3;
  if (param_2 != 0) {
    uVar8 = 0;
    lVar5 = 0;
    lVar6 = param_2;
    do {
      while( true ) {
        lVar7 = lVar6 + 1;
        if ((((int)lVar7 * (int)lVar6 & 1U) != 0) || (DAT_00104010 != 0)) {
          uVar4 = DAT_00104008 + (uVar4 ^ (uint)(lVar6 << 7)) * 0x2d6b;
          uVar4 = uVar4 >> 0xb ^ uVar4;
        }
        uVar4 = uVar4 << 7 | uVar4 >> 0x19;
        uVar3 = (uint)lVar5;
        uVar2 = uVar3 | 1;
        lVar6 = lVar7;
        if (((uVar2 * uVar2 & 7) != 1) || (DAT_00104008 != 0x3c71)) break;
        pbVar1 = (byte *)(param_1 + lVar5);
        uVar8 = uVar8 + 0x1f9;
        lVar5 = lVar5 + 1;
        uVar4 = uVar4 + (uint)*pbVar1 * 0x9d + uVar3;
        if (param_2 == lVar5) goto LAB_001011c0;
      }
      lVar5 = lVar5 + 1;
      uVar4 = uVar4 + 0x51e3 ^ uVar8;
      uVar8 = uVar8 + 0x1f9;
    } while (param_2 != lVar5);
  }
LAB_001011c0:
  if (DAT_00104010 != 0) {
    uVar8 = 0;
    do {
      uVar4 = uVar4 >> 5 ^ uVar4 * 8 ^ uVar8;
      uVar8 = uVar8 + 1;
    } while (uVar8 < DAT_00104010);
  }
  uVar4 = (uVar4 >> 0xf ^ uVar4) * 0x3b9d;
  return uVar4 >> 0xd ^ uVar4;
}

