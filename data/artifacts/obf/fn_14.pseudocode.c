
long fn_14(long param_1,ulong param_2,undefined8 param_3,long param_4,ulong param_5)

{
  uint uVar1;
  uint uVar2;
  ulong uVar3;
  long lVar4;
  ulong uVar5;
  ulong uVar6;
  ulong uVar7;
  
  lVar4 = -1;
  if ((param_2 + 2) / 3 << 2 <= param_5) {
    if (param_2 < 3) {
      uVar6 = 0;
      lVar4 = 0;
    }
    else {
      uVar5 = 0;
      lVar4 = 0;
      uVar3 = 3;
      uVar7 = param_2;
      do {
        uVar6 = uVar3;
        uVar2 = (uint)*(byte *)(param_1 + -3 + uVar6) << 0x10 |
                (uint)*(byte *)(param_1 + -2 + uVar6) << 8 | (uint)*(byte *)(param_1 + -1 + uVar6);
        if (((((int)uVar7 + 1) * (int)uVar7 & 1U) != 0) || (DAT_00104010 != 0)) {
          uVar2 = ((uint)(uVar7 << 7) ^ uVar2) * 0x2d6b + DAT_00104008;
          uVar2 = uVar2 >> 0xb ^ uVar2;
        }
        uVar1 = (int)uVar6 - 3U | 1;
        *(ushort *)(param_4 + lVar4) =
             CONCAT11("AfhmdLEr3GMxg2S/a91UZnTlHOI5KYzevFCwNQ+P4tWV7cpXRbDuykjJsoi6q80B"
                      [uVar2 >> 0xc & 0x3f],
                      "AfhmdLEr3GMxg2S/a91UZnTlHOI5KYzevFCwNQ+P4tWV7cpXRbDuykjJsoi6q80B"
                      [uVar2 >> 0x12 & 0x3f]);
        if (((uVar1 * uVar1 & 7) == 1) && (DAT_00104008 == 0x3c71)) {
          uVar3 = lVar4 + 3;
          *(char *)(param_4 + 2 + lVar4) =
               "AfhmdLEr3GMxg2S/a91UZnTlHOI5KYzevFCwNQ+P4tWV7cpXRbDuykjJsoi6q80B"[uVar2 >> 6 & 0x3f]
          ;
        }
        else {
          uVar3 = lVar4 + 0x51e5U ^ uVar5;
        }
        lVar4 = uVar3 + 1;
        uVar7 = uVar7 + 3;
        uVar5 = uVar5 + 0x5eb;
        *(char *)(param_4 + uVar3) =
             "AfhmdLEr3GMxg2S/a91UZnTlHOI5KYzevFCwNQ+P4tWV7cpXRbDuykjJsoi6q80B"[uVar2 & 0x3f];
        uVar3 = uVar6 + 3;
      } while (uVar6 + 3 <= param_2);
      param_2 = param_2 - uVar6;
    }
    if (param_2 == 1) {
      *(ushort *)(param_4 + lVar4) =
           CONCAT11("AfhmdLEr3GMxg2S/a91UZnTlHOI5KYzevFCwNQ+P4tWV7cpXRbDuykjJsoi6q80B"
                    [(*(byte *)(param_1 + uVar6) & 3) << 4],
                    "AfhmdLEr3GMxg2S/a91UZnTlHOI5KYzevFCwNQ+P4tWV7cpXRbDuykjJsoi6q80B"
                    [*(byte *)(param_1 + uVar6) >> 2]);
      *(undefined2 *)(param_4 + 2 + lVar4) = 0x3d3d;
      return lVar4 + 4;
    }
    if (param_2 == 2) {
      uVar2 = (uint)*(byte *)(param_1 + 1 + uVar6) << 8;
      *(ushort *)(param_4 + lVar4) =
           CONCAT11("AfhmdLEr3GMxg2S/a91UZnTlHOI5KYzevFCwNQ+P4tWV7cpXRbDuykjJsoi6q80B"
                    [(uVar2 | (uint)*(byte *)(param_1 + uVar6) << 0x10) >> 0xc & 0x3f],
                    "AfhmdLEr3GMxg2S/a91UZnTlHOI5KYzevFCwNQ+P4tWV7cpXRbDuykjJsoi6q80B"
                    [*(byte *)(param_1 + uVar6) >> 2]);
      *(char *)(param_4 + 2 + lVar4) =
           "AfhmdLEr3GMxg2S/a91UZnTlHOI5KYzevFCwNQ+P4tWV7cpXRbDuykjJsoi6q80B"[(uVar2 & 0xf00) >> 6];
      *(undefined1 *)(param_4 + lVar4 + 3) = 0x3d;
      return lVar4 + 4;
    }
  }
  return lVar4;
}

