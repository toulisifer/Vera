
ulong fn_20(long param_1,ulong param_2,ulong param_3,long param_4,ulong param_5)

{
  byte bVar1;
  long lVar2;
  byte *pbVar3;
  byte *pbVar4;
  long lVar5;
  ulong uVar6;
  ulong uVar7;
  long in_FS_OFFSET;
  byte local_18 [8];
  long local_10;
  
  local_10 = *(long *)(in_FS_OFFSET + 0x28);
  uVar6 = 0xffffffffffffffff;
  if (param_2 <= param_5) {
    local_18[0] = 0;
    local_18[1] = 1;
    local_18[2] = 2;
    local_18[3] = 3;
    local_18[4] = 4;
    local_18[5] = 5;
    local_18[6] = 6;
    local_18[7] = 7;
    pbVar3 = local_18 + 7;
    do {
      pbVar4 = pbVar3 + -1;
      uVar6 = param_3 % (ulong)(pbVar3 + (1 - (long)local_18));
      bVar1 = *pbVar3;
      *pbVar3 = local_18[uVar6];
      local_18[uVar6] = bVar1;
      param_3 = param_3 / (ulong)(pbVar3 + (1 - (long)local_18));
      pbVar3 = pbVar4;
    } while (pbVar4 != local_18);
    if (param_2 < 8) {
      uVar7 = 0;
    }
    else {
      lVar5 = param_4;
      uVar6 = 8;
      do {
        uVar7 = uVar6;
        lVar2 = 0;
        do {
          *(undefined1 *)(lVar5 + lVar2) =
               *(undefined1 *)(param_1 + -8 + uVar7 + (ulong)local_18[lVar2]);
          lVar2 = lVar2 + 1;
        } while (lVar2 != 8);
        lVar5 = lVar5 + 8;
        uVar6 = uVar7 + 8;
      } while (uVar7 + 8 <= param_2);
    }
    uVar6 = param_2;
    if (uVar7 < param_2) {
      do {
        *(undefined1 *)(param_4 + uVar7) = *(undefined1 *)(param_1 + uVar7);
        uVar7 = uVar7 + 1;
      } while (param_2 != uVar7);
    }
  }
  if (local_10 != *(long *)(in_FS_OFFSET + 0x28)) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
  return uVar6;
}

