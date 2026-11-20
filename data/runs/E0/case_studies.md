# Ứng viên case study — E0

## A. Gán nhầm thuật toán (V1b bác bỏ claim ALG)

### opt/fn_08 — near-miss của CRC-32 (near_miss)

- Model: algorithm = `Implements CRC-16/XMODEM.`, tên đề xuất = `fn_08`
- V1: compiled = True, FEPR = 1.0
- `contradicted` (V1b) [ALG] “The function implements Implements CRC-16/XMODEM..” → {"vector": "v00", "tag": "len0", "expected_ret": "0x0000000000000000", "oracle_ret": "0x000000000000ffff"}

<details><summary>Pseudocode model đã đọc</summary>

```c
uint fn_08(byte *param_1,long param_2)

{
  uint uVar1;
  int iVar2;
  byte *pbVar3;
  
  if (param_2 != 0) {
    pbVar3 = param_1 + param_2;
    uVar1 = 0xffffffff;
    do {
      uVar1 = uVar1 ^ *param_1;
      iVar2 = 8;
      do {
        uVar1 = -(uVar1 & 1) & 0xf7179bf5 ^ uVar1 >> 1;
        iVar2 = iVar2 + -1;
      } while (iVar2 != 0);
      param_1 = param_1 + 1;
    } while (param_1 != pbVar3);
    return ~uVar1;
  }
  return 0;
}
```
</details>

<details><summary>Mã nguồn gốc</summary>

```c
#include "vera.h"

VERA_FN(fn_08)
{
    uint32_t h = 0xFFFFFFFFu;
    (void)arg; (void)out; (void)out_cap;
    OBF_SPIN(h);
    for (size_t i = 0; i < len; i++) {
        h ^= in[i];
        OBF_JUNK(h, i);
        for (unsigned b = 0; b < 8; b++)
            OBF_GUARD(h, len + b, h = (h >> 1) ^ (0xF7179BF5u & (0u - (h & 1u))));
    }
    return (uint64_t)(h ^ 0xFFFFFFFFu);
}
```
</details>

<details><summary>recovered_c của model</summary>

```c
uint64_t fn_08(const uint8_t *in, size_t len, uint64_t arg, uint8_t *out, size_t out_cap) {
  if (len != 0) {
    uint32_t crc = 0xFFFFFFFF;
    for (size_t i = 0; i < len; i++) {
      crc ^= in[i];
      for (int j = 0; j < 8; j++) {
        crc = -(crc & 1) & 0xf7179bf5 ^ crc >> 1;
      }
    }
    return ~crc;
  }
  return 0;
}
```
</details>

### plain/fn_14 — near-miss của Base64 encode (near_miss)

- Model: algorithm = `Base64 encoding`, tên đề xuất = `fn_14`
- V1: compiled = False, FEPR = 0.0
- `contradicted` (V1b) [ALG] “The function implements Base64 encoding.” → {"vector": "v01", "tag": "len1", "expected_ret": "0x0000000000000004", "oracle_ret": "0x0000000000000004"}

<details><summary>Pseudocode model đã đọc</summary>

```c
uint64_t fn_14(uint8_t *in,size_t len,uint64_t arg,uint8_t *out,size_t out_cap)

{
  long lVar1;
  byte bVar2;
  byte bVar3;
  uint uVar4;
  size_t out_cap_local;
  uint8_t *out_local;
  uint64_t arg_local;
  size_t len_local;
  uint8_t *in_local;
  uint32_t w;
  size_t o;
  size_t i;
  size_t need;
  
  o = 0;
  i = 0;
  if (out_cap < (len + 2) / 3 << 2) {
    o = 0xffffffffffffffff;
  }
  else {
    for (; i + 3 <= len; i = i + 3) {
      uVar4 = (uint)in[i] << 0x10 | (uint)in[i + 1] << 8;
      bVar2 = in[i + 2];
      out[o] = "AfhmdLEr3GMxg2S/a91UZnTlHOI5KYzevFCwNQ+P4tWV7cpXRbDuykjJsoi6q80B"[in[i] >> 2];
      out[o + 1] = "AfhmdLEr3GMxg2S/a91UZnTlHOI5KYzevFCwNQ+P4tWV7cpXRbDuykjJsoi6q80B"
                   [(uVar4 & 0x3f000) >> 0xc];
      lVar1 = o + 3;
...
```
</details>

<details><summary>Mã nguồn gốc</summary>

```c
#include "vera.h"

VERA_FN(fn_14)
{
    static const char tb[] = "AfhmdLEr3GMxg2S/a91UZnTlHOI5KYzevFCwNQ+P4tWV7cpXRbDuykjJsoi6q80B";
    size_t need = 4 * ((len + 2) / 3), o = 0, i = 0;
    uint32_t w;
    (void)arg;
    if (out_cap < need)
        return VERA_ERR;
    for (; i + 3 <= len; i += 3) {
        w = ((uint32_t)in[i] << 16) | ((uint32_t)in[i + 1] << 8) | in[i + 2];
        OBF_JUNK(w, i + len);
        out[o++] = (uint8_t)tb[(w >> 18) & 63];
        out[o++] = (uint8_t)tb[(w >> 12) & 63];
        OBF_GUARD(o, i, out[o++] = (uint8_t)tb[(w >> 6) & 63]);
        out[o++] = (uint8_t)tb[w & 63];
    }
    if (len - i == 1) {
        w = (uint32_t)in[i] << 16;
        out[o++] = (uint8_t)tb[(w >> 18) & 63];
        out[o++] = (uint8_t)tb[(w >> 12) & 63];
        out[o++] = '=';
        out[o++] = '=';
    } else if (len - i == 2) {
        w = ((uint32_t)in[i] << 16) | ((uint32_t)in[i + 1] << 8);
        out[o++] = (uint8_t)tb[(w >> 18) & 63];
        out[o++] = (uint8_t)tb[(w >> 12) & 63];
        out[o++] = (uint8_t)tb[(w >> 6) & 63];
        out[o++] = '=';
...
```
</details>

<details><summary>recovered_c của model</summary>

```c
uint64_t fn_14(const uint8_t *in, size_t len, uint64_t arg, uint8_t *out, size_t out_cap) {
  if (out_cap < (len + 2) / 3 << 2) {
    return 0xffffffffffffffff;
  }

  size_t len_encoded = 0;
  for (size_t i = 0; i + 3 <= len; i += 3) {
    uint32_t w = (uint)in[i] << 16 | (uint)in[i + 1] << 8 | (uint)in[i + 2];
    out[len_encoded++] = "AfhmdLEr3GMxg2S/a91UZnTlHOI5KYzevFCwNQ+P4tWV7cpXRbDuykjJsoi6q80B"[in[i] >> 2];
    out[len_encoded++] = "AfhmdLEr3GMxg2S/a91UZnTlHOI5KYzevFCwNQ+P4tWV7cpXRbDuykjJsoi6q80B"[(w & 0x3f000) >> 12];
    out[len_encoded++] = "AfhmdLEr3GMxg2S/a91UZnTlHOI5KYzevFCwNQ+P4tWV7cpXRbDuykjJsoi6q80B"[(w & 0xfc0) >> 6];
    out[len_encoded++] = "AfhmdLEr3GMxg2S/a91UZnTlHOI5KYzevFCwNQ+P4tWV7cpXRbDuykjJsoi6q80B"[w & 0x3f];
  }

  if (len - i == 1) {
    out[len_encoded++] = "AfhmdLEr3GMxg2S/a91UZnTlHOI5KYzevFCwNQ+P4tWV7cpXRbDuykjJsoi6q80B"[in[i] >> 2];
    out[len_encoded++] = "AfhmdLEr3GMxg2S/a91UZnTlHOI5KYzevFCwNQ+P4tWV7cpXRbDuykjJsoi6q80B"[(in[i] & 3) << 4];
    out[len_encoded++] = '=';
    out[len_encoded++] = '=';
  } else if (len - i == 2) {
    uint32_t w = (uint)in[i] << 16 | (uint)in[i + 1] << 8;
    out[len_encoded++] = "AfhmdLEr3GMxg2S/a91UZnTlHOI5KYzevFCwNQ+P4tWV7cpXRbDuykjJsoi6q80B"[in[i] >> 2];
    out[len_encoded++] = "AfhmdLEr3GMxg2S/a91UZnTlHOI5KYzevFCwNQ+P4tWV7cpXRbDuykjJsoi6q80B"[(w & 0x3f000) >> 12];
    out[len_encoded++] = "AfhmdLEr3GMxg2S/a91UZnTlHOI5KYzevFCwNQ+P4tWV7cpXRbDuykjJsoi6q80B"[(w & 0xfc0) >> 6];
    out[len_encoded++] = '=';
  }

  return len_encoded;
}
```
</details>

## B. Giải thích có claim sai nhưng mã khôi phục đúng (E2)

### opt/fn_08 — near-miss của CRC-32 (near_miss)

- Model: algorithm = `Implements CRC-16/XMODEM.`, tên đề xuất = `fn_08`
- V1: compiled = True, FEPR = 1.0
- `verified` (IO) [IO] “Returns 0 when len == 0.” → "đúng trên 1 vector thỏa điều kiện"
- `verified` (SIDE) [SIDE] “Does not write to out.” → "không vector nào ghi out"
- `contradicted` (V1b) [ALG] “The function implements Implements CRC-16/XMODEM..” → {"vector": "v00", "tag": "len0", "expected_ret": "0x0000000000000000", "oracle_ret": "0x000000000000ffff"}

<details><summary>Pseudocode model đã đọc</summary>

```c
uint fn_08(byte *param_1,long param_2)

{
  uint uVar1;
  int iVar2;
  byte *pbVar3;
  
  if (param_2 != 0) {
    pbVar3 = param_1 + param_2;
    uVar1 = 0xffffffff;
    do {
      uVar1 = uVar1 ^ *param_1;
      iVar2 = 8;
      do {
        uVar1 = -(uVar1 & 1) & 0xf7179bf5 ^ uVar1 >> 1;
        iVar2 = iVar2 + -1;
      } while (iVar2 != 0);
      param_1 = param_1 + 1;
    } while (param_1 != pbVar3);
    return ~uVar1;
  }
  return 0;
}
```
</details>

<details><summary>Mã nguồn gốc</summary>

```c
#include "vera.h"

VERA_FN(fn_08)
{
    uint32_t h = 0xFFFFFFFFu;
    (void)arg; (void)out; (void)out_cap;
    OBF_SPIN(h);
    for (size_t i = 0; i < len; i++) {
        h ^= in[i];
        OBF_JUNK(h, i);
        for (unsigned b = 0; b < 8; b++)
            OBF_GUARD(h, len + b, h = (h >> 1) ^ (0xF7179BF5u & (0u - (h & 1u))));
    }
    return (uint64_t)(h ^ 0xFFFFFFFFu);
}
```
</details>

<details><summary>recovered_c của model</summary>

```c
uint64_t fn_08(const uint8_t *in, size_t len, uint64_t arg, uint8_t *out, size_t out_cap) {
  if (len != 0) {
    uint32_t crc = 0xFFFFFFFF;
    for (size_t i = 0; i < len; i++) {
      crc ^= in[i];
      for (int j = 0; j < 8; j++) {
        crc = -(crc & 1) & 0xf7179bf5 ^ crc >> 1;
      }
    }
    return ~crc;
  }
  return 0;
}
```
</details>

### plain/fn_08 — near-miss của CRC-32 (near_miss)

- Model: algorithm = `unknown`, tên đề xuất = `fn_08`
- V1: compiled = True, FEPR = 1.0
- `verified` (SIDE) [SIDE] “Does not write to out.” → "không vector nào ghi out"
- `contradicted` (IO) [IO] “Returns 0xFFFFFFFFFFFFFFFF when len == 0.” → {"vector": "v00", "tag": "len0", "observed": "ret 0x0000000000000000"}

<details><summary>Pseudocode model đã đọc</summary>

```c
uint64_t fn_08(uint8_t *in,size_t len,uint64_t arg,uint8_t *out,size_t out_cap)

{
  size_t out_cap_local;
  uint8_t *out_local;
  uint64_t arg_local;
  size_t len_local;
  uint8_t *in_local;
  uint32_t h;
  uint b;
  size_t i;
  
  h = 0xffffffff;
  for (i = 0; i < len; i = i + 1) {
    h = h ^ in[i];
    for (b = 0; b < 8; b = b + 1) {
      h = -(h & 1) & 0xf7179bf5 ^ h >> 1;
    }
  }
  return (ulong)~h;
}
```
</details>

<details><summary>Mã nguồn gốc</summary>

```c
#include "vera.h"

VERA_FN(fn_08)
{
    uint32_t h = 0xFFFFFFFFu;
    (void)arg; (void)out; (void)out_cap;
    OBF_SPIN(h);
    for (size_t i = 0; i < len; i++) {
        h ^= in[i];
        OBF_JUNK(h, i);
        for (unsigned b = 0; b < 8; b++)
            OBF_GUARD(h, len + b, h = (h >> 1) ^ (0xF7179BF5u & (0u - (h & 1u))));
    }
    return (uint64_t)(h ^ 0xFFFFFFFFu);
}
```
</details>

<details><summary>recovered_c của model</summary>

```c
uint64_t fn_08(const uint8_t *in, size_t len, uint64_t arg, uint8_t *out, size_t out_cap) {
  uint32_t h = 0xffffffff;
  for (size_t i = 0; i < len; i++) {
    h = h ^ in[i];
    for (uint b = 0; b < 8; b++) {
      h = -(h & 1) & 0xf7179bf5 ^ h >> 1;
    }
  }
  return (uint64_t)~h;
}
```
</details>

## C. Giải thích sạch nhưng mã khôi phục sai (E2)

### obf/fn_05 — TEA (classic)

- Model: algorithm = `unknown`, tên đề xuất = `fn_05`
- V1: compiled = False, FEPR = 0.0
- `verified` (SIDE) [SIDE] “Writes the hash value to out[0..7].” → "hàm có ghi out trên vector hợp lệ"

<details><summary>Pseudocode model đã đọc</summary>

```c
undefined8 fn_05(uint *param_1,ulong param_2,undefined8 param_3,ulong *param_4,ulong param_5)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  ulong uVar4;
  int iVar5;
  uint uVar6;
  
  if ((param_2 < 0x18) || (param_5 < 8)) {
    return 0xffffffffffffffff;
  }
  uVar6 = (int)param_2 * 0x1f9;
  uVar3 = *param_1;
  uVar2 = param_1[1];
  iVar5 = 0;
  do {
    while( true ) {
      uVar4 = param_2 + 1;
      iVar5 = iVar5 + -0x61c88647;
      if ((((uint)param_2 * (int)uVar4 & 1) != 0) || (DAT_00104010 != 0)) {
        uVar3 = ((uint)(param_2 << 7) ^ uVar3) * 0x2d6b + DAT_00104008;
        uVar3 = uVar3 >> 0xb ^ uVar3;
      }
      uVar1 = (uint)param_2 | 1;
      uVar3 = uVar3 + (uVar2 * 0x10 + param_1[2] ^ (uVar2 >> 5) + param_1[3] ^ iVar5 + uVar2);
      param_2 = uVar4;
      if (((uVar1 * uVar1 & 7) != 1) || (DAT_00104008 != 0x3c71)) break;
      uVar6 = uVar6 + 0x1f9;
...
```
</details>

<details><summary>Mã nguồn gốc</summary>

```c
#include "vera.h"

VERA_FN(fn_05)
{
    uint32_t v0, v1, k0, k1, k2, k3, s = 0u;
    (void)arg;
    if (len < 24 || out_cap < 8)
        return VERA_ERR;
    v0 = VERA_LD32(in);
    v1 = VERA_LD32(in + 4);
    k0 = VERA_LD32(in + 8);
    k1 = VERA_LD32(in + 12);
    k2 = VERA_LD32(in + 16);
    k3 = VERA_LD32(in + 20);
    for (unsigned r = 0; r < 32; r++) {
        s += 0x9E3779B9u;
        OBF_JUNK(v0, r + len);
        v0 += ((v1 << 4) + k0) ^ (v1 + s) ^ ((v1 >> 5) + k1);
        OBF_GUARD(v1, r + len, v1 += ((v0 << 4) + k2) ^ (v0 + s) ^ ((v0 >> 5) + k3));
    }
    VERA_ST32(out, v0);
    VERA_ST32(out + 4, v1);
    return 8;
}
```
</details>

<details><summary>recovered_c của model</summary>

```c
uint64_t fn_05(const uint8_t *in, size_t len, uint64_t arg, uint8_t *out, size_t out_cap) {
  if ((len < 0x18) || (out_cap < 8)) {
    return VERA_ERR;
  }
  uint uVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  int iVar5;
  uint uVar6;
  uVar6 = (int)len * 0x1f9;
  uVar3 = *(uint *)in;
  uVar2 = *(uint *)(in + 4);
  iVar5 = 0;
  do {
    uVar4 = len + 1;
    iVar5 = iVar5 + -0x61c88647;
    if ((((uint)len * (int)uVar4 & 1) != 0) || (DAT_00104010 != 0)) {
      uVar3 = ((uint)(len << 7) ^ uVar3) * 0x2d6b + DAT_00104008;
      uVar3 = uVar3 >> 0xb ^ uVar3;
    }
    uVar1 = (uint)len | 1;
    uVar3 = uVar3 + (uVar2 * 0x10 + *(uint *)(in + 8) ^ (uVar2 >> 5) + *(uint *)(in + 12) ^ iVar5 + uVar2);
    len = uVar4;
    if (((uVar1 * uVar1 & 7) != 1) || (DAT_00104008 != 0x3c71)) break;
    uVar6 = uVar6 + 0x1f9;
    uVar2 = uVar2 + (uVar3 * 0x10 + *(uint *)(in + 16) ^ (uVar3 >> 5) + *(uint *)(in + 20) ^ iVar5 + uVar3);
    if (iVar5 == -0x3910c8e0) goto LAB_0010120c;
  } while (iVar5 != -0x3910c8e0);
LAB_0010120c:
...
```
</details>

### obf/fn_08 — near-miss của CRC-32 (near_miss)

- Model: algorithm = `unknown`, tên đề xuất = `fn_08`
- V1: compiled = False, FEPR = 0.0

<details><summary>Pseudocode model đã đọc</summary>

```c
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
...
```
</details>

<details><summary>Mã nguồn gốc</summary>

```c
#include "vera.h"

VERA_FN(fn_08)
{
    uint32_t h = 0xFFFFFFFFu;
    (void)arg; (void)out; (void)out_cap;
    OBF_SPIN(h);
    for (size_t i = 0; i < len; i++) {
        h ^= in[i];
        OBF_JUNK(h, i);
        for (unsigned b = 0; b < 8; b++)
            OBF_GUARD(h, len + b, h = (h >> 1) ^ (0xF7179BF5u & (0u - (h & 1u))));
    }
    return (uint64_t)(h ^ 0xFFFFFFFFu);
}
```
</details>

<details><summary>recovered_c của model</summary>

```c
uint64_t fn_08(const uint8_t *in, size_t len, uint64_t arg, uint8_t *out, size_t out_cap) {
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
  } else {
    uVar4 = 0;
    uVar2 = 0xffffffff;
    do {
      uVar2 = uVar2 >> 5 ^ uVar2 * 8 ^ uVar4;
      uVar4 = uVar4 + 1;
    } while (uVar4 < DAT_00104010);
  }
  if (len == 0) {
    return ~uVar2;
  }
  uVar4 = (int)len * 0x1f9;
  uVar8 = 0;
  lVar6 = 0;
  do {
    uVar2 = uVar2 ^ *(byte *)(in + lVar6);
    lVar7 = lVar6 + 1;
    lVar3 = len;
...
```
</details>

### obf/fn_18 — tự thiết kế: máy trạng thái kiểm tra ngoặc (custom)

- Model: algorithm = `unknown`, tên đề xuất = `fn_18`
- V1: compiled = True, FEPR = 0.02
- `verified` (IO) [IO] “Returns 0 when len == 0.” → "đúng trên 1 vector thỏa điều kiện"

<details><summary>Pseudocode model đã đọc</summary>

```c
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
...
```
</details>

<details><summary>Mã nguồn gốc</summary>

```c
#include "vera.h"

/*
 * Máy trạng thái kiểm tra ngoặc () [] {} với chuỗi "..." và ký tự thoát \ trong chuỗi.
 * Trả 0 nếu hợp lệ; vị trí (tính từ 1) của byte lỗi đầu tiên; len + 1 nếu hết input
 * khi còn ngoặc mở hoặc chuỗi chưa đóng. Độ sâu tối đa 64.
 */
VERA_FN(fn_18)
{
    uint8_t st[64];
    size_t d = 0;
    unsigned q = 0; /* 0 = ngoài chuỗi, 1 = trong chuỗi, 2 = sau dấu thoát */
    uint8_t c;
    (void)arg; (void)out; (void)out_cap;
    for (size_t i = 0; i < len; i++) {
        c = in[i];
        OBF_JUNK(q, i + len);
        if (q == 2) {
            q = 1;
        } else if (q == 1) {
            if (c == '\\')
                q = 2;
            else if (c == '"')
                OBF_GUARD(q, i, q = 0);
        } else if (c == '"') {
            OBF_GUARD(q, i + d, q = 1);
        } else if (c == '(' || c == '[' || c == '{') {
            if (d == 64)
                return i + 1;
            OBF_GUARD(d, i, st[d++] = (uint8_t)(c == '(' ? ')' : c + 2));
...
```
</details>

<details><summary>recovered_c của model</summary>

```c
uint64_t fn_18(const uint8_t *in, size_t len, uint64_t arg, uint8_t *out, size_t out_cap) {
  if (len == 0) {
    return 0;
  }

  uint64_t uVar11 = 0;
  uint64_t uVar6 = 0;
  uint64_t uVar8 = 0;
  uint64_t lVar10 = len;
  uint64_t uVar9;

  for (uint64_t lVar4 = 0; lVar4 < lVar10; lVar4++) {
    uint8_t bVar1 = in[lVar4];

    if ((((int)(lVar10 + 1) * (uint)lVar10 & 1) != 0) || (arg != 0)) {
      uVar6 = ((uint)(lVar10 << 7) ^ uVar6) * 0x2d6b + arg;
      uVar6 = uVar6 >> 0xb ^ uVar6;
    }

    if (uVar6 == 2) {
      uVar6 = 1;
    } else {
      if (uVar6 == 1) {
        if (bVar1 == 0x5c) {
          uVar6 = 2;
        } else if ((bVar1 == 0x22) &&
                   ((((lVar4 | 1) * (lVar4 | 1) & 7) != 1 || (uVar6 = 0, arg != 0x3c71)))) {
          uVar6 = (uint)uVar11 ^ 0x51e4;
        }
      } else {
...
```
</details>

### opt/fn_05 — TEA (classic)

- Model: algorithm = `unknown`, tên đề xuất = `fn_05`
- V1: compiled = True, FEPR = 0.32
- `verified` (SIDE) [SIDE] “Writes the hash value to out[0..7].” → "hàm có ghi out trên vector hợp lệ"

<details><summary>Pseudocode model đã đọc</summary>

```c
undefined8 fn_05(uint *param_1,ulong param_2,undefined8 param_3,ulong *param_4,ulong param_5)

{
  uint uVar1;
  uint uVar2;
  int iVar3;
  
  if ((0x17 < param_2) && (7 < param_5)) {
    uVar2 = *param_1;
    iVar3 = 0;
    uVar1 = param_1[1];
    do {
      iVar3 = iVar3 + -0x61c88647;
      uVar2 = uVar2 + (uVar1 * 0x10 + param_1[2] ^ (uVar1 >> 5) + param_1[3] ^ iVar3 + uVar1);
      uVar1 = uVar1 + (uVar2 * 0x10 + param_1[4] ^ (uVar2 >> 5) + param_1[5] ^ iVar3 + uVar2);
    } while (iVar3 != -0x3910c8e0);
    *param_4 = (((((((ulong)(uVar1 >> 0x18) << 8 | (ulong)(uVar1 >> 0x10 & 0xff)) << 8 |
                   (ulong)(uVar1 >> 8 & 0xff)) << 8 | (ulong)(uVar1 & 0xff)) << 8 |
                 (ulong)(uVar2 >> 0x18)) << 8 | (ulong)(uVar2 >> 0x10 & 0xff)) << 8 |
               (ulong)(uVar2 >> 8 & 0xff)) << 8 | (ulong)(uVar2 & 0xff);
    return 8;
  }
  return 0xffffffffffffffff;
}
```
</details>

<details><summary>Mã nguồn gốc</summary>

```c
#include "vera.h"

VERA_FN(fn_05)
{
    uint32_t v0, v1, k0, k1, k2, k3, s = 0u;
    (void)arg;
    if (len < 24 || out_cap < 8)
        return VERA_ERR;
    v0 = VERA_LD32(in);
    v1 = VERA_LD32(in + 4);
    k0 = VERA_LD32(in + 8);
    k1 = VERA_LD32(in + 12);
    k2 = VERA_LD32(in + 16);
    k3 = VERA_LD32(in + 20);
    for (unsigned r = 0; r < 32; r++) {
        s += 0x9E3779B9u;
        OBF_JUNK(v0, r + len);
        v0 += ((v1 << 4) + k0) ^ (v1 + s) ^ ((v1 >> 5) + k1);
        OBF_GUARD(v1, r + len, v1 += ((v0 << 4) + k2) ^ (v0 + s) ^ ((v0 >> 5) + k3));
    }
    VERA_ST32(out, v0);
    VERA_ST32(out + 4, v1);
    return 8;
}
```
</details>

<details><summary>recovered_c của model</summary>

```c
uint64_t fn_05(const uint8_t *in, size_t len, uint64_t arg, uint8_t *out, size_t out_cap) {
  if ((0x17 < len) && (7 < out_cap)) {
    uint uVar1 = in[0];
    uint uVar2 = in[1];
    int iVar3 = 0;
    do {
      iVar3 = iVar3 + -0x61c88647;
      uVar1 = uVar1 + (uVar2 * 0x10 + in[2] ^ (uVar2 >> 5) + in[3] ^ iVar3 + uVar2);
      uVar2 = uVar2 + (uVar1 * 0x10 + in[4] ^ (uVar1 >> 5) + in[5] ^ iVar3 + uVar1);
    } while (iVar3 != -0x3910c8e0);
    out[0] = (uVar1 >> 0x18) & 0xff;
    out[1] = (uVar1 >> 0x10) & 0xff;
    out[2] = (uVar1 >> 8) & 0xff;
    out[3] = uVar1 & 0xff;
    out[4] = (uVar2 >> 0x18) & 0xff;
    out[5] = (uVar2 >> 0x10) & 0xff;
    out[6] = (uVar2 >> 8) & 0xff;
    out[7] = uVar2 & 0xff;
    return 8;
  }
  return VERA_ERR;
}
```
</details>

### opt/fn_14 — near-miss của Base64 encode (near_miss)

- Model: algorithm = `unknown`, tên đề xuất = `fn_14`
- V1: compiled = False, FEPR = 0.0
- `verified` (IO) [IO] “Returns -1 when out_cap < len.” → "đúng trên 3 vector thỏa điều kiện"

<details><summary>Pseudocode model đã đọc</summary>

```c
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
...
```
</details>

<details><summary>Mã nguồn gốc</summary>

```c
#include "vera.h"

VERA_FN(fn_14)
{
    static const char tb[] = "AfhmdLEr3GMxg2S/a91UZnTlHOI5KYzevFCwNQ+P4tWV7cpXRbDuykjJsoi6q80B";
    size_t need = 4 * ((len + 2) / 3), o = 0, i = 0;
    uint32_t w;
    (void)arg;
    if (out_cap < need)
        return VERA_ERR;
    for (; i + 3 <= len; i += 3) {
        w = ((uint32_t)in[i] << 16) | ((uint32_t)in[i + 1] << 8) | in[i + 2];
        OBF_JUNK(w, i + len);
        out[o++] = (uint8_t)tb[(w >> 18) & 63];
        out[o++] = (uint8_t)tb[(w >> 12) & 63];
        OBF_GUARD(o, i, out[o++] = (uint8_t)tb[(w >> 6) & 63]);
        out[o++] = (uint8_t)tb[w & 63];
    }
    if (len - i == 1) {
        w = (uint32_t)in[i] << 16;
        out[o++] = (uint8_t)tb[(w >> 18) & 63];
        out[o++] = (uint8_t)tb[(w >> 12) & 63];
        out[o++] = '=';
        out[o++] = '=';
    } else if (len - i == 2) {
        w = ((uint32_t)in[i] << 16) | ((uint32_t)in[i + 1] << 8);
        out[o++] = (uint8_t)tb[(w >> 18) & 63];
        out[o++] = (uint8_t)tb[(w >> 12) & 63];
        out[o++] = (uint8_t)tb[(w >> 6) & 63];
        out[o++] = '=';
...
```
</details>

<details><summary>recovered_c của model</summary>

```c
uint64_t fn_14(const uint8_t *in, size_t len, uint64_t arg, uint8_t *out, size_t out_cap) {
  if (out_cap < (len + 2) / 3 << 2) {
    return VERA_ERR;
  }
  size_t lVar7 = 0;
  if (len >= 3) {
    for (size_t uVar3 = 0; uVar3 + 3 <= len; uVar3 += 3) {
      uint uVar4 = (uint)in[uVar3] << 0x10 | (uint)in[uVar3 + 1] << 8;
      uint uVar5 = (uint)in[uVar3 + 2];
      out[lVar7++] = 'AfhmdLEr3GMxg2S/a91UZnTlHOI5KYzevFCwNQ+P4tWV7cpXRbDuykjJsoi6q80B'[uVar5 & 0x3f];
      out[lVar7++] = 'AfhmdLEr3GMxg2S/a91UZnTlHOI5KYzevFCwNQ+P4tWV7cpXRbDuykjJsoi6q80B'[(uVar5 | uVar4) >> 6 & 0x3f];
      out[lVar7++] = 'AfhmdLEr3GMxg2S/a91UZnTlHOI5KYzevFCwNQ+P4tWV7cpXRbDuykjJsoi6q80B'[uVar4 >> 0xc & 0x3f];
      out[lVar7++] = 'AfhmdLEr3GMxg2S/a91UZnTlHOI5KYzevFCwNQ+P4tWV7cpXRbDuykjJsoi6q80B'[in[uVar3] >> 2];
    }
    len -= uVar3;
  }
  if (len == 1) {
    out[lVar7++] = 'AfhmdLEr3GMxg2S/a91UZnTlHOI5KYzevFCwNQ+P4tWV7cpXRbDuykjJsoi6q80B'[(in[uVar3] & 3) << 4];
    out[lVar7++] = 'AfhmdLEr3GMxg2S/a91UZnTlHOI5KYzevFCwNQ+P4tWV7cpXRbDuykjJsoi6q80B'[in[uVar3] >> 2];
    out[lVar7++] = '=';
    out[lVar7++] = '=';
  } else if (len == 2) {
    uint uVar4 = (uint)in[uVar3] << 8;
    out[lVar7++] = 'AfhmdLEr3GMxg2S/a91UZnTlHOI5KYzevFCwNQ+P4tWV7cpXRbDuykjJsoi6q80B'[(uVar4 & 0xf00) >> 6];
    out[lVar7++] = 'AfhmdLEr3GMxg2S/a91UZnTlHOI5KYzevFCwNQ+P4tWV7cpXRbDuykjJsoi6q80B'[(uVar4 | (uint)in[uVar3 + 1] << 0x10) >> 0xc & 0x3f];
    out[lVar7++] = 'AfhmdLEr3GMxg2S/a91UZnTlHOI5KYzevFCwNQ+P4tWV7cpXRbDuykjJsoi6q80B'[in[uVar3 + 1] >> 2];
    out[lVar7++] = '=';
  }
  return lVar7;
}
```
</details>

### opt/fn_18 — tự thiết kế: máy trạng thái kiểm tra ngoặc (custom)

- Model: algorithm = `unknown`, tên đề xuất = `fn_18`
- V1: compiled = True, FEPR = 0.04

<details><summary>Pseudocode model đã đọc</summary>

```c
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
...
```
</details>

<details><summary>Mã nguồn gốc</summary>

```c
#include "vera.h"

/*
 * Máy trạng thái kiểm tra ngoặc () [] {} với chuỗi "..." và ký tự thoát \ trong chuỗi.
 * Trả 0 nếu hợp lệ; vị trí (tính từ 1) của byte lỗi đầu tiên; len + 1 nếu hết input
 * khi còn ngoặc mở hoặc chuỗi chưa đóng. Độ sâu tối đa 64.
 */
VERA_FN(fn_18)
{
    uint8_t st[64];
    size_t d = 0;
    unsigned q = 0; /* 0 = ngoài chuỗi, 1 = trong chuỗi, 2 = sau dấu thoát */
    uint8_t c;
    (void)arg; (void)out; (void)out_cap;
    for (size_t i = 0; i < len; i++) {
        c = in[i];
        OBF_JUNK(q, i + len);
        if (q == 2) {
            q = 1;
        } else if (q == 1) {
            if (c == '\\')
                q = 2;
            else if (c == '"')
                OBF_GUARD(q, i, q = 0);
        } else if (c == '"') {
            OBF_GUARD(q, i + d, q = 1);
        } else if (c == '(' || c == '[' || c == '{') {
            if (d == 64)
                return i + 1;
            OBF_GUARD(d, i, st[d++] = (uint8_t)(c == '(' ? ')' : c + 2));
...
```
</details>

<details><summary>recovered_c của model</summary>

```c
uint64_t fn_18(const uint8_t *in, size_t len, uint64_t arg, uint8_t *out, size_t out_cap) {
  if (len == 0 || len < 0 || out_cap < len || arg == 0) {
    return len;
  }

  uint8_t local_58[72];
  size_t lVar2 = 0;
  bool bVar6 = false;
  size_t lVar3 = 0;

  while (lVar2 < len) {
    uint8_t bVar4 = in[lVar2];
    if (bVar4 == 0x29) {
      break;
    }
    if (bVar4 < 0x2a) {
      if (bVar4 == 0x22) {
        lVar2++;
        if (lVar2 != len) {
          bVar4 = in[lVar2];
          break;
        }
        break;
      }
      if (bVar4 != 0x28) {
        break;
      }
      if (lVar3 == 0x40) {
        break;
      }
...
```
</details>

### plain/fn_01 — CRC-32 (classic)

- Model: algorithm = `Implements CRC-32.`, tên đề xuất = `fn_01`
- V1: compiled = True, FEPR = 0.98
- `verified` (SIDE) [SIDE] “Does not write to out.” → "không vector nào ghi out"
- `verified` (V1b) [ALG] “The function implements Implements CRC-32..” → "oracle CRC-32 khớp 50/50 vector"

<details><summary>Pseudocode model đã đọc</summary>

```c
uint64_t fn_01(uint8_t *in,size_t len,uint64_t arg,uint8_t *out,size_t out_cap)

{
  size_t out_cap_local;
  uint8_t *out_local;
  uint64_t arg_local;
  size_t len_local;
  uint8_t *in_local;
  uint32_t h;
  uint b;
  size_t i;
  
  h = 0xffffffff;
  for (i = 0; i < len; i = i + 1) {
    h = h ^ in[i];
    for (b = 0; b < 8; b = b + 1) {
      h = -(h & 1) & 0xedb88320 ^ h >> 1;
    }
  }
  return (ulong)~h;
}
```
</details>

<details><summary>Mã nguồn gốc</summary>

```c
#include "vera.h"

VERA_FN(fn_01)
{
    uint32_t h = 0xFFFFFFFFu;
    (void)arg; (void)out; (void)out_cap;
    OBF_SPIN(h);
    for (size_t i = 0; i < len; i++) {
        h ^= in[i];
        OBF_JUNK(h, i);
        for (unsigned b = 0; b < 8; b++)
            OBF_GUARD(h, len + b, h = (h >> 1) ^ (0xEDB88320u & (0u - (h & 1u))));
    }
    return (uint64_t)(h ^ 0xFFFFFFFFu);
}
```
</details>

<details><summary>recovered_c của model</summary>

```c
uint64_t fn_01(const uint8_t *in, size_t len, uint64_t arg, uint8_t *out, size_t out_cap) {
  if (len == 0) {
    return VERA_ERR;
  }
  uint32_t h = 0xffffffff;
  for (size_t i = 0; i < len; i++) {
    h = h ^ in[i];
    for (uint8_t b = 0; b < 8; b++) {
      h = -(h & 1) & 0xedb88320 ^ h >> 1;
    }
  }
  return (uint64_t)~h;
}
```
</details>

### plain/fn_18 — tự thiết kế: máy trạng thái kiểm tra ngoặc (custom)

- Model: algorithm = `unknown`, tên đề xuất = `fn_18`
- V1: compiled = False, FEPR = 0.0
- `verified` (SIDE) [SIDE] “The function does not write to the output buffer.” → "không vector nào ghi out"
- `verified` (SIDE) [SIDE] “The function does not modify the input buffer.” → "in không đổi trên mọi vector (runner kiểm)"

<details><summary>Pseudocode model đã đọc</summary>

```c
uint64_t fn_18(uint8_t *in,size_t len,uint64_t arg,uint8_t *out,size_t out_cap)

{
  long lVar1;
  uint64_t uVar2;
  uint8_t uVar3;
  long in_FS_OFFSET;
  size_t out_cap_local;
  uint8_t *out_local;
  uint64_t arg_local;
  size_t len_local;
  uint8_t *in_local;
  uint8_t c;
  uint q;
  size_t d;
  size_t i;
  uint8_t st [64];
  
  lVar1 = *(long *)(in_FS_OFFSET + 0x28);
  d = 0;
  q = 0;
  i = 0;
  do {
    if (len <= i) {
      if ((d == 0) && (q == 0)) {
        uVar2 = 0;
      }
      else {
        uVar2 = len + 1;
      }
...
```
</details>

<details><summary>Mã nguồn gốc</summary>

```c
#include "vera.h"

/*
 * Máy trạng thái kiểm tra ngoặc () [] {} với chuỗi "..." và ký tự thoát \ trong chuỗi.
 * Trả 0 nếu hợp lệ; vị trí (tính từ 1) của byte lỗi đầu tiên; len + 1 nếu hết input
 * khi còn ngoặc mở hoặc chuỗi chưa đóng. Độ sâu tối đa 64.
 */
VERA_FN(fn_18)
{
    uint8_t st[64];
    size_t d = 0;
    unsigned q = 0; /* 0 = ngoài chuỗi, 1 = trong chuỗi, 2 = sau dấu thoát */
    uint8_t c;
    (void)arg; (void)out; (void)out_cap;
    for (size_t i = 0; i < len; i++) {
        c = in[i];
        OBF_JUNK(q, i + len);
        if (q == 2) {
            q = 1;
        } else if (q == 1) {
            if (c == '\\')
                q = 2;
            else if (c == '"')
                OBF_GUARD(q, i, q = 0);
        } else if (c == '"') {
            OBF_GUARD(q, i + d, q = 1);
        } else if (c == '(' || c == '[' || c == '{') {
            if (d == 64)
                return i + 1;
            OBF_GUARD(d, i, st[d++] = (uint8_t)(c == '(' ? ')' : c + 2));
...
```
</details>

<details><summary>recovered_c của model</summary>

```c
uint64_t fn_18(const uint8_t *in, size_t len, uint64_t arg, uint8_t *out, size_t out_cap) {
  size_t d = 0;
  uint q = 0;
  size_t i = 0;
  uint8_t st[64];

  while (i < len) {
    uint8_t uVar3 = in[i];

    if (q == 2) {
      q = 1;
    } else if (q == 1) {
      if (uVar3 == '\') {
        q = 2;
      } else if (uVar3 == '"') {
        q = 0;
      }
    } else if (uVar3 == '"') {
      q = 1;
    } else if (((uVar3 == '(') || (uVar3 == '[')) || (uVar3 == '{')) {
      if (d == 0x40) {
        return i + 1;
      }
      if (uVar3 == '(') {
        uVar3 = ')';
      } else {
        uVar3 = uVar3 + '
      }
      st[d] = uVar3;
      d = d + 1;
...
```
</details>

## D. Claim IO/SIDE bị vector bác bỏ

- obf/fn_01: `contradicted` (SIDE) [SIDE] “The function writes to out[0..len-1].” → {"vector": "v00", "observed": "không vector hợp lệ nào ghi out"}
- obf/fn_14: `contradicted` (IO) [IO] “Returns 0xFFFFFFFFFFFFFFFF when the input length is less than 3.” → {"vector": "v00", "tag": "len0", "observed": "ret 0x0000000000000000"}
- obf/fn_14: `contradicted` (IO) [IO] “Returns the length of the output when the input length is 1.” → {"vector": "v01", "tag": "len1", "observed": "ret 0x0000000000000004"}
- obf/fn_14: `contradicted` (IO) [IO] “Returns the length of the output when the input length is 2.” → {"vector": "v45", "tag": "rand45", "observed": "ret 0x0000000000000004"}
- plain/fn_08: `contradicted` (IO) [IO] “Returns 0xFFFFFFFFFFFFFFFF when len == 0.” → {"vector": "v00", "tag": "len0", "observed": "ret 0x0000000000000000"}
