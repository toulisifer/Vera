"""Kiểm thử vi sai ngẫu nhiên cho các item FEPR = 1 (góp ý G1, M6).

50 vector cố định chỉ nói "không tìm thấy phản ví dụ". Ở đây sinh thêm N input ngẫu nhiên mới cho mỗi item đã qua
50/50, chạy binary gốc (oracle) trên host và recovered C trong sandbox Docker, so (ret, out). Input dùng cùng profile
với vector của hàm nhưng seed khác, độ dài 0–512, out_cap và arg ngẫu nhiên (gồm cả out_cap thiếu và arg biên).
Không dẫn hướng theo độ phủ (không phải libFuzzer): đây là kiểm thử ngẫu nhiên có oracle.

    python -m vera.verify.fuzz --run E1 --n 2000
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import tempfile
from pathlib import Path

from vera.common import DATA, load_manifest, run_vectors, so_path
from vera.corpus.vectors import PROFILES, default_cap
from vera.verify import sandbox
from vera.verify.v1 import compile_recovered

MAX64 = 0xFFFFFFFFFFFFFFFF


def fuzz_inputs(fn_id: str, n: int) -> list[dict]:
    r = random.Random(int(hashlib.sha256(f"vera-fuzz-{fn_id}".encode()).hexdigest()[:16], 16))
    gen = PROFILES[load_manifest(fn_id)["input_profile"]]
    vs = []
    for i in range(n):
        size = r.choice([r.randint(0, 8), r.randint(9, 64), r.randint(65, 512)])
        data = gen(r, size)[:size] if size else b""
        cap = r.choice([default_cap(len(data)), default_cap(len(data)), r.randint(0, max(1, 2 * len(data)))])
        arg = r.choice([r.getrandbits(64), r.getrandbits(64), 0, MAX64, r.getrandbits(8)])
        vs.append({"id": f"f{i:05d}", "in": data.hex(), "arg": arg, "out_cap": cap})
    return vs


def fuzz_item(run: str, cfg: str, fn_id: str, n: int) -> dict:
    ana = json.loads((DATA / "runs" / run / cfg / f"{fn_id}.analysis.json").read_text(encoding="utf-8"))
    vs = fuzz_inputs(fn_id, n)
    ref = run_vectors(so_path(fn_id, cfg), fn_id, vs)
    res = {"fn": fn_id, "config": cfg, "n": n, "ref_not_ok": sum(x.status != "OK" for x in ref),
           "n_compared": 0, "n_match": 0, "counterexamples": []}
    with tempfile.TemporaryDirectory(prefix="vera-fuzz-") as d:
        so = Path(d) / "recovered.so"
        ok, err = compile_recovered(ana["output"]["recovered_c"], so)
        if not ok:
            return {**res, "error": f"không biên dịch lại được: {err}"}
        got = sandbox.run_untrusted(so, fn_id, vs)
    if isinstance(got, str):
        return {**res, "error": got}
    for v, a, b in zip(vs, ref, got):
        if a.status != "OK":  # oracle không cho kết quả (không xảy ra với corpus này) → bỏ qua
            continue
        res["n_compared"] += 1
        if b.status == "OK" and (a.ret, a.out) == (b.ret, b.out) and not b.overflow:
            res["n_match"] += 1
        elif len(res["counterexamples"]) < 3:
            res["counterexamples"].append({"len": len(v["in"]) // 2, "arg": f"0x{v['arg']:016x}",
                                           "out_cap": v["out_cap"], "in_head": v["in"][:32],
                                           "expected_ret": f"0x{a.ret:016x}", "status": b.status,
                                           "got_ret": f"0x{b.ret:016x}" if b.ret is not None else None,
                                           "out_differs": b.status == "OK" and a.out != b.out})
    return res


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default="E1")
    ap.add_argument("--n", type=int, default=2000)
    a = ap.parse_args()
    items = []
    for p in sorted((DATA / "runs" / a.run).glob("*/fn_*.v1.json")):
        v = json.loads(p.read_text(encoding="utf-8"))
        if v.get("fepr") == 1.0:
            items.append((p.parent.name, v["fn"]))
    out = []
    for cfg, fn in items:
        r = fuzz_item(a.run, cfg, fn, a.n)
        out.append(r)
        print(f"{cfg}/{fn}: {r['n_match']}/{r['n_compared']} {r.get('error', '')}")
    summary = {"run": a.run, "n_per_item": a.n, "items": len(out),
               "items_all_match": sum(r["n_compared"] > 0 and r["n_match"] == r["n_compared"] for r in out),
               "results": out}
    (DATA / "runs" / a.run / "fuzz.json").write_text(json.dumps(summary, indent=1) + "\n", encoding="utf-8")
    print(f"{summary['items_all_match']}/{summary['items']} item khớp trên mọi input ngẫu nhiên")


if __name__ == "__main__":
    main()
