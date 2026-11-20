
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

ulonglong fn_18(uchar *in,ulonglong len,ulonglong arg,uchar *out,ulonglong out_cap)

{
  byte bVar1;
  uint uVar2;
  uint uVar3;
  long lVar4;
  ulonglong uVar5;
  char cVar6;
  uint uVar7;
  ulong uVar8;
  ulong uVar9;
  ulong uVar10;
  ulong uVar11;
  long in_FS_OFFSET;
  undefined8 uStack_70;
  char local_68 [72];
  long local_20;
  
  local_20 = *(long *)(in_FS_OFFSET + 0x28);
  if (len != 0) {
    uVar11 = 0;
    uVar7 = 0;
    lVar4 = 0;
    uVar9 = 0;
    uVar5 = len;
    do {
      bVar1 = in[lVar4];
      if ((((int)(uVar5 + 1) * (uint)uVar5 & 1) != 0) || (DAT_00104018 != 0)) {
        uVar7 = ((uint)(uVar5 << 7) ^ uVar7) * 0x2d6b + DAT_00104010;
        uVar7 = uVar7 >> 0xb ^ uVar7;
      }
      if (uVar7 == 2) {
LAB_00101221:
        uVar7 = 1;
      }
      else {
        uVar3 = (uint)lVar4;
        if (uVar7 == 1) {
          if (bVar1 == 0x5c) {
            uVar7 = 2;
          }
          else if ((bVar1 == 0x22) &&
                  ((((uVar3 | 1) * (uVar3 | 1) & 7) != 1 || (uVar7 = 0, DAT_00104010 != 0x3c71)))) {
            uVar7 = (uint)uVar11 ^ 0x51e4;
          }
        }
        else {
          if (bVar1 == 0x29) goto LAB_001012c4;
          if (bVar1 < 0x2a) {
            if (bVar1 == 0x22) {
              uVar3 = (int)uVar9 + uVar3;
              uVar2 = uVar3 | 1;
              if (((uVar2 * uVar2 & 7) == 1) && (DAT_00104010 == 0x3c71)) goto LAB_00101221;
              uVar7 = uVar7 + 0x51e3 ^ uVar3 * 0x1f9;
            }
            else if (bVar1 == 0x28) goto LAB_0010134a;
          }
          else if (bVar1 == 0x7b) {
LAB_0010134a:
            if (uVar9 == 0x40) {
LAB_00101439:
              uVar5 = lVar4 + 1;
              goto LAB_00101244;
            }
            if ((((uVar3 | 1) * (uVar3 | 1) & 7) == 1) && (DAT_00104010 == 0x3c71)) {
              cVar6 = bVar1 + 2;
              if (bVar1 == 0x28) {
                cVar6 = ')';
              }
              local_68[uVar9] = cVar6;
              uVar9 = uVar9 + 1;
            }
            else {
              uVar9 = uVar9 + 0x51e3 ^ uVar11;
            }
          }
          else if (bVar1 < 0x7c) {
            if (bVar1 == 0x5b) goto LAB_0010134a;
            if (bVar1 == 0x5d) goto LAB_001012c4;
          }
          else if (bVar1 == 0x7d) {
LAB_001012c4:
            if ((uVar9 == 0) || (uVar10 = uVar9 - 1, local_68[uVar9 - 1] != bVar1))
            goto LAB_00101439;
            uVar3 = (uint)uVar5 | 1;
            if (((uVar3 * uVar3 & 7) != 1) || (DAT_00104010 != 0x3c71)) {
              uVar10 = uVar9 + 0x51e3 ^ len * 0x1f9 + uVar11;
            }
            uVar9 = uVar10;
            if (DAT_00104018 != 0) {
              uVar8 = 0;
              do {
                uVar10 = uVar10 >> 5 ^ uVar10 * 8 ^ uVar8;
                uVar8 = uVar8 + 1;
                uVar9 = uVar10;
              } while ((uint)uVar8 < DAT_00104018);
            }
          }
        }
      }
      if (len == lVar4 + 1U) goto LAB_00101231;
      lVar4 = lVar4 + 1;
      uVar11 = uVar11 + 0x1f9;
      uVar5 = uVar5 + 1;
    } while( true );
  }
LAB_00101242:
  uVar5 = 0;
LAB_00101244:
  if (local_20 == *(long *)(in_FS_OFFSET + 0x28)) {
    return uVar5;
  }
                    /* WARNING: Subroutine does not return */
  uStack_70 = 0x101447;
  __stack_chk_fail();
LAB_00101231:
  if ((uVar9 != 0) || (uVar7 != 0)) {
    uVar5 = lVar4 + 2;
    goto LAB_00101244;
  }
  goto LAB_00101242;
}

