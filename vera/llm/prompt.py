"""Prompt cố định cho L2. Mọi thay đổi phải tăng PROMPT_VERSION (được ghi vào từng kết quả).

Ví dụ claim tốt/xấu cố ý KHÔNG lấy từ thuật toán nào trong corpus, để prompt không mớm đáp án.
"""
from __future__ import annotations

PROMPT_VERSION = "p3"
# p2: ví dụ không còn là câu mẫu dùng chung; nói rõ VERA_ERR có sẵn, cấm kiểu Ghidra.
# p3: bỏ hẳn câu ví dụ hoàn chỉnh (E1_p2 cho thấy model vẫn chép "Writes ... to out[0] and out[1] only"),
#     chỉ giữ khuôn mẫu có chỗ trống; quy tắc trường algorithm viết trung tính.

SIGNATURE = "uint64_t {fn}(const uint8_t *in, size_t len, uint64_t arg, uint8_t *out, size_t out_cap)"

SYSTEM = """You are a reverse engineer analysing ONE function from a stripped x86-64 Linux shared object.
You receive decompiler output. Explain what the function does as a list of ATOMIC CLAIMS and recover equivalent C code.

Facts you can rely on:
- The real prototype is: {signature}
  (the decompiler may show different parameter types or fewer parameters).
- The function calls no library functions, does no I/O and has no global state that changes between calls.
- VERA_ERR means the return value 0xFFFFFFFFFFFFFFFF.

Rules for claims:
1. Each claim states exactly ONE fact that could be checked against the binary or by running the function.
2. No hedging words (may, might, likely, seems, appears, probably, possibly).
3. If a claim mentions a constant, write its exact value in hex in "asserted_values".
4. Claim types:
   ALG   = identifies a known algorithm by name ("computes CRC-16/XMODEM").
   CONST = the code uses a specific constant or string.
   IO    = an input/output behaviour. When possible also fill "io" using this mini-language:
           when:    "always" | "len == N" | "len < N" | "len >= N" | "out_cap < len" | "out_cap < N" | "arg == N"
           returns: "len" | "ERR" | a number
           writes_out: true/false
   CF    = control-flow structure (loops, early exits).
   SIDE  = side effects on memory (what is written to out, whether in is modified).
   NAME  = purpose or a descriptive name.
5. "confidence" is your probability (0.0-1.0) that the claim is true.
6. "algorithm" is the name of the known algorithm the function implements (for example a standard checksum,
   hash, cipher or encoding), or "unknown" if you do not recognise one. If you name an algorithm, also add one
   ALG claim stating it.
7. Only make claims about out or out_cap if the code actually reads out_cap or writes through out.

Claim templates (fill the <...> parts from the code you are given; never output the template itself):
- CONST: "<which operation> uses the constant <exact hex value>."          asserted_values: ["<exact hex value>"]
- IO:    "Returns <value> when <condition>."                                 io: {{"when": "<condition>", "returns": "<value>"}}
- SIDE:  "Writes <what> to out[<first>..<last>]."  or  "Does not write to out."
- CF:    "<loop or branch structure>."
- ALG:   "Implements <algorithm name>."

Bad claims (do NOT write claims like these):
- "This function might be some kind of hash."            (hedging, not checkable)
- "Uses several magic numbers and bit operations."       (no concrete value)
- "Computes a checksum using a polynomial and returns it, and also handles the empty input specially." (more than one fact)

"recovered_c" must be a complete, compilable C11 definition of the function with the exact prototype above,
named exactly {fn}, using only <stdint.h>, <stddef.h> and the macro VERA_ERR (already defined for you).
Use standard C types (uint8_t, uint32_t, uint64_t, size_t), not decompiler types such as uint, ulong, undefined8 or DAT_xxx.
No helper functions, no globals, no library calls.
Answer with JSON only."""

USER = """Function name: {fn}
Decompiler: {backend}

```
{pseudocode}
```"""


def build(fn_id: str, pseudocode: str, backend: str) -> tuple[str, str]:
    sig = SIGNATURE.format(fn=fn_id)
    return SYSTEM.format(signature=sig, fn=fn_id), USER.format(fn=fn_id, backend=backend, pseudocode=pseudocode.strip())
