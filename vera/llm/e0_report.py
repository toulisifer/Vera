"""Báo cáo E0 phần model: tỉ lệ output đúng schema và tỉ lệ recovered_c biên dịch được.

    python -m vera.llm.e0_report --run E0

Tiêu chí dừng (hướng dẫn): ≥ 80% output đúng schema, ≥ 50% compile ở cấu hình plain.
Chỉ BIÊN DỊCH, không chạy mã do model sinh ra (chạy thuộc V1, trong Docker).
"""
from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from pathlib import Path

from vera.common import DATA, ROOT, load_manifest
from vera.oracles import lookup

HEADER = (ROOT / "harness" / "recovered_prelude.h").read_text()


def compiles(code: str) -> tuple[bool, str]:
    with tempfile.TemporaryDirectory() as d:
        src = Path(d) / "r.c"
        src.write_text(HEADER + code)
        p = subprocess.run(["gcc", "-std=c11", "-c", "-o", str(Path(d) / "r.o"), str(src)],
                           capture_output=True, text=True)
    first_err = next((ln for ln in p.stderr.splitlines() if "error" in ln), "")
    return p.returncode == 0, first_err.split("r.c:", 1)[-1][:160]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default="E0")
    ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args()
    run_dir = DATA / "runs" / a.run
    rows, stats = [], {}
    for f in sorted(run_dir.glob("*/*.analysis.json")):
        r = json.loads(f.read_text(encoding="utf-8"))
        cfg, o = f.parent.name, r["output"] or {}
        v1f = f.with_name(f.name.replace(".analysis.json", ".v1.json"))
        fepr = json.loads(v1f.read_text())["fepr"] if v1f.exists() else None
        # "đúng thuật toán": kinh điển → tên model nêu trùng oracle; near-miss/tự thiết kế → không gán tên chuẩn
        man = load_manifest(r["fn"])
        named = lookup(o.get("algorithm", "")) if o.get("algorithm") else None
        alg_ok = (named is not None and named.name == man["oracle"]) if man["group"] == "classic" else named is None
        ok, err = compiles(o.get("recovered_c", "")) if r["schema_valid"] else (False, "schema không hợp lệ")
        s = stats.setdefault(cfg, {"n": 0, "valid": 0, "compile": 0, "retry": 0, "claims": 0, "dropped": 0,
                                  "fepr1": 0, "alg_ok": 0})
        s["fepr1"] += fepr == 1.0
        s["alg_ok"] += alg_ok
        s["n"] += 1
        s["valid"] += r["schema_valid"]
        s["compile"] += ok
        s["retry"] += len(r["attempts"]) > 1
        s["claims"] += len(r.get("claims", []))
        s["dropped"] += len(r.get("dropped_claims", []))
        rows.append(f"| {cfg} | {r['fn']} | {'✅' if r['schema_valid'] else '❌'} | {len(r['attempts'])} "
                    f"| {'✅' if ok else '❌ ' + err.replace('|', '/')[:60]} | {'—' if fepr is None else f'{fepr:.2f}'} "
                    f"| {o.get('algorithm', '—')} {'✅' if alg_ok else '❌'} "
                    f"| {len(r.get('claims', []))} / {len(r.get('dropped_claims', []))} |")
        if a.verbose:
            print(f"== {cfg}/{r['fn']}  name={o.get('proposed_name')!r} alg={o.get('algorithm')!r}")
            if not r["schema_valid"]:
                print("   lỗi schema:", r["attempts"][-1]["errors"][:3])
            for c in r.get("claims", []):
                print(f"   [{c['type']}] {c['text'][:120]} {c['asserted_values']} conf={c['confidence']}")
            for c in r.get("dropped_claims", []):
                print(f"   (loại: {c['drop_reason']}) {c['text'][:100]}")
    md = [f"# {a.run} — kiểm tra năng lực model", "",
          "| Cấu hình | Hàm | Schema | Số lần gọi | Compile | FEPR | algorithm (đúng?) | claim giữ / loại |",
          "|---|---|---|---|---|---|---|---|", *rows, "",
          "| Cấu hình | Đúng schema | Compile | FEPR = 1 | Thuật toán đúng | Phải thử lại | Claim giữ / loại |",
          "|---|---|---|---|---|---|---|"]
    for cfg, s in stats.items():
        md.append(f"| {cfg} | {s['valid']}/{s['n']} | {s['compile']}/{s['n']} | {s['fepr1']}/{s['n']} "
                  f"| {s['alg_ok']}/{s['n']} | {s['retry']}/{s['n']} "
                  f"| {s['claims']} / {s['dropped']} |")
    n = sum(s["n"] for s in stats.values())
    valid = sum(s["valid"] for s in stats.values())
    plain = stats.get("plain", {"n": 1, "compile": 0})
    gate_schema, gate_compile = valid / n >= 0.8, plain["compile"] / plain["n"] >= 0.5
    md += ["", f"Cổng E0: đúng schema {valid}/{n} ({'đạt' if gate_schema else 'KHÔNG đạt'} ≥ 80%); "
               f"compile ở plain {plain['compile']}/{plain['n']} ({'đạt' if gate_compile else 'KHÔNG đạt'} ≥ 50%)."]
    (run_dir / "report.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
