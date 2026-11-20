"""Baseline V1: LLM4Decompile-Ref v2 (6.7B) tinh chỉnh pseudocode Ghidra thành C.

    python -m vera.llm.llm4decompile --run E1_llm4decompile
    python -m vera.verify.v1 --run E1_llm4decompile && python -m vera.report.metrics --run E1_llm4decompile

Prompt đúng như model card của LLM4Binary/llm4decompile-6.7b-v2:
    "# This is the assembly code:\\n" + pseudocode + "\\n# What is the source code?\\n"
gọi Ollama ở chế độ raw (không chat template), temperature 0.

Model không biết chữ ký chung của VeRA và tự đặt prototype theo Ghidra (vd. `uint fn_01(byte *p, long n)`).
Để V1 so được, mã được bọc bằng một adapter: hàm của model đổi tên thành `vera_inner`, và
`fn_XX` với chữ ký chung gọi nó, truyền in, len, arg, out, out_cap theo đúng thứ tự thanh ghi
SysV (ép kiểu theo tham số model khai báo), rồi ép giá trị trả về lên uint64_t. Như vậy
LLM4Decompile được đánh giá đúng như khi chạy binary gốc với các thanh ghi đó.

Model này chỉ sinh mã, không sinh claim → chỉ có số liệu V1 (compile rate, FEPR).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
import urllib.request

from vera.common import ARTIFACTS, CONFIGS, DATA, FN_IDS
from vera.llm.client import CACHE, OFFLINE, OLLAMA_URL, model_info

MODEL = "hf.co/RichardErkhov/LLM4Binary_-_llm4decompile-6.7b-v2-gguf:Q4_K_M"
ARG_NAMES = ["in", "len", "arg", "out", "out_cap"]
DEF_RE = re.compile(r"^([A-Za-z_][\w \t\*]*?)\b([A-Za-z_]\w*)\s*\(([^;{)]*)\)\s*\{", re.M)


def generate(prompt: str, options: dict) -> dict:
    body = {"model": MODEL, "prompt": prompt, "raw": True, "stream": False, "options": options}
    key = hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()
    path = CACHE / f"{key}.json"
    if path.exists():
        return {**json.loads(path.read_text(encoding="utf-8")), "cached": True}
    if OFFLINE:
        raise SystemExit(f"VERA_OFFLINE=1 nhưng cache thiếu {key}")
    req = urllib.request.Request(f"{OLLAMA_URL}/api/generate", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=900) as r:
        resp = json.load(r)
    rec = {"key": key, "content": resp["response"], "seconds": round(time.time() - t0, 1),
           "eval_count": resp.get("eval_count")}
    CACHE.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rec, ensure_ascii=False) + "\n", encoding="utf-8")
    return {**rec, "cached": False}


def adapt(code: str, fn_id: str) -> tuple[str | None, str]:
    """Bọc hàm đầu tiên của model bằng fn_XX theo chữ ký chung. Trả (mã, ghi chú)."""
    code = re.sub(r"^\s*#\s*include.*$", "", code, flags=re.M)  # prelude đã có header chuẩn
    m = DEF_RE.search(code)
    if not m:
        return None, "không tìm thấy định nghĩa hàm"
    ret_type, name, params = m.group(1).strip(), m.group(2), m.group(3).strip()
    if ret_type.split()[-1] in ("static", "inline"):
        ret_type = "int"
    body = re.sub(rf"\b{re.escape(name)}\b", "vera_inner", code)
    plist = [] if params in ("", "void") else [p.strip() for p in params.split(",")]
    if len(plist) > 5:
        return None, f"hàm có {len(plist)} tham số (> 5)"
    casts = []
    for p, a in zip(plist, ARG_NAMES):
        ptype = re.sub(r"\b\w+\s*$", "", p).strip() or "long"
        casts.append(f"({ptype})({a})")
    call = f"vera_inner({', '.join(casts)})"
    tail = (f"    {call};\n    return 0;" if ret_type == "void"
            else f"    return (uint64_t)({call});")
    wrapper = (f"\nuint64_t {fn_id}(const uint8_t *in, size_t len, uint64_t arg, uint8_t *out, size_t out_cap)\n"
               f"{{\n    (void)in; (void)len; (void)arg; (void)out; (void)out_cap;\n{tail}\n}}\n")
    return body + wrapper, f"adapter: {ret_type} {name}({params}) ← chữ ký chung"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default="E1_llm4decompile")
    ap.add_argument("--fns", default=",".join(FN_IDS))
    ap.add_argument("--configs", default=",".join(CONFIGS))
    a = ap.parse_args()
    run_dir = DATA / "runs" / a.run
    run_dir.mkdir(parents=True, exist_ok=True)
    options = {"temperature": 0.0, "seed": 0, "num_ctx": 8192, "num_predict": 2048}
    (run_dir / "run.json").write_text(json.dumps({
        "run": a.run, "started": time.strftime("%Y-%m-%d %H:%M:%S"), "model": model_info(MODEL),
        "baseline": "LLM4Decompile-Ref v2 6.7B", "options": options, "temperature": 0.0, "samples": 1,
        "fns": a.fns.split(","), "configs": a.configs.split(","),
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for cfg in a.configs.split(","):
        for fn_id in a.fns.split(","):
            pseudo = (ARTIFACTS / cfg / f"{fn_id}.pseudocode.c").read_text()
            prompt = "# This is the assembly code:\n" + pseudo.strip() + "\n# What is the source code?\n"
            rec = generate(prompt, options)
            code, note = adapt(rec["content"], fn_id)
            res = {"fn": fn_id, "config": cfg, "model": MODEL, "options": options, "baseline": True,
                   "schema_valid": code is not None, "adapter_note": note, "raw": rec["content"],
                   "attempts": [{"errors": [] if code else [note], "seconds": rec["seconds"],
                                 "cached": rec["cached"], "eval_count": rec.get("eval_count"), "cache_key": rec["key"]}],
                   "output": {"recovered_c": code or "", "algorithm": "unknown", "claims": []}, "claims": []}
            (run_dir / cfg).mkdir(exist_ok=True)
            (run_dir / cfg / f"{fn_id}.analysis.json").write_text(
                json.dumps(res, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
            print(f"[{a.run}] {cfg}/{fn_id}: {rec['seconds']}s{' (cache)' if rec['cached'] else ''} {note}", flush=True)


if __name__ == "__main__":
    main()
