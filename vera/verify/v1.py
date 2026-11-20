"""V1 — tương đương hàm vi sai của recovered_c so với binary gốc trên 50 vector.

    python -m vera.verify.v1 --run E0

Với mỗi analysis.json: biên dịch recovered_c (prelude + mã) thành shared object trên host
(chỉ biên dịch), chạy trong sandbox Docker, so (ret, out) với output kỳ vọng.
FEPR = số vector khớp / 50. FEPR = 1,0 KHÔNG chứng minh tương đương, chỉ là không tìm
thấy phản ví dụ trên 50 vector.

Ghi data/runs/<run>/<config>/fn_XX.v1.json.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from pathlib import Path

from vera.common import DATA, ROOT, load_vectors
from vera.corpus.vectors import pad_out
from vera.verify import sandbox

PRELUDE = ROOT / "harness" / "recovered_prelude.h"
CFLAGS = ["-std=gnu11", "-O0", "-fPIC", "-shared", "-w"]


def compile_recovered(code: str, out_so: Path) -> tuple[bool, str]:
    src = out_so.with_suffix(".c")
    src.write_text(PRELUDE.read_text() + "\n#line 1 \"recovered.c\"\n" + code)
    p = subprocess.run(["gcc", *CFLAGS, "-o", str(out_so), str(src)], capture_output=True, text=True)
    err = next((ln for ln in p.stderr.splitlines() if "error" in ln), p.stderr.strip()[:200])
    return p.returncode == 0, err


def verify(analysis: dict, vectors: list[dict] | None = None) -> dict:
    fn_id = analysis["fn"]
    out = analysis.get("output") or {}
    res = {"fn": fn_id, "config": analysis.get("config"), "compiled": False, "fepr": None,
           "n_vectors": 0, "n_match": 0, "failures": [], "sandbox_image": sandbox.IMAGE}
    if not analysis.get("schema_valid"):
        res["error"] = "schema không hợp lệ"
        return res
    vectors = vectors if vectors is not None else load_vectors(fn_id)
    res["n_vectors"] = len(vectors)
    with tempfile.TemporaryDirectory(prefix="vera-v1-") as d:
        so = Path(d) / "recovered.so"
        ok, err = compile_recovered(out["recovered_c"], so)
        res["compiled"] = ok
        if not ok:
            res["compile_error"] = err
            res["fepr"] = 0.0
            return res
        runs = sandbox.run_untrusted(so, fn_id, vectors)
    if isinstance(runs, str):
        res["error"] = runs
        res["fepr"] = 0.0
        return res
    for v, r in zip(vectors, runs):
        exp_ret, exp_out = v["ret"], pad_out(v["out"], v["out_cap"])
        got_ret = f"0x{r.ret:016x}" if r.ret is not None else None
        if r.status == "OK" and got_ret == exp_ret and r.out == exp_out and not r.overflow:
            res["n_match"] += 1
        elif len(res["failures"]) < 5:  # giữ vài phản ví dụ làm bằng chứng cho case study
            res["failures"].append({"vector": v["id"], "tag": v["tag"], "status": r.status,
                                    "expected_ret": exp_ret, "got_ret": got_ret,
                                    "out_differs": r.status == "OK" and r.out != exp_out,
                                    "overflow": r.overflow, "detail": r.detail})
    res["fepr"] = res["n_match"] / len(vectors)
    return res


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    a = ap.parse_args()
    run_dir = DATA / "runs" / a.run
    for f in sorted(run_dir.glob("*/*.analysis.json")):
        r = verify(json.loads(f.read_text(encoding="utf-8")))
        f.with_name(f.name.replace(".analysis.json", ".v1.json")).write_text(
            json.dumps(r, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        tag = f"FEPR={r['fepr']:.2f}" if r["fepr"] is not None else r.get("error", "")
        print(f"[V1] {a.run} {f.parent.name}/{r['fn']}: compiled={r['compiled']} {tag} "
              f"{r.get('compile_error', '') or r.get('error', '')}"[:200], flush=True)


if __name__ == "__main__":
    main()
