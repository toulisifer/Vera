"""Self-test cho V3 — cổng chất lượng trước lượt chạy chính (E0, RQ4).

    python -m vera.verify.selftest

1. False alarm: 20 hằng đã biết, mỗi hằng trong một ngữ cảnh biên dịch (immediate, bảng,
   số âm, modulo/chia, 64-bit, ghi vào bộ nhớ, chuỗi...), biên dịch -O0 và -O2. Claim CONST
   nêu đúng hằng đó; V3 phải trả supported. Ngưỡng: tỉ lệ bỏ sót ≤ 5% ở mỗi mức tối ưu.
2. False support: với mỗi item của corpus, claim ALG nêu một thuật toán SAI (khác thuật toán
   thật và không cùng dấu vân tay). V3 không được trả supported. Mục tiêu 0%.

Ghi data/v3_selftest.md và data/v3_selftest.json.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

from vera.common import ARTIFACTS, CONFIGS, DATA, FN_IDS, INCLUDE, load_manifest
from vera.extract.evidence import extract
from vera.verify.fingerprints import FINGERPRINTS, SAME_FINGERPRINT
from vera.verify.v3 import Evidence, check_alg, check_const

MAX_FALSE_ALARM = 0.05

# (tên, hằng dạng C, giá trị claim nêu, thân hàm; C = hằng, dùng arg để compiler không gập hằng)
CASES = [
    ("mul32", "0x5BD1E995u", "0x5BD1E995", "return (uint32_t)arg * C;"),
    ("xor32", "0xDEADBEEFu", "0xDEADBEEF", "return (uint32_t)arg ^ C;"),
    ("add32_hi", "0x9E3779B1u", "0x9E3779B1", "return (uint32_t)arg + C;"),
    ("add32", "0x2545F491u", "0x2545F491", "return (uint32_t)arg + C;"),
    ("mask31", "0x7FFFFFFFu", "0x7FFFFFFF", "return arg & C;"),
    ("mask_alt", "0x00FF00FFu", "0x00FF00FF", "return arg & C;"),
    ("mask_hi", "0xFFFF0000u", "0xFFFF0000", "return (uint32_t)arg & C;"),
    ("cmp32", "0x12345678u", "0x12345678", "return arg == C ? 7 : 9;"),
    ("cmp16", "0xABCDu", "0xABCD", "return (uint16_t)arg == C ? 7 : 9;"),
    ("mul64", "0xC6A4A7935BD1E995ull", "0xC6A4A7935BD1E995", "return arg * C;"),
    ("xor64", "0x87C37B91114253D5ull", "0x87C37B91114253D5", "return arg ^ C;"),
    ("mod_prime", "65537u", "65537", "return (uint32_t)arg % C;"),
    ("mod_small", "10007u", "10007", "return (uint32_t)arg % C;"),
    ("div", "1000003u", "1000003", "return (uint32_t)arg / C;"),
    ("table", "0x1F2E3D4Cu", "0x1F2E3D4C",
     "static const uint32_t t[4] = {0x11111111u, C, 0x22222222u, 0x33333333u}; return t[arg & 3];"),
    ("table64", "0xA5A5A5A55A5A5A5Aull", "0xA5A5A5A55A5A5A5A",
     "static const uint64_t t[3] = {1, C, 2}; return t[arg % 3];"),
    ("neg_dec", "(-12345)", "-12345", "return (uint64_t)((int64_t)arg + C);"),
    ("store", "0x0BADF00Du", "0x0BADF00D", "if (out_cap < 4) return 0; VERA_ST32(out, C); return 4;"),
    ("mul_pow2", "4096u", "4096", "return arg * C;"),
    ("string", "\"VeRA-selftest-key\"", "VeRA-selftest-key",
     "static const char s[] = C; return (uint8_t)s[arg % (sizeof s - 1)];"),
]


def build_case(name: str, c_const: str, body: str, opt: str, d: Path) -> Path:
    src = d / f"{name}.c"
    src.write_text(f'#include "vera.h"\n#define C {c_const}\n'
                   f"VERA_FN(fn_st)\n{{\n    (void)in; (void)len; (void)out; (void)out_cap;\n    {body}\n}}\n")
    so = d / f"{name}_{opt}.so"
    subprocess.run(["gcc", "-std=c11", "-fPIC", "-shared", opt, f"-I{INCLUDE}", "-w", "-o", str(so), str(src)],
                   check=True)
    subprocess.run(["strip", "--strip-all", str(so)], check=True)
    return so


def false_alarm_test() -> tuple[list[dict], dict]:
    rows, rate = [], {}
    with tempfile.TemporaryDirectory(prefix="vera-selftest-") as d:
        for opt in ("-O0", "-O2"):
            miss = 0
            for name, c_const, claimed, body in CASES:
                ev = Evidence(extract(build_case(name, c_const, body, opt, Path(d))))
                claim = {"type": "CONST", "text": "uses the constant", "asserted_values": [claimed]}
                r = check_const(claim, ev)
                ok = r["label"] == "supported"
                miss += not ok
                rows.append({"case": name, "opt": opt, "value": claimed, "supported": ok,
                             "form": r["found"][0]["form"] if ok else None})
            rate[opt] = miss / len(CASES)
    return rows, rate


def same_group(a: str, b: str) -> bool:
    return a == b or any(a in g and b in g for g in SAME_FINGERPRINT)


def false_support_test() -> tuple[list[dict], int, int]:
    fails, n = [], 0
    for fn_id in FN_IDS:
        truth = load_manifest(fn_id)["oracle"]  # None với near-miss và tự thiết kế
        for cfg in CONFIGS:
            ev = Evidence(json.loads((ARTIFACTS / cfg / f"{fn_id}.evidence.json").read_text()))
            for alg, alts in FINGERPRINTS.items():
                if not alts or (truth and same_group(alg, truth)):
                    continue
                n += 1
                if check_alg(alg, ev)["label"] == "supported":
                    fails.append({"fn": fn_id, "config": cfg, "claimed": alg, "truth": truth})
    return fails, n, len(fails)


def main() -> None:
    rows, rate = false_alarm_test()
    fails, n_fs, n_fail = false_support_test()
    gate = all(r <= MAX_FALSE_ALARM for r in rate.values()) and n_fail == 0
    md = ["# Self-test V3", "", "## 1. False alarm (20 hằng đã biết × 2 mức tối ưu)", "",
          "| Ngữ cảnh | Hằng | -O0 | -O2 |", "|---|---|---|---|"]
    by = {(r["case"], r["opt"]): r for r in rows}
    for name, _, claimed, _ in CASES:
        cells = [f"✅ {by[(name, o)]['form']}" if by[(name, o)]["supported"] else "❌" for o in ("-O0", "-O2")]
        md.append(f"| {name} | `{claimed}` | {cells[0]} | {cells[1]} |")
    md += ["", f"Tỉ lệ bỏ sót: -O0 {rate['-O0']:.0%}, -O2 {rate['-O2']:.0%} (ngưỡng ≤ {MAX_FALSE_ALARM:.0%}).", "",
           "## 2. False support (claim ALG sai trên 60 item)", "",
           f"{n_fail}/{n_fs} claim sai được V3 đánh supported (mục tiêu 0).", ""]
    md += [f"- {f['config']}/{f['fn']}: nói {f['claimed']}, thật là {f['truth'] or 'không chuẩn'}" for f in fails]
    md += ["", f"**Cổng V3: {'ĐẠT' if gate else 'KHÔNG ĐẠT'}**"]
    (DATA / "v3_selftest.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    (DATA / "v3_selftest.json").write_text(json.dumps(
        {"false_alarm": rows, "false_alarm_rate": rate, "false_support": fails, "false_support_trials": n_fs,
         "gate_passed": gate}, indent=1) + "\n", encoding="utf-8")
    print("\n".join(md))
    if not gate:
        sys.exit(1)


if __name__ == "__main__":
    main()
