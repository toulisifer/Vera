# Ứng viên case study — E1

## A. Gán nhầm thuật toán (V1b bác bỏ claim ALG)

### opt/fn_02 — FNV-1a (64-bit) (classic)

- Model: algorithm = `ALG: CRC-32`, tên đề xuất = `fn_02`
- V1: compiled = True, FEPR = 1.0
- `contradicted` (V1b) [ALG] “The function implements ALG: CRC-32.” → {"vector": "v00", "tag": "len0", "expected_ret": "0xcbf29ce484222325", "oracle_ret": "0x0000000000000000"}

<details><summary>Pseudocode model đã đọc</summary>

```c
ulong fn_02(byte *param_1,long param_2)

{
  byte bVar1;
  ulong uVar2;
  byte *pbVar3;
  
  uVar2 = 0xcbf29ce484222325;
  if (param_2 != 0) {
    pbVar3 = param_1 + param_2;
    do {
      bVar1 = *param_1;
      param_1 = param_1 + 1;
      uVar2 = (uVar2 ^ bVar1) * 0x100000001b3;
    } while (pbVar3 != param_1);
  }
  return uVar2;
}
```
</details>

<details><summary>Mã nguồn gốc</summary>

```c
#include "vera.h"

VERA_FN(fn_02)
{
    uint64_t h = 0xCBF29CE484222325ull;
    (void)arg; (void)out; (void)out_cap;
    for (size_t i = 0; i < len; i++) {
        h ^= in[i];
        OBF_GUARD(h, i, h *= 0x00000100000001B3ull);
        OBF_JUNK(h, len);
    }
    OBF_SPIN(h);
    return h;
}
```
</details>

<details><summary>recovered_c của model</summary>

```c
uint64_t fn_02(const uint8_t *in, size_t len, uint64_t arg, uint8_t *out, size_t out_cap) {
  uint64_t crc = 0xcbf29ce484222325;
  if (len != 0) {
    for (size_t i = 0; i < len; i++) {
      crc = (crc ^ in[i]) * 0x100000001b3;
    }
  }
  return crc;
}
```
</details>

### opt/fn_08 — near-miss của CRC-32 (near_miss)

- Model: algorithm = `Implements CRC-16/XMODEM.`, tên đề xuất = `fn_08`
- V1: compiled = True, FEPR = 1.0
- `contradicted` (V1b) [ALG] “The function implements CRC-16/XMODEM.” → {"vector": "v01", "tag": "len1", "expected_ret": "0x00000000a22615fe", "oracle_ret": "0x0000000000009f59"}

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

### opt/fn_09 — near-miss của FNV-1a (64-bit) (near_miss)

- Model: algorithm = `CRC-32`, tên đề xuất = `fn_09`
- V1: compiled = True, FEPR = 0.98
- `contradicted` (V1b) [ALG] “The function implements CRC-32.” → {"vector": "v00", "tag": "len0", "expected_ret": "0xcbf29ce484222325", "oracle_ret": "0x0000000000000000"}

<details><summary>Pseudocode model đã đọc</summary>

```c
ulong fn_09(byte *param_1,long param_2)

{
  byte bVar1;
  ulong uVar2;
  byte *pbVar3;
  
  uVar2 = 0xcbf29ce484222325;
  if (param_2 != 0) {
    pbVar3 = param_1 + param_2;
    do {
      bVar1 = *param_1;
      param_1 = param_1 + 1;
      uVar2 = (uVar2 ^ bVar1) * 0x100000001b5;
    } while (pbVar3 != param_1);
  }
  return uVar2;
}
```
</details>

<details><summary>Mã nguồn gốc</summary>

```c
#include "vera.h"

VERA_FN(fn_09)
{
    uint64_t h = 0xCBF29CE484222325ull;
    (void)arg; (void)out; (void)out_cap;
    for (size_t i = 0; i < len; i++) {
        h ^= in[i];
        OBF_GUARD(h, i, h *= 0x00000100000001B5ull);
        OBF_JUNK(h, len);
    }
    OBF_SPIN(h);
    return h;
}
```
</details>

<details><summary>recovered_c của model</summary>

```c
uint64_t fn_09(const uint8_t *in, size_t len, uint64_t arg, uint8_t *out, size_t out_cap) {
  if (len == 0) {
    return VERA_ERR;
  }
  uint64_t crc = 0xcbf29ce484222325;
  for (size_t i = 0; i < len; i++) {
    crc = (crc ^ in[i]) * 0x100000001b5;
  }
  return crc;
}
```
</details>

### plain/fn_02 — FNV-1a (64-bit) (classic)

- Model: algorithm = `Implements CRC-32.`, tên đề xuất = `fn_02`
- V1: compiled = True, FEPR = 1.0
- `contradicted` (V1b) [ALG] “The function implements CRC-32.” → {"vector": "v00", "tag": "len0", "expected_ret": "0xcbf29ce484222325", "oracle_ret": "0x0000000000000000"}

<details><summary>Pseudocode model đã đọc</summary>

```c
uint64_t fn_02(uint8_t *in,size_t len,uint64_t arg,uint8_t *out,size_t out_cap)

{
  size_t out_cap_local;
  uint8_t *out_local;
  uint64_t arg_local;
  size_t len_local;
  uint8_t *in_local;
  uint64_t h;
  size_t i;
  
  h = 0xcbf29ce484222325;
  for (i = 0; i < len; i = i + 1) {
    h = (h ^ in[i]) * 0x100000001b3;
  }
  return h;
}
```
</details>

<details><summary>Mã nguồn gốc</summary>

```c
#include "vera.h"

VERA_FN(fn_02)
{
    uint64_t h = 0xCBF29CE484222325ull;
    (void)arg; (void)out; (void)out_cap;
    for (size_t i = 0; i < len; i++) {
        h ^= in[i];
        OBF_GUARD(h, i, h *= 0x00000100000001B3ull);
        OBF_JUNK(h, len);
    }
    OBF_SPIN(h);
    return h;
}
```
</details>

<details><summary>recovered_c của model</summary>

```c
uint64_t fn_02(const uint8_t *in, size_t len, uint64_t arg, uint8_t *out, size_t out_cap) {
  uint64_t h = 0xcbf29ce484222325;
  for (size_t i = 0; i < len; i++) {
    h = (h ^ in[i]) * 0x100000001b3;
  }
  return h;
}
```
</details>

### plain/fn_09 — near-miss của FNV-1a (64-bit) (near_miss)

- Model: algorithm = `Implements CRC-32.`, tên đề xuất = `fn_09`
- V1: compiled = True, FEPR = 1.0
- `contradicted` (V1b) [ALG] “The function implements CRC-32.” → {"vector": "v00", "tag": "len0", "expected_ret": "0xcbf29ce484222325", "oracle_ret": "0x0000000000000000"}

<details><summary>Pseudocode model đã đọc</summary>

```c
uint64_t fn_09(uint8_t *in,size_t len,uint64_t arg,uint8_t *out,size_t out_cap)

{
  size_t out_cap_local;
  uint8_t *out_local;
  uint64_t arg_local;
  size_t len_local;
  uint8_t *in_local;
  uint64_t h;
  size_t i;
  
  h = 0xcbf29ce484222325;
  for (i = 0; i < len; i = i + 1) {
    h = (h ^ in[i]) * 0x100000001b5;
  }
  return h;
}
```
</details>

<details><summary>Mã nguồn gốc</summary>

```c
#include "vera.h"

VERA_FN(fn_09)
{
    uint64_t h = 0xCBF29CE484222325ull;
    (void)arg; (void)out; (void)out_cap;
    for (size_t i = 0; i < len; i++) {
        h ^= in[i];
        OBF_GUARD(h, i, h *= 0x00000100000001B5ull);
        OBF_JUNK(h, len);
    }
    OBF_SPIN(h);
    return h;
}
```
</details>

<details><summary>recovered_c của model</summary>

```c
uint64_t fn_09(const uint8_t *in, size_t len, uint64_t arg, uint8_t *out, size_t out_cap) {
  uint64_t h = 0xcbf29ce484222325;
  for (size_t i = 0; i < len; i++) {
    h = (h ^ in[i]) * 0x100000001b5;
  }
  return h;
}
```
</details>

### plain/fn_13 — near-miss của RC4 (near_miss)

- Model: algorithm = `RC4`, tên đề xuất = `fn_13`
- V1: compiled = True, FEPR = 1.0
- `contradicted` (V1b) [ALG] “The function implements RC4.” → {"vector": "v01", "tag": "len1", "expected_ret": "0x0000000000000001", "oracle_ret": "0x0000000000000001"}

<details><summary>Pseudocode model đã đọc</summary>

```c
uint64_t fn_13(uint8_t *in,size_t len,uint64_t arg,uint8_t *out,size_t out_cap)

{
  uint8_t uVar1;
  long lVar2;
  long in_FS_OFFSET;
  size_t out_cap_local;
  uint8_t *out_local;
  uint64_t arg_local;
  size_t len_local;
  uint8_t *in_local;
  uint8_t t;
  uint i;
  uint j;
  size_t n;
  uint8_t k [8];
  uint8_t s [256];
  
  lVar2 = *(long *)(in_FS_OFFSET + 0x28);
  j = 0;
  if (out_cap < len) {
    len = 0xffffffffffffffff;
  }
  else {
    for (i = 0; i < 8; i = i + 1) {
      k[i] = (uint8_t)(arg >> ((byte)(i << 3) & 0x3f));
    }
    for (i = 0; i < 0x100; i = i + 1) {
      s[i] = (uint8_t)i;
    }
...
```
</details>

<details><summary>Mã nguồn gốc</summary>

```c
#include "vera.h"

VERA_FN(fn_13)
{
    uint8_t s[256], k[8], t;
    unsigned i, j = 0;
    if (out_cap < len)
        return VERA_ERR;
    for (i = 0; i < 8; i++)
        k[i] = (uint8_t)(arg >> (8 * i));
    for (i = 0; i < 256; i++)
        s[i] = (uint8_t)i;
    for (i = 0; i < 256; i++) {
        OBF_GUARD(j, i, j = (j + s[i] + (k[i & 7] ^ i)) & 0xFFu);
        t = s[i]; s[i] = s[j]; s[j] = t;
    }
    i = j = 0;
    for (size_t n = 0; n < len; n++) {
        i = (i + 1) & 0xFFu;
        j = (j + s[i]) & 0xFFu;
        OBF_JUNK(j, n + len);
        t = s[i]; s[i] = s[j]; s[j] = t;
        out[n] = in[n] ^ s[(s[i] + s[j]) & 0xFFu];
    }
    return len;
}
```
</details>

<details><summary>recovered_c của model</summary>

```c
uint64_t fn_13(const uint8_t *in, size_t len, uint64_t arg, uint8_t *out, size_t out_cap) {
  if (out_cap < len) {
    return VERA_ERR;
  }

  uint8_t k[8];
  uint8_t s[256];
  uint8_t j = 0;
  uint8_t i = 0;
  uint8_t t;

  for (size_t i = 0; i < 8; i++) {
    k[i] = (uint8_t)(arg >> ((byte)(i << 3) & 0x3f));
  }

  for (size_t i = 0; i < 0x100; i++) {
    s[i] = (uint8_t)i;
  }

  for (size_t i = 0; i < 0x100; i++) {
    j = (k[i & 7] ^ i) + s[i] + j & 0xff;
    t = s[i];
    s[i] = s[j];
    s[j] = t;
  }

  j = 0;
  for (size_t n = 0; n < len; n++) {
    i = (i + 1) & 0xff;
    j = (j + s[i]) & 0xff;
...
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

### opt/fn_02 — FNV-1a (64-bit) (classic)

- Model: algorithm = `ALG: CRC-32`, tên đề xuất = `fn_02`
- V1: compiled = True, FEPR = 1.0
- `verified` (SIDE) [SIDE] “Does not write to out.” → "không vector nào ghi out"
- `contradicted` (V1b) [ALG] “The function implements ALG: CRC-32.” → {"vector": "v00", "tag": "len0", "expected_ret": "0xcbf29ce484222325", "oracle_ret": "0x0000000000000000"}

<details><summary>Pseudocode model đã đọc</summary>

```c
ulong fn_02(byte *param_1,long param_2)

{
  byte bVar1;
  ulong uVar2;
  byte *pbVar3;
  
  uVar2 = 0xcbf29ce484222325;
  if (param_2 != 0) {
    pbVar3 = param_1 + param_2;
    do {
      bVar1 = *param_1;
      param_1 = param_1 + 1;
      uVar2 = (uVar2 ^ bVar1) * 0x100000001b3;
    } while (pbVar3 != param_1);
  }
  return uVar2;
}
```
</details>

<details><summary>Mã nguồn gốc</summary>

```c
#include "vera.h"

VERA_FN(fn_02)
{
    uint64_t h = 0xCBF29CE484222325ull;
    (void)arg; (void)out; (void)out_cap;
    for (size_t i = 0; i < len; i++) {
        h ^= in[i];
        OBF_GUARD(h, i, h *= 0x00000100000001B3ull);
        OBF_JUNK(h, len);
    }
    OBF_SPIN(h);
    return h;
}
```
</details>

<details><summary>recovered_c của model</summary>

```c
uint64_t fn_02(const uint8_t *in, size_t len, uint64_t arg, uint8_t *out, size_t out_cap) {
  uint64_t crc = 0xcbf29ce484222325;
  if (len != 0) {
    for (size_t i = 0; i < len; i++) {
      crc = (crc ^ in[i]) * 0x100000001b3;
    }
  }
  return crc;
}
```
</details>

### opt/fn_08 — near-miss của CRC-32 (near_miss)

- Model: algorithm = `Implements CRC-16/XMODEM.`, tên đề xuất = `fn_08`
- V1: compiled = True, FEPR = 1.0
- `verified` (IO) [IO] “Returns 0 when len == 0.” → "đúng trên 1 vector thỏa điều kiện"
- `verified` (SIDE) [SIDE] “Does not write to out.” → "không vector nào ghi out"
- `contradicted` (V1b) [ALG] “The function implements CRC-16/XMODEM.” → {"vector": "v01", "tag": "len1", "expected_ret": "0x00000000a22615fe", "oracle_ret": "0x0000000000009f59"}

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

### plain/fn_02 — FNV-1a (64-bit) (classic)

- Model: algorithm = `Implements CRC-32.`, tên đề xuất = `fn_02`
- V1: compiled = True, FEPR = 1.0
- `verified` (SIDE) [SIDE] “Does not write to out.” → "không vector nào ghi out"
- `contradicted` (V1b) [ALG] “The function implements CRC-32.” → {"vector": "v00", "tag": "len0", "expected_ret": "0xcbf29ce484222325", "oracle_ret": "0x0000000000000000"}

<details><summary>Pseudocode model đã đọc</summary>

```c
uint64_t fn_02(uint8_t *in,size_t len,uint64_t arg,uint8_t *out,size_t out_cap)

{
  size_t out_cap_local;
  uint8_t *out_local;
  uint64_t arg_local;
  size_t len_local;
  uint8_t *in_local;
  uint64_t h;
  size_t i;
  
  h = 0xcbf29ce484222325;
  for (i = 0; i < len; i = i + 1) {
    h = (h ^ in[i]) * 0x100000001b3;
  }
  return h;
}
```
</details>

<details><summary>Mã nguồn gốc</summary>

```c
#include "vera.h"

VERA_FN(fn_02)
{
    uint64_t h = 0xCBF29CE484222325ull;
    (void)arg; (void)out; (void)out_cap;
    for (size_t i = 0; i < len; i++) {
        h ^= in[i];
        OBF_GUARD(h, i, h *= 0x00000100000001B3ull);
        OBF_JUNK(h, len);
    }
    OBF_SPIN(h);
    return h;
}
```
</details>

<details><summary>recovered_c của model</summary>

```c
uint64_t fn_02(const uint8_t *in, size_t len, uint64_t arg, uint8_t *out, size_t out_cap) {
  uint64_t h = 0xcbf29ce484222325;
  for (size_t i = 0; i < len; i++) {
    h = (h ^ in[i]) * 0x100000001b3;
  }
  return h;
}
```
</details>

### plain/fn_03 — Adler-32 (classic)

- Model: algorithm = `unknown`, tên đề xuất = `fn_03`
- V1: compiled = True, FEPR = 1.0
- `verified` (SIDE) [SIDE] “Does not write to out.” → "không vector nào ghi out"
- `contradicted` (IO) [IO] “Returns 0xFFFFFFFFFFFFFFFF when len is 0.” → {"vector": "v00", "tag": "len0", "observed": "ret 0x0000000000000001"}

<details><summary>Pseudocode model đã đọc</summary>

```c
uint64_t fn_03(uint8_t *in,size_t len,uint64_t arg,uint8_t *out,size_t out_cap)

{
  size_t out_cap_local;
  uint8_t *out_local;
  uint64_t arg_local;
  size_t len_local;
  uint8_t *in_local;
  uint32_t a;
  uint32_t b;
  size_t i;
  
  a = 1;
  b = 0;
  for (i = 0; i < len; i = i + 1) {
    a = (in[i] + a) % 0xfff1;
    b = (b + a) % 0xfff1;
  }
  return (ulong)a | (ulong)b << 0x10;
}
```
</details>

<details><summary>Mã nguồn gốc</summary>

```c
#include "vera.h"

VERA_FN(fn_03)
{
    uint32_t a = 1u, b = 0u;
    (void)arg; (void)out; (void)out_cap;
    for (size_t i = 0; i < len; i++) {
        OBF_GUARD(a, i, a = (a + in[i]) % 65521u);
        OBF_JUNK(b, len);
        b = (b + a) % 65521u;
    }
    OBF_SPIN(a);
    return ((uint64_t)b << 16) | a;
}
```
</details>

<details><summary>recovered_c của model</summary>

```c
uint64_t fn_03(const uint8_t *in, size_t len, uint64_t arg, uint8_t *out, size_t out_cap) {
  uint32_t a = 1;
  uint32_t b = 0;
  for (size_t i = 0; i < len; i++) {
    a = (in[i] + a) % 0xfff1;
    b = (b + a) % 0xfff1;
  }
  return (uint64_t)a | (uint64_t)b << 0x10;
}
```
</details>

### plain/fn_04 — djb2 (classic)

- Model: algorithm = `unknown`, tên đề xuất = `fn_04`
- V1: compiled = True, FEPR = 1.0
- `verified` (SIDE) [SIDE] “Does not write to out.” → "không vector nào ghi out"
- `contradicted` (IO) [IO] “Returns 0xFFFFFFFFFFFFFFFF when len == 0.” → {"vector": "v00", "tag": "len0", "observed": "ret 0x0000000000001505"}

<details><summary>Pseudocode model đã đọc</summary>

```c
uint64_t fn_04(uint8_t *in,size_t len,uint64_t arg,uint8_t *out,size_t out_cap)

{
  size_t out_cap_local;
  uint8_t *out_local;
  uint64_t arg_local;
  size_t len_local;
  uint8_t *in_local;
  uint32_t h;
  size_t i;
  
  h = 0x1505;
  for (i = 0; i < len; i = i + 1) {
    h = (uint)in[i] + h * 0x21;
  }
  return (ulong)h;
}
```
</details>

<details><summary>Mã nguồn gốc</summary>

```c
#include "vera.h"

VERA_FN(fn_04)
{
    uint32_t h = 5381u;
    (void)arg; (void)out; (void)out_cap;
    OBF_SPIN(h);
    for (size_t i = 0; i < len; i++) {
        OBF_GUARD(h, i, h = ((h << 5) + h) + in[i]);
        OBF_JUNK(h, len);
    }
    return h;
}
```
</details>

<details><summary>recovered_c của model</summary>

```c
uint64_t fn_04(const uint8_t *in, size_t len, uint64_t arg, uint8_t *out, size_t out_cap) {
  uint32_t h = 0x1505;
  for (size_t i = 0; i < len; i++) {
    h = (uint)in[i] + h * 0x21;
  }
  return (uint64_t)h;
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

### plain/fn_09 — near-miss của FNV-1a (64-bit) (near_miss)

- Model: algorithm = `Implements CRC-32.`, tên đề xuất = `fn_09`
- V1: compiled = True, FEPR = 1.0
- `verified` (SIDE) [SIDE] “Does not write to out.” → "không vector nào ghi out"
- `contradicted` (V1b) [ALG] “The function implements CRC-32.” → {"vector": "v00", "tag": "len0", "expected_ret": "0xcbf29ce484222325", "oracle_ret": "0x0000000000000000"}

<details><summary>Pseudocode model đã đọc</summary>

```c
uint64_t fn_09(uint8_t *in,size_t len,uint64_t arg,uint8_t *out,size_t out_cap)

{
  size_t out_cap_local;
  uint8_t *out_local;
  uint64_t arg_local;
  size_t len_local;
  uint8_t *in_local;
  uint64_t h;
  size_t i;
  
  h = 0xcbf29ce484222325;
  for (i = 0; i < len; i = i + 1) {
    h = (h ^ in[i]) * 0x100000001b5;
  }
  return h;
}
```
</details>

<details><summary>Mã nguồn gốc</summary>

```c
#include "vera.h"

VERA_FN(fn_09)
{
    uint64_t h = 0xCBF29CE484222325ull;
    (void)arg; (void)out; (void)out_cap;
    for (size_t i = 0; i < len; i++) {
        h ^= in[i];
        OBF_GUARD(h, i, h *= 0x00000100000001B5ull);
        OBF_JUNK(h, len);
    }
    OBF_SPIN(h);
    return h;
}
```
</details>

<details><summary>recovered_c của model</summary>

```c
uint64_t fn_09(const uint8_t *in, size_t len, uint64_t arg, uint8_t *out, size_t out_cap) {
  uint64_t h = 0xcbf29ce484222325;
  for (size_t i = 0; i < len; i++) {
    h = (h ^ in[i]) * 0x100000001b5;
  }
  return h;
}
```
</details>

### plain/fn_13 — near-miss của RC4 (near_miss)

- Model: algorithm = `RC4`, tên đề xuất = `fn_13`
- V1: compiled = True, FEPR = 1.0
- `verified` (IO) [IO] “Returns VERA_ERR when the output capacity is insufficient.” → "đúng trên 3 vector thỏa điều kiện"
- `verified` (SIDE) [SIDE] “Writes the encrypted data to the output buffer 'out'.” → "hàm có ghi out trên vector hợp lệ"
- `contradicted` (V1b) [ALG] “The function implements RC4.” → {"vector": "v01", "tag": "len1", "expected_ret": "0x0000000000000001", "oracle_ret": "0x0000000000000001"}

<details><summary>Pseudocode model đã đọc</summary>

```c
uint64_t fn_13(uint8_t *in,size_t len,uint64_t arg,uint8_t *out,size_t out_cap)

{
  uint8_t uVar1;
  long lVar2;
  long in_FS_OFFSET;
  size_t out_cap_local;
  uint8_t *out_local;
  uint64_t arg_local;
  size_t len_local;
  uint8_t *in_local;
  uint8_t t;
  uint i;
  uint j;
  size_t n;
  uint8_t k [8];
  uint8_t s [256];
  
  lVar2 = *(long *)(in_FS_OFFSET + 0x28);
  j = 0;
  if (out_cap < len) {
    len = 0xffffffffffffffff;
  }
  else {
    for (i = 0; i < 8; i = i + 1) {
      k[i] = (uint8_t)(arg >> ((byte)(i << 3) & 0x3f));
    }
    for (i = 0; i < 0x100; i = i + 1) {
      s[i] = (uint8_t)i;
    }
...
```
</details>

<details><summary>Mã nguồn gốc</summary>

```c
#include "vera.h"

VERA_FN(fn_13)
{
    uint8_t s[256], k[8], t;
    unsigned i, j = 0;
    if (out_cap < len)
        return VERA_ERR;
    for (i = 0; i < 8; i++)
        k[i] = (uint8_t)(arg >> (8 * i));
    for (i = 0; i < 256; i++)
        s[i] = (uint8_t)i;
    for (i = 0; i < 256; i++) {
        OBF_GUARD(j, i, j = (j + s[i] + (k[i & 7] ^ i)) & 0xFFu);
        t = s[i]; s[i] = s[j]; s[j] = t;
    }
    i = j = 0;
    for (size_t n = 0; n < len; n++) {
        i = (i + 1) & 0xFFu;
        j = (j + s[i]) & 0xFFu;
        OBF_JUNK(j, n + len);
        t = s[i]; s[i] = s[j]; s[j] = t;
        out[n] = in[n] ^ s[(s[i] + s[j]) & 0xFFu];
    }
    return len;
}
```
</details>

<details><summary>recovered_c của model</summary>

```c
uint64_t fn_13(const uint8_t *in, size_t len, uint64_t arg, uint8_t *out, size_t out_cap) {
  if (out_cap < len) {
    return VERA_ERR;
  }

  uint8_t k[8];
  uint8_t s[256];
  uint8_t j = 0;
  uint8_t i = 0;
  uint8_t t;

  for (size_t i = 0; i < 8; i++) {
    k[i] = (uint8_t)(arg >> ((byte)(i << 3) & 0x3f));
  }

  for (size_t i = 0; i < 0x100; i++) {
    s[i] = (uint8_t)i;
  }

  for (size_t i = 0; i < 0x100; i++) {
    j = (k[i & 7] ^ i) + s[i] + j & 0xff;
    t = s[i];
    s[i] = s[j];
    s[j] = t;
  }

  j = 0;
  for (size_t n = 0; n < len; n++) {
    i = (i + 1) & 0xff;
    j = (j + s[i]) & 0xff;
...
```
</details>

## C. Giải thích sạch nhưng mã khôi phục sai (E2)

### obf/fn_02 — FNV-1a (64-bit) (classic)

- Model: algorithm = `unknown`, tên đề xuất = `fn_02`
- V1: compiled = False, FEPR = 0.0
- `verified` (SIDE) [SIDE] “Does not write to out.” → "không vector nào ghi out"

<details><summary>Pseudocode model đã đọc</summary>

```c
ulong fn_02(long param_1,long param_2)

{
  uint uVar1;
  ulong uVar2;
  long lVar3;
  ulong uVar4;
  
  uVar2 = 0xcbf29ce484222325;
  if (param_2 != 0) {
    lVar3 = 0;
    uVar4 = 0;
    do {
      uVar2 = *(byte *)(param_1 + lVar3) ^ uVar2;
      uVar1 = (uint)lVar3 | 1;
      if (((uVar1 * uVar1 & 7) == 1) && (DAT_00104008 == 0x3c71)) {
        uVar2 = uVar2 * 0x100000001b3;
      }
      else {
        uVar2 = uVar2 + 0x51e3 ^ uVar4;
      }
      if (((((int)param_2 + 1) * (int)param_2 & 1U) != 0) || (DAT_00104010 != 0)) {
        uVar2 = (ulong)DAT_00104008 + (uVar2 ^ param_2 << 7) * 0x2d6b;
        uVar2 = uVar2 >> 0xb ^ uVar2;
      }
      lVar3 = lVar3 + 1;
      uVar4 = uVar4 + 0x1f9;
    } while (param_2 != lVar3);
  }
  if (DAT_00104010 != 0) {
...
```
</details>

<details><summary>Mã nguồn gốc</summary>

```c
#include "vera.h"

VERA_FN(fn_02)
{
    uint64_t h = 0xCBF29CE484222325ull;
    (void)arg; (void)out; (void)out_cap;
    for (size_t i = 0; i < len; i++) {
        h ^= in[i];
        OBF_GUARD(h, i, h *= 0x00000100000001B3ull);
        OBF_JUNK(h, len);
    }
    OBF_SPIN(h);
    return h;
}
```
</details>

<details><summary>recovered_c của model</summary>

```c
uint64_t fn_02(const uint8_t *in, size_t len, uint64_t arg, uint8_t *out, size_t out_cap) {
  uint uVar1;
  ulong uVar2;
  long lVar3;
  ulong uVar4;

  uVar2 = 0xcbf29ce484222325;
  if (len != 0) {
    lVar3 = 0;
    uVar4 = 0;
    do {
      uVar2 = *(byte *)(in + lVar3) ^ uVar2;
      uVar1 = (uint)lVar3 | 1;
      if (((uVar1 * uVar1 & 7) == 1) && (DAT_00104008 == 0x3c71)) {
        uVar2 = uVar2 * 0x100000001b3;
      } else {
        uVar2 = uVar2 + 0x51e3 ^ uVar4;
      }
      if (((((int)len + 1) * (int)len & 1U) != 0) || (DAT_00104010 != 0)) {
        uVar2 = (ulong)DAT_00104008 + (uVar2 ^ len << 7) * 0x2d6b;
        uVar2 = uVar2 >> 0xb ^ uVar2;
      }
      lVar3 = lVar3 + 1;
      uVar4 = uVar4 + 0x1f9;
    } while (len != lVar3);
  }
  if (DAT_00104010 != 0) {
    uVar4 = 0;
    do {
      uVar2 = uVar2 * 8 ^ uVar2 >> 5 ^ uVar4;
...
```
</details>

### obf/fn_04 — djb2 (classic)

- Model: algorithm = `unknown`, tên đề xuất = `fn_04`
- V1: compiled = True, FEPR = 0.0

<details><summary>Pseudocode model đã đọc</summary>

```c
void fn_04(undefined8 param_1,long param_2)

{
  long lVar1;
  uint uVar2;
  
  if (DAT_00104010 != 0) {
    uVar2 = 0;
    do {
      uVar2 = uVar2 + 1;
    } while (uVar2 < DAT_00104010);
  }
  if (param_2 != 0) {
    lVar1 = 0;
    do {
      lVar1 = lVar1 + 1;
    } while (param_2 != lVar1);
  }
  return;
}
```
</details>

<details><summary>Mã nguồn gốc</summary>

```c
#include "vera.h"

VERA_FN(fn_04)
{
    uint32_t h = 5381u;
    (void)arg; (void)out; (void)out_cap;
    OBF_SPIN(h);
    for (size_t i = 0; i < len; i++) {
        OBF_GUARD(h, i, h = ((h << 5) + h) + in[i]);
        OBF_JUNK(h, len);
    }
    return h;
}
```
</details>

<details><summary>recovered_c của model</summary>

```c
void fn_04(uint8_t *in, size_t len, uint64_t arg, uint8_t *out, size_t out_cap) { return VERA_ERR; }
```
</details>

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

### obf/fn_06 — RC4 (classic)

- Model: algorithm = `unknown`, tên đề xuất = `fn_06`
- V1: compiled = False, FEPR = 0.0

<details><summary>Pseudocode model đã đọc</summary>

```c
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

ulong fn_06(long param_1,ulong param_2,ulong param_3,long param_4,ulong param_5)

{
  byte bVar1;
  short sVar2;
  short sVar3;
  short sVar4;
  short sVar5;
  short sVar6;
  short sVar7;
  short sVar8;
  short sVar9;
  short sVar10;
  short sVar11;
  short sVar12;
  short sVar13;
  short sVar14;
  short sVar15;
  short sVar16;
  short sVar17;
  undefined1 auVar18 [16];
  undefined1 auVar19 [16];
  undefined1 auVar20 [16];
  undefined1 auVar21 [16];
  byte *pbVar22;
  byte *pbVar23;
  byte bVar24;
  uint uVar25;
...
```
</details>

<details><summary>Mã nguồn gốc</summary>

```c
#include "vera.h"

VERA_FN(fn_06)
{
    uint8_t s[256], k[8], t;
    unsigned i, j = 0;
    if (out_cap < len)
        return VERA_ERR;
    for (i = 0; i < 8; i++)
        k[i] = (uint8_t)(arg >> (8 * i));
    for (i = 0; i < 256; i++)
        s[i] = (uint8_t)i;
    for (i = 0; i < 256; i++) {
        OBF_GUARD(j, i, j = (j + s[i] + k[i & 7]) & 0xFFu);
        t = s[i]; s[i] = s[j]; s[j] = t;
    }
    i = j = 0;
    for (size_t n = 0; n < len; n++) {
        i = (i + 1) & 0xFFu;
        j = (j + s[i]) & 0xFFu;
        OBF_JUNK(j, n + len);
        t = s[i]; s[i] = s[j]; s[j] = t;
        out[n] = in[n] ^ s[(s[i] + s[j]) & 0xFFu];
    }
    return len;
}
```
</details>

<details><summary>recovered_c của model</summary>

```c
uint64_t fn_06(const uint8_t *in, size_t len, uint64_t arg, uint8_t *out, size_t out_cap) {
  if (len > out_cap) {
    return VERA_ERR;
  }

  uint8_t local_130[8];
  uint8_t local_128[264];

  for (size_t i = 0; i < len; i++) {
    local_130[i % 8] = (arg >> (i % 64)) & 0x3f;
    local_128[i] = in[i];
  }

  uint64_t uVar26 = 0xffffffffffffffff;
  uint64_t uVar28 = 0;
  uint64_t uVar31 = 0;

  for (size_t i = 0; i < len; i++) {
    uint8_t bVar24 = local_130[uVar28 & 7] + local_128[i] + (uint)uVar26 & 0xff;
    uVar26 = (uint)bVar24;
    uVar28 = (uVar28 + 1) % 256;
    uVar31 = (uVar31 + 0x1f9) % 256;
    out[i] = local_128[uVar26];
    local_128[uVar26] = bVar24;
  }

  if (len > 0) {
    uint64_t uVar27 = 0;
    uint64_t uVar29 = len;

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

### obf/fn_09 — near-miss của FNV-1a (64-bit) (near_miss)

- Model: algorithm = `unknown`, tên đề xuất = `fn_09`
- V1: compiled = False, FEPR = 0.0
- `verified` (SIDE) [SIDE] “The function does not write to out.” → "không vector nào ghi out"

<details><summary>Pseudocode model đã đọc</summary>

```c
ulong fn_09(long param_1,long param_2)

{
  uint uVar1;
  ulong uVar2;
  long lVar3;
  ulong uVar4;
  
  uVar2 = 0xcbf29ce484222325;
  if (param_2 != 0) {
    lVar3 = 0;
    uVar4 = 0;
    do {
      uVar2 = *(byte *)(param_1 + lVar3) ^ uVar2;
      uVar1 = (uint)lVar3 | 1;
      if (((uVar1 * uVar1 & 7) == 1) && (DAT_00104008 == 0x3c71)) {
        uVar2 = uVar2 * 0x100000001b5;
      }
      else {
        uVar2 = uVar2 + 0x51e3 ^ uVar4;
      }
      if (((((int)param_2 + 1) * (int)param_2 & 1U) != 0) || (DAT_00104010 != 0)) {
        uVar2 = (ulong)DAT_00104008 + (uVar2 ^ param_2 << 7) * 0x2d6b;
        uVar2 = uVar2 >> 0xb ^ uVar2;
      }
      lVar3 = lVar3 + 1;
      uVar4 = uVar4 + 0x1f9;
    } while (param_2 != lVar3);
  }
  if (DAT_00104010 != 0) {
...
```
</details>

<details><summary>Mã nguồn gốc</summary>

```c
#include "vera.h"

VERA_FN(fn_09)
{
    uint64_t h = 0xCBF29CE484222325ull;
    (void)arg; (void)out; (void)out_cap;
    for (size_t i = 0; i < len; i++) {
        h ^= in[i];
        OBF_GUARD(h, i, h *= 0x00000100000001B5ull);
        OBF_JUNK(h, len);
    }
    OBF_SPIN(h);
    return h;
}
```
</details>

<details><summary>recovered_c của model</summary>

```c
uint64_t fn_09(const uint8_t *in, size_t len, uint64_t arg, uint8_t *out, size_t out_cap) {
  uint uVar1;
  ulong uVar2;
  long lVar3;
  ulong uVar4;

  uVar2 = 0xcbf29ce484222325;
  if (len != 0) {
    lVar3 = 0;
    uVar4 = 0;
    do {
      uVar2 = *(byte *)(in + lVar3) ^ uVar2;
      uVar1 = (uint)lVar3 | 1;
      if (((uVar1 * uVar1 & 7) == 1) && (DAT_00104008 == 0x3c71)) {
        uVar2 = uVar2 * 0x100000001b5;
      }
      else {
        uVar2 = uVar2 + 0x51e3 ^ uVar4;
      }
      if (((((int)len + 1) * (int)len & 1U) != 0) || (DAT_00104010 != 0)) {
        uVar2 = (ulong)DAT_00104008 + (uVar2 ^ len << 7) * 0x2d6b;
        uVar2 = uVar2 >> 0xb ^ uVar2;
      }
      lVar3 = lVar3 + 1;
      uVar4 = uVar4 + 0x1f9;
    } while (len != lVar3);
  }
  if (DAT_00104010 != 0) {
    uVar4 = 0;
    do {
...
```
</details>

### obf/fn_11 — near-miss của djb2 (near_miss)

- Model: algorithm = `unknown`, tên đề xuất = `fn_11`
- V1: compiled = True, FEPR = 0.0

<details><summary>Pseudocode model đã đọc</summary>

```c
void fn_11(undefined8 param_1,long param_2)

{
  long lVar1;
  uint uVar2;
  
  if (DAT_00104010 != 0) {
    uVar2 = 0;
    do {
      uVar2 = uVar2 + 1;
    } while (uVar2 < DAT_00104010);
  }
  if (param_2 != 0) {
    lVar1 = 0;
    do {
      lVar1 = lVar1 + 1;
    } while (param_2 != lVar1);
  }
  return;
}
```
</details>

<details><summary>Mã nguồn gốc</summary>

```c
#include "vera.h"

VERA_FN(fn_11)
{
    uint32_t h = 7477u;
    (void)arg; (void)out; (void)out_cap;
    OBF_SPIN(h);
    for (size_t i = 0; i < len; i++) {
        OBF_GUARD(h, i, h = h * 41u + in[i]);
        OBF_JUNK(h, len);
    }
    return h;
}
```
</details>

<details><summary>recovered_c của model</summary>

```c
void fn_11(uint8_t *in, size_t len, uint64_t arg, uint8_t *out, size_t out_cap) { return VERA_ERR; }
```
</details>

### obf/fn_17 — tự thiết kế: parser TLV (custom)

- Model: algorithm = `unknown`, tên đề xuất = `fn_17`
- V1: compiled = False, FEPR = 0.0

<details><summary>Pseudocode model đã đọc</summary>

```c
ulong fn_17(long param_1,ulong param_2,undefined8 param_3,long param_4,ulong param_5)

{
  uint uVar1;
  int iVar2;
  ulong uVar3;
  ulong uVar4;
  ulong uVar5;
  ulong uVar6;
  ulong uVar7;
  
  if (param_2 == 0) {
    return 0;
  }
  uVar4 = 0;
  uVar5 = 0;
  uVar7 = 0;
  do {
    if (*(char *)(param_1 + uVar7) == '\0') break;
    if (param_2 < uVar7 + 2) {
      return 0xffffffffffffffff;
    }
    uVar6 = (ulong)*(byte *)(param_1 + 1 + uVar7);
    uVar3 = uVar7 + 2 + uVar6;
    if (param_2 < uVar3) {
      return 0xffffffffffffffff;
    }
    iVar2 = (int)(uVar7 + uVar5);
    if ((((iVar2 + 1) * iVar2 & 1U) != 0) || (DAT_00104010 != 0)) {
      uVar4 = ((uVar7 + uVar5) * 0x80 ^ uVar4) * 0x2d6b + (ulong)DAT_00104008;
...
```
</details>

<details><summary>Mã nguồn gốc</summary>

```c
#include "vera.h"

/*
 * Bản ghi: [type:1][n:1][value:n]. type = 0x00 là kết thúc (phần sau bị bỏ qua).
 * Thành công: trả (số bản ghi << 32) | tổng số byte value; out nhận type của từng bản ghi.
 * Bản ghi bị cắt cụt, hoặc out_cap nhỏ hơn số bản ghi: trả VERA_ERR, không ghi out.
 */
VERA_FN(fn_17)
{
    size_t i = 0, cnt = 0, total = 0;
    (void)arg;
    while (i < len && in[i] != 0x00) {
        if (i + 2 > len || i + 2 + in[i + 1] > len)
            return VERA_ERR;
        OBF_JUNK(total, i + cnt);
        total += in[i + 1];
        cnt++;
        i += 2 + (size_t)in[i + 1];
    }
    if (out_cap < cnt)
        return VERA_ERR;
    i = 0;
    for (size_t c = 0; c < cnt; c++) {
        OBF_GUARD(i, c + len, out[c] = in[i]);
        i += 2 + (size_t)in[i + 1];
    }
    return ((uint64_t)cnt << 32) | (uint64_t)total;
}
```
</details>

<details><summary>recovered_c của model</summary>

```c
uint64_t fn_17(const uint8_t *in, size_t len, uint64_t arg, uint8_t *out, size_t out_cap) {
  uint uVar1;
  int iVar2;
  uint64_t uVar3;
  uint64_t uVar4;
  uint64_t uVar5;
  uint64_t uVar6;
  uint64_t uVar7;

  if (len == 0) {
    return 0;
  }
  uVar4 = 0;
  uVar5 = 0;
  uVar7 = 0;
  do {
    if (*(char *)(in + uVar7) == '\0') break;
    if (len < uVar7 + 2) {
      return 0xffffffffffffffff;
    }
    uVar6 = (uint)*(byte *)(in + 1 + uVar7);
    uVar3 = uVar7 + 2 + uVar6;
    if (len < uVar3) {
      return 0xffffffffffffffff;
    }
    iVar2 = (int)(uVar7 + uVar5);
    if ((((iVar2 + 1) * iVar2 & 1U) != 0) || (DAT_00104010 != 0)) {
      uVar4 = ((uVar7 + uVar5) * 0x80 ^ uVar4) * 0x2d6b + (uint)DAT_00104008;
      uVar4 = uVar4 >> 0xb ^ uVar4;
    }
...
```
</details>

## D. Claim IO/SIDE bị vector bác bỏ

- obf/fn_01: `contradicted` (SIDE) [SIDE] “The function writes to out[0..len-1].” → {"vector": "v00", "observed": "không vector hợp lệ nào ghi out"}
- obf/fn_03: `contradicted` (SIDE) [SIDE] “The function writes to out[0..15].” → {"vector": "v00", "observed": "không vector hợp lệ nào ghi out"}
- obf/fn_07: `contradicted` (IO) [IO] “Returns 0xFFFFFFFFFFFFFFFF when the input length is less than 3.” → {"vector": "v00", "tag": "len0", "observed": "ret 0x0000000000000000"}
- obf/fn_10: `contradicted` (SIDE) [SIDE] “The function writes to out[0..15].” → {"vector": "v00", "observed": "không vector hợp lệ nào ghi out"}
- obf/fn_12: `contradicted` (IO) [IO] “Returns 8 when the function completes successfully.” → {"vector": "v00", "tag": "len0", "observed": "ret 0xffffffffffffffff"}
- obf/fn_14: `contradicted` (IO) [IO] “Returns 0xFFFFFFFFFFFFFFFF when the input length is less than 3.” → {"vector": "v00", "tag": "len0", "observed": "ret 0x0000000000000000"}
- obf/fn_14: `contradicted` (IO) [IO] “Returns the length of the output when the input length is 1.” → {"vector": "v01", "tag": "len1", "observed": "ret 0x0000000000000004"}
- obf/fn_14: `contradicted` (IO) [IO] “Returns the length of the output when the input length is 2.” → {"vector": "v45", "tag": "rand45", "observed": "ret 0x0000000000000004"}
- obf/fn_15: `contradicted` (IO) [IO] “Returns 0xffffffffffffffff when out_cap < len.” → {"vector": "v10", "tag": "cap_half", "observed": "ret 0x0000000000000002"}
- obf/fn_16: `contradicted` (SIDE) [SIDE] “The function writes to out[0..3].” → {"vector": "v00", "observed": "không vector hợp lệ nào ghi out"}
- opt/fn_03: `contradicted` (SIDE) [SIDE] “Writes the computed checksum to out[0..1].” → {"vector": "v00", "observed": "không vector hợp lệ nào ghi out"}
- opt/fn_10: `contradicted` (SIDE) [SIDE] “Writes the computed checksum to out[0..1].” → {"vector": "v00", "observed": "không vector hợp lệ nào ghi out"}
- opt/fn_20: `contradicted` (SIDE) [SIDE] “Does not write to out if param_2 < 8.” → {"vector": "v01", "tag": "len1", "observed": "hàm có ghi out"}
- plain/fn_03: `contradicted` (IO) [IO] “Returns 0xFFFFFFFFFFFFFFFF when len is 0.” → {"vector": "v00", "tag": "len0", "observed": "ret 0x0000000000000001"}
- plain/fn_04: `contradicted` (IO) [IO] “Returns 0xFFFFFFFFFFFFFFFF when len == 0.” → {"vector": "v00", "tag": "len0", "observed": "ret 0x0000000000001505"}
- plain/fn_08: `contradicted` (IO) [IO] “Returns 0xFFFFFFFFFFFFFFFF when len == 0.” → {"vector": "v00", "tag": "len0", "observed": "ret 0x0000000000000000"}
- plain/fn_10: `contradicted` (IO) [IO] “Returns 0xFFFFFFFFFFFFFFFF when len is 0.” → {"vector": "v00", "tag": "len0", "observed": "ret 0x0000000000000001"}
- plain/fn_11: `contradicted` (IO) [IO] “Returns 0xFFFFFFFFFFFFFFFF when len == 0.” → {"vector": "v00", "tag": "len0", "observed": "ret 0x0000000000001d35"}
