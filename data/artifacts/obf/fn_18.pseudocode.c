
long fn_18(long param_1,long param_2)

{
  byte bVar1;
  uint uVar2;
  uint uVar3;
  long lVar4;
  char cVar5;
  uint uVar6;
  ulong uVar7;
  ulong uVar8;
  ulong uVar9;
  long lVar10;
  ulong uVar11;
  long in_FS_OFFSET;
  undefined8 uStack_70;
  char local_68 [72];
  long local_20;
  
  local_20 = *(long *)(in_FS_OFFSET + 0x28);
  if (param_2 != 0) {
    uVar11 = 0;
    uVar6 = 0;
    lVar4 = 0;
    uVar8 = 0;
    lVar10 = param_2;
    do {
      bVar1 = *(byte *)(param_1 + lVar4);
      if ((((int)(lVar10 + 1) * (uint)lVar10 & 1) != 0) || (DAT_00104018 != 0)) {
        uVar6 = ((uint)(lVar10 << 7) ^ uVar6) * 0x2d6b + DAT_00104010;
        uVar6 = uVar6 >> 0xb ^ uVar6;
      }
      if (uVar6 == 2) {
LAB_00101221:
        uVar6 = 1;
      }
      else {
        uVar3 = (uint)lVar4;
        if (uVar6 == 1) {
          if (bVar1 == 0x5c) {
            uVar6 = 2;
          }
          else if ((bVar1 == 0x22) &&
                  ((((uVar3 | 1) * (uVar3 | 1) & 7) != 1 || (uVar6 = 0, DAT_00104010 != 0x3c71)))) {
            uVar6 = (uint)uVar11 ^ 0x51e4;
          }
        }
        else {
          if (bVar1 == 0x29) goto LAB_001012c4;
          if (bVar1 < 0x2a) {
            if (bVar1 == 0x22) {
              uVar3 = (int)uVar8 + uVar3;
              uVar2 = uVar3 | 1;
              if (((uVar2 * uVar2 & 7) == 1) && (DAT_00104010 == 0x3c71)) goto LAB_00101221;
              uVar6 = uVar6 + 0x51e3 ^ uVar3 * 0x1f9;
            }
            else if (bVar1 == 0x28) goto LAB_0010134a;
          }
          else if (bVar1 == 0x7b) {
LAB_0010134a:
            if (uVar8 == 0x40) {
LAB_00101439:
              lVar4 = lVar4 + 1;
              goto LAB_00101244;
            }
            if ((((uVar3 | 1) * (uVar3 | 1) & 7) == 1) && (DAT_00104010 == 0x3c71)) {
              cVar5 = bVar1 + 2;
              if (bVar1 == 0x28) {
                cVar5 = ')';
              }
              local_68[uVar8] = cVar5;
              uVar8 = uVar8 + 1;
            }
            else {
              uVar8 = uVar8 + 0x51e3 ^ uVar11;
            }
          }
          else if (bVar1 < 0x7c) {
            if (bVar1 == 0x5b) goto LAB_0010134a;
            if (bVar1 == 0x5d) goto LAB_001012c4;
          }
          else if (bVar1 == 0x7d) {
LAB_001012c4:
            if ((uVar8 == 0) || (uVar9 = uVar8 - 1, local_68[uVar8 - 1] != bVar1))
            goto LAB_00101439;
            uVar3 = (uint)lVar10 | 1;
            if (((uVar3 * uVar3 & 7) != 1) || (DAT_00104010 != 0x3c71)) {
              uVar9 = uVar8 + 0x51e3 ^ param_2 * 0x1f9 + uVar11;
            }
            uVar8 = uVar9;
            if (DAT_00104018 != 0) {
              uVar7 = 0;
              do {
                uVar9 = uVar9 >> 5 ^ uVar9 * 8 ^ uVar7;
                uVar7 = uVar7 + 1;
                uVar8 = uVar9;
              } while ((uint)uVar7 < DAT_00104018);
            }
          }
        }
      }
      if (param_2 == lVar4 + 1) goto LAB_00101231;
      lVar4 = lVar4 + 1;
      uVar11 = uVar11 + 0x1f9;
      lVar10 = lVar10 + 1;
    } while( true );
  }
LAB_00101242:
  lVar4 = 0;
LAB_00101244:
  if (local_20 == *(long *)(in_FS_OFFSET + 0x28)) {
    return lVar4;
  }
                    /* WARNING: Subroutine does not return */
  uStack_70 = 0x101447;
  __stack_chk_fail();
LAB_00101231:
  if ((uVar8 != 0) || (uVar6 != 0)) {
    lVar4 = lVar4 + 2;
    goto LAB_00101244;
  }
  goto LAB_00101242;
}

