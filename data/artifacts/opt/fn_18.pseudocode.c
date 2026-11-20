
long fn_18(long param_1,long param_2)

{
  long lVar1;
  long lVar2;
  long lVar3;
  byte bVar4;
  char cVar5;
  long in_FS_OFFSET;
  bool bVar6;
  undefined8 uStack_60;
  char local_58 [72];
  long local_10;
  
  local_10 = *(long *)(in_FS_OFFSET + 0x28);
  lVar2 = 0;
  if (param_2 == 0) {
LAB_001011a9:
    param_2 = 0;
  }
  else {
    bVar6 = false;
    lVar3 = 0;
    do {
      while (bVar4 = *(byte *)(param_1 + lVar2), !bVar6) {
        if (bVar4 == 0x29) goto LAB_001011d9;
        if (bVar4 < 0x2a) {
          if (bVar4 == 0x22) {
            lVar2 = lVar2 + 1;
            if (lVar2 != param_2) {
              bVar4 = *(byte *)(param_1 + lVar2);
              break;
            }
            goto LAB_00101250;
          }
          if (bVar4 != 0x28) goto LAB_001011e7;
          if (lVar3 == 0x40) goto LAB_00101259;
          cVar5 = ')';
LAB_00101210:
          local_58[lVar3] = cVar5;
          lVar3 = lVar3 + 1;
        }
        else {
          if (bVar4 == 0x7b) {
LAB_00101238:
            if (lVar3 != 0x40) {
              cVar5 = bVar4 + 2;
              goto LAB_00101210;
            }
LAB_00101259:
            param_2 = lVar2 + 1;
            goto LAB_001011ab;
          }
          if (bVar4 < 0x7c) {
            if (bVar4 == 0x5b) goto LAB_00101238;
            if (bVar4 == 0x5d) goto LAB_001011d9;
          }
          else if (bVar4 == 0x7d) {
LAB_001011d9:
            if ((lVar3 == 0) || (lVar1 = lVar3 + -1, lVar3 = lVar3 + -1, local_58[lVar1] != bVar4))
            goto LAB_00101259;
          }
        }
LAB_001011e7:
        lVar2 = lVar2 + 1;
        if (param_2 == lVar2) {
          if (lVar3 != 0) goto LAB_00101250;
          goto LAB_001011a0;
        }
      }
      if (bVar4 == 0x5c) {
        lVar2 = lVar2 + 1;
        if (param_2 != lVar2) {
          bVar6 = true;
          goto LAB_001011e7;
        }
        goto LAB_00101250;
      }
      bVar6 = bVar4 != 0x22;
      lVar2 = lVar2 + 1;
    } while (param_2 != lVar2);
    if (lVar3 == 0) {
LAB_001011a0:
      if (!bVar6) goto LAB_001011a9;
    }
LAB_00101250:
    param_2 = param_2 + 1;
  }
LAB_001011ab:
  if (local_10 != *(long *)(in_FS_OFFSET + 0x28)) {
                    /* WARNING: Subroutine does not return */
    uStack_60 = 0x101267;
    __stack_chk_fail();
  }
  return param_2;
}

