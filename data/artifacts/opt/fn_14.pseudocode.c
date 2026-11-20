
long fn_14(long param_1,ulong param_2,undefined8 param_3,long param_4,ulong param_5)

{
  byte bVar1;
  char cVar2;
  ulong uVar3;
  uint uVar4;
  ulong uVar5;
  uint uVar6;
  long lVar7;
  
  if (param_5 < (param_2 + 2) / 3 << 2) {
    return -1;
  }
  if (param_2 < 3) {
    uVar5 = 0;
    lVar7 = 0;
  }
  else {
    lVar7 = 0;
    uVar3 = 3;
    do {
      uVar5 = uVar3;
      bVar1 = *(byte *)(param_1 + -3 + uVar5);
      lVar7 = lVar7 + 4;
      uVar4 = (uint)bVar1 << 0x10 | (uint)*(byte *)(param_1 + -2 + uVar5) << 8;
      uVar6 = (uint)*(byte *)(param_1 + -1 + uVar5);
      *(uint *)(param_4 + -4 + lVar7) =
           CONCAT31(CONCAT21(CONCAT11("AfhmdLEr3GMxg2S/a91UZnTlHOI5KYzevFCwNQ+P4tWV7cpXRbDuykjJsoi6q80B"
                                      [uVar6 & 0x3f],
                                      "AfhmdLEr3GMxg2S/a91UZnTlHOI5KYzevFCwNQ+P4tWV7cpXRbDuykjJsoi6q80B"
                                      [(uVar6 | uVar4) >> 6 & 0x3f]),
                             "AfhmdLEr3GMxg2S/a91UZnTlHOI5KYzevFCwNQ+P4tWV7cpXRbDuykjJsoi6q80B"
                             [uVar4 >> 0xc & 0x3f]),
                    "AfhmdLEr3GMxg2S/a91UZnTlHOI5KYzevFCwNQ+P4tWV7cpXRbDuykjJsoi6q80B"[bVar1 >> 2]);
      uVar3 = uVar5 + 3;
    } while (uVar5 + 3 <= param_2);
    param_2 = param_2 - uVar5;
  }
  if (param_2 != 1) {
    if (param_2 != 2) {
      return lVar7;
    }
    uVar4 = (uint)*(byte *)(param_1 + 1 + uVar5) << 8;
    cVar2 = "AfhmdLEr3GMxg2S/a91UZnTlHOI5KYzevFCwNQ+P4tWV7cpXRbDuykjJsoi6q80B"[(uVar4 & 0xf00) >> 6]
    ;
    *(ushort *)(param_4 + lVar7) =
         CONCAT11("AfhmdLEr3GMxg2S/a91UZnTlHOI5KYzevFCwNQ+P4tWV7cpXRbDuykjJsoi6q80B"
                  [(uVar4 | (uint)*(byte *)(param_1 + uVar5) << 0x10) >> 0xc & 0x3f],
                  "AfhmdLEr3GMxg2S/a91UZnTlHOI5KYzevFCwNQ+P4tWV7cpXRbDuykjJsoi6q80B"
                  [*(byte *)(param_1 + uVar5) >> 2]);
    *(char *)(param_4 + 2 + lVar7) = cVar2;
    *(undefined1 *)(param_4 + lVar7 + 3) = 0x3d;
    return lVar7 + 4;
  }
  *(ushort *)(param_4 + lVar7) =
       CONCAT11("AfhmdLEr3GMxg2S/a91UZnTlHOI5KYzevFCwNQ+P4tWV7cpXRbDuykjJsoi6q80B"
                [(*(byte *)(param_1 + uVar5) & 3) << 4],
                "AfhmdLEr3GMxg2S/a91UZnTlHOI5KYzevFCwNQ+P4tWV7cpXRbDuykjJsoi6q80B"
                [*(byte *)(param_1 + uVar5) >> 2]);
  *(undefined2 *)(param_4 + 2 + lVar7) = 0x3d3d;
  return lVar7 + 4;
}

