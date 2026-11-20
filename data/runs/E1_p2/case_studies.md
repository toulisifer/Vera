# Ứng viên case study — E1_p2

## A. Gán nhầm thuật toán (V1b bác bỏ claim ALG)

## B. Giải thích có claim sai nhưng mã khôi phục đúng (E2)

### opt/fn_02 — FNV-1a (64-bit) (classic)

- Model: algorithm = `unknown`, tên đề xuất = `fn_02`
- V1: compiled = True, FEPR = 1.0
- `verified` (SIDE) [SIDE] “Does not modify the input array in any way.” → "in không đổi trên mọi vector (runner kiểm)"
- `contradicted` (SIDE) [SIDE] “Writes the hash value to the output parameter.” → {"vector": "v00", "observed": "không vector hợp lệ nào ghi out"}

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
  uint64_t hash = 0xcbf29ce484222325;
  if (len != 0) {
    for (size_t i = 0; i < len; i++) {
      hash = (hash ^ in[i]) * 0x100000001b3;
    }
  }
  return hash;
}
```
</details>

### opt/fn_08 — near-miss của CRC-32 (near_miss)

- Model: algorithm = `unknown`, tên đề xuất = `fn_08`
- V1: compiled = True, FEPR = 1.0
- `contradicted` (SIDE) [SIDE] “The function reads from the input buffer and writes the result to the output buffer.” → {"vector": "v00", "observed": "không vector hợp lệ nào ghi out"}

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
    uint32_t result = 0xffffffff;
    for (size_t i = 0; i < len; i++) {
      result ^= in[i];
      for (int j = 0; j < 8; j++) {
        result = -(result & 1) & 0xf7179bf5 ^ result >> 1;
      }
    }
    return ~result;
  }
  return 0;
}
```
</details>

### opt/fn_09 — near-miss của FNV-1a (64-bit) (near_miss)

- Model: algorithm = `unknown`, tên đề xuất = `fn_09`
- V1: compiled = True, FEPR = 1.0
- `verified` (SIDE) [SIDE] “Does not modify the input buffer.” → "in không đổi trên mọi vector (runner kiểm)"
- `contradicted` (SIDE) [SIDE] “Writes the hash value to the output buffer.” → {"vector": "v00", "observed": "không vector hợp lệ nào ghi out"}

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
  uint64_t hash = 0xcbf29ce484222325;
  if (len != 0) {
    for (size_t i = 0; i < len; i++) {
      hash = (hash ^ in[i]) * 0x100000001b5;
    }
  }
  return hash;
}
```
</details>

### opt/fn_10 — near-miss của Adler-32 (near_miss)

- Model: algorithm = `unknown`, tên đề xuất = `fn_10`
- V1: compiled = True, FEPR = 1.0
- `verified` (IO) [IO] “Returns 1 when the input length is 0.” → "đúng trên 1 vector thỏa điều kiện"
- `contradicted` (SIDE) [SIDE] “Writes the 2-byte checksum to out[0] and out[1] only.” → {"vector": "v00", "observed": "không vector hợp lệ nào ghi out"}

<details><summary>Pseudocode model đã đọc</summary>

```c
uint fn_10(byte *param_1,long param_2)

{
  byte bVar1;
  uint uVar2;
  uint uVar3;
  byte *pbVar4;
  
  if (param_2 != 0) {
    pbVar4 = param_1 + param_2;
    uVar2 = 0;
    uVar3 = 1;
    do {
      bVar1 = *param_1;
      param_1 = param_1 + 1;
      uVar3 = (uVar3 + bVar1) % 0xffef;
      uVar2 = (uVar2 + uVar3) % 0xffef;
    } while (pbVar4 != param_1);
    return uVar2 << 0x10 | uVar3;
  }
  return 1;
}
```
</details>

<details><summary>Mã nguồn gốc</summary>

```c
#include "vera.h"

VERA_FN(fn_10)
{
    uint32_t a = 1u, b = 0u;
    (void)arg; (void)out; (void)out_cap;
    for (size_t i = 0; i < len; i++) {
        OBF_GUARD(a, i, a = (a + in[i]) % 65519u);
        OBF_JUNK(b, len);
        b = (b + a) % 65519u;
    }
    OBF_SPIN(a);
    return ((uint64_t)b << 16) | a;
}
```
</details>

<details><summary>recovered_c của model</summary>

```c
uint64_t fn_10(const uint8_t *in, size_t len, uint64_t arg, uint8_t *out, size_t out_cap) {
  if (len != 0) {
    uint uVar2 = 0;
    uint uVar3 = 1;
    for (size_t i = 0; i < len; i++) {
      uint8_t bVar1 = in[i];
      uVar3 = (uVar3 + bVar1) % 0xffef;
      uVar2 = (uVar2 + uVar3) % 0xffef;
    }
    return ((uint64_t)uVar2 << 0x10) | uVar3;
  }
  return 1;
}
```
</details>

### opt/fn_16 — tự thiết kế: checksum cuộn (custom)

- Model: algorithm = `unknown`, tên đề xuất = `fn_16`
- V1: compiled = True, FEPR = 1.0
- `contradicted` (SIDE) [SIDE] “The function writes the checksum to the output buffer pointed to by param_3.” → {"vector": "v00", "observed": "không vector hợp lệ nào ghi out"}

<details><summary>Pseudocode model đã đọc</summary>

```c
uint fn_16(long param_1,long param_2,undefined8 param_3)

{
  byte *pbVar1;
  uint uVar2;
  int iVar3;
  long lVar4;
  
  uVar2 = (uint)((ulong)param_3 >> 0x20) ^ (uint)param_3;
  if (param_2 != 0) {
    lVar4 = 0;
    do {
      pbVar1 = (byte *)(param_1 + lVar4);
      iVar3 = (int)lVar4;
      lVar4 = lVar4 + 1;
      uVar2 = (uint)*pbVar1 * 0x9d + iVar3 + (uVar2 << 7 | uVar2 >> 0x19);
    } while (param_2 != lVar4);
  }
  uVar2 = (uVar2 >> 0xf ^ uVar2) * 0x3b9d;
  return uVar2 >> 0xd ^ uVar2;
}
```
</details>

<details><summary>Mã nguồn gốc</summary>

```c
#include "vera.h"

VERA_FN(fn_16)
{
    uint32_t h = (uint32_t)arg ^ (uint32_t)(arg >> 32);
    (void)out; (void)out_cap;
    for (size_t i = 0; i < len; i++) {
        OBF_JUNK(h, i + len);
        h = (h << 7) | (h >> 25);
        OBF_GUARD(h, i, h += (uint32_t)in[i] * 0x9Du + (uint32_t)i);
    }
    OBF_SPIN(h);
    h ^= h >> 15;
    h *= 0x3B9Du;
    h ^= h >> 13;
    return h;
}
```
</details>

<details><summary>recovered_c của model</summary>

```c
uint64_t fn_16(const uint8_t *in, size_t len, uint64_t arg, uint8_t *out, size_t out_cap) {
  uint uVar2;
  int iVar3;
  long lVar4;

  uVar2 = (uint)((ulong)arg >> 0x20) ^ (uint)arg;
  if (len != 0) {
    lVar4 = 0;
    do {
      uint8_t *pbVar1 = (uint8_t *)(in + lVar4);
      iVar3 = (int)lVar4;
      lVar4 = lVar4 + 1;
      uVar2 = (uint)*pbVar1 * 0x9d + iVar3 + (uVar2 << 7 | uVar2 >> 0x19);
    } while (len != lVar4);
  }
  uVar2 = (uVar2 >> 0xf ^ uVar2) * 0x3b9d;
  return uVar2 >> 0xd ^ uVar2;
}
```
</details>

### plain/fn_01 — CRC-32 (classic)

- Model: algorithm = `CRC-32`, tên đề xuất = `fn_01`
- V1: compiled = True, FEPR = 1.0
- `contradicted` (SIDE) [SIDE] “Writes the final checksum to the output buffer.” → {"vector": "v00", "observed": "không vector hợp lệ nào ghi out"}

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
  uint32_t h = 0xffffffff;
  for (size_t i = 0; i < len; i++) {
    h ^= in[i];
    for (uint8_t b = 0; b < 8; b++) {
      h = -(h & 1) & 0xedb88320 ^ h >> 1;
    }
  }
  return (uint64_t)~h;
}
```
</details>

### plain/fn_03 — Adler-32 (classic)

- Model: algorithm = `unknown`, tên đề xuất = `fn_03`
- V1: compiled = True, FEPR = 1.0
- `contradicted` (SIDE) [SIDE] “The function writes the computed checksum to the output buffer.” → {"vector": "v00", "observed": "không vector hợp lệ nào ghi out"}

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
  return (uint64_t)a | ((uint64_t)b << 0x10);
}
```
</details>

### plain/fn_16 — tự thiết kế: checksum cuộn (custom)

- Model: algorithm = `unknown`, tên đề xuất = `fn_16`
- V1: compiled = True, FEPR = 1.0
- `verified` (SIDE) [SIDE] “The function does not modify the input data.” → "in không đổi trên mọi vector (runner kiểm)"
- `contradicted` (SIDE) [SIDE] “The function writes the final hash value to the output buffer.” → {"vector": "v00", "observed": "không vector hợp lệ nào ghi out"}

<details><summary>Pseudocode model đã đọc</summary>

```c
uint64_t fn_16(uint8_t *in,size_t len,uint64_t arg,uint8_t *out,size_t out_cap)

{
  uint uVar1;
  size_t out_cap_local;
  uint8_t *out_local;
  uint64_t arg_local;
  size_t len_local;
  uint8_t *in_local;
  uint32_t h;
  size_t i;
  
  h = (uint)(arg >> 0x20) ^ (uint)arg;
  for (i = 0; i < len; i = i + 1) {
    h = (h << 7 | h >> 0x19) + (uint)in[i] * 0x9d + (int)i;
  }
  uVar1 = (h ^ h >> 0xf) * 0x3b9d;
  return (ulong)(uVar1 ^ uVar1 >> 0xd);
}
```
</details>

<details><summary>Mã nguồn gốc</summary>

```c
#include "vera.h"

VERA_FN(fn_16)
{
    uint32_t h = (uint32_t)arg ^ (uint32_t)(arg >> 32);
    (void)out; (void)out_cap;
    for (size_t i = 0; i < len; i++) {
        OBF_JUNK(h, i + len);
        h = (h << 7) | (h >> 25);
        OBF_GUARD(h, i, h += (uint32_t)in[i] * 0x9Du + (uint32_t)i);
    }
    OBF_SPIN(h);
    h ^= h >> 15;
    h *= 0x3B9Du;
    h ^= h >> 13;
    return h;
}
```
</details>

<details><summary>recovered_c của model</summary>

```c
uint64_t fn_16(const uint8_t *in, size_t len, uint64_t arg, uint8_t *out, size_t out_cap) {
  uint32_t h = (uint)(arg >> 0x20) ^ (uint)arg;
  for (size_t i = 0; i < len; i++) {
    h = (h << 7 | h >> 0x19) + (uint)in[i] * 0x9d + (int)i;
  }
  uint32_t uVar1 = (h ^ h >> 0xf) * 0x3b9d;
  return (uint64_t)(uVar1 ^ uVar1 >> 0xd);
}
```
</details>

## C. Giải thích sạch nhưng mã khôi phục sai (E2)

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
void fn_04(const uint8_t *in, size_t len, uint64_t arg, uint8_t *out, size_t out_cap) { return VERA_ERR; }
```
</details>

### obf/fn_05 — TEA (classic)

- Model: algorithm = `unknown`, tên đề xuất = `fn_05`
- V1: compiled = False, FEPR = 0.0
- `verified` (SIDE) [SIDE] “Writes the computed hash value to the output buffer.” → "hàm có ghi out trên vector hợp lệ"

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
  if (len < 0x18 || out_cap < 8) {
    return VERA_ERR;
  }

  uint uVar1, uVar2, uVar3;
  uint uVar4;
  int iVar5;
  uint uVar6;

  uVar6 = len * 0x1f9;
  uVar3 = (uint)arg;
  uVar2 = ((uint)arg >> 32);
  iVar5 = 0;

  do {
    uVar4 = len + 1;
    iVar5 = iVar5 - 0x61c88647;

    if ((((uint)len * (int)uVar4 & 1) != 0) || (DAT_00104010 != 0)) {
      uVar3 = ((uint)(len << 7) ^ uVar3) * 0x2d6b + DAT_00104008;
      uVar3 = uVar3 >> 0xb ^ uVar3;
    }

    uVar1 = (uint)len | 1;
    uVar3 = uVar3 + (uVar2 * 0x10 + in[0] ^ (uVar2 >> 5) + in[1] ^ iVar5 + uVar2);
    len = uVar4;

    if (((uVar1 * uVar1 & 7) != 1) || (DAT_00104008 != 0x3c71)) break;

...
```
</details>

### obf/fn_06 — RC4 (classic)

- Model: algorithm = `unknown`, tên đề xuất = `fn_06`
- V1: compiled = True, FEPR = 0.0
- `verified` (SIDE) [SIDE] “Writes the result to the output buffer.” → "hàm có ghi out trên vector hợp lệ"

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
  if (len == 0) {
    return VERA_ERR;
  }

  // Custom encryption algorithm
  for (size_t i = 0; i < len; i++) {
    out[i] = in[i]; // Placeholder for actual encryption logic
  }

  return arg;
}
```
</details>

### obf/fn_10 — near-miss của Adler-32 (near_miss)

- Model: algorithm = `unknown`, tên đề xuất = `fn_10`
- V1: compiled = False, FEPR = 0.0

<details><summary>Pseudocode model đã đọc</summary>

```c
ulong fn_10(long param_1,long param_2)

{
  uint uVar1;
  ulong uVar2;
  uint uVar3;
  ulong uVar4;
  long lVar5;
  uint uVar6;
  
  if (param_2 == 0) {
    uVar2 = 1;
    uVar4 = 0;
  }
  else {
    uVar4 = 0;
    uVar6 = 0;
    lVar5 = 0;
    uVar2 = 1;
    do {
      uVar3 = (uint)uVar4;
      uVar1 = (uint)lVar5 | 1;
      if (((uVar1 * uVar1 & 7) == 1) && (DAT_00104008 == 0x3c71)) {
        uVar1 = ((int)uVar2 + (uint)*(byte *)(param_1 + lVar5)) % 0xffef;
      }
      else {
        uVar1 = (int)uVar2 + 0x51e3U ^ uVar6;
      }
      uVar2 = (ulong)uVar1;
      if (((((int)param_2 + 1) * (int)param_2 & 1U) != 0) || (DAT_00104010 != 0)) {
...
```
</details>

<details><summary>Mã nguồn gốc</summary>

```c
#include "vera.h"

VERA_FN(fn_10)
{
    uint32_t a = 1u, b = 0u;
    (void)arg; (void)out; (void)out_cap;
    for (size_t i = 0; i < len; i++) {
        OBF_GUARD(a, i, a = (a + in[i]) % 65519u);
        OBF_JUNK(b, len);
        b = (b + a) % 65519u;
    }
    OBF_SPIN(a);
    return ((uint64_t)b << 16) | a;
}
```
</details>

<details><summary>recovered_c của model</summary>

```c
uint64_t fn_10(const uint8_t *in, size_t len, uint64_t arg, uint8_t *out, size_t out_cap) {
  uint uVar1;
  ulong uVar2;
  uint uVar3;
  ulong uVar4;
  long lVar5;
  uint uVar6;

  if (len == 0) {
    uVar2 = 1;
    uVar4 = 0;
  } else {
    uVar4 = 0;
    uVar6 = 0;
    lVar5 = 0;
    uVar2 = 1;
    do {
      uVar3 = (uint)uVar4;
      uVar1 = (uint)lVar5 | 1;
      if (((uVar1 * uVar1 & 7) == 1) && (DAT_00104008 == 0x3c71)) {
        uVar1 = ((int)uVar2 + (uint)*(byte *)(in + lVar5)) % 0xffef;
      } else {
        uVar1 = (int)uVar2 + 0x51e3U ^ uVar6;
      }
      uVar2 = (ulong)uVar1;
      if (((((int)len + 1) * (int)len & 1U) != 0) || (DAT_00104010 != 0)) {
        uVar3 = (uVar3 ^ (uint)(len << 7)) * 0x2d6b + DAT_00104008;
        uVar3 = uVar3 ^ uVar3 >> 0xb;
      }
      lVar5 = lVar5 + 1;
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

### obf/fn_12 — near-miss của TEA (near_miss)

- Model: algorithm = `unknown`, tên đề xuất = `fn_12`
- V1: compiled = False, FEPR = 0.0

<details><summary>Pseudocode model đã đọc</summary>

```c
undefined8 fn_12(uint *param_1,ulong param_2,undefined8 param_3,ulong *param_4,ulong param_5)

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
      iVar5 = iVar5 + -0x714851d1;
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

VERA_FN(fn_12)
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
        s += 0x8EB7AE2Fu;
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
uint64_t fn_12(const uint8_t *in, size_t len, uint64_t arg, uint8_t *out, size_t out_cap) {
  if ((len < 0x18) || (out_cap < 8)) {
    return VERA_ERR;
  }
  uint uVar1, uVar2, uVar3;
  uint uVar4;
  int iVar5;
  uint uVar6;
  uVar6 = (int)len * 0x1f9;
  uVar3 = *(uint *)in;
  uVar2 = *(uint *)(in + 4);
  iVar5 = 0;
  do {
    while( true ) {
      uVar4 = len + 1;
      iVar5 = iVar5 + -0x714851d1;
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
      if (iVar5 == -0x290a3a20) goto LAB_0010120c;
    }
    uVar2 = uVar2 + 0x51e3 ^ uVar6;
    uVar6 = uVar6 + 0x1f9;
...
```
</details>

### obf/fn_13 — near-miss của RC4 (near_miss)

- Model: algorithm = `unknown`, tên đề xuất = `fn_13`
- V1: compiled = False, FEPR = 0.0
- `verified` (SIDE) [SIDE] “Writes the encrypted data to the output buffer.” → "hàm có ghi out trên vector hợp lệ"

<details><summary>Pseudocode model đã đọc</summary>

```c
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

ulong fn_13(long param_1,ulong param_2,ulong param_3,long param_4,ulong param_5)

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
  if (len == 0) {
    return VERA_ERR;
  }

  uint8_t local_130[8];
  uint8_t local_128[256];

  // Initialize local_130
  for (size_t i = 0; i < 8; i++) {
    local_130[i] = (arg >> (i * 8)) & 0x3f;
  }

  // Perform some operations on local_128
  for (size_t i = 0; i < 256; i += 16) {
    // ... (omitted for brevity)
  }

  // Swap elements in in and out buffers
  for (size_t i = 0; i < len; i++) {
    uint8_t temp = in[i];
    out[i] = local_128[(temp + local_128[i]) % out_cap];
    in[i] = local_128[(temp + local_128[i]) % out_cap];
  }

  return arg;
}
```
</details>

### obf/fn_14 — near-miss của Base64 encode (near_miss)

- Model: algorithm = `unknown`, tên đề xuất = `fn_14`
- V1: compiled = True, FEPR = 0.08
- `verified` (SIDE) [SIDE] “Writes encoded data to the output buffer.” → "hàm có ghi out trên vector hợp lệ"

<details><summary>Pseudocode model đã đọc</summary>

```c
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
  if ((len + 2) / 3 << 2 > out_cap) {
    return VERA_ERR;
  }

  if (len < 3) {
    return 0;
  }

  size_t i = 0;
  while (i < len) {
    uint32_t value = 0;
    if (i + 2 < len) {
      value = (uint32_t)in[i + 2] << 16 | (uint32_t)in[i + 1] << 8 | (uint32_t)in[i];
      if (((((int)len + 1) * (int)len & 1U) != 0) || (arg != 0)) {
        value = ((uint)(len << 7) ^ value) * 0x2d6b + arg;
        value = value >> 0xb ^ value;
      }
      out[i / 3 * 2] = (uint16_t)("AfhmdLEr3GMxg2S/a91UZnTlHOI5KYzevFCwNQ+P4tWV7cpXRbDuykjJsoi6q80B"[value >> 0xc & 0x3f] << 8 | "AfhmdLEr3GMxg2S/a91UZnTlHOI5KYzevFCwNQ+P4tWV7cpXRbDuykjJsoi6q80B"[value >> 0x12 & 0x3f]);
      if (((i / 3 * 2 + 1) * (i / 3 * 2 + 1) & 7) == 1 && (arg == 0x3c71)) {
        out[i / 3 * 2 + 2] = "AfhmdLEr3GMxg2S/a91UZnTlHOI5KYzevFCwNQ+P4tWV7cpXRbDuykjJsoi6q80B"[value >> 6 & 0x3f];
      } else {
        out[i / 3 * 2 + 2] = out[i / 3 * 2 + 2] ^ (i / 3 * 2 + 2) ^ (i / 3 * 2 + 2);
      }
    } else if (i + 1 < len) {
      value = (uint32_t)in[i + 1] << 8;
      out[i / 3 * 2] = (uint16_t)("AfhmdLEr3GMxg2S/a91UZnTlHOI5KYzevFCwNQ+P4tWV7cpXRbDuykjJsoi6q80B"[(value | (uint32_t)in[i] << 0x10) >> 0xc & 0x3f] << 8 | "AfhmdLEr3GMxg2S/a91UZnTlHOI5KYzevFCwNQ+P4tWV7cpXRbDuykjJsoi6q80B"[in[i] >> 2]);
      out[i / 3 * 2 + 2] = "AfhmdLEr3GMxg2S/a91UZnTlHOI5KYzevFCwNQ+P4tWV7cpXRbDuykjJsoi6q80B"[(value & 0xf00) >> 6];
      out[i / 3 * 2 + 3] = 0x3d;
    } else {
...
```
</details>

## D. Claim IO/SIDE bị vector bác bỏ

- obf/fn_01: `contradicted` (SIDE) [SIDE] “Writes the hash value to out[0] and out[1] only.” → {"vector": "v00", "observed": "không vector hợp lệ nào ghi out"}
- obf/fn_02: `contradicted` (SIDE) [SIDE] “Writes the final hash value to the output buffer.” → {"vector": "v00", "observed": "không vector hợp lệ nào ghi out"}
- obf/fn_03: `contradicted` (SIDE) [SIDE] “Writes the hash value to out[0] and out[1] only.” → {"vector": "v00", "observed": "không vector hợp lệ nào ghi out"}
- obf/fn_07: `contradicted` (IO) [IO] “Returns 0xFFFFFFFFFFFFFFFF when the input length is less than 3.” → {"vector": "v00", "tag": "len0", "observed": "ret 0x0000000000000000"}
- obf/fn_08: `contradicted` (SIDE) [SIDE] “The function writes the hash value to the output buffer.” → {"vector": "v00", "observed": "không vector hợp lệ nào ghi out"}
- obf/fn_09: `contradicted` (SIDE) [SIDE] “Writes the final hash value to out[0] and out[1] only.” → {"vector": "v00", "observed": "không vector hợp lệ nào ghi out"}
- opt/fn_01: `contradicted` (SIDE) [SIDE] “Writes the 4-byte CRC-32 checksum to the output buffer.” → {"vector": "v00", "observed": "không vector hợp lệ nào ghi out"}
- opt/fn_02: `contradicted` (SIDE) [SIDE] “Writes the hash value to the output parameter.” → {"vector": "v00", "observed": "không vector hợp lệ nào ghi out"}
- opt/fn_03: `contradicted` (SIDE) [SIDE] “Writes the computed checksum to the output buffer.” → {"vector": "v00", "observed": "không vector hợp lệ nào ghi out"}
- opt/fn_06: `contradicted` (IO) [IO] “Returns 0xFFFFFFFFFFFFFFFF when the input length is less than 16 bytes.” → {"vector": "v00", "tag": "len0", "observed": "ret 0x0000000000000000"}
- opt/fn_08: `contradicted` (SIDE) [SIDE] “The function reads from the input buffer and writes the result to the output buffer.” → {"vector": "v00", "observed": "không vector hợp lệ nào ghi out"}
- opt/fn_09: `contradicted` (SIDE) [SIDE] “Writes the hash value to the output buffer.” → {"vector": "v00", "observed": "không vector hợp lệ nào ghi out"}
- opt/fn_10: `contradicted` (SIDE) [SIDE] “Writes the 2-byte checksum to out[0] and out[1] only.” → {"vector": "v00", "observed": "không vector hợp lệ nào ghi out"}
- opt/fn_14: `contradicted` (IO) [IO] “Returns 0 when len is less than 3.” → {"vector": "v01", "tag": "len1", "observed": "ret 0x0000000000000004"}
- opt/fn_16: `contradicted` (SIDE) [SIDE] “The function writes the checksum to the output buffer pointed to by param_3.” → {"vector": "v00", "observed": "không vector hợp lệ nào ghi out"}
- plain/fn_01: `contradicted` (SIDE) [SIDE] “Writes the final checksum to the output buffer.” → {"vector": "v00", "observed": "không vector hợp lệ nào ghi out"}
- plain/fn_03: `contradicted` (SIDE) [SIDE] “The function writes the computed checksum to the output buffer.” → {"vector": "v00", "observed": "không vector hợp lệ nào ghi out"}
- plain/fn_16: `contradicted` (SIDE) [SIDE] “The function writes the final hash value to the output buffer.” → {"vector": "v00", "observed": "không vector hợp lệ nào ghi out"}
- plain/fn_17: `contradicted` (IO) [IO] “The function returns 0xffffffffffffffff when the input length is less than 2.” → {"vector": "v00", "tag": "len0", "observed": "ret 0x0000000000000000"}
