
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

ulonglong fn_14(uchar *in,ulonglong len,ulonglong arg,uchar *out,ulonglong out_cap)

{
  byte bVar1;
  uint uVar2;
  uint uVar3;
  ulong uVar4;
  ulonglong uVar5;
  ulong uVar6;
  ulong uVar7;
  ulonglong uVar8;
  
  uVar5 = 0xffffffffffffffff;
  if ((len + 2) / 3 << 2 <= out_cap) {
    if (len < 3) {
      uVar7 = 0;
      uVar5 = 0;
    }
    else {
      uVar6 = 0;
      uVar5 = 0;
      uVar4 = 3;
      uVar8 = len;
      do {
        uVar7 = uVar4;
        uVar3 = (uint)in[uVar7 - 3] << 0x10 | (uint)in[uVar7 - 2] << 8 | (uint)in[uVar7 - 1];
        if (((((int)uVar8 + 1) * (int)uVar8 & 1U) != 0) || (DAT_00104010 != 0)) {
          uVar3 = ((uint)(uVar8 << 7) ^ uVar3) * 0x2d6b + DAT_00104008;
          uVar3 = uVar3 >> 0xb ^ uVar3;
        }
        uVar2 = (int)uVar7 - 3U | 1;
        *(ushort *)(out + uVar5) =
             CONCAT11("AfhmdLEr3GMxg2S/a91UZnTlHOI5KYzevFCwNQ+P4tWV7cpXRbDuykjJsoi6q80B"
                      [uVar3 >> 0xc & 0x3f],
                      "AfhmdLEr3GMxg2S/a91UZnTlHOI5KYzevFCwNQ+P4tWV7cpXRbDuykjJsoi6q80B"
                      [uVar3 >> 0x12 & 0x3f]);
        if (((uVar2 * uVar2 & 7) == 1) && (DAT_00104008 == 0x3c71)) {
          uVar4 = uVar5 + 3;
          out[uVar5 + 2] =
               "AfhmdLEr3GMxg2S/a91UZnTlHOI5KYzevFCwNQ+P4tWV7cpXRbDuykjJsoi6q80B"[uVar3 >> 6 & 0x3f]
          ;
        }
        else {
          uVar4 = uVar5 + 0x51e5 ^ uVar6;
        }
        uVar5 = uVar4 + 1;
        uVar8 = uVar8 + 3;
        uVar6 = uVar6 + 0x5eb;
        out[uVar4] = "AfhmdLEr3GMxg2S/a91UZnTlHOI5KYzevFCwNQ+P4tWV7cpXRbDuykjJsoi6q80B"
                     [uVar3 & 0x3f];
        uVar4 = uVar7 + 3;
      } while (uVar7 + 3 <= len);
      len = len - uVar7;
    }
    if (len == 1) {
      *(ushort *)(out + uVar5) =
           CONCAT11("AfhmdLEr3GMxg2S/a91UZnTlHOI5KYzevFCwNQ+P4tWV7cpXRbDuykjJsoi6q80B"
                    [(in[uVar7] & 3) << 4],
                    "AfhmdLEr3GMxg2S/a91UZnTlHOI5KYzevFCwNQ+P4tWV7cpXRbDuykjJsoi6q80B"
                    [in[uVar7] >> 2]);
      (out + uVar5 + 2)[0] = '=';
      (out + uVar5 + 2)[1] = '=';
      return uVar5 + 4;
    }
    if (len == 2) {
      bVar1 = in[uVar7 + 1];
      *(ushort *)(out + uVar5) =
           CONCAT11("AfhmdLEr3GMxg2S/a91UZnTlHOI5KYzevFCwNQ+P4tWV7cpXRbDuykjJsoi6q80B"
                    [((uint)bVar1 << 8 | (uint)in[uVar7] << 0x10) >> 0xc & 0x3f],
                    "AfhmdLEr3GMxg2S/a91UZnTlHOI5KYzevFCwNQ+P4tWV7cpXRbDuykjJsoi6q80B"
                    [in[uVar7] >> 2]);
      out[uVar5 + 2] =
           "AfhmdLEr3GMxg2S/a91UZnTlHOI5KYzevFCwNQ+P4tWV7cpXRbDuykjJsoi6q80B"
           [((uint)bVar1 << 8 & 0xf00) >> 6];
      out[uVar5 + 3] = '=';
      return uVar5 + 4;
    }
  }
  return uVar5;
}

